# PRISMA 2020 — 系统综述报告模板

## 用途

遵循 PRISMA 2020 (Page et al., 2021) 编写系统综述报告的模板。全部27项 PRISMA 条目已映射至对应章节。请配合 `references/systematic_review_toolkit.md` 获取详细指导。

**参考文献**: Page et al. (2021). The PRISMA 2020 statement: an updated guideline for reporting systematic reviews. BMJ, 372, n71. https://doi.org/10.1136/bmj.n71

---

## 标题 (Title) [PRISMA Item 1]

**[完整标题，标识本报告为系统综述、荟萃分析或两者兼有]**

示例: "The Effect of [Intervention] on [Outcome] in [Population]: A Systematic Review and Meta-Analysis"

---

## 摘要 (Abstract) [PRISMA Item 2]

### 背景 (Background)
[1-2句话说明背景及综述原因]

### 目标 (Objectives)
[研究问题 (Research Questions)，理想情况下采用 PICOS 结构]

### 数据来源 (Data Sources)
[检索的数据库及最后检索日期]

### 研究选择 (Study Selection)
[简要说明纳入标准]

### 数据提取与综合 (Data Extraction and Synthesis)
[数据提取、偏倚风险和综合分析 (Synthesis) 所用方法]

### 结果 (Results)
[纳入研究数量、关键发现、效应估计值及CI、证据确定性]

### 局限性 (Limitations)
[证据和/或综述过程的关键局限]

### 结论 (Conclusions)
[总体解读与启示]

### 注册 (Registration)
[方案注册号及注册库]

**关键词**: [3-5个关键词]

---

## 1. 引言 (Introduction)

### 1.1 理由 (Rationale) [PRISMA Item 3]

[在已有知识背景下描述本综述的理由。需阐述:]
- 问题或疑问是什么？
- 已知什么（引用已有综述）？
- 为什么需要本综述（例如：无现有综述、现有综述已过时、证据冲突）？

### 1.2 目标 (Objectives) [PRISMA Item 4]

[使用 PICOS 明确提出问题:]

- **人群 (Population)**: [target population]
- **干预/暴露 (Intervention/Exposure)**: [intervention or exposure of interest]
- **对照 (Comparator)**: [comparison group]
- **结局 (Outcome(s))**: [primary and secondary outcomes]
- **研究设计 (Study Design)**: [eligible study designs]

---

## 2. 方法 (Methods)

### 2.1 纳入排除标准 (Eligibility Criteria) [PRISMA Item 5]

| 标准 | 纳入 | 排除 |
|------|------|------|
| 研究设计 | [e.g., RCTs, quasi-experimental] | [e.g., case reports, editorials] |
| 人群 | [describe] | [describe] |
| 干预 | [describe] | [describe] |
| 对照 | [describe] | [describe] |
| 结局 | [describe] | [describe] |
| 时间范围 | [e.g., published 2014-2024] | [before cutoff] |
| 语言 | [e.g., English] | [other] |
| 场景 | [describe] | [describe] |

### 2.2 信息来源 (Information Sources) [PRISMA Item 6]

[列出所有检索的数据库和其他来源，注明覆盖日期和最后检索日期:]

| 来源 | 日期范围 | 最后检索日期 |
|------|----------|-------------|
| [Database 1] | [start]-[end] | [date] |
| [Database 2] | [start]-[end] | [date] |
| [其他来源: 参考文献列表、专家联系、灰色文献 (Grey literature)] | — | [date] |

### 2.3 检索策略 (Search Strategy) [PRISMA Item 7]

[展示至少一个数据库的完整检索策略。包括所有检索词、布尔运算符和任何已应用的筛选器。]

**[数据库名称] 检索策略**:
```
#1 [search block 1 - Population terms]
#2 [search block 2 - Intervention terms]
#3 [search block 3 - Outcome terms]
#4 #1 AND #2 AND #3
#5 #4 with filters: [date, language, document type]
```

[其他数据库的检索策略见附录 A。]

