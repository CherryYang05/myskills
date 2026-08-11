---
name: develop-software
description: 按风险分级执行通用软件工程生命周期，包括任务路由、稳定 Feature ID、Spec/ADR/Plan 状态机、Vertical Slice、架构与耦合护栏、证据驱动验证和文档治理。用于新项目、架构级变更、非平凡 Feature、bug fix、refactor、migration、implementation planning、testing、code review 或工程收尾；小改动走轻量路径，高风险改动采用匹配风险的 Artifact 与 Gate。适用于 Python、C++、Rust、TypeScript 等技术栈，以及 Codex、ChatGPT、Claude Code 或其他 coding agent。
---

# Develop Software

按风险而不是代码行数决定流程成本。核心路径是：

> 路由任务 → 选择最少必要 Artifact → 纵向切片实现 → 用实际证据关闭

不要为了展示流程而创建文档，也不要因改动很小就忽略安全、持久化、并发或公共契约风险。

## 执行合同

- 先读取当前目录适用的 `AGENTS.md`、`CLAUDE.md` 或其他 repository instructions。
- 以仓库中的代码、测试、生成物和已接受 Artifact 判断项目事实；聊天记录只提供意图，不是 source of truth。
- 保留用户已有改动。先检查 status 和 diff，只修改当前任务范围内的文件。
- 使用仓库现有的语言、目录、命令和文档约定；没有约定时再采用本 Skill 的默认值。
- Artifact 使用仓库主要文档语言；技术术语、命令、ID 和文件名保持原文。
- 只报告实际运行过的验证。无法运行时说明原因、未验证范围和风险，不得写成“已通过”。
- 多 Agent、worktree、hooks 和特定 IDE 都是可选执行手段，不是完成条件。

## 第一步：发现并路由

每次任务先做最小 discovery：

1. 读取项目指令、仓库状态和当前 diff。
2. 找到相关架构、Feature Spec、ADR、active Plan、roadmap、代码和测试。
3. 核对当前行为、目标行为、风险边界与未知项。
4. 判定 lane，简短告知用户路径后继续；只有阻塞性问题才暂停等待。

| Lane | 典型信号 | 默认路径 | 默认 Artifact |
|---|---|---|---|
| **Small / Mechanical** | typo、格式、局部 bug、行为不变的机械重构，解法明确且风险局部 | R0 → P5 → P6-lite → P7-lite | 不新建 Spec/ADR/Plan；bug 应补匹配风险的回归证据 |
| **Feature** | 新的可观察行为、非显然取舍、多个文件或模块、公共接口变化 | R0 → P0-lite → P4 → P5 → P6 → P7 | `F-NNNN` Feature Spec；满足 Plan 门槛时增加 Implementation Plan |
| **Architecture / New Project** | 新项目、系统边界或依赖方向变化、跨模块高代价决策 | R0 → P0 → P1 → P2 → P3 → P4 → P5 → P6 → P7 | Project Brief、System Design、Feature Specs；必要 ADR 和 Plans |

以下任一项出现时，不得仅因 diff 小而留在 Small lane：

- security / trust boundary、privacy、secrets 或权限；
- persistence schema、migration、数据丢失或 recovery；
- external side effect、重试、幂等或不可逆操作；
- public API / protocol / file format / backward compatibility；
- concurrency、consistency、memory ordering 或资源上限；
- 新 production dependency、架构边界或依赖方向例外。

完整判定和升降级规则见 [lifecycle-and-routing.md](references/lifecycle-and-routing.md)。

## Checkpoint 与授权

不要把“每个 Phase 都等确认”当成流程正确性。仅在以下情况暂停：

- 目标、范围或验收标准存在会改变实现方向的歧义；
- 需要用户在多个高代价方案中做取舍；
- 操作不可逆、超出已有授权或会影响外部系统；
- Spec/ADR 的 `accepted` 需要项目所有者批准，且当前请求没有明确授权；
- 仓库状态、权限或失败使继续执行不安全。

