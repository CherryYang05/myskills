#!/usr/bin/env python3
"""Render README, marketplaces, plugin icons and packages from canonical Skills."""
import argparse
import json
import re
import shutil
from pathlib import Path

from sync import ROOT, CONFIG, local_snapshot
from verify import inventory
from appearance import load_config as load_appearance_config, render_icon

MARKETPLACE = ".agents/plugins/marketplace.json"
CLAUDE_MARKETPLACE = ".claude-plugin/marketplace.json"
CURSOR_MARKETPLACE = ".cursor-plugin/marketplace.json"
SKILLS_CLI_CONFIG = "skills.sh.json"
README = "README.md"

# Source Skills remain unchanged; these folders only install the source on
# other platforms and do not belong in a ChatGPT plugin package.
OTHER_PLATFORM_INSTALL_DIRS = frozenset({".claude-plugin", ".cursor-plugin"})


def source_link(source):
    url = f"https://github.com/{source['repo']}"
    path = source["path"]
    if path:
        url += f"/tree/{source['ref']}/{path}"
    return url


def short_description(description, limit=88):
    """Compact README summaries and avoid breaking English words."""
    text = re.sub(r"\s+", " ", description).strip()
    text = re.split(r"\. |。", text, maxsplit=1)[0].strip()
    if len(text) > limit:
        shortened = text[:limit]
        if (shortened[-1].isascii() and shortened[-1].isalnum()
                and text[limit].isascii() and text[limit].isalnum()):
            last_space = shortened.rfind(" ")
            if last_space > limit // 2:
                shortened = shortened[:last_space]
        text = shortened.rstrip(" ,.;:，。；：、") + "…"
    return text.replace("|", r"\|").replace("`", "'")


def render(root=ROOT):
    packages = inventory(root)
    config = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    catalog = {"name": "cherry-myskills", "interface": {"displayName": "Cherry Skills"}, "plugins": []}
    claude_catalog = {
        "name": "cherry-skills",
        "description": "Curated external and personal Agent Skills",
        "owner": {"name": "CherryYang05", "url": "https://github.com/CherryYang05"},
        "plugins": [],
    }
    cursor_catalog = {
        "name": "cherry-skills",
        "owner": {"name": "CherryYang05"},
        "metadata": {"description": "Curated portable Agent Skills"},
        "plugins": [],
    }
    cli_paths = ["./skills/external", "./skills/personal"]
    rows = ["| Skill | 类型 | 来源 / 当前版本 | 说明 |", "|---|---|---|---|"]
    for group, directory, fields in packages:
        name = fields["name"]
        path = f"./skills/{group}/{directory}"
        plugin_path = f"./plugins/{name}"
        catalog["plugins"].append({
            "name": name,
            "source": {"source": "local", "path": plugin_path},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        })
        # Claude Code takes plugin names from marketplace entries when there is
        # no .claude-plugin/plugin.json; Cursor accepts root Agent Plugins.
        # Both platforms use the same generated self-contained plugin package.
        marketplace_desc = re.sub(r"\s+", " ", fields["description"]).strip()
        claude_catalog["plugins"].append({
            "name": name, "source": plugin_path, "description": marketplace_desc
        })
        cursor_catalog["plugins"].append({
            "name": name, "source": plugin_path, "description": marketplace_desc
        })
        desc = short_description(fields["description"])
        label = f"[{name}]({path})"
        if group == "external":
            info = config[directory]
            origin = f"[{info['repo']}]({source_link(info)}) · `{info['sha'][:12]}`"
            # GitHub Markdown tables may break Chinese at every character;
            # word-joiner entities keep the type label on one line without custom CSS.
            category = "外&#8288;部&#8288;同&#8288;步"
        else:
            origin = "自研"
            category = "自研"
        rows.append(f"| {label} | {category} | {origin} | {desc} |")
    template = (root / "automation/templates/README.md.tpl").read_text(encoding="utf-8")
    if template.count("{{SKILL_TABLE}}") != 1:
        raise ValueError("README template must contain exactly one {{SKILL_TABLE}} placeholder")
    readme = template.replace("{{SKILL_TABLE}}", "\n".join(rows))
    return {
        README: readme,
        MARKETPLACE: json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        CLAUDE_MARKETPLACE: json.dumps(claude_catalog, ensure_ascii=False, indent=2) + "\n",
        CURSOR_MARKETPLACE: json.dumps(cursor_catalog, ensure_ascii=False, indent=2) + "\n",
        SKILLS_CLI_CONFIG: json.dumps({
            "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
            "paths": cli_paths,
        }, ensure_ascii=False, indent=2) + "\n",
    }



def omit_from_chatgpt_plugin(relative):
    """Exclude only root-level, platform-specific installer metadata."""
    return relative.split("/", 1)[0] in OTHER_PLATFORM_INSTALL_DIRS


