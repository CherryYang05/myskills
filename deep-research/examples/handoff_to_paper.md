# 交接示例: deep-research → academic-paper

本示例展示 deep-research full 模式在完成研究后，如何将成果交接给 academic-paper 开始论文写作。

---

## 场景设置

用户已完成 deep-research full 模式，研究主题为"AI-Assisted Quality Assurance in Higher Education: A Comparative Analysis of Implementation Strategies in East Asian Universities"。以下是研究输出摘要。

---

## deep-research 输出摘要

### 1. 研究问题简报 (Research Question Brief)（来自 research_question_agent）

```markdown
### 主要研究问题 (Primary Research Question)
How do East Asian universities (Taiwan, Japan, South Korea) differ in their
implementation strategies for AI-assisted quality assurance, and what factors
explain the variation in adoption patterns?

### FINER Assessment
| Criterion   | Score | Justification |
|-------------|-------|---------------|
| Feasible    | 4/5   | Public data + policy documents available |
| Interesting | 5/5   | Timely: AI policy divergence across similar systems |
| Novel       | 4/5   | Few cross-national comparisons in this space |
| Ethical     | 5/5   | No human subjects; public policy analysis |
| Relevant    | 5/5   | Directly informs HEEACT and peer agencies |
| **Average** | **4.6/5** | |

### 子问题 (Sub-questions)
1. What AI-QA tools and frameworks have been adopted by accreditation agencies
   in Taiwan, Japan, and South Korea?
2. What institutional and policy factors facilitate or hinder AI-QA adoption?
3. To what extent do implementation outcomes align with stated policy objectives?
```

### 2. 方法论蓝图 (Methodology Blueprint)（来自 research_architect_agent）

```markdown
- 范式: 实用主义（比较政策分析）
- 方法: 定性比较分析 (QCA) + 文件分析
- 数据来源:
  - 政策文件（3个国家的QA框架）
  - 认证机构报告（HEEACT, JUAA/NIAD-QE, KCUE）
  - 已发表案例研究和会议论文
- 分析框架: 创新扩散理论 (Rogers) + 制度同构理论 (DiMaggio & Powell)
- 效度: 跨文件类型三角验证 (Triangulation) + 与QA从业者的成员检验
```

### 3. 注释文献目录 (Annotated Bibliography)（来自 bibliography_agent）

```markdown
识别23个来源，质量筛选后保留18个:
- 6篇同行评审 (Peer-reviewed) 文章（等级II-III证据）
- 4份认证机构报告（等级IV）
- 3份政策文件（等级IV）
- 3份会议论文（等级V）
- 2份机构案例研究（等级V）

识别的关键主题:
- AI采用成熟度差距（QA应用方面: 台湾 > 韩国 > 日本）
- 监管分歧（日本的谨慎方式 vs 韩国的自上而下推进）
- 数据基础设施作为前提条件（不仅仅是技术问题）
```

### 4. 综合分析报告 (Synthesis Report)（来自 synthesis_agent）

```markdown
## 核心发现

1. **采用模式聚类为3个模型**:
   - 台湾: 自下而上实验（机构主导试点）
   - 韩国: 自上而下授权（部委驱动框架）
   - 日本: 谨慎渐进主义（自愿指导方针）

2. **关键成功因素**（3国趋同证据）:
   - 数据基础设施成熟度
   - 认证机构技术能力
   - 大学数据共享意愿
   - AI决策的清晰治理框架

3. **核心张力**: 效率提升 vs 透明度担忧
   - 3国均报告教师对"黑箱"决策的抵制
   - 仅韩国尝试了监管回应（2025年AI教育伦理法案）

4. **证据空白**:
   - 尚无严格的成效研究（3国均在实施3年以内）
   - 学生/教师体验数据几乎完全缺失

## 识别的矛盾
- 台湾HEEACT报告"高采用率"，但学术文献表明大多数大学仍在试点阶段
  → "采用"的定义不一致

## 知识空白
- 对认证结果（通过/未通过率）的影响
- 成本效益分析
- 教师感知和行为变化
```

