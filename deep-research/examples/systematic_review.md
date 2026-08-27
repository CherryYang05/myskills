# 示例: 系统文献综述 (lit-review 模式)

## 用户请求
```
Literature review on the effectiveness of micro-credentials in professional development
```

**模式**: `lit-review`（bibliography_agent + source_verification_agent + synthesis_agent）

## bibliography_agent 输出

### 检索策略

**数据库**: Scopus、Web of Science、ERIC、ProQuest Education
**关键词**:
- 主要: "micro-credentials" OR "micro-certifications" OR "digital badges" OR "stackable credentials"
- 组合: "professional development" OR "workforce development" OR "continuing education" OR "upskilling"
- 筛选: 2018-2025, 英文, 同行评审 (Peer-reviewed) + 精选灰色文献 (Grey literature)

**PRISMA 流程**:
```
识别记录: 1,243
├── Scopus: 412
├── Web of Science: 389
├── ERIC: 287
└── ProQuest: 155

去除重复: 318
筛选记录（标题/摘要）: 925
排除记录: 791
  - 非微证书主题: 423
  - 非专业发展情境: 198
  - 仅意见/社论: 102
  - 非英文: 68
评估全文文章: 134
全文排除: 96
  - 方法学描述不足: 41
  - 聚焦K-12而非高等教育/专业发展: 32
  - 重复数据集: 14
  - 无法获取全文: 9
纳入综合分析 (Synthesis) 的研究: 38
```

### 注释文献目录 (Annotated Bibliography)（选录条目）

1. **Kato, S., Galan-Muros, V., & Weko, T. (2020). The emergence of alternative credentials. *OECD Education Working Papers*, No. 216. https://doi.org/10.1787/b741f39e-en**
   - 相关性: OECD关于替代证书生态系统的全面政策分析
   - 关键发现: 微证书在OECD国家日益普及但缺乏标准化；质量保障 (Quality Assurance) 是关键挑战
   - 方法学: 跨国比较政策分析
   - 质量: 等级VII（政策报告）但机构可信度高

2. **Ralston, S. J. (2021). Higher education's micro-credentialing craze: A postdigital-Deweyan critique. *Postdigital Science and Education*, *3*(1), 83-101.**
   - 相关性: 对微证书运动的批判性视角
   - 关键发现: 警告学习商品化；微证书可能将教育缩减为狭隘技能培训
   - 质量: 等级VII（哲学/批判分析）
   - 贡献: 主流正面叙事的重要反面观点

3. **Wheelahan, L., & Moodie, G. (2021). Analysing micro-credentials in higher education: A Bernsteinian analysis. *Journal of Curriculum Studies*, *53*(2), 212-228.**
   - 相关性: 理解微证书设计的理论框架
   - 关键发现: 微证书有"分割主义"知识路径的风险；需要嵌入连贯课程体系
   - 质量: 等级VI（带经验说明的理论分析）

[... 其余35个来源 ...]

## source_verification_agent 输出

### 来源质量矩阵

| 评级 | 数量 | 百分比 |
|------|------|--------|
| A | 5 | 13% |
| B | 14 | 37% |
| C | 12 | 32% |
| D | 6 | 16% |
| F | 1 | 3% |

**标记项**:
- 来源 #22: 掠夺性期刊 (Predatory journal) 指标（快速录用、未列出编委会）-> 排除
- 来源 #31: 作者为微证书平台CEO -> 已标注COI，附注意事项纳入
- 来源 #8, #15, #29: 2020年前数据可能不反映疫情后加速 -> 时效性注意事项

**最终纳入**: 37个来源（1个因质量问题排除）

## synthesis_agent 输出

### 文献矩阵 (Literature Matrix)（精简版）

