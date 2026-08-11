# Planning and vertical slices

## 1. Plan 与 checklist 的边界

- Feature Spec 定义要交付的行为与验收契约。
- ADR 定义高代价架构决定及理由。
- Implementation Plan 定义交付顺序、纵向切片、验证和回滚点。
- Task checklist 只是 slice 内部执行细节，可以重写、合并和删除。

不要把 requirements 复制到 Plan，也不要让一串 task 代替可工作的交付策略。

## 2. 独立 Plan 的门槛

满足任一条件时创建 Plan：

- 至少有两个能独立验证的交付切片；
- 跨模块、跨仓库或需要并行协调；
- 包含 schema/data migration、rollout 或兼容窗口；
- 包含高风险 security、recovery、concurrency 或 external side effect；
- 工作会跨多个 session/commit，必须可靠恢复上下文。

单一、短小、低风险的 Feature 可省略独立 Plan，但 Spec/issue 仍要记录实现范围、验证命令和 rollback。

不要为 Roadmap 中尚未选入近期实施的 Feature 预建 Plan。`draft` 表示正在形成真实交付策略，不表示“以后也许会做”的占位文件。

## 3. 什么是 Vertical Slice

一个 slice 必须产生最小端到端 observable behavior，并在完成时留下可运行、可验证的中间状态。它可以覆盖多个技术层，但只实现一个窄行为。

每个 slice 写清：

- **Observable behavior**：用户、调用方或运维者能看到什么；
- **Acceptance criteria**：关联哪些 `AC-n`；
- **Domain/contracts**：需要的稳定类型、规则或协议；
- **Interfaces/adapters**：哪些真实入口和边界被接通；
- **Persistence/state**：状态、migration 或明确 `N/A`；
- **Tests/evidence**：如何证明行为与风险；
- **Verification command + expected result**：完成时实际运行什么；
- **Rollback point**：如何退回上一个可工作状态；
- **Dependencies**：前置 slice、Feature 或 ADR。

错误拆法：

```text
1. 写完所有 model
2. 写完所有 DAO
3. 写完所有 service
4. 写完所有 API
5. 最后补测试
```

更好的拆法：

```text
1. 从真实入口创建一个最小对象，并能读取确认；先使用内存 adapter
2. 将同一行为接到持久化 adapter，并验证重启后的读取
3. 增加重复请求、超时和 migration 的失败语义
4. 增加 rollout 开关、可观测性和用户文档
```

第一个例子只是说明形态；不要机械要求每个项目先用内存实现。

## 4. Slice 大小

一个良好 slice 通常：

- 能在一次专注工作中完成；
- 只覆盖少量 AC 或一个完整场景；
- 不需要等待所有后续层才能验证；
- 失败时容易定位和回滚；
- 不引入尚未被下一步使用的抽象。

如果 slice 的 verification 只能写“运行完整项目看看”，继续缩小。如果每个 slice 只是“新增一个文件”，则是在伪装横向 task。

## 5. 执行循环

每次只推进下一个 ready slice：

1. 核对前置 Spec/ADR、当前代码和上一个 slice evidence；
2. 写或更新能够失败的测试/characterization，或说明为何先做受限 spike；
3. 实现满足当前 behavior 的最小改动；
4. 运行 targeted checks，再运行项目要求的 broader checks；
5. 记录命令、结果、observable evidence 和已知限制；
6. 更新 slice 状态，确保下一个 rollback point 清楚；
7. 若发现新决策或风险，停止并回到 P1/P4。

不要提前勾选后续 slice，也不要用“代码大致存在”代替从真实入口观察到行为。

## 6. Spike 与不确定性

Spike 是限时调查，不是隐形实现。创建前写明问题、时间/范围上限和退出判据。Spike 产物可以删除；若保留进入 production，必须重新按 Feature 的测试、架构和文档要求审查。

无法在计划阶段确定的细节写入 Open questions，不要用模糊 task（如“处理各种边界情况”）掩盖未知。

## 7. 并行与 WIP

只并行没有共享写热点、没有未决契约且验证相互独立的 slice。Feature 之间的并行上限由项目自己声明；通用 Skill 不强制“全仓只能一个 active Plan”。

多 Agent 的进度必须落到 Plan、代码和测试，不能只存在于各自对话。合并前重新运行共享边界和集成验证。
