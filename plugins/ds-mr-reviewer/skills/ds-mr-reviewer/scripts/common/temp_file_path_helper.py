#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate correct temp file paths for AI to write directly

Usage:
    python temp_file_path_helper.py --type analysis_stage1 --repo "NCE-T/TransCapacityMapService" --mrId 1830

Output:
    Returns the absolute path where AI should write the JSON file
"""

import argparse
import sys
from pathlib import Path

TYPE_PREFIX_MAP = {
    'coordinator': 'mr_coordinator',
    'analysis_stage0': 'analysis_stage0',
    'analysis_stage1': 'analysis_stage1',
    'analysis_stage1_batch': 'analysis_stage1_batch',
    'analysis_stage1_5': 'analysis_stage1_5',
    'analysis_stage2': 'analysis_stage2',
    'mr_risks': 'mr_risks',
}

def main():
    from logger_manager import get_logger
    
    parser = argparse.ArgumentParser(description='Generate temp file path')
    parser.add_argument('--type', type=str, required=True,
                        choices=TYPE_PREFIX_MAP.keys(),
                        help='File type')
    parser.add_argument('--repo', type=str, required=True, help='Repository name')
    parser.add_argument('--mrId', type=str, required=True, help='MR ID')

    args = parser.parse_args()

    safe_repo_name = args.repo.replace('/', '_')
    mr_info = f"{safe_repo_name}_{args.mrId}"
    logger = get_logger(mr_info)

    logger.info(f"开始生成路径 - type: {args.type}, repo: {args.repo}, mrId: {args.mrId}")

    temp_dir = Path.home() / ".mr-reviewer" / "temp"

    prefix = TYPE_PREFIX_MAP[args.type]

    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{args.mrId}"
    mr_subdir.mkdir(parents=True, exist_ok=True)

    filename = f"{prefix}.json"
    output_path = mr_subdir / filename

    logger.info(f"生成路径: {output_path}")

    print(str(output_path))

if __name__ == "__main__":
    main()