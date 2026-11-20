import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import generate


class ReadmeOrderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q", "--initial-branch=main")
        self.git("config", "user.name", "README test")
        self.git("config", "user.email", "readme@example.invalid")
        self.git("config", "commit.gpgsign", "false")
        (self.root / "automation/templates").mkdir(parents=True)
        (self.root / "automation/templates/README.md.tpl").write_text("{{SKILL_TABLE}}\n")
        self.config = {}
        self.add_skill("external", "alpha", "old-external", "2026-01-01")
        self.add_skill("personal", "alpha", "old-personal", "2026-02-01")
        self.add_skill("external", "zeta", "new-external", "2026-03-01")
        self.add_skill("personal", "zeta", "new-personal", "2026-04-01")

    def git(self, *args, env=None):
        return subprocess.check_output(["git", "-C", str(self.root), *args],
                                       env=env, text=True, stderr=subprocess.PIPE)

    def commit(self, day):
        self.git("add", ".")
        env = {**os.environ, "GIT_AUTHOR_DATE": f"{day}T12:00:00+00:00",
               "GIT_COMMITTER_DATE": f"{day}T12:00:00+00:00"}
        self.git("commit", "-q", "-m", "Fixture change", env=env)

    def add_skill(self, group, directory, name, day=None):
        path = self.root / "skills" / group / directory
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Test Skill.\n---\n")
        if group == "external":
            self.config[directory] = {
                "repo": "example/skills", "path": directory, "ref": "main", "sha": "a" * 40,
            }
            (self.root / "automation/upstreams.json").write_text(json.dumps(self.config))
        if day:
            self.commit(day)

    def row_names(self):
        readme = generate.render(self.root)[generate.README]
        return re.findall(r"^\| \[([^\]]+)\]", readme, re.M)

    def test_groups_and_first_addition_survive_updates_and_moves(self):
        expected = ["new-external", "old-external", "new-personal", "old-personal"]
        self.assertEqual(self.row_names(), expected)
        catalogs = generate.render(self.root)
        self.assertEqual(
            [p["name"] for p in json.loads(catalogs[generate.MARKETPLACE])["plugins"]],
            ["old-external", "new-external", "old-personal", "new-personal"],
        )
        old = self.root / "skills/external/alpha/SKILL.md"
        old.write_text(old.read_text() + "\nA later upstream revision.\n")
        self.commit("2026-05-01")
        self.assertEqual(self.row_names(), expected)
        self.git("mv", "skills/external/alpha", "skills/external/beta")
        self.config["beta"] = self.config.pop("alpha")
        (self.root / "automation/upstreams.json").write_text(json.dumps(self.config))
        self.commit("2026-06-01")
        self.assertEqual(self.row_names(), expected)

    def test_new_uncommitted_skill_keeps_order_after_commit(self):
        self.add_skill("external", "brand-new", "brand-new")
        before = generate.render(self.root)[generate.README]
        self.assertEqual(self.row_names()[0], "brand-new")
        self.commit("2026-07-01")
        self.assertEqual(generate.render(self.root)[generate.README], before)

    def test_bundle_uses_its_first_member(self):
        self.add_skill("external", "middle", "middle", "2026-02-15")
        (self.root / "automation/plugin-groups.json").write_text(json.dumps({
            "schemaVersion": 1,
            "plugins": {"suite": {
                "displayName": "Suite", "description": "Two related Skills.",
                "homepage": "https://example.com/suite",
                "skills": ["external/alpha", "external/zeta"],
            }},
        }))
        self.assertEqual(self.row_names(), ["middle", "Suite", "new-personal", "old-personal"])


if __name__ == "__main__":
    unittest.main()
