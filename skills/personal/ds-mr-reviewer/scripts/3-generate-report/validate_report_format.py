#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告格式验证脚本
检查MR检视报告是否符合格式要求：
1. 禁止使用表格（markdown语法 |）
2. 报告必须输出到temp目录下的mr_子目录
"""
import sys
import os
import json
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config_manager import get_temp_dir


def check_output_path(file_path):
    """
    检查报告是否输出到正确目录（temp目录下的mr_子目录）
    返回: (issues, None)
    """
    issues = []
    
    file_path = Path(file_path).resolve()
    temp_dir = get_temp_dir()
    
    if not str(file_path).startswith(str(temp_dir)):
        issues.append(f"报告应输出到temp目录: {temp_dir}")
        issues.append(f"当前路径: {file_path}")
        return issues
    
    parent_dir = file_path.parent
    if not parent_dir.name.startswith('mr_'):
        issues.append(f"报告应放在mr_开头的子目录中")
        issues.append(f"当前目录: {parent_dir}")
        return issues
    
    return issues


def check_table_syntax(file_path):
    """检查是否包含表格语法"""
    issues = []
    in_code_block = False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            if stripped.startswith('```'):
                in_code_block = not in_code_block
                continue
            
            if in_code_block:
                continue
            
            if '|' in line:
                if stripped.startswith('|') or stripped.endswith('|'):
                    if stripped.count('|') >= 2:
                        issues.append(f"第{i}行可能包含表格语法: {stripped[:50]}...")
    return issues


def validate_report(file_path, repo=None, mr_id=None):
    """
    验证报告格式

    Args:
        file_path: 报告文件路径
        repo: 仓库名称（用于日志）
        mr_id: MR ID（用于日志）
    Returns:
        (success, corrected_path): (是否成功, 修正后的路径)
    """
    if not os.path.exists(file_path):
        print(f"[ERROR] 文件不存在: {file_path}")
        return False, None

    print(f"[INFO] 开始验证报告: {file_path}")
    print("-" * 50)
    
    has_issues = False
    
    print("[CHECK 1] 检查表格语法...")
    table_issues = check_table_syntax(file_path)
    if table_issues:
        print("[FAIL] 发现表格语法:")
        for issue in table_issues:
            print(f"  - {issue}")
        has_issues = True
    else:
        print("[PASS] 未发现表格语法")
    
    print("-" * 50)
    
    print("[CHECK 2] 检查报告输出路径...")
    path_issues = check_output_path(file_path)
    if path_issues:
        print("[FAIL] 报告输出路径不正确:")
        for issue in path_issues:
            print(f"  - {issue}")
        has_issues = True
    else:
        print("[PASS] 报告已输出到正确目录")
    
    print("-" * 50)
    
    if has_issues:
        print("[RESULT] 验证失败，请修复上述问题后重新生成报告")
        return False, None
    else:
        print("[RESULT] 验证通过!")
        return True, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='验证MR检视报告格式')
    parser.add_argument('report_path', help='报告文件路径')
    parser.add_argument('--repo', help='仓库名称（用于日志）')
    parser.add_argument('--mrId', help='MR ID（用于日志）')
    args = parser.parse_args()

    report_path = args.report_path
    success, corrected_path = validate_report(report_path, repo=args.repo, mr_id=args.mrId)
    
    result = {
        "success": success,
        "corrected_path": corrected_path,
        "original_path": report_path if not corrected_path else None
    }
    print(json.dumps(result))
    
    sys.exit(0 if success else 1)
