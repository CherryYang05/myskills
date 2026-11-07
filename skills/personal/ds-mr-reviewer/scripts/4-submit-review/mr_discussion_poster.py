#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Discussion Poster

此脚本用于读取mr_risks.json，按风险级别过滤后提交带位置的Discussion评论到MR。
与mr_note_poster.py配合使用：Note负责全局评论，Discussion负责带位置的具体问题评论。

Usage:
    python mr_discussion_poster.py --mrInfoFile <coordinator路径> --risksFile <mr_risks.json路径>
    python mr_discussion_poster.py --mrInfoFile <coordinator路径> --risksFile <mr_risks.json路径> --force
"""

import argparse
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

SEVERITY_MAP = {
    "高": "major",
    "中": "minor",
    "低": "suggestion",
}

RISK_EMOJI_MAP = {
    "高": "🔴",
    "中": "🟡",
    "低": "🟢",
}


class MRDiscussionPoster:
    """MR Discussion提交器（仅负责带位置的Discussion评论）"""

    def __init__(self, config_path=None, domain=None, mode="review"):
        self.scripts_dir = Path(__file__).parent
        self.config_path = config_path
        self.domain = domain or "codehub-y.huawei.com"
        self.config = None
        self.token = None
        self.mode = mode

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

    def get_send_discussion_levels(self):
        """从config中获取send_discussion_level配置项"""
        if not self.config:
            return ["高", "中"]
        return self.config.get("send_discussion_level", ["高", "中"])

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

    def get_review_settings(self, project_id):
        """
        获取项目的review设置

        Returns:
            tuple: (settings: dict, error: str)
            settings包含:
                - categories_and_modules_enabled: bool
                - review_modules: str or None (数组第一个元素)
                - review_categories: str or None (加工后的分类字符串)
        """
        token = self.get_token()
        encoded_project = quote(project_id, safe="")
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}/review_settings"
        headers = {"PRIVATE-TOKEN": token}

        try:
            res = requests.get(url, headers=headers, verify=False, timeout=30)
            if res.status_code != http.client.OK:
                return None, f"Failed to fetch review settings: {res.status_code}"

            settings = res.json()

            # 解析 categories_and_modules_enabled
            categories_and_modules_enabled = settings.get("categories_and_modules_enabled", False)

            result = {
                "categories_and_modules_enabled": categories_and_modules_enabled,
                "review_modules": None,
                "review_categories": None,
            }

            # 如果不需要分类和模块，直接返回
            if not categories_and_modules_enabled:
                return result, None

            # 获取 review_modules：取数组第一个元素
            review_modules_list = settings.get("review_modules", [])
            if review_modules_list and len(review_modules_list) > 0:
                result["review_modules"] = review_modules_list[0]

            # 根据 secondary_category_enabled 决定数据源
            secondary_category_enabled = settings.get("secondary_category_enabled", False)

            if secondary_category_enabled:
                # 使用 secondary_categories，加工规则：取第一个分类及其第一个子分类，格式为 "父key:子key"
                secondary_categories = settings.get("secondary_categories")
                if secondary_categories:
                    if isinstance(secondary_categories, list) and len(secondary_categories) > 0:
                        first_category = secondary_categories[0]
                        if isinstance(first_category, dict):
                            parent_key = first_category.get("key", "")
                            sub_categories = first_category.get("sub_categories", [])
                            if sub_categories and len(sub_categories) > 0:
                                first_sub = sub_categories[0]
                                if isinstance(first_sub, dict):
                                    child_key = first_sub.get("key", "")
                                    result["review_categories"] = f"{parent_key}:{child_key}"
            else:
                # 使用 customized_categories，加工规则：取第一个分类的 title:item
                customized_categories = settings.get("customized_categories", [])
                if customized_categories and len(customized_categories) > 0:
                    first_category = customized_categories[0]
                    title = first_category.get("title", "")
                    items = first_category.get("items", [])
                    if items and len(items) > 0:
                        first_item = items[0]
                        result["review_categories"] = f"{title}:{first_item}"
                    elif title:
                        result["review_categories"] = title

            return result, None
        except Exception as e:
            return None, f"Error fetching review settings: {e}"

    def fetch_existing_discussions(self, project_id, mr_iid):
        """
        获取MR中已有的Discussion列表，用于逐条去重（自动分页）

        Args:
            project_id: 项目ID
            mr_iid: MR的IID

        Returns:
            tuple: (existing_set: set, message: str)
            existing_set: 已有Discussion的 (file_path, line_number) 集合
        """
        token = self.get_token()
        if not token:
            return set(), "codehub_token not configured"

        encoded_project = quote(project_id, safe="")
        base_url = f"https://{self.domain}/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}/discussions"
        headers = {"PRIVATE-TOKEN": token}
        existing_set = set()
        page = 1

        try:
            while True:
                res = requests.get(
                    base_url, params={"page": page, "per_page": 100},
                    headers=headers, verify=False, timeout=30
                )
                if res.status_code != http.client.OK:
                    return set(), f"Failed to fetch discussions: {res.status_code}"

                discussions = res.json()
                if not discussions:
                    break

                for discussion in discussions:
                    notes = discussion.get("notes", [])
                    for note in notes:
                        # 从Discussion的position中提取file_path和line_number
                        position = note.get("position") or {}
                        new_path = position.get("new_path", "")
                        new_line = position.get("new_line")
                        if new_path and new_line:
                            existing_set.add((new_path, new_line))

                # 检查是否还有下一页
                next_page = res.headers.get("x-next-page")
                if not next_page:
                    break
                page = int(next_page)

            return existing_set, f"Found {len(existing_set)} existing issue discussions"
        except Exception as e:
            return set(), f"Error fetching existing discussions: {e}"

    def build_discussion_content(self, risk):
        """
        为单个风险构建Discussion内容

        Args:
            risk: 风险信息字典，包含risk_level/file_path/line_number/description/mitigation

        Returns:
            tuple: (content: str, severity: str)
        """
        risk_level = risk.get("risk_level", "低")
        risk_emoji = RISK_EMOJI_MAP.get(risk_level, "🟢")
        file_path = risk.get("file_path", "")
        line_number = risk.get("line_number", "")
        description = risk.get("description", "")
        mitigation = risk.get("mitigation", "")

        content = f"""⚠️ {risk_emoji} {risk_level}风险问题

