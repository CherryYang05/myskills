---
name: skill-sync
description: 管理 Claude skills 与 GitHub 仓库的双向同步。当用户提到"同步 skills"、"上传 skill 到 GitHub"、"从 GitHub 下载/安装 skill"、"更新 GitHub 上的 skill"、"列出本地/远程 skills"、"对比 skills 差异"时，必须立即触发此 skill。当用户结束对 skill 的修改并说"更新一下"、"同步一下"、"提交到 GitHub"时也要触发。所有涉及 GitHub 与本地 skills 同步的操作都通过此 skill 处理。
---

# Skill Sync

管理本地 Claude skills 与 GitHub 私有仓库的双向同步。所有操作支持 Windows / Linux / macOS，仅依赖 Python 标准库。

---

## 脚本位置

```bash
# Claude.ai 网页版
python /mnt/skills/user/skill-sync/scripts/skill_sync.py <命令>

# Claude Code（Linux / macOS）
python ~/.claude/skills/skill-sync/scripts/skill_sync.py <命令>

# Claude Code（Windows）
python %USERPROFILE%\.claude\skills\skill-sync\scripts\skill_sync.py <命令>
```

如不确定环境，用以下方式自动定位：

```bash
python -c "
from pathlib import Path
candidates = [
    Path('/mnt/skills/user/skill-sync/scripts/skill_sync.py'),
    Path.home() / '.claude/skills/skill-sync/scripts/skill_sync.py',
]
for p in candidates:
    if p.exists(): print(p); break
else: print('NOT_FOUND')
"
```

后续示例中统一用 `<SCRIPT>` 代表实际路径。

---

## 认证方式：GitHub Personal Access Token

skill-sync 使用 **PAT（Personal Access Token）** 认证，不使用网页 OAuth。

**原因**：本工具运行在纯 CLI / headless 环境（Claude Code、服务器终端等），无浏览器依赖，PAT 更简单可靠。

**Token 获取**：https://github.com/settings/tokens
- 权限要求：`repo`（读写私有仓库）
- 建议使用 Fine-grained token，只授权 skill 仓库的 Contents 读写权限

**Token 存储位置**：`~/.skill-sync-config.json`
- 文件权限自动设置为 `600`（仅当前用户可读写）
- Token 在 `config` 命令显示时自动脱敏（仅展示末 4 位）

---

## 先有鸡先有蛋：在新环境 Bootstrap

在新机器上，`skill-sync` 本身还未安装，无法用 skill-sync 来安装 skill-sync。
解决方案：使用仓库中的独立 **bootstrap 脚本**，该脚本无需 skill-sync，直接从 GitHub 下载。

### 获取 bootstrap 脚本

bootstrap 脚本存放在 GitHub 仓库的 `skill-sync/scripts/bootstrap.py`。

获取方式一：curl 直接运行（最快）

```bash
# Linux / macOS
curl -fsSL https://raw.githubusercontent.com/USER/REPO/main/skill-sync/scripts/bootstrap.py \
  | python3 - --token ghp_xxxx --repo USER/REPO

# 或先下载再运行
curl -fsSL -o bootstrap.py https://raw.githubusercontent.com/USER/REPO/main/skill-sync/scripts/bootstrap.py
python3 bootstrap.py --token ghp_xxxx --repo USER/REPO
```

获取方式二：通过环境变量传入敏感参数（适合脚本/CI）

```bash
export SKILL_SYNC_TOKEN=ghp_xxxx
export SKILL_SYNC_REPO=USER/REPO
python3 bootstrap.py
```

获取方式三：指定安装路径和 profile 名称

```bash
python3 bootstrap.py \
  --token ghp_xxxx \
  --repo USER/REPO \
  --install-to ~/.claude/skills \
  --profile claude-code-linux
```

### Bootstrap 做了什么

1. 验证 Token 有效性
2. 拉取仓库文件树
3. 下载 `skill-sync/` 目录全部文件到安装路径
4. 写入 `~/.skill-sync-config.json`（token、repo、profile）

Bootstrap 完成后，直接运行正式脚本：

```bash
python ~/.claude/skills/skill-sync/scripts/skill_sync.py config
python ~/.claude/skills/skill-sync/scripts/skill_sync.py list-remote
```

---

## 多环境 Profiles 管理

不同 agent 的 skills 目录各不相同（Claude.ai、Claude Code Linux、Claude Code Windows、自建 agent 等）。skill-sync 通过 **profiles** 解决这一痛点：每个 profile 对应一个命名的本地 skills 路径，GitHub 连接（token/repo）全局共享。

### 典型配置示例

```json
{
  "github_token": "ghp_xxxx",
  "github_repo":  "user/my-skills",
  "active_profile": "claude-code-linux",
  "profiles": {
    "claude-code-linux": {
      "local_skills_path": "/home/user/.claude/skills",
      "description": "Claude Code on Linux server"
    },
    "claude-code-windows": {
      "local_skills_path": "C:\\Users\\user\\.claude\\skills",
      "description": "Claude Code on Windows PC"
    },
    "claude-ai": {
      "local_skills_path": "/mnt/skills/user",
      "description": "Claude.ai web (read-only, install restricted)"
    }
  }
}
```

### Profile 管理命令

```bash
# 列出所有 profiles（带 [active] 标记）
python <SCRIPT> config profile list

# 新增 profile
python <SCRIPT> config profile add claude-code-linux ~/.claude/skills "Claude Code on Linux"

# 切换活跃 profile
python <SCRIPT> config profile set claude-code-linux

# 删除 profile
python <SCRIPT> config profile remove old-profile
```

### 临时切换 Profile（不修改 active_profile）

所有操作命令都支持 `--profile NAME`（或 `-p NAME`）：

