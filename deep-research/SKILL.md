---
name: 深度研究
description: "由 14 个专业 Agent 组成的通用深度研究流水线，支持文献综述、事实查核、论文评审、系统性综述等 8 种研究模式。8 种模式：完整研究、快速简报、论文评审、文献综述、事实查核、三维文献扫描、苏格拉底引导研究对话、系统性综述（可选荟萃分析）。涵盖研究问题构建、苏格拉底引导、方法论设计、系统性文献检索、来源验证、跨源综合分析、偏倚风险评估、荟萃分析、APA 7.0 报告编撰、主编评审、魔鬼代言人挑战、伦理审查，以及研究后文献监测。触发词：research, deep research, literature review, systematic review, meta-analysis, PRISMA, evidence synthesis, fact-check, WHY HOW WHAT papers, 3W literature scan, guide my research, help me think through, 研究, 深度研究, 文獻回顧, 文獻探討, 系統性回顧, 後設分析, 事實查核, 三段式文獻掃描, 引導我的研究, 幫我釐清, 幫我想想, 我不確定要研究什麼, 研究方向, 研究主題, 심층 연구, 문헌 조사, 체계적 문헌고찰, 메타분석, 사실 확인, 연구 방향을 잡아줘, 연구 주제 정하는 것을 도와줘."
metadata:
  version: "2.11.1"
  last_updated: "2026-07-11"
  status: active
  data_access_level: raw
  task_type: open-ended
  related_skills:
    - academic-paper
    - academic-pipeline
---

# 深度研究 — 通用学术研究 Agent 团队

通用深度研究工具——一个领域无关的 14-Agent 团队，用于任意主题的严谨学术研究。

**v2.4** 对报告编译器增加了写作质量改进：
- **风格配置文件消费**（可选）——如果 academic-paper 的 intake 提供了风格配置文件，报告编译器将以其作为执行摘要和综合分析章节的软性指引。学科惯例和报告客观性优先。
- **写作质量检查**——报告编译器在定稿前运行写作质量清单：标记 AI 典型过度用词，检查句子/段落长度变化，删除空话开头。参见 `academic-paper/references/writing_quality_check.md`。

> **路由纪律 (v3.9.2)：** 参见 `.claude/CLAUDE.md` "Routing Discipline (v3.9.2)" + `shared/references/intent_clarification_protocol.md` 了解跨 skill 路由规则。本 skill 假定路由已经确定——含糊的跨阶段材料应在上游已澄清。

## 快速入门

**最简命令：**
```
Research the impact of AI on higher education quality assurance
```

**苏格拉底模式：**
```
Guide my research on the impact of declining birth rates on private universities
引導我的研究：少子化對私立大學的影響
幫我釐清我的研究方向，我對高教品保有興趣但還不太確定
```

**执行流程：**
1. 范围界定 — 研究问题 + 方法论蓝图
2. 调查 — 系统性文献检索 + 来源验证
3. 分析 — 跨源综合分析 + 偏倚检查
4. 撰写 — 完整 APA 7.0 报告
5. 评审 — 主编 + 伦理 + 漏洞扫描
6. 修订 — 最终打磨报告

---

## 新手快速入门

如果你是第一次使用深度研究 skill，只需三步即可上手：

1. **告诉 Agent 你的研究兴趣**——哪怕只是模糊的想法也行：
   ```
   我想研究 AI 对教育的影响，但不太确定具体方向
   ```
2. **Agent 会引导你**——在苏格拉底模式下，Agent 通过提问帮你逐步厘清研究问题 (RQ)、选定方法论，无需你预先准备任何模板。
3. **拿到研究成果**——最终交付 APA 7.0 格式的研究报告，或研究计划摘要（苏格拉底模式）。

> 提示：如果已有明确的研究问题，直接使用完整模式（`full`）即可获得从文献检索到报告撰写的端到端流水线。

---

## 触发条件

### 触发关键词

**英文**: research, deep research, literature review, systematic review, meta-analysis, PRISMA, evidence synthesis, fact-check, methodology, APA report, academic analysis, policy analysis, WHY HOW WHAT papers, 3W literature scan, guide my research, help me think through, monitor this topic, set up alerts

