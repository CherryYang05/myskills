# 预注册 (Preregistration) 模板 — OSF 标准21项预注册模板

## 用途
基于 OSF 标准数据收集前注册格式的填写模板。研究者在数据收集前完成本模板，并上传至预注册 (Preregistration) 平台（如 OSF Registries）。

---

## 说明

1. 在数据收集**之前**完成本模板
2. 标记为 `[Required]` 的项目为必填项；`[Optional]` 为推荐但非必填项
3. 如某项目不适用，填写"Not applicable"并简要说明原因
4. 完成后，前往 [OSF Registries](https://osf.io/registries) 创建预注册 (Preregistration)
5. 提交后，预注册 (Preregistration) 不可修改（可设置禁制期）

---

## A. 研究信息

### 1. 标题 [Required]
> 研究标题

```
[Enter descriptive study title]
```

### 2. 作者 [Required]
> 研究团队

| 姓名 | 机构 | 角色 | ORCID |
|------|------|------|-------|
| [Name] | [Institution] | [PI / Co-PI / RA] | [ORCID] |
| [Name] | [Institution] | [Role] | [ORCID] |

### 3. 研究问题 (Research Questions) [Required]
> 主要研究问题 (Research Questions)

```
RQ1: [Enter main research question]
RQ2: [Enter secondary research question, if any]
```

### 4. 假设 [Required]
> 预设假设
> 请清晰阐述方向性预测

```
H1: [Enter hypothesis 1, including expected direction]
    示例: 接受处理X的学生在测试Y上的得分将显著高于对照组

H2: [Enter hypothesis 2, if any]

H3: [Enter hypothesis 3, if any]
```

---

## B. 设计方案

### 5. 研究类型 [Required]
> 研究设计

- [ ] 实验
  - [ ] 被试间设计
  - [ ] 被试内设计
  - [ ] 混合设计
  - [ ] 析因设计: ___ x ___
- [ ] 观察性研究
  - [ ] 横断面研究
  - [ ] 纵向/队列研究
  - [ ] 病例对照研究
- [ ] 调查
- [ ] 其他: [Describe]

```
[Describe study design in detail]
```

### 6. 随机化 [Optional]
> 随机化程序

```
随机化方法: [Simple random / Stratified random / Cluster random / Block random / Not applicable]
随机化单位: [Individual / Class / School / Not applicable]
随机化工具: [Random number table / Computer program / Lottery / Not applicable]
分配比例: [1:1 / 2:1 / Other]
```

### 7. 盲法 [Optional]
> 盲法/掩蔽

```
盲法级别: [No blinding / Single-blind / Double-blind / Triple-blind]
盲法对象: [Participants / Researchers / Assessors / Not applicable]
盲法维持: [Describe how blinding is maintained]
揭示盲法时机: [Describe when unblinding occurs]
```

### 8. 研究设计/条件 [Required]
> 每个组/条件的具体描述

```
实验组/条件1: [Describe intervention content, duration, frequency in detail]
实验组/条件2: [If any]
对照组: [Describe control condition in detail]
```

---

## C. 抽样方案

### 9. 现有数据 [Required]
> 现有数据声明

- [ ] 尚未收集任何数据（数据创建前注册）
- [ ] 数据存在但尚未查看（任何人对数据进行观察前注册）
- [ ] 已查看部分数据（访问数据前注册）
- [ ] 已用于初步分析（数据分析后注册）

```
[Describe data status and your level of familiarity with the data]
```

### 10. 数据收集程序 [Required]
> 数据收集程序

```
收集方法: [Online survey / Paper survey / Interview / Experiment / Archival data / Other]
收集工具: [Questionnaire name / Scale name / Experimental software]
收集地点: [Online / Classroom / Laboratory / Other]
收集时间线: [Start and end dates]
数据收集者: [Who is responsible for collection]
```

### 11. 样本量 [Required]
> 计划样本量

```
目标样本量: [N = ]
每组样本量: [Experimental group n = , Control group n = ]
```

### 12. 样本量依据 [Required]
> 样本量确定的依据

```
方法: [Power analysis / Prior research conventions / Feasibility constraints / Other]

统计功效分析参数（如适用）:
- 效应量 (Effect size): [d = / f = / r = ]
- 效应量来源: [Prior study / Meta-analysis / Pilot study]
- 显著性水平 (alpha): [.05 / .01]
- 统计功效 (Power): [.80 / .90]
- 检验类型: [t-test / ANOVA / Regression / Other]
- 计算工具: [G*Power / R / Other]
- 计算结果: 最低所需 N = [  ]

超额采样率: [考虑 ___% 流失率，实际目标 N = ]
```

### 13. 停止规则 [Required]
> 何时停止数据收集

```
停止规则:
- [ ] 达到目标样本量时停止
- [ ] 在指定日期停止 (截止日期: [Date])
- [ ] 达到目标功效时停止（序贯分析）
- [ ] 其他: [Describe]
```

---

## D. 变量

### 14. 操纵变量 [实验必填]
> 自变量

```
自变量1: [Name]
操作定义: [How it is manipulated]
水平: [Level 1 / Level 2 / ...]

自变量2: [If any]
```

### 15. 测量变量 [Required]
> 因变量

```
主要因变量: [Name]
操作定义: [How it is measured]
测量工具: [Scale name / Test name]
信度与效度: [Cite reliability/validity literature]

次要因变量: [If any]

协变量/控制变量: [If any]
```

### 16. 指标 [Required]
> 每个变量的具体计分方法

```
变量1计分:
- 题项: [Which items]
- 计分方法: [Sum / Mean / Factor score / Other]
- 反向计分题项: [Which items need reverse scoring]
- 缺失数据处理: [How to handle missing values]

变量2计分: [Same format as above]
```

---

## E. 分析方案

### 17. 统计模型 [Required]
> 主要统计分析方法

```
假设1的分析:
- 统计方法: [Independent t-test / ANOVA / Regression / HLM / SEM / Other]
- 详细描述: [Model specification, e.g., DV ~ IV + covariate + (1|cluster)]

假设2的分析: [Same format as above]
```

### 18. 数据转换 [Optional]
> 数据转换计划

```
计划转换:
- [ ] 不做转换
- [ ] 对数转换: 应用于 [which variables], 触发条件 [skewness > ]
- [ ] 标准化 (Z-score)
- [ ] 其他: [Describe]
```

### 19. 推断标准 [Required]
> 统计推断标准

```
显著性水平: alpha = [.05 / .01 / .005]
多重比较校正: [Bonferroni / Holm / FDR / Not applicable]
效应量 (Effect size) 报告: [Cohen's d / eta-squared / R² / Other]
置信区间: [95% CI / 99% CI]
单侧/双侧检验: [Two-tailed / One-tailed, with justification]
```

### 20. 数据排除 [Required]
> 数据排除标准

```
排除标准:
- [ ] 未通过注意力检查 (具体标准: [                ])
- [ ] 反应时间过短/过长 (标准: < [  ] 分钟 或 > [  ] 分钟)
- [ ] 离群值 (定义: [> 3 SD / IQR方法 / Other])
- [ ] 不完整率 > [  ]%
- [ ] 其他: [Describe]

排除后程序:
- 报告排除前和排除后样本量
- 比较排除样本与保留样本的特征
```

### 21. 探索性分析 [Optional]
> 计划的探索性分析

```
探索性分析（非主要假设，但已计划）:
1. [Analysis description]
2. [Analysis description]

这些分析将在论文中明确标记为"探索性"。
```

---

## F. 其他

### 伦理审查 (Ethics Review) [Optional]
```
IRB审查状态: [Approved / Under review / Exempt / Not applicable]
IRB编号: [                ]
审查机构: [                ]
```

### 数据可用性 [Optional]
```
数据是否公开: [Yes / No / Partially]
数据仓库: [OSF / Dataverse / Other]
公开时机: [After publication / After study completion / Other]
```

### 补充材料 [Optional]
```
- [ ] 完整问卷/量表
- [ ] 刺激材料
- [ ] 分析代码
- [ ] 统计功效 (Power) 分析报告
- [ ] 预实验结果
```

---

## 提交前检查清单

- [ ] 所有 [Required] 项目已完成
- [ ] 假设已清晰阐述且可检验
- [ ] 分析方法与假设对应
- [ ] 排除标准已在数据收集前确定
- [ ] 验证性分析与探索性分析已区分
- [ ] IRB审查状态已确认
- [ ] 预注册 (Preregistration) 平台已选定（推荐 OSF Registries）

> 完成后，前往 [OSF Registries](https://osf.io/registries) 提交预注册 (Preregistration)。
