# myskills

> 个人 Agent Skills 仓库，多机同步。`~/.claude/skills` 本身是本仓库的 git 工作树；Claude Code 与 OpenCode 都直接读取该目录，一份源两个工具共用。

## 一、安装（交给 Agent）

把下面整段发给你的 Agent，它会自动完成安装：

```text
请帮我安装 skills 仓库 CherryYang05/myskills（它会成为我本机 ~/.claude/skills 的 git 工作树）：
1. 若 ~/.claude/skills 已存在且非空：进入该目录依次执行
   git init && git remote add origin https://github.com/CherryYang05/myskills.git
   && git fetch origin && git reset --hard origin/master
   && git branch --set-upstream-to=origin/master master
   若不存在：直接 git clone https://github.com/CherryYang05/myskills.git ~/.claude/skills
2. 启用 README 自动生成钩子：git -C ~/.claude/skills config core.hooksPath skill-sync/hooks
3. 运行 git -C ~/.claude/skills status 验证
（OpenCode 用户无需额外配置：OpenCode 会自动识别 ~/.claude/skills）
```

## 二、已收录的 Skills

| Skill | Description |
|-------|-------------|
| [deep-research](./deep-research) | 通用深度研究 Agent 团队 |
| [dt-case-enhancer](./dt-case-enhancer) | 使用CodeAgent对已有DT用例进行增强补齐 |
| [dt-case-generator](./dt-case-generator) | 使用CodeAgent生成DT(开发者自测试)用例 |
| [skill-blog-writer](./skill-blog-writer) | 将技术对话整理为结构完整、可独立阅读的中文技术文章 |
| [skill-creator](./skill-creator) | Create new skills, modify and improve existing skills, and… |
| [skill-dev-flow](./skill-dev-flow) | 固化 Agent 驱动的完整开发流程 |
| [skill-dev-sop](./skill-dev-sop) | 固化 Agent 驱动的通用软件开发标准流程 |
| [skill-iterate](./skill-iterate) | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好 |
| [skill-os-setup](./skill-os-setup) | 用于维护 EasyNewOS 仓库 |
| [skill-sync](./skill-sync) | 在 Agent 对话中同步本地 Agent Skills 与 GitHub 仓库 |

## 三、注意事项

- **同步即原生 git**：改完某 skill 后 `git add <skill> && git commit -m "…" && git push`；拉取用 `git pull`（覆盖本地前先 `git fetch && git diff HEAD origin/master` 确认）。
- 本 README 的表格由 `skill-sync/scripts/gen_readme.py` 自动生成（pre-commit 钩子每次提交时刷新），**请勿手改表格**。
- 切勿把 token、密钥等敏感信息提交进任何 skill；本仓库公开可见。
- 完整同步命令与 Agent 行为约定见 [skill-sync](./skill-sync) 的 SKILL.md。
