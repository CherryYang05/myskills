## [2.9.1] - 2026-04-22

### 新增

- **可选阅读检查探针（reading-check probe）**，位于 Socratic Mentor 中。通过 `ARS_SOCRATIC_READING_PROBE=1` 启用。参见 `agents/socratic_mentor_agent.md` §"Optional Reading Probe Layer" 和 `SKILL.md` §"Opt-in Reading Probe (v3.5.1)"。

### 版本

- 2.9.0 → 2.9.1（补丁版本；可选功能，默认关闭）。

---

# 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.4 | 2026-03-27 | 报告编译器（Report compiler）现在可消费可选的 Style Profile（来自学术论文 intake），并在确定报告前运行 Writing Quality Check 检查清单（checklist）。Style Profile 作为 Executive Summary 和 Synthesis 章节的软性指导；学科规范优先。Writing Quality Check 检查清单可捕获过度使用的 AI 典型词汇、破折号过度使用、开头废话及单调句式节奏。参见 `academic-paper/references/writing_quality_check.md` 和 `shared/style_calibration_protocol.md` |
| 2.3 | 2026-03-08 | 新增 systematic-review 模式（第7种模式）：符合 PRISMA 2020 的流水线（pipeline），配备 risk_of_bias_agent（偏倚风险评估 Agent，RoB 2 + ROBINS-I）、meta_analysis_agent（效应量、异质性、GRADE、叙述性综合），2个新模板（PRISMA 协议 + 报告），systematic_review_toolkit 参考文档。新增 monitoring_agent（流水线后文献监控，包含文摘、撤稿预警、作者跟踪）+ literature_monitoring_strategies 参考文档。增强 socratic_mentor_agent，添加4个收敛信号、4类问题分类法和自动结束触发器。在 SKILL.md 中新增 Quick Mode Selection Guide |
| 2.2 | 2026-03-05 | 新增综合反模式（synthesis anti-patterns）、Socratic 量化阈值与自动结束条件、参考文献存在性验证（DOI + WebSearch）、增强伦理参考完整性检查（50% + Retraction Watch）、模式转换矩阵（mode transition matrix）、跨 Agent 质量对齐定义 |
| 2.1 | 2026-03 | 新增 IRB 决策树、EQUATOR 报告指南、预注册指南 + 模板；增强 ethics_review_agent，增加受试者维度；增强 research_architect_agent，集成伦理/EQUATOR/预注册；增强 methodology_patterns，添加 EQUATOR 交叉引用 |
| 2.0 | 2026-02 | 新增 Socratic 模式（第10个 Agent）、失败路径（failure paths）、模式选择指南（mode selection guide）、交接协议（handoff protocol）、2个新示例、3个新参考文档 |
| 1.0 | 2026-02 | 初始发布：9个 Agent，5种模式，6阶段流水线（pipeline） |
