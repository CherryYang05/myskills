# 证据评估模板

## 用途
逐源质量评估卡片。由 source_verification_agent 使用，用于系统评估进入研究流程的每一个来源。

## 评估卡片

```markdown
## 证据评估卡片

### 来源标识
- **引用格式 (APA 7.0)**: [full reference]
- **DOI/URL**: [link]
- **类型**: [journal article / book / report / web / conference paper / thesis / other]
- **访问日期**: [when verified]

---

### 质量评估

#### 1. 证据等级
**等级**: [I / II / III / IV / V / VI / VII]
**判定依据**: [why this level]

#### 2. 出版场所
- **期刊/出版商**: [name]
- **收录索引**: [Scopus / WoS / PubMed / DOAJ / other / none]
- **影响因子/CiteScore**: [value or N/A]
- **COPE成员**: [Yes / No / Unknown]
- **掠夺性期刊 (Predatory journal) 指标**: [None / Flags: list]

**场所评级**: [Excellent / Good / Adequate / Questionable / Unacceptable]

#### 3. 作者可信度
- **作者**: [names]
- **所属机构**: [institutions]
- **ORCID**: [if available]
- **学术履历**: [publication history in field]
- **专业匹配度**: [relevant to topic? Yes/Partial/No]

**作者评级**: [Excellent / Good / Adequate / Unknown / Questionable]

#### 4. 方法学质量
- **研究设计**: [description]
- **样本**: [size, selection, representativeness]
- **分析方法**: [appropriate for design?]
- **局限性是否承认**: [Yes / Partially / No]
- **可重复性**: [Yes / Partially / No]

**方法评级**: [Excellent / Good / Adequate / Weak / Flawed]

#### 5. 时效性
- **出版年份**: [YYYY]
- **数据收集时段**: [if stated]
- **领域发展速度**: [Rapid / Moderate / Slow / Foundational]
- **是否仍具时效性**: [Yes / Conditionally / No]

**时效性评级**: [Current / Acceptable / Dated / Outdated / Foundational]

#### 6. 利益冲突 (Conflict of Interest)
- **已声明 COI**: [None / Listed: details]
- **资助来源**: [source or Not stated]
- **潜在未声明 COI**: [None detected / Possible: details]

**COI 评级**: [Clean / Minor / Moderate / Significant / Critical]

---

### 总体评估

| 维度 | 评级 |
|------|------|
| 证据等级 (Evidence Level) | [I-VII] |
| 出版场所 | [Excellent-Unacceptable] |
| 作者 | [Excellent-Questionable] |
| 方法 | [Excellent-Flawed] |
| 时效性 | [Current-Outdated] |
| COI | [Clean-Critical] |
| **总体** | **[A / B / C / D / F]** |

### 建议
- [ ] **作为主要证据使用** (Grade A-B)
- [ ] **作为支撑证据使用** (Grade B-C)
- [ ] **使用时需明确标注注意事项** (Grade C-D)
- [ ] **不建议使用** (Grade D-F) — 原因: [specific reason]

### 备注
[Any additional observations, caveats, or context]
```

## 批量评估摘要

```markdown
## 来源验证 (Source Verification) 摘要

**日期**: [YYYY-MM-DD]
**已评估来源数**: [N]
**评估者**: source_verification_agent

### 评级分布
| 评级 | 数量 | 百分比 |
|------|------|--------|
| A (Excellent) | X | X% |
| B (Good) | X | X% |
| C (Adequate) | X | X% |
| D (Weak) | X | X% |
| F (Unacceptable) | X | X% |

### 标记来源
| 来源 | 问题 | 严重程度 | 建议 |
|------|------|----------|------|
| [ref] | [issue] | [High/Medium/Low] | [Include with caveat / Exclude] |

### 掠夺性期刊 (Predatory journal) 预警
[List any flagged journals]

### 来源库总体质量
**评估**: [Strong / Adequate / Mixed / Weak]
**建议**: [Proceed / Supplement / Major revision of source base needed]
```

## 使用说明
- 每个来源完成一张评估卡片以进行全面验证
- 批量摘要应在所有卡片完成后生成
- 最低抽查比例：20%的来源进行完整卡片评估
- 所有 Grade D/F 的来源需要记录判定理由
- 任何掠夺性期刊 (Predatory journal) 标记都需要完整验证
