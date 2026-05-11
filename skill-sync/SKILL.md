---
name: skill-sync
description: 管理 Agent Skills 与 GitHub 仓库的双向同步。
short_description: Skills 与 GitHub 仓库双向同步
---

# skill-sync

本地 skills 与 GitHub 仓库双向同步。

## 用户确认规则

**每次与 GitHub 仓库交互（拉取或推送）前，必须先向用户展示操作摘要并等待确认，确认后才能执行。** 具体包括：

- `do-upload <name>` — 推送前列出将上传的 skill 名称，询问用户确认
- `do-update <name>` — 推送前列出将更新的 skill 名称，询问用户确认
- `do-install <name>` — 拉取前列出将安装的 skill 名称，询问用户确认
- `do-push <name> <path>` — 推送前列出 skill 名称和来源路径，询问用户确认
- 更新仓库 README — 推送前展示将要变更的内容，询问用户确认

不需要确认的操作：`list-local`、`list-remote`、`diff`、`config`（这些是只读查询）。

## 脚本路径

| 环境 | 路径 |
|------|------|
| Windows | `%USERPROFILE%\.claude\skills\skill-sync\scripts\skill_sync.py` |
| Linux/macOS | `~/.claude/skills/skill-sync/scripts/skill_sync.py` |
| Claude.ai 容器 | `/mnt/skills/user/skill-sync/scripts/skill_sync.py`（只读，需先复制到 `/home/claude/`） |

**Claude.ai 环境注意**：脚本所在目录只读，使用前必须先复制：
```bash
cp /mnt/skills/user/skill-sync/scripts/skill_sync.py /home/claude/skill_sync.py
```
后续所有命令使用 `python /home/claude/skill_sync.py`。

## 配置

### 非交互式初始化（Claude.ai 环境必须用此方式）

```bash
python <SCRIPT> config init --token <GITHUB_TOKEN> --repo <OWNER/REPO> [--local-path <PATH>] [--profile <NAME>]
```

- `--local-path` 可选，默认自动检测（Claude.ai 中为 `/mnt/skills/user`，本地为 `~/.claude/skills`）
- `--profile` 可选，默认 `default`

### 交互式配置（仅本地终端可用）

```bash
python <SCRIPT> config set
```

### 查看当前配置

```bash
python <SCRIPT> config
```

### Profile 管理

```bash
python <SCRIPT> config profile list
python <SCRIPT> config profile add <name> <path>
python <SCRIPT> config profile set <name>
```

配置文件：`~/.skill-sync-config.json`（GitHub token、仓库名、各环境路径 profile）

## 快速命令

```bash
# 列出本地 / GitHub skills
python <SCRIPT> list-local
python <SCRIPT> list-remote

# 对比差异
python <SCRIPT> diff

# 上传新 skill（本地有、远端无）
python <SCRIPT> upload <name>        # 预览
python <SCRIPT> do-upload <name>     # 执行

# 更新已有 skill（本地和远端都有）
python <SCRIPT> update <name>        # 预览
python <SCRIPT> do-update <name>     # 执行

# 安装 skill 到本地（从远端拉取）
python <SCRIPT> install <name>       # 预览
python <SCRIPT> do-install <name>    # 执行

# 从任意路径推送（不受 local_skills_path 限制）
python <SCRIPT> push <name> <source-dir>      # 预览
python <SCRIPT> do-push <name> <source-dir>   # 执行

# 更新仓库 README 中的 skills 表格
python <SCRIPT> update-readme
```

## push 命令详解

`push` 是为 Claude.ai 环境设计的命令，用于将**任意路径**下的 skill 推送到 GitHub 仓库。

典型场景：在 Claude.ai 中生成/修改了某个 skill 的 SKILL.md，文件在 `/mnt/user-data/outputs/` 或 `/home/claude/` 下，需要推送到远端。

```bash
# 推送一个目录（目录中须含 SKILL.md）
python <SCRIPT> do-push skill-blog-writer /home/claude/skill-blog-writer/

# 推送单个 SKILL.md 文件（自动使用其父目录）
python <SCRIPT> do-push skill-blog-writer /home/claude/skill-blog-writer/SKILL.md
```

与 `upload`/`update` 的区别：
- `upload`/`update` 只能推送 `local_skills_path` 下的 skills
- `push` 可以指定任意源路径，适用于 Claude.ai 容器中生成的文件

## Claude.ai 环境完整工作流

```bash
# 1. 复制脚本到可写目录
cp /mnt/skills/user/skill-sync/scripts/skill_sync.py /home/claude/skill_sync.py

# 2. 初始化配置
python /home/claude/skill_sync.py config init --token <TOKEN> --repo CherryYang05/myskills

# 3. 准备要推送的 skill（假设 SKILL.md 在 /mnt/user-data/outputs/SKILL.md）
mkdir -p /home/claude/skill-blog-writer
cp /mnt/user-data/outputs/SKILL.md /home/claude/skill-blog-writer/SKILL.md

# 4. 推送
python /home/claude/skill_sync.py do-push skill-blog-writer /home/claude/skill-blog-writer

# 5. 更新 README
python /home/claude/skill_sync.py update-readme
```

## 同步后更新仓库 README

每次执行 upload / update / push 完成后，必须同步更新 GitHub 仓库的 `README.md`：

1. 通过 GitHub API 获取当前仓库 README 内容和 SHA
2. 读取仓库中所有 skill 的 `SKILL.md` frontmatter 中的 `description` 字段
3. 重新生成 `## 已收录的 Skills` 表格部分（保留 README 其余内容不变）
4. 通过 GitHub API（PUT `repos/{owner}/{repo}/contents/README.md`）提交更新
