#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Coordinator

Usage:
    python mr_coordinator.py --mrUrl "<MR_URL>" [--outputFile <path>] [--format json|human] [--debug]

This script coordinates the data preparation steps for MR review:
1. Parse MR URL to extract repository name and MR ID
2. Fetch MR info (description, diffs, author) from CodeHub API
3. Prepare local repository (clone/pull)
4. Load review rules (language, repository, repo-root)

Output: Unified JSON file for AI analysis.
"""

import argparse
import json
import sys
import os
import re
import subprocess
import time
import yaml
from pathlib import Path
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))

import importlib.util
from logger_manager import get_logger

scripts_dir = os.path.dirname(__file__)

def load_module(name, file):
    file_path = os.path.join(scripts_dir, file)
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

mr_parse = load_module('mr_parse', 'mr_parse.py')
mr_fetcher = load_module('mr_fetcher', 'mr_fetcher.py')
mr_repo_manager = load_module('mr_repo_manager', 'mr_repo_manager.py')
mr_rules_loader = load_module('mr_rules_loader', 'mr_rules_loader.py')

MRUrlParser = mr_parse.MRUrlParser
MRFetcher = mr_fetcher.MRFetcher
MRRepoManager = mr_repo_manager.MRRepoManager
MRRulesLoader = mr_rules_loader.MRRulesLoader


class MRCoordinator:
    def __init__(self, mr_url, output_file=None, debug=False):
        self.mr_url = mr_url
        self.output_file = output_file
        self.debug = debug
        self.skill_dir = Path(__file__).parent.parent.parent
        # Use user home directory for temp files
        self.temp_dir = Path.home() / ".mr-reviewer" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.result = None

    def _get_default_output_file(self, repo_name, mr_id):
        safe_repo_name = repo_name.replace('/', '_')
        return self.temp_dir / f"mr_coordinator_{safe_repo_name}_{mr_id}.json"

    def step1_parse_mr(self):
        """Step 1: Parse MR URL"""
        print("[INFO] Step 1/4: 解析MR链接...")
        parser = MRUrlParser(self.mr_url)
        if not parser.parse():
            return None, f"无法解析MR URL: {self.mr_url}"
        result = parser.to_dict()
        print(f"[INFO]   仓库: {result['repository_name']}, MR ID: {result['mr_id']}")
        return result, None

    def step2_fetch_mr_info(self, repo_info):
        """Step 2: Fetch MR info from CodeHub API"""
        print("[INFO] Step 2/4: 获取MR信息...")
        repo_name = repo_info['repository_name']
        mr_id = repo_info['mr_id']
        domain = repo_info.get('domain', 'codehub-y.huawei.com')

        # 使用config_manager自动选择配置路径
        fetcher = MRFetcher(repo_name, mr_id, None, domain)
        result = fetcher.fetch_mr_changes()
        if not result['success']:
            return None, result.get('error', '未知错误')
        
        # 获取项目SSH URL
        project_info = fetcher.fetch_project_info()
        if project_info['success']:
            result['ssh_url_to_repo'] = project_info.get('ssh_url_to_repo', '')
            result['http_url_to_repo'] = project_info.get('http_url_to_repo', '')
        
        result['domain'] = domain
        print(f"[INFO]   标题: {result['title']}")
        print(f"[INFO]   作者: {result.get('author_name', 'unknown')}")
        print(f"[INFO]   Diff文件数: {len(result.get('diffs', []))}")
        print(f"[INFO]   目标分支: {result.get('target_branch', 'unknown')}")
        return result, None

    def step3_prepare_repo(self, repo_name, target_branch, domain=None, ssh_url=None, http_url=None):
        """Step 3: Prepare local repository"""
        print("[INFO] Step 3/4: 准备代码仓...")

        # 使用config_manager自动选择配置路径
        manager = MRRepoManager(repo_name, target_branch, None, None, domain, ssh_url, http_url)
        result = manager.prepare_repository()
        if not result['success']:
            return None, result.get('error', '准备代码仓失败')
        print(f"[INFO]   仓库路径: {result['repo_path']}")
        return result, None

    def step3_5_clone_depend_repos(self, repo_path, repo_name, target_branch):
        """
        Step 3.5: 克隆 depend_repo 依赖仓用于代码搜索
        """
        print("[INFO] Step 3.5: 克隆 depend_repo 依赖仓...")

        # 读取 MR 仓的检视规则文件 (mr_reviewer_rules.md 或 mr_reviewer_tips.md)
        rules_file = Path(repo_path) / "mr_reviewer_rules.md"
        tips_file = Path(repo_path) / "mr_reviewer_tips.md"
        depend_repos = []

        target_file = rules_file if rules_file.exists() else tips_file
        if target_file.exists():
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # 解析 depend_repo 元数据
                frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
                match = re.match(frontmatter_pattern, content, re.DOTALL)
                if match:
                    metadata = yaml.safe_load(match.group(1))
                    depend_repo_str = metadata.get('depend_repo', '')
                    if depend_repo_str:
                        depend_repos = [r.strip() for r in depend_repo_str.split(',') if r.strip()]
            except Exception as e:
                print(f"[WARN] 读取检视规则文件失败: {e}")

        if not depend_repos:
            print("[INFO]   未检测到 depend_repo 配置")
            return {}

        # 调用 clone_linked_repos 克隆依赖仓
        repo_manager = MRRepoManager(repo_name, target_branch)
        depend_repo_paths = repo_manager.clone_linked_repos(depend_repos, target_branch)

        print(f"[INFO]   depend_repo 克隆完成: {list(depend_repo_paths.keys())}")
        return depend_repo_paths

    def step4_load_rules(self, repo_path, repo_name, modified_files, target_branch):
        """Step 4: Load review rules"""
        print("[INFO] Step 4/4: 加载检视规则...")
        repo_manager = mr_repo_manager.MRRepoManager(repo_name, target_branch)
        loader = MRRulesLoader(repo_path, self.skill_dir, repo_manager)
        result = loader.load_all_rules(repo_name, modified_files, target_branch)
        rule_ids = result.get('rule_ids', [])
        print(f"[INFO]   规则数量: {len(rule_ids)} 个")
        return result, None

    def _cleanup_temp_files(self, repo_name, mr_id):
        """Clean up intermediate temp files"""
        temp_mr_info = self.temp_dir / f"mr_info_{repo_name}_{mr_id}.json"
        if temp_mr_info.exists():
            try:
                os.remove(temp_mr_info)
                print(f"[INFO] 已清理临时文件: {temp_mr_info.name}")
            except Exception as e:
                print(f"[WARN] 清理临时文件失败: {e}")

    def _write_output_file(self, repo_name, mr_id, output):
        """Write output file directly (avoiding subprocess command length limit on Windows)"""
        safe_repo_name = repo_name.replace('/', '_')
        mr_subdir = self.temp_dir / f"mr_{safe_repo_name}_{mr_id}"
        mr_subdir.mkdir(parents=True, exist_ok=True)
        output_path = mr_subdir / "mr_coordinator.json"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            print(f"[SUCCESS] 输出文件: {output_path}")
            return output_path
        except Exception as e:
            print(f"[ERROR] 保存输出文件失败: {e}")
            return None

    def run(self):
        """Execute all coordination steps"""
        start_time = time.time()
        
        safe_repo_name = "unknown"
        mr_id = "unknown"
        try:
            parser = MRUrlParser(self.mr_url)
            if parser.parse():
                safe_repo_name = parser.repository_name.replace('/', '_')
                mr_id = parser.mr_id
        except:
            pass
        
        mr_info = f"{safe_repo_name}_{mr_id}"
        logger = get_logger(mr_info)
        
        logger.info(f"开始 - MR URL: {self.mr_url}")
        
        print("=" * 50)
        print("MR Review Coordinator")
        print(f"MR URL: {self.mr_url}")
        print("=" * 50)

        step1_start = time.time()
        step1_result, step1_error = self.step1_parse_mr()
        step1_duration = time.time() - step1_start
        logger.info(f"解析MR链接 - 完成 (耗时: {step1_duration:.2f}秒)")
        
        if step1_error:
            logger.error(f"失败 - {step1_error}")
            print(f"[ERROR] Step 1失败: {step1_error}")
            return {"success": False, "error": step1_error}

        repo_name = step1_result['repository_name']
        mr_id = step1_result['mr_id']
        safe_repo_name = repo_name.replace('/', '_')
        mr_info = f"{safe_repo_name}_{mr_id}"
        logger = get_logger(mr_info)
        print("[INFO] Step 1/4: 解析MR链接 - 完成\n")

        logger.info(f"开始 - 获取MR信息")
        step2_start = time.time()
        step2_result, step2_error = self.step2_fetch_mr_info(step1_result)
        step2_duration = time.time() - step2_start
        logger.info(f"获取MR信息 - 完成 (耗时: {step2_duration:.2f}秒)")
        
        if step2_error:
            logger.error(f"失败 - {step2_error}")
            print(f"[ERROR] Step 2失败: {step2_error}")
            return {"success": False, "error": step2_error}

        target_branch = step2_result.get('target_branch')
        if not target_branch:
            print("[ERROR] 未获取到目标分支")
            return {"success": False, "error": "未获取到目标分支"}
        print("[INFO] Step 2/4: 获取MR信息 - 完成\n")

        domain = step1_result.get('domain', 'codehub-y.huawei.com')
        ssh_url = step2_result.get('ssh_url_to_repo')
        http_url = step2_result.get('http_url_to_repo')
        
        logger.info(f"开始 - 准备代码仓")
        step3_start = time.time()
        step3_result, step3_error = self.step3_prepare_repo(repo_name, target_branch, domain, ssh_url, http_url)
        step3_duration = time.time() - step3_start
        logger.info(f"准备代码仓 - 完成 (耗时: {step3_duration:.2f}秒)")
        
        if step3_error:
            logger.error(f"失败 - {step3_error}")
            print(f"[ERROR] Step 3失败: {step3_error}")
            return {"success": False, "error": step3_error}

        repo_path = step3_result['repo_path']
        print("[INFO] Step 3/4: 准备代码仓 - 完成\n")

        depend_repo_paths = self.step3_5_clone_depend_repos(repo_path, repo_name, target_branch)

        modified_files = [diff.get('new_path') for diff in step2_result.get('diffs', []) if diff.get('new_path')]
        
        logger.info(f"开始 - 加载检视规则")
        step4_start = time.time()
        step4_result, step4_error = self.step4_load_rules(repo_path, repo_name, modified_files, target_branch)
        step4_duration = time.time() - step4_start
        logger.info(f"加载检视规则 - 完成 (耗时: {step4_duration:.2f}秒)")
        
        if step4_error:
            logger.error(f"失败 - {step4_error}")
            print(f"[ERROR] Step 4失败: {step4_error}")
            return {"success": False, "error": step4_error}
        print("[INFO] Step 4/4: 加载检视规则 - 完成\n")

        if not self.debug:
            self._cleanup_temp_files(repo_name, mr_id)

        domain = step1_result.get('domain', 'codehub-y.huawei.com')
        full_repo_name = step1_result.get('mr_url', '').split('/merge_requests/')[0].split(f'/{domain}/')[-1] if 'codehub' in step1_result.get('mr_url', '') else repo_name

        output = {
            "mr_info": {
                "mr_id": step2_result.get('mr_id'),
                "project_id": step2_result.get('project_id'),
                "title": step2_result.get('title'),
                "description": step2_result.get('description'),
                "author": step2_result.get('author'),
                "author_name": step2_result.get('author_name'),
                "author_id": step2_result.get('author_id'),
                "author_username": step2_result.get('author_username'),
                "source_branch": step2_result.get('source_branch'),
                "target_branch": target_branch,
                "web_url": step2_result.get('web_url'),
                "domain": step2_result.get('domain')
            },
            "diffs": step2_result.get('diffs', []),
            "modified_files": modified_files,
            "repository": {
                "name": repo_name,
                "full_name": full_repo_name,
                "local_path": repo_path,
                "depend_repos": depend_repo_paths
            },
            "mr_related_repo_path": [repo_path] + list(depend_repo_paths.values()),
            "rules": step4_result,
            "report_share_url": "",
            "risk_level": ""
        }

        output_file = self.output_file or self._get_default_output_file(repo_name, mr_id)
        result_file = self._write_output_file(repo_name, mr_id, output)
        if not result_file:
            logger.error(f"保存输出文件失败")
            return {"success": False, "error": "保存输出文件失败"}
        
        total_duration = time.time() - start_time
        logger.info(f"完成 - 总耗时: {total_duration:.2f}秒, 输出文件: {result_file}")
        
        print(f"[SUCCESS] 输出文件: {result_file}")

        print("\n" + "=" * 50)
        print("MR Review Coordinator 完成！")
        print("=" * 50)
        return {"success": True, "output_file": str(output_file)}


def main():
    parser = argparse.ArgumentParser(description='MR Coordinator - 自动完成MR检视数据准备步骤')
    parser.add_argument('--mrUrl', required=True, help='MR URL (CodeHub/GitLab/GitHub)')
    parser.add_argument('--outputFile', help='输出JSON文件路径')
    parser.add_argument('--format', choices=['json', 'human'], default='json', help='输出格式')
    parser.add_argument('--debug', action='store_true', help='调试模式，不清理临时文件')

    args = parser.parse_args()

    coordinator = MRCoordinator(args.mrUrl, args.outputFile, args.debug)
    result = coordinator.run()

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get('success'):
        sys.exit(1)


if __name__ == '__main__':
    main()