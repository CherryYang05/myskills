#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Batch Merger - 合并规则分批检视的结果

将多个 analysis_stage1_batch{i}.json 合并为标准的 analysis_stage1.json，
格式与原有完全一致，确保后续 Stage 无感知。

Usage:
    python mr_batch_merger.py --repo "NCE-T_TxL0L1ServiceV3" --mrId 15166

Input:
    ~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage1_batch1.json
    ~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage1_batch2.json
    ...

Output:
    ~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage1.json
"""

import argparse
import json
import sys
from pathlib import Path

# selfCheck 值的优先级：违规 > 通过 > 不涉及
SELF_CHECK_PRIORITY = {
    "违规": 0,
    "通过": 1,
    "不涉及": 2,
}


def get_merge_priority(value):
    """获取 selfCheck 值的合并优先级（数值越小优先级越高）"""
    for key, priority in SELF_CHECK_PRIORITY.items():
        if value.startswith(key):
            return priority
    return 99  # 未知格式排最后


def merge_self_checks(all_self_checks):
    """
    合并多个批次的 selfCheck。

    同一 rule_id 只应出现在一个批次中（因为批次是按 rule_id 互斥划分的），
    但做防御性合并：违规优先级最高。

    Args:
        all_self_checks: list of dict, 每个批次一个 selfCheck

    Returns:
        dict: 合并后的 selfCheck
    """
    merged = {}
    for self_check in all_self_checks:
        for rule_id, value in self_check.items():
            if rule_id not in merged:
                merged[rule_id] = value
            else:
                # 取优先级更高的（违规 > 通过 > 不涉及）
                existing_priority = get_merge_priority(merged[rule_id])
                new_priority = get_merge_priority(value)
                if new_priority < existing_priority:
                    merged[rule_id] = value
    return merged


def merge_violation_details(all_violation_details):
    """
    合并多个批次的 violation_details，按 (rule_id, file_path, line_number) 去重。

    Args:
        all_violation_details: list of list, 每个批次一个 violation_details

    Returns:
        list: 合并去重后的 violation_details
    """
    seen = set()
    merged = []

    for details in all_violation_details:
        for detail in details:
            rule_id = detail.get("rule_id", "")
            file_path = detail.get("file", "")
            line = str(detail.get("line", ""))
            dedup_key = f"{rule_id}|{file_path}|{line}"

            if dedup_key not in seen:
                seen.add(dedup_key)
                merged.append(detail)

    return merged


def find_batch_files(mr_subdir):
    """
    查找所有 analysis_stage1_batch*.json 文件。

    Returns:
        list of Path: 按批次号排序的文件路径列表
    """
    import re

    batch_files = []
    for f in mr_subdir.iterdir():
        if f.is_file() and f.name.startswith("analysis_stage1_batch") and f.name.endswith(".json"):
            match = re.search(r'batch(\d+)', f.name)
            if match:
                batch_id = int(match.group(1))
                batch_files.append((batch_id, f))

    batch_files.sort(key=lambda x: x[0])
    return [f for _, f in batch_files]


def main():
    parser = argparse.ArgumentParser(
        description='MR Batch Merger - 合并规则分批检视结果'
    )
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--mrId', required=True, help='MR ID')

    args = parser.parse_args()

    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = args.repo.replace('/', '_')
    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{args.mrId}"

    if not mr_subdir.exists():
        print(f"[ERROR] 目录不存在: {mr_subdir}", file=sys.stderr)
        sys.exit(1)

    # 查找所有 batch 文件
    batch_files = find_batch_files(mr_subdir)

    if not batch_files:
        print(f"[ERROR] 未找到任何 analysis_stage1_batch*.json 文件", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] 找到 {len(batch_files)} 个批次文件")

    # 读取所有批次结果
    all_self_checks = []
    all_violation_details = []
    total_rules_applied = 0
    total_rules_related = 0
    total_rules_violated = 0

    for batch_file in batch_files:
        try:
            with open(batch_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"[WARN] 文件解析失败，跳过: {batch_file.name} - {e}", file=sys.stderr)
            continue

        self_check = data.get("selfCheck", {})
        violation_details = data.get("violation_details", [])

        all_self_checks.append(self_check)
        all_violation_details.append(violation_details)

        total_rules_applied += data.get("rules_applied", 0)
        total_rules_related += data.get("rules_related", 0)
        total_rules_violated += data.get("rules_violated", 0)

    # 合并
    merged_self_check = merge_self_checks(all_self_checks)
    merged_violation_details = merge_violation_details(all_violation_details)

    # 重新计算统计（以合并后的 selfCheck 为准）
    rules_related = sum(1 for v in merged_self_check.values() if not v.startswith("不涉及"))
    rules_violated = sum(1 for v in merged_self_check.values() if v.startswith("违规"))

    # 生成标准格式的 analysis_stage1.json
    result = {
        "rules_applied": len(merged_self_check),
        "rules_related": rules_related,
        "rules_violated": rules_violated,
        "selfCheck": merged_self_check,
        "violation_details": merged_violation_details,
    }

    # 写入
    output_path = mr_subdir / "analysis_stage1.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[SUCCESS] 合并完成: {output_path}")
    print(f"  批次数: {len(batch_files)}")
    print(f"  总规则数: {len(merged_self_check)}")
    print(f"  相关规则: {rules_related}")
    print(f"  违规规则: {rules_violated}")
    print(f"  违规详情: {len(merged_violation_details)} 条")


if __name__ == '__main__':
    main()