---

## 交接指令

完成 deep-research 后，用户输入:

```
Now help me write a paper based on this research
```

---

## academic-paper intake_agent 自动检测

**intake_agent 检测流程**:

```
扫描可用材料...

[已检测] 研究问题简报 (Research Question Brief)
  - 来源: deep-research / research_question_agent
  - 状态: 完成 (FINER 4.6/5)
  - 操作: 跳过 academic-paper 阶段1（主题界定）

[已检测] 方法论蓝图 (Methodology Blueprint)
  - 来源: deep-research / research_architect_agent
  - 状态: 完成（实用主义 QCA + 文件分析）
  - 操作: 跳过 academic-paper 阶段2（方法论设计）
  - 备注: 将直接整合到方法部分

[已检测] 注释文献目录 (Annotated Bibliography)（18个来源，APA 7.0）
  - 来源: deep-research / bibliography_agent
  - 状态: 完成，已通过质量筛选
  - 操作: 跳过 academic-paper 文献检索
  - 备注: 将作为文献综述部分的基础

[已检测] 综合分析报告 (Synthesis Report)
  - 来源: deep-research / synthesis_agent
  - 状态: 完成（3个核心发现 + 1个矛盾 + 2个空白）
  - 操作: 跳过 academic-paper 分析阶段
  - 备注: 将围绕综合分析 (Synthesis) 构建发现与讨论部分

材料评估: 全面
推荐 academic-paper 模式: full（加速流水线）
估计已完成部分: 60-70%
剩余工作: 写作、格式化、论证和润色
```

---

## 跳过的步骤及原因

| academic-paper 步骤 | 正常工作流 | 交接后 | 原因 |
|---------------------|----------|--------|------|
| 阶段1: 主题界定 | intake_agent 从头澄清 | 跳过 | 研究问题 (RQ) 简报已完成 |
| 阶段2: 结构规划 | outline_agent 设计结构 | 部分 | 有蓝图但需转换为论文结构 |
| 阶段3: 文献检索 | literature_agent 检索 | 跳过 | 文献目录已完成 |
| 阶段4: 文献综述写作 | review_writer_agent 写作 | 活跃 | 有综合分析 (Synthesis) 但需转换为论文语调 |
| 阶段5: 方法论写作 | method_writer_agent 写作 | 活跃 | 有蓝图但需扩展为完整段落 |
| 阶段6: 发现写作 | findings_writer_agent 写作 | 活跃 | 有综合分析 (Synthesis) 但需扩展论证 |
| 阶段7: 讨论写作 | discussion_writer_agent 写作 | 活跃 | 需要原创论述（非直接复制综合分析 (Synthesis)） |
| 阶段8: 引言+结论 | bookend_agent 写作 | 活跃 | 需基于全文撰写 |
| 阶段9: 摘要+格式 | format_agent 处理 | 活跃 | 需先完成全文 |
| 阶段10: 自我审查 | review_agent 审查 | 活跃 | 必须执行 |

---

## 交接后 academic-paper 实际工作流

