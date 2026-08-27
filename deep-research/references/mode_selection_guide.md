# 模式选择指南

## 概述

deep-research 提供 8 种模式，适用于不同的研究阶段和需求。本指南帮助用户选择最合适的模式。

---

## 决策流程图

```
User Input
    │
    ├── Have a clear research question?
    │   ├── Yes ──→ Have a text to review?
    │   │            ├── Yes ──→ review mode
    │   │            └── No ───→ Need PRISMA-compliant systematic review / meta-analysis?
    │   │                         ├── Yes ──→ systematic-review mode
    │   │                         └── No ───→ Need a complete report?
    │   │                                     ├── Yes ──→ full mode
    │   │                                     └── No ───→ Only need literature?
    │   │                                                 ├── Yes ──→ Need rapid paper comparison?
    │   │                                                 │            ├── Yes ──→ three-way-scan mode
    │   │                                                 │            └── No ───→ lit-review mode
    │   │                                                 └── No ───→ quick mode
    │   │
    │   └── No ──→ Want guided thinking?
    │              ├── Yes ──→ socratic mode
    │              └── No ───→ full mode
    │                          (Phase 1 interactive RQ clarification)
    │
    ├── Only need to verify specific facts?
    │   └── Yes ──→ fact-check mode
    │
    └── Not sure what you need?
        └── Describe your situation → System auto-recommends a mode
```

---

## 各模式详细信息

### full 模式（完整研究）

| 项目 | 说明 |
|------|------|
| **适用场景** | 需要从零开始进行完整的学术研究，产出可引用的研究报告 |
| **不适用** | 仅需快速了解某个主题；已有完整研究仅需审查；仅需参考文献列表 |
| **典型用户** | 准备论文开题的研究生、撰写分析报告的政策研究员、探索新领域的学者 |
| **预期产出** | 完整 APA 7.0 报告（3,000-8,000词），包括文献综述、方法论、分析、结论 |
| **预期对话轮次** | 2-5轮（Phase 1 交互 + 检查点） |
| **激活的 Agent** | 全部 9 个 |
| **所需时间** | 较长；适合无时间压力的深度研究 |

**触发示例**:
```
"Research the impact of AI on higher education quality assurance"
"Deep research on the impact of declining birth rates on Taiwan's higher education"
"Research the current state of SDGs implementation in Asian universities"
```

---

### quick 模式（快速研究）

| 项目 | 说明 |
|------|------|
| **适用场景** | 需要在时间约束下快速了解某个主题的核心观点和关键文献 |
| **不适用** | 需要完整的方法论设计；需要深度批判性分析；需要出版级质量的报告 |
| **典型用户** | 准备会议背景资料的行政人员、需要快速文献扫描的研究人员、撰写提案前的初步探索 |
| **预期产出** | 研究简报（500-1,500词），包括核心摘要、主要文献、初步观点 |
| **预期对话轮次** | 0-1轮（通常直接输出） |
| **激活的 Agent** | 4 个（RQ + Biblio + Verification + Report） |
| **所需时间** | 较短 |

**触发示例**:
```
"Quick research on blockchain in education"
"Quick research on the latest trends in educational technology"
```

---

### review 模式（文本审查）

| 项目 | 说明 |
|------|------|
| **适用场景** | 已有论文/报告/草稿，需要专业审查和反馈 |
| **不适用** | 尚无文本可审查；需要从零开始撰写研究；需要文献搜索 |
| **典型用户** | 完成论文后需要同行评审反馈的研究生、期刊投稿前的自检、同行审查 |
| **预期产出** | 审查报告，包含 Editorial Verdict（Accept/Revise/Reject）、具体修改建议、伦理审查 |
| **预期对话轮次** | 0-1轮 |
| **激活的 Agent** | 3 个（Editor + Devil's Advocate + Ethics） |
| **所需时间** | 中等，取决于文本长度 |

**触发示例**:
```
"Review this paper"
"Help me review this paper's methodology"
"Check this manuscript before submission"
```

---

### lit-review 模式（文献综述）

