---
name: skill-sync
description: 管理 Agent Skills 与 GitHub 仓库的双向同步。触发条件：同步 skills、上传/下载 skill、更新 GitHub 上的 skill、列出 skills、对比差异等。
---

# skill-sync

管理本地 skills 与 GitHub 仓库的双向同步，支持多环境 profile。

## 快速开始

```bash
# 1. 配置（首次使用）
python <SCRIPT> config set

# 2. 列出本地和 GitHub 上的 skills
python <SCRIPT> list-local
python <SCRIPT> list-remote

# 3. 对比差异
python <SCRIPT> diff
```

## 常用命令

```bash
# 上传新 skill 到 GitHub
python <SCRIPT> upload <skill-name>
python <SCRIPT> do-upload <skill-name>

# 更新 GitHub 上已有的 skill
python <SCRIPT> update <skill-name>
python <SCRIPT> do-update <skill-name>

# 从 GitHub 安装 skill 到本地
python <SCRIPT> install <skill-name>
python <SCRIPT> do-install <skill-name>
```

## 多环境 Profile

```bash
# 列出所有 profiles
python <SCRIPT> config profile list

# 新增 profile
python <SCRIPT> config profile add <name> <path> [说明]

# 切换活跃 profile
python <SCRIPT> config profile set <name>

# 临时使用某 profile（不改变默认）
python <SCRIPT> --profile <name> <命令>
```

## 配置存储

`~/.skill-sync-config.json`，包含：
- `github_token`：GitHub PAT
- `github_repo`：仓库名称（user/repo）
- `profiles`：多环境路径配置

## 注意

- git 已默认配置好，脚本直接使用 git 命令操作仓库
- 若 git 未配置，Agent 会提示用户逐步完成配置