### 2.4 筛选过程 (Selection Process) [PRISMA Item 8]

[描述研究筛选过程:]
- 各阶段审查者人数
- 如何保持独立性
- 如何解决分歧
- 使用的软件（如 Covidence、Rayyan）
- 筛选标准的预测试

### 2.5 数据收集过程 (Data Collection Process) [PRISMA Item 9]

[描述从报告中提取数据的方法:]
- 数据提取表（已开发、已预测试）
- 提取者人数及独立性
- 解决差异的流程
- 如何处理缺失数据（例如：联系作者）

### 2.6 数据项目 (Data Items) [PRISMA Item 10]

[列出所有寻求数据的变量:]

| 类别 | 变量 |
|------|------|
| 研究层面 | 作者、年份、国家、设计、场景、资金来源 |
| 参与者 | N、年龄、性别、诊断/状况、流失率 |
| 干预 | 类型、持续时间、频率、保真度 |
| 结局 | 定义、测量工具、时间点 |
| 结果 | 效应量 (Effect sizes)、CI、p值、原始数据 |

### 2.7 研究偏倚风险评估 (Study Risk of Bias Assessment) [PRISMA Item 11]

[描述偏倚风险评估:]
- 使用的工具: [RCTs 使用 RoB 2 / 非随机研究使用 ROBINS-I / 其他]
- 评估的领域
- 评估者人数及独立性
- 结果如何在综合分析 (Synthesis) 中使用

### 2.8 效应量指标 (Effect Measures) [PRISMA Item 12]

[指定每个结局的效应量指标:]

