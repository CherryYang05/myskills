# 外部 Skill 同步与修正报告

## 重构时的基线

本仓库于 2026-11-08 迁移为 `skills/external/` 与 `skills/personal/` 结构。迁移沿用最近一次已合并的 [上游更新 PR #10](https://github.com/CherryYang05/myskills/pull/10) 所记录的外部提交，没有在迁移时发起新的上游抓取。自研 Skill 未被上游替换。

| 外部 Skill | 当前同步 commit | 上游仓库 |
|---|---|---|
| deep-research | [6d9388674de1](https://github.com/Imbad0202/academic-research-skills/commit/6d9388674de1ad0437ad95db3d52f92b92204d84) | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills) |
| frontend-design | [ca45fc496a34](https://github.com/anthropics/skills/commit/ca45fc496a3436251f191354091d557da31c15b5) | [anthropics/skills](https://github.com/anthropics/skills) |
| humanizer | [0ef9fe5bc357](https://github.com/blader/humanizer/commit/0ef9fe5bc3572734fd3ae6c448fe00a30cd5dcf0) | [blader/humanizer](https://github.com/blader/humanizer) |
| impeccable | [687bc381bc90](https://github.com/pbakaus/impeccable/commit/687bc381bc9091bf252c0a05303640561014a425) | [pbakaus/impeccable](https://github.com/pbakaus/impeccable) |
| mermaid-diagrams | [3027f20f3181](https://github.com/softaworks/agent-toolkit/commit/3027f20f3181758385a1bb8c022d4041dfb4de84) | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit) |
| shadcn | [42f3bb63b46a](https://github.com/shadcn-ui/ui/commit/42f3bb63b46a69e52a24bd005cdc9ec15ba7a7b9) | [shadcn-ui/ui](https://github.com/shadcn-ui/ui) |
| skill-creator | [b9e19e6f4477](https://github.com/anthropics/skills/commit/b9e19e6f44773509fbdd7001d77ff41a49a486c1) | [anthropics/skills](https://github.com/anthropics/skills) |
| web-design-guidelines | [1a2c79d4e6c4](https://github.com/vercel-labs/agent-skills/commit/1a2c79d4e6c4a2283dc2c614b6538cbe1ed5ca62) | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) |

下一次每周五（北京时间 20:30）或手动执行 `Sync Skill Upstreams` 后，这份文件将由自动程序重新生成，列明全部外部 Skill 的检查状态、更新前后 commit、文件新增/修改/删除及上游提交。只有通过 CI 并合并到 `master` 的候选才代表实际同步。
