#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Manifest Analysis Summary - AI 分析数据汇总

读取 manifest_summary.json，收集所有子 MR + manifest 自身的 coordinator 路径，
输出统一的数据结构供 AI 读取和分析。

Usage:
    python manifest_analysis_summary.py --summaryFile <manifest_summary.json 路径>
    python manifest_analysis_summary.py --summaryFile <path> --outputFile <path>
"""

import argparse
import json
import sys
from pathlib import Path


def load_summary(summary_file):
    """读取 manifest_summary.json"""
    with open(summary_file, "r", encoding="utf-8") as f:
        return json.load(f)


def collect_all_coordinators(summary):
    """
    收集所有需要分析的 MR coordinator 信息

    Returns:
        list[dict]: 每个 MR 的 {key, repo, mr_id, coordinator_path, label, mr_type}
    """
    items = []

    # Manifest 自身
    mmr = summary.get("manifest_mr", {})
    if mmr.get("coordinator_ok"):
        repo = mmr.get("repo", "")
        mr_id = mmr.get("mr_id", "")
        safe_repo = repo.replace("/", "_") if repo else "manifest"
        items.append({
            "key": f"{safe_repo}_{mr_id}",
            "repo": repo,
            "mr_id": mr_id,
            "project_id": mmr.get("project_id"),
            "label": f"Manifest 自身: {repo}!{mr_id}",
            "mr_type": "manifest",
            "coordinator_path": mmr.get("coordinator_path", ""),
            "web_url": mmr.get("web_url", ""),
        })

    # 各子 MR
    for smr in summary.get("sub_merge_requests", []):
        if not smr.get("coordinator_ok"):
            continue
        repo = smr.get("repo_path", "")
        iid = str(smr.get("iid", ""))
        safe_repo = repo.replace("/", "_") if repo else f"sub_{iid}"
        items.append({
            "key": f"{safe_repo}_{iid}",
            "repo": repo,
            "mr_id": iid,
            "project_id": smr.get("project_id"),
            "label": f"子 MR: {repo}!{iid}",
            "mr_type": "sub",
            "coordinator_path": smr.get("coordinator_path", ""),
            "web_url": smr.get("web_url", ""),
        })

    return items


def main():
    parser = argparse.ArgumentParser(description="Manifest Analysis Summary - 汇总 AI 分析数据")
    parser.add_argument("--summaryFile", required=True, help="manifest_summary.json 路径")
    parser.add_argument("--outputFile", help="输出文件路径")
    args = parser.parse_args()

    summary = load_summary(args.summaryFile)
    items = collect_all_coordinators(summary)

    result = {
        "manifest_url": summary.get("manifest_url"),
        "total_mr_count": len(items),
        "coordinators": items,
        "failed_count": summary.get("sub_mr_count", 0) - len(items),
    }

    if args.outputFile:
        output_path = Path(args.outputFile)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"[SUCCESS] 输出到: {output_path}")

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
