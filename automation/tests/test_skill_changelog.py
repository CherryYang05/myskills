import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from skill_changelog import record_path, validate


class SkillChangelogTests(unittest.TestCase):
    def test_each_changed_skill_requires_an_append_and_keeps_history(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            packages = [("personal", name, {}) for name in ("alpha", "beta")]
            skills = [root / f"skills/personal/{name}/SKILL.md" for _, name, _ in packages]
            logs = [root / record_path(group, name) for group, name, _ in packages]
            baseline = "# 修订记录\n\n- 2026-11-10 — 建立修订基线。\n"
            for path in skills + logs:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(baseline if path in logs else "original\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "."], cwd=root, check=True)
            subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                            "commit", "-qm", "baseline"], cwd=root, check=True)

            for skill in skills:
                skill.write_text("updated\n", encoding="utf-8")
            entry = "- 2026-11-11 — 补充版本适用范围。\n"
            logs[0].write_text(baseline + entry, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "append.*beta.md"):
                validate(root, packages, "HEAD")
            logs[1].write_text(baseline + entry, encoding="utf-8")
            self.assertEqual(validate(root, packages, "HEAD"), 2)
            logs[0].write_text("# 修订记录\n\n" + entry, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Keep prior.*alpha.md"):
                validate(root, packages, "HEAD")
