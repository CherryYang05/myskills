# SDD Profiles

## Contents

1. 选择原则
2. Simple
3. Medium
4. Complex
5. 项目 Profile 与变更级别
6. 升档信号

## 1. 选择原则

根据维护和失败成本选择档位，不根据代码行数选择。优先采用能够控制真实风险的最低档。

| 信号 | Simple | Medium | Complex |
|---|---|---|---|
| 生命周期 | 原型、短期或低成本重写 | 长期维护、多个 release | 多阶段演进、长期平台或研究基座 |
| 协作 | 单人、串行 | 单人多 Agent 或少量协作者 | 并行 Feature、多团队/多仓库或强审计 |
| 架构 | 单一入口、边界显然 | 多模块、少量外部集成 | 多组件/进程/部署边界，依赖方向关键 |
| 契约 | 无稳定外部承诺 | 有 API、配置或文件格式 | 多调用方、版本兼容或协议治理 |
| 状态与失败 | 无持久化或可重建 | 普通持久化和迁移 | 恢复、幂等、一致性、故障窗口是核心能力 |
| 安全与副作用 | 低风险本地操作 | 常规鉴权或受控外部 API | 不可信执行、权限边界、敏感数据或不可逆副作用 |
| 计划 | 一个近期目标 | 若干 Feature 和短期 milestone | Roadmap、多个阶段、依赖和独立交付切片 |

推荐规则：

- 所有事实都落在 Simple 列时推荐 Simple。
- 出现长期维护、多模块、稳定契约或多个 Feature 中任一信号时，至少推荐 Medium。
- 恢复/一致性、安全边界、不可逆数据、多个部署单元、并行治理或多阶段平台中出现一个强信号，或多个 Medium 风险相互耦合时，推荐 Complex。
- 用户明确指定档位时尊重选择；若选择无法覆盖明显风险，说明缺少的控制和可能后果，再让用户决定。

## 2. Simple

适合 Halo 主题、小脚本、个人自动化和可低成本重写的原型。

固定文件：

```text
AGENTS.md
docs/project.md
```

职责：

- `AGENTS.md`：日常 S0/S1/S2 路由、真实命令、边界和 DoD。
- `docs/project.md`：产品目标、当前行为、已接受但未实现的行为、架构草图、质量约束和开放问题。

Simple 不使用 Feature 文件、ADR、独立 Plan、稳定 Artifact ID 或 validator。S1 直接更新 living project spec；S2 应暂停并建议升级，而不是临时发明一套半成品治理。

## 3. Medium

适合长期维护的个人应用、库、服务和有明确模块边界的产品。

固定文件：

```text
AGENTS.md
docs/project/project-brief.md
docs/architecture/overview.md
docs/specs/README.md
docs/adr/README.md
docs/templates/feature-spec.md
docs/templates/adr.md
```

每个 S1/S2 Feature 创建：

```text
docs/specs/F-NNNN-<slug>.md
```

Medium 的 Feature Spec 把 requirements、technical design、delivery slices 和 evidence 放在一个文件中，减少跨文件同步。跨多个 Feature、代价高且难逆转的决定才创建 `ADR-NNNN`。它不创建独立 Roadmap 和 Plan；近期 milestones 留在 Project Brief，Feature 的实现切片留在自身 Spec。

状态：

```text
Feature: draft -> accepted -> implemented -> superseded
                       \-> withdrawn
ADR:     proposed -> accepted -> superseded
                 \-> rejected
```

## 4. Complex

适合 BearAgent 类 Agent Runtime、基础设施、研究平台、数据/安全/恢复风险高或多阶段演进的项目。

固定文件：

```text
AGENTS.md
docs/index.md
docs/project/project-brief.md
docs/project/roadmap.md
docs/architecture/overview.md
docs/specs/README.md
docs/adr/README.md
docs/plans/README.md
docs/templates/feature-spec.md
docs/templates/adr.md
docs/templates/implementation-plan.md
scripts/validate_sdd.py
```

每个非平凡 Feature 使用独立 `F-NNNN` Spec 和 `PLAN-F-NNNN` Plan；S2 再增加 `ADR-NNNN`。Spec 定义 what/why，ADR 记录长期 why，Plan 定义 how/sequence，Architecture 描述 current state，Roadmap 只记录阶段与依赖。

Complex 使用稳定 ID、明确状态机、纵向切片、AC-to-evidence 映射和机械关系校验。完整规则见 `complex-governance.md`。

## 5. 项目 Profile 与变更级别

Profile 是项目长期治理方式；S0/S1/S2 是单次变化的风险：

| 变更 | Simple | Medium | Complex |
|---|---|---|---|
| S0 typo / local bug / mechanical | 直接修复与验证 | 直接修复与验证 | 直接修复与验证 |
| S1 observable behavior | 更新 `docs/project.md` | Feature Spec（含设计与切片） | Feature Spec + Plan |
| S2 architecture / data / security / recovery | 建议升档后再实现 | Feature Spec + ADR；风险持续时升档 | Feature Spec + ADR + Plan + 风险验证 |

不要因为项目是 Complex 就给 typo 创建 Spec，也不要因为项目是 Simple 就跳过不可逆迁移的设计和回滚。

## 6. 升档信号

Simple → Medium：

- living spec 已难以同时表达多个 Feature；
- 架构边界需要独立说明；
- 开始维护稳定 API、配置、文件格式或持久数据；
- 工作频繁跨 session，需求和实现状态开始混淆。

Medium → Complex：

- Feature 的设计与切片反复膨胀，需要 Spec/Plan 分离；
- 多个 milestone、Feature 依赖或并行工作需要 Roadmap；
- ADR、状态和关系数量足以产生漂移；
- security、migration、recovery、concurrency、兼容或外部副作用成为经常性风险；
- 需要机械校验、审计或跨 Agent 恢复进度。

降档时不要删除历史 Artifact。保留可追溯历史，更新 `AGENTS.md` 的新工作路由，并停止制造目标档位不再要求的文档。
