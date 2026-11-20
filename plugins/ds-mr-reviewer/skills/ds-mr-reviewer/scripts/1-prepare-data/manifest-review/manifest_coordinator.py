#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manifest MR Coordinator - 数据准备协调器

为 Manifest MR 下的每个子 MR（含 manifest 自身）准备检视数据，
调用 mr_coordinator.py 生成独立的 coordinator JSON。

Usage:
    python manifest_coordinator.py --mrUrl <MANIFEST_MR_URL>
    python manifest_coordinator.py --mrUrl <MANIFEST_MR_URL> --outputFile <PATH>
"""

import argparse
import json
import subprocess
import sys
import re
import http.client
import requests
import urllib3
from pathlib import Path
from urllib.parse import quote, urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# mr_coordinator.py 在上一级目录 ../1-prepare-data/
MR_COORDINATOR_PY = Path(__file__).resolve().parent.parent / "mr_coordinator.py"
TEMP_DIR = Path.home() / ".mr-reviewer" / "temp"


class ManifestUrlParser:
    """解析 Manifest MR URL，去掉 /sub_detail 后缀后再匹配"""

    def __init__(self, mr_url):
        self.mr_url = mr_url
        self.parsed_url = urlparse(mr_url)
        self.repository_name = None
        self.mr_id = None
        self.domain = None

    def parse(self):
        path = self.parsed_url.path
        self.domain = self.parsed_url.netloc

        # 去掉 /sub_detail 后缀
        if path.endswith("/sub_detail"):
            path = path[: -len("/sub_detail")]

        patterns = [
            r'^/(.+)/merge_requests/(\d+)/?.*$',
            r'^/(.+)/pull/(\d+)/?.*$',
            r'^/(.+)/-/change_requests/(\d+)/?.*$',
        ]

        for pattern in patterns:
            match = re.match(pattern, path)
            if match:
                self.repository_name = match.group(1)
                self.mr_id = match.group(2)
                return True
        return False


def load_config():
    """从 ~/.mr-reviewer/config.json 加载配置"""
    config_path = Path.home() / ".mr-reviewer" / "config.json"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_token(config, domain):
    """从 config 获取 token"""
    tokens = config.get("codehub_tokens", {})
    token = tokens.get(domain)
    if not token:
        token = config.get("codehub_token")
    if not token or token == "YOUR_CODEHUB_TOKEN_HERE":
        return None
    return token


def fetch_manifest_data(mr_url, config, domain):
    """
    调用 CodeHub API 获取 Manifest MR 的完整响应。

    API: GET /api/v4/projects/{encoded_project}/isource/merge_requests/{mr_id}
    超时 30s，3 次重试，检查 merge_request_type == "SuperMergeRequest"
    """
    parser = ManifestUrlParser(mr_url)
    if not parser.parse():
        raise ValueError(f"无法解析 MR URL: {mr_url}")

    token = get_token(config, domain)
    if not token:
        raise ValueError(f"Token for {domain} not configured")

    encoded_project = quote(parser.repository_name, safe='')
    api_url = f"https://{domain}/api/v4/projects/{encoded_project}/isource/merge_requests/{parser.mr_id}"
    headers = {"PRIVATE-TOKEN": token}
    print(f"[INFO] 请求 API: {api_url}", file=sys.stderr)

    for i in range(3):
        try:
            res = requests.get(api_url, headers=headers, verify=False, timeout=30)
            if res.status_code == http.client.OK:
                data = res.json()
                mr_type = data.get("merge_request_type")
                if mr_type != "SuperMergeRequest":
                    raise ValueError(
                        f"MR type is '{mr_type}', expected 'SuperMergeRequest'. "
                        f"This tool only supports Manifest (Super) Merge Requests."
                    )
                return data
            elif res.status_code in (429, 500) and i < 2:
                print(f"[WARN] 请求失败 (status={res.status_code}), 重试 {i+1}/3", file=sys.stderr)
                continue
            elif res.status_code == 404:
                raise ValueError(f"MR {parser.mr_id} not found in {parser.repository_name}")
            elif res.status_code in (401, 403):
                raise ValueError("Authentication failed, please check token")
            else:
                raise ValueError(f"Request failed with status {res.status_code}")
        except requests.exceptions.Timeout:
            if i < 2:
                print(f"[WARN] 请求超时, 重试 {i+1}/3", file=sys.stderr)
                continue
            raise

    raise RuntimeError("Failed to fetch manifest MR after retries")


def extract_sub_mrs(api_result):
    """从 omega.sub_merge_requests 提取子 MR 列表"""
    omega = api_result.get("omega", {})
    return omega.get("sub_merge_requests", [])


def build_sub_mr_url(sub_mr, domain):
    """
    从子 MR 的 source_project.path_with_namespace 拼接完整 URL，
    fallback 到 web_url。
    """
    source_project = sub_mr.get("source_project", {})
    namespace = source_project.get("path_with_namespace")

    if namespace:
        iid = sub_mr.get("iid")
        return f"https://{domain}/{namespace}/merge_requests/{iid}"

    # fallback to web_url
    web_url = sub_mr.get("web_url")
    if web_url:
        return web_url

    # last resort: extract from project_id and iid
    iid = sub_mr.get("iid")
    project_id = sub_mr.get("project_id")
    return f"https://{domain}/projects/{project_id}/merge_requests/{iid}"


def run_coordinator(mr_url, timeout=300):
    """
    子进程调用 mr_coordinator.py，返回 (ok, error_msg)。

    stdout 包含 coordinator 的输出，stderr 才是错误信息。
    """
    cmd = [sys.executable, str(MR_COORDINATOR_PY), "--mrUrl", mr_url]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode != 0:
            error_msg = result.stderr.strip() or result.stdout.strip() or f"coordinator 退出码 {result.returncode}"
            return False, error_msg
        return True, None
    except subprocess.TimeoutExpired:
        return False, f"coordinator 超时 (>{timeout}s)"
    except Exception as e:
        return False, f"coordinator 执行异常: {str(e)}"


class ManifestCoordinator:
    """Manifest MR 协调器主类"""

    def __init__(self, mr_url, output_file=None):
        self.mr_url = mr_url
        self.output_file = output_file
        self.temp_dir = TEMP_DIR
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """主流程"""
        # Step 1: 解析 manifest MR URL
        parser = ManifestUrlParser(self.mr_url)
        if not parser.parse():
            raise ValueError(f"无法解析 Manifest MR URL: {self.mr_url}")

        domain = parser.domain
        repo_name = parser.repository_name
        mr_id = parser.mr_id
        safe_repo_name = repo_name.replace("/", "_")

        print("=" * 60, file=sys.stderr)
        print(f"Manifest MR Coordinator", file=sys.stderr)
        print(f"Manifest MR URL: {self.mr_url}", file=sys.stderr)
        print(f"Domain: {domain}", file=sys.stderr)
        print(f"Repo: {repo_name}, MR ID: {mr_id}", file=sys.stderr)
        print("=" * 60, file=sys.stderr)

        # Step 2: 获取 manifest MR 数据
        print("[INFO] 获取 Manifest MR 数据...", file=sys.stderr)
        config = load_config()
        api_result = fetch_manifest_data(self.mr_url, config, domain)

        # Step 3: 提取子 MR 列表
        sub_mrs_raw = extract_sub_mrs(api_result)
        print(f"[INFO] 发现 {len(sub_mrs_raw)} 个子 MR", file=sys.stderr)

        # Step 4: 为 manifest 自身调用 coordinator
        print(f"[INFO] 为 Manifest MR 自身运行 coordinator...", file=sys.stderr)
        manifest_ok, manifest_error = run_coordinator(self.mr_url)
        if manifest_ok:
            print(f"[INFO] Manifest MR coordinator 成功", file=sys.stderr)
        else:
            print(f"[WARN] Manifest MR coordinator 失败: {manifest_error}", file=sys.stderr)

        manifest_coordinator_path = str(
            self.temp_dir / f"mr_{safe_repo_name}_{mr_id}" / "mr_coordinator.json"
        )

        # Step 5: 为每个子 MR 并行调用 coordinator
        sub_mr_results = []
        sub_mr_urls = []

        for smr in sub_mrs_raw:
            smr_url = build_sub_mr_url(smr, domain)
            sub_mr_urls.append((smr, smr_url))

        print(f"[INFO] 并行运行 {len(sub_mr_urls)} 个子 MR coordinator...", file=sys.stderr)

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_smr = {
                executor.submit(run_coordinator, smr_url): (smr, smr_url)
                for smr, smr_url in sub_mr_urls
            }

            for future in as_completed(future_to_smr):
                smr, smr_url = future_to_smr[future]
                smr_ok, smr_error = future.result()

                # 解析 source_project.path_with_namespace 作为 repo_path
                source_project = smr.get("source_project", {})
                repo_path = source_project.get("path_with_namespace", "")

                # 构建 coordinator_path
                if repo_path:
                    smr_iid = smr.get("iid")
                    smr_safe_repo = repo_path.replace("/", "_")
                    coordinator_path = str(
                        self.temp_dir / f"mr_{smr_safe_repo}_{smr_iid}" / "mr_coordinator.json"
                    )
                else:
                    # fallback: 使用 project_id
                    smr_iid = smr.get("iid")
                    proj_id = smr.get("project_id")
                    coordinator_path = str(
                        self.temp_dir / f"mr_project_{proj_id}_{smr_iid}" / "mr_coordinator.json"
                    )

                result_item = {
                    "id": smr.get("id"),
                    "iid": smr.get("iid"),
                    "project_id": smr.get("project_id"),
                    "web_url": smr.get("web_url", smr_url),
                    "source_branch": smr.get("source_branch"),
                    "target_branch": smr.get("target_branch"),
                    "repo_path": repo_path,
                    "author": {
                        "id": smr["author"]["id"] if smr.get("author") else None,
                        "username": smr["author"]["username"] if smr.get("author") else None,
                    },
                    "coordinator_ok": smr_ok,
                    "coordinator_error": smr_error,
                    "coordinator_path": coordinator_path if smr_ok else None,
                }
                sub_mr_results.append(result_item)

                if smr_ok:
                    print(f"[INFO]   子 MR #{smr.get('iid')} coordinator 成功", file=sys.stderr)
                else:
                    print(f"[WARN]   子 MR #{smr.get('iid')} coordinator 失败: {smr_error}", file=sys.stderr)

        # Step 6: 构建 summary
        author_data = api_result.get("author", {})
        project_id = api_result.get("project_id")
        web_url = api_result.get("web_url", self.mr_url)
        source_branch = api_result.get("source_branch")
        target_branch = api_result.get("target_branch")

        summary = {
            "manifest_url": self.mr_url,
            "domain": domain,
            "manifest_mr": {
                "repo": repo_name,
                "mr_id": mr_id,
                "project_id": project_id,
                "author": {
                    "id": author_data["id"] if author_data else None,
                    "username": author_data["username"] if author_data else None,
                },
                "source_branch": source_branch,
                "target_branch": target_branch,
                "web_url": web_url,
                "coordinator_ok": manifest_ok,
                "coordinator_error": manifest_error,
                "coordinator_path": manifest_coordinator_path if manifest_ok else None,
            },
            "sub_mr_count": len(sub_mr_results),
            "sub_merge_requests": sub_mr_results,
        }

        # Step 7: 写入 manifest_summary.json
        output_dir = self.temp_dir / f"manifest_{safe_repo_name}_{mr_id}"
        output_dir.mkdir(parents=True, exist_ok=True)
        summary_path = output_dir / "manifest_summary.json"

        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        print(f"\n[SUCCESS] manifest_summary: {summary_path}", file=sys.stderr)
        print(f"[INFO] 子 MR 成功: {sum(1 for s in sub_mr_results if s['coordinator_ok'])}/{len(sub_mr_results)}", file=sys.stderr)

        self.result = summary
        return summary


def main():
    parser = argparse.ArgumentParser(
        description="Manifest MR Coordinator - 为 Manifest MR 下的每个子 MR 准备检视数据"
    )
    parser.add_argument("--mrUrl", required=True, help="Manifest MR URL (SuperMergeRequest)")
    parser.add_argument("--outputFile", help="输出 JSON 文件路径（可选）")

    args = parser.parse_args()

    coordinator = ManifestCoordinator(args.mrUrl, args.outputFile)
    summary = coordinator.run()

    # 输出到指定文件或 stdout
    if args.outputFile:
        output_path = Path(args.outputFile)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 已保存到: {output_path}", file=sys.stderr)
    else:
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    # 如果所有子 MR coordinator 都失败，exit(1)
    sub_results = summary.get("sub_merge_requests", [])
    if sub_results and all(not s.get("coordinator_ok") for s in sub_results):
        print("[ERROR] 所有子 MR coordinator 均失败", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
