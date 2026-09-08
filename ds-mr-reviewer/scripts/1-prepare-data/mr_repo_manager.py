#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Repository Manager

Usage:
    python mr_repo_manager.py --repository_name <repository_name> --branch <branch_name>

This script manages the local repository for MR review:
- Checks if current directory is a git repository
- Clones the repository if needed
- Performs git pull and checks for conflicts
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config_manager import get_config, get_repo_base_dir


class MRRepoManager:
    """管理MR检视所需的本地代码仓"""

    def __init__(self, repository_name, branchName, repoPath=None, configPath=None,
                 domain=None, ssh_url=None, http_url=None):
        self.repository_name = repository_name
        self.branchName = branchName
        self.configPath = configPath or self._get_default_config_path()
        self.repoPath = repoPath
        self.domain = domain or "codehub-y.huawei.com"
        self.ssh_url = ssh_url  # 直接传入的SSH URL
        self.http_url = http_url  # 直接传入的HTTP URL

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

                # 如果没有指定repoPath，使用默认目录
                if self.repoPath is None:
                    self.repoPath = str(get_repo_base_dir())

                return self.config, None
            except Exception as e:
                return None, f"Error loading config: {str(e)}"
        else:
            # 否则使用config_manager的自动选择逻辑
            self.config = get_config()
            if not self.config:
                return None, "No config found"

            # 如果没有指定repoPath，使用默认目录
            if self.repoPath is None:
                self.repoPath = str(get_repo_base_dir())

            return self.config, None

    def is_git_repository(self, directory):
        """检查指定目录是否为git仓库"""
        try:
            git_dir = Path(directory) / ".git"
            return git_dir.exists() and git_dir.is_dir()
        except Exception:
            return False

    def get_current_branch(self, directory=".", repoPath=None):
        """获取当前目录的git分支名"""
        try:
            # 如果提供了repoPath，构造完整路径
            workdir = repoPath if repoPath else directory
            
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=workdir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return None
        except Exception:
            return None

    def is_matching_branch(self, directory):
        """
        检查指定目录的当前分支是否与期望分支匹配

        Returns:
            tuple: (is_matching: bool, current_branch: str or None)
        """
        if not self.branchName:
            # 如果没有指定期望分支，认为匹配
            return True, None
        
        try:
            current_branch = self.get_current_branch(directory)
            if current_branch is None:
                return False, None
            
            is_match = current_branch == self.branchName
            return is_match, current_branch
        except Exception:
            return False, None

    def _get_ssh_host(self):
        """将domain转换为SSH host"""
        domain_to_ssh = {
            "open.codehub.huawei.com": "szv-open.codehub.huawei.com",
            "codehub-y.huawei.com": "szv-y.codehub.huawei.com",
            "codehub.huawei.com": "szv.codehub.huawei.com",
        }
        ssh_host = domain_to_ssh.get(self.domain)
        if ssh_host:
            return ssh_host
        # 未知domain，抛出明确错误
        raise ValueError(f"未知的CodeHub域名: '{self.domain}'")

    def clone_repository(self):
        """
        克隆代码仓到指定目录（新目录结构：{repo_path}/{branch_name}/{repo_name}）
        
        Returns:
            tuple: (target_dir: Path or None, error: str or None)
        """
        repo_name_for_dir = self.repository_name.replace('/', '_')
        
        # 如果传入了ssh_url，直接使用；否则根据domain映射
        if self.ssh_url:
            git_url = self.ssh_url
        else:
            git_url = f"ssh://git@{self._get_ssh_host()}:2222/{self.repository_name}.git"
        
        target_dir = Path(self.repoPath) / self.branchName / repo_name_for_dir

        try:
            # 检查目标目录是否已存在
            if target_dir.exists():
                # 检查是否是git仓库
                if self.is_git_repository(target_dir):
                    print(f"[INFO] 目录已存在且是git仓库: {target_dir}")
                    
                    # 检查分支是否匹配
                    is_match, current_branch = self.is_matching_branch(target_dir)
                    if not is_match:
                        error_msg = f"目录已存在但当前分支({current_branch})与期望分支({self.branchName})不匹配"
                        print(f"[ERROR] {error_msg}")
                        return None, error_msg
                    
                    return target_dir, None
                else:
                    return None, f"目录已存在但不是git仓库: {target_dir}"

            # 创建父目录（包括分支名目录）
            target_dir.parent.mkdir(parents=True, exist_ok=True)

            # 执行git clone命令
            print(f"[INFO] 开始克隆代码仓...")
            print(f"[INFO] 仓库地址: {git_url}")
            print(f"[INFO] 目标目录: {target_dir}")
            print(f"[INFO] 分支: {self.branchName}")

            try:
                MRRepoManager.clone_repo(repo_name_for_dir, self.branchName, git_url, str(target_dir))
                print(f"[SUCCESS] 代码仓克隆成功: {target_dir}")
                return target_dir, None
            except subprocess.CalledProcessError:
                MRRepoManager.clone_repo(repo_name_for_dir, self.branchName, self.http_url, str(target_dir))
                print(f"[SUCCESS] 代码仓克隆成功: {target_dir}")
                return target_dir, None

        except subprocess.CalledProcessError as e:
            error_msg = f"克隆失败: {e.stderr if e.stderr else str(e)}"
            print(f"[ERROR] {error_msg}")
            return None, error_msg
        except subprocess.TimeoutExpired:
            return None, "克隆命令执行超时（超过5分钟）"
        except Exception as e:
            return None, f"克隆过程中发生错误: {str(e)}"

    def git_pull(self, repoDir, repository_name=None, branchName=None, repoPath=None):
        """
        在指定目录执行git pull，检查是否有冲突

        Args:
            repoDir: 仓库目录路径
            repository_name: 仓库名称（用于错误提示）
            branchName: 分支名称（用于错误提示）
            repoPath: 仓库路径（用于错误提示）

        Returns:
            tuple: (success: bool, message: str)
        """
        # 使用提供的参数或实例属性
        name = repository_name or self.repository_name
        branch = branchName or self.branchName
        path = repoPath or self.repoPath

        try:
            # 切换到目标分支
            print(f"[INFO] 切换到分支: {branch}")
            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=repoDir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10
            )

            if result.returncode != 0:
                return False, f"切换分支失败: {result.stderr}"

            # 执行git pull
            print(f"[INFO] 执行git pull获取最新代码...")
            result = subprocess.run(
                ["git", "pull", "origin", branch],
                cwd=repoDir,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60
            )

            if result.returncode != 0:
                output = result.stderr + result.stdout
                if "CONFLICT" in output or "conflict" in output or "冲突" in output:
                    return False, f"在目录 {path} 下的项目 {name}（分支 {branch}）发生冲突，请手工解决后重新运行"
                elif "Already up to date" in output or "已经是最新的" in output:
                    print(f"[INFO] 本地代码已是最新，无需更新")
                    return True, "本地代码已是最新"
                else:
                    return False, f"git pull失败: {output}"
            
            # 检查是否真的有更新
            if "Already up to date" in result.stdout or "已经是最新的" in result.stdout:
                print(f"[INFO] 本地代码已是最新，无需更新")
                return True, "本地代码已是最新"
            
            print(f"[SUCCESS] git pull成功，已更新到最新版本")
            return True, "git pull成功"
            
        except subprocess.TimeoutExpired:
            return False, "git pull命令执行超时"
        except UnicodeDecodeError:
            print(f"[WARNING] git pull输出包含二进制内容，跳过解析")
            return True, "git pull输出包含二进制内容但已执行"
        except Exception as e:
            return False, f"git pull过程中发生错误: {str(e)}"

    def prepare_repository(self):
        """
        准备代码仓用于MR检视
        
        步骤:
        1. 检查当前目录是否为git仓库
        2. 如果是git仓库且分支匹配，则使用当前目录
        3. 如果不是git仓库或分支不匹配，则克隆代码仓到 {repo_path}/{branch_name}/{repo_name}
        4. 执行git pull获取最新代码
        5. 检查是否有冲突
        
        Returns:
            dict: {
                "success": bool,
                "repo_path": str or None,
                "message": str,
                "error": str or None
            }
        """
        # 加载配置
        config, config_error = self.load_config()
        if config_error:
            return {
                "success": False,
                "repo_path": None,
                "message": "",
                "error": config_error
            }

        # 步骤1: 检查新目录中的代码仓是否已存在
        target_dir_path = Path(self.repoPath) / self.branchName / self.repository_name
        if target_dir_path.exists() and self.is_git_repository(target_dir_path):
            # 检查分支是否匹配
            is_match, current_branch = self.is_matching_branch(target_dir_path)
            if is_match:
                # 仓库已存在且分支匹配，使用现有目录
                print(f"[INFO] 代码仓已存在且分支匹配: {target_dir_path}")
                target_dir = target_dir_path
            else:
                # 仓库已存在但分支不匹配，克隆到新目录（实际上会失败并报错）
                print(f"[INFO] 代码仓已存在但分支不匹配（当前: {current_branch}, 期望: {self.branchName}），将尝试克隆")
                target_dir, clone_error = self.clone_repository()
                if clone_error:
                    return {
                        "success": False,
                        "repo_path": None,
                        "message": "",
                        "error": clone_error
                    }
        else:
            # 代码仓不存在，需要克隆
            print(f"[INFO] 代码仓不存在，将克隆代码仓")
            target_dir, clone_error = self.clone_repository()
            if clone_error:
                return {
                    "success": False,
                    "repo_path": None,
                    "message": "",
                    "error": clone_error
                }

        # 步骤4: 克隆后执行git pull（确保最新）
        target_dir_path = Path(target_dir)
        branch_dir = target_dir_path.parent
        success, message = self.git_pull(target_dir, self.repository_name, self.branchName, str(branch_dir))
        if not success:
            return {
                "success": False,
                "repo_path": str(target_dir),
                "message": "",
                "error": message
            }
        
        return {
            "success": True,
            "repo_path": str(target_dir),
            "message": message,
            "error": None
        }

    def get_repo_base_info(self):
        """获取仓库基本信息（用于MR URL解析等场景）"""
        config, config_error = self.load_config()
        if config_error:
            return {"error": config_error}
        
        # 从config.yaml解析出group路径（如果需要）
        # 这里简单返回仓库名
        return {
            "repo_name": self.repository_name,
            "repo_path": self.repoPath,
            "branch": self.branchName
        }

    def clone_linked_repos(self, repo_names, branch=None):
        """
        批量克隆 linked repos 用于加载检视规则

        Args:
            repo_names: list[str] - 代码仓名称列表
            branch: str - 分支名称（默认使用实例的branchName）

        Returns:
            dict: {repo_name: repo_path} 成功的仓库路径字典
        """
        if not repo_names:
            return {}

        branch = branch or self.branchName
        if not branch:
            print("[WARN] clone_linked_repos: 未指定分支")
            return {}

        config, config_error = self.load_config()
        if config_error:
            print(f"[ERROR] clone_linked_repos: 加载配置失败 - {config_error}")
            return {}

        results = {}
        repo_path = self.repoPath

        for repo_name in repo_names:
            if not repo_name:
                continue

            print(f"[INFO] clone_linked_repos: 处理仓库 {repo_name}...")

            repo_name_for_dir = repo_name.replace('/', '_')
            target_dir = Path(repo_path) / branch / repo_name_for_dir

            if target_dir.exists() and self.is_git_repository(target_dir):
                print(f"[INFO] clone_linked_repos: 仓库已存在，执行git pull: {target_dir}")
                success, message = self.git_pull(target_dir, repo_name, branch, str(target_dir.parent))
                if success:
                    results[repo_name] = str(target_dir)
                    print(f"[INFO] clone_linked_repos: 更新成功 {repo_name}")
                else:
                    print(f"[WARN] clone_linked_repos: 更新失败 {repo_name}: {message}")
                continue

            git_url = f"ssh://git@{self._get_ssh_host()}:2222/{repo_name}.git"

            try:
                target_dir.parent.mkdir(parents=True, exist_ok=True)

                print(f"[INFO] clone_linked_repos: 克隆仓库 {repo_name}...")
                result = subprocess.run(
                    ["git", "clone", "-b", branch, git_url, str(target_dir)],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=300,
                    check=True
                )

                results[repo_name] = str(target_dir)
                print(f"[SUCCESS] clone_linked_repos: 克隆成功 {repo_name}")

            except subprocess.CalledProcessError as e:
                print(f"[WARN] clone_linked_repos: 克隆失败 {repo_name}: {e.stderr if e.stderr else str(e)}")
            except subprocess.TimeoutExpired:
                print(f"[WARN] clone_linked_repos: 克隆超时 {repo_name}")
            except Exception as e:
                print(f"[WARN] clone_linked_repos: 克隆异常 {repo_name}: {str(e)}")

        return results
    @staticmethod
    def clone_repo(repo_name, branch, git_url, target_dir):
        args = ["git", "clone", "-b", branch, git_url, target_dir]
        try:
            print(f"[INFO] clone_repo: 克隆仓库 {repo_name} {' '.join(args)}...")
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=300,
                check=True
            )
            print(f"[SUCCESS] clone_repo: 克隆成功 {repo_name}")

        except subprocess.CalledProcessError as e:
            print(f"[WARN] clone_repo: 克隆失败 {repo_name}: {e.stderr if e.stderr else str(e)}")
            raise e
        except subprocess.TimeoutExpired as e:
            print(f"[WARN] clone_repo: 克隆超时 {repo_name}")
            raise e
        except Exception as e:
            print(f"[WARN] clone_repo: 克隆异常 {repo_name}: {str(e)}")
            raise e


def main():
    parser = argparse.ArgumentParser(description='MR Repository Manager - Prepare local repository for MR review')
    parser.add_argument('--repository_name', required=True, help='Repository name (e.g., TransFeatureRtn)')
    parser.add_argument('--branch', required=True, help='Branch name (e.g., br_NCEV1R25C10_Master)')
    parser.add_argument('--repoPath', help='Local repository base path (default: from config.json or D:\\\\project)')
    parser.add_argument('--configPath', help='Path to config.json (default: ../../config.json)')
    parser.add_argument('--format', choices=['human', 'json'], default='json', help='Output format')

    args = parser.parse_args()

    manager = MRRepoManager(args.repository_name, args.branch, args.repoPath, args.configPath)
    result = manager.prepare_repository()

    if args.format == 'json':
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if result["success"]:
            print(f"✓ 成功")
            print(f"  代码仓路径: {result['repo_path']}")
            print(f"  提示信息: {result['message']}")
        else:
            print(f"✗ 失败")
            print(f"  错误信息: {result['error']}")

    # 如果失败，返回非零退出码
    if not result["success"]:
        sys.exit(1)


if __name__ == '__main__':
    main()