**问题位置：** {file_path}:{line_number}

**问题描述：** {description}"""

        if mitigation:
            content += f"""

**消减措施：** {mitigation}"""

        severity = SEVERITY_MAP.get(risk_level, "suggestion")

        return content, severity

    def post_issue_discussion(
        self, project_id, mr_iid, file_path, line_number, content, severity="major", review_modules=None, review_categories=None, assignee_id=None, add_to_issue=False, risk=None
    ):
        """
        提交带位置的Discussion到MR

        Args:
            project_id: 项目ID
            mr_iid: MR的IID
            file_path: 文件路径
            line_number: 行号
            content: 评论内容
            severity: 严重程度，可选值：suggestion/minor/major/fatal
            review_modules: 检视模块分类，用于标识问题类型
            assignee_id: 指派给谁（MR的author_id）
            add_to_issue: 是否同时创建关联Issue
            risk: 原始风险数据（add_to_issue=True时用于构建Issue内容）

        Returns:
            tuple: (success: bool, message: str)
        """
        token = self.get_token()
        if not token:
            return False, "codehub_token not configured"

        encoded_project = quote(project_id, safe="")
        url = f"https://{self.domain}/api/v4/projects/{encoded_project}/merge_requests/{mr_iid}/discussions"
        headers = {"PRIVATE-TOKEN": token}
        data = {
            "body": content,
            "position": {"new_path": file_path, "new_line": line_number},
            "severity": severity,
        }
        if review_modules:
            data["review_modules"] = review_modules
        if review_categories:
            data["review_categories"] = review_categories
        if assignee_id:
            data["assignee_id"] = assignee_id

        # Add to Issue：提交Discussion时同时创建关联Issue
        if add_to_issue and risk:
            risk_level = risk.get("risk_level", "低")
            issue_severity_map = {"高": "Fatal", "中": "Major", "低": "Minor"}
            description_text = risk.get("description", "")
            mitigation_text = risk.get("mitigation", "无")
            data["create_relation_issue"] = True
            data["issue_body"] = {
                "title": f"[{risk_level}风险] {description_text[:80]}",
                "description": f"**问题位置：** {file_path}:{line_number}\n\n**问题描述：** {description_text}\n\n**消减措施：** {mitigation_text}",
                "issue_severity": issue_severity_map.get(risk_level, "Minor"),
            }

        try:
            res = requests.post(
                url, headers=headers, json=data, verify=False, timeout=30
            )
            if res.status_code == http.client.CREATED:
                return True, f"Diff discussion posted for {file_path}:{line_number}"
            else:
                return (
                    False,
                    f"Failed to post diff discussion: {res.status_code} - {res.text}",
                )
        except Exception as e:
            return False, f"Error posting diff discussion: {e}"

    def load_risks_file(self, risks_file):
        """
        读取mr_risks.json文件

        Args:
            risks_file: mr_risks.json文件路径

        Returns:
            tuple: (risks: list, error: str)
        """
        if not Path(risks_file).exists():
            return None, f"mr_risks.json文件不存在: {risks_file}"

        try:
            with open(risks_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            risks = data.get("risks", [])
            if not isinstance(risks, list):
                return None, "mr_risks.json格式错误：risks字段不是数组"

            return risks, None
        except json.JSONDecodeError as e:
            return None, f"mr_risks.json JSON解析失败: {e}"
        except Exception as e:
            return None, f"读取mr_risks.json失败: {e}"

    def _report_scenario(self, mr_info, risks, success_count, repo_name):
        """上报表2：AI检视场景数据（仅检视模式）"""
        try:
            from report_usage import report_scenario
        except ImportError:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "common"))
            from report_usage import report_scenario

        # 从web_url提取MR链接，本地模式下web_url为null则用空字符串
        web_url = mr_info.get("web_url") or ""

        # 提取仓库路径：优先从web_url提取namespace/project格式
        # web_url格式: https://codehub.huawei.com/AA_Project/AA-HSW/merge_requests/123
        repository = repo_name  # 默认用目录名解析的值
        if web_url:
            try:
                from urllib.parse import urlparse
                path = urlparse(web_url).path.strip("/")
                # path = "AA_Project/AA-HSW/merge_requests/123"
                parts = path.split("/")
                if len(parts) >= 2 and "merge_requests" in path:
                    idx = parts.index("merge_requests")
                    if idx >= 2:
                        repository = "/".join(parts[:idx])
            except Exception:
                pass

        payload = {
            "scenarioName": "AI_REVIEW",
            "account": os.environ.get("USERNAME", ""),
            "repository": repository,
            "targetBranch": mr_info.get("target_branch", ""),
            "mrLink": web_url,
            "problemCount": len(risks) if risks else 0,
            "reviewCommentCount": success_count,
            "result": "SUCCESS"
        }
        try:
            report_scenario(payload)
            print(f"[INFO] 场景数据上报成功: repository={repository}, problemCount={payload['problemCount']}, reviewCommentCount={success_count}")
        except Exception as e:
            print(f"[WARN] 场景数据上报失败: {e}")

    def run(self, mr_info_file, risks_file, force=False, issue_risk_ids=None):
        """
        执行提交Discussion流程

        Args:
            mr_info_file: mr_coordinator.json文件路径
            risks_file: mr_risks.json文件路径
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

        logger.info("开始 - 提交Discussion评论")
        start_time = datetime.now()

        config, config_error = self.load_config()
        if config_error:
            logger.error(f"失败 - {config_error}")
            return False, config_error

        if not Path(mr_info_file).exists():
            logger.error("失败 - MR信息文件不存在")
            return False, f"MR信息文件不存在: {mr_info_file}"

        # 读取mr_coordinator.json
        with open(mr_info_file, "r", encoding="utf-8") as f:
            mr_data = json.load(f)

        mr_info = mr_data.get("mr_info", mr_data)
        mr_domain = mr_info.get("domain")
        if mr_domain:
            self.domain = mr_domain

        project_id = mr_info.get("project_id")
        mr_iid = mr_info.get("mr_id")

        # 获取author_id作为assignee_id
        assignee_id = None
        try:
            author_id = mr_info.get("author_id")
            if author_id:
                assignee_id = str(author_id)
                print(f"[INFO] 获取MR作者ID: {assignee_id}")
        except Exception as e:
            print(f"[WARN] 获取author_id失败: {e}，将不设置assignee_id")

        if not project_id or not mr_iid:
            print("[WARN] MR信息中缺少project_id，尝试从API获取...")
            project_id = self.fetch_project_id_from_api(mr_data)
            if not project_id:
                logger.error("失败 - 无法获取project_id")
                return False, "MR信息中缺少project_id且无法从API获取"

        if not mr_iid:
            logger.error("失败 - mr_id为空")
            return False, "MR信息中缺少mr_id"

        # 获取send_discussion_level配置
        send_discussion_levels = self.get_send_discussion_levels()

        # 读取mr_risks.json
        print(f"[INFO] 读取mr_risks.json: {risks_file}")
        risks, risks_error = self.load_risks_file(risks_file)
        if risks_error:
            logger.error(f"失败 - {risks_error}")
            return False, risks_error

        # 按风险级别过滤
        filtered_risks = [
            risk
            for risk in risks
            if risk.get("risk_level") in send_discussion_levels
        ]

        if not filtered_risks:
            print(
                f"[INFO] 没有需要提交Discussion的风险（配置等级: {send_discussion_levels}，总风险数: {len(risks) if risks else 0}）"
            )
            logger.info("跳过 - 无符合条件的风险")
            return True, "无符合条件的风险需要提交Discussion"

        # 逐条去重：获取已有Discussion的(file_path, line_number)集合
        existing_set = set()
        if not force:
            print(f"[INFO] 获取MR {mr_iid} 已有的检视Discussion...")
            existing_set, check_msg = self.fetch_existing_discussions(project_id, mr_iid)
            print(f"[INFO] {check_msg}")
        else:
            print("[INFO] 强制提交模式，跳过去重检测")

        # 获取review设置
        review_settings, settings_error = self.get_review_settings(project_id)
        if settings_error:
            logger.error(f"获取review设置失败: {settings_error}")
            return False, f"获取review设置失败: {settings_error}"

        categories_and_modules_enabled = review_settings.get("categories_and_modules_enabled", False)
        review_modules = review_settings.get("review_modules")
        review_categories = review_settings.get("review_categories")

        print(f"[INFO] categories_and_modules_enabled: {categories_and_modules_enabled}")
        if categories_and_modules_enabled:
            print(f"[INFO] review_modules: {review_modules}")
            print(f"[INFO] review_categories: {review_categories}")
        else:
            print("[INFO] 不使用分类和模块")

        # 逐条提交Discussion（跳过与已有Discussion重复的条目）
        print(
            f"[INFO] 共 {len(filtered_risks)} 条风险需要提交Discussion（配置等级: {send_discussion_levels}）..."
        )

        success_count = 0
        fail_count = 0
        skip_count = 0
        issue_count = 0
        if issue_risk_ids is None:
            issue_risk_ids = set()

        for risk_idx, risk in enumerate(filtered_risks, start=1):
            risk_level = risk.get("risk_level", "低")
            file_path = risk.get("file_path", "")
            line_number = risk.get("line_number", 0)

            print(
                f"[INFO] 提交风险: {file_path}:{line_number} (风险等级: {risk_level})"
            )

            content, severity = self.build_discussion_content(risk)

            if not file_path or not line_number:
                print(f"[WARN] 风险ID {risk.get('id')} 缺少file_path或line_number，跳过")
                fail_count += 1
                continue

            # 逐条去重：检查同一文件同一行是否已有Discussion
            if not force and (file_path, line_number) in existing_set:
                print(f"[INFO] 跳过重复: {file_path}:{line_number} 已存在检视意见")
                skip_count += 1
                continue

            add_to_issue = risk_idx in issue_risk_ids
            success, msg = self.post_issue_discussion(
                project_id,
                mr_iid,
                file_path,
                line_number,
                content,
                severity,
                review_modules,
                review_categories,
                assignee_id,
                add_to_issue=add_to_issue,
                risk=risk if add_to_issue else None,
            )

            if success:
                success_count += 1
                if add_to_issue:
                    issue_count += 1
                    print(f"[INFO] 已同时创建关联Issue: {file_path}:{line_number}")
            else:
                fail_count += 1
                print(f"[ERROR] 提交Discussion失败: {msg}")

        print(
            f"[INFO] Discussion提交完成: 成功 {success_count} (其中转Issue {issue_count}), 跳过重复 {skip_count}, 失败 {fail_count}"
        )

        # 场景数据上报（仅检视模式）
        if self.mode == "review":
            self._report_scenario(mr_info, risks, success_count, safe_repo_name)

        duration = (datetime.now() - start_time).total_seconds()
        if success_count > 0:
            logger.info(f"完成 - 成功 {success_count} (其中转Issue {issue_count}), 跳过 {skip_count}, 失败 {fail_count} (耗时: {duration:.2f}秒)")
            return True, f"Discussion提交完成: 成功 {success_count} (其中转Issue {issue_count}), 跳过重复 {skip_count}, 失败 {fail_count}"
        elif skip_count > 0 and fail_count == 0:
            logger.info(f"完成 - 全部重复跳过 {skip_count} (耗时: {duration:.2f}秒)")
            return True, f"所有风险均已存在检视意见，跳过提交: {skip_count} 条"
        else:
            logger.error(f"失败 - 所有Discussion提交失败 (耗时: {duration:.2f}秒)")
            return False, f"所有Discussion提交失败: {fail_count} 条"


