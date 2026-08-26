---
name: develop-software
description: 为软件项目一次性初始化、迁移或重新校准可长期复用的 SDD 工作流。仅在用户明确调用并要求为新项目或既有仓库建立开发规范时使用；支持由用户指定或由 Codex 评估 Simple、Medium、Complex 三档，然后通过需求访谈生成对应的 AGENTS.md、项目文档、Spec、Architecture、ADR、Plan、Roadmap、模板与校验规则。初始化后由仓库规则驱动日常功能、修复和重构，不要在普通开发任务或每个需求中重复调用。
---

# Develop Software

把本 Skill 作为一次性的**项目 SDD 初始化器**：

> 选择 Profile → 澄清项目需求 → 套用固定模板 → 写入项目事实 → 验证并交接

初始化完成后，后续 Agent 只读取仓库中的 `AGENTS.md`、项目文档、代码和测试。不要让普通开发再次依赖本 Skill。

## 边界

执行本 Skill 时：

- 初始化空项目、把既有项目迁移到某个 SDD Profile，或重新校准已经失配的工作流；
- 固化开发流程、Source of Truth、Artifact 生命周期、验证命令与完成条件；
- 不实现业务功能，除非用户在初始化完成后另行明确要求；
- 不根据聊天历史宣称项目事实；把已确认内容写入仓库，把未知内容标为 `TBD` 或 Open question；
- 保留用户已有改动，不覆盖既有权威文档，不批量改名或删除历史 Artifact。

## 1. 检查仓库

先读取并检查：

1. 当前目录适用的 `AGENTS.md`、`CLAUDE.md` 和其他 repository instructions；
2. `git status`、当前 diff、README、贡献指南和已有 SDD 文档；
3. build、run、test、format、lint、type check、CI 和发布命令；
4. 真实模块、接口、持久状态、外部副作用及安全边界。

空目录也要先确认路径和 Git 状态。不要仅凭项目名称或预计代码行数选择 Profile。

## 2. 确定 SDD Profile

只允许以下三个固定 Profile：

| Profile | 适用项目 | 固定治理骨架 |
|---|---|---|
| **Simple** | 小型个人项目、主题、脚本、短期原型 | `AGENTS.md` + 单一 living project spec |
| **Medium** | 长期维护的应用、库、服务或多模块个人项目 | Project Brief + current Architecture + 合并设计/计划的 Feature Spec + 按需 ADR |
| **Complex** | BearAgent 类基础设施、研究平台、高风险或多阶段系统 | Project Brief + Roadmap + current Architecture + 独立 Feature Spec / ADR / Plan + 稳定 ID、状态机和 validator |

按以下优先级决定：

1. 用户明确指定 Profile：采用该档，不擅自改档；若证据显示明显不足，说明风险并请求用户确认是否仍坚持。
2. 用户要求 Codex 帮助决定：完整读取 [profiles.md](references/profiles.md)，给出一个推荐档位、关键依据和相邻档位的成本差异，等待用户确认。
3. 用户没有表达选择：根据已有描述先推荐；只有缺失信息会改变档位时，每轮询问 1–3 个问题。

Profile 必须在需求访谈和写文件前确认。不要把“项目 Profile”和日常变更的 S0/S1/S2 风险级别混为一谈。

## 3. 澄清项目需求

Profile 确认后，以产品负责人和架构师的身份进行简短、多轮访谈。优先澄清：

- 要解决的问题、目标用户和主要场景；
- Goals、Non-goals、MVP 与成功证据；
- 运行环境、技术栈偏好和兼容约束；
- 数据、外部接口、副作用、权限、安全、并发、恢复和发布风险；
- 预计生命周期、里程碑和协作方式。

每轮只问会改变范围、架构或验收的 1–3 个问题。主动质疑冲突、不可验证目标和过早复杂化；不要替用户编造 owner、deadline、性能指标或支持承诺。

访谈结束后先输出并确认：

```text
SDD Profile：
项目问题：
Goals：
Non-goals：
首个可交付结果：
关键约束与风险：
仍未决定：
将创建或迁移的文件：
```

只有内容被用户明确确认后，才把需求或决定标为 `accepted`。未确认内容保持 `draft`。

## 4. 套用固定模板

新项目使用脚本复制所选 Profile：

```bash
python3 <skill-dir>/scripts/init_profile.py <simple|medium|complex> <project-root> \
  --project-name "<project-name>" \
  --owner "<owner>"
```

