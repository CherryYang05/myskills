#!/usr/bin/env python3
from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from init_profile import ProfileError, initialize, profile_items, skill_root


MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


class InitProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_every_profile_copies_its_manifest(self) -> None:
        for profile in ("simple", "medium", "complex"):
            target = self.root / profile
            outputs = initialize(
                profile=profile,
                target=target,
                project_name="Example",
                owner="Cherry",
                initialized_on="2026-08-13",
            )
            expected = {item.relative_destination for item in profile_items(profile)}
            actual = {path.relative_to(target) for path in outputs}
            self.assertEqual(actual, expected)
            self.assertTrue(all(path.is_file() for path in outputs))
            self.assert_no_broken_local_links(target)
            combined = "\n".join(
                path.read_text(encoding="utf-8")
                for path in outputs
                if path.suffix in {".md", ".py", ".yaml", ".yml"}
            )
            self.assertNotIn("{{PROJECT_NAME}}", combined)
            self.assertNotIn("{{OWNER}}", combined)
            self.assertNotIn("{{DATE}}", combined)

    def test_skill_markdown_has_no_broken_local_links(self) -> None:
        self.assert_no_broken_local_links(skill_root())

    def assert_no_broken_local_links(self, root: Path) -> None:
        broken: list[str] = []
        for document in root.rglob("*.md"):
            content = document.read_text(encoding="utf-8")
            for match in MARKDOWN_LINK.finditer(content):
                raw_target = match.group(1).strip().strip("<>")
                parsed = urlsplit(raw_target)
                if parsed.scheme or raw_target.startswith("#") or not parsed.path:
                    continue
                target = (document.parent / unquote(parsed.path)).resolve()
                if not target.exists():
                    broken.append(f"{document.relative_to(root)} -> {raw_target}")
        self.assertEqual(broken, [])

    def test_replaces_project_metadata(self) -> None:
        target = self.root / "sample"
        initialize(
            profile="simple",
            target=target,
            project_name="Halo Theme",
            owner="CherryYang05",
            initialized_on="2026-08-13",
        )
        agents = (target / "AGENTS.md").read_text(encoding="utf-8")
        project = (target / "docs/project.md").read_text(encoding="utf-8")
        self.assertIn("Halo Theme", agents)
        self.assertIn("CherryYang05", project)
        self.assertIn("2026-08-13", project)
        self.assertNotIn("{{PROJECT_NAME}}", agents + project)

    def test_conflict_prevents_all_writes(self) -> None:
        target = self.root / "existing"
        target.mkdir()
        (target / "AGENTS.md").write_text("user content\n", encoding="utf-8")

        with self.assertRaises(ProfileError):
            initialize(
                profile="medium",
                target=target,
                project_name="Example",
                owner="Cherry",
                initialized_on="2026-08-13",
            )

        self.assertEqual((target / "AGENTS.md").read_text(encoding="utf-8"), "user content\n")
        self.assertFalse((target / "docs").exists())

    def test_dry_run_writes_nothing(self) -> None:
        target = self.root / "dry-run"
        outputs = initialize(
            profile="complex",
            target=target,
            project_name="Example",
            owner="Cherry",
            initialized_on="2026-08-13",
            dry_run=True,
        )
        self.assertGreater(len(outputs), 1)
        self.assertFalse(target.exists())

    def test_git_metadata_does_not_make_target_nonempty(self) -> None:
        target = self.root / "git-only"
        (target / ".git").mkdir(parents=True)
        outputs = initialize(
            profile="simple",
            target=target,
            project_name="Example",
            owner="Cherry",
            initialized_on="2026-08-13",
        )
        self.assertTrue(outputs)
        self.assertTrue((target / ".git").is_dir())
        self.assertTrue((target / "AGENTS.md").is_file())


if __name__ == "__main__":
    unittest.main()
