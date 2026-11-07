fork by: https://agent.huawei.com/ai/skills/mr-reviewer

**数存特色检视能力**

| 能力 | 说明 |
|------|------|
| 免配置Welink通知 | 通过MCP工具直接发送WeLink通知，无需额外配置 |
| 数存检视规则 | 覆盖 C、C++、Java、Python 四种语言的专属检视规则（安全合规、内存管理、指针操作、异常处理等） |
| Skill版本自动更新 | 检视前置阶段自动检测市场最新版本，本地落后时自动升级 |
| Discussion去重 | 提交前自动获取MR已有Discussion，同一文件同一行跳过重复提交 |
| Note去重 | 提交前自动检查MR是否已存在检视报告Note，避免重复提交 |
| 分批检视 | 大MR按文件分批、检视规则多时按规则分批，避免超出Token上下文限制 |
| Discussion转Issue | 检视意见提交Discussion时，待用户确认后自动创建关联Issue跟踪修复 |
| 代码缺陷扫描 | 针对9大类36项缺陷模式进行深度扫描，使用5个subagent并行处理 |

## 环境前置条件（需自行安装）

以下环境需用户自行安装，Skill 无法自动处理：

| 前置项 | 要求       | 说明 |
|--------|----------|------|
| Python | 3.10+    | 运行 Skill 脚本必需，低版本会报错退出  [下载链接](https://his.huawei.com/csop/index.html#/ToolInfo?samType=his&toolId=1420375075521036289)|
| pip | 可用且配置镜像源 | Python 依赖包自动安装依赖 pip，用户需要配置镜像源 [镜像配置链接](https://mirrors.tools.huawei.com/mirrorDetail/5ea638e45fb1b0f2698d3f34?mirrorName=python&catalog=tool) |
| Git | 已安装且可用   | 用于克隆代码仓和获取 diff，需在 PATH 中可找到 `git` 命令 |



## 修改配置文件config.json(前置条件，必做)

详细的逐项配置步骤请参考 [配置指南](https://portal.edevops.huawei.com/siku/project/ge79161e2454d4771b44305685ffd7bb2/wiki/7308/163443/WIKI2026072111939224)。

### 必选配置

| 配置项 | 说明 |
|--------|------|
| codehub_token | 黄区CodeHub API 访问令牌，用于获取 MR 信息和 diff 内容 |
| send_discussion_level | 需要提交discussion的风险级别，例如：`["高", "中"]`，不配置则不会提交discussion |
| onebox_share_directory_url | onebox云空间分享目录链接，如 https://onebox.huawei.com/#file/1/82547 |
| onebox_username | 公司域账户，如 a00123456 |
| onebox_password | 域账户密码 |
| onebox_idss_cid | onebox唯一标识id |
| clone_repo_path | 代码仓本地存储路径，如：D:\tmp，默认 ~/.mr-reviewer/project |

> 使用 CodeAgent3.0 时，onebox_username、onebox_password、onebox_idss_cid 三项无需配置。

### 建议配置

| 配置项 | 说明 |
|--------|------|
| codehub_tokens | 检视非黄区MR时配置对应token，如 codehub-g.huawei.com、open.codehub.huawei.com |
| welink_notify_ids | 检视结束后发送WeLink通知的目标人和群组，多个id用英文逗号隔开，如：a00123456,93065411204198 |
| exclude_file_suffix | 排除的文件后缀，多个用英文逗号分隔，如：.flex,.lightdt |
| max_rules_per_batch | 每批检视规则的最大数量，默认25。当检视规则较多时自动按此数量分批，避免超出Token上下文限制 |

---


## 使用方法

在 CodeAgent 对话框中输入以下提示词即可触发检视：

| 场景 | 提示词示例 |
|------|-----------|
| 检视 MR（推荐） | `使用 ds-mr-reviewer 帮我检视 https://codehub.huawei.com/xxx/merge_requests/123` |
| 检视 MR（简写） | `帮我检视 https://codehub.huawei.com/xxx/merge_requests/123` |

> 只要提示词中包含 CodeHub MR 链接，即可自动触发本 Skill。

## 与 review-fix agent 的集成

本 skill 的深度检视能力已融入review-fix agent （[使用手册](https://portal.edevops.huawei.com/siku/project/ge79161e2454d4771b44305685ffd7bb2/wiki/7308/163443/WIKI2026061211450957)）。review-fix agent 自动调用本 skill 执行完整的5个Stage深度检视，检视发现的问题直接交给 agent 自动修复。


## 检视规则体系

MR检视规则支持三个层级，优先级从高到低：代码仓级 > 语言级 > 全局。所有层级的规则在检视时都会被加载并遵守。

### 1️⃣ 全局 Tips

文件位置：`skills/mr-reviewer/rules/common_rules.md`

### 2️⃣ 语言级 Tips

文件位置：`skills/mr-reviewer/rules/language/`

*全局Tips和语言级Tips由数存产品线统一管理，随skill更新而更新，无需用户手动配置。*

### 3️⃣ 代码仓级 Tips

**这个文件需要像代码一样迭代演进。** 检视时会自动读取代码仓中的检视规则文件，作为需要遵守的检视规则。

代码仓级规则从以下路径加载：

| 路径 | 说明 |
|------|------|
| 代码仓 `.ai-coding/review/rules.md` | 代码仓 rules 规则 |

对于通过 `link_repo` 配置的关联代码仓，同样会从以上两个路径加载规则。

创建代码仓级tips时，请参考模板文件 `skills/mr-reviewer/rules/mr_reviewer_tips.md.example`，模板中包含：
- `link_repo`：声明当前代码仓还需要遵循其他代码仓的规则，多个仓库用英文逗号分隔
- `depend_repo`：声明当前代码仓代码依赖的其他代码仓，AI检视时可搜索其代码
- `language`：声明当前代码仓主要编程语言，用于提取对应语言tips

模板示例：

```markdown
---
link_repo: NCE-T/TransNeWebService,NCE-T/TransFrontendService
depend_repo: NCE-T/TransNeWebService,NCE-T/TransFrontendService
language: java,ts
---

# MR Reviewer Tips

本文件为代码仓的MR检视规则配置文件，放置于代码仓根目录，以下所有检视规则必须遵守。

### BIZ-001: [规则标题，使用命令式语言描述要检查什么]
- **检查锚点**: [AI重点扫描的关键字/代码模式/代码结构，多个用逗号分隔]
- **反例**: `[不好的代码片段]`
- **正例**: `[推荐的代码片段]`
```

## Codeagent3.0 权限配置

为了在 Codeagent3.0 中跳过文件操作的权限确认，可以在项目的 `.cac/settings.json` 或全局的 `~/.cac/settings.json` 中配置权限。

### 推荐配置

```json
{
  "permissions": {
    "allow": [
      "Write(C:/Users/<username>/.mr-reviewer/**)",
      "Edit(C:/Users/<username>/.mr-reviewer/**)",
      "Read(C:/Users/<username>/.mr-reviewer/**)",
      "Bash(touch:C:/Users/<username>/.mr-reviewer/**)",
      "Bash(echo:C:/Users/<username>/.mr-reviewer/**)",
      "Bash(mkdir:C:/Users/<username>/.mr-reviewer/**)",
      "Bash(python:*)",
      "Bash(cat:C:/Users/<username>/.mr-reviewer/**)"
    ]
  }
}
```

### 配置说明

| 配置项 | 说明 |
|--------|------|
| `Write/Directory/**` | 允许写入指定目录及子目录下的所有文件 |
| `Edit(Dir/**)` | 允许编辑指定目录下的文件 |
| `Read(Dir/**)` | 允许读取指定目录下的文件 |
| `Bash(touch:Dir/**)` | 允许创建空文件 |
| `Bash(echo:Dir/**)` | 允许使用 echo 重定向写入 |
| `Bash(mkdir:Dir/**)` | 允许创建目录 |
| `Bash(python:*)` | 允许执行 Python 脚本 |
| `Bash(cat:Dir/**)` | 允许使用 heredoc 写入 |

### 简化路径写法

如果权限配置不生效，可尝试简化为：

```json
{
  "permissions": {
    "allow": [
      "Write",
      "Edit",
      "Read",
      "Bash(touch:~/.mr-reviewer/**)",
      "Bash(echo:~/.mr-reviewer/**)",
      "Bash(mkdir:~/.mr-reviewer/**)",
      "Bash(python:*)",
      "Bash(cat:~/.mr-reviewer/**)"
    ]
  }
}
```

### 配置文件位置

1. **项目级配置**：`.cac/settings.json`（位于当前工作目录）
2. **全局配置**：`~/.cac/settings.json`（用户主目录）

建议在项目级配置，这样只对特定项目生效，更安全。

## 4.0版本发布说明
### 新增特性

### AI 语义级缺陷深度扫描（Step 1.5）

Stage 2 AI 深度分析新增 **Step 1.5 缺陷模式深度扫描**子步骤，5 组 AI Agent 并行对被修改函数的完整函数体进行语义级缺陷检测。

- **执行位置**：Step 1.5 与 Step 1（规则检视）并行执行，共享 Step 0 输出，二者都完成后才进入 Step 2 汇总
- **覆盖范围**：9 大类 36 项缺陷模式（并发安全、数值计算、类型系统、指针操作、资源管理、内存操作、内存计算、赋值与引用、错误处理）
- **结果融合**：Step 2 将 Step 0 + Step 1 + Step 1.5 三路结果合并去重，同一问题优先保留 Step 1.5 的结构化缺陷信息

### 本地模式新增 commit 检视模式

本地模式下新增 **commit 检视模式**，支持基于 git commit 的增量变更进行 AI 检视，包含单 commit 与 commit 区间两种子模式：

- **单 commit 模式**：`--commit <commit_hash>`，检视指定 commit 的变更，提供本地代码仓地址和单个commit hash 进行检视
- **commit 区间模式**：`--baseCommit <原commit> --headCommit <后commit>`，检视两个 commit 之间的累积变更，提供本地代码仓和原commit 和后commit进行检视

## 变更明细

- 版本号：3.5.7 → 4.0.0
- Stage 2 子步骤从 3 个（Step 0-2）扩展为 4 个（Step 0、Step 1、Step 1.5、Step 2）
- 新增本地的commit检视模式
- todowrite 任务描述更新为 `Stage 2: AI深度分析（Step0理解+Step1规则检视+Step1.5缺陷扫描+Step2汇总）`

## QA

### QA1：onebox因权限问题上传失败 
**解决方案**：访问 [onebox 个人设置](https://onebox.huawei.com/myFlow#setup)，修改账户类型到 R&D User,即修改更改角色为研发云盘，[详见文档](https://portal.edevops.huawei.com/siku/project/ge79161e2454d4771b44305685ffd7bb2/wiki/7308/163443/WIKI2026072111939224?title=QA1-onebox%E5%9B%A0%E6%9D%83%E9%99%90%E9%97%AE%E9%A2%98%E4%B8%8A%E4%BC%A0%E5%A4%B1%E8%B4%A5#:~:text=QA-,QA1%EF%BC%9Aonebox%E5%9B%A0%E6%9D%83%E9%99%90%E9%97%AE%E9%A2%98%E4%B8%8A%E4%BC%A0%E5%A4%B1%E8%B4%A5,-%E8%A7%A3%E5%86%B3%E6%96%B9%E6%A1%88%EF%BC%9A%E8%AE%BF%E9%97%AE)