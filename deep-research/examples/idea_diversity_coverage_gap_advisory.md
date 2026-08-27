# 想法多样性 / 覆盖空白咨询示例

本示例展示两个 #257 咨询面。两者均为学术者注意的警示，而非阻断项。

## 1. 苏格拉底 (Socratic) 措辞模式咨询

用户草稿:

> I want to study "exploring the impact of AI feedback on student motivation."

苏格拉底导师回应节选:

```markdown
[WORDING_PATTERN_ADVISORY]
您的措辞"exploring the impact of AI feedback on student motivation"类似于一种常见的AI典型研究问题外壳: WP01 impact/effect框架。我不是在评判这个想法；我只是在标记措辞。你所在领域的专家会用什么术语、机制、场域或张力来替代？

你关心的具体反馈情境是什么: 自动评分、形成性评语、反馈时机，还是学生如何判断反馈是否值得采纳？
```

可接受的用户选择:

- 保留原始措辞，因为它与目标期刊的框架一致。
- 用领域原生术语重述，例如 "How do first-year engineering students decide whether AI-generated formative comments are actionable during lab-report revision?"
- 请导师帮忙对范围进行压力测试，而非重写研究问题 (RQ)。

边界: 咨询不说想法是泛化的或不好的。它仅标记措辞外壳。

## 2. 文献综述分布偏斜咨询

检索背景:

- 研究问题 (RQ): "How do AI feedback systems shape student revision behavior in higher education?"
- 最终纳入来源: 25
- 主题覆盖: 研究问题 (RQ) 的所有主要子主题均已覆盖
- 已知刊物/方法元数据:
  - 23/25 来源为2023年后的NLP或学习分析刊物
  - 21/24 已知方法条目为定量日志数据研究
  - 18/20 已知地理条目为北美或西欧

检索策略报告节选:

```markdown
### 覆盖分布咨询

DISTRIBUTIONAL_SKEW_ADVISORY:
- 维度: 时间分布
- 集中度: 2023-2026 = 23/25 (92%)
- 咨询: 这是一个覆盖分布信号，不是缺陷。考虑研究问题 (RQ) 是否需要更早的关于反馈摄取、修订行为或形成性评估的基础性工作。
- 检索回应: 从反馈素养和形成性评估的基础性作品添加向后引文追踪。

DISTRIBUTIONAL_SKEW_ADVISORY:
- 维度: 方法学分布
- 集中度: 定量日志数据研究 = 21/24 (87.5%)
- 咨询: 这是一个覆盖分布信号，不是缺陷。考虑该问题是否需要质性的或混合方法的证据，了解学生如何解读反馈。
- 检索回应: 添加检索字符串 ("AI feedback" OR "automated feedback") AND ("student interpretation" OR "feedback literacy" OR interview OR qualitative)。

DISTRIBUTIONAL_SKEW_ADVISORY:
- 维度: 地理分布
- 集中度: 北美 / 西欧 = 18/20 (90%)
- 咨询: 这是一个覆盖分布信号，不是缺陷。考虑制度情境是否改变反馈摄取方式。
- 检索回应: 添加台湾、东亚和双语高等教育研究的区域数据库检索。
```

边界: 文献目录仍然有效。咨询询问语料库分布是否匹配研究问题 (RQ)；它不拒绝检索也不强制扩展。
