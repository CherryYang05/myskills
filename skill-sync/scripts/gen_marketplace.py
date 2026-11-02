#!/usr/bin/env python3
"""Generate the GitHub workspace marketplace from the existing skill packages."""

import argparse
import json
import re

import yaml

from gen_readme import repo_root, skill_dirs


def render(root):
    plugins = []
    names = set()
    for directory in skill_dirs(root):
        path = root / directory / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
        if not match:
            raise ValueError(f"{path}: missing YAML frontmatter")
        metadata = yaml.safe_load(match.group(1))
        if not isinstance(metadata, dict):
            raise ValueError(f"{path}: frontmatter must be a mapping")
        name = metadata.get("name")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"{path}: invalid marketplace name {name!r}")
        if name in names:
            raise ValueError(f"Duplicate skill name: {name}")
        if not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
            raise ValueError(f"{path}: missing description")
        names.add(name)
        plugins.append({
            "name": name,
            "source": {"source": "local", "path": f"./{directory}"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        })
    if not plugins:
        raise ValueError("No skill packages found")
    catalog = {
        "name": "cherry-myskills",
        "interface": {"displayName": "Cherry Skills"},
        "plugins": plugins,
    }
    return json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed catalog is stale")
    args = parser.parse_args()
    root = repo_root()
    target = root / ".agents/plugins/marketplace.json"
    try:
        expected = render(root)
    except (ValueError, yaml.YAMLError) as exc:
        parser.exit(1, f"[gen_marketplace] {exc}\n")
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != expected:
            parser.exit(1, "[gen_marketplace] Catalog missing or stale; run python3 skill-sync/scripts/gen_marketplace.py\n")
        print("[gen_marketplace] Catalog matches all skill packages")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding="utf-8")
        print(f"[gen_marketplace] Updated {target}")


if __name__ == "__main__":
    main()
