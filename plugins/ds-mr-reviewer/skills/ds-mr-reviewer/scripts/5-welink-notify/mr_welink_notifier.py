#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeLink Notifier for MR Review

Usage:
    python mr_welink_notifier.py --mrInfoFile mr_info.json --riskLevel 高 --reportUrl "report_url"
"""

import argparse
import asyncio
import json
import os
import re
import sys
from pathlib import Path
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from mcp_client_utils import (
        get_auth_token, build_mcp_headers, create_direct_http_client
    )
from fastmcp import Client
from fastmcp.client import StreamableHttpTransport

TZ_AI_MCP_URL = "http://tianzhou.huawei.com/agent/tools/common/mcp"
TZ_AI_TOOL_NAME = "sendWeLinkMemberMsg"


class WeLinkNotifier:
    """WeLink通知发送器"""

    def __init__(self, configPath=None):
        self.configPath = configPath or self._get_default_config_path()
        self.config = None

    def _get_default_config_path(self):
        """获取默认的config.json路径 - 只从用户目录读取"""
        user_config = Path.home() / ".mr-reviewer" / "config.json"
        if user_config.exists():
            return user_config
        raise FileNotFoundError(f"配置文件不存在: {user_config}")

    def load_config(self):
        """从config.json加载配置 - 只从用户目录读取"""
        config_path = Path(self.configPath) if not isinstance(self.configPath, Path) else self.configPath
        user_config = Path.home() / ".mr-reviewer" / "config.json"
        
        # 优先使用用户目录配置
        if user_config.exists():
            config_path = user_config
        else:
            print(f"[ERROR] 配置文件不存在: {user_config}")
            return False, f"配置文件不存在: {user_config}"

        try:
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
            return True, None
        except Exception as e:
            return False, f"Error loading config: {str(e)}"

    def construct_receiver_uid(self, author_id):
        """
        从author_id构造receiver_uid

        Args:
            author_id: 作者工号（如 s00633127）

        Returns:
            str: receiver_uid
        """
        if author_id and isinstance(author_id, str):
            return author_id
        return None

    async def _send_notification_via_mcp(self, content, receiver_uid):
        """
        通过MCP发送WeLink通知（异步）

        Args:
            content: 通知内容
            receiver_uid: 接收者UID

        Returns:
            tuple: (success: bool, message: str)
        """
        if not receiver_uid:
            return False, "receiver_uid is empty"

        if not content:
            return False, "content is empty"

        try:
            token = get_auth_token()
            headers = build_mcp_headers(token)
            transport = StreamableHttpTransport(
                url=TZ_AI_MCP_URL,
                headers=headers,
                httpx_client_factory=create_direct_http_client,
            )

            async with Client(transport) as client:
                result = await client.call_tool(TZ_AI_TOOL_NAME, {
                    "targetAccount": receiver_uid,
                    "content": content
                })

                if result and result.content:
                    text = getattr(result.content[0], "text", None)
                    if text:
                        return True, f"Notification sent successfully via MCP: {text}"

            return False, "MCP call returned empty result"

        except Exception as e:
            return False, f"MCP notification error: {str(e)}"

    def send_notification(self, content, receiver_uid):
        """
        发送WeLink通知（同步封装）

        Args:
            content: 通知内容
            receiver_uid: 接收者UID

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            return asyncio.run(self._send_notification_via_mcp(content, receiver_uid))
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"

    def notify_mr_review_complete(self, mr_title, mr_url, risk_level, author_id, author_name=None, report_path=None, share_url=None):
        """
        发送MR检视完成通知

        Args:
            mr_title: MR标题
            mr_url: MR链接
            risk_level: 风险等级
            author_id: MR提交者工号
            author_name: MR提交者姓名（可选）
            report_path: 报告路径（可选）
            share_url: OneBox分享链接（可选）

        Returns:
            tuple: (success: bool, message: str)
        """
        # 构建通知内容
        risk_emoji_map = {
            "high": "🔴",
            "medium": "🟡",
            "low": "🟢",
        }
        risk_emoji = risk_emoji_map.get(risk_level, "⚪")

        # 构建内容 - 按照用户要求的格式
        content = f"✅ MR 检视完成\n\n🔗 {mr_url}\nMR 标题: {mr_title}"
        
        # 添加作者信息（优先使用author_name，如果包含空格则移除）
        if author_name:
            author_display = author_name.replace(" ", "")
            content += f"\nMR 作者: {author_display}"
        elif author_id:
            content += f"\nMR 作者: {author_id}"
        
        content += f"\n\n⚡ 风险级别: {risk_emoji} {risk_level}"

        if share_url:
            content += f"\n\n📋 报告链接：{share_url}"

        content += f"\n\n💡 Powered By ds-mr-reviewer：https://agent.huawei.com/ai/skills/ds-mr-reviewer"

        print(f"[INFO] Notification content:")
        print(content)

        # 收集所有接收者ID
        receiver_uids = []

        # 添加MR作者（如果存在）
        author_uid = self.construct_receiver_uid(author_id)
        if author_uid:
            receiver_uids.append(author_uid)
            print(f"[INFO] Added MR author to recipients: {author_uid}")

        # 添加配置的自定义通知ID
        welink_notify_ids = self.config.get("welink_notify_ids", "") if self.config else ""
        if welink_notify_ids and isinstance(welink_notify_ids, str):
            # 按逗号分割并去除空白
            notify_ids = [uid.strip() for uid in welink_notify_ids.split(",") if uid.strip()]
            for uid in notify_ids:
                if uid not in receiver_uids:  # 避免重复
                    receiver_uids.append(uid)
                    print(f"[INFO] Added config-defined recipient: {uid}")

        if not receiver_uids:
            return False, "No valid recipients to send notification"

        # 给所有接收者发送通知
        success_count = 0
        total_count = len(receiver_uids)
        error_messages = []

        print(f"[INFO] Total recipients: {total_count}")
        print(f"[INFO] Recipient list: {receiver_uids}")

        for uid in receiver_uids:
            success, message = self.send_notification(content, uid)
            if success:
                success_count += 1
                print(f"[SUCCESS] Notification sent to {uid}")
            else:
                error_messages.append(f"{uid}: {message}")
                print(f"[ERROR] Failed to send to {uid}: {message}")

        # 返回结果
        if success_count == total_count:
            return True, f"Successfully sent to all {total_count} recipients"
        elif success_count > 0:
            return True, f"Sent to {success_count}/{total_count} recipients. Errors: {', '.join(error_messages)}"
        else:
            return False, f"Failed to send to any recipient. Errors: {', '.join(error_messages)}"


