# 跨 Agent 质量对齐 — 完整定义

统一定义，防止 Agent 间不一致。

| 概念 | 定义 | 适用 Agent |
|---------|-----------|------------|
| **Peer-reviewed**（同行评审） | 发表于具有正式同行评审流程的期刊（仅编辑审查不符合资格）。会议论文仅在明确标注同行评审时方可计入 | bibliography_agent, source_verification_agent |
| **Currency Rule**（时效性规则） | 默认：发表不超过5年。按学科覆写：CS/AI = 3年，History/Philosophy（历史/哲学）= 20年，Law（法律）= 取决于管辖权变更。经典/奠基性作品（seminal works）不论年份均可豁免 | bibliography_agent, ethics_review_agent |
| **CRITICAL severity**（致命级严重度） | 铁律：若不解决将使核心结论无效或构成学术不端的问题。必须在流水线继续前立即解决 | 所有 Agent |
| **Source Tier**（来源层级） | tier_1 = Q1同行评审期刊；tier_2 = 其他同行评审；tier_3 = 学术性但非同行评审；tier_4 = 灰色文献（grey literature） | bibliography_agent, source_verification_agent |
| **Minimum Source Count**（最低来源数量） | full = 15+，quick = 5-8，lit-review = 25+，systematic-review = 所有合格来源（无上限），fact-check = 每项声明3+ | bibliography_agent |
| **Verification Threshold**（验证阈值） | 100% DOI 检查 + 50% WebSearch 抽查 | source_verification_agent, ethics_review_agent |

> **跨技能参考**：参见 `shared/handoff_schemas.md` 了解阶段间数据交换格式。

---

## 1. 致命级（CRITICAL）严重度详细定义

致命级问题是铁律级问题——若不解决，将导致整个研究输出在学术上不可接受。以下为具体判定示例：

### 示例 1：引用虚构（Fabricated References）
- **场景**：报告中发现 DOI 不存在的文献，或标题/作者/年份与数据库记录完全不符
- **判定**：CRITICAL — 构成学术不端，必须立即删除并补充合法来源
- **不构成 CRITICAL 的边界**：DOI 存在但元数据有轻微差异（如年份差1年、副标题省略），属于 Major

### 示例 2：核心逻辑谬误（Fatal Logical Flaws）
- **场景**：报告核心结论依赖的论证链条存在根本性因果跳跃（如从相关性直接推导因果性，且无法提供机制解释）
- **判定**：CRITICAL — 核心结论不再有效
- **不构成 CRITICAL 的边界**：辅助性论据存在逻辑不严谨，但核心结论有独立支撑，属于 Major

### 示例 3：伦理阻断条件（Ethics Blocking Conditions）
- **场景**：缺少 AI 使用披露（AI Disclosure）、系统性的来源误导（systematic source misrepresentation）、抄袭（plagiarism）
- **判定**：CRITICAL — 学术诚信根本性违规，参见 `agents/ethics_review_agent.md` §"Blocking Conditions"
- **不构成 CRITICAL 的边界**：双用途（dual-use）风险评估仅属建议性（advisory），从不构成 CRITICAL；政治/机构敏感话题本身也不构成 CRITICAL

### 示例 4：证据与结论根本矛盾（Evidence-Conclusion Contradiction）
- **场景**：Phase 5 审查中发现报告的主要结论被其自身引用的数据反面支撑（如数据表明无显著差异，却结论称"显著改善"）
- **判定**：CRITICAL — 结论必须重写或证据必须重新收集
- **不构成 CRITICAL 的边界**：结论轻微超出证据支撑范围但仍在合理解释区间内，属于 Major

### 示例 5：方法论无法回答研究问题
- **场景**：Checkpoint 1 审查发现设计的方法论仅能回答描述性问题（"是什么"），但研究问题（RQ）要求因果解释（"为什么"）
- **判定**：CRITICAL — 研究设计根本无效
- **不构成 CRITICAL 的边界**：方法论能部分回答 RQ 但覆盖不完整，属于 Major

---

## 2. 来源层级（Source Tier）详细说明

