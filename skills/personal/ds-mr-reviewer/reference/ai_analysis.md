> **【强制声明】本文档为AI代码检视步骤2（AI深度分析）的完整执行流程。AI在执行步骤2时，必须完整阅读本文档并严格按照所有规定执行，不得跳过任何步骤或修改既定逻辑。**

# AI 代码检视分析流程

## 检视核心目标

1. **TOP1：发现功能修改引入的风险** - 修改代码导致已有功能不可用、已有功能部分场景行为与预期不一致、严重性能劣化等
2. **TOP2：评估自验证场景完整性** - 帮助开发者发现自测遗漏的场景

---

## 本次分析任务清单

**【重要】开始执行前，必须先用 todowrite 工具创建以下任务列表，后续每完成一项必须更新其状态为 completed：**

```
todowrite --todos [
  {content: "Step0: 理解MR整体信息 + 逐文件深度探索", status: "pending", priority: "high"},
  {content: "Step1: 加载检视规则 + 逐文件逐规则锚点匹配与检视", status: "pending", priority: "high"},
  {content: "Step1.5: 缺陷模式深度扫描（5组Agent并行语义级缺陷检测）", status: "pending", priority: "high"},
  {content: "Step2: 汇总Step0+Step1+Step1.5结果 + 评定风险等级 + 生成分析数据", status: "pending", priority: "high"}
]
```

**完成标志更新规则**：
- Step0、Step2 完成后，立即用 todowrite 更新状态为 completed
- Step1 和 Step1.5 在各自 subagent 返回后，分别更新状态为 completed
- **禁止**在 Step0 未完成时启动 Step1 或 Step1.5
- **禁止**在 Step1 和 Step1.5 都未完成时进入 Step2

---

**强制顺序约束**：
- **Step0 必须先完成**，产出 `analysis_stage0.json`
- Step0 完成后，**Step1 与 Step1.5 并行执行**（两者无数据依赖，只共享 Step0 的输出）
- Step1 和 Step1.5 **都完成后**，才能进入 Step2
- 同一 Step 内部的子步骤按编号顺序执行（Step0.1 → Step0.2 → ... → Step0.4，Step1.5.1 → ... → Step1.5.6）
- 禁止认为"改动简单"就跳过任何 Step

---

## Step0：理解与文件检视

**目标**：理解 MR 整体意图 + 对每个核心文件做深度探索（含调用链）**+ 发现并记录可能存在的风险**，产出 `analysis_stage0.json`。

**【重要】Step0 的核心职责之一是发现风险**：
- 基于对代码修改内容的理解，识别可能存在的风险点
- 这些风险可能来自：业务逻辑缺陷、边界条件遗漏、数据一致性隐患、异常场景未处理等
- Step0 发现的风险记录在 `identified_risks` 字段中
- Step1 基于规则继续检视，两者的风险发现是**互补关系**，不是替代关系

### Step0.1：读取coordinator.json并理解MR整体信息

**执行**：读取coordinator文件
```bash
python scripts/common/temp_file_reader.py --type coordinator --repo "{repo}" --mrId {mrId}
```

从 coordinator JSON 中获取：
- `mr_related_repo_path`：需要搜索的代码仓路径列表（主仓路径在第一位，后续是 depend_repo 路径）
- **后续所有在本地代码仓中的搜索文件，都在此列表中的目录下进行**

**读取 diff**：使用 `mr_diff_reader.py` 获取完整 diff 内容（直接读 coordinator.json 会因 Read 工具限制而截断）：
```bash
# 读取全部diff
python scripts/2-ai-analysis/mr_diff_reader.py --repo "NCE-T_TransAvailabilityAssuranceService" --mrId 998

# 读取单个文件的diff（支持部分路径匹配，如 "FiberGroupBusinessV2Impl.java"）
python scripts/2-ai-analysis/mr_diff_reader.py --repo "NCE-T_TransAvailabilityAssuranceService" --mrId 998 --file "srlgdetect/src/main/java/com/huawei/nce/transavailabilityassuranceservice/srlgdetect/business/impl/FiberGroupBusinessV2Impl.java"
```
- 输出包含 `---DIFF_START---` 和 `---DIFF_END---` 包裹的完整 diff

---

### Step0.2：分析MR整体意图

