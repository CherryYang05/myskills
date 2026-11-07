import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import sync_upstream as sync


def files(body='original', mode='100644', name='example'):
    content = f'---\nname: {name}\ndescription: A test workflow.\n---\n{body}\n'.encode()
    return {'SKILL.md': ('100644', content), 'scripts/run.py': (mode, b'print("example")\n')}


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / 'skill-sync').mkdir()
        self.info = {'url': 'https://github.com/example/skills', 'version': 'v1.0.0',
                     'sync': {'repository': 'example/skills', 'path': '', 'ref': 'main',
                              'mode': 'mirror', 'synced_commit': 'a' * 40}}
        self.before = files()

    def tearDown(self):
        self.temporary.cleanup()

    def materialize(self, snapshot):
        directory = self.root / 'example'
        directory.mkdir(exist_ok=True)
        for relative, (mode, content) in snapshot.items():
            target = directory / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
            target.chmod(0o755 if mode == '100755' else 0o644)
        return directory

    def plan(self, latest, local=None, info=None):
        return sync.plan_skill('example', info or self.info, local or self.before, latest, self.before, 'b' * 40)

    def test_mirror_updates_files_deletions_modes_and_baseline(self):
        directory = self.materialize(self.before)
        (directory / 'obsolete.txt').write_text('old')
        baseline = sync.local_snapshot(directory)
        latest = files('new', mode='100755')
        plan = sync.plan_skill('example', self.info, baseline, latest, baseline, 'b' * 40)
        sync.apply_plans(self.root, {'example': self.info}, [(plan, baseline, latest)])
        self.assertEqual(sync.local_snapshot(directory), latest)
        config = json.loads((self.root / sync.CONFIG).read_text())
        self.assertEqual(config['example']['version'], 'b' * 12)
        self.assertEqual(config['example']['sync']['synced_commit'], 'b' * 40)

    def test_changed_upstream_overrides_local_drift_with_mirror_fallback(self):
        customized = files('local customization')
        directory = self.materialize(customized)
        latest = files('upstream change')
        plan = self.plan(latest, local=customized)
        self.assertEqual(plan['status'], 'update_ready')
        sync.apply_plans(self.root, {'example': self.info}, [(plan, customized, latest)])
        self.assertEqual(sync.local_snapshot(directory), latest)
        self.assertEqual(json.loads((self.root / sync.CONFIG).read_text())['example']['version'], 'b' * 12)

    def test_mirror_preserves_local_drift_when_upstream_has_not_changed(self):
        customized = files('local customization')
        directory = self.materialize(customized)
        plan = self.plan(self.before, local=customized)
        self.assertEqual(plan['status'], 'blocked_local_changes')
        sync.apply_plans(self.root, {'example': self.info}, [(plan, customized, self.before)])
        self.assertEqual(sync.local_snapshot(directory), customized)

    def test_replace_discards_local_only_files_and_selected_fixes(self):
        customized = files('local customization')
        customized['LOCAL_ONLY.md'] = ('100644', b'local notes')
        directory = self.materialize(customized)
        info = copy.deepcopy(self.info)
        info['sync']['mode'] = 'replace'
        info['selected_fixes'] = {'abc123': 'old local patch'}
        info['sync']['reviewed_commit'] = 'c' * 40
        latest = files('upstream authoritative', mode='100755')
        plan = self.plan(latest, local=customized, info=info)
        self.assertEqual(plan['status'], 'update_ready')
        sync.apply_plans(self.root, {'example': info}, [(plan, customized, latest)])
        self.assertEqual(sync.local_snapshot(directory), latest)
        config = json.loads((self.root / sync.CONFIG).read_text())['example']
        self.assertEqual(config['version'], 'b' * 12)
        self.assertEqual(config['sync']['synced_commit'], 'b' * 40)
        self.assertNotIn('selected_fixes', config)
        self.assertNotIn('reviewed_commit', config['sync'])

    def test_failed_candidate_is_retried_even_when_marker_already_reported(self):
        directory = self.materialize(self.before)
        info = copy.deepcopy(self.info)
        info['sync']['mode'] = 'replace'
        latest = files('upstream update')
        plan = self.plan(latest, info=info)
        info['sync']['last_reported'] = plan['marker']
        retry = self.plan(latest, info=info)
        self.assertFalse(retry['report_changed'])
        sync.apply_plans(self.root, {'example': info}, [(retry, self.before, latest)])
        self.assertEqual(sync.local_snapshot(directory), latest)

    def test_unattended_config_rejects_report_only_mode(self):
        self.materialize(self.before)
        info = copy.deepcopy(self.info)
        info['sync']['mode'] = 'review'
        with self.assertRaisesRegex(ValueError, 'report-only'):
            sync.validate_config({'example': info}, self.root)

    def test_full_replacement_can_accept_upstream_identity_change(self):
        original = files('local version')
        directory = self.materialize(original)
        info = copy.deepcopy(self.info)
        info['sync']['mode'] = 'replace'
        latest = files('new upstream', name='renamed-example')
        plan = self.plan(latest, local=original, info=info)
        self.assertEqual(plan['status'], 'update_ready')
        sync.apply_plans(self.root, {'example': info}, [(plan, original, latest)])
        self.assertEqual(sync.local_snapshot(directory), latest)
        # A real candidate must also pass the generated marketplace's
        # package-name uniqueness check before it is allowed to merge.

    def test_review_reports_do_not_advance_sync_version(self):
        self.info['sync']['mode'] = 'review'
        directory = self.materialize(self.before)
        latest = files('new')
        plan = self.plan(latest)
        self.assertEqual(plan['status'], 'review_required')
        sync.apply_plans(self.root, {'example': self.info}, [(plan, self.before, latest)])
        self.assertEqual(sync.local_snapshot(directory), self.before)
        config = json.loads((self.root / sync.CONFIG).read_text())
        self.assertEqual(config['example']['version'], 'v1.0.0')
        self.assertTrue((self.root / 'docs/upstream-reports/example.md').exists())
        self.assertFalse(self.plan(latest, info=config['example'])['report_changed'])

    def test_unrelated_upstream_commits_are_noops(self):
        plan = self.plan(self.before)
        self.assertEqual(plan['status'], 'up_to_date')
        self.assertFalse(plan['report_changed'])

    def test_monthly_health_is_stable_within_a_month(self):
        plans = [(self.plan(self.before), self.before, self.before)]
        sync.record_monthly_health(self.root, plans, '2026-11')
        path = self.root / 'docs/upstream-reports/health.json'
        original = path.read_bytes()
        changed = copy.deepcopy(plans)
        changed[0][0]['commit'] = 'e' * 40
        sync.record_monthly_health(self.root, changed, '2026-11')
        self.assertEqual(path.read_bytes(), original)
        sync.record_monthly_health(self.root, changed, '2026-12')
        self.assertNotEqual(path.read_bytes(), original)

    def test_policy_change_reconsiders_previously_reported_candidate(self):
        review = copy.deepcopy(self.info)
        review['sync']['mode'] = 'review'
        latest = files('new')
        review_plan = self.plan(latest, info=review)
        self.info['sync']['last_reported'] = review_plan['marker']
        mirror_plan = self.plan(latest)
        self.assertEqual(mirror_plan['status'], 'update_ready')
        self.assertTrue(mirror_plan['report_changed'])

    def test_mode_only_updates_are_detected(self):
        plan = self.plan(files(mode='100755'))
        self.assertEqual(plan['status'], 'update_ready')
        self.assertEqual(plan['changes'], [{'path': 'scripts/run.py', 'change': 'modified'}])

    def test_identity_change_needs_review(self):
        self.assertEqual(self.plan(files(name='renamed'))['status'], 'blocked_identity_change')

    def test_invalid_frontmatter_fails_before_copy(self):
        latest = copy.deepcopy(self.before)
        latest['SKILL.md'] = ('100644', b'No frontmatter')
        with self.assertRaises(ValueError):
            self.plan(latest)

    def test_paths_cannot_escape_skill_directory(self):
        for path in ('../outside', '/outside', 'a/../outside', '.git/config', 'a\\b', 'line\nbreak'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                sync.safe_path(path)

    def test_local_symlinks_require_review(self):
        directory = self.materialize(self.before)
        (directory / 'link').symlink_to(self.root / 'outside')
        with self.assertRaises(ValueError):
            sync.local_snapshot(directory)

    def test_explicit_file_scope_preserves_other_local_assets(self):
        directory = self.materialize(self.before)
        self.assertEqual(set(sync.local_snapshot(directory, ['SKILL.md'])), {'SKILL.md'})

    def test_configuration_requires_exact_mirror_baseline(self):
        self.materialize(self.before)
        config = {'example': self.info}
        sync.validate_config(config, self.root)
        self.info['sync']['synced_commit'] = 'latest'
        with self.assertRaises(ValueError):
            sync.validate_config(config, self.root)

    def test_snapshot_uses_selected_git_subdirectory_and_rejects_symlinks(self):
        repository = self.root / 'repository'
        repository.mkdir()
        sync.git(repository, 'init', '--quiet')
        target = repository / 'skills/example'
        target.mkdir(parents=True)
        for relative, (_, content) in self.before.items():
            p = target / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(content)
        (repository / 'unrelated.txt').write_text('not part of package')
        sync.git(repository, 'add', '.')
        sync.git(repository, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')
        scope = {'path': 'skills/example'}
        self.assertEqual(sync.snapshot(repository, 'HEAD', scope), self.before)
        (target / 'link').symlink_to('SKILL.md')
        sync.git(repository, 'add', '.')
        sync.git(repository, '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'symlink')
        with self.assertRaises(ValueError):
            sync.snapshot(repository, 'HEAD', scope)

    def test_file_directory_transitions(self):
        before = files()
        before['changing'] = ('100644', b'file')
        directory = self.materialize(before)
        after = files()
        after['changing/nested'] = ('100644', b'child')
        plan = sync.plan_skill('example', self.info, before, after, before, 'b' * 40)
        sync.apply_plans(self.root, {'example': self.info}, [(plan, before, after)])
        self.assertEqual(sync.local_snapshot(directory), after)
        plan = sync.plan_skill('example', self.info, after, before, after, 'c' * 40)
        sync.apply_plans(self.root, {'example': self.info}, [(plan, after, before)])
        self.assertEqual(sync.local_snapshot(directory), before)


if __name__ == '__main__':
    unittest.main()
