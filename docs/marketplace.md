# Cherry Skills marketplace

本仓库通过 `.agents/plugins/marketplace.json` 提供 GitHub marketplace，名称为 `cherry-myskills`，显示名称为 Cherry Skills。每个条目直接引用仓库中现有的技能包；不复制技能、不改变原目录，也不改变 skills CLI 的安装方式。

采用 OpenAI 工作区导入文档支持的 skill package 格式。这里的 marketplace 是仓库内的分发清单，不是 GitHub 的公共 Marketplace 商店，也不表示已经发布到 ChatGPT 公开插件目录。

## ChatGPT 工作区：导入及自动同步

需要具有工作区管理员权限，以及可读取本仓库的 GitHub 账户。

1. 打开 **Admin → Plugins → Add → Import marketplace**。
2. **Source** 填 `https://github.com/CherryYang05/myskills`。
3. **Path** 留空。清单位于仓库根目录下的 `.agents/plugins/marketplace.json`，不要把清单文件名填到 Path 中。
4. **Branch, tag, or commit** 填 `master`。跟随分支才能收到后续更新；固定 commit 不会跟随最新提交。
5. 导入并检查 Import results，再为各插件配置安装策略和所需应用。
6. 在 **Admin → Plugins → Marketplaces** 查看同步报告，也可选择 **Sync now**。

官方说明新 marketplace 默认每天自动同步。同步既可能更新已有插件，也可能新增清单里的插件；合并仓库改动前应审查新增条目。同步报告可能包含单个插件的错误，不能只看任务是否结束。导入无效更新时，原插件保留最后可用版本。

清单中的 policy 是本地 marketplace 的默认元数据；工作区导入不会从仓库应用安装和认证策略，需要在管理界面设置。技能包中的脚本、网络和内部服务依赖仍受运行环境限制，本清单不自动创建 MCP 连接或授予服务权限。

## 已有安装与迁移

公共清单没有填入任何 `pluginId`，因为这些 ID 属于具体工作区。首次导入应按新来源处理，不能假定它会自动替换已有上传内容。

如果要原位迁移已有工作区插件，在工作区专用的清单中，为对应条目添加从 Admin → Plugins 取得的真实 `pluginId`，并让条目的 `name` 与原插件名完全一致。先试迁移一个插件，验证 ID、内容、共享和安装策略后再扩展。不要把独立技能的 `skill_id` 当作 `pluginId`，也不要将一个 ID 分配给多个条目。原安装若把多个技能打成一个插件，需要先按原插件边界整理包，不能直接套用本仓库的一技能一条目清单。

工作区专用迁移清单应单独维护，不要将 ID 写进这个自动生成的公共清单。迁移后更新来自 GitHub，不能再通过上传压缩包替换；不要为了迁移先卸载现有安装。删除 marketplace 会删除从它导入的插件，因此不要将删除 marketplace 用作刷新操作。

## 个人空间和桌面客户端

上述每日自动同步属于工作区管理功能。个人 Plus 空间如果没有 **Admin → Plugins → Import marketplace** 入口，仅有本仓库清单并不能自动更新已经手动上传的技能。

本清单也已在 Codex CLI 0.166.0-alpha.5.1 实测：可通过 `codex plugin marketplace add CherryYang05/myskills --ref master` 添加来源，再用 `codex plugin add humanizer@cherry-myskills` 等命令安装独立技能包。首次启用时先合并清单到 master。使用 `codex plugin marketplace upgrade cherry-myskills` 刷新来源；不要把本机安装视为网页或手机端已经同步，也不要将显式刷新当作每日自动更新保证。

当前个人空间的可靠替代仍是：在 GitHub 维护和校验版本，再通过技能编辑器或上传入口更新安装内容。不要把 GitHub 代码更新、skills CLI 更新和 ChatGPT 云端安装更新混为一谈。

## 维护清单

技能仍在仓库根目录维护。清单条目的 `name` 取自 `SKILL.md` 的 `name`，路径取自目录名。例如 `skill-blog-writer` 对应条目 `blog-writer`。名称用于稳定标识，改名应作为安装身份变更审查。

```bash
python3 -m pip install pyyaml
python3 skill-sync/scripts/gen_marketplace.py
python3 skill-sync/scripts/gen_marketplace.py --check
python3 skill-sync/scripts/gen_readme.py
```

新增、删除技能或修改技能名称后重新生成清单。普通内容更新不需要制造清单版本号：工作区跟随所选 Git 分支同步。README 的“同步版本”仍表示外部上游的实际同步基线，不是 ChatGPT 已安装版本。

CI 会检查清单是否完整、名称是否合法且唯一、各技能 frontmatter 是否具有名称和描述，以及生成结果是否与已提交清单一致。生成器使用现有 `gen_readme.py` 的目录发现规则，避免 README 和 marketplace 漏掉不同技能。

本机 Codex 安装与刷新已实测；工作区云端实际导入和同步仍需管理员在目标工作区验证。GitHub 上游维护工作流见 [上游同步](./upstream-sync.md)。

## 官方依据

- [Import and sync plugins from GitHub](https://learn.chatgpt.com/docs/enterprise/plugin-management)
- [Package your plugin](https://developers.openai.com/plugins/build/plugins)
