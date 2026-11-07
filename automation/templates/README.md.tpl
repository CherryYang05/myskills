# myskills

个人 Agent Skills 仓库。将第三方 Skill 的上游更新和自己的 Skill 统一管理，提供 GitHub Marketplace 清单供支持该功能的客户端和 ChatGPT 工作区使用。

[![Validate Skills](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml) [![Sync Skill Upstreams](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml)

## Skill 清单

{{SKILL_TABLE}}

## 安装与更新

本仓库有两种安装途径：

- **Skills CLI**：将原始 `SKILL.md` 和配套文件安装到本地代码 Agent（Codex、Claude Code、Cursor 等），支持选择 Skill、目标 Agent 和安装作用域。
- **Plugin Marketplace**：通过客户端自己的插件目录安装 `plugins/<name>/` 打包产物。导入 Marketplace 只注册可选来源，**还需要安装具体插件**。

### 方法一：npx skills（跨平台推荐）

需要 Node.js **22.20 或更高版本**。在目标项目目录执行表示项目级安装；加 `-g` 则表示当前用户全局安装。

```bash
# 查看仓库当前所有可安装的 Skill（只查询，不安装）
npx skills add CherryYang05/myskills --list

# 交互式选择 Skill 和客户端（当前项目）
npx skills add CherryYang05/myskills

# 推荐：通过 -s 指定 Skill；无需填写很长的 GitHub 子目录 URL
npx skills add CherryYang05/myskills -s humanizer

# 给 Codex 全局安装指定 Skill
npx skills add CherryYang05/myskills -s humanizer -a codex -g -y

# 给 Claude Code 全局安装指定 Skill
npx skills add CherryYang05/myskills -s blog-writer -a claude-code -g -y

# 给 Cursor 当前项目安装指定 Skill
npx skills add CherryYang05/myskills -s impeccable -a cursor -y

# 同时将两个指定 Skill 安装到 Codex 和 Claude Code（当前项目）
npx skills add CherryYang05/myskills -s humanizer -s blog-writer -a codex -a claude-code -y

# 将仓库中的所有 Skill 安装到指定客户端（全局）
npx skills add CherryYang05/myskills -s '*' -a codex -a claude-code -a cursor -g -y

# 在所有受支持的客户端安装全部 Skill（范围较大，谨慎使用）
npx skills add CherryYang05/myskills --all
```

**记忆方式：** `npx skills add CherryYang05/myskills -s <skill-name>`。例如只安装 Humanizer，直接用 `-s humanizer`；不需要记住 `skills/external/` 或 `skills/personal/` 的目录位置。

如果只是临时使用而不安装，Skills CLI 另有 `use` 命令（`@` 后面是 Skill 名称）：

```bash
npx skills use CherryYang05/myskills@humanizer -a codex
```

注意 `npx skills add humanizer@CherryYang05/myskills` 并非 CLI 支持的指定 Skill 语法；`add` 使用 `-s`，而 `use` 才使用 `owner/repo@skill`。

查看、更新和卸载通过 Skills CLI 安装的 Skill：

```bash
npx skills list                 # 当前项目已安装的 Skill
npx skills ls -g                # 全局已安装的 Skill
npx skills ls -a codex          # 只查看 Codex 的项目级 Skill
npx skills check                # 检查是否存在更新
npx skills update humanizer -g  # 更新全局安装的 humanizer
npx skills update -g            # 更新所有全局 Skill
npx skills remove humanizer -g  # 卸载全局安装的 humanizer
```

`-s`（`--skill`）选择 Skill 名称；`-a`（`--agent`）是官方支持的客户端选择参数，例如 `-a codex`、`-a claude-code`、`-a cursor`，省略时由 CLI 自动检测或交互选择；`-g` 代表全局安装，`-y` 跳过确认；`--all` 同时涵盖所有技能和所有受支持的客户端。可用 `--copy` 改用复制而非符号链接。更多参数见 [Skills CLI 官方命令文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。

### 方法二：各客户端的 Plugin Marketplace

这条途径分发自动生成的 `plugins/<name>/`。**同一个 Skill 选用一种安装途径通常就够了**，以免出现本地和插件版重复加载或版本不一致。

**Codex CLI / ChatGPT 桌面版的 Codex 模式**

```bash
# 注册 GitHub 插件市场（仓库入口是 .agents/plugins/marketplace.json）
codex plugin marketplace add CherryYang05/myskills

# 查看已注册的市场
codex plugin marketplace list

# 刷新该市场的仓库快照
codex plugin marketplace upgrade cherry-myskills

# 启动 Codex
codex
```

然后在 Codex 交互界面输入 `/plugins`，切换到 **Cherry Skills**，选择 `humanizer`（或其他插件）并点击安装。官方文档提供了市场注册 CLI 和交互式插件安装入口；这里不使用未经核实的 `codex plugin install ...` 命令。ChatGPT 桌面版也可从「插件」目录选择 Cherry Skills 安装。详见 [OpenAI 插件打包与 Marketplace 文档](https://developers.openai.com/plugins/build/plugins)。

**Claude Code**

```bash
# 注册仓库中的 .claude-plugin/marketplace.json
claude plugin marketplace add CherryYang05/myskills

# 安装指定插件：名称@市场名称
claude plugin install humanizer@cherry-skills
claude plugin install blog-writer@cherry-skills
```

也可以在 Claude Code 交互界面使用 `/plugin marketplace add CherryYang05/myskills` 和 `/plugin install humanizer@cherry-skills`。这里的 `cherry-skills` 是 Claude Marketplace 的标识，和 Codex 使用的 `cherry-myskills` 不同。

**Cursor**

在 Cursor 的 **Customize → Plugins**（或团队的 **Dashboard → Plugins & MCPs**）中，从 GitHub 仓库导入 `https://github.com/CherryYang05/myskills`，然后选择需要的插件安装。入口为 `.cursor-plugin/marketplace.json`；团队 Marketplace 依赖 Teams / Enterprise 对应功能。当前不提供未经核实的 Cursor 命令行插件安装命令。个人用户可直接使用上面的 `npx skills add ... -a cursor`。参考 [Cursor 插件文档](https://cursor.com/docs/plugins)。

**ChatGPT 网页版 / Work**

在支持导入 GitHub Marketplace 的工作区中，进入 **Admin → Plugins → Add → Import marketplace**，输入仓库 `https://github.com/CherryYang05/myskills`，跟踪 `master`，随后从 **Cherry Skills** 安装所需插件。导入和 GitHub 更新并不会自动替换网页版此前手动上传的同名插件。

## 两阶段同步

1. **外部上游 → 本仓库**：每周五北京时间 20:30，Sync Skill Upstreams 从 `automation/upstreams.json` 检查外部来源。仅在源码或生成物变化时创建候选 PR，经精确提交 CI 校验后自动合并；无变化的检查结果留在 Action Summary / Artifact，不产生空转 PR。自研 Skill 不在自动覆盖范围内。
2. **本仓库 → ChatGPT**：`.agents/plugins/marketplace.json` 指向生成的 `plugins/<name>/` 安装包；每个包包含 `plugin.json`、`skills/<name>/SKILL.md` 和运行相关文件，自动排除 Claude/Cursor 专用的安装元数据（源 Skill 完整保留）。支持 GitHub Marketplace 导入的 ChatGPT 工作区管理员可导入仓库并跟踪 `master`，平台通常每日同步，也可手动 Sync now。仓库更新不代表个人 ChatGPT Plus 空间中手动上传的插件已更新。

相关配置及同步限制详见 [架构说明](./docs/architecture.md) 和 [OpenAI 官方文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

## 维护原则

- `automation/upstreams.json` 是外部 Skill 的唯一来源注册表。外部目录和注册表必须一一对应；新增第三方 Skill 必须同时登记。
- 新增外部 Skill 的标准流程见 [外部 Skill 准入规范](./docs/adding-external-skill.md)：评估来源与风险、保持上游完整快照、登记 SHA、生成分发包、通过 PR 和 CI 后合并；后续更新自动化。
- `automation/scripts/` 管理上游检查、来源安全、版本报告、校验及自动合并；`automation/tests/` 是回归测试。
- `README.md`、`skills.sh.json`、三个平台的 Marketplace 清单和 `plugins/` 都是生成产物。编辑安装文档时改 `automation/templates/README.md.tpl`；修改 Skill、模板或配置后运行 `python3 automation/scripts/generate.py`，再运行 `python3 automation/scripts/generate.py --check`。
- `UPSTREAM_SYNC_REPORT.md` 记录最近一次实际同步的上游变更；无变化的周度检查报告保留在 GitHub Action Summary / Artifact，避免冗余提交。
- 自动流程只读取和复制上游文件，绝不执行上游脚本。外部 Skill 的自动替换可能删除旧的本地定制，历史可由 Git 恢复。
- GitHub Actions 故障会保留候选 PR 并创建故障 Issue，不绕过校验。

仓库的 Agent 维护约定见 [AGENTS.md](./AGENTS.md)，生成器、Actions 触发条件和验证步骤见 [docs/architecture.md](./docs/architecture.md)。
