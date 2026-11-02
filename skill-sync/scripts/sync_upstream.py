#!/usr/bin/env python3
"""Inspect configured upstreams; optionally prepare changes, never merge or publish."""

import argparse
import copy
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path, PurePosixPath

import yaml


CONFIG = "skill-sync/upstreams.json"
MAX_BYTES = 32 * 1024 * 1024


def git(directory, *args):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(directory), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def safe_path(value, allow_empty=False):
    if value == "" and allow_empty:
        return value
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Invalid path: {value!r}")
    path = PurePosixPath(value)
    if (path.is_absolute() or str(path) != value or
            any(p in {"..", ".git"} for p in path.parts) or
            any(ord(c) < 32 for c in value)):
        raise ValueError(f"Unsafe path: {value!r}")
    return value


def validate_config(config, root):
    if not isinstance(config, dict) or not config:
        raise ValueError("Upstream configuration must be a nonempty mapping")
    for name, info in config.items():
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            raise ValueError(f"Invalid local skill directory: {name}")
        if not (root / name / "SKILL.md").is_file():
            raise ValueError(f"Missing local skill: {name}")
        sync = info["sync"]
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", sync["repository"]):
            raise ValueError(f"Invalid GitHub repository for {name}")
        safe_path(sync["path"], allow_empty=True)
        ref = sync["ref"]
        if not isinstance(ref, str) or not ref or ref.startswith("-"):
            raise ValueError(f"Invalid tracked ref for {name}")
        if sync["mode"] not in {"mirror", "review"}:
            raise ValueError(f"Unsupported update mode for {name}")
        if sync["mode"] == "mirror" and not re.fullmatch(r"[0-9a-f]{40}", sync.get("synced_commit", "")):
            raise ValueError(f"Mirror mode needs a full synced_commit for {name}")
        if "files" in sync:
            if not isinstance(sync["files"], list) or not sync["files"]:
                raise ValueError(f"Empty file scope for {name}")
            for path in sync["files"]:
                safe_path(path)
            if "SKILL.md" not in sync["files"]:
                raise ValueError(f"File scope must include SKILL.md for {name}")
        if not isinstance(info["version"], str) or info["version"].lower() in {"", "latest", "main", "master", "head"}:
            raise ValueError(f"Untraceable synchronized version for {name}")


def snapshot(repository, commit, sync):
    prefix = sync["path"] + "/" if sync["path"] else ""
    result = {}
    total = 0
    for record in git(repository, "ls-tree", "-r", "-z", commit).split(b"\0"):
        if not record:
            continue
        header, raw_path = record.split(b"\t", 1)
        path = raw_path.decode("utf-8")
        if not path.startswith(prefix):
            continue
        relative = path[len(prefix):]
        if "files" in sync and relative not in sync["files"]:
            continue
        safe_path(relative)
        mode, kind, sha = header.decode().split()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"Unsupported symlink/submodule in upstream: {relative}")
        size = int(git(repository, "cat-file", "-s", sha))
        total += size
        if total > MAX_BYTES or len(result) >= 1000:
            raise ValueError("Upstream skill exceeds package size limits")
        result[relative] = (mode, git(repository, "cat-file", "blob", sha))
    if "SKILL.md" not in result:
        raise ValueError("Upstream skill package has no SKILL.md")
    if "files" in sync and set(result) != set(sync["files"]):
        raise ValueError("An explicitly scoped upstream file is missing")
    return result


def local_snapshot(directory, scope=None):
    if directory.is_symlink():
        raise ValueError(f"Local skill directory is a symlink: {directory}")
    result = {}
    for path in directory.rglob("*"):
        relative = path.relative_to(directory).as_posix()
        # Runtime caches are not maintained source files.
        if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
            continue
        if scope is not None and relative not in scope:
            continue
        if path.is_symlink():
            raise ValueError(f"Local symlink needs manual review: {path}")
        if path.is_file():
            safe_path(relative)
            result[relative] = ("100755" if path.stat().st_mode & 0o111 else "100644", path.read_bytes())
    return result


def identity(files):
    text = files["SKILL.md"][1].decode("utf-8")
    match = re.match(r"\A---\s*\n(.*?)\n---\s*(?:\n|$)", text, re.S)
    if not match:
        raise ValueError("Missing SKILL.md frontmatter")
    metadata = yaml.safe_load(match.group(1))
    if not isinstance(metadata, dict) or not isinstance(metadata.get("name"), str) or not isinstance(metadata.get("description"), str) or not metadata["description"].strip():
        raise ValueError("SKILL.md needs a name and description")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", metadata["name"]):
        raise ValueError("Invalid skill identity")
    return metadata["name"]


def fingerprint(files):
    digest = hashlib.sha256()
    for path, (mode, content) in sorted(files.items()):
        digest.update(path.encode() + b"\0" + mode.encode() + b"\0" + hashlib.sha256(content).digest())
    return digest.hexdigest()