### Tier 1：Q1 同行评审期刊
- **标准**：发表于 JCR/Scopus 学科排名前25%的期刊，或该领域公认的顶级会议（如 AI 领域的 NeurIPS/ICML/ACL）
- **判断依据**：期刊具有明确的影响因子排名或 CiteScore 排名；会议具有严格的接受率（< 30%）
- **边界案例**：
  - 新创期刊尚无排名 → 若编辑委员会由领域知名学者组成且遵循 COPE 规范，可临时归为 tier_1
  - Open Access 期刊 → 不因其 OA 性质降级，但需通过 DOAJ/COPE 验证排除掠夺性期刊
  - 预印本（Preprint） → 永远不属于 tier_1，即使作者后续发表于顶刊，预印本本身按 tier_3 处理

### Tier 2：其他同行评审
- **标准**：经过正式同行评审流程但不在 Q1 的期刊文章；或接受率较高（> 30%）的学术会议论文
- **判断依据**：期刊/会议具有可验证的同行评审声明
- **边界案例**：
  - 书籍章节（Book Chapter）→ 若出版社为知名学术出版社（如 Springer, Routledge, Oxford University Press），归为 tier_2
  - 仅编辑审查 → 不算同行评审，降级为 tier_3

### Tier 3：学术性但非同行评审
- **标准**：学术机构产出的工作论文（Working Paper）、预印本、学位论文、技术报告、智库报告
- **判断依据**：出自学术机构或研究组织，具有可识别的作者和机构隶属
- **边界案例**：
  - 博士论文 → 归为 tier_3（已通过委员会审查但非期刊同行评审）
  - 政府统计报告 → 若具有方法论说明，归为 tier_3；若无方法论说明，归为 tier_4

### Tier 4：灰色文献（Grey Literature）
- **标准**：新闻文章、博客文章、商业白皮书、政策简报、非学术机构报告
- **判断依据**：无正式学术评审，但可能包含有价值的事实数据或观点
- **边界案例**：
  - 国际组织报告（如 OECD, World Bank, UNESCO）→ 尽管非同行评审，因方法论严谨可酌情提升至 tier_3
  - 社交媒体帖子 → 始终归为 tier_4，无论发布者身份
  - 维基百科 → 始终归为 tier_4，不可作为主要证据来源

---

## 3. 最低来源数量场景细化

基础规则：full = 15+，quick = 5-8，lit-review = 25+，systematic-review = 无上限，fact-check = 每项声明3+。

### 按 RQ 类型的数量调整规则

| RQ 类型 | full 调整 | quick 调整 | lit-review 调整 | 说明 |
|---------|----------|-----------|----------------|------|
| 描述性（Descriptive）"是什么" | 12+ | 5+ | 20+ | 描述性研究通常文献更丰富，可适当降低 |
| 比较性（Comparative）"有何不同" | 15+（标准） | 6+ | 25+（标准） | 每个比较对象至少5篇 |
| 因果性（Causal）"为什么" | 20+ | 8+ | 30+ | 因果推断需要更强的证据密度 |
| 评价性（Evaluative）"好不好" | 18+ | 7+ | 28+ | 需兼顾正面和负面评价来源 |
| 探索性（Exploratory）"如何理解" | 10+ | 4+ | 15+ | 新兴领域文献稀缺可适当降低 |

### 特殊场景调整

- **跨学科研究**：每个涉及学科至少5篇，总数不低于标准要求的 120%
- **新兴领域（近3年文献占比 > 50%）**：可降低20%，但必须在报告中标注"Evidence Quality Limitations"
- **非英语文献为主**：数量要求不变，但需额外包含至少3篇英语文献以提供国际对比视角
- **fact-check 模式争议性声明**：需至少5篇来源（正反各至少2篇 + 1篇中立/元分析）

---

## 4. 验证阈值（Verification Threshold）操作规程

### 4.1 DOI 检查规程（100% 覆盖）

**执行步骤**：
1. 对所有非手动录入（`obtained_via != 'manual'`）的来源执行 DOI 解析
2. DOI 解析路径：Semantic Scholar API → Crossref API → OpenAlex API → arXiv API（如有 arXiv ID）
3. DOI 匹配规则：Levenshtein 相似度 >= 0.70 标题交叉验证
4. 若 DOI_MISMATCH（DOI 存在但标题不匹配）→ 标记为可疑，进入 WebSearch 二次验证

