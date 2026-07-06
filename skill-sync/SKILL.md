---
name: skill-sync
description: 在 Agent 对话中同步本地 Agent Skills 与 GitHub 仓库。~/.claude/skills 本身是 git 工作树，用原生 git 推送/拉取/查看差异，并自动维护仓库 README。当用户说"同步 skill""推送 skill 到 github""把这个 skill 推上去""拉取远端 skill""看看本地和仓库的差别""列出仓库 skills""安装 skills 仓库"时触发。
---

# skill-sync

`~/.claude/skills` 是 GitHub 仓库的 **git 工作树**，多机之间用**原生 git** 同步。Claude Code 与 OpenCode 都直接读取该目录，一份源两个工具共用。

**本 skill 不封装同步逻辑**——同步就是几条 git 命令，由 Agent 直接执行；唯一的脚本 `scripts/gen_readme.py` 只做 git 不做的事（生成仓库 README）。

约定：下文 `$D` 代表 skills 目录（Claude Code 默认 `~/.claude/skills`，即本仓库根）。

## 同步命令（原生 git）

```bash
# 看本地未提交的改动
git -C $D status

# 看本地与远端差异（远端领先了哪些 / 即将拉到什么）
git -C $D fetch && git -C $D log --oneline HEAD..origin/master

# 推送：全部改动
git -C $D add -A && git -C $D commit -m "更新 skills" && git -C $D push

# 推送：仅某个 skill（不误带其他改动）
git -C $D add <skill> && git -C $D commit -m "更新 <skill>" && git -C $D push

# 拉取：先看会变什么，确认后再拉
git -C $D fetch && git -C $D diff HEAD origin/master --stat
git -C $D pull

# 列出已收录的 skills（或直接看仓库 README 表格）
ls $D
```

提交时 pre-commit 钩子会自动刷新 README（启用一次：`git -C $D config core.hooksPath skill-sync/hooks`）；也可手动刷新：`python $D/skill-sync/scripts/gen_readme.py`。

## Agent 行为准则（重要）

1. **推送前确认，并展示内容摘要。** `git push` 前先 `git -C $D status` 和 `git -C $D diff --cached`（不要只看 `--stat`），在对话中用自然语言总结本次增加/改动/删除了什么实质内容（新增了哪个 skill、改了哪些行为规则、删了哪些文件），而不只是文件名和行数，再等待用户确认。
2. **拉取覆盖保护。** `git pull` 前先 `git -C $D fetch` + `git -C $D diff HEAD origin/master --stat`，告知用户哪些本地文件会被改动，确认后再 pull。若本地有未提交改动，先提示用户以免冲突丢失。
3. **指定 skill 推送**用 `git add <skill>`，不要 `add -A` 误带无关改动。
4. **不提交敏感信息**（token、密钥）。仓库公开可见。
5. **删除操作同样要摘要。** 删除 skill 或文件（`git rm`、手动删除后 `git add`）时，同样在对话中列出被删除的文件/skill 及删除原因（如用户说明的），再走上面第 1 条的确认流程。

## README 维护

仓库 `README.md` 三段（安装提示词 / Skills 表格 / 注意事项）由 `scripts/gen_readme.py` 生成，pre-commit 钩子自动调用，无需手改。新增/删除 skill 后提交时表格会自动更新。

## 多机安装

把仓库 `README.md` 第一段「安装」的提示词发给新机器上的 Agent 即可——它会把仓库设为该机 `~/.claude/skills` 的工作树并启用钩子。OpenCode 无需额外配置（它会自动识别 `~/.claude/skills`）。
