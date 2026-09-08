#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告文件名生成脚本
根据 mr_coordinator.json 中的 risk_level 生成报告文件名
risk_level 规范化规则：
- 包含"高"返回"高"，包含"中"返回"中"，包含"低"返回"低"
- 如果 risk_level 为空，不拼接后缀
- 其他情况保持原值
"""
import sys
import os
import json
import argparse
from pathlib import Path

RISK_LEVEL_PATTERNS = {
    '高': 'high',
    '中': 'medium',
    '低': 'low',
}

VALID_RISK_LEVELS = {'high', 'medium', 'low'}


def normalize_risk_level(risk_level: str) -> str:
    """
    规范化风险等级
    - 如果为空，返回空字符串
    - 如果包含"高"但不是"中高"这类组合，返回"高"
    - 如果包含"中"，返回"中"
    - 如果包含"低"，返回"低"
    - 其他情况保持原值
    """
    if not risk_level:
        return ''
    
    for pattern, normalized in RISK_LEVEL_PATTERNS.items():
        if pattern in risk_level:
            return normalized
    
    return risk_level


def get_report_filename(repo: str, mr_id: str, risk_level: str) -> str:
    """
    生成报告文件名
    
    Args:
        repo: 仓库名称（如 NCE-T/TransFeatureQKD）
        mr_id: MR ID
        risk_level: 风险等级（high/medium/low 或空）
    
    Returns:
        报告文件名：mr_review_report_{repository_name}_{mr_id}_{risk_level}.md
                     （如果 risk_level 为空或不是有效值，则为 mr_review_report_{repository_name}_{mr_id}.md）
    """
    repo_name = repo.replace('/', '_')
    
    if risk_level and risk_level in VALID_RISK_LEVELS:
        return f"mr_review_report_{repo_name}_{mr_id}_{risk_level}.md"
    else:
        return f"mr_review_report_{repo_name}_{mr_id}.md"


def get_risk_level_from_analysis_stage2(coordinator_dir: Path) -> str:
    """
    从 analysis_stage2.json 读取 risk_level 并规范化
    优先从此文件读取，因为 risk_level 是在 AI 分析阶段才确定的
    """
    stage2_file = coordinator_dir / "analysis_stage2.json"
    if not stage2_file.exists():
        return ''
    
    try:
        with open(stage2_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        risk_level = data.get('risk_level', '')
        return normalize_risk_level(risk_level)
    except Exception:
        return ''


def get_risk_level_from_mr_coordinator(coordinator_file: Path) -> str:
    """
    从 mr_coordinator.json 读取 risk_level 并规范化
    作为 fallback，在 analysis_stage2.json 不存在或 risk_level 为空时使用
    """
    if not coordinator_file.exists():
        raise FileNotFoundError(f"文件不存在: {coordinator_file}")
    
    with open(coordinator_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    risk_level = data.get('risk_level', '')
    normalized_level = normalize_risk_level(risk_level)
    
    if risk_level != normalized_level:
        print(f"[WARN] 发现 risk_level: '{risk_level}'，规范化为 '{normalized_level}'")
    
    return normalized_level


def generate_report_filename(coordinator_dir: Path, repo: str, mr_id: str) -> tuple:
    """
    根据 mr_coordinator.json 生成报告文件名
    
    优先级：
    1. analysis_stage2.json（AI分析阶段生成，包含最终 risk_level）
    2. mr_coordinator.json（数据准备阶段生成，risk_level 可能为空）
    
    Returns:
        (filename, risk_level, coordinator_file_path)
    """
    coordinator_file = coordinator_dir / "mr_coordinator.json"
    
    # 优先从 analysis_stage2.json 读取 risk_level
    risk_level = get_risk_level_from_analysis_stage2(coordinator_dir)
    
    # 如果为空，则从 mr_coordinator.json 读取（兼容旧版本或前置检查未通过的场景）
    if not risk_level:
        risk_level = get_risk_level_from_mr_coordinator(coordinator_file)
    
    filename = get_report_filename(repo, mr_id, risk_level)
    return filename, risk_level, str(coordinator_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='生成MR检视报告文件名')
    parser.add_argument('--repo', required=True, help='仓库名称（如 NCE-T/TransFeatureQKD）')
    parser.add_argument('--mrId', required=True, help='MR ID')
    parser.add_argument('--coordinatorDir', help='mr_coordinator.json 所在目录（默认从 temp 目录推断）')
    args = parser.parse_args()
    
    if args.coordinatorDir:
        coordinator_dir = Path(args.coordinatorDir)
    else:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
        from config_manager import get_temp_dir
        temp_dir = get_temp_dir()
        repo_part = args.repo.replace('/', '_')
        coordinator_dir = temp_dir / f"mr_{repo_part}_{args.mrId}"
    
    try:
        filename, risk_level, coordinator_path = generate_report_filename(coordinator_dir, args.repo, args.mrId)
        print(f"仓库: {args.repo}")
        print(f"MR ID: {args.mrId}")
        print(f"风险等级: {risk_level if risk_level else '(空)'}")
        print(f"报告文件名: {filename}")
        print(f"mr_coordinator.json: {coordinator_path}")
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
