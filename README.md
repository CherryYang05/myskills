# myskills

> 个人 Agent Skills 仓库，通过 [skills CLI](https://github.com/vercel-labs/skills) 安装和更新，可按需选择技能及 Claude Code、OpenCode 等 Agent。

## 一、安装

准备好 Node.js、npm 和 Git，在终端运行：

```bash
npx skills add CherryYang05/myskills --global
```

按提示选择要安装的 skill 和使用的 Agent。`--global` 表示用户级安装，可跨项目使用；去掉该参数则安装到当前项目。

常用安装方式：

```bash
# 查看仓库中可安装的 skills
npx skills add CherryYang05/myskills --list

# 只安装 MR 代码检视 skill
npx skills add CherryYang05/myskills --skill ds-mr-reviewer --global

# 只安装 humanizer
npx skills add CherryYang05/myskills --skill humanizer --global

# 为 Claude Code 和 OpenCode 安装仓库中的全部 skills
npx skills add CherryYang05/myskills --skill '*' --agent claude-code opencode --global
```

`--skill` 使用各 `SKILL.md` 的 `name` 字段，可能与文件夹名称不同；请以 `--list` 显示的名称为准。安装位置由 CLI 根据所选 Agent 和安装范围管理，完成后会显示实际路径。

## 二、已收录的 Skills

| Skill | 简介 |
|-------|------|
| [deep-research](./deep-research) | 由 14 个专业 Agent 组成的通用深度研究流水线，支持文献综述、事实查核、论文评审、系统性综述等 8 种研究模式 |
| [ds-mr-reviewer](./ds-mr-reviewer) | MR代码检视工具 |
| [dt-case-enhancer](./dt-case-enhancer) | 使用CodeAgent对已有DT用例进行增强补齐 |
| [dt-case-generator](./dt-case-generator) | 使用CodeAgent生成DT(开发者自测试)用例 |
| [humanizer](./humanizer) | 识别并改写夸张措辞、空泛表达、重复句式和多余套话，在保留原意、事实与作者风格的基础上减少 AI 写作痕迹，让文字自然、清晰。 |
| [skill-blog-writer](./skill-blog-writer) | 将技术对话整理为结构完整、可独立阅读的中文技术文章 |
| [skill-creator](./skill-creator) | 创建、改进和评测 Agent Skills，优化技能的执行效果与触发准确性。 |
| [skill-dev-flow](./skill-dev-flow) | 固化 Agent 驱动的完整开发流程 |
| [skill-dev-sop](./skill-dev-sop) | 固化 Agent 驱动的通用软件开发标准流程 |
| [skill-iterate](./skill-iterate) | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好 |
| [skill-os-setup](./skill-os-setup) | 用于维护 EasyNewOS 仓库 |
| [skill-sync](./skill-sync) | 在 Agent 对话中安装、更新 Agent Skills，或同步 skill 源码与 GitHub 仓库 |

## 三、更新与管理

```bash
# 查看已安装的全局 skills
npx skills list --global

# 更新已安装的 humanizer
npx skills update humanizer --global

# 更新 CLI 管理的全部全局 skills（包含其他仓库的 skills）
npx skills update --global
```

更新当前项目的 skills 时，进入项目目录并使用 `npx skills update --project`。若在安装目录中改过 skill，更新前先保存这些改动；需要长期维护的修改应提交到源码仓库。

## 四、维护仓库

需要新增或修改 skill 时，在独立的 Git 工作树中维护源码，例如：

```bash
git clone https://github.com/CherryYang05/myskills.git ~/code/myskills
cd ~/code/myskills
git config core.hooksPath skill-sync/hooks
```

已有源码工作树可以继续使用。源码通过 `git add`、`git commit`、`git push` 推送，拉取远端修改使用 `git pull`；提交后再用 `npx skills update` 更新本机已安装的技能。

- 本 README 由 `skill-sync/scripts/gen_readme.py` 整体生成。修改安装说明请编辑脚本模板；技能简介优先使用脚本中的中文概括，其余取自各 `SKILL.md`。
- 在源码仓库中运行 `python3 skill-sync/scripts/gen_readme.py` 可手动刷新 README；启用上述 pre-commit 钩子后，每次提交会自动刷新。
- 切勿把 token、密钥等敏感信息提交进任何 skill；本仓库公开可见。
- 完整安装、同步命令与 Agent 行为约定见 [skill-sync](./skill-sync) 的 SKILL.md。
