#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理模块 - 优先读取用户目录配置，回退到skill目录配置
"""

import json
from pathlib import Path

def get_config():
    """
    获取配置，只从用户目录读取
    
    Returns:
        dict: 配置字典
    """
    user_config_file = Path.home() / ".mr-reviewer" / "config.json"
    
    if not user_config_file.exists():
        print(f"[WARN] 用户配置文件不存在: {user_config_file}")
        return {}
    
    try:
        with open(user_config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except json.JSONDecodeError as e:
        print(f"[ERROR] 解析配置文件失败 {user_config_file}: {e}")
        return {}

def get_config_value(key, default=None):
    """
    获取配置项的值
    
    Args:
        key: 配置键
        default: 默认值
    
    Returns:
        配置值，如果不存在则返回默认值
    """
    config = get_config()
    return config.get(key, default)

def get_user_config_path():
    """
    获取用户目录配置文件路径
    
    Returns:
        Path: 用户目录配置文件路径
    """
    return Path.home() / ".mr-reviewer" / "config.json"

def get_skill_config_path():
    """
    获取skill目录配置文件路径
    
    Returns:
        Path: skill目录配置文件路径
    """
    skill_dir = Path(__file__).parent.parent.parent
    return skill_dir / "config.json"

def get_user_dir():
    """
    获取用户目录路径
    
    Returns:
        Path: 用户目录路径 (~/.mr-reviewer)
    """
    return Path.home() / ".mr-reviewer"

def get_temp_dir():
    """
    获取临时文件目录路径
    
    Returns:
        Path: 临时文件目录路径 (~/.mr-reviewer/temp)
    """
    return Path.home() / ".mr-reviewer" / "temp"

def get_repo_base_dir():
    """
    获取代码仓本地存储根目录
    
    优先读取 config.json 中的 clone_repo_path 配置，
    如果未配置则使用默认路径 ~/.mr-reviewer/project
    
    Returns:
        Path: 代码仓存储目录
    """
    config = get_config()
    clone_repo_path = config.get("clone_repo_path")
    
    if clone_repo_path:
        return Path(clone_repo_path)
    
    return Path.home() / ".mr-reviewer" / "project"