| 主题 | 支持来源 | 反对来源 | 有争议 | 强度 |
|------|---------|---------|--------|------|
| 雇主认可度提升 | 8 | 3 | 2 | 中等 |
| 学习者完成率高 | 6 | 4 | 1 | 有争议 |
| QA框架不充分 | 12 | 1 | 0 | 强 |
| 公平性效益 | 9 | 5 | 3 | 有争议 |
| 技能-岗位匹配 | 11 | 2 | 1 | 中等至强 |

### 综合分析 (Synthesis) 叙述

**主题1: 质量保障框架滞后**（强证据）
文献中最强有力的发现是现有QA框架并非为微证书而设计。37个来源中有12个涉及此主题，几乎一致认为当前的认证模式 — 为学位项目设计 — 不能很好地映射到短期、能力导向的证书上 (Kato et al., 2020; Wheelahan & Moodie, 2021)。欧洲通过欧洲MOOC联盟在通用框架方面取得了进展 (Witthaus et al., 2016)，但采纳仍然不均衡。多位作者认为，缺乏稳健的QA，微证书生态系统有沦为"狂野西部"般未经验证声明的风险 (Ralston, 2021)。

**主题2: 技能-岗位匹配前景可观**（中等至强证据）
证据表明微证书改善了技能与岗位的匹配，尤其在技术和医疗保健领域。雇主调查一致报告对拥有微证书及学位的候选人满意度更高 (Brown & Kurzweil, 2023)。然而，匹配程度在很大程度上取决于行业参与证书设计 — 未经雇主输入开发的证书显示出较弱的劳动力市场成果 (Weise, 2020)。

**主题3: 公平性结果有争议**（有争议证据）
文献对微证书是改善还是恶化教育公平存在分歧。支持者引用低成本、灵活排课和针对性技能发展作为服务不足人群的益处 (Fishman et al., 2023)。批评者反驳微证书可能创造双轨制: 弱势学习者获得"证书碎片"，而特权学习者追求完整学位 (Wheelahan & Moodie, 2021)。解决方案似乎取决于情境: 当微证书可堆叠指向学位时，公平性效益更强；当它们作为独立替代品时，分层风险增加。

**主题4: 雇主认可度增长但不均衡**（中等证据）
自2020年以来，雇主对微证书的认可度显著提升，部分受疫情加速数字化转型推动。然而，认可度因行业、地区和证书提供者而差异巨大。技术行业雇主显示最高接受度（近期调查78%），而法律和金融等传统行业仍持怀疑态度（低于30%）(Digital Promise, 2024)。

**主题5: 完成率与参与模式因设计而异**（有争议证据）
微证书项目的完成率从25%到85%不等，取决于项目设计、支持结构和学习者人口学特征。自主在线格式完成率最低（25-40%），而混合组班模式达到最高率（70-85%）。重要的是，多项研究指出"完成"可能不是正确的衡量标准 — 有些学习者通过完成特定模块实现了他们的目标，而无需完成完整证书 (Reich & Ruiperez-Valiente, 2019)。

### 知识空白
1. **纵向成果**: 无研究追踪微证书持有者超过3年
2. **非英语语境**: 89%的研究来自英语国家
3. **成本效益**: 未发现严格的成本效益分析
4. **堆叠行为**: 关于学习者如何随时间组合微证书的证据有限

### 矛盾
| 主张A | 主张B | 评估 |
|---------|---------|-----------|
| 微证书民主化获取（9个来源） | 微证书扩大数字鸿沟（5个来源） | 取决于情境: 依赖基础设施、数字素养和成本 |
| 高完成率（6个来源） | 弱势学习者完成率低（4个来源） | 取决于人群: 完成率因人口学特征差异显著 |

---

## 最终输出
- 注释文献目录 (Annotated Bibliography): 37个来源，APA 7.0
- 文献矩阵 (Literature Matrix): 5个主题 × 37个来源
- 综合分析 (Synthesis) 叙述: 约3,200字
- 4个知识空白已识别
- 2个重大矛盾已分析
- 每个主题的证据强度评估
