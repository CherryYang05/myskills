<!--
  AGENTS.md 模板 — P1 项目初始化产出
  用法:复制到仓库根目录的 AGENTS.md,删掉本注释,填充。
  铁律:只放【慢变】内容(命令/约定/不变量/目录地图)。
  绝不放:进度(done/doing/todo)、changelog、某功能的设计细节、临时笔记。
  软上限:≤ ~150 行。接近上限就 prune,或把详细内容移到 references/。
-->

# <项目名> — Agent 工作指南

一句话说明本项目是什么、给 Agent 的总体定位。

## 构建与测试

<!-- Agent 最常需要、最该一次写对的命令。带具体命令,不要"运行测试即可"这种废话。 -->
```bash
# 构建
<build command>
# 跑测试
<test command>
# 跑单个测试 / lint / 覆盖率
<...>
```

## 代码约定

<!-- 命名规范、错误处理风格、禁止的模式、必须遵守的编码标准。 -->
<!-- 系统级项目:内存管理约定、并发原语、内存序要求、对齐 MISRA/GJB 之类的标准。 -->
- 
- 

## 架构不变量

<!-- 不能违反的核心约束。改这些之前必须先有 ADR / 设计文档。 -->
- 
- 

## 目录地图

<!-- "东西在哪"。让 Agent 不用全仓扫描就知道去哪找。 -->
```
src/<...>            # 
include/<...>        # 
docs/requirements/   # 结构化需求(point-in-time)
docs/designs/        # 每功能一篇设计文档(point-in-time)
docs/decisions/      # ADR,append-only
docs/tasks/          # 任务清单(ephemeral)
CHANGELOG.md         # append-only
```

## 工作流约定

<!-- 指向开发流程:新需求/功能怎么开,设计文档门槛,收尾要做什么。 -->
- 新需求/功能按 skill-dev-flow 流程走:需求 → 拆分 → 设计(够格才写)→ 实现 → 收尾。
- 进度看 docs/tasks/ 与 issue,不在本文件维护;历史看 CHANGELOG.md。

<!-- 详细内容(如完整编码规范、子系统深度说明)放 references/,本文件只留指针。 -->
