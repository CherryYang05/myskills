#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR Rules Reader - 从 coordinator.json 读取已加载的规则，支持按批次输出

用于规则分批检视：当规则数量较多时，将规则分成多个批次，
每个 subagent 只加载一个批次的规则，避免超出 Token 上下文限制。
同时支持规则初筛阶段的数据读取与动态过滤。
"""

import argparse
import json
import re
import sys
from pathlib import Path

# 每批默认最大规则数（可通过 config.json 的 max_rules_per_batch 覆盖）
DEFAULT_MAX_RULES_PER_BATCH = 25

# 规则 category 分组优先级（用于分批排序）
CATEGORY_ORDER = [
    "COM",    # 通用规则优先
    "SEC",    # 安全
    "CON",    # 并发
    "CODE",   # 代码规范
    "PERF",   # 性能
    "ARCH",   # 架构
]


def get_coordinator_path(repo_name, mr_id):
    """根据repo和mrId获取coordinator文件路径"""
    temp_dir = Path.home() / ".mr-reviewer" / "temp"
    safe_repo_name = repo_name.replace('/', '_')
    coordinator_path = temp_dir / f"mr_{safe_repo_name}_{mr_id}" / "mr_coordinator.json"
    return coordinator_path


def read_coordinator(repo_name, mr_id):
    """读取coordinator.json"""
    coordinator_path = get_coordinator_path(repo_name, mr_id)
    try:
        with open(coordinator_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] coordinator文件不存在: {coordinator_path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON解析失败: {e}", file=sys.stderr)
        sys.exit(1)


def parse_rule_blocks(all_rules_combined):
    """解析 all_rules_combined 字符串，按 ### RULE-ID 锚点拆分为独立的规则块"""
    if not all_rules_combined:
        return []

    pattern = r'###\s+([A-Z]+(?:_[A-Z]+)?(?:-[A-Z]+)*-\d+):\s*.+'
    blocks = []
    matches = list(re.finditer(pattern, all_rules_combined))

    for i, match in enumerate(matches):
        rule_id = match.group(1).strip()
        block_start = match.start()

        if i + 1 < len(matches):
            block_end = matches[i + 1].start()
        else:
            block_end = len(all_rules_combined)

        content = all_rules_combined[block_start:block_end].rstrip()

        # 提取 category
        category_match = re.match(r'([A-Z_]+(?:-[A-Z]+)?)-\d+', rule_id)
        category = category_match.group(1) if category_match else rule_id

        blocks.append({
            "rule_id": rule_id,
            "category": category,
            "content": content,
        })

    return blocks


def get_category_sort_key(category):
    """获取 category 排序权重，未知的 category 排最后"""
    for cat in CATEGORY_ORDER:
        if cat in category:
            return CATEGORY_ORDER.index(cat)
    return len(CATEGORY_ORDER)


def get_max_rules_per_batch():
    """从 config.json 读取 max_rules_per_batch，未配置则使用默认值"""
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent / "common"))
        from config_manager import get_config_value
        value = get_config_value("max_rules_per_batch", DEFAULT_MAX_RULES_PER_BATCH)
        return int(value)
    except Exception:
        return DEFAULT_MAX_RULES_PER_BATCH


def generate_batch_plan(rule_ids, max_per_batch=None):
    """将 rule_ids 分成多批"""
    if max_per_batch is None:
        max_per_batch = get_max_rules_per_batch()

    if not rule_ids:
        # 必须返回1个空批次，防止 batch_count=0 导致大模型提示词失去判断分支
        return [{"batch_id": 1, "rule_ids": []}]

    category_groups = {}
    for rule_id in rule_ids:
        category_match = re.match(r'([A-Z_]+(?:-[A-Z]+)?)-\d+', rule_id)
        category = category_match.group(1) if category_match else "UNKNOWN"
        if category not in category_groups:
            category_groups[category] = []
        category_groups[category].append(rule_id)

    sorted_categories = sorted(category_groups.keys(), key=get_category_sort_key)
    batches = []
    current_batch = []
    batch_id = 1

    for category in sorted_categories:
        group = category_groups[category]
        if len(current_batch) + len(group) <= max_per_batch:
            current_batch.extend(group)
        else:
            if current_batch:
                batches.append({"batch_id": batch_id, "rule_ids": current_batch})
                batch_id += 1
                current_batch = []
            if len(group) <= max_per_batch:
                current_batch = list(group)
            else:
                for i in range(0, len(group), max_per_batch):
                    chunk = group[i:i + max_per_batch]
                    if current_batch and len(current_batch) + len(chunk) <= max_per_batch:
                        current_batch.extend(chunk)
                    else:
                        if current_batch:
                            batches.append({"batch_id": batch_id, "rule_ids": current_batch})
                            batch_id += 1
                        current_batch = list(chunk)

    if current_batch:
        batches.append({"batch_id": batch_id, "rule_ids": current_batch})

    return batches


