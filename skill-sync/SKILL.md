---
name: skill-sync
description: 管理 Agent Skills 与 GitHub 仓库的双向同步。
---

# skill-sync

本地 skills 与 GitHub 仓库双向同步。

## 脚本路径（固定）

| 系统 | 路径 |
|------|------|
| Windows | `%USERPROFILE%\.claude\skills\skill-sync\scripts\skill_sync.py` |
| Linux/macOS | `~/.claude/skills/skill-sync/scripts/skill_sync.py` |

## 快速命令

```bash
# 查看配置
python <SCRIPT> config

# 列出本地 / GitHub skills
python <SCRIPT> list-local
python <SCRIPT> list-remote

# 对比差异
python <SCRIPT> diff

# 上传新 skill
python <SCRIPT> upload <name>
python <SCRIPT> do-upload <name>

# 更新已有 skill
python <SCRIPT> update <name>
python <SCRIPT> do-update <name>

# 安装 skill 到本地
python <SCRIPT> install <name>
python <SCRIPT> do-install <name>
```

## Profile 管理

```bash
python <SCRIPT> config profile list
python <SCRIPT> config profile add <name> <path>
python <SCRIPT> config profile set <name>
```

## 配置

`~/.skill-sync-config.json`：GitHub token、仓库名、各环境路径 profile
