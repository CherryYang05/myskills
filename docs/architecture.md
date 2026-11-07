# myskills 仓库结构与两段同步

## 目录职责

```text
skills/
  external/<skill>/     原样镜像第三方 Skill 包，自动覆盖
  personal/<skill>/     自研 Skill，仅由维护者修改
automation/
  upstreams.json        外部来源唯一注册表
  scripts/
    sync.py             获取、比较、替换上游 Skill；产出根目录报告
    verify.py           校验 Skill 名称、来源完整性和 Frontmatter
    generate.py         统一生成 README 和 Marketplace
    auto_merge.py       精确 SHA 的 CI 验证 + 限域自动合并
  tests/                同步安全与报告、配置回归测试
.github/workflows/
  sync-upstream.yml     每周五北京时间 20:30 / 手动启动
  validate-skills.yml   PR / master / 精确候选分支的 CI
.agents/plugins/marketplace.json   ChatGPT 插件目录（自动生成）
README.md                         Skill 列表（自动生成）
UPSTREAM_SYNC_REPORT.md           上游同步与文件修正报告（自动生成）
```

保留 17 个原有 Skill：8 个外部同步、9 个自研。外部 Skill 的目录结构及文件权限尽量与上游匹配；自研 Skill 不参加自动替换。

## 为什么外部来源要有注册表

`automation/upstreams.json` 明确记录每个外部 Skill 的上游 `repo`、内部 `path`、跟踪的 `ref`、本仓库已同步的完整提交 `sha`、可选的 `preserve` 法律声明。完整 Git SHA 是唯一版本依据；README 的短 SHA 和可点击来源链接按需生成，不重复存储。所有外部 Skill 目录必须与配置键严格一一对应；新增未登记外部 Skill 会使 CI 失败。

\todo: 请勿将个人或自研 Skill 放进 external；新加的第三方 Skill 必须将它的真实来源和首次同步 SHA 一并记录。自研目录只按实际文件维护。

## GitHub 上游 → myskills

每周五北京时间 20:30 自动执行，可在 Actions 中手动启动。同步流程依次取得所有上游快照，只接收 regular Git blobs，拒绝符号链接、子模块、越界路径、超限文件集合；不会执行上游 Skill 中的脚本。所有快照获取完成才开始修改。

有变化时使用上游确切提交替换相关 external 目录、更新 SHA、生成 README / Marketplace / 根目录修正报告。即使没有内容更新，周度报告也可记录该次检查。候选 PR 只允许改动注册表中受管目录及四个生成物，不能碰 personal、同步脚本、工作流、来源地址或 legal preserve 文件。

候选 PR 的同一 head SHA 必须在 `Validate Skills` 完整通过且主分支仍等于预期基础 SHA，才允许自动合并。否则留下 PR 并在 Issue 通知，而不会强推或标记成功。

## myskills → ChatGPT

清单位于仓库根目录 `.agents/plugins/marketplace.json`，记录全部 17 个 Skill 的相对目录，其中既有 external 也有 personal。

**ChatGPT 工作区管理员**可以通过 **Admin → Plugins → Add → Import marketplace** 导入仓库，Source 填 `https://github.com/CherryYang05/myskills`，Path 留空，Branch 选 `master`。平台提供默认每日自动同步和手动 Sync now；这项同步必须在实际目标工作区完成导入后才能生效。具体入口和行为请参阅 [官方文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

个人 ChatGPT Plus 空间中的手动上传 Skill 与工作区 Marketplace 导入不同。仓库 Action 不会替换这些手动上传的插件；GitHub 中生成配置文件也不意味着 ChatGPT 端已安装或已更新。同步后应查看工作区每个插件的结果，失败更新可能保留旧版本。已有插件需要按真实 pluginId 逐一评估迁移，不能猜测 ID，也不要为刷新直接删除 Marketplace。

## 维护和测试

本地先安装 `pyyaml`，执行：

```bash
python3 -m pip install pyyaml
python3 -m unittest discover -s automation/tests -v
python3 automation/scripts/verify.py
python3 automation/scripts/generate.py --check
python3 automation/scripts/sync.py --check-config
```

生成物由 `python3 automation/scripts/generate.py` 写入。不要在根目录保留第二份手写来源索引，也不要把 Python 缓存、下载生成的二进制或测试输出提交到 Git。历史清理文件仍可从 Git 历史恢复。
