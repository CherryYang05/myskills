#!/usr/bin/env python3
"""Synchronize exclusively registered third-party Skill packages from GitHub.

Third-party source code is data: fetch pinned git trees, never execute their scripts.
No repository writes occur until all source snapshots have been inspected.
"""
import argparse
import copy
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
CONFIG = "automation/upstreams.json"
SUMMARY = "UPSTREAM_SYNC_REPORT.md"
EXTERNAL = "skills/external"
MAX_BYTES = 32 * 1024 * 1024
MAX_OVERSIZE_BYTES = 128 * 1024 * 1024
MAX_FILES = 1500
MAX_OVERSIZE_FILES = 10000
SHA_PATTERN = re.compile(r"[0-9a-f]{40}")
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def git(directory, *args):
    return subprocess.run(
        ["git", "-c", "core.hooksPath=/dev/null", "-C", str(directory), *args],
        check=True, capture_output=True,
    ).stdout


def safe_path(value, empty=False):
    if value == "" and empty:
        return value
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"Invalid path: {value!r}")
    path = PurePosixPath(value)
    if (path.is_absolute() or str(path) != value
            or any(part in {"..", ".", ".git"} for part in path.parts)
            or any(ord(char) < 32 for char in value)):
        raise ValueError(f"Unsafe path: {value!r}")
    return value


def load_config(root=ROOT, allow_missing=False):
    config = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    validate_config(config, root, allow_missing=allow_missing)
    return config


def validate_config(config, root, allow_missing=False):
    if not isinstance(config, dict) or not config:
        raise ValueError("Upstream registry must be a nonempty mapping")
    parent = root / EXTERNAL
    names = {p.name for p in parent.iterdir() if p.is_dir() and (p / "SKILL.md").is_file()} if parent.is_dir() else set()
    unregistered = names - set(config)
    missing = set(config) - names
    if unregistered or (missing and not allow_missing):
        raise ValueError(f"External directory and registry mismatch: unregistered={sorted(unregistered)}, missing={sorted(missing)}")
    for name, source in config.items():
        if not NAME_PATTERN.fullmatch(name) or not isinstance(source, dict):
            raise ValueError(f"Invalid external Skill: {name!r}")
        allowed_fields = {"repo", "path", "ref", "sha", "preserve", "root_license", "max_bytes", "max_files"}
        if set(source) - allowed_fields:
            raise ValueError(f"Unexpected registry settings for {name}: {set(source) - allowed_fields}")
        repo = source.get("repo")
        if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise ValueError(f"Invalid GitHub repository for {name}")
        safe_path(source.get("path"), empty=True)
        max_bytes = source.get("max_bytes", MAX_BYTES)
        if (type(max_bytes) is not int or not MAX_BYTES <= max_bytes <= MAX_OVERSIZE_BYTES):
            raise ValueError(f"{name}: max_bytes must be an integer within approved import bounds")
        max_files = source.get("max_files", MAX_FILES)
        if (type(max_files) is not int or not MAX_FILES <= max_files <= MAX_OVERSIZE_FILES):
            raise ValueError(f"{name}: max_files must be an integer within approved import bounds")
        root_license = source.get("root_license")
        if root_license is not None:
            safe_path(root_license)
            if PurePosixPath(root_license).name not in {"LICENSE", "LICENSE.txt", "NOTICE", "NOTICE.md", "COPYING"}:
                raise ValueError(f"Only an upstream legal notice can be included: {name}")
        ref = source.get("ref")
        if not isinstance(ref, str) or not ref or ref.startswith("-") or any(c.isspace() for c in ref):
            raise ValueError(f"Invalid tracked ref for {name}")
        if not isinstance(source.get("sha"), str) or not SHA_PATTERN.fullmatch(source["sha"]):
            raise ValueError(f"Invalid synced commit for {name}")
        preserved = source.get("preserve", [])
        if (not isinstance(preserved, list)
                or any(not isinstance(p, str) for p in preserved)
                or len(preserved) != len(set(preserved))):
            raise ValueError(f"Invalid preserve list for {name}")
        for path in preserved:
            safe_path(path)
            if PurePosixPath(path).name not in {"LICENSE", "LICENSE.txt", "NOTICE", "NOTICE.md", "COPYING"}:
                raise ValueError(f"Only legal notices can be preserved: {name}/{path}")