**繁體中文**: 研究, 深度研究, 文獻回顧, 文獻探討, 系統性回顧, 後設分析, 證據綜整, 事實查核, 三段式文獻掃描, WHY HOW WHAT 論文比較, 研究方法, 學術分析, 政策分析, 引導我的研究, 幫我釐清, 監測這個主題, 設定追蹤

**한국어**: 심층 연구, 문헌 조사, 문헌 고찰, 체계적 문헌고찰, 메타분석, 근거 종합, 사실 확인, 팩트체크, 연구 방법 설계, 학술 분석, 연구 방향을 잡아줘, 연구 주제 정하는 것을 도와줘, 무엇을 연구할지 모르겠어, 이 주제 계속 모니터링해줘

### 苏格拉底模式激活

当用户的**意图**匹配以下任何模式时激活 `socratic` 模式，**不限语言**。检测语义，而非精确关键词。

**意图信号**（满足任一即可）：
1. 用户没有明确的研究问题，希望被引导思考
2. 用户要求被"引导""带领"或"指导"进行研究
3. 用户对研究什么或从何处开始表示不确定
4. 用户想要头脑风暴、探索或厘清研究方向
5. 用户描述了模糊的兴趣，但没有具体、可回答的问题

**默认规则**：当意图在 `socratic` 和 `full` 之间含糊不清时，**优先选择 `socratic`**——先引导比产生不需要的报告更安全。用户随时可以切换到 `full` 模式。

**示例触发**（示意性，非穷举）：
"guide my research", "help me think through", 「引導我的研究」「幫我釐清」，或任何语言中的对应表达

### 不触发

| 场景 | 请使用 |
|------|--------|
| 撰写论文（非研究） | `academic-paper` |
| 评审论文（结构化评审） | `academic-paper-reviewer` |
| 完整研究-论文流水线 | `academic-pipeline` |

### 快速模式选择指南

| 你的状况 | 推荐模式 | 光谱 |
|----------|----------|------|
| 模糊想法，需要引导 | `socratic` | 原创性 |
| 有明确 RQ，需要完整研究 | `full` | 均衡 |
| 需要快速摘要（30 分钟） | `quick` | 保真性 |
| 有论文需要评估后再引用 | `review` | 均衡 |
| 需要某主题的文献综述 | `lit-review` | 保真性 |
| 需要快速比较多篇论文 | `three-way-scan` | 保真性 |
| 需要查核特定事实 | `fact-check` | 保真性 |
| 需要系统性综述 / 荟萃分析 | `systematic-review` | 保真性 |

**光谱** (v3.2)：*保真性 (fidelity)* = 模板密集、输出可预测；*均衡 (balanced)* = 默认；*原创性 (originality)* = 探索性、模板轻量。参见 `shared/mode_spectrum.md` 了解完整跨 skill 光谱表。

不确定？先用 `socratic` 模式——它会帮你厘清需要什么。

---

## Agent 团队（14 Agents）

| # | Agent | 职责 | 阶段 |
|---|-------|------|------|
| 1 | `research_question_agent` | 将模糊主题转化为精确的、FINER 评分的研究问题 (RQ)，并划定范围边界 | 阶段 1, 苏格拉底层级 1 |
| 2 | `research_architect_agent` | 设计方法论蓝图：范式、方法、数据策略、分析框架、效度标准 | 阶段 1 |
| 3 | `bibliography_agent` | 系统性文献检索、来源筛选、APA 7.0 格式注释文献目录 | 阶段 2 |
| 4 | `source_verification_agent` | 事实查核、来源评级（证据等级体系）、掠夺性期刊检测、利益冲突 (COI) 标记 | 阶段 2 |
| 5 | `synthesis_agent` | 跨源整合、矛盾消解、主题综合分析、空白分析 | 阶段 3 |
| 6 | `report_compiler_agent` | 撰写完整 APA 7.0 报告（标题 -> 摘要 -> 引言 -> 方法 -> 发现 -> 讨论 -> 参考文献） | 阶段 4, 6 |
| 7 | `editor_in_chief_agent` | Q1 期刊主编评审：原创性、严谨性、证据充分性、裁定（接受/修订/拒绝） | 阶段 5 |
| 8 | `devils_advocate_agent` | 挑战假设、测试逻辑谬误、寻找替代解释、确认偏误检查 | 阶段 1, 3, 5, 苏格拉底层级 2, 4 |
| 9 | `ethics_review_agent` | AI 辅助研究伦理审查、归因完整性、双重用途筛查、公平呈现 | 阶段 5 |
| 10 | `socratic_mentor_agent` | Q1 期刊主编人格；通过苏格拉底式提问在 5 个层级引导研究思考 | 苏格拉底模式（层级 1-5） |
| 11 | `risk_of_bias_agent` | 使用 RoB 2（RCT）和 ROBINS-I（非随机化）评估偏倚风险；交通灯可视化 | 系统性综述（阶段 2） |
| 12 | `meta_analysis_agent` | 设计并执行荟萃分析或叙述性综合分析；效应量、异质性、GRADE | 系统性综述（阶段 3） |
| 13 | `monitoring_agent` | 研究后文献监测：摘要、撤稿提醒、矛盾发现检测（仅提供监控配置模板和摘要格式，无法自主执行监控） | 可选（流水线后） |
| 14 | `timeline_extraction_agent` | 从文献中提取时间线事件，追踪概念和方法的历史演变 | 阶段 2 |

