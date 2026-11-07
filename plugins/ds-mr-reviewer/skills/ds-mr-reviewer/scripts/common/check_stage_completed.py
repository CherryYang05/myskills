#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查指定阶段的JSON文件是否已生成，用于强制校验Pipeline执行顺序

Usage:
    python check_stage_completed.py --repo "NCE-T/TransCapacityMapService" --mrId 1830 --stage analysis_stage0

Exit codes:
    0 - 文件存在，检查通过
    1 - 文件不存在或检查失败
"""

import argparse
import sys
from pathlib import Path

TYPE_PREFIX_MAP = {
    'coordinator': 'mr_coordinator',
    'analysis_stage0': 'analysis_stage0',
    'analysis_stage1': 'analysis_stage1',
    'analysis_stage2': 'analysis_stage2',
}

def main():
    parser = argparse.ArgumentParser(description='检查指定阶段的JSON文件是否已生成')
    parser.add_argument('--repo', type=str, required=True, help='Repository name')
    parser.add_argument('--mrId', type=str, required=True, help='MR ID')
    parser.add_argument('--stage', type=str, required=True,
                        choices=TYPE_PREFIX_MAP.keys(),
                        help='Stage type to check')

    args = parser.parse_args()

    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = args.repo.replace('/', '_')
    prefix = TYPE_PREFIX_MAP[args.stage]
    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{args.mrId}"
    target_file = mr_subdir / f"{prefix}.json"

    if target_file.exists():
        print(f"[SUCCESS] {args.stage}.json 文件已生成: {target_file}")
        sys.exit(0)
    else:
        print(f"[ERROR] 缺少 {args.stage}.json 文件: {target_file}")
        print(f"[ERROR] 请先完成 {args.stage} 阶段的分析，再继续执行。")
        sys.exit(1)

if __name__ == "__main__":
    main()