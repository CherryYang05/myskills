# 系统综述模式 — 完整方案（Protocol）

符合 PRISMA 规范的系统文献综述（Systematic Review），可选 Meta分析（Meta-analysis）。此模式在标准6阶段流水线基础上，增加了专门用于偏倚风险（Risk of Bias, RoB）评估（RoB 2、ROBINS-I）和定量合成（Quantitative Synthesis）的 Agent。

详细的 Agent 定义参见 `agents/risk_of_bias_agent.md` 和 `agents/meta_analysis_agent.md`。
Cochrane/PRISMA/GRADE 参考指南参见 `references/systematic_review_toolkit.md`。

## 5阶段流水线

```
User: "Systematic review of [topic]" / "Meta-analysis of [topic]"
     |
=== Phase 1: SCOPING (Generates Protocol, not just RQ) ===
     |
     |-> [research_question_agent] -> PICOS-formatted RQ
     |   - Population, Intervention, Comparator, Outcome, Study design
     |   - Explicit eligibility criteria (inclusion/exclusion)
     |
     |-> [research_architect_agent] -> Systematic Review Protocol
     |   - Protocol follows PRISMA-P 2015 (templates/prisma_protocol_template.md)
     |   - Pre-specified subgroup analyses and sensitivity analyses
     |   - Risk of bias tool selection (RoB 2 / ROBINS-I)
     |   - Meta-analysis feasibility pre-assessment
     |
     +-> [devils_advocate_agent] -- CHECKPOINT 1
         - PICOS specificity check
         - Search strategy comprehensiveness
         - Protocol completeness
         - Verdict: PASS / REVISE
     |
     ** User confirmation of protocol before Phase 2 **
     |
=== Phase 2: INVESTIGATION (PRISMA-Compliant Search + RoB) ===
     |
     |-> [bibliography_agent] -> PRISMA Flow Diagram + Source Corpus
     |   - Search >= 2 databases with documented strategy
     |   - Dual-pass screening (title/abstract -> full text)
     |   - PRISMA 2020 flow diagram with counts at each stage
     |   - Excluded studies with reasons documented
     |
     |-> [source_verification_agent] -> Verified Sources
     |   - Standard verification + predatory journal screening
     |
     +-> [risk_of_bias_agent] -> RoB Assessment
         - Per-study domain assessment with signaling questions
         - Traffic-light summary table across all studies
         - Distribution summary (% Low / Some Concerns / High)
     |
=== Phase 3: ANALYSIS (Meta-Analysis or Narrative Synthesis) ===
     |
     |-> [meta_analysis_agent] -> Quantitative or Narrative Synthesis
     |   - Feasibility assessment (pool or not?)
     |   - If feasible: effect size calculation, forest plot data,
     |     heterogeneity (I-squared, Q, tau-squared), subgroup/sensitivity analyses
     |   - If not feasible: structured narrative synthesis (SWiM)
     |   - GRADE certainty of evidence for each outcome
     |
     |-> [synthesis_agent] -> Qualitative Themes + Gap Analysis
     |   - Thematic synthesis across studies
     |   - Integration with quantitative findings
     |
     +-> [devils_advocate_agent] -- CHECKPOINT 2
         - Cherry-picking check
         - Heterogeneity explanation adequacy
         - GRADE assessment validity
         - Verdict: PASS / REVISE
     |
=== Phase 4: COMPOSITION ===
     |
     +-> [report_compiler_agent] -> PRISMA 2020 Report
         - Uses templates/prisma_report_template.md
         - All 27 PRISMA items mapped to sections
         - Study characteristics table
         - Risk of bias summary table
         - Forest plot data (if meta-analysis)
         - GRADE Summary of Findings table
     |
=== Phase 5: REVIEW (Parallel) ===
     |
     |-> [editor_in_chief_agent] -> Editorial Verdict
     |-> [ethics_review_agent] -> Ethics Clearance
     +-> [devils_advocate_agent] -- CHECKPOINT 3
     |
=== Phase 6: REVISION ===
     |
     +-> [report_compiler_agent] -> Final PRISMA Report
```

## 检查点规则

1. 所有标准检查点规则均适用（参见 SKILL.md 检查点规则）
2. **方案必须在阶段2之前注册**（或建议注册）
3. **偏倚风险（RoB）必须在阶段3之前对所有研究完成评估**
4. **每个合并结果均需进行 GRADE 评估**
5. **阶段5需验证 PRISMA 清单合规性**
