#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Fetcher

Usage:
    python mr_fetcher.py --repository_name <repository_name> --mrId <mr_id>

This script fetches MR description and diff files from CodeHub API.
It returns the MR description (with "自检项" section removed) and all diff files.
"""

import argparse
import json
import sys
import re
import os
import http.client
import requests
import urllib3
from pathlib import Path
from urllib.parse import quote

# Suppress InsecureRequestWarning when using verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config_manager import get_config


class MRFetcher:
    """从CodeHub获取MR描述和diff文件"""

    def __init__(self, repository_name, mrId, configPath=None, domain=None):
        self.repository_name = repository_name
        self.mrId = str(mrId)
        # Ensure configPath is a Path object
        self.configPath = Path(configPath) if configPath else self._get_default_config_path()
        self.domain = domain or "codehub-y.huawei.com"
        self.config = None
        self.token = None

    def _get_default_config_path(self):
        """获取默认的config.json路径"""
        # 配置文件放在skill目录下，使用相对路径：从scripts目录回退三级
        return Path(__file__).parent.parent.parent / "config.json"

    def load_config(self):
        """从config.json加载配置"""
        # 如果指定了configPath，使用指定的路径
        if self.configPath and self.configPath != self._get_default_config_path():
            if not self.configPath.exists():
                return None, f"Config file not found at {self.configPath}"

            try:
                with open(self.configPath, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                return self.config, None
            except Exception as e:
                return None, f"Error loading config: {str(e)}"
        else:
            # 否则使用config_manager的自动选择逻辑
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

    def filter_description(self, description):
        """
        过滤描述信息，移除"自检项"之后的内容

        Args:
            description: 原始描述信息

        Returns:
            过滤后的描述信息
        """
        if not description:
            return ""

        # 查找"自检项"的位置
        patterns = [
            r'自检项',
            r'自检清单',
            r'自查事项'
        ]

        for pattern in patterns:
            match = re.search(pattern, description)
            if match:
                # 保留"自检项"之前的内容（不包括"自检项"本身）
                return description[:match.start()].strip()

        return description.strip()

    def should_filter_diff(self, file_path):
        """
        判断diff文件是否应该被过滤

        Args:
            file_path: 文件路径

        Returns:
            True: 应该过滤, False: 不应该过滤
        """
        if not file_path:
            return False

        # 0. 从配置中读取需要排除的文件后缀
        exclude_suffixes = []
        if self.config:
            exclude_suffix_config = self.config.get("exclude_file_suffix", "")
            if exclude_suffix_config:
                exclude_suffixes = [s.strip() for s in exclude_suffix_config.split(",") if s.strip()]

        # 检查配置的后缀
        for suffix in exclude_suffixes:
            if file_path.endswith(suffix):
                return True

        # 3. 文件路径中，包含test目录（需判断目录名完全匹配test）
        # 例如: service/src/test/java -> 包含test目录（过滤）
        # service/src/java/iptest -> 不包含test目录（不过滤）
        path_parts = file_path.split('/') if '/' in file_path else file_path.split('\\')
        if 'test' in path_parts:
            return True

        return False

    def fetch_mr_changes(self):
        """
        从CodeHub API获取MR的描述和diff文件

        Returns:
            dict: {
                "success": bool,
                "mr_id": str,
                "title": str,
                "description": str,  # 已过滤"自检项"之后的内容
                "diffs": list of diff strings,
                "changes_count": int,
                "error": str or None
            }
        """
        # 加载配置
        config, config_error = self.load_config()
        if config_error:
            return {
                "success": False,
                "error": config_error
            }

        # 获取token
        self.token = self.get_token()
        if not self.token or self.token == "YOUR_CODEHUB_TOKEN_HERE":
            return {
                "success": False,
                "error": f"{self.domain}'s token not configured in config.json"
            }

        # 调用CodeHub API - 使用URL-encoded的项目路径方式
        encoded_project = quote(self.repository_name, safe='')
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}/merge_requests/{self.mrId}/changes"
        headers = {"PRIVATE-TOKEN": self.token}

        max_retry = 3
        for i in range(max_retry):
            try:
                res = requests.get(url, headers=headers, verify=False, timeout=30)
                if res.status_code == http.client.OK:
                    result = res.json()
                    return self._parse_response(result)
                elif res.status_code == 429:
                    if i < max_retry - 1:
                        continue
                    return {
                        "success": False,
                        "error": "Request rate limited, please try again later"
                    }
                elif res.status_code == 404:
                    return {
                        "success": False,
                        "error": f"MR {self.mrId} not found in repository {self.repository_name}"
                    }
                elif res.status_code == 401 or res.status_code == 403:
                    return {
                        "success": False,
                        "error": "Authentication failed. Please check your token in config.json"
                    }
                elif res.status_code == 500:
                    if i < max_retry - 1:
                        continue
                    return {
                        "success": False,
                        "error": f"Server error when fetching MR {self.mrId}"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Request failed with status code: {res.status_code}"
                    }
            except requests.exceptions.Timeout:
                if i < max_retry - 1:
                    continue
                return {
                    "success": False,
                    "error": "Request timeout"
                }
            except Exception as e:
                if i < max_retry - 1:
                    continue
                return {
                    "success": False,
                    "error": f"Error fetching MR: {str(e)}"
                }

        return {
            "success": False,
            "error": "Failed to fetch MR changes after retries"
        }

    def _parse_response(self, data):
        """
        解析API响应数据

        Returns:
            dict: 包含MR描述和diff文件的字典
        """
        # 原始描述
        raw_description = data.get("description", "")

        # 过滤描述，移除"自检项"之后的内容
        filtered_description = self.filter_description(raw_description)

        # 提取所有的diff，并过滤不需要的文件
        diffs = []
        changes = data.get("changes", [])

        for change in changes:
            old_path = change.get("old_path")
            new_path = change.get("new_path")
            diff_content = change.get("diff")
            
            if diff_content:
                # 检查文件是否应该被过滤
                if self.should_filter_diff(old_path) or self.should_filter_diff(new_path):
                    continue

                diffs.append({
                    "old_path": old_path,
                    "new_path": new_path,
                    "new_file": change.get("new_file", False),
                    "renamed_file": change.get("renamed_file", False),
                    "deleted_file": change.get("deleted_file", False),
                    "diff": diff_content
                })

        author_info = data.get("author", {})
        author_name = author_info.get("name") if author_info else None
        author_id = author_info.get("id") if author_info else None
        author_username = author_info.get("username") if author_info else None

        # author 字段保持为字典格式，便于后续处理（如 Welink 通知）
        author_dict = {
            "name": author_name,
            "id": str(author_id) if author_id else None,
            "username": author_username
        }

        return {
            "success": True,
            "mr_id": str(data.get("iid", self.mrId)),
            "project_id": str(data.get("project_id", "")),
            "title": data.get("title", ""),
            "description": filtered_description,
            "diffs": diffs,
            "changes_count": len(changes),
            "author_name": author_name,
            "author_id": str(author_id) if author_id else None,
            "author_username": author_username,
            "author": author_dict,
            "source_branch": data.get("source_branch", ""),
            "target_branch": data.get("target_branch", ""),
            "web_url": data.get("web_url", ""),
            "error": None
        }

    def fetch_project_info(self):
        """
        从CodeHub API获取项目信息（包含ssh_url）

        Returns:
            dict: {
                "success": bool,
                "ssh_url_to_repo": str,
                "http_url_to_repo": str,
                "error": str or None
            }
        """
        config, config_error = self.load_config()
        if config_error:
            return {
                "success": False,
                "error": config_error
            }

        self.token = self.get_token()
        if not self.token or self.token == "YOUR_CODEHUB_TOKEN_HERE":
            return {
                "success": False,
                "error": f"{self.domain}'s token not configured in config.json"
            }

        encoded_project = quote(self.repository_name, safe='')
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}"
        headers = {"PRIVATE-TOKEN": self.token}

        max_retry = 3
        for i in range(max_retry):
            try:
                res = requests.get(url, headers=headers, verify=False, timeout=30)
                if res.status_code == http.client.OK:
                    result = res.json()
                    return {
                        "success": True,
                        "ssh_url_to_repo": result.get("ssh_url_to_repo", ""),
                        "http_url_to_repo": result.get("http_url_to_repo", ""),
                        "error": None
                    }
                elif res.status_code == 404:
                    return {
                        "success": False,
                        "error": f"Project {self.repository_name} not found"
                    }
                elif res.status_code == 401 or res.status_code == 403:
                    return {
                        "success": False,
                        "error": "Authentication failed"
                    }
                else:
                    if i < max_retry - 1:
                        continue
                    return {
                        "success": False,
                        "error": f"Request failed with status code: {res.status_code}"
                    }
            except Exception as e:
                if i < max_retry - 1:
                    continue
                return {
                    "success": False,
                    "error": f"Error fetching project info: {str(e)}"
                }

        return {
            "success": False,
            "error": "Failed to fetch project info after retries"
        }

    def to_json(self):
        """将结果转换为JSON字符串"""
        return json.dumps(self.fetch_mr_changes(), ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='MR Fetcher - Fetch MR description and diffs from CodeHub')
    parser.add_argument('--repository_name', required=True, help='Repository name (e.g., TxL0L1ServiceV3)')
    parser.add_argument('--mrId', required=True, help='MR ID (e.g., 15217)')
    parser.add_argument('--configPath', help='Path to config.json (default: ../../config.json)')
    parser.add_argument('--format', choices=['human', 'json'], default='human', help='Output format: human (readable) or json (for AI processing)')
    parser.add_argument('--outputFile', help='Output file path to save MR info as JSON (for downstream processing like WeLink notification)')

    args = parser.parse_args()

    fetcher = MRFetcher(args.repository_name, args.mrId, args.configPath)
    result = fetcher.fetch_mr_changes()

    if result["success"]:
        # 如果没指定outputFile，使用默认文件名 ~/.mr-reviewer/temp/mr_info_{repository_name}_{mr_id}.json 避免并发冲突
        if not args.outputFile:
            temp_dir = Path.home() / ".mr-reviewer" / "temp"
            args.outputFile = str(temp_dir / f"mr_info_{args.repository_name}_{args.mrId}.json")
        
        # 保存到文件
        try:
            output_path = Path(args.outputFile)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"[INFO] MR信息已保存到: {output_path}")
        except Exception as e:
            print(f"[ERROR] 保存文件失败: {e}")
            sys.exit(1)

# 打印结果
        if args.format == 'json':
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif args.format == 'human':
            print(f"MR作者信息：{result.get('author', '')}")
            print(f"MR标题信息：{result.get('title', '')}")
            print(f"MR描述信息：{result.get('description', '')}")
            print(f"MR diff文件信息：")
            for diff in result.get('diffs', []):
                file_path = diff.get('new_path') or diff.get('old_path')
                print(f"  文件路径：{file_path}")
                print(f"  Diff内容：\n{diff.get('diff', '')}\n")
            print(f"MR的目标分支信息：{result.get('target_branch', '')}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

    # 如果失败，返回非零退出码
    if not result["success"]:
        sys.exit(1)


if __name__ == '__main__':
    main()