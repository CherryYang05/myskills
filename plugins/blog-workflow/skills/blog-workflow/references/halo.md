# Halo 草稿同步

目标站点以用户指定的地址或已配置的连接为准。此流程的 HTML 预检以 ByteMD 为准。未经用户要求只交付成稿。用户说上传或同步时默认存未发布草稿。向 Halo 提供最终审校后的正文和发布元数据，省去聊天记录、素材和内部审稿记录。

## 写入前

1. 查找目标站点已有分类与标签，必要时分页。对照可见名称和语义选用现有项，传入实际资源 ID，通常为 `metadata.name`。没有合适的项时说明缺什么，按用户授权范围继续。
2. 保留下载用的 Markdown 首行 H1。同步时用 H1 的文字作 Halo 标题，正文从其后一行开始。保持 Markdown 中的原始 HTML 图与 KaTeX 公式。提供与 Markdown 同稿的渲染 HTML，禁止把 Markdown 冒充渲染 HTML。可在本地使用随附的 ByteMD 预检工具。
3. 首次使用可读的稳定 slug，文章名用 `blog-<slug>`，总长不超过 63 个字符。已经有记录时优先用旧 ID。按 slug 和 ID 查现有文章，包括草稿，防止覆盖或重复。碰到回收记录、同 slug 的其他文章、后端拒绝访问或状态不明时先核对。

## 已连接 Halo 官方 MCP 时

以下名称来自 Halo MCP Server 1.3.3。以当前工具的实际参数为准。

- `halo_list_categories`、`halo_list_tags` 查已有资源。`halo_list_posts` 按页查现有 slug，`halo_get_post` 可按 `name` 读取 `HEAD` 版本的 `RAW` 或 `HTML`。写入前先确认上述读取可用。
- `halo_create_post` 用 `name`、`title`、`slug`、`raw`（Markdown 正文）、`rawType: "markdown"`、`content`（渲染后的 HTML）、`categories`、`tags` 和显式的 `publish: false`。不设置计划发布时间。实际的创建工具可直接发布，因此不能把密钥的工具清单当作草稿状态的强制限制。
- 请求超时先按稳定 ID 回读。若看到同一稿件，核对内容后使用现有 ID。状态未知时不再创建。用户明确要求改同一未发布草稿时，先核对其当前版本，处理人工改动，再使用已授权的更新工具。公开动作使用用户明确指定的稿件和发布操作。

连接使用独立、按工具授权的 Halo MCP 密钥。用户通过 Halo 控制台生成密钥，并在客户端的安全输入框配置。插件包、命令参数、文件与聊天中均不放密钥。连接未就绪时交付正文，标明草稿未写入。

## Codex 本地同步

使用 Halo 官方 CLI 1.3.0。用独立内容账号和交互式登录配置 `blog` profile，确认站点和权限。具体旗标以 `halo --help` 为准。用 `halo post category list --profile blog --json` 和 `halo post tag list --profile blog --json` 查分类标签。

将 `scripts/` 复制到可写工作目录，在该目录执行 `npm ci --ignore-scripts`。写入 `halo-meta.json`，包含 `title`、`slug`、`categories`、`tags`。执行 `node prepare-halo.cjs article.md halo-meta.json halo-draft.json`。工具输出预览和未发布 JSON，需公式时另用 KaTeX 核验。按 ID 和 slug 确认目标后，用 `halo post import-json --file halo-draft.json --profile blog --json` 创建。首次创建不传 `--force`。

无法用 API 写入时，可在已登录的 Halo ByteMD 编辑器把同一份 Markdown 正文存为草稿，填入已查得的分类标签，沿用相同的预览和回读检查。

## 回读与发布

回读文章 ID、未发布状态、分类、标签、Markdown 源文与渲染 HTML。能打开实际 Halo 主题预览时，看图、公式和手机宽度。否则明确区分本地预检和实际预览。用户明确要求公开同一篇时，从确认过的文章 ID 发布，打开未登录可访问的文章 URL 核对结果。

[Halo MCP Server](https://github.com/halo-dev/plugin-mcp-server/tree/v1.3.3) · [Halo CLI](https://github.com/halo-dev/cli/tree/1.3.0)
