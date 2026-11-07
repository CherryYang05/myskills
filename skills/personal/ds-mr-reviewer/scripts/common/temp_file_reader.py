#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Read content from temp directory (supports MR subdirectories)

Usage:
    python temp_file_reader.py --type coordinator --repo "NCE-T/TxL0L1ServiceV3" --mrId 15273
    python temp_file_reader.py --type coordinator --repo "NCE-T/TxL0L1ServiceV3" --mrId 15273 --raw
"""

import argparse
import json
import sys
from pathlib import Path

TYPE_PREFIX_MAP = {
    'coordinator': 'mr_coordinator',
    'analysis_stage0': 'analysis_stage0',
    'analysis_stage1': 'analysis_stage1',
    'analysis_stage1_5': 'analysis_stage1_5',
    'analysis_stage2': 'analysis_stage2',
    'mr_risks': 'mr_risks',
}


def main():
    from logger_manager import get_logger
    
    parser = argparse.ArgumentParser(description='Read content from temp directory')
    parser.add_argument('--type', type=str, required=True,
                        choices=TYPE_PREFIX_MAP.keys(),
                        help='File type')
    parser.add_argument('--repo', type=str, required=True, help='Repository name')
    parser.add_argument('--mrId', type=str, required=True, help='MR ID')
    parser.add_argument('--raw', action='store_true',
                        help='Output raw text content without JSON parsing (for handling malformed JSON)')

    args = parser.parse_args()

    temp_dir = Path.home() / ".mr-reviewer" / "temp"

    safe_repo_name = args.repo.replace('/', '_')
    mr_info = f"{safe_repo_name}_{args.mrId}"
    logger = get_logger(mr_info)
    
    prefix = TYPE_PREFIX_MAP[args.type]

    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{args.mrId}"
    filename = f"{prefix}.json"

    possible_paths = [
        mr_subdir / filename,
        temp_dir / f"{prefix}_{safe_repo_name}_{args.mrId}.json"
    ]

    logger.info(f"开始读取文件 - type: {args.type}, repo: {args.repo}, mrId: {args.mrId}")

    input_path = None
    for path in possible_paths:
        if path.exists():
            input_path = path
            break

    if not input_path:
        error_msg = f"[ERROR] File not found, tried: {', '.join(str(p) for p in possible_paths)}"
        logger.error(error_msg)
        print(error_msg, file=sys.stderr)
        sys.exit(1)

    logger.info(f"找到文件: {input_path}")

    if args.raw:
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(content)
        logger.info(f"成功读取原始内容 (raw mode)")
    else:
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
            print(json.dumps(content, ensure_ascii=False, indent=2))
            logger.info(f"成功解析JSON并输出")
        except json.JSONDecodeError as e:
            error_msg = f"[ERROR] JSON解析失败: {e}"
            hint_msg = f"[HINT] 如果文件格式有误，可以使用 --raw 参数读取原始内容"
            logger.error(error_msg)
            print(error_msg, file=sys.stderr)
            print(hint_msg, file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()