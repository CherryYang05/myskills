<!--
  ADR（Architecture Decision Record）模板 — 记录有长期影响的架构决策
  用法：复制到 docs/decisions/NNNN-<short-title>.md（NNNN 为递增序号），删掉本注释。
  铁律：ADR append-only，一旦写下不改。要改就写一条新 ADR，标 supersedes 指向旧的。
  这样历史永不丢失、文档永不臃肿。
  典型触发场景：打破系统设计里的依赖方向规则、引入新的跨模块依赖、重大技术选型变更。
-->

# NNNN. <决策标题：一句话，如"允许 payment 模块直接依赖 user 模块的只读接口">

Date: <YYYY-MM-DD>
Status: Accepted
<!-- Status: Proposed | Accepted | Superseded by NNNN | Deprecated -->

## Context

<!-- 什么背景下需要做这个决策？有哪些约束、压力、相关因素？客观陈述，不带结论。 -->
<!-- 若与系统设计的依赖方向规则冲突，说明冲突点和为什么现有规则不适用于本场景。 -->

## Decision

<!-- 我们决定做什么。明确、主动语态："我们将采用 X"。 -->

## Consequences

<!-- 这个决策带来的后果——好的和坏的都写。后续要承担什么、放弃了什么、引入了什么风险。 -->
<!-- 若这条 ADR 修改了架构不变量，同步更新 AGENTS.md 的"架构不变量"一节。 -->
<!-- 若这条 ADR 批准了新的依赖方向/跨模块依赖，同步更新依赖护栏工具的规则文件，否则护栏检查会持续失败。 -->