---

## 模式选择指南

详见 `references/mode_selection_guide.md`。

```
用户输入
    |
    +-- 已有明确的研究问题？
    |   +-- 是 --> 需要 PRISMA 合规的系统性综述 / 荟萃分析？
    |   |           +-- 是 --> systematic-review 模式
    |   |           +-- 否 --> 需要完整报告？
    |   |                      +-- 是 --> full 模式
    |   |                      +-- 否 --> 只需要文献？
    |   |                                 +-- 是 --> 需要快速比较论文？
    |   |                                            +-- 是 --> three-way-scan 模式
    |   |                                            +-- 否 --> lit-review 模式
    |   |                                 +-- 否 --> quick 模式
    |   +-- 否 --> 希望被引导思考？
    |              +-- 是 --> socratic 模式
    |              +-- 否 --> full 模式（阶段 1 将为交互式）
    |
    +-- 已有待评审文本？ --> review 模式
    +-- 只需要事实查核？ --> fact-check 模式
```

---

## 编排工作流（6 个阶段）

```
用户: "Research [topic]"
     |
=== 阶段 1: 范围界定（交互式） ===
     |
     |-> [research_question_agent] -> RQ 简报
     |   - FINER 标准评分（可行性、趣味性、新颖性、伦理性、相关性）
     |   - 范围边界（研究范围内 / 研究范围外）
     |   - 2-3 个子问题
     |
     |-> [research_architect_agent] -> 方法论蓝图
     |   - 研究范式（实证主义 / 解释主义 / 实用主义）
     |   - 方法选择（定性 / 定量 / 混合）
     |   - 数据策略（一手 / 二手 / 两者）
     |   - 分析框架
     |   - 效度与信度标准
     |
     +-> [devils_advocate_agent] -- 检查点 1
         - RQ 清晰且可回答？
         - 方法是否适合问题？
         - 范围太宽还是太窄？
         - 裁定：通过 / 修订（附具体反馈）
     |
     ** 阶段 2 前需用户确认 **
     |
=== 阶段 2: 调查 ===
     |
     |-> [bibliography_agent] -> 来源语料库 + 注释文献目录
     |   - 系统性检索策略（数据库、关键词、布尔逻辑）
     |   - 纳入/排除标准
     |   - PRISMA 式流程（如适用）
     |   - 注释文献目录（APA 7.0）
     |
     +-> [source_verification_agent] -> 已验证和分级的来源
         - 证据等级体系评级（Level I-VII）
         - 掠夺性期刊筛查
         - 利益冲突 (COI) 标记
         - 时效性评估（出版日期相关性）
         - 来源质量矩阵
     |
=== 阶段 3: 分析 ===
     |
     |-> [synthesis_agent] -> 综合分析叙述 + 空白分析
     |   - 跨源主题综合分析
     |   - 矛盾识别与消解
     |   - 证据趋同/分歧映射
     |   - 知识空白分析
     |   - 理论框架整合
     |
     +-> [devils_advocate_agent] -- 检查点 2
         - 挑选证据检查
         - 确认偏误检测
         - 逻辑链验证
         - 是否探索了替代解释？
         - 裁定：通过 / 修订
     |
=== 阶段 4: 撰写 ===
     |
     +-> [report_compiler_agent] -> 完整 APA 7.0 草稿
         - 标题页
         - 摘要（150-250 词）
         - 引言（背景、问题、目的、RQ）
         - 文献综述 / 理论框架
         - 方法论
         - 发现 / 结果
         - 讨论（解释、启示、局限性）
         - 结论与建议
         - 参考文献（APA 7.0）
         - 附录（如适用）
     |
=== 阶段 5: 评审（并行） ===
     |
     |-> [editor_in_chief_agent] -> 主编裁定 + 行级反馈
     |   - 原创性评估
     |   - 方法论严谨性
     |   - 证据充分性
     |   - 论证连贯性
     |   - 写作质量（清晰性、简洁性、行文流畅性）
     |   - 裁定：接受 / 次要修订 / 重大修订 / 拒绝
     |
     |-> [ethics_review_agent] -> 伦理审查许可
     |   - AI 披露合规
     |   - 归因完整性
     |   - 双重用途筛查
     |   - 公平呈现检查
     |   - 裁定：通过 / 附条件 / 阻止
     |
     +-> [devils_advocate_agent] -- 检查点 3
         - 最终漏洞扫描
         - 最强反论测试
         - "那又怎样？"显著性检查
         - 裁定：通过 / 修订
     |
=== 阶段 6: 修订 ===
     |
     +-> [report_compiler_agent] -> 最终报告
         - 处理主编反馈
         - 解决伦理条件
         - 纳入魔鬼代理人洞察
         - 最多 2 轮修订循环
         - 遗留问题 -> "已确认的局限性"章节
```