| 结局 | 类型 | 效应量指标 | 理由 |
|------|------|-----------|------|
| [Outcome 1] | 连续变量 | SMD (Hedges' g) | 不同研究使用不同量表 |
| [Outcome 2] | 二分类变量 | RR | 发病率数据 |

### 2.9 综合方法 (Synthesis Methods) [PRISMA Items 13a-13f]

**13a. 综合纳入资格**: [将研究分组到每个综合分析的标准]

**13b. 数据准备**: [准备数据的方法，例如：将SE转换为SD、处理多臂研究]

**13c. 制表/可视化**: [展示单项研究和综合分析 (Synthesis) 结果的方法，例如：森林图、汇总表]

**13d. 综合方法**: [统计模型和软件]
- 模型: [Fixed-effect / Random-effects (DerSimonian-Laird / REML)]
- 软件: [R metafor / RevMan / Stata]
- 或叙述性: [SWiM方法、计票法、效应方向图]

**13e. 异质性探索**: [使用的方法]
- 亚组分析: [预设亚组及理由]
- 荟萃回归: [检验的协变量，如适用]

**13f. 敏感性分析**: [计划的敏感性分析]
1. 逐项删除分析
2. 排除高偏倚风险研究
3. 固定效应 vs. 随机效应比较
4. [其他分析]

### 2.10 报告偏倚评估 (Reporting Bias Assessment) [PRISMA Item 14]

[评估发表偏倚的方法:]
- 漏斗图（视觉检查）
- 统计检验: [Egger's / Peter's / 剪补法]
- 方案与发表报告的比较

### 2.11 证据确定性评估 (Certainty Assessment) [PRISMA Item 15]

[用于评估证据确定性的框架:]
- GRADE 方法
- 评估因素: 偏倚风险、不一致性、间接性、不精确性、发表偏倚
- 升级因素（观察性研究）: 大效应量、剂量-反应关系、合理的混杂

---

## 3. 结果 (Results)

### 3.1 研究选择 (Study Selection) [PRISMA Item 16a, 16b]

#### PRISMA 流程图

```
 ┌─────────────────────────────────────────────────────┐
 │                 识别 (IDENTIFICATION)                │
 ├─────────────────────────────────────────────────────┤
 │ 从数据库识别的记录 (n = )                            │
 │   数据库1 (n = )                                     │
 │   数据库2 (n = )                                     │
 │   数据库3 (n = )                                     │
 │ 从其他来源识别的记录 (n = )                          │
 │   参考文献列表 (n = )                                │
 │   专家推荐 (n = )                                    │
 └──────────────────────┬──────────────────────────────┘
                        │
 ┌──────────────────────▼──────────────────────────────┐
 │ 筛选前移除的记录:                                    │
 │   重复记录 (n = )                                    │
 │   自动工具标记为不合格的记录 (n = )                   │
 │   其他原因移除的记录 (n = )                           │
 └──────────────────────┬──────────────────────────────┘
                        │
 ┌──────────────────────▼──────────────────────────────┐
 │                  筛选 (SCREENING)                    │
 ├─────────────────────────────────────────────────────┤
 │ 筛选的记录 (n = )                                    │
 │ 排除的记录 (n = )                                    │
 └──────────────────────┬──────────────────────────────┘
                        │
 ┌──────────────────────▼──────────────────────────────┐
 │ 寻求检索的报告 (n = )                                │
 │ 未检索到的报告 (n = )                                │
 └──────────────────────┬──────────────────────────────┘
                        │
 ┌──────────────────────▼──────────────────────────────┐
 │ 评估资格的报告 (n = )                                │
 │ 排除的报告及原因 (n = )                               │
 │   原因1 (n = )                                       │
 │   原因2 (n = )                                       │
 │   原因3 (n = )                                       │
 └──────────────────────┬──────────────────────────────┘
                        │
 ┌──────────────────────▼──────────────────────────────┐
 │                  纳入 (INCLUDED)                     │
 ├─────────────────────────────────────────────────────┤
 │ 纳入综述的研究 (n = )                                │
 │ 纳入研究的报告 (n = )                                │
 │ 纳入定量综合分析 (Synthesis) 的研究 (n = )            │
 └─────────────────────────────────────────────────────┘
```

[PRISMA Item 16b: 引用看似符合纳入标准但被排除的研究，并说明原因。]

### 3.2 研究特征 (Study Characteristics) [PRISMA Item 17]

**表格: 纳入研究特征**

| 研究 | 国家 | 设计 | 人群 (N) | 干预 | 对照 | 结局 | 随访 | 资金来源 |
|------|------|------|----------|------|------|------|------|----------|
| Author1 (Year) | [country] | [design] | [N] | [intervention] | [comparator] | [outcomes] | [duration] | [source] |
| Author2 (Year) | ... | ... | ... | ... | ... | ... | ... | ... |

### 3.3 研究中的偏倚风险 (Risk of Bias in Studies) [PRISMA Item 18]

**表格: 偏倚风险摘要（交通灯图）**

| 研究 | D1 | D2 | D3 | D4 | D5 | 总体 |
|------|----|----|----|----|----|------|
| Author1 (Year) | [L/S/H] | [L/S/H] | [L/S/H] | [L/S/H] | [L/S/H] | [L/S/H] |
| Author2 (Year) | ... | ... | ... | ... | ... | ... |

L = 低风险 (Low risk), S = 有一些顾虑 (Some concerns), H = 高风险 (High risk)

[各项研究偏倚风险发现的叙述性摘要]

### 3.4 单项研究结果 (Results of Individual Studies) [PRISMA Item 19]

**表格: 单项研究结果**

| 研究 | 结局 | 效应估计值 | 95% CI | p值 | 权重 |
|------|------|-----------|--------|-----|------|
| Author1 (Year) | [outcome] | [estimate] | [lower, upper] | [p] | [%] |
| Author2 (Year) | ... | ... | ... | ... | ... |

### 3.5 综合分析结果 (Results of Syntheses) [PRISMA Items 20a-20d]

#### 主要结局 (Primary Outcome): [Name]

**20a. 研究特征**: [贡献研究特征和偏倚风险的简要摘要]

**20b. 合并结果**:
- 合并效应: [estimate] (95% CI: [lower, upper])
- 统计显著性: Z = [value], p = [value]
- 异质性: I² = [value]% (95% CI: [lower, upper]), Q = [value] (df = [n], p = [value]), tau² = [value]
- 预测区间: [lower, upper]

**森林图 (Forest Plot)**: [插入或引用森林图]

**20c. 异质性调查**:
- 亚组分析: [results]
- 荟萃回归: [results, if conducted]

**20d. 敏感性分析**:
1. 逐项删除: [results — 是否有任何单项研究大幅改变了估计值？]
2. 排除高风险研究: [修正后的估计值]
3. 固定效应 vs. 随机效应: [比较]

#### 次要结局 (Secondary Outcome(s)): [Name]

[每个次要结局重复上述结构]

### 3.6 报告偏倚 (Reporting Biases) [PRISMA Item 21]

[报告发表偏倚评估:]
- 漏斗图: [对称性/非对称性描述]
- 统计检验: [result]
- 剪补法: [调整后估计值，如适用]
- 其他评估: [方案-结局比较]

### 3.7 证据确定性 (Certainty of Evidence) [PRISMA Item 22]

**GRADE 证据确定性汇总表**

| 结局 | 研究数 (n) | 参与者数 (N) | 效应 (95% CI) | 确定性 | 理由 |
|------|-----------|-------------|---------------|--------|------|
| [Outcome 1] | [n] | [N] | [estimate (CI)] | [High/Moderate/Low/Very Low] | [升级/降级原因] |
| [Outcome 2] | [n] | [N] | [estimate (CI)] | [level] | [reasons] |

---

## 4. 讨论 (Discussion) [PRISMA Item 23]

### 4.1 证据摘要 (Summary of Evidence)

[在其他证据背景下对结果进行总体解读。需阐述:]
- 每个结局的主要发现
- 与既往综述的比较
- 各研究间发现的一致性

### 4.2 局限性 (Limitations)

**证据的局限性**:
- [e.g., 各研究的偏倚风险、不一致性、间接性、不精确性]

**综述过程的局限性**:
- [e.g., 语言限制、数据库覆盖、无法联系作者]

### 4.3 启示 (Implications)

**对实践的启示**:
- [从业者应根据这些发现采取什么行动]

**对研究的启示**:
- [识别的空白、推荐的未来研究设计]

**对政策的启示**:
- [政策影响，如适用]

---

## 5. 其他信息 (Other Information)

### 5.1 注册与方案 (Registration and Protocol) [PRISMA Item 24]

[提供注册信息和方案链接:]
- 注册库: [e.g., PROSPERO]
- 注册号: [number]
- 方案URL: [link]
- 与方案的偏差: [描述任何偏差及理由]

### 5.2 支持 (Support) [PRISMA Item 25]

[描述支持来源:]
- 财务支持: [资金来源及资助号]
- 非财务支持: [e.g., 机构支持、数据库访问]
- 资助者角色: [描述资助者在综述中的任何角色]

### 5.3 利益冲突 (Competing Interests) [PRISMA Item 26]

[声明所有作者的利益冲突 (Conflict of Interest)]

### 5.4 数据与材料可用性 (Availability of Data and Materials) [PRISMA Item 27]

[报告以下各项的可用性:]
- [ ] 数据提取表
- [ ] 纳入研究的提取数据
- [ ] 分析代码
- [ ] 排除研究列表及原因
- [ ] PRISMA 检查清单（已完成）

---

## 附录 (Appendices)

### 附录 A: 完整检索策略

[所有数据库的完整检索策略]

### 附录 B: 排除研究及原因

| 研究 | 排除原因 |
|------|----------|
| [citation] | [reason] |

### 附录 C: PRISMA 2020 检查清单

[已完成的 PRISMA 2020 检查清单，每项注明页码/章节号]

| 条目号 | 检查清单条目 | 报告位置（页/章节） |
|--------|-------------|-------------------|
| 1 | Title | [page] |
| 2 | Abstract | [page] |
| ... | ... | ... |
| 27 | Availability | [page] |
