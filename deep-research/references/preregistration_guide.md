# 预注册指南 — 研究预注册指南

## 目的
研究预注册的决策指南与操作手册。协助 research_architect_agent 在方法论设计阶段判断是否需要预注册，并指导研究人员完成预注册流程。

---

## 1. 预注册决策树

```
Does your research have the following characteristics?
│
├── Confirmatory research (hypothesis testing)
│   └── Strongly recommend preregistration
│       ├── Has pre-specified statistical hypotheses → Preregister
│       ├── Will conduct significance testing → Preregister
│       └── Has primary outcome variables → Preregister
│
├── Exploratory research
│   └── Preregistration not required (but optional)
│       ├── Qualitative research → Typically not preregistered
│       ├── Data mining / EDA → Typically not preregistered
│       └── But you can preregister the research design and analysis process
│
├── Systematic review / Meta-analysis
│   └── Strongly recommend registration (PROSPERO)
│       └── Many journals require systematic reviews to be pre-registered
│
├── Randomized controlled trial (RCT)
│   └── Must register
│       ├── ICMJE requires RCTs to be pre-registered
│       └── Most journals will not accept unregistered RCTs
│
├── Replication study
│   └── Strongly recommend preregistration
│       └── Preregistration clearly distinguishes original from modified hypotheses
│
└── Secondary data analysis
    └── Recommend preregistration
        └── Prevents HARKing (Hypothesizing After Results are Known)
```

### 不需要预注册的情况

- 纯定性研究（扎根理论、现象学）
- 探索性数据分析（无预先设定的假设）
- 理论性或哲学性研究
- 文献综述（系统综述除外）
- 案例报告或案例研究

### 强烈建议预注册的情况

- 任何涉及假设检验的研究
- 涉及多重比较的研究
- 需要区分验证性研究与探索性研究分析的研究
- 可能因 p-hacking 或 HARKing (根据结果假设) 受到质疑的研究
- 申请研究经费时（展示研究严谨性）
- 期刊明确要求或鼓励预注册时

---

## 2. 预注册平台概览

| 平台 | 适用领域 | 特点 | 费用 |
|------|---------|------|------|
| **OSF Registries** | 所有学科 | 使用最广泛，多种模板，DOI，永久保存 | 免费 |
| **PROSPERO** | 系统综述 | 专为系统综述和荟萃分析设立 | 免费 |
| **AEA Registry** | 经济学 | 美国经济学会的随机对照试验 (RCT) 注册平台 | 免费 |
| **AsPredicted** | 所有学科 | 简化预注册（9个问题），快速完成 | 免费 |
| **ClinicalTrials.gov** | 临床试验 | 美国 FDA 要求的随机对照试验 (RCT) 注册 | 免费 |
| **EGAP** | 政治学 | 治理与政治实验 | 免费 |
| **RIDIE** | 发展经济学 | 国际发展影响评估注册 | 免费 |

### 平台选择指南

```
What is your research?
│
├── Systematic review / meta-analysis → PROSPERO
├── Clinical trial / medical intervention → ClinicalTrials.gov
├── Economics RCT → AEA Registry
├── Just need simple preregistration → AsPredicted
└── All other research → OSF Registries (recommended)
```

---

## 3. 21项核心内容清单

基于 OSF 标准数据收集前注册格式，以下为21项核心条目：

### A. 研究信息

| # | 条目 | 说明 |
|---|------|------|
| 1 | **研究标题** | 描述性标题 |
| 2 | **作者/研究团队** | 所有研究人员姓名及所属机构 |
| 3 | **研究问题** | 主要研究问题（清晰、具体） |
| 4 | **假设** | 预先设定的假设（包括方向性预测） |

### B. 设计方案

| # | 条目 | 说明 |
|---|------|------|
| 5 | **研究设计** | 实验/观察性，被试间/被试内，因子设计等 |
| 6 | **随机化** | 随机化方法（如适用） |
| 7 | **盲法** | 盲法级别及实施方式（如适用） |
| 8 | **条件/操纵** | 每个实验条件/组的具体描述 |

### C. 抽样方案

| # | 条目 | 说明 |
|---|------|------|
| 9 | **已有数据** | 是否使用已有数据；数据的性质和状态 |
| 10 | **数据收集程序** | 数据收集方式（问卷调查、访谈、实验、档案） |
| 11 | **样本量** | 计划样本量及确定依据 |
| 12 | **样本量依据** | 效力分析 (Power analysis) 或其他样本量计算方法 |
| 13 | **停止规则** | 何时停止收集数据（固定N / 达到目标效力 / 时间截断） |

### D. 变量

| # | 条目 | 说明 |
|---|------|------|
| 14 | **操纵变量** | 自变量的操作化定义 |
| 15 | **测量变量** | 因变量的操作化定义及测量工具 |
| 16 | **指标** | 每个变量的具体指标（量表、题项、计分方式） |

### E. 分析方案

| # | 条目 | 说明 |
|---|------|------|
| 17 | **统计模型** | 主要统计分析方法 |
| 18 | **数据转换** | 数据转换计划（如对数转换、标准化） |
| 19 | **推断准则** | 显著性水平 (alpha)、校正方法、效应量报告 |
| 20 | **数据排除** | 排除标准（异常值定义、注意力检查未通过等） |
| 21 | **探索性分析** | 计划中的非主要假设分析 |

