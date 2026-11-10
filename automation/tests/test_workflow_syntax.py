"""Validate the embedded shell scripts in GitHub Actions without executing them."""
import subprocess
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]


class WorkflowShellSyntaxTests(unittest.TestCase):
    def test_workflow_bash_run_steps_parse(self):
        workflows = sorted((ROOT / ".github/workflows").glob("*.yml"))
        self.assertTrue(workflows)
        for path in workflows:
            spec = yaml.safe_load(path.read_text(encoding="utf-8"))
            for job_name, job in (spec.get("jobs") or {}).items():
                for idx, step in enumerate(job.get("steps") or []):
                    shell = step.get("shell", "bash")
                    script = step.get("run")
                    if not script or not shell.startswith("bash"):
                        continue
                    with self.subTest(workflow=path.name, job=job_name, step=idx):
                        outcome = subprocess.run(
                            ["bash", "-n"], input=script, text=True,
                            capture_output=True, check=False,
                        )
                        self.assertEqual(outcome.returncode, 0, outcome.stderr)


if __name__ == "__main__":
    unittest.main()