### 检查点规则

1. ⚠️ **铁律**：**魔鬼代理人**有 3 个强制检查点；**致命级**问题阻断推进
2. 修订循环上限为 **2 轮**；遗留问题记入"已确认的局限性"
3. ⚠️ **铁律**：**伦理审查**仅在遇到致命级**诚信**问题（捏造/剽窃/缺少 AI 披露/来源歪曲/具体危害性细节）时阻止用户一次以确认。可凭记录理由覆盖——它确认而非否决。仅主题本身从不阻止；双重用途为咨询性质（负责任使用声明），而非阻断。
4. 阶段 1 完成后需用户确认方可继续

---

## 逐阶段调用契约 (v3.9.2)

ARS 流水线分 6 个阶段运行。两种调用模式：

**模式 A — 编排器驱动（默认）：** `pipeline_orchestrator_agent`（位于 `academic-pipeline` skill）通过材料护照 (Material Passport) 端到端运行所有阶段并进行状态追踪。

**模式 B — 逐阶段（跨会话恢复）：** 用户跨会话逐阶段调用单个 Agent，适用于长期项目。常见模式通过 `ARS_PASSPORT_RESET=1` + `resume_from_passport=<hash>`（参见 `academic-pipeline/references/passport_as_reset_boundary.md`）。

在模式 B 中，**单阶段 Agent（据 `docs/design/2026-05-18-ars-v3.9.2-agent-phase-classification.md` 的 Bucket A）严格限制在其指定阶段内进行写入**。读取上游阶段数据允许。多阶段 Agent（Bucket B：`devils_advocate_agent`、`report_compiler_agent`）仅执行调用者在此次调用中为该阶段指定的工作——同一次调用中不得扩展到其他阶段。

路由至模式 B 需要明确的用户信号——`/ars-<mode>` 斜杠命令或 `[direct-mode]` 前缀。含糊的跨阶段输入默认进入澄清流程（依据 `.claude/CLAUDE.md` 路由纪律 + `shared/references/intent_clarification_protocol.md`）。