---

## 4. 高等教育研究预注册示例

### 示例：教学策略对学习效果的影响

```
Title: The Effect of Flipped Classroom on University Students' Critical Thinking
       Skills: A Randomized Controlled Trial

Hypotheses:
H1: Students receiving flipped classroom instruction will score significantly
    higher on the CCTST than students receiving traditional lectures
H2: The benefit of flipped classroom will be greater for students with low
    prior knowledge than for those with high prior knowledge

Design: Cluster-randomized controlled trial (class as randomization unit)
Sample: 12 classes (6 experimental / 6 control), approximately 40 students
        per class, total 480
Power: 80% power to detect d = 0.4, alpha = .05, ICC = 0.05

Primary outcome: CCTST post-test score (controlling for pre-test)
Secondary outcomes: Final exam grade, learning motivation scale
Analysis: Multilevel modeling (students nested in classes)

Exclusion criteria:
- Attendance rate < 50%
- Both pre-test and post-test incomplete
- Attention check questions answered incorrectly

Exploratory analyses:
- Gender × teaching method interaction effect
- Learning motivation as a mediating variable
```

### 示例：大学辍学因素系统综述

```
Title: Factors Influencing University Student Dropout Decisions in Taiwan:
       A Systematic Literature Review

Research question: What factors influence university student dropout decisions
                   in Taiwan?
Databases: Airiti Library, TSSCI, Scopus, Web of Science
Search strategy: (dropout OR withdrawal OR leave)
                 AND (university OR higher education)
                 AND (Taiwan)
Time range: 2010-2025
Inclusion criteria:
- Studies with Taiwan university students as research subjects
- Explore causes or factors of dropout/withdrawal
- Peer-reviewed journal articles or theses/dissertations
Exclusion criteria:
- Research subjects below high school level
- Pure policy commentary (no empirical data)
Quality assessment: Mixed Methods Appraisal Tool (MMAT)
Synthesis method: Thematic synthesis
Registration platform: PROSPERO
```

---

## 5. 预注册披露声明模板

### 在论文中披露预注册

#### 标准声明（已预注册）
```
This study was preregistered on [Platform] prior to data collection
(registration number: [NUMBER]; URL: [URL]). All hypotheses, sample size
rationale, and analysis plans were specified before data collection began.
Deviations from the preregistered plan are noted in [section/supplementary
materials].
```

#### 披露与预注册的偏差
```
Deviations from preregistered plan:
1. [Deviation description]: [Reason for deviation]
2. [Deviation description]: [Reason for deviation]
These deviations do not affect the confirmatory nature of the primary analyses.
The preregistered analyses are reported as planned; additional exploratory
analyses are clearly labeled.
```

#### 未预注册时的披露
```
This study was not preregistered. While the hypotheses were formulated before
data analysis, the distinction between confirmatory and exploratory analyses
should be interpreted with this limitation in mind.
```

---

## 6. 预注册与注册报告

| 方面 | 预注册 | 注册报告 |
|------|-------------------------|-------------------------------|
| **定义** | 研究计划提前公开注册 | 研究计划提交至期刊进行预审 |
| **审查** | 不经过同行评审 | 第一阶段同行评审（研究设计） |
| **接受时机** | 完成后才提交论文 | 通过第一阶段后获得"原则性接受 (IPA)" |
| **结果偏差** | 减少但未消除（研究者仍可能选择性报告） | 大幅消除（无论结果如何均发表） |
| **发表偏差** | 无法解决 | 有效解决（零结果也予发表） |
| **适用期刊** | 所有期刊 | 仅接受注册报告的期刊 |
| **难度** | 低（只需填写表单） | 高（需要完整方法论并通过评审） |
| **灵活性** | 较高（偏差需披露但不妨碍投稿） | 较低（重大偏差可能影响接受） |

### 注册报告流程

```
Stage 1: Submit research plan
├── Introduction (theoretical background, literature review)
├── Methods (complete methodology, analysis plan)
├── Pilot data (if available)
└── Interpretation plan for predicted results
         ↓
Stage 1 Review (research design quality)
├── Accept (In-Principle Acceptance, IPA)
├── Revise and resubmit
└── Reject
         ↓
Stage 2: Conduct research, write results
├── Strictly follow the Stage 1 plan
├── Report all preregistered analyses (including null results)
├── Exploratory analyses clearly labeled
└── Deviations disclosed and explained
         ↓
Stage 2 Review (execution quality)
├── Was the Stage 1 plan faithfully executed?
├── Are results reported completely?
└── Typically not rejected due to null results
         ↓
Publication
```

### 支持注册报告的高等教育期刊选列

- *Studies in Higher Education*
- *Higher Education*
- *Assessment & Evaluation in Higher Education*
- *Teaching in Higher Education*
- *Educational Research Review*
- *Learning and Instruction*

> 完整列表：[COS Registered Reports](https://www.cos.io/initiatives/registered-reports)

---

## 快速参考：预注册3步骤

1. **决定是否预注册**：确定您的研究是否涉及假设检验
2. **选择平台**：系统综述使用 PROSPERO，其他研究使用 OSF
3. **填写21项清单**：使用 `templates/preregistration_template.md` 模板

> 预注册不是完美的解决方案，但它是目前最实用的透明度工具。即使是不完美的预注册也胜于没有预注册。
