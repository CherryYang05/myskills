import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import sync
import verify
import generate


def package(body="old", mode="100644"):
    return {
        "SKILL.md": ("100644", b"---\nname: demo\ndescription: Demo test.\n---\n" + body.encode()),
        "scripts/run.py": (mode, b"print('hello')\n")
    }


class SynchronizationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.external = self.root / sync.EXTERNAL / "demo"
        self.external.mkdir(parents=True)
        (self.root / "skills/personal/own").mkdir(parents=True)
        (self.root / "skills/personal/own/SKILL.md").write_text(
            "---\nname: own\ndescription: My own skill.\n---\n"
        )
        (self.root / "automation").mkdir()
        self.config = {"demo": {"repo": "example/demo", "path": "skills/demo", "ref": "main", "sha": "a" * 40}}
        (self.root / sync.CONFIG).write_text(json.dumps(self.config))
        self.old = package()
        self.write_files(self.old)

    def write_files(self, files):
        for name, (mode, content) in files.items():
            path = self.external / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(0o755 if mode == "100755" else 0o644)

    def test_registry_must_cover_every_external_skill(self):
        sync.validate_config(self.config, self.root)
        with self.assertRaisesRegex(ValueError, "mismatch"):
            sync.validate_config({}, self.root)
        with self.assertRaisesRegex(ValueError, "mismatch"):
            sync.validate_config({"missing": self.config["demo"]}, self.root)

    def test_only_sha_is_changed_on_apply(self):
        newer = package("new", "100755")
        newer["references/notes.md"] = ("100644", b"added")
        changes = sync.diff(self.old, newer)
        updated = sync.apply_plans(self.root, self.config, [("demo", "b" * 40, self.old, newer, changes)], "2026-W45")
        self.assertEqual(updated["demo"]["sha"], "b" * 40)
        self.assertEqual(sync.local_snapshot(self.external), newer)
        self.assertEqual((self.root / "skills/personal/own/SKILL.md").read_text().count("own"), 2)
        report = (self.root / sync.SUMMARY).read_text()
        self.assertIn("2026-W45", report)
        self.assertIn("scripts/run.py", report)
        self.assertIn("b" * 12, report)

    def test_unrelated_upstream_commit_does_not_advance_source_sha(self):
        self.assertEqual(sync.diff(self.old, dict(self.old)), [])
        result = sync.apply_plans(self.root, self.config, [("demo", "b" * 40, self.old, self.old, [])], "2026-W45")
        self.assertEqual(result["demo"]["sha"], "a" * 40)

    def test_full_replacement_removes_local_files(self):
        (self.external / "local.txt").write_text("custom")
        previous = sync.local_snapshot(self.external)
        newer = package("upstream")
        sync.apply_plans(self.root, self.config, [("demo", "b" * 40, previous, newer, sync.diff(previous, newer))])
        self.assertFalse((self.external / "local.txt").exists())

    def test_file_directory_transition(self):
        old = dict(self.old)
        old["changing"] = ("100644", b"x")
        self.write_files(old)
        newer = dict(self.old)
        newer["changing/child"] = ("100644", b"y")
        sync.apply_plans(self.root, self.config, [("demo", "b" * 40, old, newer, sync.diff(old, newer))])
        self.assertEqual((self.external / "changing/child").read_bytes(), b"y")

    def test_path_traversal_and_symlinks_rejected(self):
        for value in ("/tmp", "../escape", "a/../escape", ".git/config", "a\\b", "x\nz"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                sync.safe_path(value)
        (self.external / "link").symlink_to("SKILL.md")
        with self.assertRaisesRegex(ValueError, "symlink"):
            sync.local_snapshot(self.external)

    def test_preserved_license_cannot_be_modified(self):
        self.config["demo"]["preserve"] = ["LICENSE"]
        sync.validate_config(self.config, self.root)
        self.config["demo"]["preserve"] = ["scripts/run.py"]
        with self.assertRaisesRegex(ValueError, "legal"):
            sync.validate_config(self.config, self.root)

    def test_generate_catalog_contains_all_groups(self):
        generated = generate.render(self.root)
        catalog = json.loads(generated[generate.MARKETPLACE])
        self.assertEqual({x["name"] for x in catalog["plugins"]}, {"demo", "own"})
        self.assertIn("./skills/external/demo", generated["README.md"])
        self.assertIn("./skills/personal/own", generated["README.md"])

    def test_documented_extension_and_unknown_field(self):
        path = self.external / "SKILL.md"
        path.write_text("---\nname: demo\ndescription: Test.\nuser-invocable: false\n---\n")
        self.assertEqual(verify.read_frontmatter(path)["user-invocable"], False)
        path.write_text("---\nname: demo\ndescription: Test.\nuser-invocable: 'false'\n---\n")
        with self.assertRaisesRegex(ValueError, "boolean"):
            verify.read_frontmatter(path)


if __name__ == "__main__":
    unittest.main()
