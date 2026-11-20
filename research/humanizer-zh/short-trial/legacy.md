## Z1

首次面向海外试点账号的灰度发布完成后，平台组连续两天复核了开启缓存的试点环境的数据，发现导出任务的失败率从 3.1% 降到 2.4%。同期也调整了重试间隔，目前还无法判断失败率下降是否由缓存带来。生产环境尚未验证。

## Z2

周三起，前台取件时间改为 12:30–18:00。周三上午到的包裹可以在当天下午取。

## Z3

本研究采用回归不连续设计，对阈值附近政策与申请行为之间的关系作出局部估计。由于样本量有限，且未检验阈值处的协变量平衡，这一估计仍可能受到选择偏差的影响。

## Z4

昨天又去了一趟旧书店。门口那只猫还趴在纸箱上。我问老板生意怎么样，他说，过得去。回来的路上，我一直在想这句话。他说的可能是生意，也可能是日子。

## Z5

排查队列超时场景中的任务重试配置不一致问题时，如果已启用 `retry_v2`，值班人员应先核对两个队列的重试间隔，只有间隔相同才重跑任务。

## E1

After the first pilot ended, the support team checked logs only from accounts that had enabled caching and found that the export failure rate fell from 3.1% to 2.4%. We also changed the retry interval that week, so we cannot tell whether caching explains the drop. We have yet to test in production.

## E2

Starting Wednesday, you can pick up packages at the front desk from 12:30 to 18:00. Packages that arrive Wednesday morning will be ready for pickup that afternoon.

## E3

The on-call engineer assigned to the Saturday shift by the incident lead flagged a failure pattern that appeared only in regions with failover enabled. The team rolled back `retry_v2` at 09:20 UTC and saw no further failures in the next hour. The cause is still unconfirmed.

## E4

I went back to the bookshop yesterday. The cat was still asleep on a cardboard box by the door. I asked the owner how business was. “Getting by,” he said. I thought about what he’d said all the way home.

## E5

The audit logged when the flag was enabled. It did not log when the flag took effect. We found that the first failed request came after the flag was enabled, but the log cannot tell us whether the flag had taken effect by then. We did not check other regions.