| 项目 | 说明 |
|------|------|
| **适用场景** | 需要系统的文献搜索和综合分析，但不需要完整的研究报告 |
| **不适用** | 需要带有原创分析的完整报告；仅需验证少量事实；需要方法论设计 |
| **典型用户** | 正在撰写论文文献综述章节的研究生、进行系统性综述的研究团队、课程作业 |
| **预期产出** | 附注参考文献列表 + 综合分析（1,500-4,000词），包括主题分类、证据矩阵、研究空白 |
| **预期对话轮次** | 1-2轮（确认搜索范围） |
| **激活的 Agent** | 3 个（Biblio + Verification + Synthesis） |
| **所需时间** | 中等 |

**触发示例**:
```
"Literature review on SDGs in higher education"
"Literature review: the evolution of quality assurance in Taiwan's higher education"
"Systematic review of AI-assisted assessment"
```

---

### three-way-scan 模式（WHY / HOW / WHAT 论文对比）

| 项目 | 说明 |
|------|------|
| **适用场景** | 需要以稳定的 WHY/HOW/WHAT 框架进行论文筛选对比，比完整文献综述更轻量 |
| **不适用** | 需要完整的证据矩阵、主题综合或 PRISMA 级覆盖（请升级至 `lit-review` / `systematic-review`）；需要验证特定事实（`fact-check`） |
| **典型用户** | 探索新领域的研究人员、筛选阅读清单的学生、任何需要决定深入阅读哪些论文的人 |
| **预期产出** | 逐篇 WHY/HOW/WHAT 筛选 + 跨论文综合（共同 WHY、分歧 HOW、最强 WHAT、未解决空白）（800-2,000词） |
| **预期对话轮次** | 1-2轮（确认候选论文集） |
| **激活的 Agent** | 2 个（Biblio + Verification，检索 + 精简提取） |
| **所需时间** | 低-中 |

**触发示例**:
```
"Compare these papers in WHY/HOW/WHAT format"
"Quick 3W scan of recent LLM-evaluation papers"
"Which of these should I read first?"
```

---

### fact-check 模式（事实核查）

| 项目 | 说明 |
|------|------|
| **适用场景** | 需要验证特定事实主张的真实性和来源质量 |
| **不适用** | 需要完整的研究分析；需要文献综合；需要产出研究报告 |
| **典型用户** | 验证会议中引用的数据、核查报告中的事实准确性、核查政策主张 |
| **预期产出** | 核查报告（300-800词），包括来源评级、事实准确性评估、可信度判定 |
| **预期对话轮次** | 0轮（直接输出） |
| **激活的 Agent** | 1 个（Source Verification） |
| **所需时间** | 最短 |

**触发示例**:
```
"Fact-check these claims about Taiwan's university enrollment"
"Fact-check: Is the number of universities in Taiwan really declining?"
"Verify: 'OECD countries average 50% tertiary attainment rate'"
```

---

### socratic 模式（引导式研究）

| 项目 | 说明 |
|------|------|
| **适用场景** | 对某个主题感兴趣但不确定如何开始研究；希望通过对话厘清思路；需要研究指导 |
| **不适用** | 已有明确的研究问题和方法论；需要快速输出报告；仅需文献或事实核查 |
| **典型用户** | 首次接触研究的硕士生、转换研究领域的学者、博士研究生开题头脑风暴 |
| **预期产出** | 研究计划摘要，包含提取的 INSIGHTs、研究问题方向、方法论建议 |
| **预期对话轮次** | 8-15轮（多轮对话是核心特征） |
| **激活的 Agent** | 2-3 个（socratic_mentor + research_question + devils_advocate 视需要启用） |
| **所需时间** | 较长，但重点在于思考过程而非输出速度 |

**触发示例**:
```
"Guide my research on higher education topics"
"Guide my research on educational technology"
"Help me think through my thesis direction"
"Help me think through my research topic"
「引導我的研究：高教品保」
「幫我釐清我的研究方向」
「幫我想想，我對少子化議題有興趣但不確定要研究什麼」
「我有個模糊的想法，想找研究題目」
「帶我做研究」
```

---

