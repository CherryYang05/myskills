# 逐源方法学弱点的证据规范（上游 #916，中文适配）

**用途**：为 bibliography_agent、source_verification_agent、证据评估模板和 three-way-scan 提供一致的信息披露规则。方法学弱点仅供研究者判断，**不自动阻断、评分、改写研究问题或提出改进方向**。

## 必须满足的条件

1. **具体设计 + 失效条件**：说明某个具体样本、测量、实验设计或分析选择，在什么条件下可能扭曲结论。「样本量小」不够具体；「单中心 n=24，无法区分中心效应与处理效应」才有可核查意义。
2. **逐条标注来源**：`author-acknowledged` 表示作者在原文承认，必须附 `quote` / `page` / `section` / `paragraph` 之一的定位；`reader-inferred` 表示阅读者推断，须明确标注**尚未验证**。
3. **对缺失陈述限定阅读范围**：声称「作者没有讨论 X」时，必须列出实际检查过的章节；无法列出则不得做此断言。
4. **按论文类型固定检查维度**：实证研究关注样本、设计、测量、混杂和统计；理论研究关注假设、推导和边界；综述关注检索、筛选、偏倚与合成；案例研究关注案例选择和外推；政策研究关注证据链、反事实与适用范围。每项记为 `checked: found`、`checked: none found` 或 `not checked`。完整上游环境可使用 `academic-paper-reviewer/references/review_criteria_framework.md` 的固定类型表；本地独立安装时仅使用上述简化检查维度，不能宣称执行了缺失的上游框架。
5. **没有正文就不推断方法学弱点**：仅获得摘要、目录或未知阅读范围时，写 `not assessed (read scope: abstract_only/toc_only/unknown)`；只读部分章节时，仅在已读章节内作有限判断。

## 推荐输出

```markdown
- **Method weaknesses** (<paper type>; read: <已读章节或全文>)
  - checked: found: <criterion> | checked: none found: <criterion> | not checked: <criterion>
  - <具体设计选择>；在 <条件> 下可能导致 <偏差>。[author-acknowledged, section: <位置>]
  - <另一潜在弱点>。[reader-inferred, untested]
```

没有足够原文时：

`- **Method weaknesses**: not assessed (read scope: abstract_only)`

记录应短而可复核，避免将不确定的推断包装成作者已经承认的局限性。
