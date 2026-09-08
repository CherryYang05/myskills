> **【强制声明】本文档为单批检视流程（batch_count == 1）的执行步骤，AI在判断 batch_count == 1 后必须完整阅读并严格按照本流程执行。**

# 单批检视流程（Step1.1~Step1.3）

---

#### Step1.1：读取并加载检视规则

**读取输入文件**：
```bash
python scripts/common/temp_file_reader.py --type analysis_stage0 --repo "{repo}" --mrId {mrId}
```
**规则加载**：
- 使用以下命令读取需要检视的规则内容。为了防止语法错误，请根据情况选择对应的命令执行：
  - **如果主流程中执行了规则初筛**，请务必传递活跃规则池：
    ```bash
    python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --batch-id 1 --active-rules "{active_rules}"
    ```
  - **如果没有执行初筛**，请使用默认命令：
    ```bash
    python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --batch-id 1
    ```
- 规则已由底层自动合并分层（通用/特定仓/语言），AI 无需关心规则的分层来源，直接基于上述命令输出的 Markdown 规则内容进行检视。
---

#### Step1.2：逐文件逐规则进行锚点匹配与检视

**锚点匹配过滤流程**：
1. 遍历每条规则的 checkpoint。
2. **[匹配方式约束]**：对 checkpoint 与 diff 变更点进行**精确的关键字、代码特征与语法对位匹配（严禁使用宽泛的"语义匹配"去脑补）**。
3. **[防跳过约束]**：**严禁**基于 MR 的标题、描述或整体业务意图（如“配置重构”）主观推断规则是否适用！即使是修改配置的 MR，只要代码中出现了规则涉及的函数、格式化占位符或自定义宏，就必须强制触发该规则检查。
4. 标记每条规则的相关性：相关 / 可能相关 / 不相关。得出"不涉及"结论的**唯一合法前提**是：你已经逐行扫描了 diff 代码，且确定完全没有出现该规则对应的任何特征或关键字。
5. **所有规则都必须输出结果**（不相关标记为"不涉及"），确保无遗漏。

**逐条检视**：
- 对diff中的每一个函数进行代码检视（单个文件 diff 用 `--file` 参数获取）
- 必须严格遍历每个函数的每一个规则条目进行检视
- **禁止**跳过任何一个规则
- **禁止**合并检查规则
- 每个函数的每个规则检视完后，必须输出检视结果

**selfCheck 输出格式**：
```json
{
  "selfCheck": {
    "JAVA-SEC-001": "通过",
    "JAVA-SEC-002": "违规:在ConfigLoader.java第45行硬编码数据库密码",
    "JAVA-CON-001": "不涉及",
    "COM-001": "违规:修改了缓存刷新逻辑但未验证数据一致性"
  }
}
```

格式规则：
- rule_id 为 key 的扁平结构
- 值为 3 种之一：`"通过"` / `"违规:具体说明"` / `"不涉及"`
- 只有违规才需要写详细说明，通过和不涉及只写状态

---

#### Step1.3：生成analysis_stage1.json

**前置条件**：Step1.1 ~ Step1.2 全部完成

**输出文件**：analysis_stage1.json

**【重要】输出格式必须严格遵守模板**：

用 read 工具读取示例文件理解格式：
```
reference/analysis_example/analysis_stage1_example.json
```

**示例文件字段结构**：
- `rules_applied`：应用规则总数（整数）
- `rules_related`：相关规则数（整数）
- `rules_violated`：违规规则数（整数）
- `selfCheck`：每条规则的检视结果（对象，key为rule_id，值为`"通过"`/`"违规:说明"`/`"不涉及"`）
- `violation_details`：违规详情列表（数组，每个元素包含rule_id/title/file/line/description/suggestion）

**写入步骤**：
1. 先调用 `python scripts/common/temp_file_path_helper.py --type analysis_stage1 --repo "{repo}" --mrId {mrId}` 获取路径
2. 使用 write 工具直接写入该路径

**完成标志**：
- [ ] JSON文件已生成到正确路径
- [ ] 所有加载的规则都在 selfCheck 中有输出
- [ ] 每条违规都有对应的 violation_details 条目

**完成后更新Todo**：将 Step1 状态更新为 completed，Step1 结束