若用户已经明确批准一个范围清楚的实现，可以在解决开放问题后完成相应 Gate，不重复索取形式化确认。

## 生命周期

| Phase | 目的 | 何时执行 | Gate |
|---|---|---|---|
| **R0 Route & Discover** | 建立仓库事实，选择 lane | 每次 | 当前行为、范围和风险有证据 |
| **P0 Frame** | 定义问题、Goals、Non-goals、Acceptance Criteria | Feature / Architecture；Small 仅口头或 issue 级 | 成功条件可判断 |
| **P1 Architect** | 定义当前系统边界、依赖方向和关键质量属性 | 新项目或架构级变化 | 边界与不变量明确；高代价决定有 ADR |
| **P2 Bootstrap Controls** | 补齐 build/test/lint/CI/architecture guard 和项目指令 | 新项目，或既有项目缺少必要基线时按需 | 关键规则有可执行命令；能机械化的已落到工具 |
| **P3 Shape Work** | 建立稳定 Feature、依赖关系和交付顺序 | 新项目、大型 Epic | Feature 边界可独立验收，ID 与 milestone 解耦；不为远期 backlog 预建空 Plan |
| **P4 Specify, Decide & Plan** | 接受行为契约、必要决策和纵向切片 | Feature / Architecture | Spec accepted；相关 ADR accepted；Plan 可执行 |
| **P5 Execute Slices** | 一次实现一个可观察、可验证切片 | 有实现工作时 | 每个完成切片有命令、结果和 rollback point |
| **P6 Verify & Review** | 用 AC evidence、风险测试、架构检查和 diff review 找问题 | 所有代码变化 | 必要证据已实际运行，无未解决阻塞问题 |
| **P7 Close & Compact** | 迁移状态、同步当前事实、清理临时状态 | 所有任务 | DoD 满足，剩余工作和限制准确 |

`P2` 是一次性或按需工程基线，不是每个 Feature 都重复执行。不要为了保留编号强制经过无关 Phase。

## Artifact 选择

### Project Brief

仅用于新项目或大型 Epic，定义项目问题、总体范围和成功条件。复制 [project-brief-template.md](assets/project-brief-template.md)。

### System Design

描述**当前**系统边界、模块职责、依赖方向和机械护栏。它是慢变 current-state 文档，不是冻结的历史快照。复制 [system-design-template.md](assets/system-design-template.md)，重大变化通过 ADR 保留原因，再同步正文。

### Feature Spec

每个非平凡可观察行为使用稳定 `F-NNNN`。ID 在项目内唯一、不得复用，与 milestone/release 解耦；Feature 移动 milestone 时只修改属性，不重编号。复制 [feature-spec-template.md](assets/feature-spec-template.md)。

### ADR

只记录跨模块、影响长期边界、代价高或难以逆转的决定。不要把 ADR 当开发日记。复制 [adr-template.md](assets/adr-template.md)。

### Implementation Plan

当实现包含多个独立切片、跨边界迁移、并行/长周期工作或高风险 rollout 时创建。单一、短小且可一次验证的 Feature 可省略独立 Plan，但仍须在 Spec/issue 中写明验证和回滚。复制 [implementation-plan-template.md](assets/implementation-plan-template.md)。

只为已选入近期实施、Spec 已进入实质定义的 Feature 创建 Plan；Roadmap backlog 只登记稳定 ID、outcome 和依赖，不批量生成空 Spec/Plan。

状态、关系和 source-of-truth 规则见 [artifact-governance.md](references/artifact-governance.md)。

## 实现规则

### Small / Mechanical

1. 证明范围确实局部；bug 先建立能复现问题的证据。
2. 做最小改动，避免顺手重构。
3. 运行最窄相关测试，再运行项目要求的 lint/type/architecture checks。
4. 只在可观察行为、用户文档或 release policy 要求时更新文档/CHANGELOG。
5. 报告 observable result、验证和剩余风险。

