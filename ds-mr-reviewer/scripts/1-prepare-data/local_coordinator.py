#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local Coordinator

Usage:
    # 分支模式（原有）
    python local_coordinator.py --repoPath "<仓库路径>" --branch "<目标分支>" [--repoName <名称>] [--outputFile <path>] [--format json|human] [--debug]

    # Commit模式（单个commit的变更）
    python local_coordinator.py --repoPath "<仓库路径>" --commit "<commit_hash>" [--branch "<目标分支>"] [--repoName <名称>] [--outputFile <path>] [--format json|human] [--debug]

    # Commit区间模式（两个commit之间的累积变更）
    python local_coordinator.py --repoPath "<仓库路径>" --baseCommit "<原commit>" --headCommit "<后commit>" [--repoName <名称>] [--outputFile <path>] [--format json|human] [--debug]

This script coordinates the data preparation steps for local code review:
1. Get local git diff (committed + uncommitted changes / or specific commit diff / or commit range diff)
2. Prepare local repository info
3. Load review rules (language, repository, repo-root)

Output: Unified JSON file for AI analysis (same format as mr_coordinator.py).
"""

import argparse
import json
import sys
import os
import re
import subprocess
import time
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


mr_repo_manager = load_module('mr_repo_manager', 'mr_repo_manager.py')
mr_rules_loader = load_module('mr_rules_loader', 'mr_rules_loader.py')

MRRepoManager = mr_repo_manager.MRRepoManager
MRRulesLoader = mr_rules_loader.MRRulesLoader


class LocalCoordinator:
    def __init__(self, repo_path, branch=None, commit=None, base_commit=None, head_commit=None, repo_name=None, output_file=None, debug=False):
        self.repo_path = Path(repo_path).resolve()
        self.branch = branch
        self.commit = commit
        self.base_commit = base_commit
        self.head_commit = head_commit
        self.is_range_mode = bool(self.base_commit and self.head_commit)
        self.repo_name = repo_name or self.repo_path.name
        self.output_file = output_file
        self.debug = debug
        self.skill_dir = Path(__file__).parent.parent.parent
        self.temp_dir = Path.home() / ".mr-reviewer" / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        # 确定 mrId：区间模式使用 base+head 短 hash，commit 模式使用 commit 短 hash，分支模式使用 "local"
        if self.is_range_mode:
            base_short = self._get_commit_short_hash(self.base_commit)
            head_short = self._get_commit_short_hash(self.head_commit)
            self.mr_id = f"{base_short}_{head_short}"
        elif self.commit:
            self.mr_id = self._get_commit_short_hash()
        else:
            self.mr_id = "local"

    def _get_commit_short_hash(self, commit=None):
        """获取 commit 的短 hash（前7位）作为 mrId"""
        target = commit or self.commit
        result = self._run_git_command(["rev-parse", "--short=7", target])
        if result and result.strip():
            return result.strip()
        return target[:7] if len(target) >= 7 else target

    def _get_default_output_file(self, repo_name):
        safe_repo_name = repo_name.replace('/', '_')
        return self.temp_dir / f"mr_coordinator_{safe_repo_name}_{self.mr_id}.json"

    def _run_git_command(self, args, cwd=None):
        """Run a git command and return stdout"""
        workdir = cwd or str(self.repo_path)
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=workdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60
            )
            if result.returncode != 0:
                print(f"[WARN] git command failed: git {' '.join(args)}")
                print(f"[WARN] stderr: {result.stderr.strip()}")
                return None
            return result.stdout
        except subprocess.TimeoutExpired:
            print("[WARN] git command timed out")
            return None
        except Exception as e:
            print(f"[WARN] git command error: {e}")
            return None

    def _ensure_target_branch(self):
        """Ensure target branch is available for diff. Returns the ref to use for diff.

        Priority:
        1. Local branch {branch} if it exists
        2. Remote tracking branch origin/{branch} (fetch if needed)
        3. Fallback to current HEAD (warn user)
        """
        # Check if local branch exists
        result = self._run_git_command(["rev-parse", "--verify", self.branch])
        if result and result.strip():
            print(f"[INFO]   目标分支已存在本地: {self.branch}")
            return self.branch

        # Check if remote tracking branch exists
        remote_ref = f"origin/{self.branch}"
        result = self._run_git_command(["rev-parse", "--verify", remote_ref])
        if result and result.strip():
            print(f"[INFO]   目标分支存在于远程: {remote_ref}")
            return remote_ref

        # Try to fetch from origin
        print(f"[INFO]   目标分支不在本地，尝试 git fetch origin {self.branch}...")
        fetch_result = self._run_git_command(["fetch", "origin", self.branch])
        if fetch_result is not None:
            # Check again after fetch
            result = self._run_git_command(["rev-parse", "--verify", remote_ref])
            if result and result.strip():
                print(f"[INFO]   fetch 成功，使用远程分支: {remote_ref}")
                return remote_ref

        # Fallback: try fetching all remotes
        print(f"[WARN]   fetch origin {self.branch} 失败，尝试 git fetch --all...")
        self._run_git_command(["fetch", "--all"])
        result = self._run_git_command(["rev-parse", "--verify", remote_ref])
        if result and result.strip():
            print(f"[INFO]   fetch --all 后找到远程分支: {remote_ref}")
            return remote_ref

        # Last resort: diff against HEAD (no changes will show)
        print(f"[WARN]   无法获取目标分支 {self.branch}，将使用 HEAD 作为基准（可能无法显示变更）")
        return "HEAD"

    def step1_get_local_diff(self):
        """Step 1: Get local git diff (committed changes + uncommitted changes / or specific commit / or commit range)"""
        print("[INFO] Step 1/3: 获取本地git diff...")

        diffs = []
        modified_files = []

        # 区间模式：baseCommit..headCommit
        if self.is_range_mode:
            print(f"[INFO]   区间模式: git diff {self.base_commit} {self.head_commit}")
            range_diff = self._run_git_command(["diff", self.base_commit, self.head_commit])
            if range_diff:
                parsed = self._parse_diff_output(range_diff)
                diffs.extend(parsed['diffs'])
                modified_files.extend(parsed['files'])

            self.diff_branch = self.base_commit
            print(f"[INFO]   变更文件数: {len(modified_files)}")
            return diffs, modified_files

        # Commit 模式：获取单个 commit 的 diff
        if self.commit:
            print(f"[INFO]   Commit 模式: git diff {self.commit}^..{self.commit}")
            commit_diff = self._run_git_command(["diff", f"{self.commit}^..{self.commit}"])
            if commit_diff:
                parsed = self._parse_diff_output(commit_diff)
                diffs.extend(parsed['diffs'])
                modified_files.extend(parsed['files'])

            # Commit 模式不需要设置 diff_branch，但为了兼容性设置为 commit 的父提交
            self.diff_branch = f"{self.commit}^"
            print(f"[INFO]   变更文件数: {len(modified_files)}")
            return diffs, modified_files

        # 分支模式（原有逻辑）
        # Ensure target branch is available locally
        self.diff_branch = self._ensure_target_branch()

        # Get committed changes: git diff {branch}...HEAD
        print(f"[INFO]   获取已提交变更: git diff {self.diff_branch}...HEAD")
        committed_diff = self._run_git_command(["diff", f"{self.diff_branch}...HEAD"])
        if committed_diff:
            parsed = self._parse_diff_output(committed_diff)
            diffs.extend(parsed['diffs'])
            modified_files.extend(parsed['files'])

        # Get uncommitted changes: git diff
        print("[INFO]   获取未提交变更: git diff")
        uncommitted_diff = self._run_git_command(["diff"])
        if uncommitted_diff:
            parsed = self._parse_diff_output(uncommitted_diff)
            # Deduplicate: only add files not already in committed diff
            committed_files = set(modified_files)
            for d in parsed['diffs']:
                new_path = d.get('new_path', '')
                if new_path not in committed_files:
                    diffs.append(d)
                    if new_path:
                        modified_files.append(new_path)

        # Remove duplicates from modified_files while preserving order
        seen = set()
        unique_files = []
        for f in modified_files:
            if f not in seen:
                seen.add(f)
                unique_files.append(f)
        modified_files = unique_files

        print(f"[INFO]   变更文件数: {len(modified_files)}")
        return diffs, modified_files

    def _parse_diff_output(self, diff_output):
        """Parse unified diff output into structured diff entries"""
        diffs = []
        files = []

        if not diff_output or not diff_output.strip():
            return {'diffs': [], 'files': []}

        # Split by diff headers
        diff_sections = re.split(r'^diff --git ', diff_output, flags=re.MULTILINE)

        for section in diff_sections:
            if not section.strip():
                continue

            # Extract file paths from the diff header
            # Format: a/path/to/file b/path/to/file
            header_match = re.match(r'a/(.+?) b/(.+?)\n', section)
            if not header_match:
                continue

            old_path = header_match.group(1)
            new_path = header_match.group(2)
            files.append(new_path)

            # Extract the diff content for this file
            diff_content = f"diff --git a/{old_path} b/{new_path}\n{section}"

            # Determine change type
            change_type = "modified"
            if section.startswith('new file'):
                change_type = "added"
            elif section.startswith('deleted file'):
                change_type = "deleted"

            diffs.append({
                "old_path": old_path,
                "new_path": new_path,
                "diff": diff_content,
                "change_type": change_type
            })

        return {'diffs': diffs, 'files': files}

    def step2_get_repo_info(self):
        """Step 2: Get local repository info"""
        print("[INFO] Step 2/3: 获取本地仓库信息...")

        # Get current branch
        current_branch = self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        current_branch = current_branch.strip() if current_branch else "unknown"

        # 区间模式：从 head_commit 获取信息
        if self.is_range_mode:
            commit_hash = self._run_git_command(["rev-parse", self.head_commit])
            commit_hash = commit_hash.strip() if commit_hash else self.head_commit

            author_name = self._run_git_command(["log", "-1", "--format=%an", self.head_commit])
            author_name = author_name.strip() if author_name else "unknown"

            author_email = self._run_git_command(["log", "-1", "--format=%ae", self.head_commit])
            author_email = author_email.strip() if author_email else "unknown"

            # 使用 head_commit 的 message 作为标题
            head_title = self._run_git_command(["log", "-1", "--format=%s", self.head_commit])
            head_title = head_title.strip() if head_title else "unknown"

            base_short = self._get_commit_short_hash(self.base_commit)
            head_short = self._get_commit_short_hash(self.head_commit)
            commit_title = f"[{base_short}..{head_short}] {head_title}"

            print(f"[INFO]   当前分支: {current_branch}")
            print(f"[INFO]   区间: {base_short}..{head_short}")
            print(f"[INFO]   标题: {commit_title}")
            print(f"[INFO]   作者: {author_name}")

            return {
                "current_branch": current_branch,
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "commit_title": commit_title
            }

        # Commit 模式：从指定 commit 获取信息
        if self.commit:
            # 获取 commit 的完整 hash
            commit_hash = self._run_git_command(["rev-parse", self.commit])
            commit_hash = commit_hash.strip() if commit_hash else self.commit

            # 获取 commit 的 author 信息
            author_name = self._run_git_command(["log", "-1", "--format=%an", self.commit])
            author_name = author_name.strip() if author_name else "unknown"

            author_email = self._run_git_command(["log", "-1", "--format=%ae", self.commit])
            author_email = author_email.strip() if author_email else "unknown"

            # 获取 commit message 作为标题
            commit_title = self._run_git_command(["log", "-1", "--format=%s", self.commit])
            commit_title = commit_title.strip() if commit_title else "unknown"

            print(f"[INFO]   当前分支: {current_branch}")
            print(f"[INFO]   Commit: {commit_hash[:8]}...")
            print(f"[INFO]   标题: {commit_title}")
            print(f"[INFO]   作者: {author_name}")

            return {
                "current_branch": current_branch,
                "commit_hash": commit_hash,
                "author_name": author_name,
                "author_email": author_email,
                "commit_title": commit_title
            }

        # 分支模式（原有逻辑）
        # Get latest commit info
        commit_hash = self._run_git_command(["rev-parse", "HEAD"])
        commit_hash = commit_hash.strip() if commit_hash else "unknown"

        # Get author info
        author_name = self._run_git_command(["config", "user.name"])
        author_name = author_name.strip() if author_name else "unknown"

        author_email = self._run_git_command(["config", "user.email"])
        author_email = author_email.strip() if author_email else "unknown"

        print(f"[INFO]   当前分支: {current_branch}")
        print(f"[INFO]   最新提交: {commit_hash[:8]}...")
        print(f"[INFO]   作者: {author_name}")

        return {
            "current_branch": current_branch,
            "commit_hash": commit_hash,
            "author_name": author_name,
            "author_email": author_email,
            "commit_title": None
        }

    def step3_load_rules(self, repo_path, repo_name, modified_files, target_branch):
        """Step 3: Load review rules"""
        print("[INFO] Step 3/3: 加载检视规则...")
        repo_manager = MRRepoManager(repo_name, target_branch)
        loader = MRRulesLoader(repo_path, self.skill_dir, repo_manager)
        result = loader.load_all_rules(repo_name, modified_files, target_branch)
        rule_ids = result.get('rule_ids', [])
        print(f"[INFO]   规则数量: {len(rule_ids)} 个")
        return result

    def _write_output_file(self, repo_name, output):
        """Write output file"""
        safe_repo_name = repo_name.replace('/', '_')
        mr_subdir = self.temp_dir / f"mr_{safe_repo_name}_{self.mr_id}"
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

        safe_repo_name = self.repo_name.replace('/', '_')
        mr_info_key = f"{safe_repo_name}_{self.mr_id}"
        logger = get_logger(mr_info_key)

        mode_desc = f"区间: {self.base_commit}..{self.head_commit}" if self.is_range_mode else (f"commit: {self.commit}" if self.commit else f"分支: {self.branch}")
        logger.info(f"开始 - 本地模式, 仓库: {self.repo_name}, {mode_desc}")

        print("=" * 50)
        print("Local Review Coordinator (本地模式)")
        print(f"仓库路径: {self.repo_path}")
        if self.is_range_mode:
            base_short = self._get_commit_short_hash(self.base_commit)
            head_short = self._get_commit_short_hash(self.head_commit)
            print(f"Commit 区间: {base_short}..{head_short}")
            print(f"mrId: {self.mr_id}")
        elif self.commit:
            print(f"Commit: {self.commit}")
            print(f"mrId: {self.mr_id}")
        else:
            print(f"目标分支: {self.branch}")
        print(f"仓库名称: {self.repo_name}")
        print("=" * 50)

        # Step 1: Get local diff
        step1_start = time.time()
        diffs, modified_files = self.step1_get_local_diff()
        step1_duration = time.time() - step1_start
        logger.info(f"获取本地diff - 完成 (耗时: {step1_duration:.2f}秒)")
        print("[INFO] Step 1/3: 获取本地git diff - 完成\n")

        # Step 2: Get repo info
        step2_start = time.time()
        repo_info = self.step2_get_repo_info()
        step2_duration = time.time() - step2_start
        logger.info(f"获取仓库信息 - 完成 (耗时: {step2_duration:.2f}秒)")
        print("[INFO] Step 2/3: 获取本地仓库信息 - 完成\n")

        # Step 3: Load rules
        step3_start = time.time()
        # 区间模式或commit模式下使用 diff_branch，否则使用分支模式
        rules_target = self.diff_branch if (self.is_range_mode or self.commit) else self.branch
        rules_result = self.step3_load_rules(
            str(self.repo_path), self.repo_name, modified_files, rules_target
        )
        step3_duration = time.time() - step3_start
        logger.info(f"加载检视规则 - 完成 (耗时: {step3_duration:.2f}秒)")
        print("[INFO] Step 3/3: 加载检视规则 - 完成\n")

        # Build output (same format as mr_coordinator.py)
        # 区间模式使用区间信息，commit 模式使用 commit 信息，否则使用分支模式信息
        if self.is_range_mode:
            base_short = self._get_commit_short_hash(self.base_commit)
            head_short = self._get_commit_short_hash(self.head_commit)
            head_title = repo_info.get('commit_title', '')
            title = f"[Commit区间模式] {base_short}..{head_short}"
            if head_title:
                title = f"[Commit区间模式] {base_short}..{head_short} {head_title}"
            description = f"Commit 区间 {base_short}..{head_short} 的累积变更"
            source_branch = repo_info.get('current_branch', 'unknown')
            target_branch = self.base_commit
        elif self.commit:
            commit_title = repo_info.get('commit_title', '')
            title = f"[Commit模式] {commit_title}" if commit_title else f"[Commit模式] {self.repo_name} @ {self.commit}"
            description = f"Commit {self.commit} 的变更" if not commit_title else f"Commit {self.commit}: {commit_title}"
            source_branch = repo_info.get('current_branch', 'unknown')
            target_branch = self.branch or self.diff_branch
        else:
            title = f"[本地模式] {self.repo_name} vs {self.branch}"
            description = f"本地代码仓 {self.repo_name} 相对于 {self.branch} 分支的变更"
            source_branch = repo_info.get('current_branch', 'unknown')
            target_branch = self.branch

        output = {
            "mr_info": {
                "mr_id": self.mr_id,
                "project_id": None,
                "title": title,
                "description": description,
                "author": repo_info.get('author_email', 'unknown'),
                "author_name": repo_info.get('author_name', 'unknown'),
                "author_id": None,
                "author_username": None,
                "source_branch": source_branch,
                "target_branch": target_branch,
                "web_url": None,
                "domain": None
            },
            "diffs": diffs,
            "modified_files": modified_files,
            "repository": {
                "name": self.repo_name,
                "full_name": self.repo_name,
                "local_path": str(self.repo_path),
                "depend_repos": {}
            },
            "mr_related_repo_path": [str(self.repo_path)],
            "rules": rules_result,
            "report_share_url": "",
            "risk_level": ""
        }

        output_file = self.output_file or self._get_default_output_file(self.repo_name)
        result_file = self._write_output_file(self.repo_name, output)
        if not result_file:
            logger.error("保存输出文件失败")
            return {"success": False, "error": "保存输出文件失败"}

        total_duration = time.time() - start_time
        logger.info(f"完成 - 总耗时: {total_duration:.2f}秒, 输出文件: {result_file}")

        print(f"[SUCCESS] 输出文件: {result_file}")

        print("\n" + "=" * 50)
        print("Local Review Coordinator 完成！")
        print("=" * 50)
        return {"success": True, "output_file": str(output_file)}


def main():
    parser = argparse.ArgumentParser(description='Local Coordinator - 本地代码变更检视数据准备')
    parser.add_argument('--repoPath', required=True, help='本地代码仓路径')
    parser.add_argument('--branch', help='目标分支名（分支模式必需）')
    parser.add_argument('--commit', help='Commit hash（commit模式必需，单个commit的变更）')
    parser.add_argument('--baseCommit', help='原commit hash（区间模式必需，与 --headCommit 配合使用）')
    parser.add_argument('--headCommit', help='后commit hash（区间模式必需，与 --baseCommit 配合使用）')
    parser.add_argument('--repoName', help='代码仓名称（默认从路径推断）')
    parser.add_argument('--outputFile', help='输出JSON文件路径')
    parser.add_argument('--format', choices=['json', 'human'], default='json', help='输出格式')
    parser.add_argument('--debug', action='store_true', help='调试模式')

    args = parser.parse_args()

    # 验证参数：三种模式互斥
    has_range = bool(args.baseCommit or args.headCommit)
    if has_range and args.commit:
        parser.error('--commit 不能与 --baseCommit/--headCommit 同时使用')
    if args.baseCommit and not args.headCommit:
        parser.error('--baseCommit 必须与 --headCommit 同时使用')
    if args.headCommit and not args.baseCommit:
        parser.error('--headCommit 必须与 --baseCommit 同时使用')
    if not args.branch and not args.commit and not has_range:
        parser.error('必须提供以下之一：--branch（分支模式）、--commit（commit模式）、--baseCommit + --headCommit（区间模式）')

    if args.commit and args.branch:
        print(f"[WARN] 同时提供了 --branch 和 --commit，将使用 commit 模式")
    if has_range and args.branch:
        print(f"[WARN] 同时提供了 --branch 和 --baseCommit/--headCommit，将使用区间模式")

    coordinator = LocalCoordinator(
        repo_path=args.repoPath,
        branch=args.branch,
        commit=args.commit,
        base_commit=args.baseCommit,
        head_commit=args.headCommit,
        repo_name=args.repoName,
        output_file=args.outputFile,
        debug=args.debug
    )
    result = coordinator.run()

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))

    if not result.get('success'):
        sys.exit(1)


if __name__ == '__main__':
    main()
