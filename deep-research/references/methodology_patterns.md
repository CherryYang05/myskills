# 研究方法论模式 — 设计模板

## 目的
为常见研究设计提供即用型方法论模板。供 research_architect_agent 使用。

## 模式 1: 系统文献综述（Systematic Literature Review）

### 适用场景
- 梳理某一主题的知识现状
- 识别现有研究中的空白
- 综合证据以形成政策/实践建议

### 设计模板
```
Research Question: What is known about [topic] in [context]?

Protocol:
1. Register protocol (PROSPERO or similar)
2. Define search strategy (databases, keywords, Boolean operators)
3. Establish inclusion/exclusion criteria
4. Search execution + documentation
5. Two-pass screening (title/abstract → full text)
6. Quality appraisal of included studies
7. Data extraction
8. Synthesis (narrative, thematic, or meta-analytic)
9. Report per PRISMA guidelines

Quality Criteria:
- Comprehensive search (minimum 3 databases)
- Reproducible strategy
- Dual screening (2 reviewers or reviewer + verification)
- PRISMA checklist completed

Reporting Standard: PRISMA 2020 (see references/equator_reporting_guidelines.md)
```

### PRISMA 流程模板
```
Records identified through database searching (n = )
Additional records from other sources (n = )
         ↓
Records after duplicates removed (n = )
         ↓
Records screened (title/abstract) (n = )
Records excluded (n = )
         ↓
Full-text articles assessed for eligibility (n = )
Full-text excluded, with reasons (n = )
         ↓
Studies included in synthesis (n = )
```

## 模式 2: 比较案例研究（Comparative Case Study）

### 适用场景
- 比较政策、项目或机构
- 理解情境如何影响结果
- 从多个案例中生成理论命题

### 设计模板
```
Research Question: How does [phenomenon] vary across [cases]?

Protocol:
1. Case selection (theoretical or purposive sampling)
2. Define comparison framework (dimensions, variables)
3. Data collection per case (documents, interviews, data)
4. Within-case analysis
5. Cross-case analysis
6. Pattern identification and explanation

Quality Criteria:
- Explicit case selection rationale
- Consistent data collection across cases
- Both within-case and cross-case analysis
- Rival explanations considered
```

### 比较矩阵模板
```
| Dimension | Case A | Case B | Case C | Pattern |
|-----------|--------|--------|--------|---------|
| Context   |        |        |        |         |
| Input     |        |        |        |         |
| Process   |        |        |        |         |
| Outcome   |        |        |        |         |
```

## 模式 3: 政策分析（Policy Analysis）

### 适用场景
- 评估现有或拟议的政策
- 比较不同司法辖区的政策方法
- 评估政策结果和非预期后果

### 设计模板
```
Research Question: How effective is [policy] in achieving [goal]?

Framework Options:
A. Bardach's Eightfold Path
B. Dunn's Policy Analysis Framework
C. SWOT Analysis
D. Logic Model (Input → Activity → Output → Outcome → Impact)

Protocol:
1. Problem definition
2. Evidence gathering (quantitative + qualitative)
3. Policy option identification
4. Criteria development (effectiveness, efficiency, equity, feasibility)
5. Option assessment against criteria
6. Recommendation with trade-offs

Quality Criteria:
- Multiple criteria (not just effectiveness)
- Stakeholder perspectives included
- Unintended consequences assessed
- Implementation feasibility addressed
```

## 模式 4: 混合方法（Mixed Methods）— 聚合平行设计

### 适用场景
- 需要多种数据类型的复杂现象
- 需要对研究发现进行三角验证（triangulation）
- 定量数据需要定性解释（或反之）

