"""Reconcile completed business workflow attempts into monthly Markdown files."""
import json
import os
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

WORKFLOWS = {"sync-upstream.yml": "上游同步", "validate-skills.yml": "技能校验"}
EVENTS = {"schedule": "定时", "push": "推送", "pull_request": "PR", "workflow_dispatch": "手动/API"}
STATUS = {"success": "成功", "failure": "失败", "startup_failure": "启动失败", "timed_out": "超时",
          "cancelled": "取消", "skipped": "跳过", "neutral": "中性", "action_required": "需介入",
          "stale": "已失效"}
BEIJING = timezone(timedelta(hours=8))
ROW_ID = re.compile(r"/actions/runs/(\d+)/attempts/(\d+)\) \|$")
HEADER = ("# {month} Actions 运行记录\n\n时间为北京时间。点击运行编号可查看该次尝试的原始记录。\n\n"
          "| 开始时间 | 工作流 | 触发 | 结果 | 说明 | 运行 |\n"
          "|---|---|---|---|---|---|\n")

# Publish classifications, never raw CI output or contributor-provided annotations.
CAUSES = [
    ("locked due to a billing issue", "GitHub 因账户计费问题未启动作业"),
    ("resource not accessible by integration", "GitHub 拒绝了工作流令牌的访问请求"),
    ("rate limit", "GitHub API 请求达到速率限制"),
    ("no space left on device", "运行器磁盘空间不足"),
    ("lost communication", "GitHub 与运行器失去连接"),
    ("timed out", "作业执行超时"),
    ("merge conflict", "合并发生冲突"),
    ("default branch advanced", "主分支在校验期间已更新"),
    ("external directory and registry mismatch", "外部技能目录与来源登记表不一致"),
    ("candidate failed exact-head validation", "候选提交未通过 CI 校验"),
    ("generated plugin packages are stale", "生成的插件包与源文件不一致"),
    ("no matching distribution found", "依赖安装失败，未找到匹配版本"),
    ("invalid workflow file", "GitHub 无法解析工作流配置"),
]

# Only publish names of steps defined by the trusted default-branch workflows.
def known_steps(workflow_file):
    import yaml
    jobs = yaml.safe_load(workflow_file.read_text())["jobs"]
    return {step["name"] for job in jobs.values() for step in job.get("steps", []) if "name" in step}


def classified(text):
    message = text.lower()
    return next((summary for pattern, summary in CAUSES if pattern in message), "")


def failure_reason(run, jobs, api, steps, job_log):
    if run["conclusion"] == "timed_out":
        return "运行超过时限"
    failed = [j for j in jobs if j.get("conclusion") in ("failure", "timed_out", "startup_failure", "action_required")]
    failed_step = ""
    for job in failed:
        check = (job.get("check_run_url") or "").rsplit("/", 1)[-1]
        if check.isdecimal():
            for page in pages(api, f"check-runs/{check}/annotations"):
                for annotation in page:
                    if annotation.get("annotation_level") != "failure":
                        continue
                    if summary := classified(annotation.get("message") or ""):
                        return summary
        if job.get("steps") and job_log:
            if summary := classified(job_log(int(job["id"]))):
                return summary
        for step in job.get("steps") or []:
            if not failed_step and step.get("conclusion") in ("failure", "timed_out"):
                name = step.get("name")
                if name in steps:
                    failed_step = f"失败步骤：{name}"
    if failed_step:
        return failed_step
    if failed and all(not j.get("runner_name") and not j.get("steps") for j in failed):
        return "作业未启动，GitHub 未提供可归类的原因"
    return "原因待确认，详见该次运行"


def pages(api, path, key=None):
    page = 1
    while True:
        result = api(f"{path}?per_page=100&page={page}")
        items = result[key] if key else result
        yield items
        if len(items) < 100:
            break
        page += 1


def reconcile(folder, repo, api, workflow_dir, job_log=None):
    folder.mkdir(parents=True, exist_ok=True)
    rows = defaultdict(dict)
    seen = set()
    for file in sorted(folder.glob("????-??.md")):
        for line in file.read_text().splitlines():
            if match := ROW_ID.search(line):
                key = tuple(map(int, match.groups()))
                rows[file.stem][key] = line
                seen.add(key)

    changed = set()
    for workflow, label in WORKFLOWS.items():
        steps = known_steps(workflow_dir / workflow)
        for page in pages(api, f"actions/workflows/{workflow}/runs", "workflow_runs"):
            for latest in page:
                run_id = int(latest["id"])
                last = int(latest["run_attempt"])
                for attempt in range(1, last + 1):
                    key = (run_id, attempt)
                    if key in seen:
                        continue
                    base = f"actions/runs/{run_id}/attempts/{attempt}"
                    run = latest if attempt == last else api(base)
                    if run["status"] != "completed" or not run.get("conclusion"):
                        continue
                    status = run["conclusion"]
                    if status in ("failure", "timed_out", "startup_failure", "action_required"):
                        jobs = [job for group in pages(api, base + "/jobs", "jobs") for job in group]
                        reason = failure_reason(run, jobs, api, steps, job_log)
                    else:
                        reason = {"success": "完成", "cancelled": "运行已取消", "skipped": "未执行"}.get(status, "见运行详情")
                    started = datetime.fromisoformat((run.get("run_started_at") or run["created_at"]).replace("Z", "+00:00"))
                    local = started.astimezone(BEIJING)
                    month = local.strftime("%Y-%m")
                    url = f"https://github.com/{repo}/actions/runs/{run_id}/attempts/{attempt}"
                    link = f"[#{int(run['run_number'])} · {attempt}]({url})"
                    event = EVENTS.get(run["event"], "其他")
                    rows[month][key] = (f"| {local:%Y-%m-%d %H:%M:%S} | {label} | {event} | "
                                        f"{STATUS.get(status, '其他')} | {reason} | {link} |")
                    seen.add(key)
                    changed.add(month)
    for month in sorted(changed):
        (folder / f"{month}.md").write_text(HEADER.format(month=month) + "\n".join(sorted(rows[month].values(), reverse=True)) + "\n")
    return len(changed)


if __name__ == "__main__":
    repo = os.environ["GITHUB_REPOSITORY"]

    def github(path):
        raw = subprocess.check_output(["gh", "api", f"repos/{repo}/{path}"])
        return json.loads(raw)

    def job_log(job_id):
        # Logs may have expired or never been created. Keep the annotated failure/step then.
        result = subprocess.run(["gh", "api", f"repos/{repo}/actions/jobs/{job_id}/logs"],
                                capture_output=True, check=False)
        return result.stdout.decode(errors="replace") if result.returncode == 0 else ""

    directory = Path(__file__).resolve().parents[2] / ".github/workflows"
    count = reconcile(Path(sys.argv[1]), repo, github, directory, job_log)
    print(f"Updated {count} monthly run logs.")
