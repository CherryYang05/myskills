# Crossref API 验证协议

**状态**: v3.9.0
**使用者**: `bibliography_agent`, `migrate_literature_corpus_to_v3_9_0.py`
**API 基地址**: `https://api.crossref.org`
**Rate limit**: 10 req/s (礼貌池 (polite pool)，User-Agent 中包含 `mailto:`)，~5 req/s（匿名，有波动）。已通过线上 `x-rate-limit-limit` / `x-rate-limit-interval` 响应头确认（2026-05）。
**礼貌池邮箱环境变量**: `CROSSREF_POLITE_EMAIL`（可选）

---

## 目的

为 v3.9.0 跨索引三角验证 (cross-index triangulation) 提供第三个书目索引查询，依据规范 v3.9.0 §3.5。Crossref 是 DOI 的权威注册机构——对带有 DOI 的期刊文章覆盖最强。专著 (monograph) / 章节 (chapter) 覆盖不完整（取决于出版商参与度）。v3.9.0 将 `crossref_unmatched` 作为三个信号之一暴露，依据 R-L3-2-A 处理（默认为咨询性质；用户启用的 `contamination_triangulation` 严格策略可将 k=3 三角验证信号提升为终端阻断——参见 `shared/references/firm_rules.md`）。

结构与 `semantic_scholar_api_protocol.md` 和 `openalex_api_protocol.md` 保持一致。

## 查询模式

### 模式 1：DOI 查询加标题交叉校验（DOI 可用时的首选）

```
GET /works/{doi}
```

注意：路径中使用原始 DOI，不加 `doi:` 前缀（Crossref 惯例；OpenAlex 使用 `/works/doi:{doi}`）。

**匹配规则（镜像 S2 的 `DOI_MISMATCH` 模式）：** DOI 查询命中的结果须经 Levenshtein 相似度 0.70 的标题交叉校验门控。Crossref 将 `title` 作为语言变体列表返回；取第一个条目进行比较。若相似度低于阈值 -> DOI_MISMATCH，返回 None，向下回退到标题搜索。

### 模式 2：标题搜索（DOI 缺失或 DOI_MISMATCH 时的回退方案）

```
GET /works?query.title={url_encoded_title}&rows=5
```

**匹配规则：** Levenshtein 相似度 >= 0.70（与 S2 / OpenAlex / PaperOrchestra 阈值一致）。当多个候选通过阈值时，优先匹配年份作为决胜条件，通过 +0.05 分数加成实现。Crossref 年份位于 `issued.date-parts[0][0]`（规范字段）；若 `issued` 缺失，则回退到 `published-print` / `published-online`。

## `crossref_unmatched` 推导

当且仅当以下条件时为 `true`：
- DOI 存在：DOI 查询返回 404，或未通过标题交叉校验，且标题搜索未返回达到阈值的匹配；或
- DOI 缺失：仅标题搜索未返回达到阈值的匹配。

此检查仅在 `obtained_via != 'manual'` 时触发。

## 降级处理

| 条件 | 操作 |
|---|---|
| DOI 查询返回 HTTP 404 | 视为未命中——从 `_get` 返回 `{}`；调用方向下回退到标题搜索。不属于降级。 |
| HTTP 429（rate limit） | 退避 2 秒，最多重试 3 次。耗尽后抛出 `CrossrefUnavailable`。每次退避后刷新节流锚点。 |
| HTTP 5xx | 立即抛出 `CrossrefUnavailable`（不重试）。 |
| 网络超时（默认 30s） | 抛出 `CrossrefUnavailable`。 |
| 抛出 `CrossrefUnavailable` | 调用方必须从条目中省略 `crossref_unmatched`（依据规范 v3.9.0 R-L3-2-C：缺失 != false）。其他索引独立继续。 |

## v3.9.0 R-L3-2-D 约束

Crossref 返回 `type`（例如 `journal-article`, `book-chapter`）。**v3.9.0 忽略此字段。** 不存储在条目上，不暴露给终结器 (finalizer)，不用于任何推导。v3.10 将引入适配器声明的 `venue_type`，并带有显式来源标识 (provenance)。

## Crossref 特定说明

- **覆盖范围注意事项：** 对带有 DOI 的期刊文章覆盖最强。专著 / 章节的覆盖取决于出版商的 DOI 注册。会议论文集覆盖情况不一。这种不对称性是设计如此——与 S2 和 OpenAlex 结合，三索引信号捕获不同的文献类型分布。
- **礼貌池礼仪：** User-Agent 头（非查询参数）中的 `mailto:` 遵循 Crossref 文档中约定的更高速率限制惯例。

## 客户端实现

参见 `scripts/crossref_client.py`。`CrossrefClient` 类暴露 `doi_lookup_with_title_check(doi, expected_title)` 和 `title_search(title, year=None)` 两个方法。两者均返回 `dict | None`（dict 为 DOI 查询的 `message`，或标题搜索的 `message.items` 中的一项）。两者在降级时均按上表抛出 `CrossrefUnavailable`。

## 交叉引用

- 规范：`docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md` §3.5
- 镜像模板：`deep-research/references/semantic_scholar_api_protocol.md`
- 同级协议：`deep-research/references/openalex_api_protocol.md`
