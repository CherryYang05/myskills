"""Regression tests for external Skill frontmatter compatibility."""

import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_external_skills.py"
SPEC = importlib.util.spec_from_file_location("validate_external_skills", SCRIPT)
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ExternalSkillValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.skill_dir = Path(self.temp.name) / "example"
        self.skill_dir.mkdir()

    def write_skill(self, extra=""):
        (self.skill_dir / "SKILL.md").write_text(
            "---\nname: example\ndescription: Example skill for validation\n"
            + extra
            + "---\n\n# Example\n",
            encoding="utf-8",
        )

    def test_documented_user_invocable_boolean_is_allowed(self):
        for value in ("true", "false"):
            with self.subTest(value=value):
                self.write_skill(f"user-invocable: {value}\n")
                ok, message = validator.validate_external_skill(self.skill_dir)
                self.assertTrue(ok, message)

    def test_user_invocable_rejects_strings_and_other_values(self):
        for value in ('"false"', "0", "[]", "null"):
            with self.subTest(value=value):
                self.write_skill(f"user-invocable: {value}\n")
                ok, message = validator.validate_external_skill(self.skill_dir)
                self.assertFalse(ok)
                self.assertIn("YAML boolean", message)

    def test_unknown_frontmatter_keys_still_fail(self):
        self.write_skill("user-invocable: false\nundocumented-field: true\n")
        ok, message = validator.validate_external_skill(self.skill_dir)
        self.assertFalse(ok)
        self.assertIn("undocumented-field", message)

    def test_baseline_schema_validation_still_applies(self):
        self.write_skill("user-invocable: false\n")
        content = (self.skill_dir / "SKILL.md").read_text(encoding="utf-8")
        (self.skill_dir / "SKILL.md").write_text(
            content.replace("name: example", "name: Invalid Name"),
            encoding="utf-8",
        )
        ok, message = validator.validate_external_skill(self.skill_dir)
        self.assertFalse(ok)
        self.assertIn("kebab-case", message)

    def test_without_extension_uses_original_validator(self):
        self.write_skill()
        ok, message = validator.validate_external_skill(self.skill_dir)
        self.assertTrue(ok, message)


if __name__ == "__main__":
    unittest.main()
