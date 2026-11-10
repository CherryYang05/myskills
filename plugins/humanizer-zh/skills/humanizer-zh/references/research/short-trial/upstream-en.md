## Z1

海外试点账号的首轮灰度发布结束后，平台组连续两天复核了开启缓存的试点环境数据，发现导出任务失败率从 3.1% 降到了 2.4%。同期也调整了重试间隔，目前还无法判断这次下降是否和缓存有关。生产环境还没验证。

## Z2

从周三起，前台取件时间改为 12:30 到 18:00。周三上午到的包裹，下午就可以取。

## Z3

本研究采用回归不连续设计，在阈值附近对政策与申请行为之间的关系进行局部估计。由于样本量有限，且本研究未检验阈值处的协变量平衡，该估计仍可能受到选择偏差的影响。

## Z4

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说：“过得去。”回家路上我一直在想，他说的可能是生意，也可能是日子。

## Z5

排查队列超时场景下的重试配置不一致问题时，如果启用了 `retry_v2`，值班人员应先核对两个队列的重试间隔，确认一致后才能重跑任务。

## E1

After the first pilot ended, the support team checked logs only from accounts that had enabled caching. In those accounts, the export failure rate fell from 3.1% to 2.4%. We also changed the retry interval that week, so we can't tell whether caching explains the drop. We haven't tested in production yet.

## E2

Starting Wednesday, you can pick up packages at the front desk from 12:30 to 18:00. Packages that arrive Wednesday morning will be ready for pickup that afternoon.

## E3

The incident lead assigned an on-call engineer to the Saturday shift. The engineer flagged a failure pattern that appeared only in regions with failover enabled. The team rolled back `retry_v2` at 09:20 UTC and saw no further failures in the next hour. The cause is still unconfirmed.

## E4

I went back to the bookshop yesterday. The cat was still asleep on a cardboard box by the door. When I asked the owner how business was, he said, “Getting by.” I thought about that all the way home.

## E5

The audit log recorded when the flag was enabled. The first failed request came after that. Since the log did not record when the flag took effect, we cannot tell whether it had taken effect by the time the request failed. We did not check other regions.
