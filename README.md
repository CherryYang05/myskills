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
| [dt-case-enhancer](./dt-case-enhancer) | 对存量 DT 用例进行分析和增量补充 |
| [dt-case-generator](./dt-case-generator) | 基于 CoT 分步骤生成高质量 DT 测试用例 |
| [skill-blog-writer](./skill-blog-writer) | 将技术对话整理成发布级中文博客文章 |
| [skill-creator](./skill-creator) | 创建、修改和评估 Agent Skills |
| [skill-iterate](./skill-iterate) | 人工标注驱动的 Skill 输出质量自迭代优化 |
| [skill-os-setup](./skill-os-setup) | 维护 EasyNewOS 新系统配置仓库 |
| [skill-sync](./skill-sync) | Skills 与 GitHub 仓库双向同步 |

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
