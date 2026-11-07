#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Note Poster

此脚本用于在MR检视完成后，提交Note全局评论（检视完成通知）。
从mr_coordinator.json获取project_id、mr_id、risk_level、report_share_url。

Usage:
    python mr_note_poster.py --repo "{repo}" --mrId {mrId}
"""

import argparse
import asyncio
import json
import sys
import os
import http.client
import requests
import urllib3
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
from config_manager import get_config
from logger_manager import get_logger
from mcp_client_utils import (
    get_auth_token,
    build_mcp_headers,
    create_mcp_client,
    call_mcp_tool,
    CODEDETECTION_MCP_URL,
)

MARKER = "MR AI代码检视已完成"


TYPE_PREFIX_MAP = {
    'coordinator': 'mr_coordinator',
    'analysis_stage0': 'analysis_stage0',
    'analysis_stage1': 'analysis_stage1',
    'analysis_stage2': 'analysis_stage2',
    'mr_risks': 'mr_risks',
}


def get_temp_file_path(file_type, repo, mr_id):
    """计算临时文件路径"""
    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = repo.replace('/', '_')
    prefix = TYPE_PREFIX_MAP.get(file_type, file_type)
    mr_subdir = temp_dir / f"mr_{safe_repo_name}_{mr_id}"
    mr_subdir.mkdir(parents=True, exist_ok=True)
    return mr_subdir / f"{prefix}.json"


class MRNotePoster:
    """MR Note全局评论提交器"""

    def __init__(self, config_path=None, domain=None):
        self.scripts_dir = Path(__file__).parent
        self.config_path = config_path
        self.domain = domain or "codehub-y.huawei.com"
        self.config = None
        self.token = None

    def load_config(self):
        """从config.json加载配置"""
        if self.config_path:
            if isinstance(self.config_path, str):
                self.config_path = Path(self.config_path)

            if not self.config_path.exists():
                return None, f"Config file not found at {self.config_path}"

            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                return self.config, None
            except Exception as e:
                return None, f"Error loading config: {str(e)}"
        else:
            self.config = get_config()
            if not self.config:
                return None, "No config found"
            return self.config, None

    def get_token(self):
        """从config中获取token"""
        if not self.config:
            return None
        if self.config.get("codehub_tokens"):
            token = self.config.get("codehub_tokens").get(self.domain)
            if token:
                return token
        return self.config.get("codehub_token")

    def fetch_project_id_from_api(self, mr_data):
        """从API获取project_id"""
        web_url = mr_data.get("mr_info", {}).get("web_url", "")
        if not web_url:
            print("[ERROR] web_url为空")
            return None

        import re

        if web_url.startswith("http"):
            web_url = web_url.split("://")[1]

        if web_url.startswith(f"{self.domain}/"):
            web_url = web_url[len(f"{self.domain}/"):]

        pattern = r"([^/]+(?:/[^/]+)+?)/merge_requests/(\d+)"
        match = re.search(pattern, web_url)

        if not match:
            print(f"[ERROR] 解析web_url失败: {web_url}")
            return None

        repo_path = match.group(1)
        mr_iid = match.group(2)

        token = self.get_token()
        if not token:
            print("[ERROR] Token不存在")
            return None

        encoded_project = quote(repo_path, safe="")
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}"
        headers = {"PRIVATE-TOKEN": token}

        try:
            res = requests.get(url, headers=headers, verify=False, timeout=30)
            if res.status_code == http.client.OK:
                project_info = res.json()
                project_id = str(project_info.get("id"))
                print(f"[SUCCESS] 获取Project ID: {project_id}")
                return project_id
            else:
                print(f"[ERROR] Project API失败: {res.status_code} - {res.text}")
                return None
        except Exception as e:
            print(f"[ERROR] 获取project_id异常: {e}")
            return None

    def check_existing_review(self, project_id, mr_iid):
        """
        检查是否已存在检视报告Note（使用notes接口检查全局评论）

        Args:
            project_id: 项目ID
            mr_iid: MR的IID

        Returns:
            tuple: (exists: bool, message: str)
        """
        token = self.get_token()
        if not token:
            return False, "codehub_token not configured"

        encoded_project = quote(project_id, safe="")
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}/notes"
        headers = {"PRIVATE-TOKEN": token}

        try:
            res = requests.get(url, headers=headers, verify=False, timeout=30)
            if res.status_code != http.client.OK:
                return False, f"Failed to fetch notes: {res.status_code}"

            notes = res.json()
            for note in notes:
                body = note.get("body", "")
                if MARKER in body:
                    return True, f"Found existing review note: {note.get('id')}"

            return False, "No existing review note found"
        except Exception as e:
            return False, f"Error checking existing review: {e}"

    def build_note_content(self, mr_data, share_url=None):
        """
        构建Note全局评论内容

        Args:
            mr_data: mr_coordinator.json数据
            share_url: OneBox分享链接（可选）

        Returns:
            str: 构建好的评论内容
        """
        mr_info = mr_data.get("mr_info", mr_data)
        title = mr_info.get("title", "未知")
        web_url = mr_info.get("web_url", "")
        risk_level = mr_data.get("risk_level", "")

        risk_emoji_map = {"高": "🔴", "中": "🟡", "低": "🟢", "high": "🔴", "medium": "🟡", "low": "🟢"}
        risk_emoji = risk_emoji_map.get(risk_level, "⚪")
        risk_display = risk_level if risk_level else "unknown"

        content = f"""✅ {MARKER}（由 ds-mr-reviewer skill 自动执行)

🔗 {web_url}
MR标题：{title}

⚡ 风险等级：{risk_emoji} {risk_display}"""

        if share_url:
            content += f"""

