# Complex Profile governance

## Contents

1. Artifact 职责
2. 稳定 ID
3. 状态机
4. 关系不变量
5. Vertical Slice 与证据
6. Agent 权限

## 1. Artifact 职责

| Artifact | 回答 | 不保存 |
|---|---|---|
| Project Brief | 为什么做、总体边界和成功标准 | Feature 进度 |
| Roadmap | 阶段、outcome、依赖和退出证据 | 需求正文和 task checkbox |
| Architecture | 当前系统如何分层和运行 | 每次历史取舍 |
| Feature Spec | 一个行为应该是什么 | 实现顺序和当前进度 |
| ADR | 为什么接受一个长期决定 | Feature 是否完成 |
| Implementation Plan | 如何按切片交付、当前做到哪里 | 重复的需求正文 |
| AGENTS.md | Agent 必须遵循什么 | 当前 Feature 进度 |
| Code/tests | 当前实现和可执行证据 | 未批准的未来意图 |

代码说明“现在发生什么”，accepted Spec 说明“应该发生什么”。两者冲突意味着工作未完成，不能静默选择一方。

## 2. 稳定 ID

- Feature：项目内唯一、单调递增、永不复用的 `F-NNNN`。
- ADR：独立命名空间 `ADR-NNNN`。
- Plan：`PLAN-F-NNNN`；同一 Feature 的旧 Plan 被保留并替代时使用 `PLAN-F-NNNN-R02`。
- 文件名以完整 ID 开头并使用小写 kebab-case slug。
- milestone、release、team 和 module 是字段，不编码进 Feature ID。
- withdrawn、rejected 或 superseded 的 ID 仍被占用。

## 3. 状态机

Feature：

```text
draft -> accepted -> implemented -> superseded
   \-> withdrawn
accepted -> draft       # implementation 前显式 reopen
```

ADR：

```text
proposed -> accepted -> superseded
        \-> rejected
```

Plan：

```text
draft -> active -> completed
               \-> abandoned
               \-> superseded
```

`accepted` 不等于 implemented，implemented 不等于 released。Accepted Spec/ADR 的语义变化需要 reopen 或 successor；终态 Plan 冻结。

## 4. 关系不变量

- Plan 必须引用存在的 Feature；进入 `active` 时 Feature 必须为 `accepted`。
- Plan `completed` 与 Feature `implemented` 在同一次关闭变更中保持一致。
- 每个 Feature 最多一个 active Plan；个人项目默认全仓最多一个主 active Plan，可在项目 `AGENTS.md` 明确放宽。
- Feature 可以引用多个 ADR；ADR accepted 不能充当 Feature progress。
- Roadmap 只链接 Feature 和 milestone，不复制 Spec status 或 Plan checkbox。
- `supersedes` 与 `superseded_by` 必须双向一致，不得成环。

## 5. Vertical Slice 与证据

每个 Plan slice 必须产生一个最小、端到端、可观察且可验证的行为，并记录：

- 关联 AC；
- 涉及的 contracts、interfaces、state 和 dependencies；
- targeted test 与 broader checks；
- verification command、expected result 和实际 evidence；
- rollback point 与 remaining work。

不要按“所有 model -> 所有 DAO -> 所有 service -> 最后测试”横向拆分。AC 与 evidence 是多对多关系；不要为了表格整齐伪造一对一映射。

## 6. Agent 权限

- Agent 可以在授权范围内创建 draft、维护 active Plan 和记录实际 evidence。
- 只有用户明确接受实际语义时，才能把 Spec/ADR 标为 accepted。
- 未运行验证、验证失败或关键证据缺失时，不得标记 implemented/completed。
- 不用删除历史 Artifact 代替 supersede。
- validator 只证明结构和关系，不证明设计正确或测试真实覆盖需求。
