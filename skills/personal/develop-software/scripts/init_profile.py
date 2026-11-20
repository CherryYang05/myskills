#!/usr/bin/env python3
"""Copy one fixed develop-software SDD profile into a new project.

The command is intentionally conservative: it checks every destination first and
refuses to write anything when a conflict exists. Existing repositories should be
migrated by an agent that can reconcile their current sources of truth.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


PROFILES = ("simple", "medium", "complex")
TEXT_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".py"}


@dataclass(frozen=True)
class CopyItem:
    source: Path
    relative_destination: Path


class ProfileError(RuntimeError):
    """Raised when a profile cannot be copied safely."""


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def profile_root(profile: str) -> Path:
    if profile not in PROFILES:
        raise ProfileError(f"unknown profile '{profile}'; expected one of {', '.join(PROFILES)}")
    root = skill_root() / "assets" / "profiles" / profile
    if not root.is_dir():
        raise ProfileError(f"profile assets are missing: {root}")
    return root


def profile_items(profile: str) -> list[CopyItem]:
    root = profile_root(profile)
    items = [
        CopyItem(source=path, relative_destination=path.relative_to(root))
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]
    if profile == "complex":
        items.append(
            CopyItem(
                source=skill_root() / "scripts" / "validate_artifacts.py",
                relative_destination=Path("scripts/validate_sdd.py"),
            )
        )
    return sorted(items, key=lambda item: str(item.relative_destination))


def ensure_safe_target(target: Path) -> Path:
    resolved = target.expanduser().resolve()
    if resolved == Path(resolved.anchor):
        raise ProfileError("refusing to initialize a filesystem root")
    source = skill_root().resolve()
    if resolved == source or source in resolved.parents or resolved in source.parents:
        raise ProfileError("target cannot be the develop-software skill directory or one of its parents")
    if resolved.exists():
        unexpected = sorted(path.name for path in resolved.iterdir() if path.name != ".git")
        if unexpected:
            formatted = ", ".join(unexpected)
            raise ProfileError(
                "target is not empty; migrate existing repositories without the copy script "
                f"(found: {formatted})"
            )
    return resolved


def replacements(project_name: str, owner: str, initialized_on: str) -> dict[str, str]:
    return {
        "{{PROJECT_NAME}}": project_name,
        "{{OWNER}}": owner,
        "{{DATE}}": initialized_on,
    }


def render(source: Path, values: dict[str, str]) -> bytes:
    if source.suffix.lower() not in TEXT_SUFFIXES:
        return source.read_bytes()
    text = source.read_text(encoding="utf-8")
    for token, value in values.items():
        text = text.replace(token, value)
    return text.encode("utf-8")


def conflicts(items: Iterable[CopyItem], target: Path) -> list[Path]:
    return [target / item.relative_destination for item in items if (target / item.relative_destination).exists()]


def initialize(
    profile: str,
    target: Path,
    project_name: str,
    owner: str,
    initialized_on: str,
    dry_run: bool = False,
) -> list[Path]:
    destination = ensure_safe_target(target)
    items = profile_items(profile)
    existing = conflicts(items, destination)
    if existing:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise ProfileError(f"refusing to overwrite existing paths:\n{formatted}")

    outputs = [destination / item.relative_destination for item in items]
    if dry_run:
        return outputs

    values = replacements(project_name, owner, initialized_on)
    destination.mkdir(parents=True, exist_ok=True)
    for item, output in zip(items, outputs, strict=True):
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(render(item.source, values))
        shutil.copymode(item.source, output)
    return outputs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=PROFILES)
    parser.add_argument("target", type=Path, help="new project root")
    parser.add_argument("--project-name", help="project name; defaults to the target directory name")
    parser.add_argument("--owner", default="project owner", help="project owner recorded in templates")
    parser.add_argument("--date", default=date.today().isoformat(), help="initialization date in YYYY-MM-DD")
    parser.add_argument("--dry-run", action="store_true", help="list output paths without writing")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    project_name = args.project_name or args.target.expanduser().resolve().name
    try:
        outputs = initialize(
            profile=args.profile,
            target=args.target,
            project_name=project_name,
            owner=args.owner,
            initialized_on=args.date,
            dry_run=args.dry_run,
        )
    except (OSError, UnicodeError, ProfileError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {len(outputs)} file(s) for the {args.profile} SDD profile:")
    for output in outputs:
        print(f"- {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
