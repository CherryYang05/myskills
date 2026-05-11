# myskills

个人 Agent Skills 仓库，支持 Claude Code、OpenCode、Codex 等 Agent。

## 第一次安装

将以下提示词粘贴给 Agent，让她自动完成安装：

---

**请帮我安装 skills 仓库：**

~~~text
请执行以下步骤：
1. 运行：git clone https://github.com/CherryYang05/myskills.git ~/.claude/skills
2. 运行：python ~/.claude/skills/skill-sync/scripts/skill_sync.py config
3. 如果提示未配置，请运行：python ~/.claude/skills/skill-sync/scripts/skill_sync.py config set
4. 输入 GitHub Token（如果需要）：YOUR_GITHUB_TOKEN
5. 输入仓库名：CherryYang05/myskills
6. 完成后运行 list-local 验证
~~~

---

## 已收录的 Skills

| Skill | Description |
|-------|-------------|
| [dt-case-enhancer](./dt-case-enhancer) | 使用CodeAgent对已有DT用例进行增强补齐。这是一个通用的skill,指导用户通过思维链(CoT)的方式分步骤对存量DT用例进行分析和增量补充。当用户提到DT用例增强、用例补充、增量用例等关键词时,应使用此skill。**重要*... |
| [dt-case-generator](./dt-case-generator) | 使用CodeAgent生成DT(开发者自测试)用例。这是一个通用的的skill,指导用户通过思维链(CoT)的方式分步骤生成高质量的DT测试用例。当用户提到DT用例生成、测试用例生成、LLT测试等关键词时,应使用此skill。特别适用... |
| [skill-blog-writer](./skill-blog-writer) | 在技术对话结束后，将整个聊天内容整理成一篇结构完整的中文技术博客文章。当用户说"帮我整理成博客"、"生成博客"、"写成文章"、"整理一下"、"出一篇博客"，或者明确说"教程类博客"/"技术解析博客"时，必须立即触发本技能。即使用户只是... |
| [skill-creator](./skill-creator) | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a... |
| [skill-iterate](./skill-iterate) | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好。当用户说"优化 skill"、"改进 skill"、"记住这个问题"、"以后不要再这样"、"这个问题每次都出现"、"改进博客 skill"... |
| [skill-os-setup](./skill-os-setup) | 用于维护 EasyNewOS 仓库。当用户提到"更新README"、"修改README"、"扩展EasyNewOS"、"增加脚本"、"添加新内容到EasyNewOS"、"提交到GitHub"、"推送到github"、"按照现有结构扩展... |
| [skill-sync](./skill-sync) | 管理 Agent Skills 与 GitHub 仓库的双向同步。 |

## 常用同步命令

~~~bash
# 上传本地 skills 到 GitHub
python ~/.claude/skills/skill-sync/scripts/skill_sync.py upload <name>
python ~/.claude/skills/skill-sync/scripts/skill_sync.py do-upload <name>

# 从 GitHub 安装 skills 到本地
python ~/.claude/skills/skill-sync/scripts/skill_sync.py install <name>
python ~/.claude/skills/skill-sync/scripts/skill_sync.py do-install <name>
~~~

## 注意

- git 需已配置（Agent 会提示用户配置）
- 配置文件：`~/.skill-sync-config.json`
