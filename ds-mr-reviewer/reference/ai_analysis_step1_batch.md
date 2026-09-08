> **【强制声明】本文档为并行分批检视流程（batch_count > 1）的执行步骤，AI在判断 batch_count > 1 后必须完整阅读并严格按照本流程执行。**

# 并行分批检视流程（Step1-P1~Step1-P2）

将规则按批次拆分，每个批次由独立 subagent 并行检视，最后合并结果。

**输出保证**：合并后生成的 `analysis_stage1.json` 格式与单批流程完全一致，后续 Stage 无感知。

---

#### Step1-P1：并行 spawn subagent 执行各批次检视

对 batch_plan 中的每个批次，使用 Agent 工具 spawn 独立的 subagent **并行**执行。

**所有批次的 subagent 必须在一条消息中同时 spawn，不要逐个串行。**

**subagent prompt 模板**：

每个 subagent 的 prompt 必须包含以下内容：

```
## 任务：MR 规则分批检视 - Batch {batch_id}/{batch_count}

### MR 基本信息
- 标题：{mr_title}
- 描述：{mr_description}
- 源分支：{source_branch}
- 目标分支：{target_branch}

### 你负责的规则
本批次共 {rule_count} 条规则，Rule IDs：{rule_ids_comma_separated}

### 执行步骤

1. **读取本批规则内容**：
   - 必须通过以下命令获取本批次规则。为了防止语法错误，请根据情况选择对应的命令：
     - **如果主 Agent 进行了规则初筛**，必须传递规则池：
       `python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --batch-id {batch_id} --active-rules "{active_rules}"`
     - **若未进行初筛**，请执行：
       `python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --batch-id {batch_id}`

2. **读取 MR diff**：
   python scripts/2-ai-analysis/mr_diff_reader.py --repo "{repo}" --mrId {mrId}

3. **读取 Step0 分析结果**（用于理解文件上下文和已识别风险）：
   python scripts/common/temp_file_reader.py --type analysis_stage0 --repo "{repo}" --mrId {mrId}

4. **逐文件逐规则进行代码特征匹配与检视**：
   - 只检视本批次的规则（Rule IDs 中列出的规则）。
   - [匹配方式约束]：对 diff 中的每一个函数，遍历本批每条规则的 checkpoint 进行**精确的关键字、代码特征与语法对位匹配（严禁宽泛的"语义匹配"）**。
   - [防跳过约束]：**严禁**基于 MR 的标题、描述或整体业务意图（如“配置重构”）主观推断规则是否适用！即使是改配置的 MR，只要代码中出现了规则涉及的函数、格式化占位符（如 %s, %d）或自定义日志宏（如 QOS_PRINT_LIMIT），就必须强制执行规则检查。
   - [判定依据]：标记每条规则为 相关/可能相关/不相关。得出"不涉及"结论的**唯一合法前提**是：你已经逐行扫描了 diff 代码，且确定完全没有出现该规则对应的任何特征或关键字。
   - 所有本批规则都必须输出结果，禁止跳过任何规则，禁止合并检查规则。

5. **输出 analysis_stage1_batch{batch_id}.json**：
   - 先获取路径：python scripts/common/temp_file_path_helper.py --type analysis_stage1_batch --repo "{repo}" --mrId {mrId}
   - 拿到路径后，将文件名从 "analysis_stage1_batch.json" 改为 "analysis_stage1_batch{batch_id}.json"（如 analysis_stage1_batch1.json）
   - 使用 write 工具写入该路径

6. **输出格式**（与 analysis_stage1.json 相同结构，但只包含本批规则）：
   {
     "rules_applied": 本批规则数,
     "rules_related": 本批相关规则数,
     "rules_violated": 本批违规规则数,
     "selfCheck": { 仅本批 rule_id 的检视结果 },
     "violation_details": [ 本批违规详情 ]
   }

   selfCheck 值为 3 种之一："通过" / "违规:具体说明" / "不涉及"
   violation_details 每项包含：rule_id, title, file, line, description, suggestion
```
---

#### Step1-P2：合并所有批次结果

**前置条件**：所有 subagent 已完成，所有 `analysis_stage1_batch{i}.json` 已生成。

```bash
python scripts/2-ai-analysis/mr_batch_merger.py --repo "{repo}" --mrId {mrId}
```

**验证**：确认 `analysis_stage1.json` 已生成且包含所有规则的 selfCheck 条目。

**完成后更新Todo**：将 Step1 状态更新为 completed，Step1 结束
