#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
行号校验与修正脚本

用于校验mr_risks.json中的行号是否准确，并基于MR diff重新计算正确的行号。

v2:
- 搜索范围扩展到上下文行
- 整行匹配优先，子串兜底
- 激活关键词 fallback
- problem_code 为空时尝试从 description 提取代码片段
- 多匹配时优先选离 AI 行号最近的

Usage:
    python check_and_fix_line_numbers.py --mrInfoFile <coordinator路径> --risksFile <mr_risks路径>

输出：
    - 自动修正后的mr_risks.json（如果行号需要修正）
    - 详细的校验报告
"""

import argparse
import json
import sys
import re
import http.client
import requests
import urllib3
from pathlib import Path
from urllib.parse import quote
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ISSUE_MARKER = "MR代码检视问题"

# 添加 precise_line_finder 模块路径
sys.path.insert(0, str(Path(__file__).parent))
from precise_line_finder import find_diff_for_file, find_code_line_numbers


def extract_keywords(description):
    """
    从风险描述中提取用于匹配的关键词

    支持多种语言的函数名/变量名提取：
    - Java: 方法名、变量名、API调用
    - C: 函数名、宏名、变量名

    Returns:
        list: 关键词列表，按优先级排序
    """
    keywords = []

    # 函数名提取（Java + C 通用）
    func_patterns = [
        r'函数[：:]\s*(\w+)',
        r'(\w+)\s*函数',
        r'方法[：:]\s*(\w+)',
        r'(\w+)\s*方法',
        r'调用\s+(\w+)',
        r'(\w+)\s*\([^)]*\)',
    ]
    for pattern in func_patterns:
        match = re.search(pattern, description)
        if match:
            kw = match.group(1)
            # 过滤常见停用词
            if kw not in ('if', 'else', 'for', 'while', 'return', 'switch', 'case'):
                keywords.append(('method', kw))

    # 变量名/标识符提取
    var_patterns = [
        r'(\w+)\s+为\s*null',
        r'(\w+)\s+参数',
        r'(\w+)\s+可能为空',
        r'变量\s*(\w+)',
        r'(\w+)\.length\(\)',
        r'(\w+)\.substring\(',
    ]
    for pattern in var_patterns:
        match = re.search(pattern, description)
        if match:
            keywords.append(('var', match.group(1) if match.groups() else match.group(0)))

    # 宏/常量提取（C 风格大写标识符）
    macro_matches = re.findall(r'\b([A-Z][A-Z_0-9]{2,})\b', description)
    for m in macro_matches[:2]:
        keywords.append(('var', m))

    return keywords[:8]


def extract_code_from_description(description):
    """
    从描述文本中提取可能的代码片段

    AI 可能在描述中用反引号、引号或中文引号包裹了代码片段，
    当 problem_code 为空时，尝试从这里提取。

    Returns:
        list: 提取到的代码片段列表
    """
    snippets = []

    # 提取反引号包裹的代码: `code`
    backtick_matches = re.findall(r'`([^`]+)`', description)
    for m in backtick_matches:
        m = m.strip()
        if 3 < len(m) < 200:
            snippets.append(m)

    # 提取中文单引号包裹的代码: 'code'
    cn_quote_matches = re.findall(r'[\u2018\u2019]([^\u2018\u2019]+)[\u2018\u2019]', description)
    for m in cn_quote_matches:
        m = m.strip()
        # 包含代码特征的才保留（有 = ; () . 等符号）
        if 3 < len(m) < 200 and re.search(r'[=;().\[\]{}]', m):
            snippets.append(m)

    # 提取英文单引号包裹的代码: 'code'
    en_single_matches = re.findall(r"'([^']+)'", description)
    for m in en_single_matches:
        m = m.strip()
        if 3 < len(m) < 200 and re.search(r'[=;().\[\]{}]', m):
            snippets.append(m)

    # 提取双引号包裹的代码片段: "xxx()"
    quote_matches = re.findall(r'"([^"]*[=;().\[\]{}][^"]*)"', description)
    for m in quote_matches:
        m = m.strip()
        if 3 < len(m) < 200:
            snippets.append(m)

    return snippets[:3]  # 最多取3个


def calculate_match_score(code_line, keywords):
    """
    计算代码行与关键词的匹配度

    Returns:
        int: 匹配分数
    """
    score = 0

    for kw_type, kw_value in keywords:
        if kw_type == 'method':
            pattern = r'\b' + re.escape(kw_value) + r'\s*\('
            if re.search(pattern, code_line):
                score += 3

        elif kw_type == 'var':
            pattern = r'\b' + re.escape(kw_value) + r'\b'
            matches = re.findall(pattern, code_line)
            score += len(matches)

        elif kw_type == 'code':
            if re.search(kw_value, code_line):
                score += 5

    return score


def keyword_fallback_search(diff_content, description, current_line):
    """
    关键词 fallback 搜索：当 problem_code 匹配失败时，
    用描述中的关键词在 diff 的上下文行中搜索最佳匹配行。

    Args:
        diff_content: diff 内容
        description: 风险描述
        current_line: AI 给出的行号（作为参考距离）

    Returns:
        tuple: (line_number, confidence) 或 (None, 'none')
    """
    keywords = extract_keywords(description)
    if not keywords:
        return None, 'none'

    # 解析 hunk
    hunk_pattern = re.compile(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@.*$', re.MULTILINE)
    hunks = list(hunk_pattern.finditer(diff_content))

    if not hunks:
        return None, 'none'

    candidates = []  # (line_num, score)

    for i, hunk_match in enumerate(hunks):
        new_start = int(hunk_match.group(3))
        start_pos = hunk_match.end()
        end_pos = hunks[i + 1].start() if i + 1 < len(hunks) else len(diff_content)
        hunk_content = diff_content[start_pos:end_pos]
        hunk_lines = hunk_content.split('\n')

        new_line_num = new_start
        for line in hunk_lines:
            if line.startswith('+') or line.startswith(' '):
                code_content = line[1:].strip()
                score = calculate_match_score(code_content, keywords)
                if score > 0:
                    candidates.append((new_line_num, score))
                new_line_num += 1
            elif line.startswith('-'):
                pass  # 删除行不计数

    if not candidates:
        return None, 'none'

    # 按分数降序，同分时选离 current_line 最近的
    candidates.sort(key=lambda x: (-x[1], abs(x[0] - (current_line or 0))))
    best_line, best_score = candidates[0]

    # 关键词匹配置信度为 low
    confidence = 'low'
    return best_line, confidence


def find_line_in_diff_new(file_path, diffs, risk_description, problem_code=None, current_line=None):
    """
    在diff的new版本中查找风险描述对应的行号

    优先级：
    1. problem_code 精确匹配（整行 ==）
    2. problem_code 子串匹配（snippet in code）
    3. 从 description 提取代码片段再匹配
    4. 关键词 fallback 搜索

    Args:
        file_path: 文件路径
        diffs: coordinator中的diffs列表
        risk_description: 风险描述
        problem_code: AI输出的问题代码片段（可选）
        current_line: AI给出的行号（用于多匹配时选择最近行号）

    Returns:
        tuple: (line_number, confidence, method)
        - line_number: 计算出的行号，如果无法确定则返回None
        - confidence: 'high', 'medium', 'low', 'none'
        - method: 'precise_exact', 'precise_contains', 'description_extract', 'keyword_fallback', 'manual'
    """
    json_data = {"diffs": diffs}
    diff_content = find_diff_for_file(json_data, file_path)
    if not diff_content:
        return None, 'none', 'manual'

    # Step 1: problem_code 匹配（优先）
    if problem_code and problem_code.strip():
        matches = find_code_line_numbers(diff_content, problem_code, prefer_line=current_line)
        if matches:
            line_num, match_type = matches[0]
            if match_type == 'exact':
                return line_num, 'high', 'precise_exact'
            else:
                return line_num, 'medium', 'precise_contains'

    # Step 2: 从 description 中提取代码片段再匹配
    desc_snippets = extract_code_from_description(risk_description)
    for snippet in desc_snippets:
        matches = find_code_line_numbers(diff_content, snippet, prefer_line=current_line)
        if matches:
            line_num, match_type = matches[0]
            confidence = 'medium' if match_type == 'exact' else 'low'
            return line_num, confidence, 'description_extract'

    # Step 3: 关键词 fallback 搜索
    fallback_line, fallback_conf = keyword_fallback_search(
        diff_content, risk_description, current_line
    )
    if fallback_line is not None:
        return fallback_line, fallback_conf, 'keyword_fallback'

    # Step 4: 全部失败，返回 None
    return None, 'none', 'manual'


def check_and_fix_line_numbers(mr_info_file, risks_file, force=False):
    """
    校验并修正mr_risks.json中的行号

    Returns:
        tuple: (success: bool, message: str, fixed_count: int, needs_manual_check: list)
    """
    with open(mr_info_file, 'r', encoding='utf-8') as f:
        coordinator = json.load(f)

    with open(risks_file, 'r', encoding='utf-8') as f:
        risks_data = json.load(f)

    diffs = coordinator.get('diffs', [])
    risks = risks_data.get('risks', [])

    fixed_count = 0
    needs_manual_check = []
    fixed_risks = []

    for risk in risks:
        risk_id = risk.get('id')
        file_path = risk.get('file_path')
        current_line = risk.get('line_number')
        description = risk.get('description', '')
        problem = risk.get('problem', '')
        problem_code = risk.get('problem_code')

        new_line, confidence, method = find_line_in_diff_new(
            file_path, diffs, description, problem_code, current_line
        )

        if new_line is not None:
            # 匹配成功
            if new_line != current_line:
                print(f"[WARN] 风险{risk_id}: 行号需要修正 {current_line} -> {new_line} (置信度: {confidence}, 方法: {method})")
                print(f"       文件: {file_path}")
                print(f"       问题: {problem[:50]}...")
                risk['line_number'] = new_line
                fixed_count += 1
            else:
                print(f"[INFO] 风险{risk_id}: 行号正确 {current_line} (置信度: {confidence}, 方法: {method})")
            fixed_risks.append(risk)
        else:
            # 所有匹配方式均失败，使用原始行号
            print(f"[INFO] 风险{risk_id}: 保留原始行号 {current_line} (方法: {method})")
            needs_manual_check.append({
                'id': risk_id,
                'file_path': file_path,
                'current_line': current_line,
                'problem': problem
            })
            fixed_risks.append(risk)

    if fixed_count > 0 or needs_manual_check:
        with open(risks_file, 'w', encoding='utf-8') as f:
            json.dump(risks_data, f, ensure_ascii=False, indent=2)
        print(f"\n[INFO] 已更新mr_risks.json (修正{fixed_count}条, 需人工确认{len(needs_manual_check)}条)")

    if needs_manual_check:
        print(f"\n[WARN] 以下风险需要人工确认行号:")
        for item in needs_manual_check:
            print(f"  - 风险{item['id']}: {item['file_path']}:{item['current_line']}")

    return True, f"校验完成: 修正{fixed_count}条, 需人工确认{len(needs_manual_check)}条", fixed_count, needs_manual_check


def main():
    parser = argparse.ArgumentParser(description='行号校验与修正脚本')
    parser.add_argument('--mrInfoFile', required=True, help='mr_coordinator.json文件路径')
    parser.add_argument('--risksFile', required=True, help='mr_risks.json路径')
    parser.add_argument('--force', action='store_true', help='强制执行校验')

    args = parser.parse_args()

    success, message, fixed_count, needs_manual_check = check_and_fix_line_numbers(
        args.mrInfoFile,
        args.risksFile,
        args.force
    )

    print(f"\n[SUMMARY] {message}")

    if needs_manual_check:
        print("\n[MANUAL_CHECK_REQUIRED]")
        print("请AI介入确认以下风险的行号:")
        for item in needs_manual_check:
            print(f"  - 风险{item['id']}: {item['file_path']}:{item['current_line']}")
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
