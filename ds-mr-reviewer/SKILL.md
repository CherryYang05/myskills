---
name: ds-mr-reviewer
description: MR代码检视工具。提供MR URL，自动分析代码变更、识别功能风险、给出验证场景建议、生成检视报告并发送WeLink通知。当用户提供检视代码的url链接，并且url包含codehub时，必须使用此技能。也支持本地仓库路径输入。
author: wangchaoju
category: task-review
version: 4.0.0
---

[点击查看给人类的说明书，AI不需要看这个链接](https://agent.huawei.com/ai/skills/ds-mr-reviewer?tab=readme)

# DS MR Reviewer Skill

## 检测模式选择

## 功能说明

从 MR 链接自动提取代码变更信息，基于本地项目代码仓库、MR 描述、diff 文件和自定义检视规则进行全面的代码检视。

**重点关注：**

- 功能修改引入的风险（业务逻辑、性能、边界场景、数据一致性等）
- 黑盒验证场景的完整性，以及必须要补充的验证场景建议

---

## 模式判断

**判断规则：**
- 默认为检视模式（完整5个Stage）
- 当调用参数包含 `模式：修复模式` 时，进入修复模式（完整5个Stage，结束后返回风险JSON给调用方）
- 当调用参数包含 `本地模式` 或提供了本地仓库路径（`--repoPath`）时，进入本地模式（仅Stage 1+2+3，跳过Stage 4+5）
  - 若同时提供 `--commit`，则基于指定 commit 的变更进行检视
  - 若同时提供 `--baseCommit` + `--headCommit`，则基于两个 commit 之间的累积变更进行检视（区间模式）

**三种模式的区别：**

| 维度 | 检视模式 | 修复模式 | 本地模式 |
|------|---------|---------|---------|
| 触发方式 | 默认 | `模式：修复模式` | `--repoPath` |
| Stage 1 数据来源 | `mr_coordinator.py` | `mr_coordinator.py` | `local_coordinator.py` |
| Stage 4（提交Discussion/Note） | 执行 | 执行 | **跳过** |
| Stage 5（WeLink通知） | 执行 | 执行 | **跳过** |
| 结束后返回风险JSON | 否 | **是** | **是** |

---

## 必须遵守的限制约束

- 必须严格按照规定的Stage执行
- AI 主导流程控制，根据需要调用 Python 脚本工具
- 临时文件，统一在 `~/.mr-reviewer/temp/` 目录下

---

## 检查前置条件

**【强制】每次执行检视流程前，必须先运行前置条件检查，不可跳过！此步骤会自动检测并升级 skill 到市场最新版本。**

```bash
python scripts/common/check_prerequisites.py
```

详细前置条件检查请参考：[前置条件检查](reference/prerequisites.md)

---

## 执行检视流程

**【重要】开始执行前，必须先用 todowrite 工具创建以下任务列表，后续每完成一项必须更新其状态为 completed：**

**检视模式或修复模式：**
```
todowrite --todos [
  {content: "Stage 1: 准备数据", status: "pending", priority: "high"},
  {content: "Stage 2: AI深度分析", status: "pending", priority: "high"},
  {content: "Stage 3: 生成检视报告", status: "pending", priority: "high"},
  {content: "Stage 4: 提交MR评论", status: "pending", priority: "high"},
  {content: "Stage 5: 发送WeLink通知", status: "pending", priority: "high"}
]
```

**本地模式：**
```
todowrite --todos [
  {content: "Stage 1: 准备数据", status: "pending", priority: "high"},
  {content: "Stage 2: AI深度分析", status: "pending", priority: "high"},
  {content: "Stage 3: 生成检视报告", status: "pending", priority: "high"}
]
```


**完成标志更新规则**：
- 每完成一个Stage，必须立即用todowrite将该Stage状态更新为completed
- **禁止**在未完成当前Stage的情况下跳到下一个Stage

### Stage 0：清理临时文件

**重要**：每次启动skill时，首先执行清理操作，删除过期的临时文件。

```bash
python scripts/0-clean-temp/cleanup_temp.py
```

### Stage 1：准备数据

#### MR模式（有MR链接）

如果 MR URL 路径中不包含 `manifest`，说明是普通 MR；否则是 Manifest MR（含多个子 MR）。

**普通 MR：**

```bash
python scripts/1-prepare-data/mr_coordinator.py --mrUrl "<MR_URL>"
```

输出文件：`~/.mr-reviewer/temp/mr_{repo}_{mr_id}/mr_coordinator.json`，**记住`{repo}`和`{mr_id}`，后面调用脚本会经常使用。**

**Manifest MR（含多个子 MR）：**

```bash
python scripts/1-prepare-data/manifest-review/manifest_coordinator.py --mrUrl "<MANIFEST_MR_URL>"
```

manifest 模式下会为 manifest 自身和每个子 MR 分别调用 `mr_coordinator.py` 生成独立的 coordinator JSON，并输出 `manifest_summary.json` 到 `~/.mr-reviewer/temp/manifest_{repo}_{mrId}/manifest_summary.json`。

后续 AI 分析时读取 `manifest_summary.json` 中的 `coordinator_path` 逐个子 MR 读取 diff 进行分析。**记住`{repo}`和`{mr_id}`，后面调用脚本会经常使用。**

#### 本地模式或提供了本地仓库路径

```bash
# 分支对比模式
python scripts/1-prepare-data/local_coordinator.py --repoPath "<仓库路径>" --branch "<目标分支>"

# Commit 模式
python scripts/1-prepare-data/local_coordinator.py --repoPath "<仓库路径>" --commit "<commit_hash>"

# Commit 区间模式
python scripts/1-prepare-data/local_coordinator.py --repoPath "<仓库路径>" --baseCommit "<原commit>" --headCommit "<后commit>"
```

**输入参数：**
- `--repoPath`（必需）：本地代码仓路径
- `--branch`：目标分支名，与 `--commit` 或 `--baseCommit/--headCommit` 二选一
- `--commit`：Commit hash，与 `--branch` 或 `--baseCommit/--headCommit` 二选一
- `--baseCommit`：原 commit hash，与 `--headCommit` 配合使用，构成区间模式
- `--headCommit`：后 commit hash，与 `--baseCommit` 配合使用，构成区间模式
- `--repoName`（可选）：代码仓名称，默认从路径推断

**diff来源：**
- 分支模式：`git diff {branch}...HEAD`（已提交变更） + `git diff`（未提交修改）
- Commit 模式：`git diff {commit}^..{commit}`（指定 commit 的变更）
- 区间模式：`git diff {baseCommit} {headCommit}`（两个 commit 之间的累积变更）

**输出：** `~/.mr-reviewer/temp/mr_{repo}_{mrId}/mr_coordinator.json`
- 分支模式：`mrId` 为 `"local"`
- Commit 模式：`mrId` 为 commit 短 hash
- 区间模式：`mrId` 为 `{baseCommit短hash}_{headCommit短hash}`

**记住`{repo}`和`{mrId}`，后面 Stage 2/3 调用脚本会经常使用。**

后续 Stage 2/3 的执行流程与 MR 模式完全一致，无感知差异。

#### 规则文件规范化迁移（必执行步骤）

无论是执行的 MR 模式还是本地模式，在生成 `mr_coordinator.json` 之后，**必须**执行以下脚本。该脚本会自动检查目标代码仓，将遗留的旧检视规则文件统一迁移到标准的 `.ai-coding/review/` 目录下，以便后续 Stage 统一加载：

```bash
python scripts/1-prepare-data/migrate_rules.py --repoPath "<代码仓的本地绝对路径>"
```

### Stage 2：AI 深度分析

**【强制】必须完整阅读并严格按照以下文档执行：** [AI 分析技术细节](reference/ai_analysis.md)

**注意**：Stage 2包含Step 0-2三个子步骤，在所有Step完成后，才将Stage 2标记为completed。

**Manifest MR 模式：** 如果 Stage 1 执行后检测到 `~/.mr-reviewer/temp/manifest_{repo}_{mrId}/manifest_summary.json` 存在，则进入 manifest MR 模式：
1. 先读取 `manifest_summary.json`，获取 `manifest_mr.coordinator_path` 和 `sub_merge_requests[].coordinator_path`
2. 逐个读取各 coordinator JSON 中的 diff，分析每个子 MR 的代码变更
3. 汇总所有子 MR + manifest 自身的风险，统一评定风险等级

### Stage 3：生成检视报告

**执行步骤：**

1. **获取报告文件名**：
   ```bash
   python scripts/common/generate_report_filename.py --repo "{repo}" --mrId {mrId}
   ```

2. **读取阶段2输出**：
   ```bash
   python scripts/common/temp_file_reader.py --type analysis_stage2 --repo "{repository_name}" --mrId {mr_id}
   ```

3. **生成报告**：读取 `reference/report_template.md`，从 `analysis_stage2.json` 和历史信息中提取字段填充模板：
   - 填充MR基本信息（URL、标题、作者、分支等）
   - 填充风险分析结果（高/中/低风险、风险数量）
   - 填充变更意图、核心变更、潜在问题
   - 按优先级（高/中/低）分类验证场景
   - **禁止使用markdown的表格语法，使用列表替代**

4. **验证报告格式**：
   ```bash
   python scripts/3-generate-report/validate_report_format.py <报告路径>
   ```
   - 验证通过（`"success": true`）：继续执行
   - 验证失败（`"success": false`）：修正问题后重新验证

5. **上传报告并更新coordinator**（必须执行）：
   ```bash
   python scripts/3-generate-report/upload_report_to_onebox.py --repo "{repo}" --mrId {mrId}
   ```

**报告存储路径**：`~/.mr-reviewer/temp/mr_{repo}_{mrId}/`

### Stage 4：提交MR评论（本地模式跳过）

**本地模式下直接跳过此Stage。**

**【强制】必须完整阅读并严格按照以下文档执行：** [提交MR评论流程](reference/submit_mr_review.md)

### Stage 5：发送WeLink通知（本地模式跳过）

**本地模式下直接跳过此Stage。**

调用WeLink通知脚本（路径自动计算）：

```bash
python scripts/5-welink-notify/mr_notify_after_analysis.py \
    --repo "{repo}" \
    --mrId {mrId}
```

---

## 修复模式/本地模式结束

修复模式和本地模式结束后，需要返回风险JSON给调用方（如review-fix agent），用于自动修复。

**本地模式：** Stage 3 完成后即结束流程，不执行Stage 4（提交MR评论）和Stage 5（WeLink通知），直接返回风险JSON。

**修复模式：** 5个Stage全部执行完成后，返回风险JSON。

**返回格式：**

```json
{
   "risk_level": "高/中/低",
   "issue_count": {
      "high": 0,
      "medium": 0,
      "low": 0
   },
   "high_risks": [
      {
         "id": "R001",
         "problem": "问题描述",
         "problem_code": "必填，原样复制diff中出现的问题代码行",
         "file_path": "文件路径",
         "line_number": "行号",
         "description": "详细描述",
         "mitigation": "修复建议"
      }
   ],
   "medium_risks": [],
   "low_risks": [],
   "report_url": "OneBox报告链接",
   "repo": "仓库名",
   "mrId": "MR ID",
   "repository": {
      "local_path": "代码仓本地路径"
   },
   "source_branch": "MR源分支名"
}
```

**数据来源：** 从 `analysis_stage2.json` 中提取风险列表，从 `mr_coordinator.json` 中提取仓库和MR信息。

---

**skill执行过程中产生文件的存储路径**：

- 临时文件：`~/.mr-reviewer/temp/mr_{repo}_{mrId}/`
- 代码仓：`~/.mr-reviewer/project/`（可通过 `clone_repo_path` 配置）