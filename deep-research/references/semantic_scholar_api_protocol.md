# Semantic Scholar API 验证协议（Verification Protocol）

**状态**: v3.3
**使用者**: `source_verification_agent`, `bibliography_agent`, `integrity_verification_agent`
**API 基地址**: `https://api.semanticscholar.org/graph/v1`
**速率限制（Rate limit）**: 1 请求/秒（未认证），10 请求/秒（使用 API key）
**API key 环境变量**: `S2_API_KEY`（可选；未设置时优雅降级）

---

## 目的

通过 Semantic Scholar Academic Graph API 对参考文献的存在性和书目（bibliographic）准确性进行程序化验证。该协议补充（而非替代）基于 WebSearch 的验证，通过增加结构化的、基于 API 的检查来返回机器可读的元数据。

PaperOrchestra（Song et al., 2026）表明，两阶段引用流水线（citation pipeline）—— (1) 通过网络搜索进行广泛发现，（2）通过 Semantic Scholar API 进行顺序验证——能够实现显著更高的引用覆盖率（P0 Recall +2-6%，P1 Recall +12-14%，相对于基线）。ARS 将该验证阶段作为现有多层验证策略中的附加层级予以采纳。

---

## 查询模式

### 模式 1: 标题搜索（Title Search，主要）

```
GET /paper/search?query={url_encoded_title}&limit=5&fields=title,authors,year,externalIds,venue,publicationDate
```

**匹配规则**: 计算查询标题与每个结果标题之间的 Levenshtein 相似度（不区分大小写，去除标点）。当相似度 >= 0.70 时予以接受（与 PaperOrchestra 的阈值一致）。若多个结果 >= 0.70，优先选择年份匹配的结果。

### 模式 2: DOI 查询（当 DOI 可用时）

```
GET /paper/DOI:{doi}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
```

**匹配规则**: DOI 匹配为精确匹配。交叉检查返回的标题是否与参考文献标题匹配（Levenshtein >= 0.70）。若 DOI 匹配但标题不匹配，标记为 `DOI_MISMATCH`——这是一种已知的幻觉（hallucination）模式，即伪造的 DOI 解析到了一篇不相关的论文。

### 模式 3: Semantic Scholar ID 查询（用于重新验证）

```
GET /paper/{paperId}?fields=title,authors,year,externalIds,venue,publicationDate,citationCount
```

在重新验证先前已解析为 Semantic Scholar ID 的参考文献时使用（该 ID 存储在书目的 `semantic_scholar_id` 字段中）。

---

## 验证层级（Verification Tiers，已更新 S2 API）

| 层级 | 方法 | 覆盖范围 | 目的 |
|------|------|----------|------|
| **Tier 0（新增）** | Semantic Scholar API | 100% 的参考文献 | 程序化存在性检查 + 元数据提取 |
| Tier 1 | DOI 解析（resolution） | 100% 含 DOI 的参考文献 | URL 级别存在性检查 |
| Tier 2 | WebSearch 抽查（spot-check） | 50% 的来源 | 人类可读验证 |

**执行顺序**: 优先执行 Tier 0（批量，1 请求/秒）。通过 Tier 0 的参考文献跳过 Tier 2，除非因其他原因被标记。未通过 Tier 0 的参考文献进入 Tier 1 + Tier 2 进行人工调查。

---

## 响应处理

### 匹配成功时

在参考文献的验证审计记录（audit trail）中记录以下内容：
- `semantic_scholar_id`: S2 论文 ID（例如，`"649def34f8be52c8b66281af98ae884c09aef38b"`）
- `s2_title`: 返回的标题
- `s2_authors`: 返回的作者列表
- `s2_year`: 返回的年份
- `s2_venue`: 返回的发表场所（venue）
- `s2_citation_count`: 引用次数（供参考）
- `match_score`: Levenshtein 相似度分数
- `verification_method`: `"s2_title_search"` 或 `"s2_doi_lookup"`

### 无匹配时

- 若 0 个结果的 Levenshtein >= 0.70：分类为 `S2_NOT_FOUND`
- `S2_NOT_FOUND` 并不自动意味着虚构——该论文可能存在但未被 Semantic Scholar 索引（例如，非常新近、非英语、灰色文献/grey literature）
- 继续进入 Tier 1（DOI）和 Tier 2（WebSearch）进行进一步调查
- 若所有层级均失败：按现有协议分类为 `NOT_FOUND`

### API 失败时

- HTTP 429（速率限制）: 退避（back off）2 秒，最多重试 3 次
- HTTP 5xx: 跳过该参考文献的 S2 检查，进入 Tier 1
- 网络错误: 跳过剩余批次的全部 S2 检查，记录 `[S2-API-UNAVAILABLE]`
- **切勿因 S2 API 失败而阻塞流水线**——优雅降级至仅使用 WebSearch 的现有验证方式

---

## 基于 S2 ID 的去重（Deduplication）

当两篇参考文献解析到相同的 `semantic_scholar_id` 时，标记为重复。`bibliography_agent` 在搜索期间利用此信息进行去重（与 PaperOrchestra 通过 Semantic Scholar ID 去重的方法一致）。

---

## 成本与性能

- **每篇论文的 API 调用次数**: 约 30-80 次（每条参考文献一次，典型论文有 30-80 条参考文献）
- **耗时**: 在 1 请求/秒（未认证）下，完整论文需 30-80 秒。使用 API key（10 请求/秒）时：3-8 秒
- **成本**: 免费（Semantic Scholar API 对学术用途免费）
- **建议**: 设置 `S2_API_KEY` 以加速验证。可从 https://www.semanticscholar.org/product/api#api-key 获取

---

## 参考文献

- Song, Y., Song, Y., Pfister, T., & Yoon, J. (2026). PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper Writing. *arXiv preprint arXiv:2604.05018*. — Section 4 Step 3 (Literature Review Agent), Appendix D.3 (Citation Verification).
- Semantic Scholar API 文档: https://api.semanticscholar.org/
