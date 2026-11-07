# GitHub 上游同步：更新优先，必要时全量替换

GitHub Actions **Sync Skill Upstreams** 每周五北京时间 20:30（UTC 12:30）执行，从 `skill-sync/upstreams.json` 读取所有外部来源配置；未登记的自研 Skill 不参与同步。README 的「来源」「同步版本」也只读取这份配置。**一次正常检查若发现上游管理范围内有文件或权限差异，必须生成可自动合并的真实更新候选；仅生成“需要人工审查”的报告不算完成同步。**

## 自动更新策略

- 仓库现有 8 个外部 Skill 均设为 `sync.mode=replace`，以后新增外部 Skill 也使用 `replace`。配置验证会拒绝 `review`（只报告不更新）模式，避免无意停滞。
- `replace` 逐文件按上游跟踪 ref 的**已解析完整 commit**替换技能包，并同步添加、删除、权限更改；包括原本翻译、个性化定制及本地独有文件。原内容可通过 Git 历史恢复，但不继续保存在更新后的技能目录中。**例外：**经配置登记的 LICENSE/NOTICE 法律声明必须保留，且自动 PR 不得修改它们。请勿在受控目录内放私密文件。
- `mirror` 为历史兼容策略。若本地完全等于已同步基线，则直接同步；若有本地定制且上游真的发生变化，也回退到完整上游替换；若上游未变而只有本地变化，则保持本地不动。
- 上游技能变更名称时也准备替换候选，随后通过 Marketplace 唯一性校验阻止非法或重复名称进入默认分支。
- 脚本不执行从上游获取的脚本。先完整获取、限定路径、大小、symlink/submodule 和 frontmatter 格式，再准备变更。标记新版只可使用该次快照 commit 的短 SHA，完整 `synced_commit` 保存于配置；绝不凭无关的项目 Release 伪造技能版本。
- 完整替换后删除旧的 `selected_fixes`、`reviewed_commit` 等定制/审查标记，避免误称本地差异仍有效。**包括 deep-research 的中文修改也会被覆盖，这是用户明确选择的升级优先策略。**

如果同一候选曾因验证或合并失败而没有进入默认分支，下一次检查**仍须重试**：`last_reported` 只能去重报告，不能跳过实际文件更新。

## 提交、验证和失败处理

1. 获取所有上游快照并计算文件/权限变化；生成候选文件、配置版本、README 和 Marketplace。
2. 仅添加受管辖 Skill 文件及衍生报告，推送机器人候选分支和 PR。
3. 单独启动候选 head SHA 对应的只读 **Validate Skills**，检查配置、安全变更范围、单元测试、frontmatter、README 可复现性、Marketplace 可复现性、Python 语法。
4. **只有确切候选 SHA 校验成功**且 PR、主分支和文件范围未变化才自动合并。校验失败或 GitHub API/Runner 不可用时绝不伪称成功，也不绕过 CI 强推；候选 PR 保留，后续重复运行可以重试。

受保护的配置字段、上游仓库地址、脚本本身和其他自研 Skill 不能被候选 PR 顺带修改。定时任务有可能因 GitHub 服务、GitHub Actions 配额、权限、恶意上游或无法通过验证而失败；无法对外部平台承诺 100% 成功。必须报告失败的具体执行步骤与候选链接，继续重试或修复，不得把“发现更新”冒充完成。

工作流使用内置 `GITHUB_TOKEN`。创建 PR 需在仓库 **Settings → Actions → General** 开启 Actions 创建 PR 的许可。其校验调度依赖 `actions:write`，校验本身只读。GitHub 对 GITHUB_TOKEN 触发事件有限制，因此通过 `workflow_dispatch` 校验精确候选提交，不依赖未被触发的 PR 校验。分支保护、审批和安全规则不会被绕过。

每次实际同步会生成根目录 `UPSTREAM_SYNC_REPORT.md`，汇总全部受管 Skill 的检查结果、更新前后版本、上游 commit 和文件变化；详细报告保留在 `docs/upstream-reports/`。报告在候选分支生成，只有 CI 通过并合并到 master 才代表已落地；失败时查看 Actions 日志和失败 issue。无变化的检查按北京时间周次记录，避免同周重复空提交。

每个 UTC 月首次正常检查会更新 `docs/upstream-reports/health.json`；同一月不重复更新该月健康记录。定时工作流可能延迟。

## 配置字段

- `url`：README 来源地址；`version`：当前仓库实际同步的 commit 短 SHA（历史记录可保留原 tag/version，后续更新转为 SHA）。
- `sync.repository`、`sync.path`、`sync.ref`：GitHub 上游仓库、技能子目录及跟踪分支。
- `sync.mode`：默认 `replace`，遗留 `mirror` 可用；定时任务禁止仅报告的 `review`。
- `sync.files`：可选文件白名单，但配置白名单意味着只同步所列文件。**当前 8 个外部 Skill 均已取消白名单，完整跟踪对应的上游技能目录**；今后优先采用完整目录，除非明确需要限制更新范围。
- `sync.synced_commit`：完整 SHA；更新成功后对应本次真实上游快照。
- `sync.preserve_files`：仅可登记许可证或第三方 NOTICE 类文件（如 Impeccable 的 `LICENSE`、`NOTICE.md`），不参与源码替换且禁止自动 PR 修改；如果上游同名文件出现，自动同步会失败并要求检查，避免覆盖法律声明。
- `sync.last_reported`：报告去重标识，**不阻止未合并更新重试**。

## 手动执行与本机检查

在 GitHub **Actions → Sync Skill Upstreams → Run workflow** 中，将 `dry_run` 留为 `false`，可启动真正的候选生成、CI 和自动合并。设为 `true` 则只检查并生成报告。

```bash
python3 -m pip install pyyaml
python3 skill-sync/scripts/sync_upstream.py --validate-config
python3 -m unittest discover -s skill-sync/tests -v
python3 skill-sync/scripts/sync_upstream.py --report /tmp/upstream-report.json
# 仅在本地临时分支预览实际替换，必须检查 git diff
python3 skill-sync/scripts/sync_upstream.py --apply
python3 skill-sync/scripts/gen_readme.py
python3 skill-sync/scripts/gen_marketplace.py --check
```

GitHub 仓库自动更新成功之后，ChatGPT 手动上传的技能仍需重新安装；此工作流**仅更新 GitHub 仓库**。已通过支持 GitHub Marketplace 的工作区导入、且实际跟踪 `master` 的插件才能使用平台提供的后续同步流程。

## 第二段：GitHub → ChatGPT Marketplace

通过 **Admin → Plugins → Marketplaces** 导入本仓库，Source 使用 `https://github.com/CherryYang05/myskills`，Path 留空，Branch 使用 `master`。工作区 Marketplace 默认每日检查更新，也可选择 **Sync now**，并检查单个插件同步结果。不要固定在 commit 或 tag，否则不会跟随 master。

该链路不需要 GPT 定时任务重复执行第一段上游检查；可停用原来的上游同步/补救任务。Marketplace 的每日同步是平台任务，不等同于 GPT 对话里的定时任务。仅有清单不证明目标工作区已导入或开启同步，实际配置应在管理界面核对。

## 官方参考

- [GitHub 定时工作流](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [Actions 的 PR 创建权限](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)
- [GITHUB_TOKEN 触发工作流的行为](https://docs.github.com/en/actions/concepts/security/github_token)
