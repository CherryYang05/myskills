---
name: develop-software
description: 为软件项目一次性初始化或重新校准 Agent 开发工作流。用于用户明确要求初始化新项目、为既有仓库搭建或固化开发 SOP、生成 AGENTS.md，或按项目实际需要配置 Spec、ADR、Plan、验证与文档结构时。把选定规则写入仓库供后续 Agent 直接遵循；不要用于普通功能开发、bug 修复、重构、测试或代码评审，也不要在每个需求中重复运行。
---

# Develop Software

把本 Skill 当作**项目工作流初始化器**，而不是所有软件任务都要经过的运行时 SOP：

> 项目事实与风险 → 选择必要模块 → 固化到仓库 → 后续 Agent 直接按仓库规则工作

一个项目通常只运行一次。只有项目阶段、团队协作、风险边界或治理需求发生实质变化时，才显式重新校准。

## 完成定义

初始化完成后应满足：

- 后续 Agent 不加载本 Skill，也能从仓库文件知道如何开发、验证和收尾；
- `AGENTS.md` 或仓库既有指令包含真实命令、source of truth、变更路由、风险规则与完成条件；
- 只创建项目确实需要的 Artifact、模板和检查，不生成整套空目录；
- 能机械判断的规则由 test、lint、CI、schema check 或脚本执行；
- 同一事实只有一个权威位置，项目不依赖某次聊天保存关键状态。

不要在这里实现业务 Feature。若用户同时要求初始化和开发，先完成可独立验收的工作流初始化，再按新写入的仓库规则处理开发任务。

## 1. 识别已有工作流

先读取并检查：

1. 当前目录适用的 `AGENTS.md`、`CLAUDE.md`、contributor guide 和其他 repository instructions；
2. `git status`、当前 diff 和用户已有改动；
3. README、roadmap、architecture、RFC/Spec、ADR、Plan、issue 模板和文档索引；
4. build、test、format、lint、type check、CI、hooks 和发布命令；
5. 代码中的真实模块边界、持久化状态、外部接口与高风险副作用。

若仓库已经有自洽工作流，不要再次铺设模板。只在用户明确要求重新校准时审计差距并做最小迁移。保留现有命名与目录，优先映射，不为符合本 Skill 的默认布局批量搬家。

只把仓库证据或用户明确说明的内容写成事实。不要猜测 owner、支持版本、用户、期限、质量目标或已接受决定；未知内容保留为 `draft`、assumption 或 Open question。

## 2. 建立项目画像

根据证据判断以下维度；只有缺失信息会实质改变选择时才提问：

- 项目是 spike、短期个人工具，还是长期维护的产品/基础设施；
- 单人还是多人/多 Agent 协作，工作是否跨 session、branch 或团队；
- 是否存在 public API、持久化数据、migration、外部写入或兼容承诺；
- security、privacy、concurrency、recovery、performance 和 release 风险；
- 是否需要审计、审批、稳定 ID、里程碑与可恢复的实施状态；
- 现有工具链能机械执行哪些规则。

不要用代码行数或“新项目”三个字直接推导重型流程。完整组合方法见 [lifecycle-and-routing.md](references/lifecycle-and-routing.md)。

## 3. 选择工作流模块

从下表组合最少必要集合，不把任一档位当作固定套餐：

| 模块 | 默认 | 选择条件 |
|---|---|---|
| Repository instructions | 必选 | 所有项目；优先完善已有文件 |
| 权威 build/test/static-check 命令 | 必选 | 有可执行代码的项目 |
| Project Brief | 按需 | 新的长期项目或大型 Epic 需要稳定总体边界 |
| Current System Design | 按需 | 模块、状态、部署或依赖边界不再显然 |
| Roadmap | 按需 | 存在多个可独立交付 outcome、依赖或 milestone |
| Feature Spec 与稳定 `F-NNNN` | 按需 | 行为契约需跨 session/协作者长期保持 |
| ADR | 按需 | 决策跨模块、代价高、难逆转或需要保留理由 |
| Implementation Plan | 按需 | 多纵向切片、长周期、高风险迁移或 rollout |
| Artifact validator | 按需 | 已采用稳定 ID/状态机，且机械校验收益高于维护成本 |
| CI / architecture guard | 按需强化 | 规则可机械化，或违规代价较高 |
| 执行器 wrapper | 按需 | 执行器不能直接读取权威 repository instructions |

风险可以升级某个模块，但不必升级整套流程。例如一个小项目出现不可逆 migration 时，可以只增加 ADR、迁移 Plan 和 recovery test，而不启用完整 Feature 编号体系。

## 4. 先给出选择清单

在写入前给用户一份简短清单：

```text
项目画像：
保留：
新增：
明确省略：
关键理由：
```

用户明确要求初始化或重新校准，已经授权安全、可逆且范围清楚的仓库内修改。仅在会覆盖现有权威内容、存在两个高代价方向、需要不可逆操作或目标仍有阻塞性歧义时暂停确认。

初始化授权不等于批准新写入的产品或架构语义。新 Project Brief、Feature Spec 与 ADR 默认保持 `draft` / `proposed`；只有用户已明确接受其实际内容时才迁移为 `accepted`。

