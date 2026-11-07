import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import auto_merge_upstream as merge


REPO = 'example/skills'
HEAD = 'a' * 40
BASE = 'b' * 40
BRANCH = 'automation/upstream-' + BASE[:12] + '-' + 'c' * 16


class FakeGitHub:
    def __init__(self, conclusion='success', moved_head=False, moved_base=False, wrong_run_head=False):
        self.calls = []
        self.pr_reads = 0
        self.base_reads = 0
        self.dispatches = 0
        self.conclusion = conclusion
        self.moved_head = moved_head
        self.moved_base = moved_base
        self.wrong_run_head = wrong_run_head

    def api(self, path, method='GET', body=None):
        self.calls.append((path, method, body))
        if method == 'PUT':
            return {'merged': True, 'sha': 'd' * 40}
        if method == 'POST':
            self.dispatches += 1
            return None
        if path == 'pulls/7':
            self.pr_reads += 1
            return {'state': 'open', 'draft': False, 'user': {'login': 'github-actions[bot]'},
                    'head': {'repo': {'full_name': REPO}, 'ref': BRANCH,
                             'sha': 'e' * 40 if self.moved_head and self.pr_reads > 1 else HEAD},
                    'base': {'repo': {'full_name': REPO}, 'ref': 'master'}}
        if path.startswith('git/ref/'):
            self.base_reads += 1
            return {'object': {'sha': 'f' * 40 if self.moved_base and self.base_reads > 1 else BASE}}
        if '/runs?' in path:
            runs = []
            for i in range(self.dispatches):
                result = self.conclusion[min(i, len(self.conclusion) - 1)] if isinstance(self.conclusion, list) else self.conclusion
                runs.append({'id': 123 + i, 'head_sha': 'e' * 40 if self.wrong_run_head else HEAD,
                             'status': 'completed', 'conclusion': result, 'html_url': f'https://example.invalid/run/{123 + i}'})
            return {'workflow_runs': runs}
        raise AssertionError(path)