```
=== academic-paper: 加速流水线 ===

步骤1: 结构映射
  [outline_agent]
  - 输入: 研究问题 (RQ) 简报 + 方法论蓝图 (Blueprint) + 综合分析 (Synthesis) 报告
  - 输出: 完整论文大纲，每个章节标注对应的 deep-research 材料
  - 输出示例:

    I. 引言
       - 背景: AI在高等教育QA中的应用（来自综合分析 (Synthesis) 背景）
       - 问题: 跨国差异未得到解释
       - 目的: 比较3种东亚模式
       - 研究问题 (RQ): [直接引用研究问题 (RQ) 简报]

    II. 文献综述
       - 2.1 AI在质量保障 (Quality Assurance) 中的应用（来自文献目录主题）
       - 2.2 创新扩散框架（来自蓝图）
       - 2.3 制度同构（来自蓝图）
       - 2.4 东亚高等教育体系比较

    III. 方法论
       - 3.1 研究设计: QCA + 文件分析（来自蓝图）
       - 3.2 案例选择和数据来源
       - 3.3 分析框架
       - 3.4 效度与局限性

    IV. 发现
       - 4.1 三种采用模型（来自综合分析 (Synthesis) 发现1）
       - 4.2 关键成功因素（来自综合分析 (Synthesis) 发现2）
       - 4.3 效率与透明度张力（来自综合分析 (Synthesis) 发现3）

    V. 讨论
       - 5.1 理论启示
       - 5.2 对认证机构的政策启示
       - 5.3 实践建议
       - 5.4 局限性（来自综合分析 (Synthesis) 空白 + 蓝图效度）

    VI. 结论
       - 摘要 + 未来研究方向

步骤2: 章节写作（并行）
  [review_writer_agent] → 文献综述
    - 基于注释文献目录 (Annotated Bibliography) 和综合分析 (Synthesis)，转换为流畅的文献综述
    - 非逐篇摘要，而是主题性整合

  [method_writer_agent] → 方法论
    - 将蓝图 (Blueprint) 扩展为完整的方法论段落
    - 为QCA添加技术细节和程序说明

  [findings_writer_agent] → 发现
    - 将综合分析 (Synthesis) 的3个核心发现扩展为有证据支撑的论证
    - 每个发现辅以具体案例和数据
    - 处理综合分析 (Synthesis) 中标记的矛盾

步骤3: 讨论 + 首尾章节
  [discussion_writer_agent] → 讨论
    - 原创论述: 发现与理论之间的对话
    - 不重复发现，而是解释"为什么"
    - 将 deep-research 知识空白整合为未来研究方向

  [bookend_agent] → 引言 + 结论
    - 引言: 从宏观背景到具体研究问题 (RQ)
    - 结论: 无新信息，呼应研究问题 (RQ) 并展望未来

步骤4: 摘要 + 格式
  [format_agent]
    - 摘要: 150-250字，IMRAD结构
    - APA 7.0 全文格式化
    - 参考文献列表清理（基于文献目录 + 新增引用）

步骤5: 自我审查
  [review_agent]
    - 内部一致性检查（研究问题 (RQ) → 方法 → 发现 → 讨论逻辑链）
    - 引用完整性（每个主张都有引用）
    - 格式合规
    - 裁定: 可投稿 / 需要修订
```

---

## 用户可见的交接体验

**academic-paper 的开场消息**:

> 我已阅读您在 deep-research 阶段的全部输出，包括:
> - 研究问题简报 (Research Question Brief)（FINER 4.6/5）
> - 方法论蓝图 (Methodology Blueprint)（QCA + 文件分析）
> - 注释文献目录 (Annotated Bibliography)（18个经质量筛选的来源）
> - 综合分析报告 (Synthesis Report)（3个核心发现 + 2个知识空白）
>
> 基于这些材料，我已完成论文大纲的初步规划。以下是计划的论文结构:
> [展示大纲]
>
> 我有两个问题需要确认:
> 1. 目标期刊是什么？（这影响字数限制和格式要求）
> 2. 论文语言应为英文还是双语？
>
> 确认后，我将开始写作。由于研究基础已经十分全面，我可以跳过早期探索阶段，直接进入论文写作。

---

## 注意事项

1. **非复制粘贴**: academic-paper 不直接复制 deep-research 输出，而是将其转化为学术论文的语调和格式
2. **可能发现新问题**: 写作过程中，academic-paper 的 Agent 可能发现 deep-research 遗漏的要点，将主动补充
3. **仍需用户确认**: 目标期刊、语言偏好、特定格式要求仍需用户输入
4. **审查建议自动衔接**: 论文完成后，用户可继续使用 `academic-paper-reviewer` 进行正式审查
