#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cleanup temp directory - remove MR subdirectories older than retention days
Temp files are now stored in user home directory: ~/.mr-reviewer/temp

Usage:
    python cleanup_temp.py --retentionDays 7
"""

import argparse
import json
import os
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))
from config_manager import get_temp_dir, get_repo_base_dir

REPO_RETENTION_DAYS = 15

def cleanup_mr_subdirectories(temp_dir, cutoff_time):
    """Cleanup old MR subdirectories"""
    deleted_count = 0
    deleted_dirs = 0
    
    for subdir in temp_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith('mr_'):
            # Check if any file in subdirectory is newer than cutoff
            has_new_file = False
            for file_path in subdir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime >= cutoff_time:
                    has_new_file = True
                    break
            
            # If no new files, delete entire subdirectory
            if not has_new_file:
                import shutil
                shutil.rmtree(subdir)
                deleted_dirs += 1
                # Count files in deleted directory for logging
                file_count = sum(1 for item in subdir.rglob('*') if item.is_file())
                deleted_count += file_count
                print(f"[DEBUG] Removed directory {subdir.name} ({file_count} files)")
    
    return deleted_count, deleted_dirs

def cleanup_flat_files(temp_dir, cutoff_time):
    """Cleanup old flat files (non-MR subdirectory files)"""
    deleted_count = 0
    for file_path in temp_dir.iterdir():
        if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
            file_path.unlink()
            deleted_count += 1
            print(f"[DEBUG] Deleted {file_path.name}")
    return deleted_count

def cleanup_old_repos(repo_base_dir, cutoff_time):
    """清理超过15天的代码仓目录"""
    deleted_count = 0
    deleted_dirs = 0
    
    if not repo_base_dir.exists():
        print(f"[INFO] 代码仓目录不存在: {repo_base_dir}")
        return deleted_count, deleted_dirs
    
    print(f"[INFO] 开始扫描代码仓目录: {repo_base_dir}")
    
    for subdir in repo_base_dir.iterdir():
        if not subdir.is_dir():
            continue
        
        dir_age_days = (time.time() - subdir.stat().st_mtime) / (24 * 3600)
        if dir_age_days > REPO_RETENTION_DAYS:
            try:
                shutil.rmtree(subdir)
                deleted_dirs += 1
                print(f"[DEBUG] 已删除过期代码仓目录: {subdir.name} (创建于 {dir_age_days:.0f} 天前)")
            except Exception as e:
                print(f"[WARN] 删除代码仓目录失败: {subdir.name}, 错误: {e}")
    
    if deleted_dirs > 0:
        print(f"[SUCCESS] 已清理 {deleted_dirs} 个过期代码仓目录")
    else:
        print(f"[INFO] 没有需要清理的过期代码仓目录")
    
    return deleted_count, deleted_dirs

def main():
    parser = argparse.ArgumentParser(description='Cleanup temp directory')
    parser.add_argument('--retentionDays', type=int, default=7, help='Retention days (deprecated, fixed to 7 days)')

    args = parser.parse_args()

    # 临时文件固定保留7天
    retention_days = 7

    # Get temp directory from config manager
    temp_dir = get_temp_dir()

    if not temp_dir.exists():
        print("[INFO] Temp directory does not exist")
        return
    
    # Calculate cutoff time
    cutoff_time = time.time() - (retention_days * 24 * 3600)
    
    # Cleanup MR subdirectories
    deleted_files, deleted_dirs = cleanup_mr_subdirectories(temp_dir, cutoff_time)
    
    # Cleanup other flat files
    deleted_flat = cleanup_flat_files(temp_dir, cutoff_time)
    
    total_deleted = deleted_files + deleted_flat
    print(f"[SUCCESS] Deleted {total_deleted} files in {deleted_dirs} MR subdirectories (+ {deleted_flat} other files) older than {retention_days} days")
    
    # Cleanup old repositories
    print(f"\n[INFO] === 清理过期代码仓目录 ===")
    repo_base_dir = get_repo_base_dir()
    repo_cutoff_time = time.time() - (REPO_RETENTION_DAYS * 24 * 3600)
    cleanup_old_repos(repo_base_dir, repo_cutoff_time)

if __name__ == "__main__":
    main()
