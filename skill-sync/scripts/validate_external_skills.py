#!/usr/bin/env python3
"""Validate external Skill frontmatter across Agent Skills and Claude Code.

The reference quick_validate.py belongs to the upstream-managed skill-creator
package. Keep compatibility rules here so upstream synchronization cannot
overwrite local CI fixes.
"""

import json
import re
import sys
import tempfile
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "skill-creator" / "scripts"))
from quick_validate import validate_skill as validate_base_skill  # noqa: E402


# Documented Claude Code fields not supported by the reference Agent Skills
# validator. Add further extensions only with an explicit schema and tests.
EXTENSION_FIELDS = {"user-invocable": bool}
FRONTMATTER = re.compile(r"\A---\r?\n(.*?)\r?\n---(?=\r?\n|\Z)", re.DOTALL)


def validate_external_skill(skill_dir):
    """Apply base validation, allowing known extensions with strict types."""
    skill_dir = Path(skill_dir)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return validate_base_skill(skill_dir)

    content = skill_md.read_text(encoding="utf-8")
    match = FRONTMATTER.match(content)
    if not match:
        return validate_base_skill(skill_dir)

    try:
        fields = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return validate_base_skill(skill_dir)
    if not isinstance(fields, dict):
        return validate_base_skill(skill_dir)

    for key, expected_type in EXTENSION_FIELDS.items():
        if key in fields and type(fields[key]) is not expected_type:
            return False, f"{key} must be a YAML boolean (true or false)"

    if not any(key in fields for key in EXTENSION_FIELDS):
        return validate_base_skill(skill_dir)

    # Only exclude recognized extensions for the baseline validator.
    # Unknown fields still fail rather than being silently accepted.
    baseline_fields = {
        key: value for key, value in fields.items()
        if key not in EXTENSION_FIELDS
    }
    with tempfile.TemporaryDirectory(prefix="skill-frontmatter-") as temp:
        normalized = Path(temp) / "SKILL.md"
        normalized.write_text(
            "---\n"
            + yaml.safe_dump(baseline_fields, allow_unicode=True, sort_keys=False)
            + "---\n"
            + content[match.end():].lstrip("\r\n"),
            encoding="utf-8",
        )
        return validate_base_skill(Path(temp))


def main():
    configured = json.loads(
        (ROOT / "skill-sync" / "upstreams.json").read_text(encoding="utf-8")
    )
    failed = []
    for name in sorted(configured):
        ok, message = validate_external_skill(ROOT / name)
        print(f"{name}: {message}", flush=True)
        if not ok:
            failed.append(name)
    if failed:
        raise SystemExit(f"Invalid external Skill(s): {', '.join(failed)}")


if __name__ == "__main__":
    main()