def get_rules_content_for_batch(all_rules_combined, batch_rule_ids):
    """从 all_rules_combined 中提取指定 rule_ids 对应的规则 markdown 内容"""
    if not batch_rule_ids:
        return ""
    blocks = parse_rule_blocks(all_rules_combined)
    block_map = {b["rule_id"]: b["content"] for b in blocks}
    parts = []
    for rule_id in batch_rule_ids:
        content = block_map.get(rule_id)
        if content:
            parts.append(content)
    return "\n\n".join(parts)


# ==============================================================================
# 初筛功能相关工具函数 (硬匹配逻辑)
# ==============================================================================

def get_mr_search_text(coordinator):
    """从已加载的 coordinator 数据中拼接 MR Diff 文本，用于静态前置过滤"""
    text_parts = []
    try:
        for diff_item in coordinator.get('diffs', []):
            if diff_item.get('diff'):
                text_parts.append(diff_item.get('diff'))
        return '\n'.join(text_parts)
    except Exception as e:
        print(f"[WARN] 拼接搜索文本失败，将跳过前置过滤。原因: {e}", file=sys.stderr)
        return ""


def extract_code_tokens(checkpoint_str):
    """从锚点中提取纯代码特征，过滤掉无意义的短字母，并保留关键操作符"""
    tokens = []
    
    # 1. 提取英文、数字、下划线构成的词，或者带 % 的格式化占位符
    for t in re.findall(r'[a-zA-Z0-9_]+|%[a-zA-Z]', checkpoint_str):
        # 过滤掉双字母以内的泛词（如 if, as, to），保留占位符（如 %s）
        if len(t) > 2 or t.startswith('%'):
            tokens.append(t)
            
    # 2. 提取关键的代码操作符（原生正则会把这些过滤掉）
    operators = ['==', '!=', '===', '!==', '<<', '>>', '+=', '-=']
    for op in operators:
        if op in checkpoint_str:
            tokens.append(op)
            
    # 去重后返回
    return list(set(tokens))


def filter_rules_by_anchors(rule_ids, checkpoints_map, search_text):
    """基于智能提取的代码特征对规则进行硬匹配安全过滤"""
    if not search_text:
        return rule_ids

    filtered_ids = []
    search_text_lower = search_text.lower() # 提前转小写，优化非正则匹配性能

    for rule_id in rule_ids:
        cp_str = checkpoints_map.get(rule_id, "")
        if not cp_str:
            # 如果没有配置锚点，为了安全起见，默认放行
            filtered_ids.append(rule_id)
            continue
            
        tokens = extract_code_tokens(cp_str)
        if not tokens:
            # 如果提取不到有效 token，默认放行
            filtered_ids.append(rule_id)
            continue
            
        matched = False
        for token in tokens:
            if not token[0].isalnum():
                # 针对占位符 (%s) 或操作符 (==)，直接做简单的子串忽略大小写匹配
                if token.lower() in search_text_lower:
                    matched = True
                    break
            else:
                # 针对常规单词，使用词边界 \b 进行正则匹配，防止“子串误杀”（如 int 命中 print）
                # 开启 IGNORECASE 解决 SELECT vs select 的问题
                if re.search(r'\b' + re.escape(token) + r'\b', search_text, re.IGNORECASE):
                    matched = True
                    break
                    
        if matched:
            filtered_ids.append(rule_id)
            
    return filtered_ids

# ==============================================================================
# CLI 命令处理函数
# ==============================================================================