class AutoMergeTests(unittest.TestCase):
    def execute(self, api, **kwargs):
        return merge.merge_candidate(api, REPO, 7, BRANCH, HEAD, 'master', BASE, sleep=lambda _: None, **kwargs)

    def assert_no_merge(self, api):
        self.assertFalse(any(method == 'PUT' for _, method, _ in api.calls))

    def test_exact_head_success_dispatches_before_merging(self):
        api = FakeGitHub()
        run, sha = self.execute(api)
        self.assertEqual(sha, 'd' * 40)
        self.assertTrue(run.endswith('/123'))
        self.assertEqual(api.calls[-1], ('pulls/7/merge', 'PUT', {'sha': HEAD, 'merge_method': 'merge'}))
        self.assertIn(('actions/workflows/validate-skills.yml/dispatches', 'POST', {'ref': BRANCH}), api.calls)

    def test_failed_or_cancelled_validation_never_merges(self):
        for conclusion in ('failure', 'cancelled', 'action_required', 'skipped'):
            api = FakeGitHub(conclusion=conclusion)
            with self.subTest(conclusion=conclusion), self.assertRaises(ValueError):
                self.execute(api)
            self.assert_no_merge(api)

    def test_failed_first_validation_is_retried_before_merging(self):
        api = FakeGitHub(conclusion=['failure', 'success'])
        run, sha = self.execute(api)
        self.assertTrue(run.endswith('/124'))
        self.assertEqual(sha, 'd' * 40)
        self.assertEqual(api.dispatches, 2)

    def test_changed_head_is_not_merged(self):
        api = FakeGitHub(moved_head=True)
        with self.assertRaises(ValueError):
            self.execute(api)
        self.assert_no_merge(api)

    def test_stale_base_is_not_merged(self):
        api = FakeGitHub(moved_base=True)
        with self.assertRaises(ValueError):
            self.execute(api)
        self.assert_no_merge(api)

    def test_other_commit_success_does_not_count(self):
        api = FakeGitHub(wrong_run_head=True)
        with self.assertRaises(TimeoutError):
            self.execute(api, timeout=0.001)
        self.assert_no_merge(api)

    def test_non_bot_or_unrelated_branch_is_rejected(self):
        api = FakeGitHub()
        pr = api.api('pulls/7')
        pr['user']['login'] = 'someone-else'
        with self.assertRaises(ValueError):
            merge.validate_pr(pr, REPO, BRANCH, HEAD, 'master')
        pr['user']['login'] = 'github-actions[bot]'
        pr['head']['ref'] = 'feature/other-work'
        with self.assertRaises(ValueError):
            merge.validate_pr(pr, REPO, 'feature/other-work', HEAD, 'master')

    def config(self):
        return {'mirror': {'url': 'example', 'version': 'v1', 'sync': {'mode': 'mirror', 'files': ['SKILL.md'], 'synced_commit': BASE}},
                'custom': {'url': 'example', 'version': 'v1', 'sync': {'mode': 'review'}}}

    def test_only_configured_files_and_reports_can_merge(self):
        before = self.config()
        after = copy.deepcopy(before)
        after['mirror']['version'] = HEAD[:12]
        after['mirror']['sync']['synced_commit'] = HEAD
        after['custom']['sync']['last_reported'] = 'fingerprint'
        merge.validate_scope(before, after, ['mirror/SKILL.md', 'docs/upstream-reports/custom.md', merge.CONFIG])
        for path in ('custom/SKILL.md', '.github/workflows/validate-skills.yml', 'skill-sync/scripts/sync_upstream.py', 'mirror/extra.py'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                merge.validate_scope(before, after, [path])

    def test_full_replace_scope_can_remove_local_customization_metadata(self):
        before = self.config()
        before['custom']['sync']['mode'] = 'replace'
        before['custom']['selected_fixes'] = {'old': 'locally adapted'}
        before['custom']['sync']['reviewed_commit'] = 'c' * 40
        after = copy.deepcopy(before)
        after['custom'].pop('selected_fixes')
        after['custom']['sync'].pop('reviewed_commit')
        after['custom']['sync']['synced_commit'] = HEAD
        after['custom']['version'] = HEAD[:12]
        merge.validate_scope(before, after, [
            'custom/SKILL.md', 'custom/references/legacy.md', merge.CONFIG
        ])

    def test_full_replace_cannot_modify_preserved_license(self):
        before = self.config()
        before['custom']['sync']['mode'] = 'replace'
        before['custom']['sync']['preserve_files'] = ['LICENSE', 'NOTICE.md']
        after = copy.deepcopy(before)
        with self.assertRaisesRegex(ValueError, 'legal notice'):
            merge.validate_scope(before, after, ['custom/LICENSE'])

    def test_full_replace_rejects_unpinned_or_fabricated_version(self):
        before = self.config()
        before['custom']['sync']['mode'] = 'replace'
        after = copy.deepcopy(before)
        after['custom']['version'] = 'latest'
        after['custom']['sync']['synced_commit'] = HEAD
        with self.assertRaises(ValueError):
            merge.validate_scope(before, after, [merge.CONFIG])
        after['custom']['version'] = HEAD[:12]
        after['custom']['sync']['repository'] = 'evil/skills'
        with self.assertRaises(ValueError):
            merge.validate_scope(before, after, [merge.CONFIG])

    def test_source_policy_and_review_version_cannot_change(self):
        before = self.config()
        after = copy.deepcopy(before)
        after['custom']['version'] = 'invented'
        with self.assertRaises(ValueError):
            merge.validate_scope(before, after, [merge.CONFIG])
        after = copy.deepcopy(before)
        after['mirror']['sync']['mode'] = 'review'
        with self.assertRaises(ValueError):
            merge.validate_scope(before, after, [merge.CONFIG])


if __name__ == '__main__':
    unittest.main()