📋 报告链接：{share_url}"""

        content += f"""

📝 可在代码仓根目录 mr_reviewer_tips.md 或 .codespec/review/codecheck.md 自定义 CodeCheck 规则

💡 Powered By ds-mr-reviewer：https://agent.huawei.com/ai/skills/ds-mr-reviewer"""

        return content

    def post_note(self, project_id, mr_iid, content):
        """
        提交Note全局评论到MR

        Args:
            project_id: 项目ID
            mr_iid: MR的IID
            content: 评论内容

        Returns:
            tuple: (success: bool, message: str)
        """
        token = self.get_token()
        if not token:
            return False, "codehub_token not configured"

        encoded_project = quote(project_id, safe="")
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}/notes"
        headers = {"PRIVATE-TOKEN": token}
        data = {"body": content}

        try:
            res = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
            if res.status_code == http.client.CREATED:
                return True, "Note posted successfully"
            else:
                return False, f"Failed to post note: {res.status_code} - {res.text}"
        except Exception as e:
            return False, f"Error posting note: {e}"

    async def delete_force_review_note_async(self, mr_url):
        """调用 codedetection-mcp-server 删除强制检视评论"""
        try:
            token = get_auth_token()
            headers = build_mcp_headers(token)
            client = create_mcp_client(CODEDETECTION_MCP_URL, headers)

            async with client:
                result = await call_mcp_tool(
                    client,
                    "delete_ai_review_note",
                    {"mrUrl": mr_url}
                )

            if not result or not isinstance(result, dict):
                return False, f"MCP 调用返回格式异常: {result}"

            success = result.get("success")
            msg = result.get("msg", "无消息提示")

            if success is True:
                return True, f"成功 ({msg})"
            else:
                return False, f"失败 ({msg})"

        except Exception as e:
            return False, f"MCP 调用异常: {e}"

    def delete_force_review_note(self, mr_url):
        """
        同步版本的删除强制检视评论

        Args:
            mr_url: MR 链接

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            return asyncio.run(self.delete_force_review_note_async(mr_url))
        except Exception as e:
            return False, f"删除强制检视评论异常: {e}"

    def run(self, mr_info_file, share_url=None, force=False):
        """
        执行提交Note全局评论流程

        Args:
            mr_info_file: mr_coordinator.json文件路径
            share_url: OneBox分享链接（可选）
            force: 是否强制提交（跳过重复检测）

        Returns:
            tuple: (success: bool, message: str)
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

        logger = get_logger(f"{safe_repo_name}_{mr_id}")

        logger.info("开始 - 提交Note评论")
        start_time = datetime.now()

        config, config_error = self.load_config()
        if config_error:
            logger.error(f"失败 - {config_error}")
            return False, config_error

        if not Path(mr_info_file).exists():
            return False, f"MR信息文件不存在: {mr_info_file}"

        with open(mr_info_file, "r", encoding="utf-8") as f:
            mr_data = json.load(f)

        mr_info = mr_data.get("mr_info", mr_data)
        mr_domain = mr_info.get("domain")
        if mr_domain:
            self.domain = mr_domain

        project_id = mr_info.get("project_id")
        mr_iid = mr_info.get("mr_id")

        if not project_id or not mr_iid:
            print("[WARN] MR信息中缺少project_id，尝试从API获取...")
            project_id = self.fetch_project_id_from_api(mr_data)
            if not project_id:
                return False, "MR信息中缺少project_id且无法从API获取"

        if not mr_iid:
            return False, "MR信息中缺少mr_id"

        # 重复检测
        if not force:
            print(f"[INFO] 检查MR {mr_iid} 是否已存在检视报告Note...")
            exists, check_msg = self.check_existing_review(project_id, mr_iid)
            print(f"[INFO] {check_msg}")

            if exists:
                logger.info("跳过 - 已存在检视报告Note")
                return True, "已存在检视报告Note，跳过提交"
        else:
            print("[INFO] 强制提交模式，跳过重复检测")

        # 使用coordinator中的share_url，如果未通过参数传入
        if not share_url:
            share_url = mr_data.get("report_share_url")

        # 构建Note内容
        print("[INFO] 构建Note内容...")
        content = self.build_note_content(mr_data, share_url=share_url)

        # 提交Note
        print("[INFO] 提交Note到MR...")
        success, post_msg = self.post_note(project_id, mr_iid, content)

        duration = (datetime.now() - start_time).total_seconds()
        if success:
            # 删除强制检视评论
            mr_web_url = mr_info.get("web_url", "")
            if mr_web_url:
                logger.info("准备调用 MCP 服务删除强制检视评论...")
                del_success, del_msg = self.delete_force_review_note(mr_web_url)
                if del_success:
                    logger.info(f"删除强制评论成功: {del_msg}")
                else:
                    logger.warning(f"删除强制评论失败 (不影响主流程): {del_msg}")

            logger.info(f"完成 - (耗时: {duration:.2f}秒)")
        else:
            logger.error(f"失败 - {post_msg} (耗时: {duration:.2f}秒)")

        return success, post_msg


def main():
    parser = argparse.ArgumentParser(description='MR Note Poster - 提交检视完成Note全局评论到MR')
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--mrId', required=True, help='MR ID')
    parser.add_argument('--configPath', help='config.json路径')

    args = parser.parse_args()

    mr_info_file = str(get_temp_file_path('coordinator', args.repo, args.mrId))
    print(f"[INFO] 自动计算coordinator路径: {mr_info_file}")

    poster = MRNotePoster(config_path=args.configPath)
    success, message = poster.run(
        mr_info_file=mr_info_file,
        share_url=None,
        force=False
    )

    if success:
        print(f"[SUCCESS] {message}")
        sys.exit(0)
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
