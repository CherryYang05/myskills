---
scenario: Fact-checking claims about Taiwan's higher education
mode: fact-check
agents_used:
  - source_verification_agent
input: User provides 7 claims about Taiwan's higher education
output: Claim-by-claim verification report + verification summary
note: This example uses Taiwan HEI data. The fact-check mode works with any topic — just provide claims about your research area (e.g., "US enrollment has declined 15% since 2010", "EU universities spend more on research than US ones").
---

# 事实核查模式示例: 台湾高等教育主张验证

本示例以台湾高等教育为领域案例，展示 `fact-check` 模式的完整工作流程。同一工作流程适用于任何研究领域 — 只需将主张替换为与你研究相关的陈述即可。source_verification_agent 将根据可用证据验证每个主张。

---

## 用户请求

```
Please fact-check the following claims about Taiwan's higher education:

1. Taiwan currently has 152 colleges and universities.
2. HEEACT was established in 2005 and is the only institution responsible for higher education accreditation in Taiwan.
3. The average student-to-faculty ratio in Taiwan's universities is 1:20.
4. Declining birth rates have caused more than 10 universities in Taiwan to complete their exit or closure procedures.
5. Taiwan's higher education expenditure as a percentage of GDP is approximately 0.4%, lower than the OECD average.
6. The vacancy rate for the 2024 academic year university examination distribution admission reached 15%.
7. Taiwan produces approximately 4,000 doctoral graduates per year, of which more than half enter academia as faculty.
```

---

## source_verification_agent 验证报告

### 主张1

> "Taiwan currently has 152 colleges and universities."

**裁定:** 警告 — 部分属实

**验证依据:** 根据教育部112学年度（2023-2024）高等教育概况统计，台湾大专校院总数为145所（含大学、独立学院及专科学校）。此数字因学校停办或合并而持续变动。若将军警院校（如国防大学、中央警察大学）纳入，总数略有增加，但仍未达152所。"152"可能引用较早年度（约108-109学年度）的数据，当时仍有较多学校在运营。

**来源:** 教育部统计处，《高等教育概况统计》，112学年度（2023-2024）。

**修正建议:** 应更新至最近学年度数据，并明确统计范围定义（是否包含军警院校、宗教研修院校等特殊类型）。

---

### 主张2

> "HEEACT was established in 2005 and is the only institution responsible for higher education accreditation in Taiwan."

**裁定:** 警告 — 部分属实

**验证依据:** 高等教育评鉴中心（HEEACT）确实于2005年12月26日成立 — 此部分正确。但"唯一"的说法不准确。台湾的高等教育评鉴制度自2017年起推动多元化，除HEEACT外，中华工程教育学会（IEET）、台湾评鉴协会（TWAEA）等也经教育部认可执行特定类型之品保认证。此外，自2023年第三周期校务评鉴起，大学也可选择自办外部评鉴。因此，HEEACT是最主要的认证机构，但并非唯一。

**来源:**
- HEEACT官网，关于我们 > 发展沿革
- 教育部，《大学自办评鉴结果审查原则》（2017年修订）
- 教育部，《大专校院校务评鉴委托品质保证认证实施计划》（116学年度）

**修正建议:** 修订为"HEEACT成立于2005年，是台湾最主要的高等教育认证机构之一。"

---

### 主张3

> "The average student-to-faculty ratio in Taiwan's universities is 1:20."

**裁定:** 警告 — 部分属实

**验证依据:** 师生比的计算方式不同会产生差异。教育部公布的全体校院师生比（含专任及折计兼任）与仅以专任教师计算的结果差异颇大。依112学年度数据，公立大学日间学制折计师生比约为18:1至22:1（因校而异），私立大学约为22:1至28:1，整体平均值约为23:1，而非20:1。另外，"1:20"是非常规写法 — 师生比通常写为"20:1"（每1位教师对应20位学生），而非"1:20"。

**来源:** 教育部统计处，《各类学校校院学生及专任教师统计》，112学年度。

**修正建议:** 修订为"台湾日间高等教育学制的折计师生比约为23:1，公立与私立学校之间差异显著"，并使用正确的记法格式。

---

### 主张4

> "Declining birth rates have caused more than 10 universities in Taiwan to complete their exit or closure procedures."

**裁定:** 已验证 (Verified)

**验证依据:** 根据教育部公告及《私立高级中等以上学校退场条例》实施状况，截至2025年初，已完成停招或停办程序的学校包括：高凤数位内容学院（2014年停办）、永达技术学院（2014年停招、2021年停办）、高美医护管理专科学校（2018年停招）、亚太创意技术学院（2019年停招）、南荣科技大学（2020年停招）、稻江科技暨管理学院（2020年停招）、台湾观光学院（2022年停办）、兰阳技术学院（2022年停招）、中州科技大学（2023年停招）、和春技术学院（2023年停招）、大同技术学院（2023年停招）、台湾首府大学（2023年停办）、明道大学（2024年停招）、环球科技大学（2024年停招）等，总数超过10所；此主张已验证。

