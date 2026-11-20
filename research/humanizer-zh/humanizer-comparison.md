# Humanizer 中英文改稿对照

中文日常润色，我会继续用 `humanizer-zh`。它在这组中文样稿里胜过上一版，和新版中文相比也略占优。新版中文在排障句中保留了完整的技术含义，也保留了已经好读的随笔。英文我会优先用新版 `humanizer-edit-en`，尤其是技术、方法和随笔类短稿。原版英文 `humanizer` 处理短通知时更直接。

## 对照怎么做

为中文、英文各编写五段短稿，覆盖发布进展、通知、技术或学术句、随笔和需要精确保留的限定。每段给相应版本同样的读者说明、原文和交付要求。每个版本各生成一次。生成和评阅由分开的模型会话完成。每道题随机打乱改稿、用字母替换版本名，再交给一个不知道版本对应关系的模型评阅。依次比较原意与边界、第一遍是否好读、文体与改动克制程度，允许并列。共比较 35 份改稿。

原版英文使用 [blader/humanizer v3.1.0](https://github.com/blader/humanizer/blob/main/SKILL.md)，原版中文使用 [op7418/humanizer-zh，2026-09-23 修订](https://github.com/op7418/Humanizer-zh/blob/main/SKILL.md)。上一版是本对话第一轮交付的中文 Skill，在英文题里属于跨语言尝试。原版英文也额外参加了中文题，供参考。原版中文只参加中文题。

这些数字描述一次小样本模型试改与盲评。样稿是自拟短文，没有重复运行、独立人类读者测试或不加载 Skill 的对照，也没有测长文和真实发布稿。结果适合判断这组样稿里的取舍。新版在主对照之后只针对通知调整了规则，附录单列复测。

## 样稿结果

| 样稿 | 左侧版本 | 右侧版本 | 左侧胜／平／负 |
| --- | --- | --- | --- |
| 中文 | 上一版 | 原版 humanizer-zh | 1／0／4 |
| 中文 | 新版 | 原版 humanizer-zh | 1／2／2 |
| 中文 | 新版 | 上一版 | 4／0／1 |
| 英文 | 上一版 | 原版 humanizer | 2／1／2 |
| 英文 | 新版 | 原版 humanizer | 4／0／1 |
| 英文 | 新版 | 上一版 | 4／0／1 |

- **套话重的通知（Z2、E2）。** 所有版本都能删掉铺垫和自我拔高，差异在细节。Z2 上一版的“当天下午”更明确，E2 原版英文和上一版直接告诉读者何时可以取件，新版试测稿则从前台会做什么写起。
- **意义边界（Z1、E1、E5）。** 中文灰度更新里的“是否由缓存带来”是在问因果。英文原版试改中文时写成“是否和缓存有关”，放宽了问题。英文灰度更新的两个旧版都加入了 *so*，把重试间隔变更写成无法归因的明确理由。新版把观察范围、同期变更和不确定性分别交代。英文方法段里，原文明确说的是日志无法判断生效时间，英文原版改成 *we cannot tell* 后扩大了这一限制。
- **句法和技术限定（Z3、Z5、E3）。** 中文摘要中，上一版的“阈值附近政策”会让人把阈值短暂读成在修饰政策。两套中文专版把它放回估计动作旁。Z5 新版保留了“任务重试配置状态不一致”的完整含义和重跑前置条件。英文新版把 E3 的嵌套从句展开，同时保留了值班工程师的身份、操作时间和观察窗口。
- **作者已经写得好（Z4、E4）。** 两篇随笔本来就清楚。新版逐字保留。旧版做了可有可无的改动，其中英文原版试改中文随笔时把“回来路上”写成“回家路上”，加入了原文没有说的目的地。

## 通知规则复测

中英文版都补了同一项取舍。通知优先交代读者可以或需要做什么，条件和时间跟着动作走。复测重跑 Z2、E2，并各加一篇新通知。复测仅核对行动、时间和条件的交代，无新增盲评排名。

**Z2 最终稿**

周三起，可在 12:30–18:00 到前台取件。周三上午到的包裹，当天下午可以取。

**E2 最终稿**

From Wednesday, you can pick up packages at the front desk between 12:30 and 18:00. Parcels that arrive on Wednesday morning will be ready that afternoon.

**Z6 最终稿**

试改输入

请给准备来办公楼办门禁的同事润色通知，去掉套话，只给成稿。

为了进一步提升园区来访管理效率，接待处将自下周一起开展临时门禁卡领取服务，办理时间为工作日 9:00–16:00。当天上午提交申请的同事，可以在当天下午 2 点后凭工牌取卡。周末不办理。

下周一起，可在工作日 9:00–16:00 到接待处领取临时门禁卡。上午提交申请的同事，当天下午 2 点后可凭工牌取卡。周末不办理。

**E6 最终稿**

试改输入

Edit this notice for library visitors. Return just the notice.

As part of our commitment to a more convenient library experience, the West Desk will facilitate device returns on Friday between 10 a.m. and 4 p.m. The West Desk cannot accept returns without the charger. If you do not have the charger, bring the device to the main desk instead.

You can return your device with its charger at the West Desk on Friday between 10 a.m. and 4 p.m. If you do not have the charger, bring the device to the main desk.

## 全部主对照样稿

以下按题列出原始任务、四个或三个试改版本以及解盲后的结果。并列项在这一轮评阅中无明确高下。

### Z1

**任务与原文**

请把这段灰度发布更新改得更自然，读者是了解项目的同事。只交付正文。

在面向海外试点账号的首次灰度发布完成并对开启缓存的试点环境进行连续两天的数据复核后，平台组观察到导出任务的失败率从 3.1% 降到 2.4%。同期也调整了重试间隔，目前无法判断降幅是否由缓存带来。生产环境尚未验证。

**上一版**

首次面向海外试点账号的灰度发布完成后，平台组连续两天复核了开启缓存的试点环境的数据，发现导出任务的失败率从 3.1% 降到 2.4%。同期也调整了重试间隔，目前还无法判断失败率下降是否由缓存带来。生产环境尚未验证。

**原版 humanizer-zh**

面向海外试点账号的首次灰度发布完成后，平台组连续两天复核了启用缓存的试点环境数据，观察到导出任务失败率从 3.1% 降到 2.4%。同期也调整了重试间隔，目前无法判断降幅是否由缓存带来。生产环境尚未验证。

**原版 humanizer**

海外试点账号的首轮灰度发布结束后，平台组连续两天复核了开启缓存的试点环境数据，发现导出任务失败率从 3.1% 降到了 2.4%。同期也调整了重试间隔，目前还无法判断这次下降是否和缓存有关。生产环境还没验证。

**新版**

面向海外试点账号的首次灰度发布完成后，平台组连续两天复核了开启缓存的试点环境数据，发现导出任务的失败率从 3.1% 降到 2.4%。同期也调整了重试间隔，目前还无法判断降幅是否由缓存带来。生产环境尚未验证。

**盲评排序**　原版 humanizer-zh ＞ 新版 ＞ 上一版 ＞ 原版 humanizer

### Z2

**任务与原文**

把这段通知去掉 AI 味，读者是上班时会来取件的同事。只交付正文。

在这个追求高效协同的时代，值得关注的是，本次通知不仅是一次时间安排的优化，更是一次服务体验的全面升级。周三起，前台取件时间改为 12:30–18:00。周三上午到的包裹可以在下午取。总的来说，这标志着取件服务迈向新的阶段。

**上一版**

周三起，前台取件时间改为 12:30–18:00。周三上午到的包裹可以在当天下午取。

**原版 humanizer-zh**

从周三起，前台取件时间改为 12:30–18:00。周三上午到的包裹，下午就可以取。

**原版 humanizer**

从周三起，前台取件时间改为 12:30 到 18:00。周三上午到的包裹，下午就可以取。

**新版**

周三起，前台取件时间改为 12:30–18:00。周三上午到的包裹可以在下午取。

**盲评排序**　上一版 ＞ 原版 humanizer-zh ＝ 原版 humanizer ＞ 新版

### Z3

**任务与原文**

把论文摘要里的这句话润色一下，保留术语、归因和语气。只交付正文。

值得注意的是，本研究所用的回归不连续设计在阈值附近提供了关于政策与申请行为之间关系的局部估计，但由于样本量有限且未检验阈值处的协变量平衡，这一估计仍可能受到选择偏差的影响。

**上一版**

本研究采用回归不连续设计，对阈值附近政策与申请行为之间的关系作出局部估计。由于样本量有限，且未检验阈值处的协变量平衡，这一估计仍可能受到选择偏差的影响。

**原版 humanizer-zh**

本研究采用回归不连续设计，在阈值附近对政策与申请行为之间的关系作了局部估计。由于样本量有限，且未检验阈值处的协变量平衡，这一估计仍可能受到选择偏差的影响。

**原版 humanizer**

本研究采用回归不连续设计，在阈值附近对政策与申请行为之间的关系进行局部估计。由于样本量有限，且本研究未检验阈值处的协变量平衡，该估计仍可能受到选择偏差的影响。

**新版**

本研究采用回归不连续设计，在阈值附近对政策与申请行为之间的关系进行了局部估计。由于样本量有限，且未检验阈值处的协变量平衡，这一估计仍可能受到选择偏差的影响。

**盲评排序**　原版 humanizer-zh ＝ 新版 ＞ 原版 humanizer ＞ 上一版

### Z4

**任务与原文**

润色这段个人随笔，让它好读一点。只交付正文。

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说，过得去。回来路上我想了一路，他说的可能是生意，也可能是日子。

**上一版**

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说，过得去。回来的路上，我一直在想这句话。他说的可能是生意，也可能是日子。

**原版 humanizer-zh**

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说，过得去。回来路上，我一直在想，他说的可能是生意，也可能是日子。

**原版 humanizer**

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说：“过得去。”回家路上我一直在想，他说的可能是生意，也可能是日子。

**新版**

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说，过得去。回来路上我想了一路，他说的可能是生意，也可能是日子。

**盲评排序**　新版 ＝ 原版 humanizer-zh ＞ 上一版 ＞ 原版 humanizer

### Z5

**任务与原文**

把选中的一句改顺，发在内部排障群。前后是上下文，只返回选中的一句。

前文：这个问题出现在批量导出时。

选中：针对队列超时场景下的任务重试配置状态不一致问题，在启用 `retry_v2` 时值班人员应先核对两个队列的重试间隔，只有两个间隔相同时才重跑任务。

后文：试点周五结束。

**上一版**

排查队列超时场景中的任务重试配置不一致问题时，如果已启用 `retry_v2`，值班人员应先核对两个队列的重试间隔，只有间隔相同才重跑任务。

**原版 humanizer-zh**

处理队列超时场景中的任务重试配置不一致问题时，如果启用了 `retry_v2`，值班人员应先核对两个队列的重试间隔，只有间隔相同才重跑任务。

**原版 humanizer**

排查队列超时场景下的重试配置不一致问题时，如果启用了 `retry_v2`，值班人员应先核对两个队列的重试间隔，确认一致后才能重跑任务。

**新版**

排查队列超时场景中的任务重试配置状态不一致问题时，若已启用 `retry_v2`，值班人员应先核对两个队列的重试间隔，确认间隔相同后才能重跑任务。

**盲评排序**　新版 ＞ 原版 humanizer-zh ＞ 上一版 ＞ 原版 humanizer

### E1

**任务与原文**

Lightly edit this rollout update for teammates who know the project. Return just the edited passage.

The support team, after the first pilot ended and after checking logs from only those accounts that had enabled caching, observed that failed exports fell from 3.1% to 2.4%. We also changed the retry interval that week. We cannot tell whether caching explains the drop, and we have yet to test in production.

**上一版**

After the first pilot ended, the support team checked logs only from accounts that had enabled caching and found that the export failure rate fell from 3.1% to 2.4%. We also changed the retry interval that week, so we cannot tell whether caching explains the drop. We have yet to test in production.

**原版 humanizer**

After the first pilot ended, the support team checked logs only from accounts that had enabled caching. In those accounts, the export failure rate fell from 3.1% to 2.4%. We also changed the retry interval that week, so we can't tell whether caching explains the drop. We haven't tested in production yet.

**新版**

After the first pilot ended, the support team observed that the export failure rate fell from 3.1% to 2.4%. The team based that observation on logs from caching-enabled accounts only. We also changed the retry interval that week. We cannot tell whether caching explains the drop, and we have yet to test in production.

**盲评排序**　新版 ＞ 原版 humanizer ＞ 上一版

### E2

**任务与原文**

Remove the AI tone from this notice for people who collect packages at work. Return just the notice.

In today's fast-paced workplace, pickup is about more than getting a package. It's about creating a smoother, smarter, more seamless experience. From Wednesday, the front desk will hand out packages from 12:30 to 18:00. Parcels that come in on Wednesday morning will be ready that afternoon. A small change. A big step forward.

**上一版**

Starting Wednesday, you can pick up packages at the front desk from 12:30 to 18:00. Packages that arrive Wednesday morning will be ready for pickup that afternoon.

**原版 humanizer**

Starting Wednesday, you can pick up packages at the front desk from 12:30 to 18:00. Packages that arrive Wednesday morning will be ready for pickup that afternoon.

**新版**

From Wednesday, the front desk will hand out packages from 12:30 to 18:00. Parcels that come in on Wednesday morning will be ready that afternoon.

**盲评排序**　上一版 ＝ 原版 humanizer ＞ 新版

### E3

**任务与原文**

Lightly edit for an engineering incident report. Keep the technical terms, time ordering, and what is still unknown. Return just the edited passage.

The failure pattern the on-call engineer the incident lead assigned to the Saturday shift flagged appeared only in regions that had failover enabled. The team rolled back `retry_v2` at 09:20 UTC. They saw no further failures in the next hour, although they have not confirmed the cause.

**上一版**

The on-call engineer assigned to the Saturday shift by the incident lead flagged a failure pattern that appeared only in regions with failover enabled. The team rolled back `retry_v2` at 09:20 UTC and saw no further failures in the next hour. The cause is still unconfirmed.

**原版 humanizer**

The incident lead assigned an on-call engineer to the Saturday shift. The engineer flagged a failure pattern that appeared only in regions with failover enabled. The team rolled back `retry_v2` at 09:20 UTC and saw no further failures in the next hour. The cause is still unconfirmed.

**新版**

The incident lead assigned the on-call engineer to the Saturday shift. The engineer flagged a failure pattern that appeared only in regions with failover enabled. The team rolled back `retry_v2` at 09:20 UTC. They saw no further failures in the next hour, although they have not confirmed the cause.

**盲评排序**　新版 ＞ 上一版 ＞ 原版 humanizer

### E4

**任务与原文**

Make this short personal essay a little easier to read. Return just the passage.

I went back to the bookshop yesterday. The cat was still asleep on a cardboard box by the door. I asked the owner how business was. “Getting by,” he said. I thought about that all the way home.

**上一版**

I went back to the bookshop yesterday. The cat was still asleep on a cardboard box by the door. I asked the owner how business was. “Getting by,” he said. I thought about what he’d said all the way home.

**原版 humanizer**

I went back to the bookshop yesterday. The cat was still asleep on a cardboard box by the door. When I asked the owner how business was, he said, “Getting by.” I thought about that all the way home.

**新版**

I went back to the bookshop yesterday. The cat was still asleep on a cardboard box by the door. I asked the owner how business was. “Getting by,” he said. I thought about that all the way home.

**盲评排序**　新版 ＞ 原版 humanizer ＞ 上一版

### E5

**任务与原文**

Lightly edit this paragraph for a methods section. Keep the genuine distinction and the uncertainty. Return just the passage.

The audit logged when the flag was enabled, not when it took effect. We found that the first failed request came after the flag was enabled, but the log cannot tell us whether the flag had taken effect by then. We did not check other regions.

**上一版**

The audit logged when the flag was enabled. It did not log when the flag took effect. We found that the first failed request came after the flag was enabled, but the log cannot tell us whether the flag had taken effect by then. We did not check other regions.

**原版 humanizer**

The audit log recorded when the flag was enabled. The first failed request came after that. Since the log did not record when the flag took effect, we cannot tell whether it had taken effect by the time the request failed. We did not check other regions.

**新版**

The audit logged when the flag was enabled, not when it took effect. We found that the first failed request came after the flag was enabled, but the log cannot tell us whether the flag had taken effect by then. We did not check other regions.

**盲评排序**　新版 ＞ 上一版 ＞ 原版 humanizer
