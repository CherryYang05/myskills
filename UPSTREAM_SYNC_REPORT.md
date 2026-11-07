# 外部 Skill 同步与修正报告

检查周期（北京时间）：2026-W45

仅检查 `skill-sync/upstreams.json` 登记的外部 Skill；自研 Skill 不参与上游替换。
本报告随更新候选生成。只有候选通过 CI 并合并到 master 后，才代表已完成同步；失败详情以 Actions 日志为准。

| Skill | 检查结果 | 更新前版本 | 候选版本 | 文件变化数 | 上游提交 |
|---|---|---|---|---|---|
| deep-research | 已准备同步 | v2.11.1 | 6d9388674de1 | 56 | [6d9388674de1](https://github.com/Imbad0202/academic-research-skills/commit/6d9388674de1ad0437ad95db3d52f92b92204d84) |
| frontend-design | 无变化 | ca45fc4 | ca45fc4 | 0 | [2c5958ecac7c](https://github.com/anthropics/skills/commit/2c5958ecac7cee2b583967a2c4981d0f4a75c579) |
| humanizer | 已准备同步 | v3.1.0 | 0ef9fe5bc357 | 13 | [0ef9fe5bc357](https://github.com/blader/humanizer/commit/0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0) |
| impeccable | 已准备同步 | 4.8.0 (c3bb418) | 687bc381bc90 | 2 | [687bc381bc90](https://github.com/pbakaus/impeccable/commit/687bc381bc9091bf252c0a05303640561014a425) |
| mermaid-diagrams | 已准备同步 | 3027f20 | 3027f20f3181 | 2 | [3027f20f3181](https://github.com/softaworks/agent-toolkit/commit/3027f20f3181758385a1bb8c022d4041dfb4de84) |
| shadcn | 已准备同步 | 4aaea19 | 42f3bb63b46a | 3 | [42f3bb63b46a](https://github.com/shadcn-ui/ui/commit/42f3bb63b46a69e52a24bd005cdc9ec15ba7a7b9) |
| skill-creator | 无变化 | b9e19e6 | b9e19e6 | 0 | [2c5958ecac7c](https://github.com/anthropics/skills/commit/2c5958ecac7cee2b583967a2c4981d0f4a75c579) |
| web-design-guidelines | 已准备同步 | 1a2c79d | 1a2c79d4e6c4 | 1 | [1a2c79d4e6c4](https://github.com/vercel-labs/agent-skills/commit/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62) |

## 文件修正明细

### deep-research

[详细报告](./docs/upstream-reports/deep-research.md)

- modified: SKILL.md
- modified: agents/bibliography_agent.md
- modified: agents/devils_advocate_agent.md
- modified: agents/editor_in_chief_agent.md
- modified: agents/ethics_review_agent.md
- modified: agents/meta_analysis_agent.md
- modified: agents/monitoring_agent.md
- modified: agents/report_compiler_agent.md
- modified: agents/research_architect_agent.md
- modified: agents/research_question_agent.md
- modified: agents/risk_of_bias_agent.md
- modified: agents/socratic_mentor_agent.md
- modified: agents/source_verification_agent.md
- modified: agents/synthesis_agent.md
- modified: agents/timeline_extraction_agent.md
- modified: examples/exploratory_research.md
- modified: examples/fact_check_mode.md
- modified: examples/handoff_to_paper.md
- modified: examples/idea_diversity_coverage_gap_advisory.md
- modified: examples/policy_analysis.md
- modified: examples/review_mode.md
- modified: examples/socratic_guided_research.md
- modified: examples/systematic_review.md
- modified: references/apa7_style_guide.md
- modified: references/argumentation_reasoning_framework.md
- modified: references/arxiv_api_protocol.md
- modified: references/changelog.md
- modified: references/chinese_literature_api_protocol.md
- modified: references/cross_agent_quality_definitions.md
- modified: references/crossref_api_protocol.md
- modified: references/equator_reporting_guidelines.md
- modified: references/ethics_checklist.md
- modified: references/failure_paths.md
- removed: references/handoff_and_ledger_safety.md
- modified: references/interdisciplinary_bridges.md
- modified: references/irb_decision_tree.md
- modified: references/literature_monitoring_strategies.md
- removed: references/local_sync_notes.md
- modified: references/logical_fallacies.md
- removed: references/method_weaknesses.md
- modified: references/methodology_patterns.md
- modified: references/mode_selection_guide.md
- modified: references/openalex_api_protocol.md
- modified: references/preregistration_guide.md
- modified: references/semantic_scholar_api_protocol.md
- modified: references/socratic_mode_protocol.md
- modified: references/socratic_questioning_framework.md
- modified: references/source_quality_hierarchy.md
- modified: references/systematic_review_protocol.md
- modified: references/systematic_review_toolkit.md
- modified: templates/evidence_assessment_template.md
- modified: templates/literature_matrix_template.md
- modified: templates/preregistration_template.md
- modified: templates/prisma_protocol_template.md
- modified: templates/prisma_report_template.md
- modified: templates/research_brief_template.md

### humanizer

[详细报告](./docs/upstream-reports/humanizer.md)

- added: .claude-plugin/marketplace.json
- added: .claude-plugin/plugin.json
- added: .cursor-plugin/plugin.json
- added: .github/ISSUE_TEMPLATE/config.yml
- added: .github/ISSUE_TEMPLATE/new-pattern.yml
- added: .github/ISSUE_TEMPLATE/rewrite-problem.yml
- added: .github/workflows/validate.yml
- added: AGENTS.md
- added: CHANGELOG.md
- added: LICENSE
- added: README.md
- added: agents/openai.yaml
- added: scripts/validate-package.py

### impeccable

[详细报告](./docs/upstream-reports/impeccable.md)

- removed: UPSTREAM.md
- modified: scripts/impeccable.cmd

### mermaid-diagrams

[详细报告](./docs/upstream-reports/mermaid-diagrams.md)

- removed: LICENSE
- removed: UPSTREAM.md

### shadcn

[详细报告](./docs/upstream-reports/shadcn.md)

- removed: LICENSE.md
- modified: SKILL.md
- removed: UPSTREAM.md

### web-design-guidelines

[详细报告](./docs/upstream-reports/web-design-guidelines.md)

- removed: UPSTREAM.md

