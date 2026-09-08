# MR Reviewer 前置步骤指南

本文档说明使用 MR Reviewer Skill 前需要满足的前置条件，以及如何自动检查和修复这些问题。

## 前置条件检查

在使用 MR Reviewer 之前，请先运行前置条件检查脚本：

```bash
cd skills/mr-reviewer
python scripts/common/check_prerequisites.py
```

或者使用 `--fix` 参数自动尝试修复问题：

```bash
python scripts/common/check_prerequisites.py --fix
```

---

## 必需的前置条件

### 1. Python 环境

- **版本要求**: Python 3.7 或更高版本
- **检查方式**: 运行 `python --version` 或 `python3 --version`

### 2. Python 依赖库

MR Reviewer 依赖以下 Python 包：

| 包名 | 用途 | 类型 |
|------|------|------|
| `requests` | HTTP 请求，用于调用 CodeHub API | 核心 |
| `urllib3` | SSL 证书警告处理 | 核心 |
| `requests-toolbelt` | OneBox 上传 multipart 编码 | 核心 |
| `pyyaml` | YAML 配置文件解析 | 核心 |
| `httpx` | MCP 客户端异步 HTTP（WeLink 通知） | 可选 |
| `fastmcp` | MCP 协议客户端（WeLink 通知） | 可选 |
| `pywin32` | Windows DPAPI 令牌解密 | 可选-Windows |

> **提示**：推荐使用 `uv` 管理 Python 环境，结合 `requirements.txt` 一键安装所有依赖。

**自动安装**:
```bash
# 使用 uv
uv pip install -r scripts/requirements.txt --system

# 或使用 pip
pip install -r scripts/requirements.txt
```

**分步安装**:
```bash
# 核心依赖
uv pip install requests requests-toolbelt pyyaml --system
pip install requests requests-toolbelt pyyaml

# WeLink 通知依赖（可选，需要 Windows）
uv pip install httpx fastmcp pywin32 --system
pip install httpx fastmcp pywin32
```

### 3. Git

- **用途**: 克隆代码仓库到本地
- **检查方式**: 运行 `git --version`

