#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from validate_artifacts import Config, validate_repository


FEATURE_SECTIONS = """
## Goals
## Non-goals
## Cross-cutting concerns
## Architecture and coupling
## Acceptance criteria
## Documentation and release impact
## Open questions
"""

ADR_SECTIONS = """
## Context
## Considered options
## Decision
## Consequences
## Migration and rollback
## Validation
"""

PLAN_SECTIONS = """
## Preconditions
## Vertical slices
## Cross-cutting checks
## Final verification
## Remaining work and known limitations
"""


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        for directory in ("docs/specs", "docs/adr", "docs/plans"):
            (self.root / directory).mkdir(parents=True, exist_ok=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write(self, relative: str, content: str) -> None:
        (self.root / relative).write_text(content.strip() + "\n", encoding="utf-8")

    def validate(self):
        return validate_repository(
            Config(
                root=self.root,
                spec_dir=self.root / "docs/specs",
                adr_dir=self.root / "docs/adr",
                plan_dir=self.root / "docs/plans",
                strict_sections=True,
            )
        )

    def valid_feature(self, status: str = "accepted", implemented_in: str = "null") -> str:
        return f"""
---
status: {status}
feature_id: F-0001
milestone: P1
implemented_in: {implemented_in}
related_adrs:
  - ADR-0001
superseded_by: null
---
{FEATURE_SECTIONS}
"""

    def valid_adr(self) -> str:
        return f"""
---
status: accepted
adr_id: ADR-0001
superseded_by: null
---
{ADR_SECTIONS}
"""

    def test_valid_completed_feature_and_plan(self) -> None:
        self.write("docs/specs/F-0001-example.md", self.valid_feature("implemented", '"abc123"'))
        self.write("docs/adr/ADR-0001-example.md", self.valid_adr())
        self.write(
            "docs/plans/PLAN-F-0001-example.md",
            f"""
---
status: completed
plan_id: PLAN-F-0001
related_feature: F-0001
superseded_by: null
---
{PLAN_SECTIONS}
### VS-01: behavior
Status: completed
- [x] verified
| command | expected | actual | passed |
""",
        )
        report = self.validate()
        self.assertEqual(report.errors, 0, report.issues)

    def test_filename_id_mismatch_is_error(self) -> None:
        self.write("docs/specs/F-0002-example.md", self.valid_feature())
        self.write("docs/adr/ADR-0001-example.md", self.valid_adr())
        report = self.validate()
        self.assertTrue(any("does not match" in issue.message for issue in report.issues))

    def test_multiple_active_plans_are_error(self) -> None:
        self.write("docs/specs/F-0001-example.md", self.valid_feature())
        self.write("docs/adr/ADR-0001-example.md", self.valid_adr())
        for slug in ("one", "two"):
            self.write(
                f"docs/plans/PLAN-F-0001-{slug}.md",
                f"""
---
status: active
plan_id: PLAN-F-0001
related_feature: F-0001
superseded_by: null
---
{PLAN_SECTIONS}
""",
            )
        report = self.validate()
        self.assertTrue(any("multiple active Plans" in issue.message for issue in report.issues))

    def test_completed_plan_with_unchecked_item_is_error(self) -> None:
        self.write("docs/specs/F-0001-example.md", self.valid_feature("implemented", '"abc123"'))
        self.write("docs/adr/ADR-0001-example.md", self.valid_adr())
        self.write(
            "docs/plans/PLAN-F-0001-example.md",
            f"""
---
status: completed
plan_id: PLAN-F-0001
related_feature: F-0001
superseded_by: null
---
{PLAN_SECTIONS}
### VS-01: behavior
Status: completed
- [ ] not done
""",
        )
        report = self.validate()
        self.assertTrue(any("unchecked" in issue.message for issue in report.issues))

    def test_missing_supersession_target_is_error(self) -> None:
        self.write(
            "docs/specs/F-0001-example.md",
            f"""
---
status: superseded
feature_id: F-0001
milestone: P1
related_adrs: []
superseded_by: F-0002
---
{FEATURE_SECTIONS}
""",
        )
        report = self.validate()
        self.assertTrue(any("does not exist" in issue.message for issue in report.issues))

    def test_plan_revision_can_supersede_previous_plan(self) -> None:
        self.write("docs/specs/F-0001-example.md", self.valid_feature())
        self.write("docs/adr/ADR-0001-example.md", self.valid_adr())
        self.write(
            "docs/plans/PLAN-F-0001-old.md",
            f"""
---
status: superseded
plan_id: PLAN-F-0001
related_feature: F-0001
supersedes: null
superseded_by: PLAN-F-0001-R02
---
{PLAN_SECTIONS}
""",
        )
        self.write(
            "docs/plans/PLAN-F-0001-R02-new.md",
            f"""
---
status: active
plan_id: PLAN-F-0001-R02
related_feature: F-0001
supersedes: PLAN-F-0001
superseded_by: null
---
{PLAN_SECTIONS}
""",
        )
        report = self.validate()
        self.assertEqual(report.errors, 0, report.issues)


if __name__ == "__main__":
    unittest.main()