## 5. 固化到仓库

### Repository instructions

以 [agents-template.md](assets/agents-template.md) 为素材，生成项目自包含的 `AGENTS.md` 或完善既有权威文件：

- 写入真实可执行的 build/test/lint/architecture 命令；
- 写入项目地图、架构不变量、风险边界与禁止操作；
- 写入适合该项目的日常变更路由和 Artifact 触发条件；
- 写入 Definition of Done、文档同步面与授权边界；
- 链接项目的 architecture、roadmap、Spec/ADR/Plan 索引。

不要让 `AGENTS.md` 要求普通任务再次调用 `develop-software`。不要把当前 Feature 进度或整套模板正文塞入其中。

### Docs 与 Artifact

只复制已选择模块的素材，并按项目删减模板字段：

- Project Brief：[project-brief-template.md](assets/project-brief-template.md)
- System Design：[system-design-template.md](assets/system-design-template.md)
- Roadmap：[roadmap-template.md](assets/roadmap-template.md)
- Feature Spec：[feature-spec-template.md](assets/feature-spec-template.md)
- ADR：[adr-template.md](assets/adr-template.md)
- Implementation Plan：[implementation-plan-template.md](assets/implementation-plan-template.md)

默认可使用 `docs/project/`、`docs/architecture/`、`docs/specs/`、`docs/adr/` 和 `docs/plans/`，但已有仓库约定优先。不要创建空 Spec、空 ADR、远期空 Plan 或没有 owner 的占位文档。

需要稳定 Artifact 状态时读取 [artifact-governance.md](references/artifact-governance.md)；需要架构护栏时读取 [architecture-and-coupling.md](references/architecture-and-coupling.md)；需要纵向切片和证据规则时分别读取 [planning-and-vertical-slices.md](references/planning-and-vertical-slices.md) 与 [verification-and-review.md](references/verification-and-review.md)。

### 机械规则与可移植性

- 将确定性规则接入项目自己的 test、lint、CI 或脚本，不只写在 prompt 中；
- 若启用 Artifact validator，将脚本复制或适配到仓库并写入权威验证命令，不让项目运行依赖本 Skill 的安装路径；
- 对只能读取 `CLAUDE.md` 的执行器，使用 [claude-wrapper-template.md](assets/claude-wrapper-template.md) 引用 `AGENTS.md`，不维护第二份 SOP；
- 不在 Global instructions 中配置“每个软件任务都调用本 Skill”。跨执行器规则见 [executor-portability.md](references/executor-portability.md)。

## 6. 验证初始化结果

至少检查：

1. 新增文件没有未替换占位符、空章节、断链或重复 source of truth；
2. `AGENTS.md` 足以让一个不了解本次对话的 Agent 找到权威上下文并执行常见任务；
3. 写入的命令确实存在；能安全运行时实际运行，不能运行时标明原因；
4. 选择的 Artifact 状态、ID 与关系可以自洽；启用 validator 时运行其测试和一次项目扫描；
5. wrapper、CI 和文档索引都指向同一套权威规则；
6. 普通 Feature、bug fix、refactor、test 或 review 不需要重新调用本 Skill。

## 7. 交付初始化结果

向用户报告：

1. 采用的项目工作流及选择理由；
2. 新增、修改和明确省略的模块；
3. 后续 Agent 从哪些仓库文件开始工作；
4. 实际运行的验证命令与结果；
5. 何种项目变化才需要再次运行本 Skill。

## Resource 路由

| 初始化决策 | 必读 Reference | 常用 Asset |
|---|---|---|
| 工作流裁剪、已有项目迁移、日常任务路由 | `lifecycle-and-routing.md` | `agents-template.md` |
| 启用 Feature/ADR/Plan 状态与稳定 ID | `artifact-governance.md` | 对应 Artifact 模板 |
| 建立系统边界、依赖方向或机械护栏 | `architecture-and-coupling.md` | `system-design-template.md` |
| 配置多切片或跨 session 计划 | `planning-and-vertical-slices.md` | `implementation-plan-template.md` |
| 配置验证矩阵、review 与 DoD | `verification-and-review.md` | `agents-template.md` |
| 配置文档同步、current/accepted/planned 分层 | `documentation-governance.md` | Project/Artifact 模板 |
| 接入 Codex、Claude Code 或其他执行器 | `executor-portability.md` | `agents-template.md`、wrapper |

不要一次性加载或复制所有资源。选择某个模块时才读取对应 Reference，并把必要规则改写为项目自己的、可长期维护的版本。

## 再次运行的边界

仅在以下情况显式重新运行：

- 新建独立项目或大型子系统；
- 项目从 spike 进入长期维护，或从单人进入多人/多 Agent 协作；
- public contract、数据、安全、发布或合规风险发生结构性变化；
- 现有 SOP 明显过轻、过重、互相冲突或已经漂移；
- 用户明确要求迁移、审计或重新裁剪工作流。

普通开发任务直接遵循初始化后写入仓库的规则。
