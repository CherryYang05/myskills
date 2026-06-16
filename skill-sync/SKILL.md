---
name: skill-sync
description: 管理 Agent Skills 与 GitHub 仓库的双向同步。
---

# skill-sync

本地 skills 与 GitHub 仓库双向同步。**全程走 git（HTTPS + token），不使用 GitHub REST API。**

## 工作机制

- 维护一个持久缓存仓库 `~/.skill-sync-cache/<repo>`：仅首次完整 `git clone` 一次，之后每次同步只做 `fetch + reset`，不再重复克隆。
- `push` / `pull` **默认只预览**变更；只有加 `--apply` 才真正提交推送 / 写入本地。
- 仓库 `README.md` 的「已收录的 Skills」表格和「常用同步命令」段由脚本在每次 `push` 时**自动生成**（从各 skill 的 `SKILL.md` frontmatter `description` 提取），无需手动维护，也不依赖 REST API。

## 用户确认规则

**执行任何会推送到 GitHub 或写入本地的操作前，必须先展示预览摘要并等待用户确认。** 具体：

- `push <name>`（不带 `--apply`）— 只读预览，列出将提交的文件变更；展示给用户确认
- `push <name> --apply` — 真正推送，**仅在用户确认后执行**
- `pull <name>`（不带 `--apply`）— 只读预览，列出将覆盖/新增的本地 skill；展示给用户确认
- `pull <name> --apply` — 真正写入本地，**仅在用户确认后执行**

不需要确认的只读操作：`status`、`config`。

## 脚本路径（固定）

| 系统 | 路径 |
|------|------|
| Windows | `%USERPROFILE%\.claude\skills\skill-sync\scripts\skill_sync.py` |
| Linux/macOS | `~/.claude/skills/skill-sync/scripts/skill_sync.py` |

## 命令

```bash
# 查看配置
python <SCRIPT> config

# 查看状态：本地 vs 仓库差异（只读）
#   NEW=仅本地  REMOTE=仅远程  SAME=一致  MOD=内容不同
python <SCRIPT> status

# 推送本地 → GitHub（先预览，再 --apply）
python <SCRIPT> push              # 全部本地 skill
python <SCRIPT> push <name> ...   # 指定 skill
python <SCRIPT> push --apply      # 确认后执行

# 拉取 GitHub → 本地（先预览，再 --apply）
python <SCRIPT> pull              # 全部
python <SCRIPT> pull <name> ...   # 指定
python <SCRIPT> pull --apply      # 确认后执行
```

旧命令 `upload`/`do-upload`/`update`/`do-update`/`install`/`do-install`/`list-local`/`list-remote`/`diff` 仍作为别名映射到新命令，保持向后兼容。

## Profile 管理

```bash
python <SCRIPT> config profile list
python <SCRIPT> config profile add <name> <path>
python <SCRIPT> config profile set <name>
```

## 配置

`~/.skill-sync-config.json`：GitHub token、仓库名、各环境路径 profile。

> 注意：该 token 仅用于 git over HTTPS（clone/fetch/push）。本仓库**不使用 GitHub REST API**，因此 token 无需具备 API 权限。token 不会写入缓存仓库的 `.git/config`（fetch/push 时以参数形式临时传入）。
