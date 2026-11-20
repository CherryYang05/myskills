import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import action_run_log as journal


class ActionRunLogTests(unittest.TestCase):
    def test_backfill_attempts_no_runner_and_idempotent_replay(self):
        base = {"id": 31, "run_number": 8, "created_at": "2026-11-06T19:53:52Z",
                "event": "schedule", "run_attempt": 2, "status": "completed", "conclusion": "success"}
        requests = []

        def api(p):
            requests.append(p)
            if "workflows/sync-upstream" in p:
                return {"workflow_runs": [base, {**base, "id": 32, "run_attempt": 1, "status": "in_progress"}]}
            if "workflows/validate-skills" in p:
                return {"workflow_runs": []}
            if p.endswith("attempts/1"):
                return {**base, "conclusion": "failure"}
            if "attempts/1/jobs" in p:
                return {"jobs": [{"steps": [], "conclusion": "failure", "check_run_url": "https://api.github.com/check-runs/900"}]}
            if "check-runs/900/annotations" in p:
                return [{"annotation_level": "failure", "message": "Account is locked due to a billing issue."}]
            raise AssertionError(p)

        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            workflows = Path(__file__).resolve().parents[2] / ".github/workflows"
            self.assertEqual(journal.reconcile(root, "a/b", api, workflows), 1)
            data = (root / "2026-11.md").read_text()
            self.assertIn("2026-11-07 03:53:52", data)
            self.assertIn("计费问题", data)
            self.assertIn("attempts/1)", data)
            self.assertIn("attempts/2)", data)
            self.assertNotIn("runs/32", data)
            requests.clear()
            self.assertEqual(journal.reconcile(root, "a/b", api, workflows), 0)
            self.assertTrue(all("/workflows/" in path for path in requests))

    def test_failure_details_use_known_reason_or_step_without_publishing_raw_logs(self):
        run = {"conclusion": "failure"}
        jobs = [{"id": 20, "conclusion": "failure", "steps": [{"name": "Check", "conclusion": "failure"}]}]
        self.assertIn("登记表", journal.failure_reason(run, jobs, None, {"Check"},
                      lambda _: "External directory and registry mismatch: private input"))
        self.assertEqual(journal.failure_reason(run, jobs, None, {"Check"}, lambda _: ""), "失败步骤：Check")
        self.assertIn("原因待确认", journal.failure_reason(run, jobs, None, set(), lambda _: ""))
