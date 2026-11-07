#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Reviewer Skill 统一日志管理器

提供标准化的日志记录功能，所有脚本统一使用此模块进行日志记录。

日志格式：
    {时间} - {级别} - [{MR信息}] [{脚本名}] {消息}

Example:
    logger = get_logger("NCE-T_TransFrontendNeMgrBiz_3261")
    logger.info("成功解析JSON并输出")
"""

import logging
import os
import inspect
from pathlib import Path
from datetime import datetime
from typing import Optional

_logs_dir = Path.home() / ".mr-reviewer" / "logs"
_logs_dir.mkdir(parents=True, exist_ok=True)

_log_file = _logs_dir / f"mr_reviewer_skill_{datetime.now().strftime('%Y%m%d')}.log"

_root_logger = None
_handler_added = False


def _get_root_logger() -> logging.Logger:
    """获取根logger，单例模式"""
    global _root_logger, _handler_added
    
    if _root_logger is None:
        _root_logger = logging.getLogger('mr_reviewer_skill')
        _root_logger.setLevel(logging.INFO)
        
        if not _handler_added:
            file_handler = logging.FileHandler(_log_file, encoding='utf-8')
            file_handler.setLevel(logging.INFO)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)
            _root_logger.addHandler(file_handler)
            _handler_added = True
    
    return _root_logger


def _get_script_name() -> str:
    """获取调用栈中的脚本名（不含.py后缀）"""
    stack = inspect.stack()
    for frame_info in stack:
        filename = frame_info.filename
        if filename.endswith('.py'):
            script_name = os.path.basename(filename)
            if script_name != '__init__.py' and script_name != 'logger_manager.py':
                return script_name[:-3]
    return 'unknown'


def get_logger(mr_info: str) -> logging.Logger:
    """
    获取配置好的logger实例

    Args:
        mr_info: MR标识信息，格式如 NCE-T_TransFrontendNeMgrBiz_3261

    Returns:
        配置好的logger实例
    """
    _get_root_logger()
    script_name = _get_script_name()

    logger = logging.getLogger(f'mr_reviewer_skill.{mr_info}.{script_name}')
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    file_handler = logging.FileHandler(_log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)

    file_formatter = logging.Formatter(
        f'%(asctime)s - %(levelname)s - [{mr_info}] [{script_name}] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    console_formatter = logging.Formatter(
        f'%(asctime)s - %(levelname)s - [{mr_info}] [{script_name}] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger


def log_info(mr_info: str, message: str):
    """快捷日志方法"""
    logger = get_logger(mr_info)
    logger.info(message)


def log_error(mr_info: str, message: str):
    """快捷日志方法"""
    logger = get_logger(mr_info)
    logger.error(message)


def log_warning(mr_info: str, message: str):
    """快捷日志方法"""
    logger = get_logger(mr_info)
    logger.warning(message)


def log_debug(mr_info: str, message: str):
    """快捷日志方法"""
    logger = get_logger(mr_info)
    logger.debug(message)