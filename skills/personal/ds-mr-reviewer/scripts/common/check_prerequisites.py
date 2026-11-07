#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Reviewer 前置条件检查脚本

此脚本检查 MR Reviewer Skill 运行所需的前置条件：
1. Python 版本
2. Python 依赖库
3. Git 是否安装
4. config.json 是否存在和配置正确

Usage:
    python check_prerequisites.py [--fix]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


class PrerequisitesChecker:
    """前置条件检查器"""

    def __init__(self, skill_dir=None, fix=False):
        self.skill_dir = Path(skill_dir) if skill_dir else Path(__file__).parent.parent.parent
        self.fix = fix
        self.issues = []
        self.warnings = []
        self.fixed = []
        self.version = self._get_skill_version()

    def _get_skill_version(self):
        """从 SKILL.md 中获取版本号"""
        skill_md = self.skill_dir / "SKILL.md"
        if not skill_md.exists():
            return None
        try:
            with open(skill_md, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('version:'):
                        return line.strip().split('version:')[1].strip()
        except Exception:
            pass
        return None

    def check_python_version(self):
        """检查 Python 版本"""
        print("[INFO] 检查 Python 版本...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 10):
            self.issues.append(f"Python 版本过低: {version.major}.{version.minor}.{version.micro}，需要 Python 3.10+")
            return False

        print(f"  [OK] Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True

    def check_python_package(self, package_name, required=True, optional_imports=None):
        """
        检查 Python 包是否安装

        Args:
            package_name: 包名（pip install 时使用的名称）
            required: 是否必需
            optional_imports: 可选的导入名称列表（如果第一个失败则尝试其他的）
        """
        if optional_imports is None:
            optional_imports = [package_name]

        for import_name in optional_imports:
            try:
                __import__(import_name)
                return True
            except ImportError:
                continue

        if required:
            self.issues.append(f"缺少必需的 Python 包: {package_name}")
            return False
        else:
            self.warnings.append(f"缺少可选的 Python 包: {package_name}（功能可能受限）")
            return False

    def install_package(self, package_name):
        """尝试自动安装 Python 包"""
        print(f"  [INFO] 尝试自动安装 {package_name}...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "--trusted-host", "mirrors.tools.huawei.com", "-i", "http://mirrors.tools.huawei.com/pypi/simple", package_name, "-q"],
                capture_output=True,
                text=True,
                timeout=120
            )
            if result.returncode == 0:
                self.fixed.append(f"已自动安装: {package_name}")
                print(f"  [OK] 已安装: {package_name}")
                return True
            else:
                print(f"  [FAIL] 安装失败: {result.stderr}")
                return False
        except subprocess.TimeoutExpired:
            print(f"  [FAIL] 安装超时")
            return False
        except Exception as e:
            print(f"  [FAIL] 安装异常: {e}")
            return False

    def check_python_dependencies(self):
        """检查 Python 依赖"""
        print("\n[INFO] 检查 Python 依赖...")

        # 核心依赖（MR检视基本功能必需）
        core_deps = [
            ("requests", True, None),
            ("urllib3", True, None),
            ("requests_toolbelt", True, ["requests_toolbelt", "requests.toolbelt"]),
            ("yaml", True, ["yaml", "pyyaml"]),
        ]

        # WeLink通知依赖（可选，需要Windows）
        welink_deps = [
            ("httpx", False, None),
            ("fastmcp", False, None),
            ("pywin32", False, ["win32", "pywin32"]),
        ]

        deps_status = []

        # 检查核心依赖
        print("\n  --- 核心依赖 ---")
        for pkg_name, required, optional_imports in core_deps:
            if self.check_python_package(pkg_name, required=required, optional_imports=optional_imports):
                print(f"  [OK] {pkg_name}")
            else:
                if self.fix:
                    if self.install_package(pkg_name):
                        self.check_python_package(pkg_name, required=required, optional_imports=optional_imports)
                deps_status.append(False)

        # 检查WeLink通知依赖
        print("\n  --- WeLink通知依赖（可选） ---")
        for pkg_name, required, optional_imports in welink_deps:
            if self.check_python_package(pkg_name, required=required, optional_imports=optional_imports):
                print(f"  [OK] {pkg_name}")
            else:
                if self.fix:
                    if self.install_package(pkg_name):
                        self.check_python_package(pkg_name, required=required, optional_imports=optional_imports)
                deps_status.append(False)

        return all(deps_status) if deps_status else True

    def check_git(self):
        """检查 Git 是否安装"""
        print("\n[INFO] 检查 Git...")
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"  [OK] {version}")
                return True
            else:
                self.issues.append("Git 未安装或不可用")
                return False
        except FileNotFoundError:
            self.issues.append("Git 未安装（找不到 git 命令）")
            return False
        except Exception as e:
            self.issues.append(f"Git 检查异常: {e}")
            return False

    def check_config_file(self):
        """检查 config.json 配置文件 - 只检查用户目录"""
        print("\n[INFO] 检查配置文件...")
        config_path = Path.home() / ".mr-reviewer" / "config.json"

        # 检查文件是否存在
        if not config_path.exists():
            self.issues.append(f"配置文件不存在: {config_path}")
            # 如果是 fix 模式，尝试创建默认配置
            if self.fix:
                default_config = {
                    "codehub_token": "YOUR_CODEHUB_TOKEN_HERE"
                }
                try:
                    config_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(default_config, f, ensure_ascii=False, indent=2)
                    self.fixed.append(f"已创建默认配置文件: {config_path}")
                    print(f"  [OK] 已创建默认配置文件")
                    print(f"  ! 请编辑配置文件，填入您的 codehub_token")
                    return False  # 仍需用户配置
                except Exception as e:
                    print(f"  [FAIL] 创建配置文件失败: {e}")
            return False

        # 检查配置内容
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 检查必需的配置项
            codehub_token = config.get("codehub_token", "").strip()
            if not codehub_token or codehub_token == "YOUR_CODEHUB_TOKEN_HERE":
                self.issues.append("config.json 中未配置 codehub_token")
                print(f"  [FAIL] 未配置 codehub_token")
                return False

            print(f"  [OK] 配置文件存在")
            return True

        except json.JSONDecodeError as e:
            self.issues.append(f"config.json 格式错误: {e}")
            return False
        except Exception as e:
            self.issues.append(f"读取配置文件失败: {e}")
            return False

    def check_skill_version(self):
        """检查 skill 版本并自动更新"""
        print("\n[INFO] 检查 Skill 版本...")
        if not self.version:
            print("  [WARN] 无法获取本地版本号，跳过版本检查")
            return True

        updater_script = Path(__file__).parent / "skill_version_updater.py"
        if not updater_script.exists():
            print(f"  [WARN] 版本更新脚本不存在: {updater_script}，跳过版本检查")
            return True

        try:
            result = subprocess.run(
                [sys.executable, str(updater_script), "--version", self.version],
                timeout=180,
            )
            # 不捕获输出，让子进程直接打印到终端
            if result.returncode != 0:
                self.warnings.append(f"Skill 版本检查/更新异常 (退出码 {result.returncode})")
            print("  [OK] 版本检查完成")
            return True
        except subprocess.TimeoutExpired:
            print("  [WARN] 版本检查超时，跳过")
            self.warnings.append("Skill 版本检查超时")
            return True
        except Exception as e:
            print(f"  [WARN] 版本检查异常: {e}，跳过")
            return True

    def report_access(self):
        """上报 Skill 调用统计（fire-and-forget，不阻塞流程）"""
        try:
            from report_usage import report_access as _report
            _report("SKILL", "ds-mr-reviewer")
            print("  [OK] 调用统计已上报")
        except Exception:
            # 上报失败不影响主流程
            pass

    def check_all(self):
        """执行所有检查"""
        print("=" * 60)
        print("MR Reviewer 前置条件检查")
        print("=" * 60)

        # 调用统计上报
        self.report_access()

        # 静态检查
        results = []
        results.append(self.check_python_version())
        results.append(self.check_python_dependencies())
        results.append(self.check_git())
        results.append(self.check_config_file())

        # 版本检查
        self.check_skill_version()

        return not self.issues

    def print_summary(self):
        """打印检查结果摘要"""
        print("\n" + "=" * 60)
        print("检查结果摘要")
        print("=" * 60)

        if self.issues:
            print("\n[X] 问题 (必须修复):")
            for issue in self.issues:
                print(f"   - {issue}")

        if self.warnings:
            print("\n[!] 警告 (建议修复):")
            for warning in self.warnings:
                print(f"   - {warning}")

        if self.fixed:
            print("\n[OK] 已自动修复:")
            for fix in self.fixed:
                print(f"   - {fix}")

        if not self.issues and not self.warnings:
            print("\n[OK] 所有前置条件已满足！")

        print()

    def get_status(self):
        """获取检查状态"""
        if self.issues:
            return "failed"
        elif self.warnings:
            return "warning"
        else:
            return "ok"


def main():
    parser = argparse.ArgumentParser(description="MR Reviewer 前置条件检查")
    parser.add_argument("--fix", action="store_true", default=True, help="自动尝试修复问题（默认开启）")
    parser.add_argument("--skill-dir", help="Skill 目录路径（默认: 当前目录）")

    args = parser.parse_args()

    checker = PrerequisitesChecker(skill_dir=args.skill_dir, fix=args.fix)
    success = checker.check_all()
    checker.print_summary()

    status = checker.get_status()
    if status == "failed":
        print("[X] 前置条件检查未通过，请修复上述问题后重试。")
        print("\n如何获取 CodeHub Token:")
        print("   1. 登录 CodeHub (例如: https://open.codehub.huawei.com 或 https://codehub-y.huawei.com)")
        print("   2. 点击右上角头像 -> 个人设置")
        print("   3. 选择 访问令牌 -> 创建个人访问令牌")
        print("   4. 权限至少需要: read_api")
        print("   5. 将生成的令牌填入 config.json 的 codehub_token 字段")
        sys.exit(1)
    elif status == "warning":
        print("[!] 前置条件检查通过，但有警告事项。")
        sys.exit(0)
    else:
        print("[OK] 前置条件检查通过！")
        sys.exit(0)


if __name__ == "__main__":
    main()
