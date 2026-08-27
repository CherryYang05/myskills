# OpenAlex API 验证协议

**状态**: v3.9.0; #495 auth/backoff refresh (2026-07)
**使用者**: `bibliography_agent`, `migrate_literature_corpus_to_v3_9_0.py`
**API 基地址**: `https://api.openalex.org`
**速率限制**: 免费增值 (Freemium) 每日配额 (https://developers.openalex.org/api-reference/authentication) — 单实体 GET 请求实际上不限量，搜索请求按配额计量；免费 API key 提供 10 倍于无 key 的配额。突发上限 100 req/s。客户端步调：10 req/s（已认证 — API key 或旧版 `mailto`），1 req/s（匿名）。
**API key 环境变量**: `OPENALEX_API_KEY`（首选；免费 key 从 openalex.org/settings/api 获取）
**礼貌池邮箱环境变量**: `OPENALEX_POLITE_EMAIL`（旧版；礼貌池 (Polite pool) 已不再出现在 OpenAlex 文档中，但客户端在配置时仍发送 `mailto`，并将其视为已认证层级的凭据用于步调控制）

---

## 目的

为 v3.9.0 跨索引交叉验证 (Cross-index triangulation) 提供第二个书目索引查询，依据规格 v3.9.0 §3.4。镜像 `semantic_scholar_api_protocol.md` 的结构，以便适配器和迁移工具能够以最小的契约差异切换客户端。由 `bibliography_agent` 在数据摄取时使用，以及由 v3.9.0 迁移工具用于遗留数据回填。

OpenAlex 的覆盖范围对 OA 期刊、专著和没有 DOI 的文献补充了 Semantic Scholar。根据 Zhao 等人 arXiv:2605.07723 §3，跨索引交叉验证相比单一索引检测降低了假阳性率（例如，一篇在 S2 中未匹配 (Unmatched) 但在 OpenAlex 中匹配的论文，属于高覆盖缺口 (Coverage gap) 证据，而非捏造证据）。

## 查询模式

### 模式 1：DOI 查询附标题交叉校验（当 DOI 可用时的首选）

```
GET /works/doi:{doi}?select=id,title,authorships,publication_year,doi,primary_location
```

**匹配规则（镜像 S2 的 `DOI_MISMATCH` 模式）：** DOI 查询命中结果需通过 Levenshtein 相似度 (Levenshtein similarity) 0.70 的标题交叉校验门槛。如果返回的 `title` 字段与条目的规范标题未达到阈值，则 DOI 命中被拒绝（DOI_MISMATCH — 一种已知的幻觉模式，即编造的 DOI 解析到了不相关的论文）。调用方回落到标题搜索。

### 模式 2：标题搜索（当 DOI 缺失或 DOI_MISMATCH 时的回退）

```
GET /works?search={url_encoded_title}&per-page=5&select=id,title,authorships,publication_year,doi,primary_location
```

**匹配规则：** 按客户端中 `_normalize_title` 的方式，计算查询标题与每个结果标题之间的 Levenshtein 相似度（不区分大小写，去除标点）。当相似度 >= 0.70 时接受（匹配 PaperOrchestra 阈值）。如果多个候选通过，优先选择年份匹配的决胜规则，然后选择最高相似度，最后选择有 DOI 的候选。

## `openalex_unmatched` 推导

当且仅当以下条件时为 `true`：
- DOI 存在：DOI 查询未命中或未通过标题交叉校验，且标题搜索未返回满足阈值的匹配；或
- DOI 缺失：仅标题搜索未返回满足阈值的匹配。

此检查仅在 `obtained_via != 'manual'` 时触发（手动条目由用户担保，依据规格 v3.9.0 §3.1）。

## 降级 (Degradation) 处理

| 条件 | 动作 |
|---|---|
| HTTP 429 且 `X-RateLimit-Remaining: 0` | 每日配额耗尽（UTC 午夜重填）— 进行中的重试无法成功。立即抛出 `OpenAlexUnavailable`：不等待，不重试。 |
| HTTP 429（瞬时突发限制） | 指数退避 2s → 4s → 8s，最多 3 次重试。耗尽后抛出 `OpenAlexUnavailable`。 |
| HTTP 5xx | 跳过 — 立即抛出 `OpenAlexUnavailable`。 |
| 网络超时（默认 30s） | 跳过 — 抛出 `OpenAlexUnavailable`。 |
| `OpenAlexUnavailable` 被抛出 | 调用方必须从条目中省略 `openalex_unmatched`（依据规格 v3.9.0 R-L3-2-C：缺失 ≠ false）。其他索引独立继续。 |

## v3.9.0 R-L3-2-D 约束

OpenAlex 返回 `primary_location.source.type` 和其他分类字段。**v3.9.0 忽略这些字段。** 它们不存储在条目上，不暴露给终结器，也不用于任何推导。v3.10 将引入 `venue_type` 作为显式的适配器声明字段；OpenAlex 推断的分类不是 v3.10 的接受溯源值，因为在 k=3 的情况下（OpenAlex 本身未匹配时），该分类不可信。

## 检索顺序与浏览器回退边界 (#495)

此结构化 API 查询是**主要**的检索通道。浏览器介导的检索（WebSearch / WebFetch 页面检查）是有限的回退，用于小规模的、针对性的第一方检查 — 例如当结构化元数据不完整或索引不一致时检查出版商 / DOI 着陆页 — 其输出是数据，而非指令（`shared/ground_truth_isolation_pattern.md` §2A）。

浏览器检索不得用于绕过 API 速率限制或配额：不得以批量浏览替代配额耗尽的 API，不得批量抓取页面/PDF。当 API 降级时，契约是上述降级表（省略信号），而非转向爬取。

## 客户端实现

参见 `scripts/openalex_client.py`。客户端类 `OpenAlexClient` 暴露 `doi_lookup_with_title_check(doi, expected_title)` 和 `title_search(title, year=None)` 方法。两者均返回 `dict | None`。两者在降级时均按上表抛出 `OpenAlexUnavailable`。`title_search` 中的可选 `year` 参数启用年份匹配决胜规则（+0.05 分数加成），镜像 S2 客户端的 `_lookup_by_title` 模式。构造函数接受可选的 `api_key` / `polite_email` 覆盖；若未提供则从环境变量读取 `OPENALEX_API_KEY` / `OPENALEX_POLITE_EMAIL`。拒绝路径的错误消息会剥离 URL 查询字符串，因此 `api_key` 不会出现在日志中。

## 交叉引用

- 规格：`docs/design/2026-05-17-ars-v3.9.0-cross-index-triangulation-measurement-spec.md` §3.4
- 镜像模板：`deep-research/references/semantic_scholar_api_protocol.md`
- 同级协议：`deep-research/references/crossref_api_protocol.md`