脚本遇到同名文件会在写入前失败，不会覆盖。先用 `--dry-run` 可以查看文件清单。

复制后必须把模板改写为该项目的真实内容：

- 删除模板说明和无关小节；
- 用仓库真实命令替换命令占位；尚未选定工具链时明确写 `TBD`，不伪造命令；
- 根据已确认需求创建首个项目级 Artifact；Medium/Complex 需要时创建首个 `F-NNNN` Feature；
- 将 Profile 名称、Source of Truth、日常变更路由和升级条件写入根 `AGENTS.md`；
- 不创建虚假的已实现能力，不把 Roadmap 或 accepted Spec 写成 current behavior。

各 Profile 的精确文件清单和日常行为见 [profiles.md](references/profiles.md)。复杂 Artifact 的状态、ID 与关系规则见 [complex-governance.md](references/complex-governance.md)。

## 5. 处理既有项目

不要对非空仓库直接运行复制脚本并强行覆盖。完整读取 [migration.md](references/migration.md)，然后：

1. 映射已有 README、RFC、Spec、ADR、issue 和计划到目标 Profile；
2. 选择一个权威入口，优先完善现有 `AGENTS.md`；
3. 只补缺失的职责，不复制同一事实；
4. 保留稳定链接、编号和历史状态；
5. 先迁移当前真实 Feature，再决定是否迁移历史文档；
6. 通过一个真实后续需求验证路由，而不是预生成整份 backlog。

升级或降级 Profile 属于重新校准，必须显式调用本 Skill。普通 Feature 不得偷偷改变项目 Profile。

## 6. 固化日常开发

生成的 `AGENTS.md` 必须让一个不了解本次对话的 Agent 自动执行以下路由：

```text
自然语言需求
  → 读取仓库事实
  → 判断 S0 / S1 / S2 变更级别
  → 使用当前 Profile 规定的 Artifact
  → 必要的用户确认
  → 实现一个可验证切片
  → 测试与问题导向 review
  → 同步 current facts 与状态
```

三档共同遵守：

- S0：typo、局部 bug、行为不变的机械重构；不新建仪式性 Artifact，bug 要有回归证据。
- S1：新增或修改可观察行为；先更新当前 Profile 的行为契约与验收标准。
- S2：架构边界、持久化、迁移、安全、公开契约、外部副作用、并发或恢复；先解决设计与回滚，再编码。

Profile 决定 Artifact 形态，变更级别决定本次需要哪些 Gate。Complex 项目中的 typo 仍是 S0；Simple 项目出现高风险变化时应暂停并建议重新运行本 Skill 升档。

## 7. 验证

初始化结束前至少检查：

1. `AGENTS.md` 能独立说明读取顺序、日常路由、授权边界和 Definition of Done；
2. 项目事实、计划事实和当前实现没有混写；
3. Markdown 本地链接有效，不存在未解释的模板占位或空 Artifact；
4. 写入的命令确实存在；能安全运行时实际执行；
5. Medium 的 Feature ID、状态和索引一致；
6. Complex 复制 `validate_artifacts.py` 到项目自己的 `scripts/validate_sdd.py`，运行其单元测试和项目扫描；
7. 普通 Feature、bug、refactor、test 和 review 不需要再次调用 `develop-software`。

Skill 自身修改后运行：

```bash
python3 scripts/test_init_profile.py
python3 scripts/test_validate_artifacts.py
python3 /root/.codex/skills/oai/skill-creator/scripts/quick_validate.py .
```

## 8. 交付

向用户报告：

1. 最终 Profile 及选择理由；
2. 已确认的项目目标、范围与未决问题；
3. 创建、迁移和保留的文件；
4. 后续自然语言需求如何被仓库规则自动路由；
5. 实际运行的验证及未覆盖风险；
6. 何种变化需要再次调用本 Skill 升档、降档或重新校准。

不要在交付中要求用户记住一组提示词。初始化后的仓库规则才是长期接口。

## Resource 路由

| 场景 | 必读资源 |
|---|---|
| 由 Codex 选择 Profile，或解释三档差异 | `references/profiles.md` |
| 说明模板来源或重新评估模板设计 | `references/sdd-basis.md` |
| 既有项目迁移、升档或降档 | `references/migration.md` |
| Complex 的 ID、状态机、关系和 validator | `references/complex-governance.md` |

只读取当前任务需要的 Reference；但一旦选择某个 Reference，必须完整读取。
