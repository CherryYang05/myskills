#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
精确代码行号查找模块

基于 find_code_line_in_diff.py 实现精确字符串匹配，
在 diff 的 new 版本中查找代码片段的行号。

v2: 扩展搜索范围到上下文行，整行匹配优先，支持混合行类型多行匹配，支持空行匹配
"""

import re
from typing import List, Dict, Optional, Tuple


def find_diff_for_file(json_data: Dict, target_file: str) -> Optional[str]:
    """
    根据文件名找到对应的 diff 内容

    Args:
        json_data: coordinator.json 解析结果
        target_file: 文件路径

    Returns:
        diff 内容，未找到返回 None
    """
    diffs = json_data.get("diffs", [])

    for diff in diffs:
        new_path = diff.get("new_path", "")
        if target_file == new_path:
            return diff.get("diff", "")

    return None


def find_code_line_numbers(diff_content: str, code_snippet: str,
                           prefer_line: int = None) -> List[Tuple[int, str]]:
    """
    在 git diff 中找到目标代码在修改后文件中的行号。
    支持多行代码片段匹配，扩展搜索上下文行。

    Args:
        diff_content: git diff 的完整内容
        code_snippet: 要查找的目标代码（支持多行，\n 分隔）
        prefer_line: AI 建议的行号，多个匹配时优先选离此行最近的

    Returns:
        目标代码在修改后文件中的行号列表，每个元素为 (line_number, match_type)
        match_type: 'exact' (整行精确匹配) 或 'contains' (子串包含匹配)
    """
    results = []

    # 空片段直接返回
    if not code_snippet or not code_snippet.strip():
        return results

    # 解析 hunk 头部
    hunk_pattern = re.compile(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@.*$', re.MULTILINE)
    hunks = list(hunk_pattern.finditer(diff_content))

    if not hunks:
        return results

    # 多行处理：按 \n 分割代码片段
    snippet_lines = [line.strip() for line in code_snippet.strip().split('\n')]
    # 保留空行：AI 可能在 problem_code 中用 \n\n 表示 diff 中的新增空行
    # 例如 ".next = NULL,\n\n\n.attr_table = ..." 对应 diff 中间有2个空行
    snippet_len = len(snippet_lines)

    if snippet_len == 0:
        return results

    for i, hunk_match in enumerate(hunks):
        new_start = int(hunk_match.group(3))

        # 获取当前 hunk 的内容
        start_pos = hunk_match.end()
        end_pos = hunks[i + 1].start() if i + 1 < len(hunks) else len(diff_content)
        hunk_content = diff_content[start_pos:end_pos]

        hunk_lines = hunk_content.split('\n')

        # 预处理：为每行构建 (前缀, 去前缀strip后的内容, new行号)
        indexed_lines = []
        new_line_num = new_start
        for line in hunk_lines:
            if line.startswith('+'):
                indexed_lines.append(('+', line[1:].strip(), new_line_num))
                new_line_num += 1
            elif line.startswith(' '):
                indexed_lines.append((' ', line[1:].strip(), new_line_num))
                new_line_num += 1
            elif line.startswith('-'):
                # 删除行不出现在新文件中，但占据滑动窗口位置
                indexed_lines.append(('-', line[1:].strip(), None))
            else:
                # split('\n') 产生的空串或尾部空串，不是真实 diff 行，跳过不计数
                # 真正的空行在 diff 中表示为 ' '（单空格，上下文空行）或 '+'（新增空行）
                if line == '':
                    continue
                # 其他异常行也跳过
                pass

        def _match_snippet_line(snippet_line, diff_code):
            """
            匹配 snippet 的一行与 diff 行的 strip 后内容。
            snippet 空行只匹配 diff 空行；非空行精确/子串匹配。
            Returns: 'exact' | 'contains' | None(不匹配)
            """
            # snippet 空行：匹配 diff 中内容为空的行
            if snippet_line == '':
                return 'exact' if diff_code == '' else None
            # diff 空行：无法匹配非空 snippet
            if diff_code == '':
                return None
            # 精确匹配
            if snippet_line == diff_code:
                return 'exact'
            # 子串包含匹配
            if snippet_line in diff_code:
                return 'contains'
            return None

        # 滑动窗口匹配
        line_idx = 0
        while line_idx <= len(indexed_lines) - snippet_len:
            first = indexed_lines[line_idx]
            # 首行必须是 + 或 空格（新文件中存在的行）
            if first[0] not in ('+', ' '):
                line_idx += 1
                continue

            first_code = first[1]
            first_line_num = first[2]

            # 首行匹配
            first_match = _match_snippet_line(snippet_lines[0], first_code)
            if first_match is None:
                line_idx += 1
                continue

            # 单行 snippet
            if snippet_len == 1:
                results.append((first_line_num, first_match))
                line_idx += 1
                continue

            # 多行 snippet 匹配
            match = True
            all_match_type = first_match
            for j in range(1, snippet_len):
                next_idx = line_idx + j
                if next_idx >= len(indexed_lines):
                    match = False
                    break
                next_item = indexed_lines[next_idx]
                # 支持 + 行和上下文行（空格行）
                if next_item[0] not in ('+', ' '):
                    match = False
                    break
                next_code = next_item[1]
                next_match = _match_snippet_line(snippet_lines[j], next_code)
                if next_match is None:
                    match = False
                    break
                # 任一行是子串匹配则整体降级为 contains
                if next_match == 'contains':
                    all_match_type = 'contains'

            if match:
                results.append((first_line_num, all_match_type))

            line_idx += 1

    # 按 match_type 排序：exact 优先，contains 在后
    results.sort(key=lambda x: (0 if x[1] == 'exact' else 1, x[0]))

    # 如果有 prefer_line，优先选离它最近的匹配
    if prefer_line and len(results) > 1:
        best = min(results, key=lambda x: abs(x[0] - prefer_line))
        # 把最佳结果放最前
        results.remove(best)
        results.insert(0, best)

    return results


def find_code_line_numbers_simple(diff_content: str, code_snippet: str) -> List[int]:
    """
    兼容旧接口：只返回行号列表（不含 match_type）

    Args:
        diff_content: git diff 的完整内容
        code_snippet: 要查找的目标代码

    Returns:
        目标代码在修改后文件中的行号列表
    """
    results = find_code_line_numbers(diff_content, code_snippet)
    return [line_num for line_num, _ in results]


if __name__ == "__main__":
    import sys
    import json

    if len(sys.argv) < 4:
        print("用法: python precise_line_finder.py <json文件路径> <文件名> <代码片段> [偏好行号]")
        print("示例: python precise_line_finder.py mr_coordinator.json src/main.java 'import sys' 131")
        sys.exit(1)

    json_file_path = sys.argv[1]
    target_file = sys.argv[2]
    code_snippet = sys.argv[3]
    prefer_line = int(sys.argv[4]) if len(sys.argv) > 4 else None

    with open(json_file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    diff_content = find_diff_for_file(json_data, target_file)
    if diff_content is None:
        print(f"错误: 未找到文件 '{target_file}' 的 diff")
        sys.exit(1)

    result = find_code_line_numbers(diff_content, code_snippet, prefer_line)
    if result:
        for line_num, match_type in result:
            print(f"行号: {line_num} (匹配类型: {match_type})")
    else:
        print("未找到匹配的代码")
