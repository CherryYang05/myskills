# Artifact governance

## 1. Artifact 不是同一种事实

| Artifact | 它回答的问题 | Source of truth 内容 | 默认写语义 |
|---|---|---|---|
| Project Brief | 为什么做、总体边界是什么 | 项目问题、Goals、Non-goals、成功标准 | draft 时修改；accepted 后实质变化需重新接受或 supersede |
| System Design | 当前系统如何分层 | 当前边界、职责、依赖方向、关键质量属性 | 慢变 current-state；原因由 ADR 保存 |
| Feature Spec | 某个行为应该是什么 | 场景、要求、失败语义、AC | 按状态机管理 |
| ADR | 为什么选择这个长期决定 | 选项、决定、后果、适用边界 | proposed 可改；accepted 后冻结语义 |
| Implementation Plan | 当前如何交付 Feature | slices、进度、验证、回滚点 | draft/active 是 living state；终态冻结 |
| Roadmap | 何时做、先后关系是什么 | milestone 与稳定 Feature 的映射 | 原地更新，不复制实现进度 |
| AGENTS.md | Agent 在本仓库必须遵守什么 | 项目命令、局部不变量、风险和验证要求 | 小而稳，直接修正并定期 prune |
| Code/tests/generated refs | 当前实现究竟是什么 | 可执行行为、schema、CLI/API | 由实现和自动化生成维护 |
| Release notes | 用户拿到了什么 | 已发布的用户可见变化 | 按项目 release policy append |

Source of truth 不是一条全局优先级链。代码说明“现在发生什么”，accepted Spec 说明“应该发生什么”；冲突表示工作未完成，不能静默选择一方。

## 2. 稳定 ID

- Feature 使用项目内唯一、单调分配且永不复用的 `F-NNNN`。
- 文件名以完整 ID 开头：`F-NNNN-<slug>.md`。
- milestone、release、team、module 是独立字段；移动它们不得重编号。
- ADR 使用独立命名空间 `ADR-NNNN`。
- 首个 Plan 推荐 `PLAN-F-NNNN-<slug>.md`，通过 `related_feature` 关联 Feature。
- 同一 Feature 的旧 Plan 需要保留并被替代时，后继 Plan 使用 revision，
  例如 `PLAN-F-0001-R02-<slug>.md`；revision 不是 Feature 版本。
- 被取消或 superseded 的 ID 仍然占用，避免历史链接指向新含义。

## 3. 状态机

### Feature Spec

```text
draft ──> accepted ──> implemented ──> superseded
draft ──> withdrawn
accepted ──> draft       (implementation 前显式 reopen)
accepted ──> withdrawn | superseded
```

- `draft`：可实质编辑，开放问题允许存在。
- `accepted`：行为契约和范围已批准；不表示代码存在。
- `implemented`：DoD 和 AC evidence 满足；不表示已发布。
- `superseded`：由 `superseded_by` 指向后继 Feature。
- `withdrawn`：不会继续交付，保留原因。

Accepted 后只允许非语义修正（拼写、链接、澄清不改变契约）。实质改变应明确 reopen 为 draft 并重新批准，或在已有实现/外部依赖时创建后继 Feature。

### ADR

```text
proposed ──> accepted ──> superseded
        └──> rejected
```

ADR 没有 `implemented`。`accepted` 只说明决策生效。Accepted 后允许修复拼写和失效链接；改变 Decision、Drivers 或 Consequences 时创建新 ADR supersede。

### Implementation Plan

```text
draft ──> active ──> completed
                ├──> abandoned
                └──> superseded
```

- 每个 Feature 默认最多一个 `active` Plan；项目可以在 Repository `AGENTS.md` 进一步限制全仓 WIP。
- `completed` 要求所有必须 slice 有证据，不能靠改状态隐藏未完成 checkbox。
- 终态 Plan 冻结；后续工作创建新 Plan 或 Feature。
- 只有交付策略变化但 Feature 行为契约未变时才创建 Plan revision；行为变化应创建后继 Feature。

## 4. 关系不变量

- Plan 必须引用存在的 Feature；进入 `active` 时 Feature 必须是 `accepted`。
- Plan `completed` 与 Feature `implemented` 应在同一关闭变更中保持一致。
- Feature 可以引用多个 ADR；ADR accepted 不能作为 Feature progress。
- Roadmap 只保存 milestone 映射，不重复 Spec status 或 slice checkbox。
- `superseded_by` 必须指向真实 Artifact，并与后继的 `supersedes` 双向一致，且不能形成环。
- 同一事实只维护一个手写权威位置；其他位置使用链接或生成内容。

## 5. 默认目录与迁移

默认：

```text
docs/project/project-brief.md
docs/architecture/system-design.md
docs/specs/F-NNNN-<slug>.md
docs/adr/ADR-NNNN-<slug>.md
docs/plans/PLAN-F-NNNN-<slug>.md
```

目录不是协议。已有仓库可保留 `rfcs/`、`decisions/` 或 issue tracker，只要能表达稳定 ID、状态、关系和 source of truth。不要仅为符合默认目录批量搬迁历史链接。

## 6. Agent 修改权限

- Agent 可以在已有授权范围内创建 draft、维护 active Plan 和记录 evidence。
- `accepted` 应代表真实项目决策。若用户已明确授权清晰方案，可直接迁移；否则请求所有者确认。
- Agent 不得在验证失败、未运行或证据缺失时把 Spec 标为 `implemented`。
- Agent 不得用删除旧 Artifact 代替 `superseded`，除非内容从未被接受且确认无历史价值。
