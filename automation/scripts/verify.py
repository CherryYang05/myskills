#!/usr/bin/env python3
"""Validate Skill inventory, frontmatter, upstream registry and tracked artifacts."""
import argparse
import re
import subprocess
from pathlib import Path

import yaml

from sync import ROOT, EXTERNAL, load_config

SKILLS = "skills"
FRONT = re.compile(r"\A---\r?\n(.*?)\r?\n---(?=\r?\n|\Z)", re.DOTALL)
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools", "user-invocable"}


def read_frontmatter(file):
    text = file.read_text(encoding="utf-8")
    match = FRONT.match(text)
    if match is None:
        raise ValueError(f"{file}: SKILL.md missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    if not isinstance(data, dict):
        raise ValueError(f"{file}: YAML metadata must be a mapping")
    name, desc = data.get("name"), data.get("description")
    if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
        raise ValueError(f"{file}: invalid Skill name {name!r}")
    if not isinstance(desc, str) or not desc.strip() or len(desc) > 1024:
        raise ValueError(f"{file}: invalid description")
    if "<" in desc or ">" in desc:
        raise ValueError(f"{file}: description may not contain angle brackets")
    if "user-invocable" in data and type(data["user-invocable"]) is not bool:
        raise ValueError(f"{file}: user-invocable must be boolean")
    if "metadata" in data and not isinstance(data["metadata"], dict):
        raise ValueError(f"{file}: metadata must be a mapping")
    if "compatibility" in data and (not isinstance(data["compatibility"], str)
                                    or len(data["compatibility"]) > 500):
        raise ValueError(f"{file}: invalid compatibility")
    if "allowed-tools" in data and not isinstance(data["allowed-tools"], str):
        raise ValueError(f"{file}: invalid allowed-tools")
    return data


def inventory(root=ROOT):
    packages = []
    names = set()
    for group in ("external", "personal"):
        directory = root / SKILLS / group
        if not directory.is_dir():
            raise ValueError(f"Missing required Skill category: {group}")
        for path in sorted(directory.iterdir()):
            if not path.is_dir() or path.name.startswith("."):
                continue
            skill = path / "SKILL.md"
            if not skill.is_file():
                raise ValueError(f"Unexpected directory without SKILL.md: {path}")
            fields = read_frontmatter(skill)
            if group == "external" and set(fields) - FIELDS:
                raise ValueError(f"Unsupported external metadata: {path}: {sorted(set(fields) - FIELDS)}")
            name = fields["name"]
            if name in names:
                raise ValueError(f"Duplicate Skill name: {name}")
            names.add(name)
            packages.append((group, path.name, fields))
    config = load_config(root)
    external = {directory for group, directory, _ in packages if group == "external"}
    if external != set(config):
        raise ValueError("External Skill source registry disagrees with packages")
    if not packages:
        raise ValueError("No Skills found")
    return packages


def no_tracked_artifacts(root=ROOT):
    tracked = subprocess.check_output(["git", "-C", str(root), "ls-files", "-z"]).decode().split("\0")
    forbidden = [
        path for path in tracked if path and (
            "__pycache__" in Path(path).parts or ".pytest_cache" in Path(path).parts
            or "node_modules" in Path(path).parts or Path(path).suffix in {".pyc", ".pyo"}
            or Path(path).name == ".DS_Store"
        )
    ]
    if forbidden:
        raise ValueError("Tracked runtime files: " + ", ".join(forbidden))


def main():
    packages = inventory()
    no_tracked_artifacts()
    print(f"Validated {len(packages)} Skill packages (external: {sum(g == 'external' for g, _, _ in packages)}).")


if __name__ == "__main__":
    main()