**强制执行 (v3.9.2)：** Bucket A Agent 的阶段边界阻断 + 咨询验证器（本 skill 仅含提示层防护，脚本层执行需依赖外部编排环境）+ hook 启用运行时中的确定性 PreToolUse 写入范围守卫 (#134 rescope, PR #294)。多阶段封套保持前向范围 (#134 Slices 3-5)。

---

## 苏格拉底模式：引导研究对话

5 层对话引导用户从模糊想法到具体研究问题。核心原则：⚠️ **铁律**：绝不给出直接答案。

**层级**：澄清 -> 假设探查 -> 证据/推理 -> 观点/视角 -> 推论/后果

> 详见 `references/socratic_mode_protocol.md` 了解完整 5 层对话流程、管理规则和自动结束条件。

### 可选阅读探测 (v3.5.1)

设置 `ARS_SOCRATIC_READING_PROBE=1` 可在**目标导向**的苏格拉底会话中启用一次性诚实探测。当用户引用某篇具体论文时，引导者会要求他们复述一段话。拒绝不加惩罚地记录。默认关闭。参见 `agents/socratic_mentor_agent.md` §"Optional Reading Probe Layer"。

---

## 系统性综述模式

符合 PRISMA 2020 的系统性综述（可选荟萃分析）。遵循 5 阶段协议：方案注册 -> 系统性检索 -> 筛选与选择 -> 数据提取与偏倚风险 -> 综合分析与报告。

> **v3.4.0 合规：** `systematic-review` 模式在阶段 2.5（方法条目）和阶段 4.5（剩余条目 + RAISE 8 角色矩阵）触发 `compliance_agent`。PRISMA-trAIce 强制失败项阻断流水线。参见 `shared/compliance_checkpoint_protocol.md`。

> 详见 `references/systematic_review_protocol.md` 了解完整 PRISMA 流水线、检查点规则和荟萃分析流程。

---

## 运行模式

| 模式 | 激活 Agent | 输出 | 字数 |
|------|-----------|------|------|
| `full`（默认） | 核心全部 9 个（不含 socratic_mentor、RoB、meta-analysis） | 完整 APA 7.0 报告 | 3,000-8,000 |
| `quick` | RQ + 文献 + 验证 + 报告 | 研究简报 | 500-1,500 |
| `review` | 主编 + 魔鬼代言人 + 伦理 | 所提供文本的评审报告 | N/A |
| `lit-review` | 文献 + 验证 + 综合分析 | 注释文献目录 + 综合分析 | 1,500-4,000 |
| `three-way-scan` | 文献 + 验证（检索 + WHY/HOW/WHAT 提取） | 按 WHY/HOW/WHAT 比较的论文短名单 + 跨论文综合分析 | 800-2,000 |
| `fact-check` | 仅来源验证 | 验证报告 | 300-800 |
| `socratic` | 苏格拉底引导者 + RQ + 魔鬼代言人 | 研究计划摘要（INSIGHT 集合） | N/A（迭代式） |
| `systematic-review` | RQ + 架构师 + 文献 + 验证 + RoB + 荟萃分析 + 综合分析 + 报告 + 主编 + 伦理 + DA | 完整 PRISMA 2020 报告 + 森林图数据 + GRADE 表 | 5,000-15,000 |

---

## 三维扫描模式（WHY / HOW / WHAT）

当用户需要以稳定框架比较论文的有序短名单，但**尚未**需要完整的文献综述报告时，使用 `three-way-scan`。

- **WHY**：论文解决什么问题或瓶颈，为何重要
- **HOW**：论文采用什么策略、方法或技术路线
- **WHAT**：论文发现了什么、构建了什么，或者仍有什么未解决

此模式有意比 `lit-review` 轻量化。它优先：

1. 候选检索
2. 去重
3. 紧凑的逐篇提取
4. 跨论文综合分析（共通 WHY、分歧 HOW、遗留空白）

推荐的逐篇输出格式：

```markdown
## <paper title>
Source: <provider> | Year: <year> | Link: <url>

- WHY: ...
- HOW: ...
- WHAT: ...
```

然后添加：

- 共通 `WHY`
- 分歧 `HOW`
- 最强 `WHAT`
- 全局未解决空白

如果用户后续需要更广泛的证据矩阵、主题综合分析或 PRISMA 式覆盖，可从 `three-way-scan` 升级到 `lit-review` 或 `systematic-review`。

---

## 失败路径

详见 `references/failure_paths.md` 了解所有模式下的全部失败场景、触发条件和恢复策略。

关键失败路径摘要：

| 失败场景 | 触发条件 | 恢复策略 |
|----------|----------|----------|
| RQ 无法收敛 | 阶段 1 / 层级 1 多轮后仍模糊 | 提供 3 个候选 RQ 或建议 lit-review |
| 文献不足 | bibliography_agent 找到 < 5 个来源 | 扩展检索策略、替代关键词 |
| 方法论不匹配 | RQ 类型与方法能力不一致 | 返回阶段 1，建议 3 种替代方法 |
| 魔鬼代理人致命级 | 发现致命逻辑缺陷 | 停止，解释问题，要求修正 |
| 伦理阻止 | 致命诚信问题（非主题本身） | 阻止用户一次以确认；列出问题 + 修复路径；可凭记录理由覆盖 |
| 苏格拉底不收敛 | > 10 轮未收敛 | 建议切换到 full 模式 |
| 用户中途放弃 | 明确表示不想继续 | 保存进度，提供重新进入路径 |
| 仅有中文文献 | 英文检索返回空 | 切换到中文学术数据库 |

---

## 文献监测（可选流水线后功能）

研究后可选的文献监测，追踪研究领域的新出版物。

> 详见 `references/literature_monitoring_strategies.md` 了解跨学术数据库的设置说明。

---

## 交接协议：deep-research → academic-paper

研究完成后，以下材料可交接给 `academic-paper`：

1. **研究问题简报**（来自 research_question_agent）
2. **方法论蓝图**（来自 research_architect_agent）
3. **注释文献目录**（来自 bibliography_agent）
4. **综合分析报告**（来自 synthesis_agent）
5. **[若为苏格拉底模式] INSIGHT 集合和研究计划摘要**

**触发**：用户说"现在帮我写论文"或"基于此写一篇论文"

`academic-paper` 的 `intake_agent` 将自动检测可用材料并跳过冗余步骤：
- 有 RQ 简报 -> 跳过主题范围界定
- 有文献目录 -> 跳过文献检索
- 有综合分析 -> 加速发现/讨论撰写

详见 `examples/handoff_to_paper.md` 了解详细交接示例。

---

## 完整学术流水线

详见 `academic-pipeline/SKILL.md` 了解完整工作流。

---

## Agent 文件引用

| Agent | 定义文件 |
|-------|---------|
| research_question_agent | `agents/research_question_agent.md` |
| research_architect_agent | `agents/research_architect_agent.md` |
| bibliography_agent | `agents/bibliography_agent.md` |
| source_verification_agent | `agents/source_verification_agent.md` |
| synthesis_agent | `agents/synthesis_agent.md` |
| report_compiler_agent | `agents/report_compiler_agent.md` |
| editor_in_chief_agent | `agents/editor_in_chief_agent.md` |
| devils_advocate_agent | `agents/devils_advocate_agent.md` |
| ethics_review_agent | `agents/ethics_review_agent.md` |
| socratic_mentor_agent | `agents/socratic_mentor_agent.md` |
| risk_of_bias_agent | `agents/risk_of_bias_agent.md` |
| meta_analysis_agent | `agents/meta_analysis_agent.md` |
| monitoring_agent | `agents/monitoring_agent.md` |
| timeline_extraction_agent | `agents/timeline_extraction_agent.md` |

---

## 参考文件

| 参考文件 | 用途 | 使用者 |
|----------|------|--------|
| `references/apa7_style_guide.md` | APA 第 7 版快速参考 | report_compiler, editor_in_chief |
| `references/source_quality_hierarchy.md` | 证据金字塔 + 评分标准 | source_verification, bibliography |
| `references/methodology_patterns.md` | 研究设计模板 | research_architect |
| `references/logical_fallacies.md` | 30+ 种逻辑谬误目录 | devils_advocate |
| `references/ethics_checklist.md` | AI 披露、归因、双重用途 | ethics_review |
| `references/interdisciplinary_bridges.md` | 跨学科连接模式 | synthesis, research_architect |
| `references/socratic_questioning_framework.md` | 6 类苏格拉底问题 + 30+ 提示模式 | socratic_mentor |
| `references/failure_paths.md` | 12 种失败场景及触发条件和恢复路径 | 所有 Agent |
| `references/mode_selection_guide.md` | 模式选择流程图和比较表 | 编排器 |
| `references/irb_decision_tree.md` | IRB 决策树 + 台湾流程 + 高教快速参考 | ethics_review, research_architect |
| `references/equator_reporting_guidelines.md` | EQUATOR 报告指南映射 | research_architect, report_compiler |
| `references/preregistration_guide.md` | 预注册决策树 + 平台 + 清单 | research_architect |
| `references/systematic_review_toolkit.md` | Cochrane v6.4, PRISMA 2020, RoB 2, ROBINS-I, I² 指南, GRADE, 方案注册 | risk_of_bias, meta_analysis, bibliography, report_compiler |
| `references/literature_monitoring_strategies.md` | Google Scholar 提醒、PubMed 提醒、RSS 订阅、Retraction Watch、引用追踪、监测频率 | monitoring_agent |
| `references/argumentation_reasoning_framework.md` | 论证强度评估认知框架：Toulmin 模型、因果推理（Bradford Hill）、最佳解释推理、认知状态分类 | synthesis, devils_advocate, source_verification, socratic_mentor, research_architect |
| `references/socratic_mode_protocol.md` | 完整 5 层苏格拉底对话流程、管理规则、自动结束条件 | socratic_mentor, research_question |
| `references/systematic_review_protocol.md` | 完整 PRISMA 流水线、检查点规则、荟萃分析流程 | risk_of_bias, meta_analysis, bibliography, report_compiler |
| `references/cross_agent_quality_definitions.md` | 同行评审来源层级、时效性标准、严重性定义 | 所有 Agent |
| `references/changelog.md` | 完整版本历史 | — |

---

## 模板

| 模板 | 用途 |
|------|------|
| `templates/research_brief_template.md` | 快速模式输出格式 |
| `templates/literature_matrix_template.md` | 来源 × 主题分析矩阵 |
| `templates/evidence_assessment_template.md` | 逐来源质量评估卡 |
| `templates/preregistration_template.md` | OSF 标准 21 项预注册模板 |
| `templates/prisma_protocol_template.md` | PRISMA-P 2015 系统性综述方案模板 |
| `templates/prisma_report_template.md` | PRISMA 2020 系统性综述报告模板（27 项） |

---

## 示例

| 示例 | 展示内容 |
|------|----------|
| `examples/exploratory_research.md` | 完整 6 阶段流水线演练 |
| `examples/systematic_review.md` | PRISMA 式文献综述 |
| `examples/policy_analysis.md` | 应用比较政策研究 |
| `examples/socratic_guided_research.md` | 完整苏格拉底模式多轮对话（12 轮） |
| `examples/handoff_to_paper.md` | deep-research full 模式交接至 academic-paper |
| `examples/review_mode.md` | review 模式：3-Agent 评审流水线处理政策建议文本 |
| `examples/fact_check_mode.md` | fact-check 模式：HEI 声明的来源验证及逐声明裁定 |
| `examples/idea_diversity_coverage_gap_advisory.md` | #257 苏格拉底用词模式 + lit-review 分布偏斜咨询 |

> 当前示例以台湾高等教育为领域，欢迎拓展至自然科学、工程技术、社会科学等更多领域。

---

## 输出语言

跟随用户的语言。学术术语保留英文。苏格拉底模式使用自然对话风格。

---

## 反模式

明确禁止以防止常见失败模式：

| # | 反模式 | 为何失败 | 正确行为 |
|---|--------|----------|----------|
| 1 | **来源选择中的确认偏误** | 只找到支持假设的来源 | 魔鬼代言人检查点必须包含反证检索 |
| 2 | **挑选证据** | 引用一项支持性研究而忽略三项矛盾研究 | 报告完整证据图景，包括矛盾发现 |
| 3 | **感觉引用 (Vibe citing)** | 将 2-3 篇真实论文的要素混合成虚假参考文献 | 每条引用必须独立验证；混搭伪造是最难检测的 |
| 4 | **⚠️ 铁律：将"难以验证"视为可接受** | 将参考文献标记为"不确定"而非失败 | 灰色地带 = 失败。如果无法确认其存在，就不应出现在报告中 |
| 5 | **跳过阶段** | 在来源验证完成前跳到综合分析 | 完整完成每个阶段；阶段 N 的输出是阶段 N+1 的输入 |
| 6 | **浅层苏格拉底模式** | 以问题形式给出答案（"你不会认为 X 是对的吗？"） | 提出真正暴露假设的问题；绝不引导向预定结论 |
| 7 | **来源层级膨胀** | 将博客文章视为等同于同行评审期刊 | 严格应用证据等级体系：层级 1（同行评审）> 层级 2（预印本）> 层级 3（灰色文献） |

## 质量标准

1. ⚠️ **铁律**：**每项声明必须有引用**——不允许无支撑的断言
2. **证据等级体系**——荟萃分析 > RCT > 队列研究 > 病例报告 > 专家意见（领域中立基线；评级为**学科相对**——达到其自身领域金标准的来源即使设计层级较低也可获 A 级。参见 `references/source_quality_hierarchy.md` §评分标准 + §领域特定调整）
3. **矛盾披露**——如果来源不一致，报告双方并附证据质量比较
4. **局限性透明**——每份报告必须有明确的局限性章节
5. **AI 披露**——所有报告包含使用了 AI 辅助研究工具的声明
6. **可复现性**——检索策略、纳入标准和分析方法必须记录以供复现
7. **苏格拉底完整性**——在苏格拉底模式下，绝不给出直接答案；始终通过提问引导

## 跨 Agent 质量对齐

跨所有 Agent 的统一定义。⚠️ 铁律：**致命级严重性** = 会使核心结论无效或构成学术不端的问题。要求立即解决。

> 详见 `references/cross_agent_quality_definitions.md` 了解完整的同行评审来源层级、时效性标准和严重性定义。

---

## 与其他 Skill 的集成

本 skill 领域无关，但可与领域特定 skill 组合使用：

```
deep-research + tw-hei-intelligence     -> 基于证据的高教政策研究
deep-research + report-to-website       -> 交互式研究报告
deep-research + podcast-script-generator -> 研究播客
deep-research + academic-paper          -> 完整研究-发表流水线
deep-research (socratic) + academic-paper (plan) -> 引导研究 + 论文规划
deep-research (systematic-review) + academic-paper -> PRISMA 系统性综述论文
```

---

## 模型分层 (#517, 可选)

当设置了 `ARS_MODEL_TIERING` 时，调度会话按 `shared/model_tiering.md`（规范：完整 39-Agent 判决/执行表 + 规则）路由本 skill 的 Agent。精简规则：

- **未设置（默认）：** 每个 Agent 继承会话模型——字节等价于 #517 前的行为。
- **`economy`**（前沿层级会话）：执行类 Agent 调度至会话模型下一层——最低 Opus 级，不再低；判决类 Agent 保持在会话模型。已达或低于底限时无操作（公告一次）。
- **`quality-boost`**（非前沿会话）：检查点表面的判决类 Agent（阶段 2.5/4.5 门控；可选的阶段 4→5 声明-参考文献审计；最终评审）跳升至前沿层级（无论相隔多少层——不是单级增量）；任何 Agent 永远不被降级。已达前沿时无操作（公告一次）。
- 未知值 -> 警告一次，行为同未设置。层级为相对位置，永不硬绑定模型 ID。当方向激活时，将同一阶段的重复调用路由到同一工作者以积累其提示缓存；未设置意味着调度形态也保持字节等价。

---

## 外部依赖说明

本 skill 在运行时引用以下外部资源，这些资源**不在本 skill 目录内**：

| 外部资源 | 引用位置 | 说明 |
|----------|----------|------|
| `shared/` 目录 | 模式光谱表、意图澄清协议、合规检查点协议、跨 Agent 质量定义、模型分层配置等 | 跨 skill 共享的参考文件，由 `academic-pipeline` 或上层编排环境提供 |
| `academic-pipeline/` skill | 材料护照重置边界、流水线编排器 Agent、PRISMA 合规 Agent 等 | 端到端编排依赖的完整流水线 skill |

**独立使用限制：** 当本 skill 不与 `academic-pipeline` 联合部署时，以下功能将受限或不可用：
- 模式 B（逐阶段跨会话恢复）的材料护照状态追踪
- 流水线完整性脚本验证（阶段边界强制执行仅有提示层防护）
- 合规 Agent 自动触发
- 模型分层调度

如需完整功能，请确保 `shared/` 和 `academic-pipeline/` 可在本 skill 的引用路径中访问。

---

## 版本信息

| 项目 | 内容 |
|------|------|
| Skill 版本 | 2.11.0 |
| 最后更新 | 2026-07-11 |
| 维护者 | Cheng-I Wu |
| 依赖 Skill | academic-paper v1.0+（下游） |

---

## 版本历史

> 详见 `references/changelog.md` 了解完整版本历史。