def next_plugin_version(root, plugin_root, name, candidate):
    """Bump a patch version only when distributable package bytes change.

    The existing generated package is the release baseline. This keeps version
    state within the already committed artifact: no second release registry.
    """
    directory = root / plugin_root
    manifest_path = directory / "plugin.json"
    if not manifest_path.exists():
        return "1.0.0"
    old_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(old_manifest, dict) or old_manifest.get("name") != name:
        raise ValueError(f"Invalid existing plugin identity: {manifest_path}")
    version = old_manifest.get("version")
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", version):
        raise ValueError(f"Expected release version MAJOR.MINOR.PATCH: {manifest_path}")
    proposed = dict(candidate)
    current_manifest = json.loads(candidate["plugin.json"][1])
    current_manifest["version"] = version
    proposed["plugin.json"] = (
        "100644", (json.dumps(current_manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    )
    if local_snapshot(directory) == proposed:
        return version
    major, minor, patch = map(int, version.split("."))
    return f"{major}.{minor}.{patch + 1}"


def render_plugin_files(root=ROOT):
    """Produce portable installable plugin packages from canonical Skill sources.

    The generated plugins/ tree contains ordinary files so a downloaded plugin
    remains self-contained; source Skill packages are never rewritten.
    Other platforms\u0027 installer metadata is omitted from the generated packages.
    """
    generated = {}
    appearance = load_appearance_config(root)
    for group, directory, fields in inventory(root):
        name = fields["name"]
        source = root / "skills" / group / directory
        plugin_root = f"plugins/{name}"
        homepage = f"https://github.com/CherryYang05/myskills/tree/master/skills/{group}/{directory}"
        description = re.sub(r"\s+", " ", fields["description"]).strip()
        subtitle = description[:117].rstrip() + ("…" if len(description) > 117 else "")
        icon_svg, brand_color, _fallback = render_icon(name, appearance)
        manifest = {
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "name": name,
            "version": "1.0.0",
            "description": description,
            "author": {
                "name": "CherryYang05",
                "url": "https://github.com/CherryYang05"
            },
            "homepage": homepage,
            "repository": "https://github.com/CherryYang05/myskills",
            "extensions": {
                "com.openai": {
                    "interface": {
                        "displayName": name,
                        "shortDescription": subtitle,
                        "longDescription": description,
                        "developerName": "CherryYang05",
                        "category": "Productivity",
                        "websiteURL": homepage,
                        "brandColor": brand_color,
                        "logo": "./assets/icon.svg",
                        "composerIcon": "./assets/icon.svg"
                    }
                }
            }
        }
        package = {"assets/icon.svg": ("100644", icon_svg)}
        for relative, (mode, content) in sorted(local_snapshot(source).items()):
            if omit_from_chatgpt_plugin(relative):
                continue
            package[f"skills/{name}/{relative}"] = (mode, content)
        package["plugin.json"] = (
            "100644", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        manifest["version"] = next_plugin_version(root, plugin_root, name, package)
        package["plugin.json"] = (
            "100644", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        for relative, file in package.items():
            generated[f"{plugin_root}/{relative}"] = file
    return generated


def check_or_write_plugin_files(root, generated, check):
    """Detect stale or missing plugin files and preserve executable bits."""
    folder = root / "plugins"
    if folder.is_symlink():
        raise ValueError("Generated plugin directory must not be a symlink")
    if check:
        present = {}
        if folder.exists():
            for path in folder.rglob("*"):
                if path.is_symlink():
                    raise ValueError(f"Generated plugin contains symlink: {path}")
                if path.is_file():
                    if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                        continue
                    relative = path.relative_to(root).as_posix()
                    mode = "100755" if path.stat().st_mode & 0o111 else "100644"
                    present[relative] = (mode, path.read_bytes())
        if present != generated:
            missing = sorted(set(generated) - set(present))
            extra = sorted(set(present) - set(generated))
            changed = sorted(p for p in set(present) & set(generated) if present[p] != generated[p])
            raise SystemExit(
                f"Generated plugin packages are stale (missing={missing[:5]}, "
                f"extra={extra[:5]}, modified={changed[:5]}). "
                "Run python3 automation/scripts/generate.py"
            )
        return
    if folder.exists():
        shutil.rmtree(folder)
    for relative, (mode, content) in sorted(generated.items()):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o755 if mode == "100755" else 0o644)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render()
    plugin_files = render_plugin_files()
    for name, content in generated.items():
        target = ROOT / name
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Generated file is stale: {name}. Run python3 automation/scripts/generate.py")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    check_or_write_plugin_files(ROOT, plugin_files, args.check)
    print(f"Generated artifacts {'verified' if args.check else 'updated'} "
          f"({len(generated)} indexes, {len(plugin_files)} plugin files).")


if __name__ == "__main__":
    main()