def main():
    parser = argparse.ArgumentParser(description="WeLink Notifier for MR Review")
    parser.add_argument("--mrTitle", help="MR标题")
    parser.add_argument("--mrUrl", help="MR链接")
    parser.add_argument("--riskLevel", help="风险等级（高/中/低）")
    parser.add_argument("--authorName", help="作者姓名")
    parser.add_argument("--authorId", help="作者工号")
    parser.add_argument("--reportPath", help="报告路径")
    parser.add_argument("--mrInfo", help="MR信息JSON字符串")
    parser.add_argument("--mrInfoFile", help="MR信息JSON文件路径")
    parser.add_argument("--configPath", help="config.json路径")
    parser.add_argument("--shareUrl", help="OneBox分享链接")

    args = parser.parse_args()

    # 初始化通知器
    notifier = WeLinkNotifier(configPath=args.configPath)
    success, error = notifier.load_config()
    if not success:
        print(f"[ERROR] {error}")
        sys.exit(1)

    # 解析MR信息
    mr_data = {}
    if args.mrInfoFile:
        try:
            with open(args.mrInfoFile, "r", encoding="utf-8") as f:
                mr_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to read mrInfoFile: {e}")
            sys.exit(1)
    elif args.mrInfo:
        try:
            mr_data = json.loads(args.mrInfo)
        except json.JSONDecodeError as e:
            print(f"[ERROR] Invalid mrInfo JSON: {e}")
            sys.exit(1)
    else:
        # 使用命令行参数
        mr_data = {
            "title": args.mrTitle,
            "url": args.mrUrl,
            "author": {
                "name": args.authorName,
                "id": args.authorId
            }
        }

    # 提取信息 - 兼容mr_data直接是MR信息或包含mr_info包装的结构
    mr_info = mr_data.get("mr_info", mr_data)
    mr_title = args.mrTitle or mr_info.get("title", "Unknown MR")
    mr_url = args.mrUrl or mr_info.get("web_url") or mr_data.get("url", "")
    
    # 风险等级标准化处理
    raw_risk_level = args.riskLevel or mr_data.get("risk_level", "low")
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
    risk_level = risk_level_mapping.get(raw_risk_level, raw_risk_level if raw_risk_level in ['high', 'medium', 'low'] else 'low')
    
    report_path = args.reportPath
    share_url = args.shareUrl

    # 提取作者信息
    author = mr_info.get("author", mr_data.get("author", {}))
    author_id = args.authorId or author.get("id")
    author_username = author.get("username") or mr_info.get("author_username")
    # 优先从命令行参数，然后从mr_info顶层，最后从author对象获取name
    author_name = args.authorName or mr_info.get("author_name") or author.get("name")

    # 发送通知，明确使用author_username作为作者工号
    success, message = notifier.notify_mr_review_complete(
        mr_title=mr_title,
        mr_url=mr_url,
        risk_level=risk_level,
        author_id=author_username,
        author_name=author_name,
        report_path=report_path,
        share_url=share_url
    )

    if success:
        print(f"[SUCCESS] {message}")
        sys.exit(0)
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()