### systematic-review 模式（系统综述 / Meta分析）

| 项目 | 说明 |
|------|------|
| **适用场景** | 需要符合 PRISMA 的系统综述，可能包含 Meta分析；为政策或临床决策进行证据综合 |
| **不适用** | 没有明确 PICOS 问题的探索性研究；叙述性文献综述；快速了解某个主题 |
| **典型用户** | 进行 Cochrane 风格综述的研究人员、撰写系统综述章节的博士生、为指南综合证据的政策团队 |
| **预期产出** | PRISMA 2020 报告：研究方案、流程图、偏倚风险评估、森林图数据（如有 Meta分析）、GRADE 证据表、完整参考文献列表 |
| **预期对话轮次** | 3-6轮（研究方案审查 + 筛选决策 + 综合决策） |
| **激活的 Agent** | 8-10 个（RQ + Architect + Biblio + Verification + RoB + Meta-Analysis/Synthesis + Report + Editor + Ethics） |
| **所需时间** | 最长；系统综述本身就需要全面深入 |

**触发示例**:
```
"Systematic review of AI-assisted assessment in higher education"
"Meta-analysis of the effect of active learning on STEM outcomes"
"PRISMA review of quality assurance frameworks in Asian universities"
"Evidence synthesis on the impact of accreditation on institutional improvement"
```

---

## 常见误选场景

| 用户说法 | 实际可能需要 | 推荐模式 | 原因 |
|-----------|------------------|---------|------|
| "帮我做一个完整的文献综述" | 完整报告（含分析和结论） | `full`，而非 `lit-review` | lit-review 仅产出参考文献和综合分析，无原创分析 |
| "快速查一下 X 的情况" | 事实核查 | `fact-check`，而非 `quick` | 如果仅需验证特定事实，fact-check 更精准 |
| "我想研究 X" / 「我想研究X」（但无法清晰表达想知道什么） | 研究思路厘清 | `socratic`，而非 `full` | full 模式的 Phase 1 也有交互，但 socratic 更深入 |
| "帮我修改这篇论文" | 论文修改指导 | `review`，而非 `full` | 已有文本，需要审查而非从零开始研究 |
| "我需要 APA 格式的参考文献" | 参考文献格式化 | `lit-review`，而非 `full` | 如果仅需要参考文献列表和格式化，无需完整研究 |
| "帮我想研究题目" / 「幫我想研究題目」 | 研究方向探索 | `socratic` | 最适合没有明确方向的用户 |
| "X 的系统综述" | 符合 PRISMA 的综述 | `systematic-review`，而非 `lit-review` | lit-review 是叙述性综述；systematic-review 遵循 PRISMA 方案，包含偏倚风险评估和可选的 Meta分析 |
| "我需要一个 Meta分析" | 定量证据综合 | `systematic-review` | Meta分析是系统综述的组成部分，不是独立模式 |
| "论文章节的文献综述" | 叙述性文献综述 | `lit-review`，而非 `systematic-review` | 论文文献综述章节通常是叙述性的，不需要符合 PRISMA |

---

## 模式切换

### 常见切换路径

```
socratic → full              苏格拉底模式完成后继续进行完整研究
socratic → academic-paper    苏格拉底模式完成后直接撰写论文
lit-review → full            文献综述后需要完整分析
lit-review → systematic-review  初步文献调研后需要正式 PRISMA 合规
fact-check → full            事实核查后需要更深入研究
quick → full                 快速研究后发现值得深入
review → full                审查后需要重新研究
systematic-review → academic-paper  将系统综述撰写为论文
```

### deep-research 到 academic-paper 模式映射

| deep-research 模式 | 产出 | 映射到 academic-paper 模式 | 说明 |
|-------------------|------|--------------------------|------|
| `full` | 完整研究报告 | `full` 或 `revision` | 研究完成，进入论文撰写 |
| `socratic` | 研究计划摘要 | `plan` | 研究方向确定，规划论文结构 |
| `lit-review` | 附注参考文献列表 + 综合分析 | `full`（基于文献） | 文献综述完成，开始撰写论文 |
| `quick` | 研究简报 | `plan`（需要扩展） | 初步探索完成，规划完整论文 |
| `review` | 审查报告 | 不映射 | 审查结束，修改原论文 |
| `fact-check` | 核查报告 | 不映射 | 事实核查结束 |
| `systematic-review` | PRISMA 报告 + 森林图 + GRADE 表 | `full`（系统综述论文） | 系统综述完成，撰写为期刊论文 |

