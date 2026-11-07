#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规则文件合并与迁移脚本
用于在准备数据阶段，将代码仓中遗留的多个检视规则文件合并为唯一的 .ai-coding/review/rules.md 文件。
"""

import argparse
from pathlib import Path

def migrate_rule_files(repo_path_str):
    repo_path = Path(repo_path_str).expanduser().resolve()
    
    if not repo_path.exists() or not repo_path.is_dir():
        print(f"[ERROR] 仓库目录不存在: {repo_path}")
        return

    print(f"[INFO] 开始检查并合并规则文件: {repo_path}")
    
    target_dir = repo_path / ".ai-coding" / "review"
    target_file = target_dir / "rules.md"

    # 如果目标文件已经存在，说明已经合并过，直接跳过
    if target_file.exists():
        print(f"[INFO] 目标合并文件已存在，无需重复迁移: {target_file.relative_to(repo_path)}")
        return

    # 需要被合并的旧文件列表（按优先级顺序）
    sources = [
        repo_path / "mr_reviewer_rules.md",
        repo_path / "mr_reviewer_tips.md",
        repo_path / ".codespec" / "review" / "codecheck.md"
    ]

    merged_content = []
    files_to_remove = []

    for src in sources:
        if src.exists() and src.is_file():
            try:
                with open(src, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        merged_content.append(content)
                files_to_remove.append(src)
            except Exception as e:
                print(f"  [ERROR] 读取文件失败 {src.name}: {e}")

    # 如果提取到了内容，才去创建文件夹并写入新的 rules.md
    if merged_content:
        try:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write("\n\n\n".join(merged_content) + "\n")
            print(f"  [SUCCESS] 成功合并规则到: {target_file.relative_to(repo_path)}")

            # 合并成功后，删除旧文件
            for f in files_to_remove:
                try:
                    f.unlink()
                    print(f"  [INFO] 已清理旧文件: {f.relative_to(repo_path)}")
                except Exception as e:
                    print(f"  [WARN] 清理旧文件失败 {f.name}: {e}")

        except Exception as e:
            print(f"  [ERROR] 写入合并文件失败: {e}")
    else:
        print("[INFO] 没有找到需要迁移的旧规则文件，未做任何修改。")


def main():
    parser = argparse.ArgumentParser(description="合并仓库中的代码检视规则文件到 rules.md")
    parser.add_argument('--repoPath', required=True, help="需要处理的本地代码仓绝对路径")
    
    args = parser.parse_args()
    migrate_rule_files(args.repoPath)

if __name__ == "__main__":
    main()