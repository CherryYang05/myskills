<!--
  AGENTS.md 模板 — P2 项目初始化产出
  用法：复制到仓库根目录的 AGENTS.md，删掉本注释，填充。
  铁律：只放【慢变】内容（命令/约定/架构不变量/目录地图）。
  绝不放：进度（done/doing/todo）、changelog、某功能的设计细节、临时笔记。
  软上限：≤ ~150 行。接近上限就 prune，或把详细内容移到 references/。
-->

# <项目名> — Agent 工作指南

一句话说明本项目是什么、给 Agent 的总体定位。

## 构建与测试

<!-- Agent 最常需要、最该一次写对的命令。带具体命令，不要"运行测试即可"这种废话。 -->
```bash
# 构建
<build command>
# 跑单元测试 / 集成测试
<unit test command>
<integration test command>
# 跑单个测试 / lint / 覆盖率
<...>
# 架构护栏（依赖方向机械检查，违反即失败）
<如 lint-imports / depcruise --validate / ArchUnit 测试>
```

## 代码约定

<!-- 命名规范、错误处理风格、禁止的模式、必须遵守的编码标准。 -->
<!-- 系统级项目：内存管理约定、并发原语、内存序要求。 -->
-
-

## 架构不变量

<!-- 来自 P1 系统设计文档，一旦确认极少变动。改这些之前必须先有 ADR。 -->
- 模块依赖方向：<例：上层依赖下层，禁止反向依赖>
- 禁止的依赖：<例：UI 层不得直接访问数据库>
-

## 目录地图

<!-- "东西在哪"。让 Agent 不用全仓扫描就知道去哪找。同时体现本项目的文件分类原则。 -->
<!-- 分类原则：feature-based（按功能） / layer-based（按技术层） / 混合，二选一，写明是哪种。 -->
```
docs/architecture/    # 系统设计文档（极慢变）
docs/requirements/    # 结构化需求（point-in-time）
docs/designs/         # 功能设计文档，含耦合评估（point-in-time）
docs/decisions/       # ADR，append-only
docs/tasks/           # 任务清单（ephemeral）
CHANGELOG.md          # append-only
src/<...>             # 分类原则：<feature-based | layer-based>，见下方说明
  <module>/           # 每个模块的对外接口 + 内部实现 + 对应测试
common/ or shared/    # 仅被依赖，不得反向依赖业务模块
```

## 工作流约定

<!-- 指向开发流程：新需求/功能怎么开，设计文档门槛，收尾要做什么。 -->
- 新需求/功能按本项目的 Agent 驱动开发 SOP 走：需求（EARS 验收标准）→（新项目需系统设计）→ 拆分 → 设计（够格才写，含耦合评估）→ 实现（测试先行，护栏/耦合自查）→ 测试与评审（单元+集成+设计符合性评审，AC 回链）→ 收尾。
- 进度看 docs/tasks/ 与 issue，不在本文件维护；历史看 CHANGELOG.md。

<!-- 详细内容（如完整编码规范、子系统深度说明）放 references/，本文件只留指针。 -->
