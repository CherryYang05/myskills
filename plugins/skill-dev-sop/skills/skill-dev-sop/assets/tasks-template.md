<!--
  任务清单模板 — P4/P5 使用
  用法：复制到 docs/tasks/<feature-slug>.md，删掉本注释。
  这是 ephemeral 区：放心勾选、增删、重写，不用心疼。完成后可删或归档。
  作用是把"进度"从设计文档和 AGENTS.md 里隔离出来，避免污染慢变文档。
-->

# Tasks — <功能名称>

关联设计：docs/designs/<feature-slug>.md

## 待办

<!-- 颗粒度：每条是一个可独立完成、可验证的步骤。太粗拆开，太细合并。 -->
<!-- 每条 task 标注它服务的验收标准编号 [AC-n]，保证 AC ↔ task ↔ 测试可机械对账。 -->
- [ ] 测试先行：从 AC + Failure Modes 生成会失败的测试骨架 [AC-*]
- [ ] <task> [AC-n]
- [ ]

## 单元测试

<!-- 对应 design doc 的 Failure Modes 和 Acceptance Criteria 的核心路径。 -->
- [ ] 核心路径覆盖：<...> [AC-n]
- [ ] 边界/失败路径覆盖：<对应 design 的 Failure Modes> [AC-n]
- [ ] Mock 仅覆盖模块边界之外的依赖（外部 API/数据库），未 mock 被测模块内部实现

## 集成测试

<!-- 对应系统设计里的关键跨模块流程，以及本功能标注"跨模块影响"的部分。 -->
- [ ] 跨模块流程：<...>
- [ ] 契约测试：<被多方依赖的接口/协议>

## 耦合自查（P5）

<!-- 优先跑依赖护栏工具；详细人工清单见 assets/coupling-checklist.md。 -->
- [ ] 依赖护栏工具通过（无护栏项目：已过 coupling-checklist），无未解决的依赖方向/循环依赖问题

## 设计符合性评审（P6）

- [ ] 已用全新上下文(subagent)对照 design doc 审过 diff，无偏离设计/范围蔓延问题
- [ ] 按 AC 编号逐条回链测试结果，全部通过

## 收尾（P7，完成后逐项做）

- [ ] design doc Status → Implemented
- [ ] CHANGELOG.md append 一行（做了什么 + 关联 design/req）
- [ ] 若引入新稳定约定/命令/目录，精简更新 AGENTS.md
- [ ] 依赖图复查：跑依赖护栏工具（无护栏项目人工复查），无未经批准的新跨模块依赖
- [ ] 清理本 tasks 文件 / 清空 .agent-scratch