### 设计模板
```
Research Question: What is the nature and extent of [phenomenon]?

Protocol:
QUAN strand:                    QUAL strand:
1. Survey/data collection       1. Interviews/focus groups
2. Statistical analysis         2. Thematic analysis
3. Quantitative findings        3. Qualitative findings
                    ↓
            4. Integration
            5. Joint display
            6. Meta-inference

Quality Criteria:
- Both strands have independent rigor
- Integration strategy explicit (not just parallel reporting)
- Joint display or mixed methods matrix
- Meta-inferences draw on both strands

Reporting Standards: QUAL strand → COREQ; QUAN strand → STROBE/CONSORT (see references/equator_reporting_guidelines.md)
```

## 模式 5: 内容分析（Content Analysis）/ 文档分析

### 适用场景
- 分析文本、政策、媒体或文档
- 识别传播中的模式
- 对大型文档集进行系统性审查

### 设计模板
```
Research Question: What themes/patterns emerge from [document set]?

Protocol:
1. Define corpus (which documents, inclusion criteria)
2. Develop coding framework (deductive, inductive, or hybrid)
3. Code systematically (inter-coder reliability if multiple coders)
4. Analyze codes → categories → themes
5. Report with exemplar quotes/excerpts

Quality Criteria:
- Corpus selection transparent
- Coding framework documented
- Inter-coder reliability reported (if applicable)
- Saturation discussed
```

## 模式 6: 探索性研究（Exploratory Research）

### 适用场景
- 新兴或研究不足的主题
- 为未来研究生成假设
- 从参与者视角理解现象

### 设计模板
```
Research Question: How do [participants] experience/understand [phenomenon]?

Protocol:
1. Purposive sampling
2. Semi-structured interviews or observations
3. Iterative data collection and analysis
4. Open coding → axial coding → selective coding
5. Theory or framework development
6. Member checking / peer debriefing

Quality Criteria:
- Reflexivity statement
- Thick description
- Data saturation discussed
- Transferability criteria addressed

Reporting Standard: COREQ for interviews/focus groups (see references/equator_reporting_guidelines.md)
```

## 模式 7: 标杆研究（Benchmarking Study）

### 适用场景
- 将绩效与标准或同行进行比较
- 识别最佳实践
- 设定绩效目标

### 设计模板
```
Research Question: How does [entity] perform compared to [benchmark]?

Protocol:
1. Select benchmarking type (internal, competitive, functional, generic)
2. Identify indicators and metrics
3. Collect comparable data
4. Analyze gaps
5. Identify best practices from high performers
6. Develop improvement recommendations

Quality Criteria:
- Comparable metrics (apples to apples)
- Context factors acknowledged
- Multiple indicators (not single metric)
- Actionable recommendations
```

## 模式 8: 技术需求分析（Technology Requirements Analysis）

### 适用场景
- 评估新技术的可行性、需求分析和技术比较
- 系统设计前的技术选型决策
- 技术采纳的风险和收益评估
- 当研究问题涉及"应使用哪种技术？"或"该技术能否解决问题？"

### 设计模板
```
Research Question: What technology approach best addresses [need] given [constraints]?

Protocol:
1. Requirement Elicitation
   - Stakeholder interviews
   - Existing system/process analysis
   - Functional requirements vs non-functional requirements (performance, security, scalability)
2. Technology Scanning
   - Inventory of candidate technologies (at least 3 options)
   - Technology Readiness Level (TRL) assessment
   - Community activity, documentation completeness, long-term maintenance risk
3. Feasibility Assessment
   - Technical feasibility: Can it be done?
   - Economic feasibility: Is it worth doing?
   - Organizational feasibility: Does the team have the capability?
   - Schedule feasibility: Is there enough time?
4. Proof of Concept (PoC)
   - Construct minimal verification targeting key technical risks
   - Define success criteria (performance thresholds, integration test pass rates)
   - Document encountered problems and solutions
5. Requirement Specification
   - Produce formal requirements document
   - Define acceptance criteria
   - Establish traceability matrix (requirements ↔ design ↔ testing)

Quality Criteria:
- Requirements completeness: All stakeholder requirements have been collected
- Traceability: Each requirement is traceable to its source; each design decision maps to a corresponding requirement
- Technical feasibility verification: Key technical risks have been validated through PoC
- Fair comparison of options: Consistent evaluation framework used to compare different technology options
```

