#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
MR Rules Loader

Usage:
    python mr_rules_loader.py --repoPath "D:\project\for_mr_review\br_NCEV1R25C10_Master\TransFeatureAson"

This script loads review rules from:
1. Language-specific rules: rules/language/{language}_rules.md
2. Repo root rules: {repo_path}/.ai-coding/review/rules.md
3. Linked repo rules: via link_repo metadata, clone and load linked repos' rule files
"""

import argparse
import json
import re
import sys
from pathlib import Path


class MRRulesLoader:
    def __init__(self, repo_path=None, skill_dir=None, repo_manager=None):
        self.repo_path = Path(repo_path) if repo_path else None
        self.skill_dir = Path(skill_dir) if skill_dir else Path(__file__).parent.parent.parent
        self.rules_dir = self.skill_dir / "rules"
        self.language_dir = self.rules_dir / "language"
        self.repo_manager = repo_manager
        self.visited_repos = set()

    def _parse_structured_rules(self, content):
        """解析结构化markdown规则，提取rule_id列表和规则详情"""
        if not content:
            return []

        rules = []
        pattern = r'###\s+([A-Z]+(?:_[A-Z]+)?(?:-[A-Z]+)*-\d+):\s*(.+)'
        for match in re.finditer(pattern, content):
            rule_id = match.group(1).strip()
            title = match.group(2).strip()

            rule_block_start = match.start()
            next_match = re.search(pattern, content[match.end():])
            if next_match:
                rule_block = content[rule_block_start:match.end() + next_match.start()]
            else:
                rule_block = content[rule_block_start:]

            checkpoint = ""
            cp_match = re.search(r'\- \*\*检查锚点\*\*:\s*(.+)', rule_block)
            if cp_match:
                checkpoint = cp_match.group(1).strip()

            sample_bad = ""
            bad_match = re.search(r'\- \*\*反例\*\*:\s*(.+)', rule_block)
            if bad_match:
                sample_bad = bad_match.group(1).strip()

            sample_good = ""
            good_match = re.search(r'\- \*\*正例\*\*:\s*(.+)', rule_block)
            if good_match:
                sample_good = good_match.group(1).strip()

            rules.append({
                "rule_id": rule_id,
                "title": title,
                "checkpoint": checkpoint,
                "sample_bad": sample_bad,
                "sample_good": sample_good
            })

        return rules

    def _read_file_content(self, file_path):
        """读取文件内容"""
        if not file_path or not Path(file_path).exists():
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"[WARN] 读取文件失败 {file_path}: {e}")
            return None

    def _get_language_from_file(self, file_path):
        """根据文件路径判断编程语言"""
        if not file_path:
            return None

        extensions = {
            '.java': 'java',
            '.py': 'python',
            '.cpp': 'cpp', '.cc': 'cpp', '.hpp': 'cpp',
            '.c': 'c', '.h': 'c',
            '.js': 'js_ts', '.jsx': 'js_ts',
            '.ts': 'js_ts', '.tsx': 'js_ts',
            '.go': 'go',
            '.rs': 'rust',
            '.php': 'php',
        }

        ext = Path(file_path).suffix.lower()
        return extensions.get(ext)

    def _load_language_rules(self, lang):
        """加载指定语言的检视规则"""
        if not lang:
            return ""

        rules_file = self.language_dir / f"{lang}_rules.md"
        content = self._read_file_content(rules_file)
        return content or ""

    def _load_common_rules(self):
        """加载通用检视规则 common_rules.md"""
        common_rules_file = self.rules_dir / "common_rules.md"
        return self._read_file_content(common_rules_file) or ""

    def _find_repo_rule_file(self, repo_path):
        """
        查找代码仓唯一合并的规则文件 rules.md
        """
        if not repo_path:
            return None

        rules_file = Path(repo_path) / ".ai-coding" / "review" / "rules.md"
        content = self._read_file_content(rules_file)
        
        return content

    def _load_repo_root_rules(self):
        """加载代码仓规则"""
        if not self.repo_path:
            return ""
        return self._find_repo_rule_file(self.repo_path) or ""

    def _parse_frontmatter(self, content):
        """解析YAML元数据"""
        if not content:
            return {}

        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if not match:
            return {}

        try:
            import yaml
            metadata = yaml.safe_load(match.group(1))
            return metadata if metadata else {}
        except Exception as e:
            print(f"[WARN] 解析frontmatter失败: {e}")
            return {}

    def _get_link_repo(self, content):
        """从检视规则文件内容中提取link_repo配置"""
        metadata = self._parse_frontmatter(content)
        link_repo_str = metadata.get('link_repo', '')

        if not link_repo_str:
            return []

        repos = [r.strip() for r in link_repo_str.split(',') if r.strip()]
        return repos

    def _load_linked_repo_rules_recursive(self, repo_name, repo_path, target_branch):
        """递归加载linked repo的检视规则"""
        if repo_name in self.visited_repos:
            print(f"[INFO] 检测到循环引用，跳过: {repo_name}")
            return {}

        self.visited_repos.add(repo_name)
        rules_content_map = {}

        content = self._find_repo_rule_file(repo_path)
        if not content:
            return rules_content_map

        print(f"[INFO] 加载linked repo检视规则: {repo_name}")
        rules_content_map[repo_name] = content

        link_repos = self._get_link_repo(content)
        if not link_repos:
            return rules_content_map

        if self.repo_manager:
            linked_paths = self.repo_manager.clone_linked_repos(link_repos, target_branch)
        else:
            linked_paths = {}

        for linked_repo in link_repos:
            linked_path = linked_paths.get(linked_repo)
            if not linked_path:
                print(f"[WARN] 未找到linked repo路径: {linked_repo}")
                continue

            linked_rules_map = self._load_linked_repo_rules_recursive(
                linked_repo, linked_path, target_branch
            )
            rules_content_map.update(linked_rules_map)

        return rules_content_map

    def load_all_rules(self, repo_name=None, modified_files=None, target_branch=None):
        """加载所有检视规则"""
        language_rules_content = {}
        linked_repo_rules_content = {}
        language_rules_set = set()

        if modified_files:
            for file_path in modified_files:
                lang = self._get_language_from_file(file_path)
                if lang:
                    language_rules_set.add(lang)

        repo_root_rules = self._load_repo_root_rules()


        if target_branch:
            self.visited_repos = set()
            if repo_name:
                self.visited_repos.add(repo_name)

            link_repos = self._get_link_repo(repo_root_rules)
            if link_repos and self.repo_manager:
                linked_paths = self.repo_manager.clone_linked_repos(link_repos, target_branch)

                for linked_repo, linked_path in linked_paths.items():
                    linked_rules_map = self._load_linked_repo_rules_recursive(
                        linked_repo, linked_path, target_branch
                    )
                    linked_repo_rules_content.update(linked_rules_map)

        for lang in language_rules_set:
            lang_content = self._load_language_rules(lang)
            if lang_content:
                language_rules_content[lang] = lang_content

        rules_parts = []

        common_rules = self._load_common_rules()
        if common_rules:
            rules_parts.append("=== 通用检视规则 (common_rules.md) ===\n")
            rules_parts.append(common_rules)

        if repo_root_rules:
            rules_parts.append("=== 代码仓统一检视规则 (.ai-coding/review/rules.md) ===\n")
            rules_parts.append(repo_root_rules)

        if linked_repo_rules_content:
            for linked_repo, rules_content in linked_repo_rules_content.items():
                rules_parts.append(f"\n=== Linked Repo: {linked_repo} (.ai-coding/review/rules.md) ===\n")
                rules_parts.append(rules_content)

        for lang, lang_content in language_rules_content.items():
            rules_parts.append(f"\n=== 语言规则: {lang} ===\n")
            rules_parts.append(lang_content)

        all_rules_combined = "\n".join(rules_parts)

        rule_ids = []
        checkpoints_map = {}
        
        if all_rules_combined:
            parsed_rules = self._parse_structured_rules(all_rules_combined)
            rule_ids = [r["rule_id"] for r in parsed_rules]
            
            for r in parsed_rules:
                if r.get("checkpoint"):
                    checkpoints_map[r["rule_id"]] = r.get("checkpoint")

        return {
            "all_rules_combined": all_rules_combined,
            "rule_ids": rule_ids,
            "checkpoints": checkpoints_map  
        }

    def get_repo_root_rules_content(self):
        """获取代码仓根目录检视规则文件的内容"""
        return self._load_repo_root_rules()


def main():
    parser = argparse.ArgumentParser(description='MR Rules Loader')
    parser.add_argument('--repoPath', required=True, help='Repository local path')
    parser.add_argument('--repoName', help='Repository name (e.g., TransFeatureAson)')
    parser.add_argument('--targetBranch', help='Target branch for cloning linked repos')
    parser.add_argument('--mrInfoFile', required=True, help='MR info JSON file path from step 2')
    parser.add_argument('--format', choices=['human', 'json'], default='json', help='Output format')

    args = parser.parse_args()

    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from mr_repo_manager import MRRepoManager
    repo_manager = MRRepoManager(args.repoName or "", args.targetBranch or "")

    loader = MRRulesLoader(repo_path=args.repoPath, repo_manager=repo_manager)

    try:
        with open(args.mrInfoFile, 'r', encoding='utf-8') as f:
            mr_data = json.load(f)
        diffs = mr_data.get('diffs', [])
        modified_files = [diff.get('new_path') or diff.get('old_path') for diff in diffs if diff.get('new_path') or diff.get('old_path')]
        print(f"[INFO] 从MR信息文件自动提取 {len(modified_files)} 个修改文件")
    except Exception as e:
        print(f"[ERROR] 读取MR信息文件失败: {e}")
        sys.exit(1)

    result = loader.load_all_rules(args.repoName, modified_files, args.targetBranch)

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["all_rules_combined"]:
            print("=== 已加载检视规则 ===")
            print(f"规则数量: {len(result['rule_ids'])}")
        else:
            print("[INFO] 未找到检视规则文件")

    return 0


if __name__ == '__main__':
    sys.exit(main())