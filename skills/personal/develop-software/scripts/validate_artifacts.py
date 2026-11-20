#!/usr/bin/env python3
"""Validate develop-software Feature Specs, ADRs, and Implementation Plans.

The validator intentionally checks deterministic structure and relationships only.
It does not judge design quality, test coverage, or whether reported evidence is true.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


FEATURE_ID_RE = re.compile(r"^F-\d{4}$")
ADR_ID_RE = re.compile(r"^ADR-\d{4}$")
PLAN_ID_RE = re.compile(r"^PLAN-F-\d{4}(?:-R\d{2})?$")
FEATURE_FILE_RE = re.compile(r"^(F-\d{4})-[a-z0-9][a-z0-9-]*\.md$")
ADR_FILE_RE = re.compile(r"^(ADR-\d{4})-[a-z0-9][a-z0-9-]*\.md$")
PLAN_FILE_RE = re.compile(r"^(PLAN-F-\d{4}(?:-R\d{2})?)-[a-z0-9][a-z0-9-]*\.md$")

FEATURE_STATUSES = {"draft", "accepted", "implemented", "superseded", "withdrawn"}
ADR_STATUSES = {"proposed", "accepted", "rejected", "superseded"}
PLAN_STATUSES = {"draft", "active", "completed", "abandoned", "superseded"}

REQUIRED_SECTIONS = {
    "feature": {
        "goals",
        "non-goals",
        "cross-cutting concerns",
        "architecture and coupling",
        "acceptance criteria",
        "documentation and release impact",
        "open questions",
    },
    "adr": {
        "context",
        "considered options",
        "decision",
        "consequences",
        "migration and rollback",
        "validation",
    },
    "plan": {
        "preconditions",
        "vertical slices",
        "cross-cutting checks",
        "final verification",
        "remaining work and known limitations",
    },
}


@dataclass(frozen=True)
class Issue:
    level: str
    path: str
    message: str


@dataclass
class Report:
    artifacts: int = 0
    issues: list[Issue] = field(default_factory=list)

    def error(self, path: Path, message: str) -> None:
        self.issues.append(Issue("error", str(path), message))

    def warning(self, path: Path, message: str) -> None:
        self.issues.append(Issue("warning", str(path), message))

    @property
    def errors(self) -> int:
        return sum(issue.level == "error" for issue in self.issues)

    @property
    def warnings(self) -> int:
        return sum(issue.level == "warning" for issue in self.issues)


@dataclass
class Artifact:
    kind: str
    path: Path
    metadata: dict[str, Any]
    body: str

    @property
    def identifier(self) -> str | None:
        key = {"feature": "feature_id", "adr": "adr_id", "plan": "plan_id"}[self.kind]
        value = self.metadata.get(key)
        return value if isinstance(value, str) else None

    @property
    def status(self) -> str | None:
        value = self.metadata.get("status")
        return value.lower() if isinstance(value, str) else None


@dataclass(frozen=True)
class Config:
    root: Path
    spec_dir: Path
    adr_dir: Path
    plan_dir: Path
    strict_sections: bool = False


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value == "[]":
        return []
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(part) for part in inner.split(",")]
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str, str | None]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, "missing YAML front matter"
    try:
        end = next(index for index in range(1, len(lines)) if lines[index].strip() == "---")
    except StopIteration:
        return None, text, "unterminated YAML front matter"

    metadata: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in lines[1:end]:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        list_match = re.match(r"^\s+-\s+(.+?)\s*$", raw_line)
        if list_match and current_list_key:
            current = metadata.setdefault(current_list_key, [])
            if not isinstance(current, list):
                return None, text, f"front matter key '{current_list_key}' mixes scalar and list values"
            current.append(parse_scalar(list_match.group(1)))
            continue
        key_match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", raw_line)
        if not key_match:
            return None, text, f"unsupported front matter line: {raw_line.strip()}"
        key, raw_value = key_match.groups()
        if key in metadata:
            return None, text, f"duplicate front matter key '{key}'"
        if raw_value:
            metadata[key] = parse_scalar(raw_value)
            current_list_key = None
        else:
            metadata[key] = []
            current_list_key = key
    return metadata, "\n".join(lines[end + 1 :]), None


def discover(directory: Path, kind: str) -> Iterable[Path]:
    if not directory.is_dir():
        return []
    key = {"feature": "feature_id", "adr": "adr_id", "plan": "plan_id"}[kind]
    paths: list[Path] = []
    for path in sorted(directory.rglob("*.md")):
        if path.name.lower() in {"readme.md", "index.md"}:
            continue
        text = path.read_text(encoding="utf-8")
        metadata, _, _ = parse_frontmatter(text)
        if metadata and key in metadata:
            paths.append(path)
            continue
        patterns = {"feature": FEATURE_FILE_RE, "adr": ADR_FILE_RE, "plan": PLAN_FILE_RE}
        if patterns[kind].match(path.name):
            paths.append(path)
    return paths


def load_artifact(path: Path, kind: str, report: Report) -> Artifact | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        report.error(path, f"cannot read UTF-8 Markdown: {exc}")
        return None
    metadata, body, error = parse_frontmatter(text)
    if error or metadata is None:
        report.error(path, error or "invalid front matter")
        return None
    report.artifacts += 1
    return Artifact(kind, path, metadata, body)


def headings(body: str) -> set[str]:
    result: set[str] = set()
    for line in body.splitlines():
        match = re.match(r"^#{2,6}\s+(.+?)\s*$", line)
        if match:
            heading = re.sub(r"[`*_]", "", match.group(1)).strip().lower()
            result.add(heading)
    return result


def check_required_sections(artifact: Artifact, report: Report, strict: bool) -> None:
    missing = sorted(REQUIRED_SECTIONS[artifact.kind] - headings(artifact.body))
    for section in missing:
        message = f"missing standard section '## {section.title()}'"
        if strict:
            report.error(artifact.path, message)
        else:
            report.warning(artifact.path, message)


def check_identity(artifact: Artifact, report: Report) -> None:
    rules = {
        "feature": ("feature_id", FEATURE_ID_RE, FEATURE_FILE_RE, FEATURE_STATUSES, ("milestone",)),
        "adr": ("adr_id", ADR_ID_RE, ADR_FILE_RE, ADR_STATUSES, ()),
        "plan": ("plan_id", PLAN_ID_RE, PLAN_FILE_RE, PLAN_STATUSES, ("related_feature",)),
    }
    id_key, id_pattern, filename_pattern, statuses, extra_keys = rules[artifact.kind]
    for key in (id_key, "status", *extra_keys):
        if key not in artifact.metadata:
            report.error(artifact.path, f"missing required front matter key '{key}'")

    identifier = artifact.identifier
    if not identifier or not id_pattern.match(identifier):
        report.error(artifact.path, f"invalid {id_key}: expected {id_pattern.pattern}")
    filename_match = filename_pattern.match(artifact.path.name)
    if not filename_match:
        report.error(artifact.path, "filename must start with the full ID and use a lowercase kebab-case slug")
    elif identifier and filename_match.group(1) != identifier:
        report.error(artifact.path, f"filename ID '{filename_match.group(1)}' does not match {id_key} '{identifier}'")

    status = artifact.status
    if status not in statuses:
        report.error(artifact.path, f"invalid status '{status}'; expected one of {sorted(statuses)}")

    if re.search(r"<[^>]+>|\{[a-z][a-z0-9-]{2,}\}|\b(?:F|ADR)-NNNN\b", artifact.body):
        report.warning(artifact.path, "contains template placeholders")


def as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value if item is not None]
    return [str(value)]


def check_terminal_content(artifact: Artifact, report: Report) -> None:
    if artifact.kind == "feature" and artifact.status == "implemented":
        if re.search(r"^\s*[-*]\s+\[\s\]", artifact.body, re.MULTILINE):
            report.error(artifact.path, "implemented Feature contains unchecked checklist items")
        if not artifact.metadata.get("implemented_in"):
            report.warning(artifact.path, "implemented Feature has no implemented_in reference")

    if artifact.kind == "plan" and artifact.status == "completed":
        if re.search(r"^\s*[-*]\s+\[\s\]", artifact.body, re.MULTILINE):
            report.error(artifact.path, "completed Plan contains unchecked checklist items")
        slice_statuses = [
            value.lower()
            for value in re.findall(r"^Status:\s*([A-Za-z_-]+)\s*$", artifact.body, re.MULTILINE)
        ]
        invalid = sorted({value for value in slice_statuses if value not in {"completed", "skipped"}})
        if invalid:
            report.error(artifact.path, f"completed Plan has non-terminal slice status: {', '.join(invalid)}")
        if not slice_statuses:
            report.warning(artifact.path, "completed Plan has no explicit slice Status lines")
        if re.search(r"\|\s*pending\s*\|", artifact.body, re.IGNORECASE):
            report.error(artifact.path, "completed Plan contains a pending verification result")


def check_duplicate_ids(artifacts: list[Artifact], report: Report) -> None:
    seen: dict[tuple[str, str], Path] = {}
    for artifact in artifacts:
        if not artifact.identifier:
            continue
        key = (artifact.kind, artifact.identifier)
        if key in seen:
            report.error(artifact.path, f"duplicate {artifact.identifier}; first defined in {seen[key]}")
        else:
            seen[key] = artifact.path


def check_references(artifacts: list[Artifact], report: Report) -> None:
    by_kind: dict[str, dict[str, Artifact]] = {"feature": {}, "adr": {}, "plan": {}}
    for artifact in artifacts:
        if artifact.identifier:
            by_kind[artifact.kind][artifact.identifier] = artifact

    active_by_feature: dict[str, list[Artifact]] = {}
    for artifact in artifacts:
        if artifact.kind == "feature":
            for adr_id in as_string_list(artifact.metadata.get("related_adrs")):
                if adr_id not in by_kind["adr"]:
                    report.error(artifact.path, f"related ADR '{adr_id}' does not exist")

        if artifact.kind == "plan":
            feature_id = artifact.metadata.get("related_feature")
            if not isinstance(feature_id, str) or feature_id not in by_kind["feature"]:
                report.error(artifact.path, f"related Feature '{feature_id}' does not exist")
                continue
            expected_plan_prefix = f"PLAN-{feature_id}"
            if artifact.identifier and not re.match(
                rf"^{re.escape(expected_plan_prefix)}(?:-R\d{{2}})?$", artifact.identifier
            ):
                report.error(
                    artifact.path,
                    f"plan_id must be '{expected_plan_prefix}' or a revision for related_feature '{feature_id}'",
                )
            feature = by_kind["feature"][feature_id]
            if artifact.status == "active":
                active_by_feature.setdefault(feature_id, []).append(artifact)
                if feature.status != "accepted":
                    report.error(artifact.path, f"active Plan requires accepted Feature; found '{feature.status}'")
            if artifact.status == "completed" and feature.status != "implemented":
                report.error(artifact.path, f"completed Plan requires implemented Feature; found '{feature.status}'")

    for feature_id, plans in active_by_feature.items():
        if len(plans) > 1:
            paths = ", ".join(str(plan.path) for plan in plans)
            report.error(plans[-1].path, f"Feature {feature_id} has multiple active Plans: {paths}")

    for kind, id_map in by_kind.items():
        for identifier, artifact in id_map.items():
            successor = artifact.metadata.get("superseded_by")
            if artifact.status == "superseded" and not successor:
                report.error(artifact.path, "superseded Artifact must set superseded_by")
            if successor and artifact.status != "superseded":
                report.error(artifact.path, "Artifact with superseded_by must have status 'superseded'")
            if successor:
                if successor == identifier:
                    report.error(artifact.path, "superseded_by cannot reference itself")
                elif successor not in id_map:
                    report.error(artifact.path, f"superseded_by target '{successor}' does not exist")
                elif id_map[successor].metadata.get("supersedes") != identifier:
                    report.error(
                        artifact.path,
                        f"superseded_by target '{successor}' must set supersedes: {identifier}",
                    )

            predecessor = artifact.metadata.get("supersedes")
            if predecessor:
                if predecessor == identifier:
                    report.error(artifact.path, "supersedes cannot reference itself")
                elif predecessor not in id_map:
                    report.error(artifact.path, f"supersedes target '{predecessor}' does not exist")
                elif id_map[predecessor].metadata.get("superseded_by") != identifier:
                    report.error(
                        artifact.path,
                        f"supersedes target '{predecessor}' must set superseded_by: {identifier}",
                    )

    check_supersession_cycles(by_kind, report)


def check_supersession_cycles(by_kind: dict[str, dict[str, Artifact]], report: Report) -> None:
    for id_map in by_kind.values():
        for start, artifact in id_map.items():
            visited: set[str] = set()
            current = start
            while current in id_map:
                if current in visited:
                    report.error(artifact.path, f"supersession cycle detected from '{start}'")
                    break
                visited.add(current)
                successor = id_map[current].metadata.get("superseded_by")
                if not isinstance(successor, str) or not successor:
                    break
                current = successor


def validate_repository(config: Config) -> Report:
    report = Report()
    artifacts: list[Artifact] = []
    for directory, kind in (
        (config.spec_dir, "feature"),
        (config.adr_dir, "adr"),
        (config.plan_dir, "plan"),
    ):
        for path in discover(directory, kind):
            artifact = load_artifact(path, kind, report)
            if artifact:
                artifacts.append(artifact)

    for artifact in artifacts:
        check_identity(artifact, report)
        check_required_sections(artifact, report, config.strict_sections)
        check_terminal_content(artifact, report)
    check_duplicate_ids(artifacts, report)
    check_references(artifacts, report)
    return report


def relative_or_absolute(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="project root (default: current directory)")
    parser.add_argument("--spec-dir", default="docs/specs", help="Feature Spec directory relative to root")
    parser.add_argument("--adr-dir", default="docs/adr", help="ADR directory relative to root")
    parser.add_argument("--plan-dir", default="docs/plans", help="Implementation Plan directory relative to root")
    parser.add_argument(
        "--strict-sections",
        action="store_true",
        help="treat missing standard template sections as errors instead of warnings",
    )
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: project root does not exist or is not a directory: {root}", file=sys.stderr)
        return 2
    config = Config(
        root=root,
        spec_dir=relative_or_absolute(root, args.spec_dir),
        adr_dir=relative_or_absolute(root, args.adr_dir),
        plan_dir=relative_or_absolute(root, args.plan_dir),
        strict_sections=args.strict_sections,
    )
    report = validate_repository(config)
    issues = sorted(report.issues, key=lambda issue: (issue.path, issue.level, issue.message))

    if args.json:
        print(
            json.dumps(
                {
                    "artifacts": report.artifacts,
                    "errors": report.errors,
                    "warnings": report.warnings,
                    "issues": [issue.__dict__ for issue in issues],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        for issue in issues:
            print(f"{issue.level.upper()}: {issue.path}: {issue.message}")
        print(
            f"Validated {report.artifacts} artifact(s): "
            f"{report.errors} error(s), {report.warnings} warning(s)."
        )
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
