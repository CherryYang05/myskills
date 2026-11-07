#!/usr/bin/env python3
"""Dispatch read-only CI for an exact upstream candidate, then merge that SHA."""

import argparse
import copy
import json
import os
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote, urlencode

from sync_upstream import CONFIG, git


class GitHub:
    def __init__(self, repository):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("Invalid repository")
        self.prefix = f"repos/{repository}"

    def api(self, path, method="GET", body=None):
        command = ["gh", "api", "--method", method, f"{self.prefix}/{path}"]
        if body is not None:
            command += ["--input", "-"]
        result = subprocess.run(command, input=json.dumps(body) if body is not None else None,
                                text=True, check=True, capture_output=True)
        return json.loads(result.stdout) if result.stdout.strip() else None


def validate_pr(pr, repository, branch, head, base):
    if (pr["state"] != "open" or pr.get("draft") or
            pr["user"]["login"] != "github-actions[bot]" or
            pr["head"]["repo"]["full_name"] != repository or
            pr["base"]["repo"]["full_name"] != repository or
            pr["head"]["ref"] != branch or pr["head"]["sha"] != head or
            pr["base"]["ref"] != base or
            not re.fullmatch(r"automation/upstream-[0-9a-f]{12}-[0-9a-f]{16}", branch)):
        raise ValueError("PR identity, ownership, branch, or head changed; refusing automatic merge")


def validate_scope(before, after, paths):
    if set(before) != set(after):
        raise ValueError("Automatic updates cannot add or remove upstream configurations")
    left, right = copy.deepcopy(before), copy.deepcopy(after)
    for name in before:
        mode = before[name]["sync"]["mode"]
        if mode in {"mirror", "replace"}:
            for side in (left, right):
                side.pop("version", None)
                side["sync"].pop("synced_commit", None)
        if mode == "replace":
            # A complete upstream copy may drop old, local-only adaptation
            # metadata. It cannot silently substitute different fix records.
            if after[name].get("selected_fixes") not in (None, before[name].get("selected_fixes")):
                raise ValueError("Replacement cannot fabricate selected_fixes")
            if (after[name]["sync"].get("reviewed_commit") not in
                    (None, before[name]["sync"].get("reviewed_commit"))):
                raise ValueError("Replacement cannot fabricate a reviewed commit")
            for side in (left, right):
                side.pop("selected_fixes", None)
                side["sync"].pop("reviewed_commit", None)
        for side in (left, right):
            side[name]["sync"].pop("last_reported", None)
        if mode in {"mirror", "replace"} and after[name].get("version") != before[name].get("version"):
            pinned = after[name]["sync"].get("synced_commit", "")
            if not re.fullmatch(r"[0-9a-f]{40}", pinned) or after[name]["version"] != pinned[:12]:
                raise ValueError("Updated version must match its pinned upstream commit")
    if left != right:
        raise ValueError("Source settings or review-mode synchronized version changed")
    allowed = {CONFIG, "README.md", ".agents/plugins/marketplace.json", "docs/upstream-reports/health.json"}
    allowed.update(f"docs/upstream-reports/{name}.md" for name in before)
    for path in paths:
        if path in allowed:
            continue
        matched = False
        for name, info in before.items():
            policy = info["sync"]
            if name == "skill-sync" or policy["mode"] not in {"mirror", "replace"} or not path.startswith(name + "/"):
                continue
            if "files" not in policy or path[len(name) + 1:] in policy["files"]:
                matched = True
                break
        if not matched:
            raise ValueError(f"Candidate modifies a file outside automatic update scope: {path}")


def verify_base(api, branch, expected):
    current = api.api(f"git/ref/heads/{quote(branch, safe='')}")["object"]["sha"]
    if current != expected:
        raise ValueError("Default branch advanced during validation; retry from its new base")


def merge_candidate(api, repository, number, branch, head, base, base_sha, timeout=600, sleep=time.sleep):
    pr = api.api(f"pulls/{number}")
    validate_pr(pr, repository, branch, head, base)
    verify_base(api, base, base_sha)
    query = urlencode({"event": "workflow_dispatch", "branch": branch, "per_page": 100})
    runs_path = "actions/workflows/validate-skills.yml/runs?" + query
    deadline = time.monotonic() + timeout
    # CI runners can fail before any test step starts. Retry failures without
    # changing the candidate; never merge unless a fresh exact-head run passes.
    completed = None
    for attempt in range(3):
        previous = {run["id"] for run in api.api(runs_path)["workflow_runs"]}
        api.api("actions/workflows/validate-skills.yml/dispatches", "POST", {"ref": branch})
        while time.monotonic() < deadline:
            candidates = [run for run in api.api(runs_path)["workflow_runs"]
                          if run["id"] not in previous and run["head_sha"] == head]
            completed = next((run for run in candidates if run["status"] == "completed"), None)
            if completed:
                if completed["conclusion"] == "success":
                    break
                if attempt == 2:
                    raise ValueError(
                        f"Candidate validation failed after 3 attempts: {completed['html_url']}"
                    )
                break
            sleep(5)
        else:
            raise TimeoutError("Timed out waiting for exact-head validation; PR left open")
        if completed and completed["conclusion"] == "success":
            break
    # Never merge a newer, unvalidated push or an outdated candidate base.
    validate_pr(api.api(f"pulls/{number}"), repository, branch, head, base)
    verify_base(api, base, base_sha)
    result = api.api(f"pulls/{number}/merge", "PUT", {"sha": head, "merge_method": "merge"})
    if not result.get("merged"):
        raise ValueError(f"GitHub did not merge the candidate: {result.get('message')}")
    return completed["html_url"], result["sha"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pr", required=True, type=int)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--base-sha", required=True)
    args = parser.parse_args()
    if not all(re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (args.head, args.base_sha)):
        parser.error("Exact full commit SHAs are required")
    root = Path(__file__).resolve().parents[2]
    before = json.loads(git(root, "show", f"{args.base_sha}:{CONFIG}"))
    after = json.loads(git(root, "show", f"{args.head}:{CONFIG}"))
    paths = git(root, "diff", "--no-renames", "--name-only", "-z", args.base_sha, args.head).decode().strip("\0").split("\0")
    validate_scope(before, after, paths)
    repository, base = os.environ["REPOSITORY"], os.environ["BASE_BRANCH"]
    run_url, merge_sha = merge_candidate(GitHub(repository), repository, args.pr, args.branch,
                                        args.head, base, args.base_sha)
    summary = f"Validated {args.head} in {run_url}; automatically merged PR #{args.pr} as {merge_sha}.\n"
    print(summary)
    if os.environ.get("GITHUB_STEP_SUMMARY"):
        with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as handle:
            handle.write(summary)


if __name__ == "__main__":
    main()