### deep-research 与 academic-paper-reviewer 模式映射

| deep-research `review` 模式 | academic-paper-reviewer |
|------------------------------|------------------------|
| 3 个 Agent（Editor + DA + Ethics） | 专用论文审查技能 |
| 适用于任何文本的质量审查 | 专为学术论文审查流程设计 |
| 产出 Editorial Verdict | 产出结构化审查意见 |
| 推荐用于：初稿筛选、非学术文本 | 推荐用于：正式投稿前审查 |

---

## 完整学术研究流水线

```
Step 1: deep-research (socratic/full)
          ↓ 研究计划 / 完整报告
Step 2: academic-paper (plan/full)
          ↓ 论文草稿
Step 3: academic-paper-reviewer (full/guided)
          ↓ 审查意见
Step 4: academic-paper (revision)
          ↓ 修改后的论文
Step 5: [重复步骤 3-4 直到通过]
          ↓ 最终论文
```

---

## 模式切换矩阵

研究过程中切换模式的规则。并非所有切换都是安全的。

### 切换：quick → full
- **时机**：快速简报揭示主题比预期更复杂
- **可复用**：RQ Brief（原样）、初始关键词列表
- **必须重做**：完整文献搜索（quick 仅使用 5-8 个来源）、综合分析、验证
- **质量差距**：full 模式要求 15+ 个来源、3+ 个数据库、正式方法论设计

### 切换：lit-review → full
- **时机**：文献综述发现值得用原创方法论研究的空白
- **可复用**：完整参考文献、综合分析主题、证据空白分析
- **必须重做**：研究设计（methodology_patterns）、数据收集计划、伦理审查（如为原创研究）
- **质量差距**：full 模式增加原创研究设计；lit-review 仅为二次分析

### 切换：socratic → full
- **时机**：苏格拉底对话产生了成熟的研究问题 (RQ)，用户希望进行自主研究
- **可复用**：RQ Brief（含 socratic_insights）、积累的 INSIGHTs、范围界定
- **必须重做**：RQ 形成之后的所有内容（参考文献、综合分析、验证、报告）
- **质量差距**：socratic 模式仅产出 RQ Brief；full 模式执行完整流水线

### 切换：fact-check → full
- **时机**：事实核查揭示某项主张是一个更大争议话题的一部分，值得深入研究
- **可复用**：已验证/已驳斥的主张、来源验证结果
- **必须重做**：RQ 形成（从验证重新构建为探究）、完整参考文献、综合分析
- **质量差距**：fact-check 是二元的（真/假/混合）；full 模式产出细致入微的分析

### 切换：lit-review → systematic-review
- **时机**：文献综述发现主题值得正式 PRISMA 合规（例如，投稿需要它的期刊）
- **可复用**：初始关键词策略、部分已识别来源（需重新筛选）
- **必须重做**：研究方案注册、正式纳入/排除标准、双人筛选、偏倚风险评估、Meta分析可行性评估
- **质量差距**：systematic-review 需要研究方案、偏倚风险评估、GRADE；lit-review 均无

### 切换：systematic-review → academic-paper
- **时机**：系统综述完成，用户希望将其撰写为期刊论文
- **可复用**：全部内容 — PRISMA 报告实质上就是论文草稿
- **必须重做**：按目标期刊要求格式化、摘要重写
- **质量差距**：极小 — 系统综述产出已按 PRISMA 2020 结构化

### 禁止的切换
- **full → quick**：不能将完整研究降级为快速简报（丧失严谨性）
- **任何 → socratic**：苏格拉底模式仅作为入口；不能在流水线中途切换进入
- **paper-review → full**：论文审查评估已有工作；full 模式创建新研究。两者属于根本不同的任务
