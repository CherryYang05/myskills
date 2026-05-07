# myskills

个人 Agent Skills 仓库，用于在不同环境间同步和管理个人 skills，支持 Claude Code、OpenCode、Codex 等各类 Agent。

## 快速开始（在新环境安装 skill-sync）

```bash
curl -fsSL https://raw.githubusercontent.com/CherryYang05/myskills/main/skill-sync/scripts/bootstrap.py | python3 - --token 你的GitHub_TOKEN --repo CherryYang05/myskills
```

参数说明：
- `--token`: GitHub Personal Access Token（需 repo 权限）
- `--repo`: 仓库地址，默认 `CherryYang05/myskills`
- `--install-to`: 可选，指定安装路径
- `--profile`: 可选，profile 名称，默认 `default`

获取 Token: https://github.com/settings/tokens

验证安装:
```bash
python ~/.claude/skills/skill-sync/scripts/skill_sync.py config
```

---

## 已收录的 Skills

| Skill 名称 | 说明 |
|-----------|------|
| skill-sync | 本地 skills 与 GitHub 仓库的双向同步工具 |
| easy-new-os-maintain | 用于维护 EasyNewOS 仓库的 README 和脚本扩展 |
| skill-creator | 创建和优化 Claude skills，支持测试和性能评估 |

## 简介

随着使用 Agent 的场景增多（Windows 本机、Linux 服务器、网页版等），各环境的 skills 难以保持一致。本仓库用于集中存储个人 skills，配合 skill-sync 工具实现多环境双向同步。

所有操作通过 `skill-sync` 脚本完成，认证使用 GitHub PAT，环境配置保存在 `~/.skill-sync-config.json`。

## 仓库地址

https://github.com/CherryYang05/myskills
