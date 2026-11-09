# 候选 Agent Skills 调研清单

> 核查日期：2026-11-10。**执行状态**：Caveman、Taste、Playwright 与 GSAP 官方 8 个子 Skill 已通过 [PR #33](https://github.com/CherryYang05/myskills/pull/33) 导入本仓库（共 11 项）；Hypit 仍是候选，**没有导入**。导入 GitHub 仓库不代表已安装到本地 Codex 或 ChatGPT。Star 数为调研时近似值。安全校验为静态检查，不能保证上游代码绝对安全。

## 当前状态与建议

- **已引入**：`caveman`、`design-taste-frontend`、`playwright`、`gsap-core`、`gsap-timeline`、`gsap-scrolltrigger`、`gsap-plugins`、`gsap-utils`、`gsap-react`、`gsap-performance`、`gsap-frameworks`。完整源码位于 `skills/external/`，可分发插件位于 `plugins/`，许可证和 SVG 图标随包提供。
- **仅候选**：Hypit。其内容未进入上游注册表、Plugin 或自动同步。
- **验证**：[PR #33](https://github.com/CherryYang05/myskills/pull/33) 已通过精确提交验证并合并。首次引入后，后续更新由原每周同步机制管理。
- **本地 Codex 安装示例**：

  ```bash
  npx skills add CherryYang05/myskills -s caveman -a codex -g -y
  npx skills add CherryYang05/myskills -s design-taste-frontend -a codex -g -y
  npx skills add CherryYang05/myskills -s playwright -a codex -g -y
  npx skills add CherryYang05/myskills -s gsap-core -a codex -g -y
  ```


以当前仓库已有的 [frontend-design](./skills/external/frontend-design)、[impeccable](./skills/external/impeccable)、[shadcn](./skills/external/shadcn)、[web-design-guidelines](./skills/external/web-design-guidelines) 为参照，推荐顺序为：

1. **Playwright（优先评估）**：补足实际浏览器操作、回归验证、页面截图的执行能力，与现有设计类 Skills 互补。
2. **Taste（优先试用）**：为新页面提供视觉方向和成稿自检；与 frontend-design/impeccable 有重叠，应在同一页面任务上做 A/B 验证后再决定长期共存。
3. **GSAP AI Skills（按需引入）**：做复杂页面时间轴、滚动触发效果时有价值；普通 TODO/后台界面不必为动效增加依赖。
4. **Caveman（暂缓）**：输出压缩和日志/输入压缩是不同机制；需实测总 Token、正确率、返工成本，避免损害复杂排障与知识学习质量。
5. **Hypit（收藏观察）**：面向视频生产，暂时偏离本仓库日常软件开发需求；有第三方生成服务成本和非标准许可。

## 候选条目

### 1. Caveman — 简短输出及上下文压缩

- **官方来源**：[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)；约 **11.9 万 Stars**（仓库，非单个 Skill）。
- **能力**：简短输出模式（`caveman`、`ultracave`、`megacave`）；完整产品另外包含输入文件压缩、模型/推理强度选择等模块。只安装 Skill 不等于启用完整 CLI/代理能力。
- **视频核验**：`63 → 20 tokens` 为一段示例回复的比较，无法推导每次任务节省 65% 的总 Token；其输入压缩测试也明确存在对不同文件类型收益不一、部分样本结果更差的情况。
- **许可**：仓库 3.0.0 及以后以 Apache-2.0 发布，早期版本许可不同；云服务另行处理。见 [LICENSING.md](https://github.com/JuliusBrussee/caveman/blob/main/LICENSING.md)。
- **仅安装简短输出 Skill（按需）**：

  ```bash
  npx skills add JuliusBrussee/caveman --skill caveman -a codex -g
  ```

- **评估重点**：相同复杂修复任务的整体输入/输出 Token、正确率、遗漏的风险告警和二次追问成本；不建议为个人学习对话长期强制极简模式。

### 2. Taste — 前端设计方向及真实浏览器检查

- **官方来源**：[Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill)；约 **11.2 万 Stars**。
- **能力**：从对 247 个参考站点的研究中生成 20 种设计路线，选择视觉结构、字体、色彩、图片；在多种视口宽度进行浏览器检查并迭代。其设计产出仍需要根据功能信息架构、可访问性和产品真实性人工判断。
- **许可/依赖**：仓库 MIT；需要 Node.js 22+ 和 Chrome/Edge/Chromium；可选 FFmpeg；获取素材/字体可能访问网络。参考 [官方说明](https://www.tasteskill.dev/docs)。
- **安装（指定 Skill，避免仓库其他命名导致歧义）**：

  ```bash
  npx skills add Leonxlnx/taste-skill --skill design-taste-frontend -a codex -g
  ```

- **推荐场景**：Daily Planner、个人项目展示页、产品 Landing Page。与现有 impeccable 做对照实验，比较产出质量、耗时、浏览器迭代次数、Token 成本。

### 3. Playwright — 真实浏览器自动化

- **Skill 来源**：[openai/skills → .curated/playwright](https://github.com/openai/skills/blob/main/skills/.curated/playwright/SKILL.md)。
- **框架来源**：[microsoft/playwright](https://github.com/microsoft/playwright)；约 **10 万 Stars** 属于微软的自动化框架，**不能记作 OpenAI Playwright Skill 的 Stars**。
- **能力**：通过 Playwright CLI 执行导航、DOM 快照、点击/输入、表单、截图、tracing、数据提取和 UI 流程排障。Skill 中明确要求先取得 snapshot，再以当前元素引用操作。
- **许可/依赖**：Playwright 核心框架 Apache-2.0；Skill 位于 OpenAI curated 目录，正式复制/再分发前仍需检查该 Skill 文件夹的单独 LICENSE；需要 Node/npm (`npx`) 与可运行的浏览器环境。
- **安装**：

  ```bash
  npx skills add https://github.com/openai/skills --skill playwright -a codex -g
  ```

- **推荐场景**：对本地站点执行端到端冒烟测试、截图审查及可复现的交互回归。外部网站访问要遵守权限、服务条款和速率限制，涉及登录/提交操作时另行确认。

### 4. GSAP AI Skills — 网页动画与 ScrollTrigger

- **官方来源**：[greensock/gsap-skills](https://github.com/greensock/gsap-skills)；约 **1.8 万 Stars**。
- **能力**：多项专用 Skill，涵盖 GSAP 核心 API、timeline、ScrollTrigger、插件、框架集成与性能。它们指导 AI 编写动画代码，实际项目仍需安装 `gsap` 依赖并实现。
- **许可**：Skills 仓库 MIT；GSAP 官方说明目前所有插件均免费提供，包括商业使用。需要分别遵循 Skills 仓库与 GSAP 软件本身的使用条款。
- **安装（可先选一项）**：

  ```bash
  npx skills add greensock/gsap-skills --skill gsap-scrolltrigger -a codex -g
  # 项目代码实际使用时另行安装：
  npm install gsap
  ```

- **推荐场景**：个人博客的滚动叙事、产品展示动画；核心规划系统须以可用性、响应速度、减弱动画偏好（prefers-reduced-motion）优先。

### 5. Hypit — 视频分析、编辑与批量变体

- **官方来源**：[hypit-ai/hypit](https://github.com/hypit-ai/hypit)；约 **2.9 万 Stars**。
- **能力**：从参考视频或文字说明形成可编辑的视频生产流程，处理字幕、B-roll、图形、动效与变体。Skill 提供制作知识，执行另需 Hypit 可执行程序和运行环境。
- **许可**：采用 [Hypit 自定义修改版 Apache-2.0 许可](https://github.com/hypit-ai/hypit/blob/main/LICENSE)。内部/自用商业工作通常允许，但面向第三方的多租户托管、商业再分发等需要商业授权；作者主张用户拥有生成结果，第三方模型和素材仍受各自条款约束。
- **成本**：Skill/Hypit 可免费使用；外部 AI 模型、视频生成与服务可能收费。
- **安装**：

  ```bash
  npx skills add hypit-ai/hypit -a codex -g
  ```

- **风险**：引用爆款视频时须核对素材版权、肖像及声音授权，不应把“复刻工作流”理解为可不受限制地复制他人视频。

## 引入策略与维护

- **状态**：前四个项目已引入 GitHub 仓库（GSAP 拆成 8 个子 Skill），Hypit 未引入。上游版本、图标和生成包由自动工作流维护。
- **评估规则**：在隔离项目先审查 `SKILL.md`、脚本、依赖与权限，再安装试用；比较有/无 Skill 的真实任务产出，避免用 Stars 或营销节省比例替代评估。
- **正式引入**：按 [AGENTS.md](./AGENTS.md) 固定源 SHA、核对完整许可、静态审查脚本、加入规范图标和 CI 验证，再合入主分支。
- **关于“Codex 搜不到”**：技能仓库不一定进入 Codex 内置目录。安装前确认 Node/npm；可使用上述 `npx skills add ... -a codex` 指向明确 GitHub 仓库和 Skill 名，完成后用 `npx skills ls -g` 检查并重新开启 Codex 会话。仓库记录与客户端实际安装状态分别核验。

## 参考资料

- Caveman：[官方仓库](https://github.com/JuliusBrussee/caveman)、[许可说明](https://github.com/JuliusBrussee/caveman/blob/main/LICENSING.md)
- Taste：[官方仓库](https://github.com/Leonxlnx/taste-skill)、[文档](https://www.tasteskill.dev/docs)
- Playwright：[OpenAI Skill](https://github.com/openai/skills/blob/main/skills/.curated/playwright/SKILL.md)、[微软框架](https://github.com/microsoft/playwright)
- GSAP：[官方 Skills](https://github.com/greensock/gsap-skills)
- Hypit：[官方仓库](https://github.com/hypit-ai/hypit)、[许可](https://github.com/hypit-ai/hypit/blob/main/LICENSE)