def tree_snapshot(repository, commit, subdirectory, max_bytes=MAX_BYTES, max_files=MAX_FILES):
    """Get regular Git blobs, including executable mode. Reject links/submodules."""
    prefix = subdirectory + "/" if subdirectory else ""
    result = {}
    size_total = 0
    raw = git(repository, "ls-tree", "-r", "-z", commit)
    for entry in raw.split(b"\0"):
        if not entry:
            continue
        header, path_bytes = entry.split(b"\t", 1)
        path = path_bytes.decode("utf-8")
        if not path.startswith(prefix):
            continue
        relative = safe_path(path[len(prefix):])
        mode, kind, blob_sha = header.decode().split()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError(f"Unsupported Git object in upstream: {relative}")
        length = int(git(repository, "cat-file", "-s", blob_sha))
        size_total += length
        if size_total > max_bytes or len(result) >= max_files:
            raise ValueError(
                f"External Skill package exceeds safety bounds: {subdirectory} "
                f"({size_total} bytes, limit={max_bytes}, files={len(result) + 1}, file_limit={max_files})"
            )
        result[relative] = (mode, git(repository, "cat-file", "blob", blob_sha))
    if "SKILL.md" not in result:
        raise ValueError(f"Missing SKILL.md in upstream subdirectory: {subdirectory}")
    return result


def local_snapshot(directory, preserved=()):
    if directory.is_symlink():
        raise ValueError(f"Skill directory is a symlink: {directory}")
    result = {}
    for file in directory.rglob("*"):
        if "__pycache__" in file.parts or file.suffix in {".pyc", ".pyo"}:
            continue
        relative = file.relative_to(directory).as_posix()
        if relative in preserved:
            continue
        if file.is_symlink():
            raise ValueError(f"Local symlink needs review: {file}")
        if file.is_file():
            safe_path(relative)
            result[relative] = ("100755" if file.stat().st_mode & 0o111 else "100644", file.read_bytes())
    return result


def diff(before, after):
    return [
        {"path": name, "change": ("added" if name not in before else
                                    "removed" if name not in after else "modified")}
        for name in sorted(before.keys() | after.keys())
        if before.get(name) != after.get(name)
    ]


def fetch_snapshots(config):
    """Build every plan before mutating the checkout."""
    planned = []
    # Reuse one remote checkout for Skills sharing a repository and tracked ref.
    # This saves network fetches without changing the pinned commit semantics.
    with tempfile.TemporaryDirectory(prefix="myskills-sync-") as temp:
        fetched = {}
        for name, source in sorted(config.items()):
            key = (source["repo"], source["ref"])
            if key not in fetched:
                repo_dir = Path(temp) / f"remote-{len(fetched)}"
                repo_dir.mkdir()
                git(repo_dir, "init", "--bare", "--quiet")
                git(repo_dir, "remote", "add", "origin", f"https://github.com/{source['repo']}.git")
                git(repo_dir, "fetch", "--quiet", "--depth=1", "origin", source["ref"])
                remote_sha = git(repo_dir, "rev-parse", "FETCH_HEAD").decode().strip()
                fetched[key] = (repo_dir, remote_sha)
            repo_dir, remote_sha = fetched[key]
            latest = tree_snapshot(
                repo_dir, remote_sha, source["path"],
                max_bytes=source.get("max_bytes", MAX_BYTES),
                max_files=source.get("max_files", MAX_FILES),
            )
            # Attach the exact root license when the selected Skill subfolder
            # does not include its own. No upstream script is ever executed.
            root_license = source.get("root_license")
            if root_license:
                target = "LICENSE.upstream.txt"
                if target in latest:
                    raise ValueError(f"Upstream license overlay path conflict: {name}")
                legal = git(repo_dir, "show", f"{remote_sha}:{root_license}")
                if not legal or len(legal) > 256 * 1024:
                    raise ValueError(f"Missing or oversized upstream license: {name}")
                latest[target] = ("100644", legal)
            preserve = set(source.get("preserve", []))
            if preserve.intersection(latest):
                raise ValueError(f"Preserved legal notice conflicts with upstream: {name}")
            before = local_snapshot(ROOT / EXTERNAL / name, preserve)
            changes = diff(before, latest)
            planned.append((name, remote_sha, before, latest, changes))
    return planned


