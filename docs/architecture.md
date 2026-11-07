# myskills 仓库结构与两段同步

## 目录职责

```text
skills/
  external/<skill>/     原样镜像第三方 Skill 包，自动覆盖
  personal/<skill>/     自研 Skill，仅由维护者修改
plugins/<skill>/         自动生成的自包含 Plugin 安装包；plugin.json + skills/<skill>/
automation/
  upstreams.json        外部来源唯一注册表
  templates/
    README.md.tpl       README 唯一可编辑正文模板，注入自动生成的 Skill 表格
  scripts/
    sync.py             获取、比较、替换上游 Skill；产出根目录报告
    verify.py           校验 Skill 名称、来源完整性和 Frontmatter
    generate.py         统一生成 README、多平台 Marketplace、CLI 配置和 Plugin 安装包
    auto_merge.py       精确 SHA 的 CI 验证 + 限域自动合并
  tests/                同步安全与报告、配置回归测试
.github/workflows/
  sync-upstream.yml     每周五北京时间 20:30 / 手动启动
  validate-skills.yml   PR / master / 精确候选分支的 CI
.agents/plugins/marketplace.json   ChatGPT 插件目录（自动生成）
.claude-plugin/marketplace.json   Claude Code 插件目录（自动生成）
.cursor-plugin/marketplace.json   Cursor 团队插件目录（自动生成）
skills.sh.json                    Skills CLI 发现路径配置（自动生成）
README.md                         Skill 列表（自动生成）
UPSTREAM_SYNC_REPORT.md           上游同步与文件修正报告（自动生成）
```

Skill 数量与分组以 `README.md` 中动态生成的清单为准。外部 Skill 的目录结构及文件权限尽量与上游匹配；自研 Skill 不参加自动替换。

## 为什么外部来源要有注册表

`automation/upstreams.json` 明确记录每个外部 Skill 的上游 `repo`、内部 `path`、跟踪的 `ref`、本仓库已同步的完整提交 `sha`、可选的 `preserve` 法律声明。完整 Git SHA 是唯一版本依据；README 的短 SHA 和可点击来源链接按需生成，不重复存储。所有外部 Skill 目录必须与配置键严格一一对应；新增未登记外部 Skill 会使 CI 失败。

**注意：** 请勿将个人或自研 Skill 放进 external；新加的第三方 Skill 必须将它的真实来源和首次同步 SHA 一并记录。自研目录只按实际文件维护。

## 跨平台分发和 Skills CLI

`skills/external/`、`skills/personal/` 保持唯一源码；第三方上游原有的 `.claude-plugin/` 和 `.cursor-plugin/` 文件完整保留，便于直接使用原作者的仓库。它们位于 Skill 的子目录，不能充当 `myskills` 仓库的 Marketplace 根入口。

三份生成的根索引：`.agents/plugins/marketplace.json`（ChatGPT）、`.claude-plugin/marketplace.json`（Claude Code）、`.cursor-plugin/marketplace.json`（Cursor）。它们都指向 `plugins/<name>/` 中的通用 Agent Plugin（根级 `plugin.json`，`skills/<name>/SKILL.md`）；Claude Code 的单插件 Manifest 可省略，由 Marketplace 条目提供名称并发现标准 `skills/` 目录。Cursor 团队 Marketplace 需要相应计划与管理权限。

