# myskills

统一管理第三方与自研 Agent Skills，自动同步上游，并向 ChatGPT、Claude Code、Cursor 和 Skills CLI 分发。

[![Validate Skills](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/validate-skills.yml) [![Sync Skill Upstreams](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml/badge.svg?branch=master)](https://github.com/CherryYang05/myskills/actions/workflows/sync-upstream.yml)

## Skill 清单

| Skill | 类型 | 来源 / 当前版本 | 说明 |
|---|---|---|---|
| [caveman](./skills/external/caveman) | 外&#8288;部&#8288;同&#8288;步 | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman/tree/main/skills/caveman) · `3dc497a7f858` | Terse caveman voice: answer first, fluff gone, every technical fact kept |
| [deep-research](./skills/external/deep-research) | 外&#8288;部&#8288;同&#8288;步 | [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills/tree/main/deep-research) · `6d9388674de1` | Universal deep research agent team |
| [design-taste-frontend](./skills/external/design-taste-frontend) | 外&#8288;部&#8288;同&#8288;步 | [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill/tree/main/skills/taste-skill) · `f6b76575f949` | tasteskill 2.5.1, the anti-slop frontend skill |
| [frontend-design](./skills/external/frontend-design) | 外&#8288;部&#8288;同&#8288;步 | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/frontend-design) · `ca45fc496a34` | Guidance for distinctive, intentional visual design when building new UI or reshaping an… |
| [gsap-core](./skills/external/gsap-core) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-core) · `aed9cfd32777` | Official GSAP skill for the core API — gsap.to(), from(), fromTo(), easing, duration… |
| [gsap-frameworks](./skills/external/gsap-frameworks) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-frameworks) · `aed9cfd32777` | Official GSAP skill for Vue, Svelte, and other non-React frameworks — lifecycle, scoping… |
| [gsap-performance](./skills/external/gsap-performance) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-performance) · `aed9cfd32777` | Official GSAP skill for performance — prefer transforms, avoid layout thrashing… |
| [gsap-plugins](./skills/external/gsap-plugins) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-plugins) · `aed9cfd32777` | Official GSAP skill for GSAP plugins — registration, ScrollToPlugin, ScrollSmoother… |
| [gsap-react](./skills/external/gsap-react) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-react) · `aed9cfd32777` | Official GSAP skill for React — useGSAP hook, refs, gsap.context(), cleanup |
| [gsap-scrolltrigger](./skills/external/gsap-scrolltrigger) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-scrolltrigger) · `aed9cfd32777` | Official GSAP skill for ScrollTrigger — scroll-linked animations, pinning, scrub… |
| [gsap-timeline](./skills/external/gsap-timeline) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-timeline) · `aed9cfd32777` | Official GSAP skill for timelines — gsap.timeline(), position parameter, nesting… |
| [gsap-utils](./skills/external/gsap-utils) | 外&#8288;部&#8288;同&#8288;步 | [greensock/gsap-skills](https://github.com/greensock/gsap-skills/tree/main/skills/gsap-utils) · `aed9cfd32777` | Official GSAP skill for gsap.utils — clamp, mapRange, normalize, interpolate, random… |
| [humanizer](./skills/external/humanizer) | 外&#8288;部&#8288;同&#8288;步 | [blader/humanizer](https://github.com/blader/humanizer) · `0ef9fe5bc357` | Rewrite AI-sounding text so it reads like the writer without changing what it says |
| [impeccable](./skills/external/impeccable) | 外&#8288;部&#8288;同&#8288;步 | [pbakaus/impeccable](https://github.com/pbakaus/impeccable/tree/main/.agents/skills/impeccable) · `b3ced85312e9` | Use when the user wants to design, redesign, shape, critique, audit, polish, simplify… |
| [mermaid-diagrams](./skills/external/mermaid-diagrams) | 外&#8288;部&#8288;同&#8288;步 | [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit/tree/main/skills/mermaid-diagrams) · `3027f20f3181` | Comprehensive guide for creating software diagrams using Mermaid syntax |
| [playwright](./skills/external/playwright) | 外&#8288;部&#8288;同&#8288;步 | [openai/skills](https://github.com/openai/skills/tree/main/skills/.curated/playwright) · `49f948faa925` | Use when the task requires automating a real browser from the terminal (navigation, form… |
| [shadcn](./skills/external/shadcn) | 外&#8288;部&#8288;同&#8288;步 | [shadcn-ui/ui](https://github.com/shadcn-ui/ui/tree/main/skills/shadcn) · `42f3bb63b46a` | Manages shadcn components and projects — adding, searching, fixing, debugging, styling… |
| [skill-creator](./skills/external/skill-creator) | 外&#8288;部&#8288;同&#8288;步 | [anthropics/skills](https://github.com/anthropics/skills/tree/main/skills/skill-creator) · `b9e19e6f4477` | Create new skills, modify and improve existing skills, and measure skill performance |
| [web-design-guidelines](./skills/external/web-design-guidelines) | 外&#8288;部&#8288;同&#8288;步 | [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills/tree/main/skills/web-design-guidelines) · `1a2c79d4e6c4` | Review UI code for Web Interface Guidelines compliance |
| [ds-mr-reviewer](./skills/personal/ds-mr-reviewer) | 自研 | 自研 | MR代码检视工具 |
| [dt-case-enhancer](./skills/personal/dt-case-enhancer) | 自研 | 自研 | 使用CodeAgent对已有DT用例进行增强补齐 |
| [dt-case-generator](./skills/personal/dt-case-generator) | 自研 | 自研 | 使用CodeAgent生成DT(开发者自测试)用例 |
| [humanizer-en](./skills/personal/humanizer-en) | 自研 | 自研 | Edit or review existing English prose when asked to humanize it, remove AI tone, or… |
| [humanizer-zh](./skills/personal/humanizer-zh) | 自研 | 自研 | 编辑或审阅已有的中文稿件 |
| [blog-writer](./skills/personal/skill-blog-writer) | 自研 | 自研 | 将技术对话整理为结构完整、可独立阅读的中文技术文章 |
| [skill-dev-flow](./skills/personal/skill-dev-flow) | 自研 | 自研 | 固化 Agent 驱动的完整开发流程——从需求分析、项目初始化（AGENTS.md）、需求拆分（模块/功能/任务），到逐个功能的设计文档、实现、收尾归档 |
| [skill-dev-sop](./skills/personal/skill-dev-sop) | 自研 | 自研 | 固化 Agent 驱动的通用软件开发标准流程——需求分析、系统设计（架构总览/模块边界/依赖方向）、项目初始化（AGENTS.md）、模块与任务拆分、逐个功能的设计文档（含耦合… |
| [skill-iterate](./skills/personal/skill-iterate) | 自研 | 自研 | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好 |
| [skill-os-setup](./skills/personal/skill-os-setup) | 自研 | 自研 | 用于维护 EasyNewOS 仓库 |

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

