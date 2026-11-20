import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import auto_merge

BASE = "b" * 40
HEAD = "a" * 40
BRANCH = "automation/upstream-" + BASE[:12] + "-" + "c" * 16
REPO = "sample/myskills"


class FakeGitHub:
    def __init__(self, conclusion="success", wrong_head=False, moved_base=False, moved_head=False):
        self.calls = []
        self.dispatches = 0
        self.read_pr = 0
        self.read_base = 0
        self.conclusion = conclusion
        self.wrong_head = wrong_head
        self.moved_base = moved_base
        self.moved_head = moved_head

    def api(self, path, method="GET", payload=None):
        self.calls.append((path, method, payload))
        if method == "POST":
            self.dispatches += 1
            return None
        if method == "PUT":
            return {"merged": True, "sha": "d" * 40}
        if path == "pulls/7":
            self.read_pr += 1
            return {
                "state": "open", "draft": False, "user": {"login": "github-actions[bot]"},
                "head": {
                    "repo": {"full_name": REPO}, "ref": BRANCH,
                    "sha": "e" * 40 if self.moved_head and self.read_pr > 1 else HEAD
                },
                "base": {"repo": {"full_name": REPO}, "ref": "master"},
            }
        if path.startswith("git/ref/"):
            self.read_base += 1
            return {"object": {"sha": "f" * 40 if self.moved_base and self.read_base > 1 else BASE}}
        if "/runs?" in path:
            runs = []
            for i in range(self.dispatches):
                conclusion = self.conclusion[min(i, len(self.conclusion) - 1)] if isinstance(self.conclusion, list) else self.conclusion
                runs.append({
                    "id": 123 + i, "status": "completed", "conclusion": conclusion,
                    "head_sha": "e" * 40 if self.wrong_head else HEAD,
                    "html_url": f"https://example.invalid/runs/{i}",
                })
            return {"workflow_runs": runs}
        raise AssertionError(path)


class AutoMergeTests(unittest.TestCase):
    def run_merge(self, client, **kwargs):
        return auto_merge.validate_and_merge(client, REPO, 7, BRANCH, HEAD, "master", BASE, sleeper=lambda _: None, **kwargs)

    def test_good_candidate_is_checked_before_merge(self):
        client = FakeGitHub()
        self.run_merge(client)
        self.assertTrue(any("validate-skills.yml/dispatches" in p and m == "POST" for p, m, _ in client.calls))
        self.assertEqual(client.calls[-1], ("pulls/7/merge", "PUT", {"sha": HEAD, "merge_method": "merge"}))

    def test_failing_ci_cannot_merge(self):
        for conclusion in ("failure", "cancelled", "skipped"):
            client = FakeGitHub(conclusion)
            with self.subTest(conclusion=conclusion), self.assertRaises(ValueError):
                self.run_merge(client)
            self.assertFalse(any(method == "PUT" for _, method, _ in client.calls))

    def test_retry_after_first_failure(self):
        client = FakeGitHub(["failure", "success"])
        self.run_merge(client)
        self.assertEqual(client.dispatches, 2)

    def test_changed_candidate_or_base_refuse_merge(self):
        for args in ({"moved_base": True}, {"moved_head": True}):
            client = FakeGitHub(**args)
            with self.assertRaises(ValueError):
                self.run_merge(client)
            self.assertFalse(any(m == "PUT" for _, m, _ in client.calls))

    def test_scope_denies_self_authored_skill_and_workflow(self):
        before = {"demo": {"repo": "upstream/demo", "path": "", "ref": "main", "sha": BASE}}
        after = copy.deepcopy(before)
        after["demo"]["sha"] = HEAD
        auto_merge.validate_scope(before, after, ["skills/external/demo/SKILL.md", "plugins/demo/plugin.json", "plugins/demo/skills/demo/SKILL.md", auto_merge.CONFIG, auto_merge.SUMMARY])
        for path in ("skills/personal/own/SKILL.md", "automation/scripts/sync.py", ".github/workflows/sync-upstream.yml", "skills/external/other/SKILL.md", "plugins/other/plugin.json"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                auto_merge.validate_scope(before, after, [path])
        after["demo"]["ref"] = "untrusted"
        with self.assertRaisesRegex(ValueError, "source or policy"):
            auto_merge.validate_scope(before, after, [auto_merge.CONFIG])

    def test_scope_allows_generated_multi_platform_catalogs(self):
        before = {"demo": {"repo": "upstream/demo", "path": "", "ref": "main", "sha": BASE}}
        after = copy.deepcopy(before)
        after["demo"]["sha"] = HEAD
        auto_merge.validate_scope(before, after, [
            "skills/external/demo/SKILL.md", "plugins/demo/plugin.json",
            ".agents/plugins/marketplace.json", ".claude-plugin/marketplace.json",
            ".cursor-plugin/marketplace.json", "skills.sh.json",
        ])
        for path in (".claude-plugin/plugin.json", ".cursor-plugin/plugin.json",
                     "skills/personal/own/SKILL.md"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unapproved"):
                auto_merge.validate_scope(before, after, [path])

    def test_scope_protects_legal_notice(self):
        before = {"demo": {"repo": "upstream/demo", "path": "", "ref": "main", "sha": BASE, "preserve": ["LICENSE"]}}
        with self.assertRaisesRegex(ValueError, "legal notice"):
            auto_merge.validate_scope(before, before, ["skills/external/demo/LICENSE"])

    def test_scope_allows_only_the_matching_external_revision_log(self):
        registry = {"demo": {"repo": "upstream/demo", "path": "", "ref": "main", "sha": BASE}}
        skill = "skills/external/demo/SKILL.md"
        log = "skill-changelogs/external/demo.md"
        auto_merge.validate_scope(registry, registry, [skill, log])
        for paths in ([log], [skill, "skill-changelogs/personal/demo.md"]):
            with self.subTest(paths=paths), self.assertRaisesRegex(ValueError, "unapproved"):
                auto_merge.validate_scope(registry, registry, paths)

    def test_scope_allows_only_trusted_fully_external_bundles(self):
        source = {"repo": "upstream/demo", "path": "", "ref": "main", "sha": BASE}
        before = {"demo": source, "second": source}
        groups = {"suite": {"skills": ["external/demo", "external/second"]}}
        auto_merge.validate_scope(before, before, [
            "plugins/suite/plugin.json", "plugins/suite/skills/second/SKILL.md",
            "skills/external/second/SKILL.md",
        ], groups)
        for path in ("plugins/unregistered/plugin.json", auto_merge.GROUPS_CONFIG,
                     "skills/personal/second/SKILL.md"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "unapproved"):
                auto_merge.validate_scope(before, before, [path], groups)
        for member in ("personal/second", "external/missing"):
            with self.subTest(member=member), self.assertRaisesRegex(ValueError, "unapproved"):
                auto_merge.validate_scope(before, before, ["plugins/suite/plugin.json"], {
                    "suite": {"skills": ["external/demo", member]},
                })


if __name__ == "__main__":
    unittest.main()
