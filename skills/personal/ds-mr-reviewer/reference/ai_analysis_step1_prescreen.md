> **【强制声明】本文档为规则初筛降维流程（当初始 batch_count > 2 时触发）。AI必须完整阅读并严格按照本流程执行，以避免 Token 超载。**

# 规则初筛降维流程 (Step1-Pre)

当前规则数量过于庞大，为兼顾效率与成本，必须在深度检视前进行“混合初筛”，剔除绝大部分无关规则。

### Step1-Pre.1：获取混合初筛数据

**执行**：
```bash
python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --prescreen-data
```

你将得到一个 JSON 结果，包含：
- `hard_matched_rules`：脚本依靠字面量精确匹配已命中的规则列表（这些规则已确定需要检视）。
- `pending_rules_to_llm`：脚本未命中的规则ID及其对应的 `checkpoint`（需要你进行语义兜底判定）。

### Step1-Pre.2：执行 LLM 语义初筛

**【强制判定任务】：**
结合 Step0 中读取的完整 diff 内容，对 `pending_rules_to_llm` 字典中的每一条规则进行轻量级判定。
- **判定原则（宁滥勿缺）**：只要 Diff 中有任何修改，在语义上、操作类型上可能涉及该 checkpoint 描述的场景（例如变种写法、间接调用），就必须判定为命中。
- **无需深度推理**：不要在此步骤判断代码是否真的违规，只要有一丝相关可能，即予保留。

**合并规则集**：
将你自己判定为“命中”的 rule_ids 与脚本给出的 `hard_matched_rules` 列表合并。去重后，得到一个最终的规则列表，并用逗号拼接成字符串（例如："JAVA-SEC-001,JAVA-PERF-002,COM-001"）。将此字符串记为 `active_rules`。

### Step1-Pre.3：生成动态分批计划并跳转

将上一步合并得到的 `active_rules` 字符串，传入脚本重新生成分批计划：

```bash
python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --batch-plan --active-rules "<这里替换为你合并后的 active_rules 字符串>"
```

根据重新输出的 `batch_count`，决定最终的检视路径：
- **如果 `batch_count == 1`** → 读取 **[单批检视流程](ai_analysis_step1_single.md)** 并执行。
- **如果 `batch_count > 1`** → 读取 **[分批检视流程](ai_analysis_step1_batch.md)** 并执行。