`skills.sh.json` 明确声明 `skills/external` 和 `skills/personal` 为 Skills CLI 发现路径；`npx skills add CherryYang05/myskills --list` 应显示仓库中全部 Skill。安装示例见 [README 安装与更新](../README.md#安装与更新)。Claude Code 通过 `claude plugin marketplace add CherryYang05/myskills` 注册目录，之后 `claude plugin install humanizer@cherry-skills`。两种安装方式互相独立。Cursor 的自建团队 Marketplace 与 CLI 安装也可独立使用。

## GitHub 上游 → myskills

每周五北京时间 20:30 自动执行，可在 Actions 中手动启动。同步流程按仓库与 ref 缓存已取得的上游快照（同源 Skill 共享一次 Git fetch），只接收 regular Git blobs，拒绝符号链接、子模块、越界路径、超限文件集合；不会执行上游 Skill 中的脚本。所有快照获取完成才开始修改。

有变化时使用上游确切提交替换相关 external 目录、更新 SHA、生成 README / 多平台 Marketplace / CLI 配置 / 完整 Plugin 包 / 根目录修正报告。没有源文件变化时保留 `UPSTREAM_SYNC_REPORT.md` 和 `automation/upstreams.json` 原样，避免日期变化引起空转 PR；每次检查状态都写入 Action Summary，JSON Artifact 可下载查证。候选 PR 只允许改动注册表中受管目录及生成物（包括对应 `plugins/<external-name>/` 包），不能碰 personal、同步脚本、工作流、来源地址或 legal preserve 文件。

候选 PR 的同一 head SHA 必须在 `Validate Skills` 完整通过且主分支仍等于预期基础 SHA，才允许自动合并。否则留下 PR 并在 Issue 通知，而不会强推或标记成功。

## myskills → ChatGPT

清单位于仓库根目录 `.agents/plugins/marketplace.json`，列出全部 16 个 Skill 对应的 `./plugins/<name>` 安装包。`plugins/` 是构建产物：每个包都有根目录 `plugin.json`，以及 `skills/<name>/SKILL.md` 和原 Skill 的脚本、参考资料、资源文件；生成时仅排除源 Skill 根目录的 `.claude-plugin/`、`.cursor-plugin/` 等其他客户端专用安装元数据。源目录始终保留原始文件。原始源码仍位于 `skills/external/` 或 `skills/personal/`，禁止手动编辑 `plugins/`；生成器会完整重建它们，只有分发包的内容（含 manifest）变化时才自动递增该 Plugin 的补丁版本号，不额外维护版本注册表。

**ChatGPT 工作区管理员**可以通过 **Admin → Plugins → Add → Import marketplace** 导入仓库，Source 填 `https://github.com/CherryYang05/myskills`，Path 留空，Branch 选 `master`。平台提供默认每日自动同步和手动 Sync now；这项同步必须在实际目标工作区完成导入后才能生效。具体入口和行为请参阅 [官方文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

个人 ChatGPT Plus 空间中的手动上传 Skill 与工作区 Marketplace 导入不同。仓库 Action 不会替换这些手动上传的插件；GitHub 中生成配置文件也不意味着 ChatGPT 端已安装或已更新。同步后应查看工作区每个插件的结果，失败更新可能保留旧版本。已有插件需要按真实 pluginId 逐一评估迁移，不能猜测 ID，也不要为刷新直接删除 Marketplace。

## 生成器与 GitHub Actions 的触发条件

- **手动生成（本地）**：在仓库根目录执行 `python3 automation/scripts/generate.py`，同时更新 `README.md`、`.agents/plugins/marketplace.json` 和全部 `plugins/<name>/`。源 Skill 目录保持不变；生成器会重建插件包，因此不要在生成目录内直接改文件。
- **PR 验证**：任何 Pull Request 都触发 [Validate Skills](../.github/workflows/validate-skills.yml)；该流程运行回归测试、来源校验以及 `python3 automation/scripts/generate.py --check`。它只检查，不自动修改 PR；如果你手动修改了 Skill，必须同时提交生成产物，否则 CI 失败。
- **自动上游同步**：每周五北京时间 20:30，或在 [Sync Skill Upstreams](../.github/workflows/sync-upstream.yml) 中 `Run workflow` 且 `dry_run=false`，才会真正抓取外部 Skill、执行 `sync.py --apply`、调用 `generate.py`、生成候选 PR、在精确 SHA 的 CI 成功后自动合并。仅检查模式 `dry_run=true` 不写入仓库。
- **PR 上游预览**：修改上游同步逻辑、来源配置、自动合并规则或相关测试的 PR 还会触发 `Sync Skill Upstreams / preview`，仅查询上游来源，不重写插件目录。
- **合并后检查**：`master` 的 push 再次触发 Validate Skills，验证生成结果与最终合并版本一致。

检查成功的证据是：PR/主分支 Actions 显示 `Validate Skills: success`（包含 `Verify generated README, Marketplace and Plugin packages` 和 `Verify Skills CLI discovers all source Skills`），`plugins/<name>/plugin.json` 和 `plugins/<name>/skills/<name>/SKILL.md` 均存在，且 `generate.py --check` 退出码为 0。GitHub 验证成功只确认仓库打包结果；ChatGPT 客户端还需要在已导入的 Marketplace 中执行同步，并检查插件详情是否识别到 Skill。

## 维护和测试

本地先安装 `pyyaml`，执行：

```bash
python3 -m pip install pyyaml
python3 -m unittest discover -s automation/tests -v
python3 automation/scripts/verify.py
python3 automation/scripts/generate.py --check
python3 automation/scripts/sync.py --check-config
```

README 正文只编辑 `automation/templates/README.md.tpl`，`{{SKILL_TABLE}}` 标记由生成器注入。生成物由 `python3 automation/scripts/generate.py` 写入。CI 对每个 Plugin 的 manifest、Skill 文件内容和执行权限做一致性校验。不要在根目录保留第二份手写来源索引，也不要把 Python 缓存、下载生成的二进制或测试输出提交到 Git。历史清理文件仍可从 Git 历史恢复。
