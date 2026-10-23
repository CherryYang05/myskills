# deep-research 本地上游同步记录

- **当前同步基线**：上游 deep-research `v2.11.1`；本地是中文翻译、结构适配与独立安装降级版本。
- **已选择性吸收**：`c6222bb914a0`（#938，RQ Brief FINER 1–5 与 scope 字段）；`08046bd744c6`（#898，可信 ledger 读取约束，未带脚本）；`a3ef8c79d888`（#973，Hook 防护适用边界，部分）；`3224a27a2571`（#990/#992，缺少必需材料的阶段阻断与 Socratic 非生成边界）。中文 DOI 核验另参考上游 #595，未移植执行客户端。
- **尚未同步的上游版本**：上游 `deep-research/SKILL.md` 为 `2.12.1`；上游整个 academic-research-skills 仓库的 Release `v3.23.1` 是**项目级**版本，不可误写为本地 deep-research 的 Skill 版本。
- **未集成的运行时依赖**：`academic-pipeline/`、`shared/`、`scripts/run_ledger.py`、`scripts/chinese_literature_client.py`、Hook 配置和相关完整性校验器。本地提示层规则不能替代这些机械约束。
- **版本管理原则**：`skill-sync/scripts/gen_readme.py` 中 `EXTERNAL_SOURCES["deep-research"]["version"]` 保留可追溯的已同步基线 `v2.11.1`；`selected_fixes` 逐项记录已适配上游提交。只有全量移植、兼容性验证与 README 生成通过后，才能将基线提升为新的上游 Skill 版本或 commit。
