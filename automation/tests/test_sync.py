import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        (self.root / "automation/templates").mkdir()
        template = Path(__file__).resolve().parents[1] / "templates/README.md.tpl"
        (self.root / "automation/templates/README.md.tpl").write_bytes(template.read_bytes())
        (self.root / "automation/plugin-appearance.json").write_text(json.dumps({
            "schemaVersion": 1,
            "default": {
                "brandColor": "#7B9EB5", "concept": "Temporary default",
                "glyph": '<path d="M20 20h50v50"/>',
            },
            "skills": {
                name: {
                    "brandColor": "#6CA8D8", "concept": f"Icon for {name}",
                    "glyph": '<path d="M20 20h50v50"/>',
                }
                for name in ("demo", "own")
            },
        }))
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
        with self.assertRaisesRegex(ValueError, "nonempty"):
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
        report = self.root / sync.SUMMARY
        report.write_text("previous actual update")
        old_registry = (self.root / sync.CONFIG).read_bytes()
        result = sync.apply_plans(self.root, self.config, [("demo", "b" * 40, self.old, self.old, [])], "2026-W45")
        self.assertEqual(result["demo"]["sha"], "a" * 40)
        # A weekly no-op must not create a false release or report-only PR.
        self.assertEqual(report.read_text(), "previous actual update")
        self.assertEqual((self.root / sync.CONFIG).read_bytes(), old_registry)

    def test_shared_upstream_repo_is_fetched_only_once(self):
        # Two names within the same upstream repo/ref must reuse a Git fetch.
        (self.root / "skills/external/second").mkdir()
        (self.root / "skills/external/second/SKILL.md").write_text(
            "---\nname: second\ndescription: second\n---\n"
        )
        config = dict(self.config)
        config["second"] = {**self.config["demo"], "path": "skills/second"}
        calls = []

        def fake_git(directory, *args):
            calls.append(args)
            if args[0] == "rev-parse":
                return b"b" * 40
            return b""

        with mock.patch.object(sync, "ROOT", self.root), \
                mock.patch.object(sync, "git", side_effect=fake_git), \
                mock.patch.object(sync, "tree_snapshot", return_value=self.old):
            plans = sync.fetch_snapshots(config)
        self.assertEqual(len(plans), 2)
        self.assertEqual(sum(command[0] == "fetch" for command in calls), 1)

    def test_github_step_summary_includes_noop_checks(self):
        summary = self.root / "GITHUB_STEP_SUMMARY"
        data = [("demo", "a" * 40, self.old, self.old, [])]
        with mock.patch.dict("os.environ", {"GITHUB_STEP_SUMMARY": str(summary)}):
            sync.append_action_summary(data)
        self.assertIn("No changes detected", summary.read_text())
        self.assertIn("demo", summary.read_text())

    def test_plugin_versions_bump_only_when_distributable_changes(self):
        first = generate.render_plugin_files(self.root)
        generate.check_or_write_plugin_files(self.root, first, False)
        same = generate.render_plugin_files(self.root)
        self.assertEqual(same, first)

        # Source content changes: increment demo, leave unrelated own untouched.
        (self.external / "scripts/run.py").write_text("print('updated')\n")
        second = generate.render_plugin_files(self.root)
        manifest = lambda package, name: json.loads(package[f"plugins/{name}/plugin.json"][1])
        self.assertEqual(manifest(second, "demo")["version"], "1.0.1")
        self.assertEqual(manifest(second, "own")["version"], "1.0.0")
        generate.check_or_write_plugin_files(self.root, second, False)
        self.assertEqual(generate.render_plugin_files(self.root), second)

        # Claude-only installer metadata has no effect on the exported package.
        ignored = self.external / ".claude-plugin/plugin.json"
        ignored.parent.mkdir()
        ignored.write_text('{"name":"demo"}')
        self.assertEqual(generate.render_plugin_files(self.root), second)

    def test_readme_template_requires_one_placeholder(self):
        indexes = generate.render(self.root)
        self.assertIn("| demo |", indexes[generate.README].replace("[demo](./skills/external/demo)", "demo"))
        template = self.root / "automation/templates/README.md.tpl"
        template.write_text("No placeholder")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            generate.render(self.root)

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

    def test_only_other_platform_installers_are_filtered_from_plugins(self):
        source_metadata = {
            ".claude-plugin/plugin.json": b'{"name": "demo"}',
            ".claude-plugin/marketplace.json": b'{"name": "demo-claude"}',
            ".cursor-plugin/plugin.json": b'{"name": "demo"}',
            ".hidden/runtime.txt": b"hidden runtime dependency",
            "references/.cursor-plugin/notes.md": b"nested reference must survive",
        }
        for relative, content in source_metadata.items():
            path = self.external / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        original = sync.local_snapshot(self.external)
        for relative in source_metadata:
            self.assertIn(relative, original)

        generated = generate.render_plugin_files(self.root)
        plugin_prefix = "plugins/demo/skills/demo/"
        self.assertIn(plugin_prefix + "SKILL.md", generated)
        self.assertIn(plugin_prefix + ".hidden/runtime.txt", generated)
        self.assertIn(plugin_prefix + "references/.cursor-plugin/notes.md", generated)
        for relative in (".claude-plugin/plugin.json",
                         ".claude-plugin/marketplace.json",
                         ".cursor-plugin/plugin.json"):
            self.assertNotIn(plugin_prefix + relative, generated)
        # Installers are only filtered from the distributable package.
        for relative, content in source_metadata.items():
            self.assertEqual((self.external / relative).read_bytes(), content)
        generate.check_or_write_plugin_files(self.root, generated, False)
        generate.check_or_write_plugin_files(self.root, generated, True)

    def test_generated_plugins_include_functional_icon_assets(self):
        generated = generate.render_plugin_files(self.root)
        for name in ("demo", "own"):
            manifest = json.loads(generated[f"plugins/{name}/plugin.json"][1])
            interface = manifest["extensions"]["com.openai"]["interface"]
            self.assertEqual(interface["logo"], "./assets/icon.svg")
            self.assertEqual(interface["composerIcon"], "./assets/icon.svg")
            self.assertEqual(interface["brandColor"], "#6CA8D8")
            svg = generated[f"plugins/{name}/assets/icon.svg"][1]
            self.assertIn(b'viewBox="0 0 128 128"', svg)
            self.assertIn(b'<linearGradient id="tile"', svg)
            self.assertIn(b'<stop offset="0%"', svg)
            self.assertIn(b'<stop offset="100%"', svg)
            self.assertIn(b'stroke-width="5.5"', svg)
            self.assertIn(b'opacity=".045"', svg)
            self.assertIn(b"<title>", svg)
            self.assertLess(len(svg), 5000)
        generate.check_or_write_plugin_files(self.root, generated, False)
        generate.check_or_write_plugin_files(self.root, generated, True)

    def test_appearance_fallback_is_deterministic_but_ci_rejects_it(self):
        from appearance import load_config as appearance_config, render_icon, validate_coverage
        path = self.root / "automation/plugin-appearance.json"
        cfg = json.loads(path.read_text())
        del cfg["skills"]["own"]
        path.write_text(json.dumps(cfg))
        loaded = appearance_config(self.root)
        icon_one, color, fallback = render_icon("own", loaded)
        icon_two, _, fallback_two = render_icon("own", loaded)
        self.assertTrue(fallback and fallback_two)
        self.assertEqual(icon_one, icon_two)
        self.assertEqual(color, loaded["default"]["brandColor"])
        with self.assertRaisesRegex(ValueError, "missing=.*own"):
            validate_coverage(loaded, {"demo", "own"})
        # A staging build can still render a coherent generic icon.
        package = generate.render_plugin_files(self.root)
        self.assertEqual(package["plugins/own/assets/icon.svg"][1], icon_one)

    def test_appearance_rejects_unsafe_svg_and_light_brand_colors(self):
        from appearance import validate_entry
        valid = {
            "brandColor": "#6CA8D8", "concept": "Research helper",
            "glyph": '<path d="M20 20h50v50"/>',
        }
        validate_entry("demo", valid)
        for glyph in ('<script>alert(1)</script>',
                      '<image href="https://attacker.invalid/x.png"/>',
                      '<path d="M20 20" onload="alert(1)"/>',
                      '<path d="M20 20" fill="url(https://bad.invalid)"/>'):
            with self.subTest(glyph=glyph), self.assertRaises(ValueError):
                validate_entry("demo", {**valid, "glyph": glyph})
        with self.assertRaisesRegex(ValueError, "contrast"):
            validate_entry("demo", {**valid, "brandColor": "#FFFFFF"})
        # Too-dark colors are rejected to keep the family soft and airy.
        with self.assertRaisesRegex(ValueError, "contrast"):
            validate_entry("demo", {**valid, "brandColor": "#17345A"})

    def test_pastel_gradient_blends_are_reproducible(self):
        from appearance import blend_hex, contrast_against_white, load_config
        self.assertEqual(blend_hex("#000000", "#FFFFFF", 13), "#212121")
        self.assertEqual(blend_hex("#FFFFFF", "#273B5E", 7), "#F0F1F4")
        config = load_config(self.root)
        for name in ("demo", "own"):
            self.assertGreaterEqual(
                contrast_against_white(config["skills"][name]["brandColor"]), 2.35
            )
            self.assertLessEqual(
                contrast_against_white(config["skills"][name]["brandColor"]), 4.2
            )

    def test_appearance_change_triggers_only_own_plugin_version(self):
        from appearance import load_config as appearance_config
        first = generate.render_plugin_files(self.root)
        generate.check_or_write_plugin_files(self.root, first, False)
        cfg = json.loads((self.root / "automation/plugin-appearance.json").read_text())
        cfg["skills"]["demo"]["glyph"] = '<circle cx="64" cy="64" r="22"/>'
        (self.root / "automation/plugin-appearance.json").write_text(json.dumps(cfg))
        next_build = generate.render_plugin_files(self.root)
        v = lambda name: json.loads(next_build[f"plugins/{name}/plugin.json"][1])["version"]
        self.assertEqual(v("demo"), "1.0.1")
        self.assertEqual(v("own"), "1.0.0")
        self.assertNotEqual(first["plugins/demo/assets/icon.svg"], next_build["plugins/demo/assets/icon.svg"])
        generate.check_or_write_plugin_files(self.root, next_build, False)
        self.assertEqual(generate.render_plugin_files(self.root), next_build)

    def test_cross_platform_marketplaces_and_cli_paths(self):
        indexes = generate.render(self.root)
        for key in (generate.MARKETPLACE, generate.CLAUDE_MARKETPLACE,
                    generate.CURSOR_MARKETPLACE):
            self.assertIn(key, indexes)
            catalog = json.loads(indexes[key])
            self.assertEqual({entry["name"] for entry in catalog["plugins"]}, {"demo", "own"})
            for entry in catalog["plugins"]:
                src = entry["source"]
                self.assertEqual(
                    src["path"] if isinstance(src, dict) else src,
                    "./plugins/" + entry["name"],
                )
        self.assertEqual(json.loads(indexes[generate.CLAUDE_MARKETPLACE])["name"], "cherry-skills")
        self.assertEqual(json.loads(indexes[generate.CURSOR_MARKETPLACE])["name"], "cherry-skills")
        paths = json.loads(indexes[generate.SKILLS_CLI_CONFIG])["paths"]
        self.assertEqual(paths, ["./skills/external", "./skills/personal"])
        plugins = generate.render_plugin_files(self.root)
        for name in ("demo", "own"):
            self.assertIn(f"plugins/{name}/plugin.json", plugins)
            self.assertIn(f"plugins/{name}/skills/{name}/SKILL.md", plugins)

    def test_cli_inventory_output_check(self):
        from check_cli_inventory import check_cli_output
        packages = verify.inventory(self.root)
        self.assertEqual(check_cli_output("demo\nown", packages), 2)
        with self.assertRaisesRegex(ValueError, "own"):
            check_cli_output("demo", packages)

    def test_generate_catalog_contains_all_groups(self):
        generated = generate.render(self.root)
        catalog = json.loads(generated[generate.MARKETPLACE])
        self.assertEqual({x["name"] for x in catalog["plugins"]}, {"demo", "own"})
        self.assertIn("./skills/external/demo", generated["README.md"])
        self.assertIn("./skills/personal/own", generated["README.md"])

        self.assertIn("./plugins/demo", generated[generate.MARKETPLACE])
        self.assertIn("./plugins/own", generated[generate.MARKETPLACE])
        packaged = generate.render_plugin_files(self.root)
        demo = json.loads(packaged["plugins/demo/plugin.json"][1])
        self.assertEqual(demo["name"], "demo")
        self.assertEqual(demo["homepage"], "https://github.com/CherryYang05/myskills/tree/master/skills/external/demo")
        self.assertEqual(packaged["plugins/demo/skills/demo/SKILL.md"], self.old["SKILL.md"])
        self.assertEqual(packaged["plugins/demo/skills/demo/scripts/run.py"], self.old["scripts/run.py"])
        self.assertIn("plugins/own/skills/own/SKILL.md", packaged)
        generate.check_or_write_plugin_files(self.root, packaged, False)
        generate.check_or_write_plugin_files(self.root, packaged, True)
        (self.root / "plugins/demo/skills/demo/SKILL.md").write_text("stale!")
        with self.assertRaisesRegex(SystemExit, "stale"):
            generate.check_or_write_plugin_files(self.root, packaged, True)

    def test_future_frontmatter_keys_are_forward_compatible(self):
        path = self.external / "SKILL.md"
        path.write_text(
            "---\nname: demo\ndescription: Future-compatible Skill.\n"
            "new-client-feature: enabled\n---\n"
        )
        packages = verify.inventory(self.root)
        self.assertEqual(packages[0][2]["new-client-feature"], "enabled")

    def test_readme_description_does_not_split_english_words(self):
        self.assertEqual(
            generate.short_description("Review accessibility rules and improve the design system", limit=22),
            "Review accessibility…",
        )
        self.assertEqual(
            generate.short_description("检查前端页面的可访问性。其他信息"),
            "检查前端页面的可访问性",
        )

    def test_documented_extension_and_unknown_field(self):
        path = self.external / "SKILL.md"
        path.write_text("---\nname: demo\ndescription: Test.\nuser-invocable: false\n---\n")
        self.assertEqual(verify.read_frontmatter(path)["user-invocable"], False)
        path.write_text("---\nname: demo\ndescription: Test.\nuser-invocable: 'false'\n---\n")
        with self.assertRaisesRegex(ValueError, "boolean"):
            verify.read_frontmatter(path)


if __name__ == "__main__":
    unittest.main()