def main():
    parser = argparse.ArgumentParser(description='MR Discussion Poster - 提交带位置的Discussion评论到MR')
    parser.add_argument('--mrInfoFile', required=True, help='mr_coordinator.json文件路径')
    parser.add_argument('--risksFile', required=True, help='mr_risks.json文件路径')
    parser.add_argument('--configPath', help='config.json路径')
    parser.add_argument('--force', action='store_true', help='强制提交，跳过重复检测')
    parser.add_argument('--mode', choices=['review', 'fix', 'local'], default='review',
                        help='运行模式：review=检视模式, fix=修复模式, local=本地模式')
    parser.add_argument('--issueRisks', default='',
                        help='需要转Issue的风险序号列表(1-based)，逗号分隔，如: 1,3,5')

    args = parser.parse_args()

    # 解析issueRisks
    issue_risk_ids = set()
    if args.issueRisks:
        issue_risk_ids = {int(x.strip()) for x in args.issueRisks.split(",") if x.strip().isdigit()}

    poster = MRDiscussionPoster(config_path=args.configPath, mode=args.mode)
    success, message = poster.run(
        mr_info_file=args.mrInfoFile,
        risks_file=args.risksFile,
        force=args.force,
        issue_risk_ids=issue_risk_ids
    )

    if success:
        print(f"[SUCCESS] {message}")
        sys.exit(0)
    else:
        print(f"[ERROR] {message}")
        sys.exit(1)


if __name__ == "__main__":
    main()
