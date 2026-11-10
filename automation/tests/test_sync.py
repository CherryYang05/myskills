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
import plugin_groups


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
                "brandColor": "#576579", "concept": "Temporary default",
                "glyph": '<path d="M20 20h50v50"/>',
            },
            "skills": {
                name: {
                    "brandColor": "#365DAD", "concept": f"Icon for {name}",
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

    def test_registration_bootstrap_allows_missing_only_during_apply(self):
        pending = dict(self.config)
        pending["brand-new"] = {
            "repo": "example/other", "path": "skills/brand-new",
            "ref": "main", "sha": "b" * 40,
            "root_license": "LICENSE",
        }
        with self.assertRaisesRegex(ValueError, "mismatch"):
            sync.validate_config(pending, self.root)
        sync.validate_config(pending, self.root, allow_missing=True)
        with self.assertRaisesRegex(ValueError, "legal"):
            sync.validate_config({
                **self.config,
                "brand-new": {**pending["brand-new"], "root_license": "src/unsafe.py"},
            }, self.root, allow_missing=True)

    def test_upstream_root_license_is_bundled_from_same_commit(self):
        with mock.patch.object(sync, "ROOT", self.root), \
                mock.patch.object(sync, "git") as fetch, \
                mock.patch.object(sync, "tree_snapshot", return_value=self.old):
            def fake_git(_directory, *args):
                if args[0] == "rev-parse":
                    return b"b" * 40
                if args[0] == "show":
                    return b"MIT License\\n"
                return b""
            fetch.side_effect = fake_git
            plans = sync.fetch_snapshots({
                "demo": {**self.config["demo"], "root_license": "LICENSE"},
            })
        latest = plans[0][3]
        self.assertEqual(latest["LICENSE.upstream.txt"], ("100644", b"MIT License\\n"))
        self.assertTrue(any(call.args[1] == "show" for call in fetch.call_args_list))

    def test_per_source_size_override_is_bounded(self):
        large = {**self.config["demo"], "max_bytes": 128 * 1024 * 1024}
        sync.validate_config({"demo": large}, self.root)
        for invalid in (0, -1, "lots", 512 * 1024 * 1024):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "max_bytes"):
                sync.validate_config({"demo": {**large, "max_bytes": invalid}}, self.root)
        roomy = {**large, "max_files": 10000}
        sync.validate_config({"demo": roomy}, self.root)
        for invalid in (0, "a lot", 50000):
            with self.subTest(invalid=invalid), self.assertRaisesRegex(ValueError, "max_files"):
                sync.validate_config({"demo": {**roomy, "max_files": invalid}}, self.root)

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

    def write_plugin_group(self):
        group = {
            "displayName": "Demo Suite", "description": "Use both demo workflows together.",
            "homepage": "https://example.com/suite",
            "skills": ["external/demo", "personal/own"],
        }
        (self.root / plugin_groups.CONFIG).write_text(json.dumps({
            "schemaVersion": 1, "plugins": {"suite": group},
        }))
        path = self.root / "automation/plugin-appearance.json"
        appearance = json.loads(path.read_text())
        appearance["skills"] = {"suite": appearance["skills"]["demo"]}
        path.write_text(json.dumps(appearance))
        return group

    def test_plugin_bundle_replaces_listings_and_keeps_all_skill_files(self):
        old = generate.render_plugin_files(self.root)
        generate.check_or_write_plugin_files(self.root, old, False)
        self.write_plugin_group()
        original = sync.local_snapshot(self.external)
        grouped = generate.render_plugin_files(self.root)
        for catalog_path in (generate.MARKETPLACE, generate.CLAUDE_MARKETPLACE,
                             generate.CURSOR_MARKETPLACE):
            entries = json.loads(generate.render(self.root)[catalog_path])["plugins"]
            self.assertEqual([entry["name"] for entry in entries], ["suite"])
        self.assertEqual(grouped["plugins/suite/skills/demo/SKILL.md"], self.old["SKILL.md"])
        self.assertEqual(grouped["plugins/suite/skills/demo/scripts/run.py"], self.old["scripts/run.py"])
        self.assertIn("plugins/suite/skills/own/SKILL.md", grouped)
        manifest = json.loads(grouped["plugins/suite/plugin.json"][1])
        interface = manifest["extensions"]["com.openai"]["interface"]
        self.assertEqual(interface["displayName"], "Demo Suite")
        self.assertLessEqual(len(interface["shortDescription"]), 30)
        self.assertEqual(sync.local_snapshot(self.external), original)
        self.assertEqual(len(verify.inventory(self.root)), 2)
        with self.assertRaisesRegex(SystemExit, "stale"):
            generate.check_or_write_plugin_files(self.root, grouped, True)
        generate.check_or_write_plugin_files(self.root, grouped, False)
        self.assertFalse((self.root / "plugins/demo").exists())
        self.assertFalse((self.root / "plugins/own").exists())
        generate.check_or_write_plugin_files(self.root, grouped, True)

    def test_changing_any_bundled_skill_bumps_the_shared_plugin_once(self):
        self.write_plugin_group()
        first = generate.render_plugin_files(self.root)
        generate.check_or_write_plugin_files(self.root, first, False)
        self.assertEqual(generate.render_plugin_files(self.root), first)
        source = self.root / "skills/personal/own/SKILL.md"
        source.write_text(source.read_text() + "\nUpdated secondary workflow.\n")
        second = generate.render_plugin_files(self.root)
        self.assertEqual(json.loads(second["plugins/suite/plugin.json"][1])["version"], "1.0.1")
        generate.check_or_write_plugin_files(self.root, second, False)
        self.assertEqual(generate.render_plugin_files(self.root), second)

    def test_personal_listing_overrides_apply_only_to_the_individual_plugin(self):
        source = self.root / "skills/personal/own/SKILL.md"
        source.write_text(
            "---\nname: own\ndescription: My own skill.\nmetadata:\n"
            "  plugin-display-name: Personal Tool\n"
            "  plugin-short-description: Personal workflow\n"
            "  plugin-default-prompt: Use my workflow.\n---\n"
        )
        generated = generate.render_plugin_files(self.root)
        interface = lambda name: json.loads(generated[f"plugins/{name}/plugin.json"][1])["extensions"]["com.openai"]["interface"]
        self.assertEqual(interface("own")["displayName"], "Personal Tool")
        self.assertEqual(interface("own")["shortDescription"], "Personal workflow")
        self.assertEqual(interface("own")["defaultPrompt"], "Use my workflow.")
        self.assertEqual(interface("demo")["displayName"], "demo")
        self.assertNotIn("defaultPrompt", interface("demo"))
        self.write_plugin_group()
        generated = generate.render_plugin_files(self.root)
        self.assertEqual(interface("suite")["displayName"], "Demo Suite")
        self.assertNotIn("defaultPrompt", interface("suite"))

    def test_group_configuration_rejects_missing_duplicate_and_unsafe_members(self):
        group = self.write_plugin_group()
        cases = [
            {"suite": {**group, "skills": ["external/demo", "external/missing"]}},
            {"suite": {**group, "skills": ["external/demo", "external/demo"]}},
            {"suite": {**group, "skills": ["external/demo", "../personal/own"]}},
            {"suite": {**group, "skills": ["external/demo"]}},
            {"suite": group, "other": group},
            {"demo": group},
            {"../suite": group},
            {"suite": {**group, "homepage": "https://user:password@example.com"}},
        ]
        for groups in cases:
            with self.subTest(groups=groups):
                (self.root / plugin_groups.CONFIG).write_text(json.dumps({
                    "schemaVersion": 1, "plugins": groups,
                }))
                with self.assertRaises(ValueError):
                    plugin_groups.plugin_inventory(self.root)

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
            self.assertEqual(interface["brandColor"], "#365DAD")
            svg = generated[f"plugins/{name}/assets/icon.svg"][1]
            self.assertIn(b'viewBox="0 0 128 128"', svg)
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
            "brandColor": "#365DAD", "concept": "Research helper",
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