**判定标准**：
- DOI 存在且标题匹配 → PASS
- DOI 存在但标题不匹配 → DOI_MISMATCH → 需人工确认
- DOI 不存在 → 转入 WebSearch 验证
- 所有 API 均不可用 → 省略该索引信号（absent ≠ false）

### 4.2 WebSearch 抽查规程（50% 覆盖）

**抽样策略**：
1. 优先抽查 tier_3 和 tier_4 来源（100% 覆盖）
2. 抽查 DOI_MISMATCH 的来源（100% 覆盖）
3. 从 tier_1 和 tier_2 中随机抽取 30%
4. 确保总抽查比例 >= 50%

**执行步骤**：
1. 使用 WebSearch 搜索来源标题 + 作者
2. 确认来源存在于可验证的数据库或出版商网站
3. 交叉核对标题、作者、年份、期刊/出版商
4. 检查 Retraction Watch 数据库确认未被撤稿

**判定标准**：
- 搜索结果精确匹配 → VERIFIED
- 搜索结果部分匹配（如标题略不同）→ 需人工判断
- 搜索不到 → NOT_FOUND → 进入全层级验证
- 发现已被撤稿 → CRITICAL → 必须移除引用

### 4.3 多索引交叉验证（Cross-Index Triangulation）

当 k=3 个索引（Semantic Scholar + Crossref + OpenAlex）均报告 unmatched 时，视为正面不存在证据，触发 CRITICAL。当仅有1-2个索引报告 unmatched 时，视为覆盖缺口（coverage gap），不视为造假证据。

---

## 5. 严重度升级规则

### Minor → Major 升级条件

以下任一条件满足时，Minor 问题升级为 Major：
1. **重复出现**：同一类型的 Minor 问题在报告中出现 3 次及以上
2. **累积效应**：3个及以上 Minor 问题共同影响同一章节/论证的可靠性
3. **影响核心论点**：Minor 问题虽本身不严重，但恰好涉及报告核心结论的支撑证据
4. **用户特别关注**：用户明确指出该问题对其研究判断有显著影响

### Major → CRITICAL 升级条件

以下任一条件满足时，Major 问题升级为 CRITICAL：
1. **结构性扩散**：Major 问题影响报告 50% 以上的章节
2. **方法论根本缺陷**：Major 问题本质是方法论设计缺陷，导致后续所有分析不可靠
3. **诚信违规**：Major 问题涉及学术诚信（如系统性来源误导、抄袭）
4. **连续未修复**：经过一轮修订后 Major 问题仍未解决

### 升级时机

- **Checkpoint 审查时**：devils_advocate_agent 在每个 Checkpoint 评估时有权升级严重度
- **Phase 5 审查时**：editor_in_chief_agent 和 ethics_review_agent 在最终审查时可升级
- **跨阶段累积**：若同一问题在多个 Phase 被标记为 Major 但均未修复，在 Phase 5 自动升级为 CRITICAL

### 不允许降级

- 已确认的 CRITICAL 问题不可在任何情况下降级为 Major
- 已确认的 Major 问题不可降级为 Minor
- 修复后需重新评估——修复是"替换"而非"降级"

---

## 6. 学科领域货币性规则扩展表

