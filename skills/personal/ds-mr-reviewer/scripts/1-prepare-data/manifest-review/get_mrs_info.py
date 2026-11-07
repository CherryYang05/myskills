#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取 Manifest MR 下所有子 MR 的摘要信息。

从 Manifest MR（SuperMergeRequest）的 API 响应中提取 omega.sub_merge_requests 字段，
再结合顶层 author / source_branch / target_branch 信息，输出每个子 MR 的结构化摘要。

Usage:
    python get_mrs_info.py --mrUrl <MANIFEST_MR_URL>
    python get_mrs_info.py --mrUrl <MANIFEST_MR_URL> --outputFile <PATH>
"""

import argparse
import json
import sys
import re
import http.client
import requests
import urllib3
from pathlib import Path
from urllib.parse import quote, urlparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class MRUrlParser:
    """解析 MR URL 获取代码仓和 MR ID 信息"""

    def __init__(self, mr_url):
        self.mr_url = mr_url
        self.parsed_url = urlparse(mr_url)
        self.repository_name = None
        self.mr_id = None
        self.domain = None

    def parse(self):
        path = self.parsed_url.path
        self.domain = self.parsed_url.netloc

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


def fetch_manifest_mr(mr_url, config_path=None):
    """调用 CodeHub API 获取 Manifest MR 的完整响应"""
    parser = MRUrlParser(mr_url)
    if not parser.parse():
        raise ValueError(f"无法解析 MR URL: {mr_url}")

    if config_path is None:
        config_path = Path.home() / ".mr-reviewer" / "config.json"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    domain = parser.domain
    token = None
    if config.get("codehub_tokens"):
        token = config["codehub_tokens"].get(domain)
    if not token:
        token = config.get("codehub_token")
    if not token or token == "YOUR_CODEHUB_TOKEN_HERE":
        raise ValueError(f"Token for {domain} not configured")

    encoded_project = quote(parser.repository_name, safe='')
    url = f"https://{domain}/api/v4/projects/{encoded_project}/isource/merge_requests/{parser.mr_id}"
    headers = {"PRIVATE-TOKEN": token}
    print(f"[INFO] 请求 API: {url}", file=sys.stderr)

    for i in range(3):
        try:
            res = requests.get(url, headers=headers, verify=False, timeout=30)
            if res.status_code == http.client.OK:
                return res.json()
            elif res.status_code in (429, 500) and i < 2:
                continue
            elif res.status_code == 404:
                raise ValueError(f"MR {parser.mr_id} not found in {parser.repository_name}")
            elif res.status_code in (401, 403):
                raise ValueError("Authentication failed, please check token")
            else:
                raise ValueError(f"Request failed with status {res.status_code}")
        except requests.exceptions.Timeout:
            if i < 2:
                continue
            raise

    raise RuntimeError("Failed to fetch MR after retries")


def extract_mrs_info(api_result):
    """
    从 Manifest MR 的 API 结果中提取每个子 MR 的摘要信息。

    提取字段:
      - omega.sub_merge_requests[i].id
      - omega.sub_merge_requests[i].iid
      - omega.sub_merge_requests[i].project_id
      - omega.sub_merge_requests[i].author.id
      - omega.sub_merge_requests[i].author.username
      - omega.sub_merge_requests[i].source_branch
      - omega.sub_merge_requests[i].target_branch

    以及顶层 MR 信息:
      - author.id / author.username
      - source_branch / target_branch
    """
    omega = api_result.get("omega", {})

    # 顶层 MR 信息
    author_data = api_result.get("author")
    top_author = None
    if author_data:
        top_author = {
            "id": author_data.get("id"),
            "username": author_data.get("username"),
        }
    top_source_branch = api_result.get("source_branch")
    top_target_branch = api_result.get("target_branch")

    sub_mrs_raw = omega.get("sub_merge_requests", [])

    sub_mrs = []
    for smr in sub_mrs_raw:
        smr_author_data = smr.get("author")
        smr_author = None
        if smr_author_data:
            smr_author = {
                "id": smr_author_data.get("id"),
                "username": smr_author_data.get("username"),
            }
        sub_mrs.append({
            "id": smr.get("id"),
            "iid": smr.get("iid"),
            "project_id": smr.get("project_id"),
            "author": smr_author,
            "source_branch": smr.get("source_branch"),
            "target_branch": smr.get("target_branch"),
        })

    return {
        "mr_url": api_result.get("web_url", ""),
        "iid": api_result.get("iid"),
        "project_id": api_result.get("project_id"),
        "author": top_author,
        "source_branch": top_source_branch,
        "target_branch": top_target_branch,
        "sub_mr_count": len(sub_mrs),
        "sub_merge_requests": sub_mrs,
    }


def main():
    parser = argparse.ArgumentParser(
        description="获取 Manifest MR 下所有子 MR 的摘要信息"
    )
    parser.add_argument("--mrUrl", required=True, help="Manifest MR URL")
    parser.add_argument("--outputFile", help="输出文件路径（可选）")
    parser.add_argument("--configPath", help="config.json 路径")
    args = parser.parse_args()

    # Step 1: 调用 API 获取 Manifest MR 数据
    api_result = fetch_manifest_mr(args.mrUrl, args.configPath)
    print(f"[INFO] API 响应成功，MR 类型: {api_result.get('merge_request_type', 'unknown')}", file=sys.stderr)

    # Step 2: 提取子 MR 摘要
    result = extract_mrs_info(api_result)

    # Step 3: 输出
    if args.outputFile:
        output_path = Path(args.outputFile)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 已保存到: {output_path}", file=sys.stderr)

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
