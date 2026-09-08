#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Review WeLink Notifier

此脚本在检视完成后发送WeLink通知。从mr_coordinator.json中读取risk_level和report_share_url。
上传报告到OneBox、提交Discussion等逻辑已分别移至步骤3和步骤4。

Usage:
    # 方式1：直接传入coordinator路径
    python mr_notify_after_analysis.py --mrInfoFile <coordinator路径>

    # 方式2：传入repo和mrId，自动计算coordinator和report路径
    python mr_notify_after_analysis.py --repo "{repo}" --mrId {mrId}
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime
import io


TYPE_PREFIX_MAP = {
    'coordinator': 'mr_coordinator',
    'analysis_stage0': 'analysis_stage0',
    'analysis_stage1': 'analysis_stage1',
    'analysis_stage2': 'analysis_stage2',
    'mr_risks': 'mr_risks',
}

REPORT_VALID_RISK_LEVELS = {'high', 'medium', 'low'}


def get_temp_file_path(file_type, repo, mr_id):
    """
    计算临时文件路径

    Args:
        file_type: 文件类型 (如 'coordinator')
        repo: 仓库名称
        mr_id: MR ID

    Returns:
        Path: 文件绝对路径
    """
    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = repo.replace('/', '_')
    prefix = TYPE_PREFIX_MAP.get(file_type, file_type)
    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{mr_id}"
    mr_subdir.mkdir(parents=True, exist_ok=True)
    return mr_subdir / f"{prefix}.json"


def normalize_risk_level(risk_level: str) -> str:
    """规范化风险等级"""
    if not risk_level:
        return ''
    mapping = {'高': 'high', '中': 'medium', '低': 'low'}
    for k, v in mapping.items():
        if k in risk_level:
            return v
    return risk_level if risk_level in REPORT_VALID_RISK_LEVELS else ''


def get_report_path(repo: str, mr_id: str) -> tuple:
    """
    计算报告文件路径

    Args:
        repo: 仓库名称
        mr_id: MR ID

    Returns:
        tuple: (report_path, risk_level)
    """
    mr_info_file = get_temp_file_path('coordinator', repo, mr_id)
    if not mr_info_file.exists():
        raise FileNotFoundError(f"coordinator文件不存在: {mr_info_file}")

    mr_subdir = mr_info_file.parent
    report_files = list(mr_subdir.glob("mr_review_report_*.md"))
    if not report_files:
        raise FileNotFoundError(f"未找到报告文件: {mr_subdir}/mr_review_report_*.md")
    if len(report_files) > 1:
        print(f"[WARN] 找到多个报告文件，使用最新修改的: {report_files[-1]}")
    report_path = report_files[-1]

    risk_level = ''
    filename = report_path.stem
    for lvl in REPORT_VALID_RISK_LEVELS:
        if filename.endswith(f"_{lvl}"):
            risk_level = lvl
            break

    return report_path, risk_level

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from logger_manager import get_logger