```bash
# 临时用 claude-code-windows profile 执行 diff，不影响默认 profile
python <SCRIPT> --profile claude-code-windows diff

# 安装到特定 profile 对应的路径
python <SCRIPT> -p claude-ai install skill-name
```

---

## 初次使用：配置检查

**每次触发此 skill 时，先检查配置是否完整：**

```bash
python <SCRIPT> config
```

若输出 `[WARN] 尚未配置`，引导用户运行：

```bash
python <SCRIPT> config set
```

> `config set` 需要交互式输入，在 Claude.ai 网页版须在 bash 中运行并等待输入。
> 配置保存在 `~/.skill-sync-config.json`，Token 文件权限自动设置为 600。

---

## 操作一：列出 Skills

```bash
# 列出本地（当前 active profile）
python <SCRIPT> list-local

# 列出 GitHub
python <SCRIPT> list-remote

# 对比差异
python <SCRIPT> diff
```

这三个命令直接运行，无需确认，输出结果展示给用户即可。

---

## 操作二：上传 Skills 到 GitHub

**规则：只上传 GitHub 上没有的 skills，不会覆盖已有的。**

### 第一步：预览（必须先执行）

```bash
python <SCRIPT> upload               # 上传所有本地有、GitHub 没有的
python <SCRIPT> upload skill-a skill-b  # 或指定名称
```

解析输出中的 `##CONFIRM_UPLOAD##` 行，提取 JSON 列表，向用户展示，然后**明确询问是否确认上传**。

### 第二步：等待用户确认

用中文问：**「以上 X 个 skills 将上传到 GitHub，是否确认？」**

### 第三步：实际上传

```bash
python <SCRIPT> do-upload skill-a skill-b
```

---

## 操作三：从 GitHub 安装 Skills 到本地

### 第一步：预览

```bash
python <SCRIPT> install              # 安装所有 GitHub 上的 skills
python <SCRIPT> install skill-a      # 或指定名称
```

解析 `##CONFIRM_INSTALL##` 行，向用户展示安装路径，**明确询问是否确认安装**。

### 第二步：等待用户确认

用中文问：**「以上 X 个 skills 将安装到本地 [路径]，是否确认？」**

### 第三步：实际安装

```bash
python <SCRIPT> do-install skill-a
```

> **Claude.ai 网页版限制**：`/mnt/skills/user` 为只读挂载，`do-install` 可能写入失败。此时告知用户：skill 文件已下载，需要通过 Claude.ai 设置页面手动上传。

---

## 操作四：更新 GitHub 上已有的 Skills

用于将本地修改后的 skill 推送覆盖 GitHub 上的旧版本。

### 触发场景

用户在当前对话中对某个 skill 进行了修改，现在想把改动同步到 GitHub。

### 第一步：总结改动（仅"更新"场景）

在运行预览命令之前，**先向用户总结本次改动**：

> 例如：「本次对 `tech-blog-writer` 做了以下修改：
> 1. 更新了触发关键词，新增"总结一下"
> 2. 调整了博客结构，去掉了"参考资料"章节
> 是否将以上改动更新到 GitHub？」

若用户确认，再执行第二步。

### 第二步：预览

```bash
python <SCRIPT> update skill-name
```

解析 `##CONFIRM_UPDATE##` 行，再次确认。

### 第三步：更新 GitHub

```bash
python <SCRIPT> do-update skill-name
```

### 第四步：询问是否同步本地

**「GitHub 已更新完成。是否同时将 GitHub 版本同步到本地？」**

- 用户确认 -> 运行 `do-install skill-name`
- 用户拒绝 -> 结束

---

## 操作五：更新仓库 README（自动执行）

**重要**：每次 `do-upload` 或 `do-update` 成功后，必须自动执行此操作。

### 触发时机

- `do-upload` 成功后
- `do-update` 成功后

### 更新内容

1. 在 README 顶部添加或更新"收录的 skills"章节：

```markdown
## 收录的 Skills

| Skill 名称 | 说明 |
|-----------|------|
| skill-name | skill 的 description 第一行 |
```

2. 如果是新增 skill，在表格末尾追加一行
3. 如果是更新 skill，更新对应行的说明
4. 如果是删除 skill，从表格中移除（较少见）

### README 更新位置

- 在 README 最顶部（标题之后）插入"收录的 Skills"表格
- 如果已有"收录的 Skills"章节，则更新该章节而不是新增

### 执行命令

```bash
# 获取所有远程 skills
python <SCRIPT> list-remote

# 读取每个 skill 的 description 生成表格
```

### Git 提交

README 更新后自动提交，commit 信息为：`docs: 更新 skills 列表`

---

## 确认规则总结

| 操作 | 需要确认 | 确认时机 |
|------|----------|----------|
| list-local / list-remote / diff | 不需要 | — |
| upload -> do-upload | 需要 | 展示预览后 |
| install -> do-install | 需要 | 展示预览后 |
| update -> do-update | 需要 x2 | 总结改动后 + 展示预览后 |
| update -> do-install（本地同步）| 需要 | GitHub 更新完成后 |
| do-upload / do-update | 自动 | 更新 README 后自动提交 |

---

## 常见问题处理

- **HTTP 401**：Token 无效或过期 -> 引导用户重新运行 `config set`
- **HTTP 404**：仓库不存在或无权限 -> 检查 `github_repo` 配置和 Token 的 `repo` 权限
- **本地路径不存在**：提示用户检查当前 profile 的 `local_skills_path`，或切换 profile
- **skill 无 SKILL.md**：该目录不会被识别为 skill，提醒用户检查目录结构
- **旧格式配置**：`config set` 会自动将 `local_skills_path` 迁移到 `profiles.default`