## 新增 Skill 的自动生成流程

1. 在 `automation/upstreams.json` 登记经过来源、许可和安全审查的上游 Skill，使用完整的 Git commit SHA；如许可证位于仓库根目录，填写 `root_license: "LICENSE"`（实际为 JSON 键 `"root_license": "LICENSE"`）。
2. 在 `automation/plugin-appearance.json` 为对应的 **Skill 名称**设置专属颜色、SVG `glyph` 与概念说明。Actions 负责将这些矢量源数据渲染成统一的 128×128 图标，不会自动创作图形。
3. 推送到 `master` 后，`Sync Skill Upstreams` 的 Push 触发器会拉取缺失的第三方 Skill、做静态安全/许可证检查、生成 Plugin/Marketplace/README 与版本号，并创建候选 PR。
4. 只有候选 PR 的**精确提交**通过 `Validate Skills` 后才会自动合并。第一次登记但未生成时，短暂的主分支验证失败属于引导阶段状态；如 Action 受账户权限/计费限制未运行，不能认为导入完成，需查看 Workflow/PR 结果。

新增或移除上游的注册表修改必须经过人工/Agent 明确审查和提交；自动流程不会自行发现、添加来源。每周五的同步仍仅更新已经登记的来源。

## 仓库维护

- `skills/external/` 保存第三方 Skill 的完整上游快照，来源与固定提交记录在 `automation/upstreams.json`；`skills/personal/` 保存自研 Skill，不受上游同步覆盖。
- `plugins/`、三个平台的 Marketplace、`skills.sh.json`、本 README 均由 `automation/scripts/generate.py` 生成。README 正文编辑 `automation/templates/README.md.tpl`；SVG 图标编辑 `automation/plugin-appearance.json`。**不要直接修改生成物**。
- 每周五北京时间 20:30，GitHub Actions 检查上游；有变动才创建候选 PR，通过 CI 后自动合并。无变化的检查结果留在 Action Summary / Artifact；最近一次实际同步记录见 [UPSTREAM_SYNC_REPORT.md](./UPSTREAM_SYNC_REPORT.md)。
- GitHub 生成与合并成功不保证客户端已刷新。安装和更新结果须在目标客户端核验。

新增第三方 Skill 时，直接提供 GitHub 链接并要求加入仓库即可。来源与许可证审查、代码安全检查、专属图标设计、生成和 CI 的强制要求都集中在 [AGENTS.md](./AGENTS.md)。完整历史可从 Git 提交追溯。
