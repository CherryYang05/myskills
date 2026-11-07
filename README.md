# myskills

个人 Agent Skills 仓库。将第三方 Skill 的上游更新和自己的 Skill 统一管理，提供 GitHub Marketplace 清单供支持该功能的客户端和 ChatGPT 工作区使用。

## 安装

**Skills CLI** 直接读取本仓库的 `skills/external/` 与 `skills/personal/`，可以独立于 Plugin Marketplace 安装。需要 Node.js 和 [Skills CLI](https://github.com/vercel-labs/skills)：

```bash
# 预览可安装的 16 个 Skill
npx skills add CherryYang05/myskills --list

# 选择一个 Skill，安装至 Claude Code（全局）
npx skills add CherryYang05/myskills --skill humanizer -a claude-code -g -y

# 同时安装两个 Skill 到 Cursor（项目级；在目标项目目录中执行）
npx skills add CherryYang05/myskills --skill humanizer --skill blog-writer -a cursor -y

# 安装所有 Skill 到 Codex 和 Claude Code（全局）
npx skills add CherryYang05/myskills --skill '*' -a codex -a claude-code -g -y

# 安装全部 Skill 到 CLI 支持的所有客户端（谨慎使用）
npx skills add CherryYang05/myskills --all
```

也支持将单个 Skill 目录作为来源：`npx skills add https://github.com/CherryYang05/myskills/tree/master/skills/external/humanizer`。用 `npx skills ls -g` 检查已安装的全局 Skill，`npx skills check` 检查更新。

**Marketplace 分发**：ChatGPT 使用 `.agents/plugins/marketplace.json`；Claude Code 使用 `.claude-plugin/marketplace.json`；Cursor 使用 `.cursor-plugin/marketplace.json`（团队 Marketplace，受计划及权限约束）。三个入口均引用自动生成的 `plugins/<name>/`，原始上游文件保持原样。Claude Code 的安装命令：

```bash
claude plugin marketplace add CherryYang05/myskills
claude plugin install humanizer@cherry-skills
```

## Skill 清单

| Skill | 类型 | 来源 / 当前版本 | 说明 |
|---|---|---|---|
| [deep-research](./skills/external/deep-research) | 外&#8288;部&#8288;同&#8288;步 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research) · `6d9388674de1` | Universal deep research agent team |
| [frontend-design](./skills/external/frontend-design) | 外&#8288;部&#8288;同&#8288;步 | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design) · `ca45fc496a34` | Guidance for distinctive, intentional visual design when building new UI or reshaping an… |
| [humanizer](./skills/external/humanizer) | 外&#8288;部&#8288;同&#8288;步 | [blader/humanizer](https://github.com/blader/humanizer) · `0ef9fe5bc357` | Rewrite AI-sounding text so it reads like the writer without changing what it says |
| [impeccable](./skills/external/impeccable) | 外&#8288;部&#8288;同&#8288;步 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable/tree/main/.agents/skills/impeccable) · `687bc381bc90` | Use when the user wants to design, redesign, shape, critique, audit, polish, simplify… |
| [mermaid-diagrams](./skills/external/mermaid-diagrams) | 外&#8288;部&#8288;同&#8288;步 | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/main/skills/mermaid-diagrams) · `3027f20f3181` | Comprehensive guide for creating software diagrams using Mermaid syntax |
| [shadcn](./skills/external/shadcn) | 外&#8288;部&#8288;同&#8288;步 | [shadcn-ui/ui](https://github.com/shadcn-ui/ui/tree/main/skills/shadcn) · `42f3bb63b46a` | Manages shadcn components and projects — adding, searching, fixing, debugging, styling… |
| [skill-creator](./skills/external/skill-creator) | 外&#8288;部&#8288;同&#8288;步 | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) · `b9e19e6f4477` | Create new skills, modify and improve existing skills, and measure skill performance |
| [web-design-guidelines](./skills/external/web-design-guidelines) | 外&#8288;部&#8288;同&#8288;步 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) · `1a2c79d4e6c4` | Review UI code for Web Interface Guidelines compliance |
| [ds-mr-reviewer](./skills/personal/ds-mr-reviewer) | 自研 | 自研 | MR代码检视工具 |
| [dt-case-enhancer](./skills/personal/dt-case-enhancer) | 自研 | 自研 | 使用CodeAgent对已有DT用例进行增强补齐 |
| [dt-case-generator](./skills/personal/dt-case-generator) | 自研 | 自研 | 使用CodeAgent生成DT(开发者自测试)用例 |
| [blog-writer](./skills/personal/skill-blog-writer) | 自研 | 自研 | 将技术对话整理为结构完整、可独立阅读的中文技术文章 |
| [skill-dev-flow](./skills/personal/skill-dev-flow) | 自研 | 自研 | 固化 Agent 驱动的完整开发流程——从需求分析、项目初始化（AGENTS.md）、需求拆分（模块/功能/任务），到逐个功能的设计文档、实现、收尾归档 |
| [skill-dev-sop](./skills/personal/skill-dev-sop) | 自研 | 自研 | 固化 Agent 驱动的通用软件开发标准流程——需求分析、系统设计（架构总览/模块边界/依赖方向）、项目初始化（AGENTS.md）、模块与任务拆分、逐个功能的设计文档（含耦合… |
| [skill-iterate](./skills/personal/skill-iterate) | 自研 | 自研 | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好 |
| [skill-os-setup](./skills/personal/skill-os-setup) | 自研 | 自研 | 用于维护 EasyNewOS 仓库 |

## 两阶段同步

1. **外部上游 → 本仓库**：每周五北京时间 20:30，Sync Skill Upstreams 从 `automation/upstreams.json` 读取全部外部 Skill 来源，按上游 Git 提交获取完整技能目录；生成候选 PR。只有通过精确提交的 Validate Skills 校验后才自动合并，更新 README、Marketplace 清单及根目录 `UPSTREAM_SYNC_REPORT.md`。自研 Skill 不在自动覆盖范围内。
2. **本仓库 → ChatGPT**：`.agents/plugins/marketplace.json` 指向生成的 `plugins/<name>/` 安装包；每个包包含 `plugin.json`、`skills/<name>/SKILL.md` 和运行相关文件，自动排除 Claude/Cursor 专用的安装元数据（源 Skill 完整保留）。支持 GitHub Marketplace 导入的 ChatGPT 工作区管理员可导入仓库并跟踪 `master`，平台通常每日同步，也可手动 Sync now。仓库更新不代表个人 ChatGPT Plus 空间中手动上传的插件已更新。

工作区导入：**Admin → Plugins → Add → Import marketplace**；Source 为 `https://github.com/CherryYang05/myskills`，Path 留空，Branch 填 `master`。已有手动上传插件的身份迁移需要单独处理。详见 [OpenAI 官方导入文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

## 维护原则

- `automation/upstreams.json` 是外部 Skill 的唯一来源注册表。外部目录和注册表必须一一对应；新增第三方 Skill 必须同时登记。
- `automation/scripts/` 管理上游检查、来源安全、版本报告、校验及自动合并；`automation/tests/` 是回归测试。
- `README.md`、`skills.sh.json`、三个平台的 Marketplace 清单和 `plugins/` 都是生成产物。修改 Skill 或配置后执行 `python3 automation/scripts/generate.py`，再运行 `python3 automation/scripts/generate.py --check` 验证。
- `UPSTREAM_SYNC_REPORT.md` 是 GitHub 上游检查生成的根目录报告。成功合并才代表相应 Skill 已实际同步。
- 自动流程只读取和复制上游文件，绝不执行上游脚本。外部 Skill 的自动替换可能删除旧的本地定制，历史可由 Git 恢复。
- GitHub Actions 故障会保留候选 PR 并创建故障 Issue，不绕过校验。

仓库的 Agent 维护约定见 [AGENTS.md](./AGENTS.md)，生成器、Actions 触发条件和验证步骤见 [docs/architecture.md](./docs/architecture.md)。