def cmd_prescreen_data(args):
    """处理 --prescreen-data 命令，输出硬匹配结果和待LLM初筛的锚点"""
    coordinator = read_coordinator(args.repo, args.mrId)
    rules_data = coordinator.get("rules", {})
    rule_ids = rules_data.get("rule_ids", [])
    checkpoints_map = rules_data.get("checkpoints", {})
    
    # 获取 diff 文本
    search_text = get_mr_search_text(coordinator)
    
    # 1. 脚本通过字面量精确硬匹配命中的规则
    hard_matched = filter_rules_by_anchors(rule_ids, checkpoints_map, search_text)
    
    # 2. 未命中的规则，抽取出来交给 LLM 做语义初筛
    pending_rules = [rid for rid in rule_ids if rid not in hard_matched]
    pending_checkpoints = {rid: checkpoints_map.get(rid, "") for rid in pending_rules}
    
    result = {
        "total_rules": len(rule_ids),
        "hard_matched_count": len(hard_matched),
        "pending_count": len(pending_rules),
        "hard_matched_rules": hard_matched,
        "pending_rules_to_llm": pending_checkpoints
    }
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_batch_plan(args):
    """处理 --batch-plan 命令"""
    coordinator = read_coordinator(args.repo, args.mrId)
    rules_data = coordinator.get("rules", {})
    rule_ids = rules_data.get("rule_ids", [])

    # 使用 is not None，这样即使传入空字符串 "" 也能被正确拦截
    if args.active_rules is not None:
        active_list = [r.strip() for r in args.active_rules.split(',') if r.strip()]
        # 求交集，保证顺位不变，并且过滤掉非法/捏造的 ID
        rule_ids = [r for r in rule_ids if r in active_list]

    batches = generate_batch_plan(rule_ids)
    max_per_batch = get_max_rules_per_batch()

    result = {
        "total_rules": len(rule_ids),
        "batch_count": len(batches),
        "max_rules_per_batch": max_per_batch,
        "batches": batches,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_batch_rules(args):
    """处理 --batch-id 命令"""
    coordinator = read_coordinator(args.repo, args.mrId)
    rules_data = coordinator.get("rules", {})
    all_rules_combined = rules_data.get("all_rules_combined", "")
    rule_ids = rules_data.get("rule_ids", [])

    if args.active_rules is not None:
        active_list = [r.strip() for r in args.active_rules.split(',') if r.strip()]
        rule_ids = [r for r in rule_ids if r in active_list]

    batches = generate_batch_plan(rule_ids)

    if args.batch_id < 1 or args.batch_id > len(batches):
        print(f"[ERROR] batch_id {args.batch_id} 超出范围 (1-{len(batches)})", file=sys.stderr)
        sys.exit(1)

    batch = batches[args.batch_id - 1]
    batch_rule_ids = batch["rule_ids"]

    content = get_rules_content_for_batch(all_rules_combined, batch_rule_ids)

    print(f"---RULES_BATCH_START---")
    print(f"Batch {args.batch_id}/{len(batches)}, Rules: {len(batch_rule_ids)}")
    print(f"Rule IDs: {', '.join(batch_rule_ids)}")
    print(f"---RULES_CONTENT---")
    print(content)
    print(f"---RULES_BATCH_END---")


def main():
    parser = argparse.ArgumentParser(
        description='MR Rules Reader - 从coordinator读取规则，支持分批输出及初筛支持'
    )
    parser.add_argument('--repo', required=True, help='仓库名称')
    parser.add_argument('--mrId', required=True, help='MR ID')
    
    parser.add_argument('--active-rules', type=str, 
                       help='逗号分隔的rule_id，指定需要分批的活跃规则池')

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--batch-plan', action='store_true',
                       help='输出分批计划（JSON格式，不含规则内容）')
    group.add_argument('--batch-id', type=int,
                       help='输出指定批次的规则内容（markdown）')
    group.add_argument('--prescreen-data', action='store_true',
                       help='输出初筛所需数据（硬匹配结果与待LLM兜底规则）')

    args = parser.parse_args()

    if args.batch_plan:
        cmd_batch_plan(args)
    elif args.batch_id is not None:
        cmd_batch_rules(args)
    elif args.prescreen_data:
        cmd_prescreen_data(args)


if __name__ == '__main__':
    main()