class MRWeLinkNotifier:
    """MR WeLink通知器（简化版，仅发送通知）"""

    def __init__(self, config_path=None):
        self.scripts_dir = Path(__file__).parent
        if config_path:
            self.config_path = Path(config_path)
        else:
            user_config = Path.home() / ".mr-reviewer" / "config.json"
            skill_config = Path(__file__).parent.parent.parent / "config.json"
            self.config_path = user_config if user_config.exists() else skill_config
        self.welink_notifier_script = self.scripts_dir / "mr_welink_notifier.py"
        self.config = self._load_config()

    def _load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] 加载配置文件失败: {e}")
            return {}

    def _extract_mr_info(self, mr_info_file):
        """
        从mr_info_file路径中提取repo_name和mr_id

        Args:
            mr_info_file: MR信息JSON文件路径

        Returns:
            tuple: (safe_repo_name, mr_id)
        """
        safe_repo_name = "unknown"
        mr_id = "unknown"
        try:
            mr_info_path = Path(mr_info_file)
            parent_dir = mr_info_path.parent.name
            if parent_dir.startswith("mr_"):
                parts = parent_dir[3:].rsplit("_", 1)
                if len(parts) == 2:
                    safe_repo_name = parts[0]
                    mr_id = parts[1]
        except Exception:
            pass
        return safe_repo_name, mr_id

    def send_notification(self, mr_info_file, report_path, risk_level=None, share_url=None):
        """
        发送Welink通知

        Args:
            mr_info_file: MR信息JSON文件路径
            report_path: 报告文件路径
            risk_level: 风险等级（可选，未指定则从coordinator读取）
            share_url: OneBox分享链接（可选，未指定则从coordinator读取）

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            with open(mr_info_file, 'r', encoding='utf-8') as f:
                mr_data = json.load(f)
        except Exception as e:
            return False, f"读取MR信息失败: {e}"

        # 从coordinator获取risk_level和share_url
        if risk_level is None:
            risk_level = mr_data.get("risk_level", "低")
            print(f"[INFO] 从coordinator读取风险等级: {risk_level}")

        if share_url is None:
            share_url = mr_data.get("report_share_url")
            if share_url:
                print(f"[INFO] 从coordinator读取报告分享链接: {share_url}")

        # 风险等级标准化处理
        risk_level_mapping = {
            '高': 'high',
            '中': 'medium',
            '低': 'low',
            '中等': 'medium',
            '普通': 'low',
            '低风险': 'low',
            '中风险': 'medium',
            '高风险': 'high',
        }
        risk_level = risk_level_mapping.get(risk_level, risk_level if risk_level in ['high', 'medium', 'low'] else 'low')

        cmd = [
            sys.executable,
            str(self.welink_notifier_script),
            "--mrInfoFile", str(mr_info_file),
            "--reportPath", str(report_path),
            "--riskLevel", risk_level,
            "--configPath", str(self.config_path)
        ]

        if share_url:
            cmd.extend(["--shareUrl", share_url])

        print("[INFO] 调用Welink通知脚本...")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8', errors='replace')
            if result.returncode == 0:
                return True, "Welink通知发送成功"
            else:
                return False, f"Welink通知失败: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, "Welink通知请求超时"
        except Exception as e:
            return False, f"Welink通知异常: {e}"

    def run(self, mr_info_file, report_path):
        """
        执行WeLink通知流程

        Args:
            mr_info_file: mr_coordinator.json文件路径
            report_path: 报告文件路径

        Returns:
            tuple: (success: bool, message: str)
        """
        start_time = time.time()

        safe_repo_name, mr_id = self._extract_mr_info(mr_info_file)
        logger = get_logger(f"{safe_repo_name}_{mr_id}")

        logger.info("开始 - 发送WeLink通知")

        # 验证文件存在
        if not Path(report_path).exists():
            logger.error(f"失败 - 报告文件不存在: {report_path}")
            return False, f"报告文件不存在: {report_path}"

        if not Path(mr_info_file).exists():
            logger.error(f"失败 - MR信息文件不存在: {mr_info_file}")
            return False, f"MR信息文件不存在: {mr_info_file}"

        # 发送Welink通知
        notify_start = time.time()
        success, message = self.send_notification(mr_info_file, report_path)
        notify_duration = time.time() - notify_start

        if success:
            logger.info(f"WeLink通知发送成功 (耗时: {notify_duration:.2f}秒)")
        else:
            logger.error(f"WeLink通知发送失败: {message} (耗时: {notify_duration:.2f}秒)")

        total_duration = time.time() - start_time
        logger.info(f"完成 - 总耗时: {total_duration:.2f}秒")

        return success, message


def main():
    parser = argparse.ArgumentParser(description='MR Review WeLink Notifier - 发送WeLink通知')
    parser.add_argument('--mrInfoFile', help='mr_coordinator.json文件路径 (与--repo+--mrId二选一)')
    parser.add_argument('--repo', help='仓库名称 (与--repo+--mrId配合使用)')
    parser.add_argument('--mrId', help='MR ID (与--repo配合使用)')
    parser.add_argument('--configPath', help='config.json路径')

    args = parser.parse_args()

    if args.repo and args.mrId:
        mr_info_file = str(get_temp_file_path('coordinator', args.repo, args.mrId))
        report_path, _ = get_report_path(args.repo, args.mrId)
        print(f"[INFO] 自动计算coordinator路径: {mr_info_file}")
        print(f"[INFO] 自动计算报告路径: {report_path}")
    elif args.mrInfoFile:
        mr_info_file = args.mrInfoFile
        mr_info_path = Path(mr_info_file)
        parent_dir = mr_info_path.parent.name
        if parent_dir.startswith("mr_"):
            parts = parent_dir[3:].rsplit("_", 1)
            if len(parts) == 2:
                repo_from_path = parts[0].replace('_', '/')
                mr_id_from_path = parts[1]
                try:
                    report_path, _ = get_report_path(repo_from_path, mr_id_from_path)
                    print(f"[INFO] 从mrInfoFile路径推断报告路径: {report_path}")
                except Exception:
                    report_path = None
            else:
                report_path = None
        else:
            report_path = None
    else:
        print("[ERROR] 必须提供--repo+--mrId")
        sys.exit(1)

    notifier = MRWeLinkNotifier(config_path=args.configPath)
    success, message = notifier.run(
        mr_info_file=mr_info_file,
        report_path=str(report_path) if report_path else None
    )

    if success:
        print(f"[SUCCESS] {message}")
        sys.exit(0)
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)


if __name__ == '__main__':
    main()
