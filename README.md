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

| Skill | 说明 |
|-------|------|
| skill-blog-writer | 在技术对话结束后，将整个聊天内容整理成一篇结构完整的中文技术博客文章。当用户说"帮我整理成博客"、"生成博客"、"写成文章"、"整理一下"、"出一篇博客"，或者明确说"教程类博客"/"技术解析博客"时，必须立即触发本技能。即使用户只是随口说"总结一下聊天内容"，也应该主动询问是否需要生成博客。博客以中文撰写，技术术语保留英文原文。 |
| skill-creator | Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill's description for better triggering accuracy. |
| skill-iterate | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好。当用户说"优化 skill"、"改进 skill"、"记住这个问题"、"以后不要再这样"、"这个问题每次都出现"、"改进博客 skill"、"改进 llt skill" 时触发。注意：只想修改当前输出（"重新写一下"、"改这里"）时不触发，让原始 skill 处理。 |
| skill-os-setup | 用于维护 EasyNewOS 仓库。当用户提到"更新README"、"修改README"、"扩展EasyNewOS"、"增加脚本"、"添加新内容到EasyNewOS"、"提交到GitHub"、"推送到github"、"按照现有结构扩展"、"按照我的风格"，或对仓库进行任何维护操作时触发。这个仓库用于新系统（Win、macOS、Linux）配置，包含软件安装、系统配置、脚本等。 |
| skill-sync | 管理 Agent Skills 与 GitHub 仓库的双向同步。 |

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