def apply_snapshot(directory, before, latest, changes):
    for item in changes:
        if item["change"] == "removed":
            (directory / item["path"]).unlink()
    for path in sorted(directory.rglob("*"), key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    for item in changes:
        if item["change"] != "removed":
            mode, content = latest[item["path"]]
            path = directory / item["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
            path.chmod(0o755 if mode == "100755" else 0o644)


def render_report(before_config, after_config, planned, period=None):
    period = period or datetime.now(timezone(timedelta(hours=8))).strftime("%G-W%V")
    lines = [
        "# 外部 Skill 同步与修正报告", "",
        f"检查周期（北京时间）：{period}", "",
        "覆盖 registry 中全部外部 Skill；自研 Skill 不在自动替换范围内。",
        "该文件由 GitHub Actions 生成，只有候选通过 CI 并合并到 master 才视为同步成功。", "",
        "| Skill | 结果 | 上次同步 commit | 本次同步 commit | 变更文件 |",
        "|---|---|---|---|---:|",
    ]
    changed = []
    for name, remote_sha, _, _, changes in planned:
        old = before_config[name]["sha"]
        new = after_config[name]["sha"]
        status = "已同步" if changes else "无变化"
        lines.append(f"| {name} | {status} | {old[:12]} | {new[:12]} | {len(changes)} |")
        if changes:
            changed.append(name)
    lines.extend(["", "## 文件变更", ""])
    if not changed:
        lines.append("本次未发现需要同步的 Skill 内容或文件权限变化。")
    for name, remote_sha, _, _, changes in planned:
        if not changes:
            continue
        lines.extend([f"### {name}", "",
                      f"上游提交：[{remote_sha}](https://github.com/{before_config[name]['repo']}/commit/{remote_sha})", "",
                      "| 文件路径 | 变化 |", "|---|---|"])
        lines.extend(f"| {c['path'].replace('|', '&#124;')} | {c['change']} |" for c in changes)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def apply_plans(root, config, planned, period=None):
    updated = copy.deepcopy(config)
    # A check with no content/permission changes must not create a weekly PR
    # solely to refresh timestamps in UPSTREAM_SYNC_REPORT.md.
    if not any(changes for _, _, _, _, changes in planned):
        return updated
    for name, remote_sha, old, latest, changes in planned:
        if changes:
            apply_snapshot(root / EXTERNAL / name, old, latest, changes)
            updated[name]["sha"] = remote_sha
    (root / CONFIG).write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / SUMMARY).write_text(render_report(config, updated, planned, period), encoding="utf-8")
    return updated


def append_action_summary(planned):
    """Record every check as a GitHub Actions run summary, including no-ops."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return
    lines = [
        "## Upstream Skill check", "",
        f"Checked {len(planned)} registered external Skills.",
        "", "| Skill | Upstream commit | Changed files |",
        "|---|---|---:|",
    ]
    for name, sha, _, _, changes in planned:
        lines.append(f"| {name} | `{sha[:12]}` | {len(changes)} |")
    changes = sum(bool(changes) for _, _, _, _, changes in planned)
    lines.extend([
        "",
        (f"{changes} Skill(s) changed; candidate PR requires validated merge."
         if changes else "No changes detected; no PR or report commit will be created."),
        "",
    ])
    with open(summary_path, "a", encoding="utf-8") as file:
        file.write("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-config", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--report-json", type=Path)
    args = parser.parse_args()
    # A registry entry may precede its first generated snapshot. Only the
    # apply path may temporarily accept this bootstrap state.
    config = load_config(allow_missing=args.apply)
    if args.check_config:
        print(f"Validated {len(config)} external Skill sources")
        return
    planned = fetch_snapshots(config)
    for name, remote_sha, _, _, changes in planned:
        print(f"{name}: {'update' if changes else 'unchanged'} ({len(changes)} files, upstream {remote_sha[:12]})")
    if args.report_json:
        args.report_json.write_text(json.dumps({
            "skills": [{"name": name, "upstream": sha, "changed_files": len(changes)}
                       for name, sha, _, _, changes in planned]
        }, indent=2) + "\n", encoding="utf-8")
    append_action_summary(planned)
    if args.apply:
        apply_plans(ROOT, config, planned)
        # Do not accept a half-populated registry after the fetch completes.
        load_config()


if __name__ == "__main__":
    main()