### 技术比较矩阵模板
```
| Evaluation Dimension | Option A | Option B | Option C | Weight |
|---------------------|----------|----------|----------|--------|
| Functional Fit      |          |          |          | 30%    |
| Technology Maturity  |          |          |          | 20%    |
| Adoption Cost        |          |          |          | 15%    |
| Maintenance Cost     |          |          |          | 10%    |
| Learning Curve       |          |          |          | 10%    |
| Scalability          |          |          |          | 10%    |
| Community/Ecosystem  |          |          |          | 5%     |
| Weighted Total       |          |          |          | 100%   |
```

## 模式 9: 法律案例分析（Legal Case Analysis）

### 适用场景
- 法律与监管政策分析、判例法研究、法律文本解释
- 分析特定法律问题的现行法规和司法意见
- 比较不同司法辖区的法律方法
- 当研究问题涉及法律解释、权利与义务分析或政策分析的法律层面

### 与模式 3（政策分析）的区别
- **政策分析**：侧重评估政策效果 — "这项政策有效吗？""是否有更好的政策选项？"
- **法律案例分析**：侧重分析法律文本和判例法 — "法律是如何规定的？""法院如何解释？""是否存在法律漏洞？"

### 设计模板
```
Research Question: How does the law address [issue] and what are the implications for [context]?

Protocol:
1. Issue Identification
   - Translate research question into specific legal issues
   - Distinguish questions of fact vs questions of law
   - Define the relevant legal domains (public law / private law / international law)
2. Legal Framework Mapping
   - Constitutional-level provisions
   - Statutory / regulatory / administrative rule levels
   - International conventions / soft law
   - Legislative history and rationale for amendments
3. Case Law Analysis
   - Systematic case law search (court level, time range, keywords)
   - Extract key holdings from decisions
   - Analyze trends in case law evolution
   - Identify majority opinions vs dissenting opinions
4. Legal Reasoning
   - Textual interpretation, systematic interpretation, purposive interpretation, historical interpretation
   - Comparative law analysis (how other jurisdictions handle the issue)
   - Review and evaluate scholarly opinions
   - Interest balancing and value judgments
5. Recommendations
   - Interpretive recommendations under existing law
   - Legislative reform recommendations (if necessary)
   - Practical implementation recommendations
   - Risk warnings

Quality Criteria:
- Legal source accuracy: Cited regulations and cases must be current and effective versions
- Logical consistency: Legal reasoning process must not be self-contradictory
- Argumentation completeness: All possible interpretive paths have been considered
- Comparative law rigor: When comparing jurisdictions, differences in legal system backgrounds must be noted
```

### 法律分析结构模板
```
I. Legal Issues
   [Specific legal issues in dispute]

II. Relevant Provisions
   1. Statutory level:
   2. Regulatory level:
   3. International norms:

III. Judicial Opinions
   1. Majority opinion: [Case number] [Key holding]
   2. Dissenting opinion: [Case number] [Key holding]
   3. Trends:

IV. Scholarly Opinions
   1. View A:
   2. View B:
   3. Author's view:

V. Comparative Law
   [How other jurisdictions handle the issue]

VI. Conclusions and Recommendations
```

## 模式 10: 创作/实践导向研究（Creative/Practice-Based Research）

### 适用场景
- 艺术导向研究：通过艺术创作生成知识
- 设计研究 / 通过设计做研究（research through design）：通过设计过程生成知识
- 实践导向 / 实践驱动研究：实践本身就是研究方法
- 当研究问题涉及创意实践、设计思维或艺术探究

### 与传统学术研究的区别
- **产出形式**：可以是创意作品 + 论文（而非仅论文）
- **知识类型**：重视实践性知识（tacit knowledge，隐性知识）和具身知识（embodied knowledge）
- **过程即方法**：创意/设计过程本身就是研究方法，而不仅仅是研究对象
- **主体性**：研究者的主观体验是合法的知识来源，但需要系统性反思