### Feature / Architecture

1. 先完成并接受 Spec；需要 ADR 时先决定，不用代码暗中替代决策。
2. 需要 Plan 时按最小端到端 observable behavior 拆分，不按 `model → DAO → service → API → test` 横向铺开。
3. 每个 slice 明确 behavior、contracts、interfaces/adapters、state/persistence、tests/evidence、verification command、expected result 和 rollback point。
4. 优先 test-first；探索、characterization 或难以自动化的场景允许先调查，但关闭前必须补齐风险匹配的证据。
5. 发现 Spec 缺口、架构例外或风险升级时，停止当前 slice，更新相应 Artifact 并重新过 Gate。
6. 逐条建立 `AC → Evidence` 映射。映射允许多对多，不伪造“一条 AC 对一个测试”的形式关系。

切片方法见 [planning-and-vertical-slices.md](references/planning-and-vertical-slices.md)。验证与 review 见 [verification-and-review.md](references/verification-and-review.md)。

## 架构与机械护栏

按以下链路治理耦合：

> System Design → dependency direction → architecture invariant → machine-enforceable guard → Feature coupling assessment → implementation check → review

优先使用项目栈适配的 import/dependency lint、architecture test、schema compatibility test、CI 或 hooks；Agent 指令只能指导，不能代替强制层。选择原则和示例见 [architecture-and-coupling.md](references/architecture-and-coupling.md)。

## 关闭条件

关闭 Feature 前必须回答：

- Acceptance Criteria 是否满足，证据在哪里？
- Implementation 和所有必须 slice 是否完成？
- Relevant tests/checks 是否实际运行并通过？
- Spec、ADR、System Design、生成物与代码是否一致？
- 用户文档、运维文档、migration/release notes 是否需要同步？
- Verification commands、observable result 和 known limitations 是什么？
- Plan 是否准确反映未完成工作？

只有以上条件成立，才能把 Plan 标为 `completed`、Feature 标为 `implemented`。`ADR accepted`、`code written`、`tests passed`、`Feature implemented` 和 `released` 是不同事实，不得互相替代。

文档更新、supersede 与 compaction 规则见 [documentation-governance.md](references/documentation-governance.md)。

## Resource 路由

| 当前任务 | 必读 Reference | 常用 Asset |
|---|---|---|
| 路由、Phase、旧项目接入 | `lifecycle-and-routing.md` | `project-brief-template.md` |
| 创建/迁移 Spec、ADR、Plan | `artifact-governance.md` | 对应三个模板 |
| 新项目、边界、依赖或 cross-cutting 风险 | `architecture-and-coupling.md` | `system-design-template.md`、`agents-template.md` |
| 规划或执行多个切片 | `planning-and-vertical-slices.md` | `implementation-plan-template.md` |
| 测试、验收、review、DoD | `verification-and-review.md` | Plan 的 Final verification |
| 文档同步、漂移、归档、收尾 | `documentation-governance.md` | 各 Artifact 状态字段 |
| Global/Repository 指令或跨执行器接入 | `executor-portability.md` | `agents-template.md`、`claude-wrapper-template.md` |

不要一次性读取所有 references；只加载当前决策需要的文件。

## 机械验证 Artifact

项目采用默认目录时运行：

```bash
python3 <skill-dir>/scripts/validate_artifacts.py <project-root> --strict-sections
```

自定义目录时使用 `--spec-dir`、`--adr-dir`、`--plan-dir`。脚本只检查 ID、Front Matter、状态、关系、active Plan 唯一性和 completed Plan 完整性；它不能判断设计质量，也不能证明测试真的覆盖 AC。

## 最终交付格式

向用户返回：

1. 完成的 observable outcome；
2. 创建或迁移的 Artifact 与状态；
3. 实际运行的命令和结果；
4. 未完成工作、无法验证项和 known limitations；
5. 若有，下一项最小可执行工作。
