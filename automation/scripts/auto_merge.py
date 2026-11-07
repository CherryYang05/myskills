#!/usr/bin/env python3
"""Verify and auto-merge only approved upstream Skill updates after exact-head CI."""
import argparse
import copy
import json
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote, urlencode

from sync import CONFIG, EXTERNAL, SUMMARY, ROOT

SHA_RE = re.compile(r"[0-9a-f]{40}")


class GitHub:
    def __init__(self, repo):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
            raise ValueError("Invalid GitHub repository")
        self.prefix = f"repos/{repo}"

    def api(self, path, method="GET", payload=None):
        command = ["gh", "api", "--method", method, f"{self.prefix}/{path}"]
        if payload is not None:
            command.extend(["--input", "-"])
        response = subprocess.run(
            command, input=json.dumps(payload) if payload is not None else None,
            text=True, check=True, capture_output=True
        ).stdout
        return json.loads(response) if response.strip() else None


def validate_scope(before, after, changed_paths):
    if set(before) != set(after):
        raise ValueError("Automatic sync may not add or remove source entries")
    for name in before:
        left, right = copy.deepcopy(before[name]), copy.deepcopy(after[name])
        old_sha, new_sha = left.pop("sha", None), right.pop("sha", None)
        if left != right:
            raise ValueError(f"Upstream source or policy changed in automatic PR: {name}")
        if not isinstance(new_sha, str) or not SHA_RE.fullmatch(new_sha):
            raise ValueError(f"Invalid pinned source commit: {name}")
        if old_sha != new_sha and not SHA_RE.fullmatch(old_sha or ""):
            raise ValueError(f"Invalid previous source commit: {name}")
    allowed = {CONFIG, SUMMARY, "README.md", ".agents/plugins/marketplace.json",
               ".claude-plugin/marketplace.json", ".cursor-plugin/marketplace.json",
               "skills.sh.json"}
    for path in changed_paths:
        if path in allowed:
            continue
        found = False
        for name, source in before.items():
            plugin_prefix = f"plugins/{name}/"
            if path.startswith(plugin_prefix):
                found = True
                break
            prefix = f"{EXTERNAL}/{name}/"
            if path.startswith(prefix):
                relative = path[len(prefix):]
                if relative in source.get("preserve", []):
                    raise ValueError(f"Automatic sync cannot overwrite preserved legal notice: {path}")
                found = True
                break
        if not found:
            raise ValueError(f"Automatic candidate touches unapproved path: {path}")


def validate_pr(pr, repo, branch, head, base):
    if (pr["state"] != "open" or pr.get("draft")
            or pr["user"]["login"] != "github-actions[bot]"
            or pr["head"]["repo"]["full_name"] != repo
            or pr["base"]["repo"]["full_name"] != repo
            or pr["head"]["ref"] != branch or pr["head"]["sha"] != head
            or pr["base"]["ref"] != base
            or not re.fullmatch(r"automation/upstream-[0-9a-f]{12}-[0-9a-f]{16}", branch)):
        raise ValueError("Candidate PR identity/head/ownership changed")


def verify_base(api, branch, expected_sha):
    actual = api.api(f"git/ref/heads/{quote(branch, safe='')}")["object"]["sha"]
    if actual != expected_sha:
        raise ValueError("Default branch advanced; regenerate candidate on new base")


def validate_and_merge(api, repo, number, branch, head, base, base_sha, timeout=600, sleeper=time.sleep):
    validate_pr(api.api(f"pulls/{number}"), repo, branch, head, base)
    verify_base(api, base, base_sha)
    query = urlencode({"event": "workflow_dispatch", "branch": branch, "per_page": 100})
    path = f"actions/workflows/validate-skills.yml/runs?{query}"
    deadline = time.monotonic() + timeout
    for attempt in range(3):
        existing_ids = {run["id"] for run in api.api(path)["workflow_runs"]}
        api.api("actions/workflows/validate-skills.yml/dispatches", "POST", {"ref": branch})
        while time.monotonic() < deadline:
            runs = api.api(path)["workflow_runs"]
            matches = [run for run in runs if run["id"] not in existing_ids and run["head_sha"] == head]
            completed = next((run for run in matches if run["status"] == "completed"), None)
            if completed:
                if completed["conclusion"] == "success":
                    validate_pr(api.api(f"pulls/{number}"), repo, branch, head, base)
                    verify_base(api, base, base_sha)
                    result = api.api(f"pulls/{number}/merge", "PUT", {"sha": head, "merge_method": "merge"})
                    if not result.get("merged"):
                        raise ValueError(f"GitHub rejected merge: {result.get('message')}")
                    return completed["html_url"], result["sha"]
                if attempt == 2:
                    raise ValueError(f"Candidate failed exact-head validation three times: {completed['html_url']}")
                break
            sleeper(5)
        else:
            raise TimeoutError("Timed out waiting for exact-head CI; candidate left unmerged")
    raise AssertionError("Unreachable: no successful validation")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pr", type=int, required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base-sha", required=True)
    args = parser.parse_args()
    if not SHA_RE.fullmatch(args.head) or not SHA_RE.fullmatch(args.base_sha):
        parser.error("Full expected SHAs are required")
    from sync import git
    before = json.loads(git(ROOT, "show", f"{args.base_sha}:{CONFIG}"))
    after = json.loads(git(ROOT, "show", f"{args.head}:{CONFIG}"))
    names = git(ROOT, "diff", "--no-renames", "--name-only", "-z", args.base_sha, args.head).decode().strip("\0").split("\0")
    validate_scope(before, after, names)
    repo, base = os.environ["REPOSITORY"], os.environ["BASE_BRANCH"]
    ci_url, merge_sha = validate_and_merge(GitHub(repo), repo, args.pr, args.branch, args.head, base, args.base_sha)
    message = f"Validated exact commit {args.head} in {ci_url}; merged candidate PR #{args.pr} as {merge_sha}.\n"
    print(message)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as file:
            file.write(message)


if __name__ == "__main__":
    main()
