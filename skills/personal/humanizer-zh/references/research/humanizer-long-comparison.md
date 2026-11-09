# Humanizer 长稿对照

本轮分别试改中文、英文的技术复盘和个人随笔，共四篇自拟稿。中文按汉字数计，英文按单词数计，均含标题和表格文字。每篇有十个正文段落。原稿有明显套话，也保留了一些读来已经顺畅的段落，便于观察改稿是否过度。

## 怎么比

- **直接改**只看改稿要求和原稿。**上游**用上一轮留存的 [blader/humanizer v3.1.0](https://github.com/blader/humanizer/blob/main/SKILL.md) 和 [op7418/Humanizer-zh 2026-09-23 版](https://github.com/op7418/Humanizer-zh/blob/main/SKILL.md)。**上一版**用 `humanizer-edit-zh`、`humanizer-edit-en`。**微调初稿**是本次 `humanizer-zh`、`humanizer-en` 在盲评前的版本。
- 先跑直接改、上游和上一版。根据长稿里观察到的问题微调，再让独立会话用微调初稿重跑同一批稿。每个条件各跑一次，共 16 份结果。改稿后逐篇随机打乱标签，由不知道版本对应关系的模型分别评阅中文和英文。先核对原意和结构，再看可读性、跨段一致性和作者口吻，允许并列。
- 表格、标题、命令、链接目标、引文和随笔段落数另外与原稿比对。原样段落数仅作辅助观察。改得更少本身不代表改得更好。

## 逐篇结果

| 样稿 | 篇幅 | 盲评排序 | 微调初稿结构检查 |
| --- | ---: | --- | --- |
| 中文技术复盘 | 1,193 字 | 上游 Humanizer ＞ 微调初稿 ＞ 上一版 ＞ 仅用改稿要求 | 通过 |
| 中文随笔 | 1,025 字 | 上一版 ＝ 上游 Humanizer ＞ 仅用改稿要求 ＞ 微调初稿 | 通过 |
| 英文技术复盘 | 835 词 | 上一版 ＞ 微调初稿 ＞ 上游 Humanizer ＝ 仅用改稿要求 | 通过 |
| 英文随笔 | 804 词 | 微调初稿 ＝ 上一版 ＝ 仅用改稿要求 ＞ 上游 Humanizer | 通过 |

| 微调初稿对照对象 | 中文胜／平／负 | 英文胜／平／负 |
| --- | ---: | ---: |
| 上游 Humanizer | 0／0／2 | 2／0／0 |
| 上一版 | 1／0／1 | 0／1／1 |
| 仅用改稿要求 | 1／0／1 | 1／1／0 |

- **中文上游版更稳。** 在技术稿里，上游明确说完成率来自全部 48 个工作区中符合口径的任务，也保住了扩试点的“日志覆盖”条件。微调初稿写成完成“补抽日志”，让覆盖到位的要求没那么明确，也把“状态一致性问题”泛化为“状态存疑”。在随笔里，上游与上一版并列。微调初稿保住了橘子和收音机的回扣，但把一口气说完的自我纠正拆成了两句。
- **英文微调初稿好于上游，上一版仍值得保留。** 英文技术稿里，上一版把故障写为一种模式，保留了模式中出现超时这一点。微调初稿写成多项作业超时的模式，读者更容易推断原文未说明的观察次数。上游改成一次超时，丢了模式这一层。英文随笔中，微调初稿、上一版和直接改并列，差异主要在修理多层从句时先写包裹还是先写留下包裹的人。
- **删掉套话不构成优势。** 只给一条具体改稿要求，也能删掉四篇里明显的套话，16 份改稿都通过了结构比对。差距更多来自句子和段落背后的限定，而这些限定往往也是最容易被当作重复删掉的内容。

四篇是为测试编写的样稿。第一次微调用了这批稿里暴露的问题，之后也用同一批稿复测。每篇、每个版本只有一次改稿和一次模型评阅。这次对照可以用来审查具体取舍。

## 两个版本各改了什么

| 版本 | 保留的语言重点 | 长稿微调 |
| --- | --- | --- |
| `humanizer-zh` | 中文话题衔接、抽象措辞和语体错位 | 跨段核对对象、指标和责任人，保留原文的触发状态和验收标准。删去随笔里的套话后，优先用原句接回叙事。 |
| `humanizer-en` | 英文嵌套、修饰范围和句界提示 | 跨段核对术语与证据范围。区分故障模式和单次事件、复核请求和操作许可。原文未交代观察次数时，改稿保留这个未知。 |

## 交付版定点复核

盲评之后，交付版补了触发状态、验收标准、随笔停顿和观察次数的检查。用三段新稿复核这些改动，结果单独记录，盲评表仍按当时的版本计算。

| 新片段 | 检查点 | 交付版表现 |
| --- | --- | --- |
| 中文交接 | 区分状态不一致与状态不明，抽完日志与覆盖到位 | 保留了两种状态的不同处理。已抽查三个节点与两个机房晚高峰覆盖未确认分开交代，恢复自动切换仍需同时满足日志覆盖和工单核查。 |
| 中文随笔 | 删除套话后的衔接、口吻和物件回扣 | 只删除第二段开头的套话，其余文字逐字保留。原话、停顿和塑料袋的回扣都在原位。 |
| 英文交接 | 保留观察次数未知、审批权限和两个重启条件 | 拆开了嵌套从句，仍写明复核者没说样本有几例。保留了复核消息的权限限制、两项重启条件和 06:00、08:00 两个时间。 |

## 原稿与全部改稿

### 中文技术复盘

**改稿要求**

请润色下面的试点复盘。读者是负责批准下一轮试点的工程和支持同事。保留标题、段落层次、链接、表格、引文和命令。改顺正文和套话，保留范围、指标口径和原作者的谨慎语气。只给改好的正文。

**原稿**

```markdown
# 导出队列试点复盘

## 试点范围

为进一步推动导出体验优化工作的持续落地，我们在 9 月 7 日至 9 月 11 日对 48 个主动报名的工作区开启了新队列。本轮观察只包含这些工作区里的手动 CSV 导出，定时导出和 API 触发的导出仍走旧队列。支持团队也看了同一批工作区前一周的数据，作为对照口径。两周都使用 UTC 记录时间，表里只纳入当周提交且当周结束的任务。

这 48 个工作区里，有 12 个在试点开始前已经开启缓存。支持团队只从这 12 个工作区抽了错误日志。其余 36 个工作区仍计入下表的任务指标。这个区别值得反复强调，因为后文对错误类型的讨论来自日志，完成率则来自全量任务记录。[口径说明](./metrics.md#exports)里还列出了跨周任务的处理方式。

| 指标 | 前一周 | 试点周 |
| --- | ---: | ---: |
| 手动 CSV 任务数 | 1,240 | 1,310 |
| 完成率 | 96.1% | 97.4% |
| 完成任务的 p95 耗时 | 78 秒 | 71 秒 |

## 为什么暂时不扩大

从上述指标可以看到，本轮试点在导出任务顺利完成方面释放了积极信号。完成率上升了 1.3 个百分点。p95 的统计对象是已完成任务，超时任务不在分母内，所以耗时的变化只说明完成任务的情况。试点周我们还缩短了重试间隔，两周的工作负载也没有做匹配。现在还不能判断完成率的变化有多少来自新队列。

支持同事对 12 个工作区的错误日志进行了逐条查看，发现可重试的连接中断少了一些。只有这 12 个工作区参加了日志抽样，因此还不知道其他工作区是否出现了同样的变化。有一条工单把用户看到的现象说得很清楚：“页面显示完成，但导出的文件一直没出现。”该工单在 9 月 11 日仍未关闭。它对应的是文件交付问题，现有完成率只记录任务状态。

支持团队还查了两个在试点周收到的定时导出工单。它们和前面那条工单的现象相似，但定时导出没有走新队列，两个工单也没有纳入这轮日志抽样。工单会保留在支持队列，另行排查。这里说明这个情况，是为了避免把用户描述相似的工单都当成试点证据。即使下一轮加上定时导出，也要先分别记录手动和定时任务的结果。

## 值班如何判断要不要重跑

对于涉及新旧队列切换后的待处理任务状态一致性问题，值班同事要先查原任务状态，再确认原任务是否已经写过文件。只有原任务超时、没有写入文件、且两个队列的重试间隔一致时，才可以手动重跑。若状态为未知，先在值班群报任务 ID，等支持团队核对。用于预览的命令是 `queue retry --dry-run`，预览不会重跑任务。

这里再说明一个容易混淆的情况。任务已经写完文件但页面仍在等待时，值班先通知支持团队查交付记录。上面的重跑条件仍然适用。队列有空位和收到用户催单都不能替代状态检查。支持团队会把查到的记录贴回原工单，试点组再据此核对任务记录和文件交付记录。

有时候同一个人会在群里和工单里各问一次。支持团队按任务 ID 合并记录，仍在原工单回复。若两条消息没有提供任务 ID，先请用户补充，值班同事暂时不合并。这个约定只用于记录跟进情况，与任务能否重跑无关。

## 下一轮如何做

下一轮计划沿用同一批工作区，保持重试间隔固定，另外补抽未开启缓存的工作区日志。我们还想让支持和工程一起对照任务完成记录与文件交付记录，看看“任务完成”能覆盖多少用户真正拿到文件的情况。两项工作还未排期。等日志覆盖和工单核查都完成后，工程组再决定是否把试点扩到定时导出。

整体而言，这次复盘为后续导出能力的持续优化提供了新的实践基础。试点期间先维持原来的值班流程，临时变更由当班同事在试点群通知。
```

**仅用改稿要求**（正文逐字保留 0/10 段）

```markdown
# 导出队列试点复盘

## 试点范围

9 月 7 日至 9 月 11 日，我们为 48 个主动报名的工作区开启了新队列。本轮试点只看这些工作区的手动 CSV 导出。定时导出和 API 触发的导出仍走旧队列。支持团队用同一批工作区前一周的数据作对照。两周都按 UTC 记录时间，表里只纳入当周提交且当周结束的任务。

试点开始前，48 个工作区中有 12 个已开启缓存。支持团队只从这 12 个工作区抽取错误日志，下表的任务指标则覆盖全部 48 个工作区。后文讨论的错误类型来自抽样日志，完成率来自符合上述时间口径的全量任务记录。[口径说明](./metrics.md#exports)列出了跨周任务的处理方式。

| 指标 | 前一周 | 试点周 |
| --- | ---: | ---: |
| 手动 CSV 任务数 | 1,240 | 1,310 |
| 完成率 | 96.1% | 97.4% |
| 完成任务的 p95 耗时 | 78 秒 | 71 秒 |

## 为什么暂时不扩大

试点周的完成率上升了 1.3 个百分点。p95 耗时只按已完成的任务计算，超时任务不在统计范围内。试点周我们也缩短了重试间隔，两周的工作负载没有做匹配。目前还不能判断完成率的变化有多少来自新队列。

支持同事逐条查看了 12 个工作区的错误日志，发现可重试的连接中断少了一些。其他工作区是否也有同样的变化，还需要查证。有一条工单写道：“页面显示完成，但导出的文件一直没出现。”这条工单在 9 月 11 日仍未关闭。它反映的是文件交付问题，而表里的完成率只记录任务状态。

支持团队还查了试点周收到的两条定时导出工单。它们描述的现象与前一条相似，但定时导出仍走旧队列，这两条工单也不在本轮日志抽样范围内。支持团队会把它们留在支持队列中另行排查。如果下一轮纳入定时导出，也要先分别记录手动任务和定时任务的结果。

## 值班如何判断要不要重跑

切换队列后，值班同事遇到待处理任务，要先查原任务的状态，再确认它是否写过文件。只有原任务已超时、未写入文件，且两个队列的重试间隔一致，才可以手动重跑。状态未知时，先在值班群报任务 ID，等支持团队核对。用 `queue retry --dry-run` 可以预览，预览不会重跑任务。

如果任务已经写完文件，页面却还在等待，值班同事先通知支持团队查交付记录。重跑仍须满足上面的条件，即使队列有空位或用户催单，也要先核对任务状态。支持团队会把查到的记录贴回原工单，试点组再核对任务记录和文件交付记录。

同一个人有时会在群里和工单里各问一次。支持团队按任务 ID 合并记录，仍在原工单回复。如果两条消息都没有任务 ID，先请用户补充，暂不合并。这个约定只用于记录跟进情况，重跑仍按上面的条件判断。

## 下一轮如何做

下一轮计划沿用同一批工作区，固定重试间隔，并补抽未开启缓存的工作区日志。我们还想请支持和工程同事一起核对任务完成记录和文件交付记录，看看显示“任务完成”的导出里，有多少次用户确实拿到了文件。两项工作还未排期。等日志覆盖和工单核查都完成后，工程组再决定是否把试点扩到定时导出。

试点期间先沿用原来的值班流程。需要临时变更时，由当班同事在试点群通知。
```

**上游 Humanizer**（正文逐字保留 0/10 段）

```markdown
# 导出队列试点复盘

## 试点范围

9 月 7 日至 9 月 11 日，我们为 48 个主动报名的工作区开启了新队列。本轮试点只观察这些工作区的手动 CSV 导出，定时导出和 API 触发的导出仍走旧队列。支持团队用同一批工作区前一周的数据作对照。两周都按 UTC 记录时间，表里只纳入当周提交且当周结束的任务。

试点开始前，有 12 个工作区已经开启缓存。支持团队只从这 12 个工作区抽取错误日志，另外 36 个工作区也计入下表的任务指标。后文讨论的错误类型来自抽样日志，完成率则根据全部 48 个工作区符合统计口径的任务记录计算。[口径说明](./metrics.md#exports)里还列出了跨周任务的处理方式。

| 指标 | 前一周 | 试点周 |
| --- | ---: | ---: |
| 手动 CSV 任务数 | 1,240 | 1,310 |
| 完成率 | 96.1% | 97.4% |
| 完成任务的 p95 耗时 | 78 秒 | 71 秒 |

## 为什么暂时不扩大

完成率上升了 1.3 个百分点。p95 耗时的变化只反映已完成任务的情况，超时任务不计入。试点周我们还缩短了重试间隔，两周的工作负载也没有做匹配。现在还不能判断完成率的变化有多少来自新队列。

支持同事逐条查看了 12 个工作区抽取的错误日志，发现可重试的连接中断少了一些。目前还不知道其他工作区是否有同样的变化。一条工单记录了用户看到的现象：“页面显示完成，但导出的文件一直没出现。”该工单在 9 月 11 日仍未关闭。它对应的是文件交付问题，现有完成率只记录任务状态。

支持团队还查了试点周收到的两个定时导出工单。用户描述的现象与前一条工单相似。定时导出没有走新队列，这两个工单也未纳入本轮日志抽样。不能只凭用户描述相似就把工单算作试点证据。这两个工单会留在支持队列，另行排查。即使下一轮加上定时导出，也要先分别记录手动和定时任务的结果。

## 值班如何判断要不要重跑

队列切换后，值班同事遇到待处理任务，要先查原任务的状态，再确认它是否已经写过文件。只有原任务超时、没有写入文件，而且两个队列的重试间隔一致时，才可以手动重跑。若状态未知，先在值班群报任务 ID，等支持团队核对。用 `queue retry --dry-run` 可以预览，预览不会重跑任务。

如果任务已经写完文件，页面却仍在等待，值班同事先通知支持团队查交付记录。重跑条件仍然适用。即使队列有空位或用户来催，也要先查状态。支持团队会把查到的记录贴回原工单，试点组再据此核对任务记录和文件交付记录。

有时候同一个人会在群里和工单里各问一次。支持团队按任务 ID 合并记录，仍在原工单回复。若两条消息都没有提供任务 ID，先请用户补充，值班同事暂时不合并。这个约定只用于记录跟进情况，与任务能否重跑无关。

## 下一轮如何做

下一轮计划沿用同一批工作区，保持重试间隔固定，再补抽未开启缓存的工作区日志。我们还想让支持和工程一起对照任务完成记录与文件交付记录，看看“任务完成”能覆盖多少用户真正拿到文件的情况。两项工作还未排期。等日志覆盖和工单核查都完成后，工程组再决定是否把试点扩到定时导出。

试点期间先维持原来的值班流程，临时变更由当班同事在试点群通知。
```

**上一版**（正文逐字保留 1/10 段）

```markdown
# 导出队列试点复盘

## 试点范围

9 月 7 日至 9 月 11 日，我们为 48 个主动报名的工作区开启了新队列。本轮只观察这些工作区里的手动 CSV 导出，定时导出和 API 触发的导出仍走旧队列。支持团队用同一批工作区前一周的数据作对照。两周都按 UTC 记录时间，表里只纳入当周提交且当周结束的任务。

这 48 个工作区里，有 12 个在试点开始前已经开启缓存。支持团队只从这 12 个工作区抽取错误日志，其余 36 个工作区的任务仍计入下表的指标。后文对错误类型的讨论基于抽样日志，完成率则来自两周纳入统计的全部任务记录。[口径说明](./metrics.md#exports)里还列出了跨周任务的处理方式。

| 指标 | 前一周 | 试点周 |
| --- | ---: | ---: |
| 手动 CSV 任务数 | 1,240 | 1,310 |
| 完成率 | 96.1% | 97.4% |
| 完成任务的 p95 耗时 | 78 秒 | 71 秒 |

## 为什么暂时不扩大

完成率上升了 1.3 个百分点。p95 只统计已完成任务，超时任务不在分母内，因此耗时的变化只反映已完成任务的情况。试点周我们还缩短了重试间隔，两周的工作负载也没有做匹配。现在还不能判断完成率的变化有多少来自新队列。

支持同事逐条查看了从这 12 个工作区抽取的错误日志，发现可重试的连接中断少了一些。其他工作区的日志没有抽样，还不知道是否出现了同样的变化。有一条工单写道：“页面显示完成，但导出的文件一直没出现。”该工单在 9 月 11 日仍未关闭。它涉及文件交付，现有完成率只按任务状态统计。

支持团队还查了两个在试点周收到的定时导出工单。它们和前面那条工单的现象相似，但定时导出没有走新队列，两个工单也没有纳入这轮日志抽样。工单会保留在支持队列，另行排查。即使下一轮加上定时导出，也要先分别记录手动和定时任务的结果。

## 值班如何判断要不要重跑

新旧队列切换后，如果待处理任务的状态可能不一致，值班同事要先查原任务状态，再确认原任务是否已经写过文件。只有原任务超时、没有写入文件，且两个队列的重试间隔一致时，才可以手动重跑。若状态为未知，先在值班群报任务 ID，等支持团队核对。可用 `queue retry --dry-run` 预览重跑操作。预览不会重跑任务。

任务已经写完文件但页面仍在等待时，值班同事先通知支持团队查交付记录。上面的重跑条件仍然适用。队列有空位或用户催单，都不能替代状态检查。支持团队会把查到的记录贴回原工单，试点组再据此核对任务记录和文件交付记录。

有时候同一个人会在群里和工单里各问一次。支持团队按任务 ID 合并记录，仍在原工单回复。若两条消息没有提供任务 ID，先请用户补充，值班同事暂时不合并。这个约定只用于记录跟进情况，与任务能否重跑无关。

## 下一轮如何做

下一轮计划沿用同一批工作区，保持重试间隔固定，并从未开启缓存的工作区补抽日志。我们还想让支持和工程一起对照任务完成记录与文件交付记录，看看“任务完成”能覆盖多少用户真正拿到文件的情况。两项工作还未排期。等补抽日志和工单核查都完成后，工程组再决定是否把试点扩到定时导出。

试点期间先维持原来的值班流程，临时变更由当班同事在试点群通知。
```

**微调初稿**（正文逐字保留 0/10 段）

```markdown
# 导出队列试点复盘

## 试点范围

9 月 7 日至 9 月 11 日，我们为 48 个主动报名的工作区启用了新队列。本轮只观察这些工作区里的手动 CSV 导出。定时导出和 API 触发的导出仍走旧队列。支持团队用同一批工作区前一周的数据作对照。两周都使用 UTC 记录时间，表里只纳入当周提交且当周结束的任务。

试点开始前，这 48 个工作区中已有 12 个开启缓存。支持团队只从这 12 个工作区抽取错误日志。其余 36 个工作区仍计入下表的任务指标。后文对错误类型的讨论依据抽样日志，完成率则来自全量任务记录。[口径说明](./metrics.md#exports)里还列出了跨周任务的处理方式。

| 指标 | 前一周 | 试点周 |
| --- | ---: | ---: |
| 手动 CSV 任务数 | 1,240 | 1,310 |
| 完成率 | 96.1% | 97.4% |
| 完成任务的 p95 耗时 | 78 秒 | 71 秒 |

## 为什么暂时不扩大

完成率上升了 1.3 个百分点。p95 耗时只统计已完成任务，超时任务不计入。试点周我们还缩短了重试间隔，两周的工作负载也没有做匹配。现在还不能判断完成率的变化有多少来自新队列。

支持同事逐条查看了这 12 个工作区的错误日志，发现可重试的连接中断少了一些。其他工作区是否也有同样的变化，目前还不知道。有一条工单这样描述用户看到的情况：“页面显示完成，但导出的文件一直没出现。”9 月 11 日，这条工单仍未关闭。它涉及文件交付，现有完成率是按任务状态算的。

支持团队还查了试点周收到的两个定时导出工单。用户描述的现象和前面那条工单相似，但定时导出仍走旧队列，这两个工单也没有纳入本轮日志抽样。工单会保留在支持队列，另行排查。即使下一轮加上定时导出，也要先分别记录手动和定时任务的结果。

## 值班如何判断要不要重跑

新旧队列切换后，遇到待处理任务状态存疑的情况，值班同事先查原任务状态，再确认原任务是否已写过文件。只有原任务超时、没有写入文件，且两个队列的重试间隔一致时，才可以手动重跑。若状态为未知，先在值班群报任务 ID，等支持团队核对。可以用 `queue retry --dry-run` 预览，预览不会重跑任务。

任务已经写完文件但页面仍在等待时，值班同事先通知支持团队查交付记录。上面的重跑条件仍然适用。即使队列有空位或用户催单，也要先查任务状态。支持团队会把查到的记录贴回原工单，试点组再对照任务记录和文件交付记录。

有时同一个人会在群里和工单里各问一次。支持团队按任务 ID 合并记录，仍在原工单回复。如果两条消息都没提供任务 ID，先请用户补充，值班同事暂时不合并。这个约定只用于跟进记录，与任务能否重跑无关。

## 下一轮如何做

下一轮计划沿用同一批工作区，固定重试间隔，并补抽未开启缓存的工作区日志。我们还想让支持和工程一起对照任务完成记录与文件交付记录，看看记录里的“任务完成”在多大程度上能反映用户实际拿到文件的情况。两项工作还未排期。等补抽日志和核查工单的工作都完成后，工程组再决定是否把试点扩到定时导出。

试点期间先维持原来的值班流程，临时变更由当班同事在试点群通知。
```

**盲评依据**

- 四稿都保留了标题、段落、表格、链接、工单引文和命令，也保留了缩短重试间隔、负载未匹配、工单仍未关闭、两项工作未排期等信息。上游 Humanizer 把“全量任务记录”具体写成“全部 48 个工作区符合统计口径的任务记录”，还明确说明了为什么不能把描述相似的工单算作试点证据。它保留了“日志覆盖和工单核查都完成后”的决策条件。值班段的“遇到待处理任务”字面适用范围比原文的状态一致性问题略宽，三项重跑条件及状态未知时的处理路径都完整。
- 微调初稿 用“在多大程度上能反映用户实际拿到文件的情况”讲清了计划核查的关系，语气也保持审慎。微调初稿 和 上一版 都把“日志覆盖”写成完成“补抽日志”的动作，覆盖到位这一层在决策条件里变得不够明确。
- 上一版 用“如果待处理任务的状态可能不一致”保留了值班检查的触发情形。p95 一段在句首和句尾各说一次只反映已完成任务，还保留了原稿容易让人停下来琢磨的“分母”，读起来比 微调初稿 多绕一步。
- 仅用改稿要求 的“有多少次用户确实拿到了文件”把记录间的核查收窄为在显示“任务完成”的导出中计数。原文对如何衡量二者的关系留有余地。仅用改稿要求 把“值班同事暂时不合并”缩成“暂不合并”，承接前一句时容易读成仍由支持团队处理。

### 中文随笔

**改稿要求**

这篇稿子要发在个人公众号。帮我去掉后加的 AI 腔，保留原来的说话习惯、引号里的原话、时间顺序和有意留白。可以轻改不顺的地方，保留标题和主体段落。只给正文。

**原稿**

```markdown
# 我妈的旧收音机

周六回去，吃过午饭我去厨房洗碗。我妈把收音机从窗台上拿下来，问我会不会修。灰落得很厚，放收音机的那块窗台倒是白的。她拿手指指了指开关，说：“有时候响，有时候要等一下。”我说我看看。她把我手里的碗接了过去。

这个看似平凡的家庭片段，实际上折射出了当代生活中跨代际沟通的深层命题。那台收音机是我上初中那会儿她买的，白壳子，提手有一道裂纹。我以前写作业嫌它响，让她关一点，她就搬去厨房听。厨房门关上，隔着一层玻璃，还是能听到主持人笑。她也笑。我那时只觉得吵。

我拿纸巾擦了半天。插上电，转过新闻台和两个卖药的台，喇叭一直有沙沙声，偶尔冒出来一句话。她站在旁边等我。我说可能是开关接触不良，也可能是里面的线有问题，手头没有工具。她说：“那你下回带来。”话说完，她就去阳台收衣服了。

值得注意的是，围绕这次维修需求，我们并没有马上展开更深层次的情感交流。我把收音机放回窗台，发现它底下原来垫了两张折过的车票，是同一天来回的票，一张写着到东站，一张写着从东站出发。票上是二〇一七年四月。我不记得那天她去了哪儿，也没问。

她收完衣服，进屋问我要不要带点橘子。我说家里还有。她挑了两个放桌上，说：“那就路上吃。”我把它们塞进外套口袋。一个偏硬，一个已经有点软。我到楼下吃了软的那个，剥开的皮一直攥着，出了小区才碰到垃圾桶。

小区门口从前有个修鞋的摊子，我记得他也修拉链。那天走出去才想起这回事，又折回来找了一圈。原来摆摊的地方停着几辆共享单车。我去隔壁配钥匙的店问，店里的人说修鞋的人去年冬天就没来了，去哪儿不知道。我买了个钥匙圈，两块钱。回去坐车的时候，我把家里那把钥匙换了上去。

我弟晚上发消息，问我有没有把收音机带走。他前一周也回去过，说我妈跟他提过一次。他问要不要在网上买一台新的。我说先别买，我下次带工具。聊到这里他就去忙了，过一会儿才又发了一句：“她以前收天气预报都用这个。”我说我记得，发出去才想起来我记得的是她听戏，天气预报是什么时候听的我其实不知道。

我找了两张家里以前的照片。第一张是我爸换厨房灯管，我妈站在凳子下面给他递东西，窗台只拍到一半。第二张是过年吃饭，收音机在桌子一角，旁边压着一包还没拆的瓜子。照片是我弟拍的，他把四个人都拍进去了，谁也没看镜头。我本来想问他是哪一年，后来没发。

隔了两天，她打电话，说那天我走了以后收音机又响过一阵。她听见有人说夜里要降温，后来声音自己断了。她问我有没有把外套扣子扣好。我当时站在公交站上，天已经黑了。电话里有锅盖碰到灶台的声音。我等了一下，听见她喊我爸去看火。

因此，这台收音机不仅是一件承载家庭记忆的旧物，更是一座连接过去与现在的桥梁，提醒我们在忙碌生活中重新发现那些无声却深刻的牵挂。挂电话之后我把手插进外套口袋，摸到了另一个橘子。它已经有点软了。
```

**仅用改稿要求**（正文逐字保留 6/10 段）

```markdown
# 我妈的旧收音机

周六回去，吃过午饭我去厨房洗碗。我妈把收音机从窗台上拿下来，问我会不会修。灰落得很厚，放收音机的那块窗台倒是白的。她指了指开关，说：“有时候响，有时候要等一下。”我说我看看。她把我手里的碗接了过去。

那台收音机是我上初中那会儿她买的，白壳子，提手有一道裂纹。我以前写作业嫌它响，让她关一点，她就搬去厨房听。厨房门关上，隔着一层玻璃，还是能听到主持人笑。她也笑。我那时只觉得吵。

我拿纸巾擦了半天。插上电，转过新闻台和两个卖药的台，喇叭一直有沙沙声，偶尔冒出来一句话。她站在旁边等我。我说可能是开关接触不良，也可能是里面的线有问题，手头没有工具。她说：“那你下回带来。”话说完，她就去阳台收衣服了。

我把收音机放回窗台，发现它底下原来垫了两张折过的车票，是同一天来回的票，一张写着到东站，一张写着从东站出发。票上是二〇一七年四月。我不记得那天她去了哪儿，也没问。

她收完衣服，进屋问我要不要带点橘子。我说家里还有。她挑了两个放桌上，说：“那就路上吃。”我把它们塞进外套口袋。一个偏硬，一个已经有点软。我到楼下吃了软的那个，剥开的皮一直攥着，出了小区才碰到垃圾桶。

小区门口从前有个修鞋的摊子，我记得他也修拉链。那天走出去才想起这回事，又折回来找了一圈。原来摆摊的地方停着几辆共享单车。我去隔壁配钥匙的店问，店里的人说修鞋的人去年冬天就没来了，去哪儿不知道。我买了个钥匙圈，两块钱。回去坐车的时候，我把家里那把钥匙换了上去。

我弟晚上发消息，问我有没有把收音机带走。他前一周也回去过，说我妈跟他提过一次。他问要不要在网上买一台新的。我说先别买，我下次带工具。聊到这里他就去忙了，过一会儿才又发了一句：“她以前收天气预报都用这个。”我说我记得，发出去才想起来我记得的是她听戏，天气预报是什么时候听的我其实不知道。

我找了两张家里以前的照片。第一张是我爸换厨房灯管，我妈站在凳子下面给他递东西，窗台只拍到一半。第二张是过年吃饭，收音机在桌子一角，旁边压着一包还没拆的瓜子。照片是我弟拍的，他把四个人都拍进去了，谁也没看镜头。我本来想问他是哪一年，后来没发。

隔了两天，她打电话，说那天我走了以后收音机又响过一阵。她听见有人说夜里要降温，后来声音自己断了。她问我有没有把外套扣子扣好。我当时站在公交站上，天已经黑了。电话里有锅盖碰到灶台的声音。我等了一下，听见她喊我爸去看火。

挂电话之后我把手插进外套口袋，摸到了另一个橘子。它已经有点软了。
```

**上游 Humanizer**（正文逐字保留 6/10 段）

```markdown
# 我妈的旧收音机

周六回去，吃过午饭我去厨房洗碗。我妈把收音机从窗台上拿下来，问我会不会修。灰落得很厚，放收音机的那块窗台倒是白的。她拿手指指了指开关，说：“有时候响，有时候要等一下。”我说我看看。她把我手里的碗接了过去。

那台收音机是我上初中那会儿她买的，白壳子，提手有一道裂纹。我以前写作业嫌它响，让她关一点，她就搬去厨房听。厨房门关上，隔着一层玻璃，还是能听到主持人笑。她也笑。我那时只觉得吵。

我拿纸巾擦了半天。插上电，转过新闻台和两个卖药的台，喇叭一直有沙沙声，偶尔冒出来一句话。她站在旁边等我。我说可能是开关接触不良，也可能是里面的线有问题，手头没有工具。她说：“那你下回带来。”话说完，她就去阳台收衣服了。

我把收音机放回窗台，发现它底下原来垫了两张折过的车票，是同一天来回的票，一张写着到东站，一张写着从东站出发。票上是二〇一七年四月。我不记得那天她去了哪儿，也没问。

她收完衣服，进屋问我要不要带点橘子。我说家里还有。她挑了两个放桌上，说：“那就路上吃。”我把它们塞进外套口袋。一个偏硬，一个已经有点软。我到楼下吃了软的那个，剥开的皮一直攥着，出了小区才碰到垃圾桶。

小区门口从前有个修鞋的摊子，我记得他也修拉链。那天走出去才想起这回事，又折回来找了一圈。原来摆摊的地方停着几辆共享单车。我去隔壁配钥匙的店问，店里的人说修鞋的人去年冬天就没来了，去哪儿不知道。我买了个钥匙圈，两块钱。回去坐车的时候，我把家里那把钥匙换了上去。

我弟晚上发消息，问我有没有把收音机带走。他前一周也回去过，说我妈跟他提过一次。他问要不要在网上买一台新的。我说先别买，我下次带工具。聊到这里他就去忙了，过一会儿才又发了一句：“她以前收天气预报都用这个。”我说我记得，发出去才想起来我记得的是她听戏，天气预报是什么时候听的，我其实不知道。

我找了两张家里以前的照片。第一张是我爸换厨房灯管，我妈站在凳子下面给他递东西，窗台只拍到一半。第二张是过年吃饭，收音机在桌子一角，旁边压着一包还没拆的瓜子。照片是我弟拍的，他把四个人都拍进去了，谁也没看镜头。我本来想问他是哪一年，后来没发。

隔了两天，她打电话，说那天我走了以后收音机又响过一阵。她听见有人说夜里要降温，后来声音自己断了。她问我有没有把外套扣子扣好。我当时站在公交站上，天已经黑了。电话里有锅盖碰到灶台的声音。我等了一下，听见她喊我爸去看火。

挂电话之后我把手插进外套口袋，摸到了另一个橘子。它已经有点软了。
```

**上一版**（正文逐字保留 7/10 段）

```markdown
# 我妈的旧收音机

周六回去，吃过午饭我去厨房洗碗。我妈把收音机从窗台上拿下来，问我会不会修。灰落得很厚，放收音机的那块窗台倒是白的。她拿手指指了指开关，说：“有时候响，有时候要等一下。”我说我看看。她把我手里的碗接了过去。

那台收音机是我上初中那会儿她买的，白壳子，提手有一道裂纹。我以前写作业嫌它响，让她关一点，她就搬去厨房听。厨房门关上，隔着一层玻璃，还是能听到主持人笑。她也笑。我那时只觉得吵。

我拿纸巾擦了半天。插上电，转过新闻台和两个卖药的台，喇叭一直有沙沙声，偶尔冒出来一句话。她站在旁边等我。我说可能是开关接触不良，也可能是里面的线有问题，手头没有工具。她说：“那你下回带来。”话说完，她就去阳台收衣服了。

我把收音机放回窗台，发现它底下原来垫了两张折过的车票，是同一天来回的票，一张写着到东站，一张写着从东站出发。票上是二〇一七年四月。我不记得那天她去了哪儿，也没问。

她收完衣服，进屋问我要不要带点橘子。我说家里还有。她挑了两个放桌上，说：“那就路上吃。”我把它们塞进外套口袋。一个偏硬，一个已经有点软。我到楼下吃了软的那个，剥开的皮一直攥着，出了小区才碰到垃圾桶。

小区门口从前有个修鞋的摊子，我记得他也修拉链。那天走出去才想起这回事，又折回来找了一圈。原来摆摊的地方停着几辆共享单车。我去隔壁配钥匙的店问，店里的人说修鞋的人去年冬天就没来了，去哪儿不知道。我买了个钥匙圈，两块钱。回去坐车的时候，我把家里那把钥匙换了上去。

我弟晚上发消息，问我有没有把收音机带走。他前一周也回去过，说我妈跟他提过一次。他问要不要在网上买一台新的。我说先别买，我下次带工具。聊到这里他就去忙了，过一会儿才又发了一句：“她以前收天气预报都用这个。”我说我记得，发出去才想起来我记得的是她听戏，天气预报是什么时候听的我其实不知道。

我找了两张家里以前的照片。第一张是我爸换厨房灯管，我妈站在凳子下面给他递东西，窗台只拍到一半。第二张是过年吃饭，收音机在桌子一角，旁边压着一包还没拆的瓜子。照片是我弟拍的，他把四个人都拍进去了，谁也没看镜头。我本来想问他是哪一年，后来没发。

隔了两天，她打电话，说那天我走了以后收音机又响过一阵。她听见有人说夜里要降温，后来声音自己断了。她问我有没有把外套扣子扣好。我当时站在公交站上，天已经黑了。电话里有锅盖碰到灶台的声音。我等了一下，听见她喊我爸去看火。

挂电话之后我把手插进外套口袋，摸到了另一个橘子。它已经有点软了。
```

**微调初稿**（正文逐字保留 5/10 段）

```markdown
# 我妈的旧收音机

周六回去，吃过午饭，我去厨房洗碗。我妈把收音机从窗台上拿下来，问我会不会修。灰落得很厚，放收音机的那块窗台倒是白的。她指了指开关，说：“有时候响，有时候要等一下。”我说我看看。她把我手里的碗接了过去。

那台收音机是我上初中那会儿她买的，白壳子，提手有一道裂纹。我以前写作业嫌它响，让她关一点，她就搬去厨房听。厨房门关上，隔着一层玻璃，还是能听到主持人笑。她也笑。我那时只觉得吵。

我拿纸巾擦了半天。插上电，转过新闻台和两个卖药的台，喇叭一直有沙沙声，偶尔冒出来一句话。她站在旁边等我。我说可能是开关接触不良，也可能是里面的线有问题，手头没有工具。她说：“那你下回带来。”话说完，她就去阳台收衣服了。

我把收音机放回窗台，发现它底下原来垫了两张折过的车票，是同一天来回的票，一张写着到东站，一张写着从东站出发。票上是二〇一七年四月。我不记得那天她去了哪儿，也没问。

她收完衣服，进屋问我要不要带点橘子。我说家里还有。她挑了两个放桌上，说：“那就路上吃。”我把它们塞进外套口袋。一个偏硬，一个已经有点软。我到楼下吃了软的那个，剥开的皮一直攥着，出了小区才碰到垃圾桶。

小区门口从前有个修鞋的摊子，我记得他也修拉链。那天走出去才想起这回事，又折回来找了一圈。原来摆摊的地方停着几辆共享单车。我去隔壁配钥匙的店问，店里的人说修鞋的人去年冬天就没来了，去哪儿不知道。我买了个钥匙圈，两块钱。回去坐车的时候，我把家里那把钥匙换了上去。

我弟晚上发消息，问我有没有把收音机带走。他前一周也回去过，说我妈跟他提过一次。他问要不要在网上买一台新的。我说先别买，我下次带工具。聊到这里他就去忙了，过一会儿才又发了一句：“她以前收天气预报都用这个。”我说我记得，发出去才想起来，我记得的是她听戏。天气预报是什么时候听的，我其实不知道。

我找了两张家里以前的照片。第一张是我爸换厨房灯管，我妈站在凳子下面给他递东西，窗台只拍到一半。第二张是过年吃饭，收音机在桌子一角，旁边压着一包还没拆的瓜子。照片是我弟拍的，他把四个人都拍进去了，谁也没看镜头。我本来想问他是哪一年，后来没发。

隔了两天，她打电话，说那天我走了以后收音机又响过一阵。她听见有人说夜里要降温，后来声音自己断了。她问我有没有把外套扣子扣好。我当时站在公交站上，天已经黑了。电话里有锅盖碰到灶台的声音。我等了一下，听见她喊我爸去看火。

挂电话之后我把手插进外套口袋，摸到了另一个橘子。它已经有点软了。
```

**盲评依据**

- 四稿都删掉了三处替读者解释故事的套话，保留了标题、主体段落、四处引语和叙事顺序。“我不记得那天她去了哪儿，也没问”与“我本来想问他是哪一年，后来没发”都保留了原有的留白。橘子从装进口袋到在公交站摸到另一个，首尾仍接得上。
- 上一版 完整保留了删去套话后的句子。上游 Humanizer 只在“天气预报是什么时候听的，我其实不知道”里加了一处停顿，读起来稍清楚，也接得上前面的“发出去才想起来我记得的是她听戏”。两种节奏都符合原稿。
- 仅用改稿要求 把“她拿手指指了指开关”收成“她指了指开关”，意思完整，少了一点作者的口头语感。微调初稿 也做了这处改动，还把“我记得的是她听戏。天气预报是什么时候听的，我其实不知道”断成两句，原本一口气说完的自我纠正变得更整齐。两处都只是节奏和语气上的差别。

### 英文技术复盘

**改稿要求**

Lightly edit this rollout memo for engineers and support leads who will decide whether to expand the pilot. Remove canned phrasing and repair hard-to-read sentences. Keep the headings, Markdown table, quotation, link target, inline command, chronology, and evidence boundaries. Return only the finished memo.

**原稿**

```markdown
# Export queue pilot

## What the pilot covered

To move the needle on our end-to-end export experience, the release team enabled the new queue for 42 workspaces that had volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both sets of figures use UTC and count only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from the table, including from the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs only from those 9 workspaces, while the figures below cover all 42. This distinction is a key thing to note moving forward as we assess the data. The logs provide examples of what went wrong. The table describes how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue. These numbers are a promising step on a broader journey of continuous improvement.

The failure pattern the support engineer the incident lead assigned to the Saturday shift flagged in the sampled logs involved a timeout after the job had written a file. The same engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The support lead said the ticket review the pilot group requested would cover delivery failures as well as job failures. The lead did not say when the review would start. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

In addition, the pilot group received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. They describe the same job, so Support will keep one record for the review and link the other two reports from that record. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The counts in the table are job counts from the queue and do not depend on whether a customer contacted us.

## When to rerun a job

For the purpose of facilitating a clear operational response, the on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record says the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket. That gives the pilot group a way to compare the file record with what the customer could actually see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message is a request to review the job. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.
```

**仅用改稿要求**（正文逐字保留 0/10 段）

```markdown
# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week covers the same 42 workspaces. We used UTC for both weeks and counted only jobs that started and ended in the same reporting week. The job counts and all other figures in the table exclude jobs still open at the end of their reporting week.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support sampled error logs only from those 9 workspaces. The logs provide examples of what went wrong there. The table covers all 42 workspaces and shows how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for how we handled jobs that crossed the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, that engineer flagged a failure pattern involving a timeout after a job had written a file. The engineer also marked a ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when we drafted this memo. A completed job can still have a file delivery problem. The table measures job completion only.

The pilot group requested a ticket review. The support lead said it would cover both file delivery failures and job failures, with no start date given. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. The review cannot tell us how common the problem is in API exports.

The pilot group received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for the review and link the other two reports from it. A report with no job ID stays separate until Support can identify the job. Support has yet to match all of these reports to the file records. The table counts jobs from the queue regardless of whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview the rerun. The preview does not rerun the job.

If the file record shows the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. Apply the same rerun rule even if a customer asks again or a slot opens in the queue. Support should add the delivery record to the original ticket so the pilot group can compare the file record with what the customer could see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message requests a job review. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should continue the review and apply the same checks.

## Before the next decision

The team proposes using the same workspaces and keeping the retry interval fixed in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports once the additional log sampling and the ticket review are complete. Until then, follow the current on-call procedure. The shift engineer will post any temporary exception in the pilot channel.
```

**上游 Humanizer**（正文逐字保留 1/10 段）

```markdown
# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that had volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both weeks use UTC. The table counts only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from every row, including the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs from those 9 workspaces only, so the examples of failures come from that group. The table covers all 42 workspaces and shows how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, the engineer flagged a timeout that occurred after the job had written a file. The same engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The support lead said the ticket review requested by the pilot group would cover delivery failures as well as job failures. The lead did not say when the review would start. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

The pilot group also received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for the review and link the other two reports from it. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The table counts jobs from the queue regardless of whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record shows that the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket so the pilot group can compare the file record with what the customer could actually see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message requests a review and gives no authorisation to rerun the job. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.
```

**上一版**（正文逐字保留 1/10 段）

```markdown
# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that had volunteered for the pilot, which ran from 7 to 11 September. The pilot covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both sets of figures use UTC and count only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from the table, including from the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs only from those 9 workspaces, while the figures below cover all 42. The logs provide examples of what went wrong. The table describes how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration fell among completed jobs, the only jobs included in that calculation. The platform team also shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, that engineer flagged a failure pattern involving a timeout after a job had written a file. The engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The pilot group requested a ticket review. The support lead said it would cover delivery failures as well as job failures, but gave no start date. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

The pilot group also received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for that job in the review and link the other two reports from it. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The table's job counts come from the queue and do not depend on whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job's status and file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record says the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket so the pilot group can compare the file record with what the customer could actually see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message is a request to review the job. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and using a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.
```

**微调初稿**（正文逐字保留 2/10 段）

```markdown
# Export queue pilot

## What the pilot covered

The release team enabled the new queue for 42 workspaces that had volunteered for the pilot. The pilot ran from 7 to 11 September and covered only manual CSV exports. Scheduled exports and exports triggered through the API stayed on the old queue. The comparison week used the same 42 workspaces. Both sets of figures use UTC and count only jobs that started and ended in the same reporting week. Jobs still open at the end of either week are excluded from the table, including from the job counts.

Before the pilot began, 9 of the 42 workspaces had caching enabled. Support read error logs only from those 9 workspaces. The logs provide examples of what went wrong. The table covers all 42 workspaces and shows how often jobs in the reporting window completed. See the [measurement notes](./metrics.md#queue-pilot) for the handling of jobs that cross the week boundary.

| Metric | Comparison week | Pilot week |
| --- | ---: | ---: |
| Manual CSV jobs | 1,120 | 1,180 |
| Completion rate | 95.8% | 97.0% |
| p95 duration for completed jobs | 83 seconds | 74 seconds |

## What we can conclude

The completion rate rose by 1.2 percentage points. The p95 duration, calculated only for completed jobs, also fell. The platform team shortened the retry interval during the pilot, and we did not match workloads across the two weeks. We do not know how much of the change in completion rate came from the new queue.

The incident lead assigned a support engineer to the Saturday shift. In the sampled logs, that engineer flagged a pattern of jobs timing out after writing a file. The same engineer marked one ticket for follow-up. In it, a customer wrote, “The page says done, but the file never showed up.” The ticket was still open when the memo was drafted. A completed job can still have a file delivery problem. The table tracks job completion and does not measure whether a customer received the file.

The support lead said that the ticket review requested by the pilot group would cover delivery failures as well as job failures. The lead did not say when the review would start. Two other tickets were set aside because the exports had been triggered through the API. Those tickets may be worth looking at separately. Their exclusion from this review says nothing about how common the problem is in API exports.

The pilot group received three reports from the same person about a single job ID. The reports arrived in two channels and one ticket. Support will keep one record for the review and link the other two reports from that record. A report with no job ID stays separate until Support can identify the job. Support has not yet matched all of these reports to the file records. The counts in the table are job counts from the queue and do not depend on whether a customer contacted us.

## When to rerun a job

The on-call engineer should check the original job status and its file record. Rerun a job only if it timed out, wrote no file, and has the same retry interval in both queues. If the status is unknown, post the job ID in the support channel and wait for Support to check it. Use `queue retry --dry-run` to preview a rerun. The preview does not rerun the job.

If the file record says the job already wrote a file, ask Support to check delivery. Leave the job alone while Support checks. A customer asking again or a free slot in the queue does not change the rerun rule. Support should put the delivery record in the original ticket. The pilot group can then compare the file record with what the customer could see.

When Support confirms a missing file, it records what it found in the original ticket and tells the on-call engineer. That message is a request to review the job. It does not authorise a rerun. If a second shift takes over before the review is complete, the departing engineer posts the job ID and the last confirmed status in the support channel. The new shift should pick up the same review and apply the same checks.

## Before the next decision

The team proposes keeping the same workspaces and a fixed retry interval in the next round. Support also plans to sample logs from workspaces with caching disabled. Neither work item has been scheduled. The release lead will decide whether to include scheduled exports after both the additional log sampling and the ticket review are complete. Until then, the current on-call procedure stays in place. The shift engineer will post any temporary exception in the pilot channel.
```

**盲评依据**

- 上一版 把原文层层嵌套的 “the support engineer the incident lead assigned” 拆成两句，同时保留 “flagged a failure pattern involving a timeout”。它也单独交代试点组提出工单复核，随后才写支持主管说明复核范围和未给开始日期，人员分工和先后关系都清楚。
- 微调初稿 的 “The p95 duration, calculated only for completed jobs, also fell” 把计算范围自然放进句子。它把日志发现写成 “a pattern of jobs timing out”，比原文更明确地暗示有多项作业发生超时，原文没有交代观察到多少项。上游 Humanizer 的 “flagged a timeout” 则缩成了一次超时，丢掉了识别出故障模式这一层。
- 仅用改稿要求 保住了 “a failure pattern”，但 “The table measures job completion only” 字面上容易掩盖表里还有作业数和已完成作业的 p95 用时。上游 Humanizer 明确写出表格不衡量客户是否收到文件，在这处更严谨。四版的表格、引文、链接和命令一致，也都保留了重跑的三个必要条件、状态未知时的处理以及扩大范围前须完成的两项工作。

### 英文随笔

**改稿要求**

Edit this personal essay for a small community newsletter. Remove the bits that sound pasted in from a generic essay. Make a light edit where a sentence is hard to follow. Keep the title, paragraph structure, British spelling, quotations, chronology, and the narrator's dry voice. Return only the essay.

**原稿**

```markdown
# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

In an age of increasingly impersonal transactions, the neighbourhood repair shop had long served as a vital hub of authentic human connection. Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The parcel the woman the café owner used to send over on Wednesdays left by the till was still there. It had my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

The transition from active service to a state of closure was, in many ways, an exercise in navigating the emotional complexities of change. It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

Ultimately, the closing of the shop was not simply the end of a business, but a testament to the enduring power of ordinary places to shape our lives in extraordinary ways. I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.
```

**仅用改稿要求**（正文逐字保留 6/10 段）

```markdown
# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The woman the café owner used to send over on Wednesdays had left a parcel by the till. It was still there, with my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.
```

**上游 Humanizer**（正文逐字保留 6/10 段）

```markdown
# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The parcel was still by the till. The woman who'd left it there used to come over on Wednesdays, sent by the café owner. It had my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.
```

**上一版**（正文逐字保留 6/10 段）

```markdown
# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The woman the café owner used to send over on Wednesdays had left a parcel by the till. It was still there, with my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.
```

**微调初稿**（正文逐字保留 6/10 段）

```markdown
# The last Saturday at the shop

The bell still rang when I opened the door. It always had a little delay, just long enough for me to think the spring had finally gone. I stood there with my hand on the door and heard it go twice. The shop had closed to customers the previous evening. I had come back for a screwdriver I had left in the drawer behind the till.

Most of what I remember about it is small. There was a biscuit tin full of screws that didn't match anything. The stool by the counter was too tall for most children and too low for anyone trying to see the clock. Colin used to keep a second clock under the counter. He said the first one was for customers.

I had worked there two Saturdays a month since the autumn I left school. Some people still assumed that Colin was my uncle. He had corrected that once, in my hearing, then apparently decided it wasn't worth the effort. He was at the back of the shop that morning, on his knees, counting the sockets in a cardboard box. He said, “There's tea, if the milk's all right.” I took that as permission to smell it.

The parcel was still by the till. The woman who'd left it was the one the café owner used to send over on Wednesdays. It had my name on it in pencil. I asked Colin if he knew what it was. He said he thought it might be a jumper, but he hadn't opened it. The string was wet at one end. I put the parcel on the stool while I cleared the drawer.

When I pulled the drawer all the way out, a folded order form fell behind the till. I could see the corner of it through the gap. Colin said to leave it, then got up and fetched the long kitchen tongs. He held the drawer and I reached in. The paper was blank apart from somebody's shopping list on the back. We put it with the receipts anyway. There was a pile of them under the tin and I thought one more couldn't hurt.

It took about an hour to sort the drawer. There were three pencils, a ruler with the first inch missing, and a wallet Colin had put there after someone dropped it in January. He still had the phone number for the owner on the back of a receipt. He asked if I could ring it once more. I did. It went to voicemail. I left the same message I had left in January.

By midday the owner of the café came in for the spare key. She had brought a paper bag with two buns in it. She gave one to Colin and one to me. Neither of us had asked, which I think was the point. We ate at the counter. From there you could see the space on the wall where the little clock had been. I asked where it was. Colin said he hadn't decided who was having it yet. Then he said, “You can have the other one.” I didn't ask which one he meant.

I left before Colin did. He was trying the spare key in the back door, though there was no reason for it to have stopped working. I got as far as the crossing before I remembered the screwdriver. By the time I turned round, the shop light was off. I could have knocked on the window. I went on to the bus stop instead. When the bus arrived I put the parcel on my knees and kept my hands on it the whole way home.

I opened the parcel when I got home. It was a jumper, the one I'd left there in March after the heating came back on. The woman had washed it. I knew because it smelt of a kind of soap I hadn't used since I was a child. I looked in the pockets. One had a bus ticket in it, the ink almost gone. I put the ticket on the kitchen sill, where it stayed for most of that winter.

I saw Colin on the bus the following Thursday. He looked down at the jumper and asked if it was new. I said no. He nodded. The stop after mine, he rang the bell.
```

**盲评依据**

- 四版都删去了 “In an age of increasingly impersonal transactions”、关店时的抽象过渡和结尾的 “Ultimately” 议论。段落、英式用词和引语均保留。开头门铃和结尾公交车铃仍彼此呼应，“I didn't ask which one he meant” 也留住了时钟的悬念。
- 微调初稿 用 “The parcel was still by the till” 先写叙述者看到的东西，再说清谁留下包裹。上一版 和 仅用改稿要求 正文完全相同，用 “The woman the café owner used to send over on Wednesdays had left a parcel by the till” 先交代人物关系，再用 “It was still there” 接回眼前。两种安排都拆开了原文的多层嵌套，保住了动作归属和时间线。
- 上游 Humanizer 同样保留了人物关系，但 “used to come over on Wednesdays, sent by the café owner” 把谁派她来的信息放成句末补语，读起来略像补注，与叙述者平直的语气稍有距离。这个差别只涉及句子节奏。