def differences(before, after):
    return [{"path": path, "change": "added" if path not in before else "removed" if path not in after else "modified"}
            for path in sorted(before.keys() | after.keys()) if before.get(path) != after.get(path)]


def plan_skill(name, info, local, latest, baseline, commit):
    identity_changed = identity(local) != identity(latest)
    changes = differences(local, latest)
    if not changes:
        status = "up_to_date"
    elif identity_changed:
        status = "blocked_identity_change"
    elif info["sync"]["mode"] == "review":
        status = "review_required"
    elif local != baseline:
        status = "blocked_local_changes"
    else:
        status = "update_ready"
    marker = fingerprint(local) + ":" + fingerprint(latest) + ":" + status
    return {"skill": name, "status": status, "commit": commit,
            "changes": changes, "marker": marker,
            "report_changed": bool(changes) and info["sync"].get("last_reported") != marker}


def fetch_plan(root, config, cache):
    plans = []
    for name, info in sorted(config.items()):
        sync = info["sync"]
        repository = cache / name
        repository.mkdir()
        git(repository, "init", "--bare", "--quiet")
        git(repository, "remote", "add", "origin", f"https://github.com/{sync['repository']}.git")
        git(repository, "fetch", "--quiet", "--depth=1", "origin", sync["ref"])
        commit = git(repository, "rev-parse", "FETCH_HEAD").decode().strip()
        latest = snapshot(repository, commit, sync)
        local = local_snapshot(root / name, sync.get("files"))
        baseline = None
        if sync["mode"] == "mirror":
            git(repository, "fetch", "--quiet", "--depth=1", "origin", sync["synced_commit"])
            baseline = snapshot(repository, sync["synced_commit"], sync)
        plan = plan_skill(name, info, local, latest, baseline, commit)
        plans.append((plan, local, latest))
    return plans


def markdown(plan, info):
    name = plan["skill"]
    sync = info["sync"]
    prefix = sync["path"] + "/" if sync["path"] else ""
    lines = [f"# {name} 上游检查", "", f"状态：`{plan['status']}`", "",
             f"本仓库同步基线：`{info['version']}`。检查提交：[{plan['commit']}](https://github.com/{sync['repository']}/commit/{plan['commit']})。", "",
             "此报告不表示已经完整同步。review 模式及 blocked 状态不修改技能文件或同步版本；last_reported 仅用于避免重复报告。", "",
             "| 文件 | 变化（包含权限差异） | 上游文件 |", "|---|---|---|"]
    from urllib.parse import quote
    for item in plan["changes"]:
        path = item["path"]
        link = "—" if item["change"] == "removed" else f"[查看](https://github.com/{sync['repository']}/blob/{plan['commit']}/{quote(prefix + path)})"
        label = path.replace("|", "\\|").replace("`", "\\`")
        lines.append(f"| {label} | {item['change']} | {link} |")
    return "\n".join(lines) + "\n"


def apply_plans(root, config, plans):
    updated = copy.deepcopy(config)
    for plan, before, latest in plans:
        name = plan["skill"]
        if not plan["changes"] or not plan["report_changed"]:
            continue
        info = updated[name]
        report = root / "docs/upstream-reports" / f"{name}.md"
        report.parent.mkdir(parents=True, exist_ok=True)
        report.write_text(markdown(plan, info), encoding="utf-8")
        if plan["status"] == "update_ready":
            directory = root / name
            # Delete first so a file can become a directory (or the reverse).
            for item in plan["changes"]:
                if item["change"] == "removed":
                    (directory / item["path"]).unlink()
            for path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
                if path.is_dir() and not any(path.iterdir()):
                    path.rmdir()
            for item in plan["changes"]:
                if item["change"] != "removed":
                    target = directory / item["path"]
                    target.parent.mkdir(parents=True, exist_ok=True)
                    mode, content = latest[item["path"]]
                    target.write_bytes(content)
                    target.chmod(0o755 if mode == "100755" else 0o644)
            info["sync"]["synced_commit"] = plan["commit"]
            # A resolved Git commit is always traceable; do not invent a release version.
            info["version"] = plan["commit"][:12]
        info["sync"]["last_reported"] = plan["marker"]
    (root / CONFIG).write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="prepare candidate changes in this checkout")
    parser.add_argument("--validate-config", action="store_true", help="validate configuration without network access")
    parser.add_argument("--report", type=Path, help="write an inspection report outside the source tree")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    config = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    validate_config(config, root)
    if args.validate_config:
        print(f"Validated {len(config)} upstream configurations")
        return
    with tempfile.TemporaryDirectory(prefix="skill-upstreams-") as temporary:
        plans = fetch_plan(root, config, Path(temporary))
    report = {"skills": [plan for plan, _, _ in plans]}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for plan, _, _ in plans:
        print(f"{plan['skill']}: {plan['status']} ({len(plan['changes'])} file differences)")
    if args.apply:
        apply_plans(root, config, plans)


if __name__ == "__main__":
    main()