**安装方式**:
- Windows: 下载 [Git for Windows](https://git-scm.com/download/win)
- macOS: `brew install git` 或从 App Store 安装 Xcode
- Linux: `sudo apt install git` 或 `sudo yum install git`

### 4. 配置文件 (config.json)

配置文件必须存在于用户目录 `~/.mr-reviewer/config.json`。

**必需的配置项**：

| 配置项 | 说明 |
|--------|------|
| `codehub_token` | CodeHub API 访问令牌，用于获取 MR 信息和 diff 内容 |
| `codehub_tokens` | 检视多个域名MR时的token配置，如 open.codehub.huawei.com、cr-y.codehub.huawei.com |

**可选的配置项**：

| 配置项 | 说明 |
|--------|------|
| `welink_notify_ids` | 额外的通知人 ID，多个用英文逗号分隔 |
| `onebox_share_directory_url` | OneBox 分享目录链接 |
| `onebox_username` | W3 用户名 |
| `onebox_password` | W3 密码 |
| `onebox_idss_cid` | 用户唯一标识（登录 W3 → F12 → 搜索 idss_cid 获取） |
| `exclude_file_suffix` | 需要排除的文件后缀，多个用英文逗号分隔 |
| `send_discussion_level` | 推送 CodeHub 检视意见的问题级别，支持 `["高", "中", "低"]` |
| `clone_repo_path` | 代码仓本地存储路径，不配置则使用默认路径 `~/.mr-reviewer/project` |

**如何获取 CodeHub Token** (必需):

1. 登录 CodeHub (例如: https://open.codehub.huawei.com 或 https://codehub-y.huawei.com)
2. 点击右上角头像 → **个人设置**
3. 选择 **访问令牌** → **创建个人访问令牌**
4. 填写令牌描述，选择过期时间
5. 权限勾选 **read_api**（至少）
6. 点击创建，**务必保存好生成的令牌**（只会显示一次）
7. 将令牌填入 `config.json` 的 `codehub_token` 字段

---

## 可选功能的前置条件

以下功能为**可选**，不配置也能完成基本的 MR 代码检视，但会缺少相应功能。

### 1. OneBox 报告上传功能

如果需要将检视报告上传到 OneBox 并生成分享链接，需要额外配置：

| 配置项 | 用途            |
|--------|---------------|
| `onebox_share_directory_url` | OneBox 分享目录链接 |
| `onebox_username` | W3 用户名        |
| `onebox_password` | W3 密码         |
| `onebox_idss_cid` | 用户唯一标识        |

**获取 idss_cid 方法**：
1. 登录 W3 首页
2. 按 `F12` 打开开发者工具
3. 切换到 `Network`（网络）标签
4. 搜索 `idss_cid`，在请求头中获取值

### 2. WeLink 通知功能

如果需要在 MR 检视完成后发送通知到 WeLink，需要配置：

| 配置项 | 用途 |
|--------|------|
| `welink_notify_ids` | 额外的通知人 ID（多个用英文逗号分隔） |

---

## 常见问题排查

### 问题 1: Python 包未安装（核心依赖）

**错误信息**:
```
ModuleNotFoundError: No module named 'requests'
```

**解决方案**:
```bash
uv pip install requests requests-toolbelt pyyaml --system
pip install requests requests-toolbelt pyyaml
```

### 问题 2: WeLink 通知发送失败（缺少可选依赖）

**错误信息**:
```
❌ 环境依赖检查失败：
  - 缺少依赖: httpx（pip install httpx>=0.27）
  - 缺少依赖: fastmcp（pip install fastmcp>=2.0）
  - 缺少依赖: pywin32（pip install pywin32>=306，Windows 必需）
```

**解决方案**:
```bash
uv pip install httpx fastmcp pywin32 --system
pip install httpx fastmcp pywin32
```

### 问题 2: Git 未安装

**错误信息**:
```
FileNotFoundError: [WinError 2] The system cannot find the file specified
```

**解决方案**: 安装 Git 并确保在系统 PATH 中

### 问题 3: config.json 不存在

**错误信息**:
```
Config file not found at ~/.mr-reviewer/config.json
```

**解决方案**:
1. 创建 `~/.mr-reviewer/` 目录
2. 复制 `config.json.example` 为 `~/.mr-reviewer/config.json`
3. 编辑填入您的 `codehub_token`

### 问题 4: codehub_token 未配置

**错误信息**:
```
token not configured in config.json
```

**解决方案**: 编辑 `config.json`，将 `codehub_token` 的值替换为您申请到的令牌

---

## 自动修复

运行以下命令可以自动检查并尝试修复大部分问题：

```bash
python scripts/common/check_prerequisites.py --fix
```

**自动修复的内容**:
- ✅ 安装缺失的 Python 包（requests, urllib3）
- ✅ 创建默认 config.json 配置文件
- ✅ 创建代码仓存储目录
- ✅ 创建报告输出目录

**无法自动修复的内容**:
- ❌ Git 安装（需要手动安装）
- ❌ codehub_token 配置（需要用户手动填写）
- ❌ welink_token 配置（可选，不影响基本功能）

---

## 验证配置

完成所有前置条件后，运行以下命令验证配置是否正确：

```bash
python scripts/common/check_prerequisites.py
```

如果输出显示 `✅ 所有前置条件已满足！`，则表示配置完成，可以开始使用 MR Reviewer。

---

## 目录结构

```
mr-reviewer/
├── config.json.example      # 配置文件示例
├── SKILL.md                 # Skill 说明文档
├── scripts/
│   ├── 0-clean-temp/        # 清理过期临时文件
│   ├── 1-prepare-data/      # 数据准备
│   ├── 2-ai-analysis/       # AI分析支持
│   ├── 3-generate-report/   # 生成报告+上传OneBox
│   ├── 4-submit-review/     # 提交MR评论
│   ├── 5-welink-notify/     # 发送WeLink通知
│   └── common/              # 通用脚本
├── rules/                   # 检视规则目录
└── reference/               # 参考文档目录

用户目录（~/.mr-reviewer/）：
├── config.json              # 用户配置文件（必需）
├── temp/                    # 临时文件目录（自动创建）
│   └── mr_{repo}_{mrId}/    # MR临时文件子目录
├── project/                 # 代码仓本地存储目录（自动创建，可通过clone_repo_path配置）
└── logs/                    # 日志文件目录（自动创建）
```

**相关文档**:
- [SKILL.md](../SKILL.md) - 完整的配置说明和使用指南
- [AI 分析技术细节](ai_analysis.md) - 详细的 AI 分析流程和技术实现