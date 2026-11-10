# myskills

统一管理第三方与自研 Agent Skills，自动同步上游，并向 ChatGPT、Claude Code、Cursor 和 Skills CLI 分发。

[![Validate Skills](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml) [![Sync Skill Upstreams](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml)

## Skill 清单

{{SKILL_TABLE}}

**Blog** 把当前对话或学习笔记整理成博客，按读者视角审稿并润色，交付含内嵌 HTML 图的 Markdown。从 **Cherry Skills** 安装 **Blog** 后，在插件菜单选择它即可使用。插件内置 Bearguin Halo MCP，在 macOS 的本机会话中可从钥匙串授权并同步草稿、分类和标签。连接步骤见 [Halo 草稿同步](skills/personal/blog-workflow/references/halo.md)。

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

**GSAP 系列统一安装 `gsap` 插件**，其中包含 core、timeline、ScrollTrigger、plugins、utils、React、performance 和 frameworks 八个分类。三个 Marketplace 均只显示一个 GSAP 插件入口；上方清单与 Skills CLI 仍按原始分类列出技能。已安装旧分类插件时，刷新 Marketplace 后安装 `gsap`，再卸载旧的 `gsap-*` 插件，避免重复加载。

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

## 新增 Skill 的自动生成流程

1. 在 `automation/upstreams.json` 登记经过来源、许可和安全审查的上游 Skill，使用完整的 Git commit SHA；如许可证位于仓库根目录，填写 `root_license: "LICENSE"`（实际为 JSON 键 `"root_license": "LICENSE"`）。
2. 默认每个 Skill 生成一个插件；系列技能可在 `automation/plugin-groups.json` 明确列出成员，合成一个插件。随后在 `automation/plugin-appearance.json` 按 **Plugin 名称**设置专属颜色、SVG `glyph` 与概念说明。Actions 负责将这些矢量源数据渲染成统一的 128×128 图标，不会自动创作图形。
3. 推送到 `master` 后，`Sync Skill Upstreams` 的 Push 触发器会拉取缺失的第三方 Skill、做静态安全/许可证检查、生成 Plugin/Marketplace/README 与版本号，并创建候选 PR。
4. 只有候选 PR 的**精确提交**通过 `Validate Skills` 后才会自动合并。第一次登记但未生成时，短暂的主分支验证失败属于引导阶段状态；如 Action 受账户权限/计费限制未运行，不能认为导入完成，需查看 Workflow/PR 结果。

新增或移除上游的注册表修改必须经过人工/Agent 明确审查和提交；自动流程不会自行发现、添加来源。每周五的同步仍仅更新已经登记的来源。

## 仓库维护

- `skills/external/` 保存第三方 Skill 的完整上游快照，来源与固定提交记录在 `automation/upstreams.json`；`skills/personal/` 保存自研 Skill，不受上游同步覆盖。
- `plugins/`、三个平台的 Marketplace、`skills.sh.json`、本 README 均由 `automation/scripts/generate.py` 生成。README 正文编辑 `automation/templates/README.md.tpl`；插件分组编辑 `automation/plugin-groups.json`；SVG 图标编辑 `automation/plugin-appearance.json`。**不要直接修改生成物**。
- 每周五北京时间 20:30，GitHub Actions 检查上游；有变动才创建候选 PR，通过 CI 后自动合并。无变化的检查结果留在 Action Summary / Artifact；最近一次实际同步记录见 [UPSTREAM_SYNC_REPORT.md](./UPSTREAM_SYNC_REPORT.md)。
- GitHub 生成与合并成功不保证客户端已刷新。安装和更新结果须在目标客户端核验。

新增第三方 Skill 时，直接提供 GitHub 链接并要求加入仓库即可。来源与许可证审查、代码安全检查、专属图标设计、生成和 CI 的强制要求都集中在 [AGENTS.md](./AGENTS.md)。完整历史可从 Git 提交追溯。