1. **分析 MR 标题** - 提取核心关键词，判断变更类型
2. **分析 MR 描述** - 修改背景、技术方案、自验证结果
3. **分析整体 diff** - 统计修改文件数量和类型，识别核心变更文件（用上一步的 `mr_diff_reader.py` 输出分析）
4. **总结变更目的** - 用一句话概括本次 MR 的核心目标

---

### Step0.3：逐文件深度探索

对每个核心文件，按需执行以下探索：

1. **文件职责与修改影响范围** - 理解文件在业务架构中的位置，修改可能波及的范围
2. **上下行调用链追踪**（针对中高风险变更）：
   - 上游：谁调用了被修改的函数（追踪2-3层）
   - 下游：被修改的函数调用了谁（追踪直接依赖）
3. **修改点关联的业务逻辑和数据流** - 识别修改影响的业务场景和数据流转
4. **风险识别** - 基于以上分析给出初步风险等级
5. **【重要】识别并记录可能存在的风险** - 基于对代码修改内容的理解，识别以下类型的风险：
   - 基础的逻辑缺陷或语法缺陷等
   - 业务逻辑缺陷
   - 边界条件遗漏
   - 数据一致性隐患
   - 异常场景未处理
   - 空指针/数组越界等潜在异常
   - 其他基于业务理解的合理风险推断

---

### Step0.4：生成analysis_stage0.json

**前置条件**：Step0.1 ~ Step0.3 全部完成

**输出文件**：analysis_stage0.json

**【重要】输出格式必须严格遵守模板**：

用 read 工具读取示例文件理解格式：
```
reference/analysis_example/analysis_stage0_example.json
```

**示例文件字段结构**：
- `change_intention`：变更意图（字符串）
- `change_type`：变更类型（字符串）
- `core_files`：核心文件列表（数组）
- `mr_summary`：MR概述（字符串）
- `file_analysis`：每个核心文件的分析结果（对象，key为文件路径）
- `identified_risks`：该文件相关的风险列表（数组，每个元素包含id/problem/location/description/mitigation）

**写入步骤**：
1. 先调用 `python scripts/common/temp_file_path_helper.py --type analysis_stage0 --repo "{repo}" --mrId {mrId}` 获取路径
2. **【强制安全校验】获取路径后，必须先使用 read 工具读取该路径（即使你确信这是个新文件或空文件，也必须执行 read 动作，否则底层系统会拦截写入操作）。**
3. 使用 write 工具直接写入该路径（**必须**遵循示例文件的字段结构和格式）

**完成标志**：
- [ ] JSON文件已生成到正确路径
- [ ] change_intention 和 change_type 已明确
- [ ] 每个核心文件都有 file_analysis 条目
- [ ] 每个文件的 initial_risk 已评定
- [ ] 每个文件已识别并记录可能存在的风险到 identified_risks

**完成后更新Todo**：将 Step0 状态更新为 completed，Step0 结束

---

## Step0 完成后：并行启动 Step1 与 Step1.5

Step0 完成（`analysis_stage0.json` 写入）后，在**同一条消息中**同时 spawn 两个 subagent：（均 `run_in_background: true`）：

