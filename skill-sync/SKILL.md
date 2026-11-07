---
name: skill-sync
description: 在 Agent 对话中安装、更新 Agent Skills，或同步 skill 源码与 GitHub 仓库。使用 npx skills 管理安装，用原生 git 推送、拉取和查看源码差异，并自动维护仓库 README。当用户说"同步 skill""推送 skill 到 github""把这个 skill 推上去""拉取远端 skill""看看本地和仓库的差别""列出仓库 skills""安装 skills 仓库""更新 skills"时触发。
---

# skill-sync

使用 `npx skills` 安装和更新技能；在 Git 源码工作树中维护技能、生成 README 并推送到 GitHub。安装位置由 CLI 根据所选 Agent 和安装范围管理，不能默认把安装目录当作源码仓库。

默认安装源为 `CherryYang05/myskills`；用户指定其他仓库时，替换为实际的 `owner/repo`。所需环境为 Node.js、npm 和 Git。

## 安装与更新

```bash
# 查看仓库中可安装的 skills
npx skills add CherryYang05/myskills --list

# 全局安装，按提示选择 skill 和 Agent
npx skills add CherryYang05/myskills --global

# 仅安装指定 skill
npx skills add CherryYang05/myskills --skill ds-mr-reviewer --global

# 为 Claude Code 和 OpenCode 安装全部 skills
npx skills add CherryYang05/myskills --skill '*' --agent claude-code opencode --global

# 查看已安装的全局 skills
npx skills list --global

# 更新指定的全局 skill
npx skills update ds-mr-reviewer --global
```

`--skill` 匹配 `SKILL.md` 的 `name` 字段，以 `--list` 显示的名称为准。项目级安装需在目标项目目录中运行 `add` 并去掉 `--global`；更新项目级技能使用 `npx skills update <name> --project`。`npx skills update --global` 会更新 CLI 管理的所有全局 skills，包含其他仓库的技能，仅在用户需要这一范围时使用。

更新或重新安装前，检查目标安装目录是否有用户修改；先保存需要保留的内容。若用户要把安装目录中的修改推回 GitHub，先与源码工作树比较，再将指定 skill 的改动同步到源码中提交。

## 源码同步（原生 git）

下文 `$D` 代表已验证的源码仓库根目录。先查找已有工作树，通过 `git -C "$D" rev-parse --show-toplevel` 和 `git -C "$D" remote -v` 确认路径与远端。若尚未克隆，将仓库克隆到独立开发目录，例如 `~/code/myskills`，再设置 `$D`。已有位于 `~/.claude/skills` 的 Git 工作树可继续作为源码维护；迁移安装方式时先保留本地修改，不要对已有技能目录执行 `git reset --hard`。

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

提交时 pre-commit 钩子会自动刷新 README（在源码工作树中启用一次：`git -C "$D" config core.hooksPath skill-sync/hooks`）；也可手动刷新：`python3 "$D/skill-sync/scripts/gen_readme.py"`。推送后，用 `npx skills update <name> --global` 更新相应的全局安装，项目级安装改用 `--project`。

## Agent 行为准则（重要）

1. **人工推送前确认，并展示内容摘要。** 手动 `git push` 前先 `git -C $D status` 和 `git -C $D diff --cached`（不要只看 `--stat`），在对话中用自然语言总结本次增加/改动/删除了什么实质内容（新增了哪个 skill、改了哪些行为规则、删了哪些文件），而不只是文件名和行数，再等待用户确认。**例外**：用户已授权每周自动上游同步，此固定范围内的受管 Skill 更新（包括必要时全量替换）无须每次单独确认；必须通过来源检查、候选 PR、精确提交 CI 和范围校验后合并。此授权不适用于自研 Skill、仓库配置或其他操作。
2. **拉取覆盖保护。** `git pull` 前先 `git -C $D fetch` + `git -C $D diff HEAD origin/master --stat`，告知用户哪些本地文件会被改动，确认后再 pull。若本地有未提交改动，先提示用户以免冲突丢失。
3. **指定 skill 推送**用 `git add <skill>`，不要 `add -A` 误带无关改动。
4. **不提交敏感信息**（token、密钥）。仓库公开可见。
5. **删除操作同样要摘要。** 删除 skill 或文件（`git rm`、手动删除后 `git add`）时，同样在对话中列出被删除的文件/skill 及删除原因（如用户说明的），再走上面第 1 条的确认流程。

## README 维护

仓库 `README.md` 的安装说明、Skills 表格及更新与维护说明由 `scripts/gen_readme.py` 整体生成。修改说明时编辑脚本模板；新增/删除 skill 后生成表格。脚本中的中文简介覆盖项用于提供完整概括，其余简介取自各 `SKILL.md`。Skills 表格必须包含“来源”和“同步版本”列：本仓库原创内容标记为“自研”，同步版本显示“—”；基于外部 GitHub 仓库引入、翻译、封装或改编的 Skill 标记为带上游链接的“外部参考”，并显示当前仓库实际同步到的上游版本。上游有正式版本号时记录版本号；没有正式版本号时记录对应的上游 commit 短 SHA。Skill 名称必须链接到本仓库对应 Skill 目录。外部来源、同步版本及 GitHub 定时更新策略统一维护在 `upstreams.json` 中；`scripts/gen_readme.py` 将它读取为 `EXTERNAL_SOURCES` 供兼容使用。新增、删除、更换外部上游或同步上游更新时必须同步更新此配置并重新生成 README。不得把“latest”作为同步版本，因为它无法证明仓库内容对应哪个具体上游状态。

运行源码工作树中的脚本；通过 CLI 安装的 `skill-sync` 目录不包含完整仓库，脚本会拒绝在该目录中生成 README。pre-commit 钩子仅在源码工作树中启用。

## 多机安装

在新机器上执行 `npx skills add CherryYang05/myskills --global`，选择需要的技能与 Agent。后续用 `npx skills update <name> --global` 更新已安装的技能；需要开发时另行准备源码工作树。

## GitHub 自动检查上游

源码仓库中的 `.github/workflows/sync-upstream.yml` 每周五北京时间 20:30 执行（无需 GPT 定时任务重复检查原始上游），检查 `upstreams.json`。**所有登记的外部 Skill 必须采用自动实际同步策略**：优先接受无冲突的上游更新；本地改动冲突或无法可靠合并时，以经过核验的上游快照**完整替换**受管目录，包含删除本地独有文件。现有外部 Skill 使用 `replace` 模式，配置校验禁止仅报告的 `review` 模式。完全替换的旧中文/个人定制可从 Git 历史恢复，版本改为上游具体 commit 短 SHA；`last_reported` 不得阻止未合并候选重试。任务创建机器人候选 PR，派发只读完整校验，确认相同提交成功且主分支未前进后自动合并；不会绕过 CI 或合并其他 PR。若平台、权限或校验故障，必须继续重试并主动报告实际阻碍，绝不能把“发现更新”称为成功同步。手动检查用 `python3 scripts/sync_upstream.py`，仅在源码开发分支中添加 `--apply` 生成候选；脚本不会自动提交或推送。根目录 `UPSTREAM_SYNC_REPORT.md` 汇总每次检查及文件修正，逐项报告保留在 `docs/upstream-reports/`，README 和 Marketplace 同步生成。完整说明见源码仓库的 `docs/upstream-sync.md`。

通过 marketplace 安装到本机 Codex 的技能，需单独刷新来源；更新 GitHub 仓库不等于更新 ChatGPT 个人空间手动上传的技能。
