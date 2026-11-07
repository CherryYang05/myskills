#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Diff Reader

Usage:
    python mr_diff_reader.py --repo "NCE-T_TxL0L1ServiceV3" --mrId 15228
    python mr_diff_reader.py --repo "NCE-T_TxL0L1ServiceV3" --mrId 15228 --file "srlgdetect/src/main/java/com/huawei/nce/transavailabilityassuranceservice/srlgdetect/business/impl/FiberGroupBusinessV2Impl.java"

从mr_coordinator输出的JSON文件中读取完整的diff内容，
解决AI直接读取JSON文件时因Read工具输出限制导致diff信息不完整的问题。

输出格式：
    ---DIFF_START---
    <完整的diff内容>
    ---DIFF_END---
    ---METADATA---
    {
        "total_files": <文件数>,
        "files": [
            {
                "path": "<文件路径>",
                "diff_length": <diff长度>,
                "lines": <行数>
            }
        ],
        "total_diff_length": <总diff长度>
    }
    ---METADATA_END---
"""

import argparse
import json
import sys
from pathlib import Path

# 将 scripts 目录添加到 Python 路径，以便导入 common 模块
# 脚本路径: skills/mr-reviewer/scripts/2-ai-analysis/mr_diff_reader.py
# common 模块在: skills/mr-reviewer/scripts/common/
scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

# 导入 logger_manager（位于 common 子目录）
from common.logger_manager import get_logger


def get_coordinator_path(repo_name, mr_id):
    """根据repo和mrId获取coordinator文件路径"""
    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = repo_name.replace('/', '_')
    coordinator_path = temp_dir / f"mr_{safe_repo_name}_{mr_id}" / "mr_coordinator.json"
    return coordinator_path


def read_json_file(file_path):
    """读取JSON文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] 文件不存在: {file_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON解析失败: {e}", file=sys.stderr)
        sys.exit(1)


def find_matching_diffs(diffs, file_path):
    """
    查找匹配的diff项。

    匹配规则（优先级从高到低）：
    1. 全路径精确匹配：diff的new_path或old_path与file_path完全相等
    2. 部分路径匹配：diff的new_path或old_path包含file_path

    Returns:
        匹配的diff列表
    """
    # 第一轮：全路径精确匹配
    exact_matches = [
        d for d in diffs
        if d.get("new_path") == file_path or d.get("old_path") == file_path
    ]
    if exact_matches:
        return exact_matches

    # 第二轮：部分路径匹配（全路径包含file_path）
    partial_matches = [
        d for d in diffs
        if file_path in (d.get("new_path") or "") or file_path in (d.get("old_path") or "")
    ]
    return partial_matches


def analyze_diffs(diffs):
    """
    分析diff内容，返回元数据
    """
    metadata = {
        "total_files": len(diffs),
        "files": [],
        "total_diff_length": 0
    }

    for diff_item in diffs:
        diff_content = diff_item.get("diff", "")
        file_path = diff_item.get("new_path") or diff_item.get("old_path", "unknown")

        file_info = {
            "path": file_path,
            "diff_length": len(diff_content),
            "lines": len(diff_content.split('\n'))
        }

        metadata["files"].append(file_info)
        metadata["total_diff_length"] += len(diff_content)

    return metadata


def format_output(diffs, metadata):
    """格式化输出"""
    output_parts = []

    output_parts.append("---DIFF_START---")
    for diff_item in diffs:
        file_path = diff_item.get("new_path") or diff_item.get("old_path", "unknown")
        diff_content = diff_item.get("diff", "")

        output_parts.append(f"\n=== FILE: {file_path} ===\n")
        output_parts.append(diff_content)
    output_parts.append("---DIFF_END---")

    output_parts.append("\n---METADATA---")
    output_parts.append(json.dumps(metadata, ensure_ascii=False, indent=2))
    output_parts.append("---METADATA_END---")

    return "".join(output_parts)


def main():
    parser = argparse.ArgumentParser(
        description='MR Diff Reader - 从mr_coordinator JSON文件中读取完整diff内容'
    )
    parser.add_argument(
        '--repo',
        required=True,
        help='仓库名称（如：NCE-T_TxL0L1ServiceV3）'
    )
    parser.add_argument(
        '--mrId',
        required=True,
        help='MR ID'
    )
    parser.add_argument(
        '--file',
        dest='specific_file',
        help='只输出指定文件的diff（传入文件路径，支持部分匹配）'
    )

    args = parser.parse_args()

    mr_info = f"{args.repo}_{args.mrId}"
    json_file_path = get_coordinator_path(args.repo, args.mrId)

    logger = get_logger(mr_info)
    logger.info(f"开始读取diff文件")

    data = read_json_file(json_file_path)

    diffs = data.get("diffs", [])
    if not diffs:
        print("[WARN] 未找到diff内容", file=sys.stderr)
        sys.exit(1)

    if args.specific_file:
        diffs = find_matching_diffs(diffs, args.specific_file)
        if not diffs:
            print(f"[WARN] 未找到文件 {args.specific_file} 的diff", file=sys.stderr)
            sys.exit(1)

    metadata = analyze_diffs(diffs)
    output = format_output(diffs, metadata)
    print(output)
    logger.info(f"成功读取diff内容 - 文件数: {metadata['total_files']}, 总长度: {metadata['total_diff_length']}")


if __name__ == '__main__':
    main()