**来源:**
- 教育部年度大专校院停招/停办公告
- 教育部《私立高级中等以上学校退场条例》实施进度报告

**备注:** 此数字持续增加中；部分学校尚在"专案辅导"阶段，尚未完成退场程序。

---

### 主张5

> "Taiwan's higher education expenditure as a percentage of GDP is approximately 0.4%, lower than the OECD average."

**裁定:** 警告 — 部分属实

**验证依据:** 此主张需区分"政府公共支出"与"总支出（含民间）"。根据教育部统计，台湾政府公共支出用于高等教育的GDP占比约为0.4-0.5%，确实低于OECD平均约0.9%（Education at a Glance 2021数据）。但若纳入民间支出（学费、企业赞助等），台湾高等教育总支出GDP占比约为1.2-1.3%，接近OECD平均1.5%。因此，"0.4%"仅反映公共支出部分。该主张未区分公共与民间支出，可能产生误导。

**来源:**
- 教育部统计处，《教育经费统计》，112年度
- OECD, *Education at a Glance 2023*, Table C2.1

**修正建议:** 修订为"台湾公共支出用于高等教育的GDP占比约为0.4-0.5%，低于OECD平均0.9%；但若计入民间支出，总占比约为1.2-1.3%，差距缩小。"

---

### 主张6

> "The vacancy rate for the 2024 academic year university examination distribution admission reached 15%."

**裁定:** 无法验证 (Unverifiable)

**验证依据:** 大学考试分发入学委员会每年发布分发结果，但"缺额率"的定义和计算方式在不同报告中可能不一致。此处引用的"15%"缺乏明确来源与计算基础：分母是核定招生名额？还是扣除其他入学管道后剩余名额？近年媒体报导的数据差异极大，从个位数百分比到超过20%不等，取决于计算方式以及是否仅计算一般大学或包含技专校院。此外，113学年度分发结果应以大考中心正式公告为准，而非媒体估算。

**来源:** 无法取得精确官方数据以验证此特定数字。

**修正建议:** 引用大考中心官方统计，明确定义缺额率之计算方式，并注明数据来源年度。

---

### 主张7

> "Taiwan produces approximately 4,000 doctoral graduates per year, of which more than half enter academia as faculty."

**裁定:** 不实 (False)

**验证依据:** 前半部分大致正确 — 根据教育部统计，台湾近年每年博士学位授予数约3,800至4,200人，"约4,000人"为合理说法。但后半部分 — "超过半数进入学术界担任教职" — 与现有数据不符。根据国科会（前科技部）博士人才追踪调查及教育部毕业生流向调查，近年博士毕业生进入学术界（担任大专校院专任教师）的比例约为25-30%。因少子化使得教职缺额大幅缩减，新聘教师名额逐年下降，博士毕业生进入学术界的比例持续走低。多数博士毕业生流向业界、研究机构或博士后职位，而非直接成为专任教师。

**来源:**
- 教育部统计处，《毕业生流向调查》
- 国科会，《博士人才培育与就业调查》
- 教育部统计处，《大专校院学位授予统计》，111-112学年度

**修正建议:** 修订为"台湾每年约产生4,000名博士毕业生，其中约25-30%进入大专校院担任专任教师。此比例因少子化缩减教职缺额而持续下降。"

---

## 验证摘要报告

### 总览

| # | 主张摘要 | 裁定 | 严重程度 |
|------|----------|------|----------|
| 1 | 152所高等教育机构 | 警告 — 部分属实 | 低 — 数据过时 |
| 2 | HEEACT是唯一认证机构 | 警告 — 部分属实 | 中 — 事实错误 |
| 3 | 师生比1:20 | 警告 — 部分属实 | 低 — 近似但记法有误 |
| 4 | 超过10所学校已退场 | 已验证 (Verified) | 不适用 |
| 5 | 高教支出占GDP 0.4% | 警告 — 部分属实 | 中 — 未区分公共与民间支出 |
| 6 | 缺额率15% | 无法验证 (Unverifiable) | 高 — 无法验证 |
| 7 | 超过半数博士毕业生进入学术界 | 不实 (False) | 高 — 严重不准确 |

### 验证统计

- 已验证 (Verified): 1项主张 (14%)
- 警告 — 部分属实: 4项主张 (57%)
- 不实 (False): 1项主张 (14%)
- 无法验证 (Unverifiable): 1项主张 (14%)

### 总体评估

本组主张的整体准确性偏低。7项主张中，仅1项完全正确，4项部分正确但存在遗漏或不够精确，1项明显不实，1项无法验证。最严重的是主张7（博士毕业生职业走向），与实际数据严重偏离，若用于政策论述可能导致错误结论。

### 验证建议

1. 所有数据应注明具体来源与年度
2. 涉及比例或百分比的主张应明确定义分子与分母
3. 描述制度体系的主张（如认证制度）应反映最新制度变革
4. 无法取得精确数据的主张应标注为"估算"或"据媒体报导"，而非既定事实