| Subagent | 任务 | Prompt 要点 |
|----------|------|-------------|
| `step1-rules-review` | 执行 Step1 | 读取 `analysis_stage0.json`，然后完整阅读 [Step1 章节](#step1规则检视) 并按其执行，输出 `analysis_stage1.json` |
| `step1_5-defect-scan` | 执行 Step1.5 | 读取 `analysis_stage0.json`，然后完整阅读 [Step1.5 章节](#step15缺陷模式深度扫描) 并按其执行，输出 `analysis_stage1_5.json` |

两个 subagent 都完成后，主 agent 进入 Step2。

---

## Step1：规则检视

**目标**：基于检视规则对变更点做逐条检视，产出 `analysis_stage1.json`。为兼顾效率与成本，规则数量较少时直接并行检视，规则数量极其庞大（拆分批次>2）时，触发”混合初筛”降维。

### Step1.0：判断是否需要规则分批与初筛

**执行**：获取全量规则的分批计划，判断策略路由。
```bash
python scripts/2-ai-analysis/mr_rules_reader.py --repo "{repo}" --mrId {mrId} --batch-plan
```

根据输出的 `batch_count` 决定下一步：
- `batch_count == 1` → **读取 [单批检视流程](ai_analysis_step1_single.md) 并执行**
- `batch_count == 2` → **读取 [分批检视流程](ai_analysis_step1_batch.md) 并执行**
- `batch_count > 2` → **读取 [规则初筛降维流程](ai_analysis_step1_prescreen.md) 并执行**

---

## Step1.5：缺陷模式深度扫描

**目标**：基于9大类36项缺陷模式，对 MR diff 涉及的被修改函数进行语义级缺陷深度扫描，产出 `analysis_stage1_5.json`。

**【重要】Step1.5 与 Step1 的区别**：
- Step1 是基于检视规则（编码规范）的锚点匹配检视
- Step1.5 是基于缺陷模式（语义级缺陷）的深度扫描，聚焦于被修改函数的完整函数体

### Step1.5.1：读取输入文件

**读取输入文件**：
```bash
python scripts/common/temp_file_reader.py --type analysis_stage0 --repo "{repo}" --mrId {mrId}
```

从 `analysis_stage0.json` 中获取：
- `core_files`：核心文件列表
- `file_analysis`：每个文件的分析结果（包含函数级别的修改信息）

### Step1.5.2：读取缺陷检测规则

规则已按 agent 拆分为 5 个专属文件，每个 agent 只需读取自己负责的规则文件（无需读取全量规则）：

| Agent | 规则文件 | 负责类别 | 缺陷项数 |
|-------|---------|---------|---------|
| Agent 1 | `defect_scan_rules/agent1_concurrency.md` | 并发安全类 | 5项 |
| Agent 2 | `defect_scan_rules/agent2_numeric_type.md` | 数值计算类 + 类型系统类 | 6项 |
| Agent 3 | `defect_scan_rules/agent3_pointer_resource.md` | 指针操作类 + 资源管理类 | 8项 |
| Agent 4 | `defect_scan_rules/agent4_memory_assign.md` | 内存操作类 + 内存计算类 + 赋值与引用类 | 11项 |
| Agent 5 | `defect_scan_rules/agent5_error_handling.md` | 错误处理类 | 6项 |

各 agent 在 Step1.5.4 启动时，prompt 中指定读取对应的规则文件。

### Step1.5.3：识别被修改函数

从 diff 中识别被修改的函数：
1. 读取每个核心文件的 diff
2. 从 diff 的 `@@` 行提取函数签名（如果 diff 中包含函数上下文）
3. 如果 diff 中不包含函数签名，从修改的行号向上查找最近的函数定义
4. 记录每个被修改函数的：
   - 函数名
   - 文件路径
   - 函数起始行号
   - 函数结束行号（通过匹配括号确定）

### Step1.5.4：5组Agent并行扫描

**【重要】使用 Agent 工具并行启动5个 subagent**，每个 Agent 负责特定类别的缺陷检测：

| Agent | 名称 | 负责类别 | 缺陷项数 | 规则文件 |
|-------|------|---------|---------|---------|
| Agent 1 | 并发安全类审核 | 并发安全类 | 5项 | `defect_scan_rules/agent1_concurrency.md` |
| Agent 2 | 数值计算与类型系统类审核 | 数值计算类 + 类型系统类 | 6项 | `defect_scan_rules/agent2_numeric_type.md` |
| Agent 3 | 指针与资源管理类审核 | 指针操作类 + 资源管理类 | 8项 | `defect_scan_rules/agent3_pointer_resource.md` |
| Agent 4 | 内存操作与计算及赋值引用类审核 | 内存操作类 + 内存计算类 + 赋值与引用类 | 11项 | `defect_scan_rules/agent4_memory_assign.md` |
| Agent 5 | 错误处理类审核 | 错误处理类 | 6项 | `defect_scan_rules/agent5_error_handling.md` |

**Agent Prompt 构建模板**：

```
你是代码缺陷扫描专家，负责审核【{类别名}】类编码缺陷。

## 缺陷模式定义
请先使用 Read 工具读取你的专属规则文件：reference/defect_scan_rules/{规则文件名}
该文件包含你负责的所有缺陷模式的定义（检测特征、关键词、误报排除、严重度、修复建议）。

## 扫描目标
以下函数是 MR diff 中被修改的函数，需要对每个函数的**完整函数体**进行扫描：

{函数列表，每个函数包含：文件路径、函数名、起始行号、结束行号}

代码库根目录: {mr_related_repo_path}

## 扫描步骤
1. 使用Read工具逐个读取目标文件
2. 定位到被修改函数的起始行号
3. 读取完整函数体（从函数签名到结束括号）
4. 根据缺陷模式的检测特征和关键词，搜索可疑代码
5. 读取完整函数体上下文
6. 根据代码特征判断是否为真正缺陷
7. 应用误报排除规则过滤
8. 确认缺陷后记录详细信息

## 输出格式
返回JSON数组（不要markdown代码块标记）：
[
  {
    "file": "文件相对路径",
    "line": 123,
    "pattern": "缺陷模式名称",
    "category": "所属大类",
    "severity": "严重/中等/轻度",
    "description": "问题描述",
    "code_snippet": "关键代码片段（原样复制，不要改写）",
    "root_cause": "根因分析",
    "fix_suggestion": "修复建议",
    "confidence": "高/中/低"
  }
]

## 重要规则
- 只报告有明确代码证据的问题
- 忽略test/mock/stub/diagnose代码
- 忽略static inline工具函数
- 没有检测到缺陷返回空数组：[]
- 每条缺陷的code_snippet必须原样复制代码，不要改写或省略
```

**启动方式**：

```python
agents = [
    Agent(prompt=agent1_prompt, name="ai-scan-concurrency", run_in_background=True),
    Agent(prompt=agent2_prompt, name="ai-scan-numeric-type", run_in_background=True),
    Agent(prompt=agent3_prompt, name="ai-scan-pointer-resource", run_in_background=True),
    Agent(prompt=agent4_prompt, name="ai-scan-memory-assign", run_in_background=True),
    Agent(prompt=agent5_prompt, name="ai-scan-error-handling", run_in_background=True),
]
```

### Step1.5.5：合并去重

等待5个Agent完成，收集每个Agent返回的JSON数组。

**去重规则**：
- 同一文件+行号+缺陷模式只保留一条
- 如果多个Agent报告了同一位置的不同缺陷，都保留

### Step1.5.6：生成analysis_stage1_5.json

**前置条件**：Step1.5.1 ~ Step1.5.5 全部完成

**输出文件**：analysis_stage1_5.json

**【重要】输出格式必须严格遵守模板**：

用 read 工具读取示例文件理解格式：
```
reference/analysis_example/analysis_stage1_5_example.json
```

**示例文件字段结构**：
- `scan_files_count`：扫描文件数（整数）
- `scan_functions_count`：扫描函数数（整数）
- `defect_findings`：缺陷发现列表（数组，每个元素包含id/file/line/pattern/category/severity/description/code_snippet/root_cause/fix_suggestion/confidence）

**写入步骤**：
1. 先调用 `python scripts/common/temp_file_path_helper.py --type analysis_stage1_5 --repo "{repo}" --mrId {mrId}` 获取路径
2. **【强制安全校验】获取路径后，必须先使用 read 工具读取该路径（即使你确信这是个新文件或空文件，也必须执行 read 动作，否则底层系统会拦截写入操作）。**
3. 使用 write 工具直接写入该路径（**必须**遵循示例文件的字段结构和格式）

**完成标志**：
- [ ] JSON文件已生成到正确路径
- [ ] scan_files_count 和 scan_functions_count 已统计
- [ ] 每条缺陷的 code_snippet 必填且是原样复制的代码（非空、非注释、非自然语言描述）
- [ ] 每条缺陷的 pattern、category、severity 已明确

**完成后更新Todo**：将 Step1.5 状态更新为 completed，Step1.5 结束

---

## Step2：风险评估与数据分析

**目标**：汇总 Step0 + Step1 + Step1.5 的分析结果，评定风险等级，生成分析数据，产出 `analysis_stage2.json`。

---

### Step2.1：汇总Step0+Step1+Step1.5结果并评定风险等级

**读取输入文件**：
```bash
python scripts/common/temp_file_reader.py --type analysis_stage0 --repo "{repo}" --mrId {mrId}
python scripts/common/temp_file_reader.py --type analysis_stage1 --repo "{repo}" --mrId {mrId}
python scripts/common/temp_file_reader.py --type analysis_stage1_5 --repo "{repo}" --mrId {mrId}
```

**三路汇总风险**：
1. 从 Step0 的 `file_analysis` 中提取每个文件的 `identified_risks`
2. 从 Step1 的 `violation_details` 提取规则违规信息。Step1规则违规的风险等级映射规则：
   - **高**：规则违规大概率导致功能问题
   - **中**：规则违规可能影响功能，但不必然，默认等级
   - **低**：规则违规仅影响代码风格，不影响功能
3. 从 Step1.5 的 `defect_findings` 提取缺陷扫描结果。Step1.5缺陷扫描的风险等级映射规则：
   - **高**：severity="严重" 且 confidence="高"或"中"，或 severity="中等" 且 confidence="高"
   - **中**：severity="中等" 且 confidence="中"，或 severity="严重" 且 confidence="低"
   - **低**：severity="中等" 且 confidence="低"，或 severity="轻度"
4. **三路合并去重**（Step0、Step1和Step1.5可能发现同一类问题，合并时保留最详细的描述）
   - 如果 Step0 和 Step1.5 发现了同一文件+同一行号附近的风险，合并为一条，优先保留 Step1.5 的结构化缺陷信息（pattern、root_cause、fix_suggestion）
   - 如果 Step1 和 Step1.5 发现了同一类问题，合并为一条，优先保留 Step1.5 的缺陷模式分类
5. 综合评定整体风险等级

**风险等级评定规则**：
- **高**：有高风险问题，或明确违反检视规则，或明确有功能问题等
- **中**：可能有功能问题风险，比如性能劣化风险问题等
- **低**：仅有代码风格问题

**risk_level 字段只允许输出**：`高`、`中`、`低` 三个值。禁止使用`中等`、`普通`、`低风险`、`高风险`等其他表述。

---

### Step2.2：生成验证场景建议

基于汇总的风险结果，从以下维度提供验证场景建议：

- **基于风险点**（必须有）：破坏性变更→回归测试，功能逻辑风险→边界条件/异常分支，数据一致性风险→并发场景/异常恢复，性能风险→压力测试
- **功能拓展场景**（重要补充）：修改功能在场景A正常，需验证场景B、C是否受影响
- **基于变更上下文**：基本功能流程、异常场景、性能场景、回归场景
- **结合 MR 自验证结果**：已验证场景轻量检视，未验证场景重点补充

---

### Step2.3：生成analysis_stage2.json

**前置条件**：Step2.1 ~ Step2.2 全部完成

**输出文件**：analysis_stage2.json

**【重要】输出格式必须严格遵守模板**：

用 read 工具读取示例文件理解格式：
```
reference/analysis_example/analysis_stage2_example.json
```

**示例文件字段结构**：
- `risk_level`：风险等级（只能是"高""中""低"三个值）
- `issue_count`：问题数量统计（对象，包含high/medium/low）
- `high_risks`：高风险列表（数组，每个元素包含id/problem/file_path/line_number/description/mitigation/problem_code）
- `medium_risks`：中风险列表（数组）
- `low_risks`：低风险列表（数组）
- `validation_scenarios`：验证场景列表（数组，每个元素包含scenario/priority/test_type/related_files）
- `recommended_action`：建议操作（"可以通过"|"需修改"|"不建议合并"）

**风险条目字段说明**：
- `file_path`：文件在MR diff中的完整相对路径（从diff的new_path获取），如 `src/main/java/com/huawei/TransNeWebBaseOperationLog.java`
- `line_number`：起始行号，纯整数，如 131（AI估算值，后续Stage 4会用problem_code自动校验修正）
- `problem_code`：**【必填】** 问题代码片段，用于Stage 4精准定位Discussion行号。**必须原样复制diff中出现的代码行**，填写规范如下：
  - 从diff的 `+` 行或上下文行（空格开头行）中原样复制，**不要改写、不要省略、不要添加**
  - 至少包含完整的一行代码，如 `"if (isNeedSecondAuthException()) {"`，不要只写变量名如 `"name"`
  - 如果问题跨多行，复制连续的多行，用 `\n` 分隔
  - **禁止**：只写注释、用自然语言描述、改写缩进、用省略号代替
- `mitigation`：修复建议

**写入步骤**：
1. 先调用 `python scripts/common/temp_file_path_helper.py --type analysis_stage2 --repo "{repo}" --mrId {mrId}` 获取路径
2. **【强制安全校验】获取路径后，必须先使用 read 工具读取该路径（以解除底层系统的文件防覆盖保护锁）。**
3. 使用 write 工具直接写入该路径

**完成标志**：
- [ ] JSON文件已生成到正确路径
- [ ] risk_level 已评定（只允许"高""中""低"三个值）
- [ ] validation_scenarios 至少包含 1 个场景
- [ ] **每条风险的 problem_code 必填且是原样复制的代码（非空、非注释、非自然语言描述）**

**完成后更新Todo**：将 Step2 状态更新为 completed，Step2 结束。
