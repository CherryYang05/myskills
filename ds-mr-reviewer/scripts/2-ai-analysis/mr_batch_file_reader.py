#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量读取MR修改的文件内容

用于帮助AI更高效地分析所有修改的文件，执行阶段1的文件级检视

Usage:
    python mr_batch_file_reader.py --repo "NCE-T_TxL0L1ServiceV3" --mrId 15166
    
Output:
    打印每个修改文件的路径和内容摘要
"""

import argparse
import json
import os
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='批量读取MR修改的文件内容')
    parser.add_argument('--repo', type=str, required=True, help='Repository name')
    parser.add_argument('--mrId', type=str, required=True, help='MR ID')
    parser.add_argument('--max-files', type=int, default=25, help='最大处理文件数')
    
    args = parser.parse_args()
    
    # 获取用户目录下的临时文件目录
    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    repo_name = args.repo.replace('/', '_')
    mr_dir = temp_dir / f"mr_{repo_name}_{args.mrId}"
    coordinator_file = mr_dir / "mr_coordinator.json"
    
    if not coordinator_file.exists():
        print(f"[ERROR] coordinator文件不存在: {coordinator_file}")
        print(f"[INFO] 请先运行: python scripts/1-prepare-data/mr_coordinator.py --mrUrl \"...\"")
        return
    
    # 读取coordinator
    with open(coordinator_file, 'r', encoding='utf-8') as f:
        coordinator = json.load(f)
    
    # 获取代码仓路径
    repo_path = coordinator.get('repository', {}).get('local_path')
    if not repo_path:
        print("[ERROR] 无法获取代码仓路径")
        return
    
    repo_path = Path(repo_path)
    if not repo_path.exists():
        print(f"[ERROR] 代码仓路径不存在: {repo_path}")
        return
    
    # 获取修改的文件列表
    modified_files = coordinator.get('modified_files', [])
    
    print("=" * 60)
    print(f"开始分析 {len(modified_files)} 个修改文件")
    print("=" * 60)
    
    # 遍历每个修改文件
    for i, file_path in enumerate(modified_files[:args.max_files]):
        if not file_path:
            continue
            
        full_path = repo_path / file_path
        print(f"\n[{i+1}/{len(modified_files)}] 文件: {file_path}")
        print("-" * 50)
        
        if not full_path.exists():
            print(f"  [SKIP] 文件不存在")
            continue
        
        try:
            # 读取文件内容（限制行数）
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            total_lines = len(lines)
            print(f"  总行数: {total_lines}")
            
            # 显示文件开头部分
            preview_lines = min(30, total_lines)
            print(f"  前{preview_lines}行:")
            for line in lines[:preview_lines]:
                print(f"    {line.rstrip()}")
                
            if total_lines > preview_lines:
                print(f"    ... (还有 {total_lines - preview_lines} 行)")
                
        except Exception as e:
            print(f"  [ERROR] 读取失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"分析完成，共处理 {min(len(modified_files), args.max_files)} 个文件")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()