### 设计模板
```
Research Question: What knowledge emerges through the practice of [creative activity] in [context]?

Protocol:
1. Reflective Practice
   - Define research question and creative intention
   - Establish reflective framework (e.g., Schön's reflection-in-action / reflection-on-action)
   - Confirm researcher positioning (insider / practitioner-researcher)
2. Process Documentation
   - Studio journal / design diary
   - Process video/audio documentation
   - Iteration version records (sketches, drafts, prototypes)
   - Decision point documentation: Why this approach and not another?
3. Contextual Analysis
   - Situate the creative process within disciplinary/cultural/historical context
   - Engage in dialogue with existing works/theories
   - Identify themes and insights emerging from the creative process
4. Knowledge Articulation
   - Transform tacit knowledge into communicable forms
   - Build bridges from practice to concepts
   - Distill transferable principles or frameworks
5. Presentation of Findings
   - Work presentation (exhibition, performance, prototype demonstration)
   - Written discourse (exegesis / critical commentary)
   - Integrate the relationship between work and discourse

Quality Criteria:
- Depth of reflection: Not just describing "what was done," but analyzing "why it was done this way" and "what was learned"
- Creative process transparency: Readers can understand the complete path from problem to work
- Clarity of knowledge contribution: Clearly state what this research contributes to knowledge
- Contextualization quality: The work does not exist in isolation but engages with the discipline
- Methodological reflexivity: The researcher is aware of their own role and biases
```

### 实践导向研究文档模板
```
Phase 1: Positioning
- Research question:
- Creative intention:
- Researcher positioning (practitioner / observer / participant):
- Theoretical framework:

Phase 2: Process
| Iteration | Date | Action | Reflection | Turning Point |
|-----------|------|--------|------------|---------------|
| v1        |      |        |            |               |
| v2        |      |        |            |               |
| v3        |      |        |            |               |

Phase 3: Outcomes
- Work description:
- Knowledge contribution:
- Transferable principles/frameworks:
- Recommendations for future practice/research:
```

## 选择合适的模式

```
What type of question?
├── "What is known?" → 系统文献综述（Systematic Literature Review）
├── "How do cases compare?" → 比较案例研究（Comparative Case Study）
├── "Is this policy working?" → 政策分析（Policy Analysis）
├── "What's happening and why?" → 混合方法（Mixed Methods）
├── "What do documents reveal?" → 内容分析（Content Analysis）
├── "How is this experienced?" → 探索性研究（Exploratory Research）
├── "How do we compare?" → 标杆研究（Benchmarking Study）
├── "Which technology should we use?" → 技术需求分析（Technology Requirements Analysis）
├── "What does the law say?" → 法律案例分析（Legal Case Analysis）
└── "What knowledge emerges from practice?" → 创作/实践导向研究（Creative/Practice-Based Research）

更细致的决策：
├── 技术评估相关
│   ├── 比较不同技术选项 → 模式 8（技术需求分析）
│   └── 比较不同组织的技术采纳情况 → 模式 2（比较案例研究）
├── 法律/政策相关
│   ├── 法律文本如何规定及法院如何解释 → 模式 9（法律案例分析）
│   └── 政策是否有效及如何改进 → 模式 3（政策分析）
├── 创意/设计相关
│   ├── 通过创作过程生成知识 → 模式 10（创作/实践导向研究）
│   ├── 理解创作者的体验 → 模式 6（探索性研究）
│   └── 分析创意文本/作品 → 模式 5（内容分析）
└── 不确定
    ├── 文献稀缺的新主题 → 模式 6（探索性研究）
    ├── 需要多种数据类型的复杂问题 → 模式 4（混合方法）
    └── 先看看前人的研究路径 → 模式 1（系统文献综述）
```
