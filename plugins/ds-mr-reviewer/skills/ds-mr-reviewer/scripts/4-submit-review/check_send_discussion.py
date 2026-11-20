#!/usr/bin/env python3
"""
获取send_discussion_level配置，判断是否需要提交Discussion
- 读取config.json的send_discussion_level配置
- 输出配置值，由AI根据配置和MR风险等级判断是否需要提交Discussion
- 当判断不需要提交Discussion时（mode=review），自动上报表2场景数据

Usage:
    python check_send_discussion.py --mode <review|fix|local> --mrInfoFile <path> --riskLevel <高|中|低>
"""

import argparse
import json
import os
import sys
from pathlib import Path


def get_config_path():
    """获取config.json路径"""
    home = Path.home()
    return home / ".mr-reviewer" / "config.json"


def get_send_discussion_level():
    """获取send_discussion_level配置"""
    config_path = get_config_path()

    if not config_path.exists():
        print("EMPTY")
        print("config.json不存在，send_discussion_level配置为空")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
    except Exception as e:
        print("EMPTY")
        print(f"读取config.json失败: {e}，send_discussion_level配置为空")
        return None

    send_discussion_level = config.get("send_discussion_level")

    if send_discussion_level is None:
        print("EMPTY")
        print("send_discussion_level配置不存在")
        return None

    if not isinstance(send_discussion_level, list):
        print("EMPTY")
        print(f"send_discussion_level配置类型错误: {type(send_discussion_level)}，需要是数组")
        return None

    print(f"send_discussion_level={json.dumps(send_discussion_level, ensure_ascii=False)}")
    return send_discussion_level


def _get_risk_counts_from_coordinator(mr_info_file):
    """从 mr_coordinator.json 同目录的 analysis_stage2.json 读取风险统计

    Returns:
        tuple: (high_count, medium_count, low_count) 或 (0, 0, 0)
    """
    coordinator_path = Path(mr_info_file)
    if not coordinator_path.exists():
        return 0, 0, 0

    coordinator_dir = coordinator_path.parent
    stage2_file = coordinator_dir / "analysis_stage2.json"

    if not stage2_file.exists():
        return 0, 0, 0

    try:
        with open(stage2_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        high = len(data.get("high_risks", []))
        medium = len(data.get("medium_risks", []))
        low = len(data.get("low_risks", []))
        return high, medium, low
    except Exception:
        return 0, 0, 0


def _get_mr_info(mr_info_file):
    """读取 mr_coordinator.json 中的 MR 信息

    Returns:
        dict 或 None
    """
    coordinator_path = Path(mr_info_file)
    if not coordinator_path.exists():
        return None
    try:
        with open(coordinator_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # 兼容 mr_info 包装和直接结构
        return data.get("mr_info", data)
    except Exception:
        return None


def _report_scenario_on_skip(mr_info_file, risk_level):
    """跳过Discussion时上报场景数据（仅检视模式）

    Args:
        mr_info_file: mr_coordinator.json 路径
        risk_level: 当前MR风险等级（高/中/低）
    """
    mr_info = _get_mr_info(mr_info_file)
    if not mr_info:
        print("[WARN] 无法读取MR信息，场景数据上报跳过")
        return

    # 获取风险统计
    high, medium, low = _get_risk_counts_from_coordinator(mr_info_file)
    problem_count = high + medium + low

    # 提取仓库路径
    web_url = mr_info.get("web_url") or ""
    repository = ""
    if web_url:
        try:
            from urllib.parse import urlparse
            path = urlparse(web_url).path.strip("/")
            parts = path.split("/")
            if len(parts) >= 2 and "merge_requests" in path:
                idx = parts.index("merge_requests")
                if idx >= 2:
                    repository = "/".join(parts[:idx])
        except Exception:
            pass

    # 上报场景数据
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
        from report_usage import report_scenario

        payload = {
            "scenarioName": "AI_REVIEW",
            "account": os.environ.get("USERNAME", ""),
            "repository": repository,
            "targetBranch": mr_info.get("target_branch", ""),
            "mrLink": web_url,
            "problemCount": problem_count,
            "reviewCommentCount": 0,  # 未提交Discussion
            "result": "SUCCESS"
        }
        report_scenario(payload)
        print(f"[INFO] 跳过Discussion提交，场景数据已上报: repository={repository}, "
              f"problemCount={problem_count} (高={high},中={medium},低={low}), "
              f"reviewCommentCount=0, risk_level={risk_level}")
    except Exception as e:
        print(f"[WARN] 场景数据上报失败: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="检查是否需要提交Discussion")
    parser.add_argument("--mode", choices=["review", "fix", "local"], default="review",
                        help="运行模式：review=检视模式, fix=修复模式, local=本地模式")
    parser.add_argument("--mrInfoFile", help="mr_coordinator.json文件路径")
    parser.add_argument("--riskLevel", help="当前MR风险等级（高/中/低）")

    args = parser.parse_args()

    # 获取 send_discussion_level 配置
    send_discussion_level = get_send_discussion_level()

    # 判断是否需要提交 Discussion
    need_discussion = True
    skip_reason = ""

    if send_discussion_level is None or len(send_discussion_level) == 0:
        need_discussion = False
        skip_reason = "send_discussion_level为空"
    elif args.riskLevel:
        if args.riskLevel not in send_discussion_level:
            need_discussion = False
            skip_reason = f"risk_level={args.riskLevel} 不在 send_discussion_level={json.dumps(send_discussion_level, ensure_ascii=False)} 中"

    # 不需要提交 Discussion 时
    if not need_discussion:
        print(f"SKIP_DISCUSSION")
        print(f"原因: {skip_reason}")

        # 检视模式下自动上报场景数据
        if args.mode == "review" and args.mrInfoFile:
            _report_scenario_on_skip(args.mrInfoFile, args.riskLevel or "未知")
        elif args.mode == "review" and not args.mrInfoFile:
            print("[WARN] 检视模式但未提供 --mrInfoFile，场景数据上报跳过")
