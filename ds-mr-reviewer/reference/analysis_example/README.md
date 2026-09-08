# Analysis Stage Examples

本目录包含MR检视分析各阶段的JSON Schema示例文件，用于指导AI生成正确的分析结果格式。

## 文件说明

- **analysis_stage0_example.json** - 阶段0：理解与文件检视的输出格式示例（含调用链分析、initial_risk初判）
- **analysis_stage1_example.json** - 阶段1：规则检视的输出格式示例（rule_id扁平selfCheck、violation_details）
- **analysis_stage2_example.json** - 阶段2：风险评估与报告格式化的输出格式示例（风险等级、报告格式化字段、验证场景）

## 使用方法

请确保AI生成的JSON内容符合对应的格式，以保证后续流程正常执行。

## 详细格式定义

各阶段的完整格式定义请参考 `reference/ai_analysis.md` 中各阶段的"JSON 产出格式"部分。