| 学科领域 | 默认可接受年龄 | 快速变化子领域 | 可接受年龄（子领域） | 经典/奠基性作品豁免规则 |
|---------|-------------|-------------|-------------------|----------------------|
| **计算机科学 / AI** | 3年 | LLM, 生成式AI, 深度学习 | 1-2年 | Turing (1950), McCarthy (1956) 等奠基论文永久豁免 |
| **医学 / 临床** | 5年 | COVID-19, 基因疗法, 免疫治疗 | 2-3年 | Bradford Hill (1965) 因果标准永久豁免 |
| **教育学** | 7年 | EdTech, 在线学习, AI辅助教学 | 3-5年 | Bloom (1984), Biggs (1996) 等经典理论永久豁免 |
| **心理学** | 7年 | 认知神经科学, 社交媒体心理 | 3-5年 | Piaget, Vygotsky, Bandura 等经典理论永久豁免 |
| **社会学** | 10年 | 数字社会, 不平等研究 | 5-7年 | Bourdieu, Giddens, Beck 等经典理论永久豁免 |
| **经济学** | 7年 | 行为经济学, 加密经济学 | 3-5年 | Smith (1776), Keynes (1936) 等经典永久豁免 |
| **政治学 / 公共政策** | 10年 | 民主倒退, 气候政策 | 5-7年 | Dahl, Ostrom 等经典永久豁免 |
| **法律** | 取决于管辖权变更 | 欧盟数据保护法, AI监管法 | 2-3年 | 重要判例法永久有效（如 Marbury v. Madison） |
| **历史学 / 哲学** | 20年 | 数字史学 | 10年 | 所有一级历史文献永久豁免 |
| **工程 / 技术** | 5年 | 量子计算, 区块链, 自动驾驶 | 2-3年 | 奠基性工程标准（如 IEEE 754）永久豁免 |
| **环境科学 / 可持续发展** | 5年 | 气候模型, 碳捕获 | 3-5年 | IPCC 评估报告自发布日起5年内有效 |

### 经典/奠基性作品（Seminal Works）判定标准

作品需同时满足以下条件方可获得年龄豁免：
1. **被引量**：Google Scholar 被引 >= 500 次（人文领域 >= 100 次）
2. **范式定义**：该作品定义了后续研究的核心范式/概念/方法
3. **持续引用**：近5年内仍有活跃引用（年均 >= 10 次）
4. **未被推翻**：后续研究未从根本上否定其核心结论

---

## 7. 跨 Agent 一致性检查点

以下流程节点需要确认各 Agent 对质量定义的对齐，防止因理解差异导致输出不一致：

### Checkpoint 0：流水线启动前
- **参与 Agent**：research_question_agent, research_architect_agent
- **检查内容**：确认学科领域 → 货币性规则选择；确认 RQ 类型 → 最低来源数量标准
- **输出物**：Quality Scope Document（质量范围文档），包含领域、可接受年龄、来源数量阈值

### Checkpoint 1：方法论设计后
- **参与 Agent**：research_architect_agent, devils_advocate_agent
- **检查内容**：方法论是否与 RQ 类型匹配；Source Tier 使用标准是否明确；验证阈值计划是否完整
- **冲突解决**：devils_advocate_agent 有权否决不匹配的方法论设计

### Checkpoint 2：文献检索完成后
- **参与 Agent**：bibliography_agent, source_verification_agent
- **检查内容**：来源层级分类是否一致；DOI 检查和 WebSearch 抽查是否按规程执行；来源数量是否达到阈值
- **冲突解决**：若两 Agent 对同一来源的 Tier 分类不一致，以 source_verification_agent 的判定为准

### Checkpoint 3：综合分析后
- **参与 Agent**：synthesis_agent, devils_advocate_agent
- **检查内容**：证据与结论的一致性；是否使用了不当来源支撑核心结论；论证结构是否符合 Toulmin 模型
- **冲突解决**：devils_advocate_agent 发现 CRITICAL 问题时有权阻断流水线

### Checkpoint 4：报告完成后
- **参与 Agent**：editor_in_chief_agent, ethics_review_agent, report_compiler_agent
- **检查内容**：APA 7.0 格式一致性；伦理审查结果是否已整合；所有严重度升级是否已正确处理
- **冲突解决**：ethics_review_agent 的 BLOCKED 判定具有一票否决权（仅限诚信违规）

### Phase 间交接检查
- **触发时机**：每个 Phase 结束向下一 Phase 传递数据时
- **检查内容**：
  1. 传递的数据结构是否符合 `shared/handoff_schemas.md` 定义
  2. 所有来源的 verification_status 字段是否完整
  3. 严重度标签是否正确传递（不允许在交接中丢失或降级）
  4. Quality Scope Document 是否随数据一起传递

### 跨 Agent 定义冲突处理原则
1. **来源层级冲突**：以 source_verification_agent 判定为准
2. **严重度判定冲突**：以更高级别为准（宁可升级不可降级）
3. **货币性规则冲突**：以 Quality Scope Document 中的定义为共识
4. **最低数量争议**：按 RQ 类型的数量调整规则执行，有争议时取较高标准
