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
| [dt-case-enhancer](./dt-case-enhancer) | 使用CodeAgent对已有DT用例进行增强补齐 |
| [dt-case-generator](./dt-case-generator) | 使用CodeAgent生成DT(开发者自测试)用例 |
| [skill-blog-writer](./skill-blog-writer) | 在技术对话结束后，将整个聊天内容整理成一篇结构完整的中文技术博客文章 |
| [skill-creator](./skill-creator) | Create new skills, modify and improve existing skills, an… |
| [skill-dev-flow](./skill-dev-flow) | 固化 Agent 驱动的完整开发流程——从需求分析、项目初始化（AGENTS.md）、需求拆分（模块/功能/任务）… |
| [skill-iterate](./skill-iterate) | 对其他 skill 的输出进行人工标注驱动的自迭代优化，修改 SKILL.md 让未来输出更好 |
| [skill-os-setup](./skill-os-setup) | 用于维护 EasyNewOS 仓库 |
| [skill-sync](./skill-sync) | 管理 Agent Skills 与 GitHub 仓库的双向同步 |

## 常用同步命令


~~~bash
# 查看状态：本地 vs 仓库差异（只读，不改动任何东西）
python ~/.claude/skills/skill-sync/scripts/skill_sync.py status

# 推送本地 skills 到 GitHub（默认仅预览，加 --apply 才推送）
python ~/.claude/skills/skill-sync/scripts/skill_sync.py push              # 同步全部本地 skill
python ~/.claude/skills/skill-sync/scripts/skill_sync.py push <name> ...   # 仅同步指定 skill
python ~/.claude/skills/skill-sync/scripts/skill_sync.py push --apply      # 确认后执行

# 从 GitHub 拉取到本地（默认仅预览，加 --apply 才写入）
python ~/.claude/skills/skill-sync/scripts/skill_sync.py pull              # 全部
python ~/.claude/skills/skill-sync/scripts/skill_sync.py pull <name> ...   # 指定
python ~/.claude/skills/skill-sync/scripts/skill_sync.py pull --apply      # 确认后执行
~~~

## 注意

- git 需已配置（Agent 会提示用户配置）
- 配置文件：`~/.skill-sync-config.json`
