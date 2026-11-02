# GitHub 上游同步

GitHub Actions 每周五北京时间 21:00（UTC 13:00）运行 **Sync Skill Upstreams**，直接读取 `skill-sync/upstreams.json`。README 的来源和同步版本也读取这份配置，不解析 Markdown 表格、不维护第二份来源映射。

| 技能 | 策略 | 管理范围 |
|---|---|---|
| humanizer | mirror：生成同步候选 PR | 上游根目录的 SKILL.md |
| skill-creator | mirror：生成同步候选 PR | 上游 skills/skill-creator 整个目录，包含可执行权限 |
| deep-research | review：仅生成差异报告 | 上游 deep-research 目录；保留本仓库中文定制和同步版本 |

工作流只生成 PR，不自动合并。先检查文件变化和校验结果，再合并到 master。

## 首次启用

1. 将此工作流及脚本合并到默认分支 master；定时任务只会在默认分支运行。
2. 打开仓库 **Settings → Actions → General**，确认 Actions 已启用，并允许 **Allow GitHub Actions to create and approve pull requests**。工作流只申请创建 PR 所需的 contents: write 和 pull-requests: write，不调用 PR 审批或自动合并。
3. 打开 **Actions → Sync Skill Upstreams → Run workflow**。保持 dry_run 为 false 生成候选 PR；勾选则只检查并提供报告，不写来源文件或创建 PR。
4. 查看运行日志和 **upstream-sync-report**（或 **upstream-preview**）附件。没有新内容时不创建 PR；有候选时，运行摘要提供 PR 链接。

使用内置 GITHUB_TOKEN，不要求个人令牌或 API 密钥。GitHub 使用它创建的 PR，其 CI 可能需要点击 **Approve workflows to run**；不要把未启动的校验当作通过。仓库如果长期没有活动，GitHub 可能停用公开仓库的定时任务；可在 Actions 中重新启用。定时运行也可能延迟，不是准点执行保证。

## 配置字段

每个键是本地技能目录名。`url` 是 README 来源链接，`version` 是实际同步基线；`selected_fixes` 保留人工选择性移植记录。

`sync` 配置：

- `repository`：上游 owner/repo，仅接受 GitHub 仓库。
- `path`：技能在上游的目录，空字符串表示仓库根目录。
- `ref`：跟踪分支或明确指定的 Git ref。
- `mode`：mirror 或 review。
- `files`：可选的明确文件白名单；没有此字段则管理整个技能目录。
- `synced_commit`：mirror 必须提供完整的已同步 commit SHA，作为保护本地定制的比较基线。不要填写上游最新 SHA 冒充已同步。
- `last_reported`：脚本维护的本地/上游内容指纹，仅用于避免重复报告，不代表已经同步。

新增外部技能时，先登记为 review 并核查范围。只有确认本地管理范围与某个上游提交一致后，才配置 mirror 和 synced_commit。

## 更新和保护逻辑

检查按文件内容及可执行权限进行。上游项目发 Release，或跟踪分支出现无关目录提交，不会单独触发技能更新。

mirror 更新前，本地管理范围必须仍与 synced_commit 的文件和权限一致。出现本地定制或技能 name 变化时，生成 blocked 报告，保留技能内容和版本。review 模式始终保留源文件，只更新报告及 last_reported。

mirror 候选将本次完整上游 commit 记录到 synced_commit，并将 README 同步版本更新为可追溯的 commit 短 SHA，不根据项目 Release 或可能过期的技能 metadata 推断版本。报告记录候选提交及文件列表；只有 PR 合并后才是主分支的新基线。

脚本先获取并验证所有来源，再准备改动。获取失败、文件缺失、异常 frontmatter、符号链接或子模块会使运行失败，不发布部分结果。读取上游文件不会执行上游脚本；自动任务使用本仓库同步代码与生成器。CI 在 PR 中另行校验候选。

同一候选 diff 使用固定的 automation/upstream-* 分支；已有对应 PR（包括已关闭的 PR）时不重复创建。工作流不强制推送、不覆盖用户编辑的远端分支。若关闭 PR 表示暂不采纳相同更新，未来相同候选不会反复打开。

已合并的报告位于 docs/upstream-reports/。deep-research 报告合并仅记录“已报告”，不代表移植完成；移植仍需审查上游变更、保留中文规则并正确维护同步基线。

## 本地检查

```bash
python3 -m pip install pyyaml
python3 skill-sync/scripts/sync_upstream.py --validate-config
python3 -m unittest discover -s skill-sync/tests -v
# 默认只读检查
python3 skill-sync/scripts/sync_upstream.py --report /tmp/upstream-report.json
# 仅在干净的源码开发分支生成候选，不提交、不推送
python3 skill-sync/scripts/sync_upstream.py --apply
python3 skill-sync/scripts/gen_readme.py
python3 skill-sync/scripts/gen_marketplace.py
```

## 与本机 Codex 的关系

GitHub 上游检查 → 更新 PR → 合并 master → 本机 Codex 刷新 GitHub 来源，这是不同步骤。本工作流不直接更新你的电脑或个人空间中上传的技能。

本机 marketplace 必须跟踪 master，才能接收主分支合并的更新。随后可使用 `codex plugin marketplace upgrade cherry-myskills` 刷新来源。只跟踪旧 PR 分支时，不会收到 master 的新提交；本机每日自动刷新需另行设置。

## 官方参考

- [GitHub 定时工作流](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [Actions 的 PR 创建权限](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [GITHUB_TOKEN 触发工作流的行为](https://docs.github.com/en/actions/concepts/security/github_token)
