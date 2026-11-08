# myskills

统一管理第三方与自研 Agent Skills，自动同步上游，并向 ChatGPT、Claude Code、Cursor 和 Skills CLI 分发。

[![Validate Skills](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml) [![Sync Skill Upstreams](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml)

## Skill 清单

{{SKILL_TABLE}}

## 安装与更新

### Skills CLI（Codex / Claude Code / Cursor 等）

在目标项目目录执行下面的命令；加 `-g` 可全局安装，`-y` 跳过交互确认。

```bash
# 查看全部 Skill；或者交互式选择
npx skills add CherryYang05/myskills --list
npx skills add CherryYang05/myskills

# 指定 Skill 和客户端
npx skills add CherryYang05/myskills -s humanizer -a codex -g -y
npx skills add CherryYang05/myskills -s blog-writer -a claude-code -g -y
npx skills add CherryYang05/myskills -s impeccable -a cursor -y

# 安装全部 Skill 到选定客户端；或全部受支持客户端
npx skills add CherryYang05/myskills -s '*' -a codex -a claude-code -g -y
npx skills add CherryYang05/myskills --all

# 临时使用，不安装
npx skills use CherryYang05/myskills@humanizer -a codex
```

`-s / --skill` 选技能，`-a / --agent` 选客户端，`-g` 全局安装。`add` 通过 `-s` 选技能；`use` 使用 `owner/repo@skill`。详见 [Skills CLI](https://github.com/vercel-labs/skills)。

```bash
npx skills ls -g                 # 查看已全局安装的 Skill
npx skills check                 # 检查更新
npx skills update -g             # 更新全局 Skill
npx skills remove humanizer -g   # 卸载指定 Skill
```

### 各客户端 Plugin Marketplace

Marketplace 提供的是另一种分发方式：先注册仓库，再选择具体 Plugin 安装。已经通过 Skills CLI 安装的同名 Skill 通常无需重复安装。

**Codex CLI / ChatGPT 桌面版**

```bash
codex plugin marketplace add CherryYang05/myskills
codex plugin marketplace list
codex plugin marketplace upgrade cherry-myskills
```

在 Codex 中打开 `/plugins`，从 **Cherry Skills** 选择所需插件安装。

**Claude Code**

```bash
claude plugin marketplace add CherryYang05/myskills
claude plugin install humanizer@cherry-skills
```

也可在交互界面使用 `/plugin`。`cherry-skills` 为 Claude Marketplace 标识。

**Cursor**：在 Customize → Plugins（或团队 Dashboard → Plugins & MCPs）中从 GitHub 导入 `https://github.com/CherryYang05/myskills`；团队 Marketplace 取决于计划与权限。个人使用也可选择上面的 `npx skills add ... -a cursor`。

**ChatGPT 工作区**：支持 GitHub Marketplace 的管理员可在 Admin → Plugins → Add → Import marketplace 中导入本仓库并跟踪 `master`，随后从 **Cherry Skills** 安装。既有手动上传的插件不会被 GitHub Action 自动替换。

## 仓库维护

- `skills/external/` 保存第三方 Skill 的完整上游快照，来源与固定提交记录在 `automation/upstreams.json`；`skills/personal/` 保存自研 Skill，不受上游同步覆盖。
- `plugins/`、三个平台的 Marketplace、`skills.sh.json`、本 README 均由 `automation/scripts/generate.py` 生成。README 正文编辑 `automation/templates/README.md.tpl`；SVG 图标编辑 `automation/plugin-appearance.json`。**不要直接修改生成物**。
- 每周五北京时间 20:30，GitHub Actions 检查上游；有变动才创建候选 PR，通过 CI 后自动合并。无变化的检查结果留在 Action Summary / Artifact；最近一次实际同步记录见 [UPSTREAM_SYNC_REPORT.md](./UPSTREAM_SYNC_REPORT.md)。
- GitHub 生成与合并成功不保证客户端已刷新。安装和更新结果须在目标客户端核验。

新增第三方 Skill 时，直接提供 GitHub 链接并要求加入仓库即可。来源与许可证审查、代码安全检查、专属图标设计、生成和 CI 的强制要求都集中在 [AGENTS.md](./AGENTS.md)。完整历史可从 Git 提交追溯。
