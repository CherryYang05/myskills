# 示例: 探索性研究 — 完整流水线

## 用户请求
```
Research the impact of AI on higher education quality assurance
```

## 阶段1: 范围界定 (SCOPING)

### research_question_agent 输出

**主题领域**: 人工智能在高等教育质量保障中的应用

**主要研究问题 (Research Question)**:
> 人工智能技术如何被整合到高等教育质量保障 (Quality Assurance) 过程中，其中有哪些新兴的益处、风险和制度性影响？

**FINER 评估**:
| 标准 | 得分 | 理由 |
|------|------|------|
| 可行性 (Feasible) | 4/5 | 文献库不断增长；可通过学术数据库获取 |
| 有趣性 (Interesting) | 5/5 | 处于两大行业交叉点的快速演变领域 |
| 新颖性 (Novel) | 4/5 | 综合性综述较少；多数研究为个案性质 |
| 伦理性 (Ethical) | 4/5 | 涉及重要的AI伦理问题，但本身不具危害性 |
| 相关性 (Relevant) | 5/5 | 直接为QA机构战略和政策提供依据 |
| **平均** | **4.4/5** | |

**范围边界**:
- 范围内: AI/ML在机构/专业认证、用于QA的学习分析、自动化评估、AI在自我评价中的应用
- 范围外: AI在教学/学习中的应用（除非与QA直接相关）、AI抄袭检测（独立文献）、特定供应商产品
- 关键假设: 聚焦高等教育；"质量保障 (Quality Assurance)"包括内部QA和外部认证

**子问题**:
1. 目前有哪些AI技术正在高等教育质量保障 (QA) 中被应用或试点？
2. 利益相关者报告了AI整合到QA中的哪些益处和风险？
3. AI增强的QA过程带来了哪些制度性和政策性影响？

### research_architect_agent 输出

**研究范式**: 实用主义（混合证据类型，应用导向）
**方法**: 系统文献综述 (Systematic Literature Review) 与主题综合分析 (Thematic Synthesis)
**数据策略**: 二手数据（学术文献 + QA机构的灰色文献 (Grey literature)）
**分析框架**: 按子问题组织的主题分析
**效度标准**: 全面检索、透明的纳入标准、PRISMA 报告

### devils_advocate_agent — 检查点 (Checkpoint) 1

**裁定**: 通过 (PASS)（附轻微备注）
- 次要级 (Minor): 研究问题 (RQ) 较宽泛 — 考虑"新兴 (emerging)"是否将范围限定为仅近期文献
- 次要级 (Minor): 需明确定义"质量保障 (Quality Assurance)"（内部vs外部、过程vs结果）
- 观察: 快速发展的领域意味着任何综述可能很快过时

## 阶段2: 调查 (INVESTIGATION)

### bibliography_agent 输出

**检索策略**: 4个数据库（Scopus、Web of Science、ERIC、Google Scholar），关键词: "artificial intelligence" AND "quality assurance" AND "higher education"，日期范围: 2019-2025，英文和中文。

**PRISMA 流程**: 847条识别 → 612条去重后 → 89条筛选 → 31条全文 → 22条纳入

**注释文献目录 (Annotated Bibliography)**（节选）:
1. **Zawacki-Richter, O., et al. (2019). Systematic review of research on artificial intelligence applications in higher education. *International Journal of Educational Technology in Higher Education*, *16*(1), 39. https://doi.org/10.1186/s41239-019-0171-0**
   - 相关性: AI在高等教育中的基础性映射
   - 关键发现: AI主要用于画像/预测、评估、自适应学习
   - 质量: 等级V（描述性研究的系统综述）

2. **Sanchez-Prieto, J.C., et al. (2024). AI-enhanced quality assurance: A framework for European higher education. *Quality in Higher Education*, *30*(1), 45-62.**
   - 相关性: 直接涉及AI+QA交叉领域
   - 关键发现: 提出4维度框架；利益相关者接受度不一
   - 质量: 等级VI（带案例说明的框架论文）

[... 其余20个来源 ...]

### source_verification_agent 输出

**审查来源数**: 22 | **已验证**: 20 | **标记**: 2 | **拒绝**: 0

**标记项**:
1. 来源 #14 — 中等COI（作者为AI-QA初创公司的CTO）
2. 来源 #19 — 时效性问题（2019年的综述可能不反映GPT之后的发展）

## 阶段3: 分析 (ANALYSIS)

### synthesis_agent 输出

**关键主题**:
1. **AI应用类型学**（强证据，15个来源）: 分类、分析、自动化、预测
2. **益处: 效率与规模**（中等证据，9个来源）: 减轻审查负担、更快周转、更大规模数据处理
3. **风险: 偏见与透明度**（中等证据，8个来源）: 算法偏见、黑箱决策、问责缺口
4. **制度准备度**（新兴证据，5个来源）: 能力建设、基础设施、文化阻力
5. **政策框架**（新兴证据，4个来源）: 监管、标准、治理模式

**关键矛盾**: 来源对AI在QA中是减少还是放大偏见存在分歧 — 取决于实施设计和监督机制。

**知识空白**: 全球南方证据有限；缺乏纵向研究；无关于学生对QA中AI感知的研究。

### devils_advocate_agent — 检查点 (Checkpoint) 2

**裁定**: 通过 (PASS)
- 次要级 (Minor): 检测到技术正面倾向 — 确保风险获得同等权重
- 观察: 大部分证据来自欧洲/北美背景

## 阶段4: 撰写 (COMPOSITION)

### report_compiler_agent 输出

[完整 APA 7.0 报告，约5,200字]

标题: Artificial Intelligence in Higher Education Quality Assurance: A Systematic Review of Applications, Benefits, Risks, and Institutional Implications

[摘要、引言、文献综述、方法论、发现（按5个主题组织）、讨论、局限、结论、参考文献（22个来源）]

## 阶段5: 审查 (REVIEW)

### editor_in_chief_agent 输出

**裁定**: 小幅修改 (Minor Revision)（得分: 3.7/5.0）
- 优势: 检索全面、主题组织良好
- 重大级 (Major): 讨论部分需要加强发现与现有QA理论的联系
- 次要级 (Minor): 部分引用格式不一致（3处引用）
- 次要级 (Minor): 摘要超过250字限制

### ethics_review_agent 输出

**裁定**: 通过 (CLEARED)
- AI披露声明存在且准确
- 所有引用已抽查（5/22 = 23%）— 全部验证通过
- 双重用途风险: 低
- 公正代表性: 充分（已注明地理局限）

### devils_advocate_agent — 检查点 (Checkpoint) 3

**裁定**: 通过 (PASS)
- 观察: 结论建议#3（"QA机构应采用AI工具"）的强度超过证据支持 — 建议弱化措辞
- "那又怎样？"检验: 通过 — 对QA实践有明确启示

## 阶段6: 修订 (REVISION)

### report_compiler_agent（修订1）

**变更**:
1. 讨论部分扩展，增加QA理论联系（重大级，主编）
2. 3处引用格式错误已更正（次要级，主编）
3. 摘要精简至248字（次要级，主编）
4. 建议#3弱化为"应考虑试点"（观察，魔鬼代言人）

**最终字数**: 5,450字
**使用修订轮次**: 第1轮（共2轮）

---

## 最终输出摘要
- 完整 APA 7.0 报告: 5,450字
- 22个引用来源（等级I-VII）
- 5个主题性发现
- 3条建议
- 伦理审查已通过
- 完成1轮修订
