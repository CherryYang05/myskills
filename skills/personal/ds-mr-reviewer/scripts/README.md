# MR Review Scripts

本目录下的脚本按功能和执行顺序组织到不同的子目录中，每个子目录内的脚本按执行顺序排列。

## 目录结构

| 目录 | 说明 |
|------|------|
| `0-clean-temp/` | 清理过期临时文件（步骤0） |
| `1-prepare-data/` | 数据准备（步骤1） |
| `2-ai-analysis/` | AI分析支持（步骤2） |
| `3-generate-report/` | 生成报告+上传OneBox（步骤3） |
| `4-submit-review/` | 提交MR评论（步骤4） |
| `5-welink-notify/` | 发送WeLink通知（步骤5） |
| `common/` | 通用脚本（可被多个步骤调用） |

---

## 脚本详细说明

### 0-clean-temp/ - 清理临时文件

#### cleanup_temp.py

**作用**：清理过期的临时文件和代码仓，临时文件超过7天、代码仓超过15天自动清理。

**输入**：
- `--retentionDays`（可选）：保留天数（已废弃，固定为7天）

**输出**：
- 成功：打印清理的文件数量和路径
- 失败：打印错误信息

**清理策略**：
- 删除所有超过7天的MR子目录（`~/.mr-reviewer/temp/mr_{repo}_{mrId}/`）
- 删除所有超过15天的代码仓目录（`~/.mr-reviewer/project/`）
- 清理~/.mr-reviewer/temp目录下的其他过期文件

---

### 1-prepare-data/ - 数据准备

#### mr_coordinator.py

**作用**：协调器，自动依次执行MR检视的数据准备步骤：解析MR URL → 获取MR信息 → 准备代码仓 → 加载检视规则，输出统一JSON供AI分析。

**输入**：
- `--mrUrl`（必需）：MR URL，支持CodeHub/GitLab/GitHub格式
- `--outputFile`（可选）：输出JSON文件路径
- `--format`（可选）：输出格式，可选`json`或`human`，默认`json`
- `--debug`（可选）：调试模式，不清理临时文件

**输出**：
- 统一JSON文件，包含MR信息、diffs、代码仓路径、检视规则

**执行流程**：
```
Step 1/4: 解析MR链接 → Step 2/4: 获取MR信息 → Step 3/4: 准备代码仓 → Step 4/4: 加载检视规则
```

**使用示例**：
```bash
python scripts/1-prepare-data/mr_coordinator.py --mrUrl "https://codehub-y.huawei.com/NCE-T/TxL0L1ServiceV3/merge_requests/15217"
```

---

#### mr_parse.py

**作用**：从MR URL提取代码仓名称、MR ID和project ID。

**输入**：
- `--mrUrl`（必需）：MR URL

**输出**：
```json
{
  "repository_name": "NCE-T/TxL0L1ServiceV3",
  "mr_id": "15217",
  "mr_url": "https://codehub-y.huawei.com/..."
}
```

---

#### mr_fetcher.py

**作用**：通过CodeHub API获取MR描述、diff文件、作者信息，自动过滤测试文件和自检项内容。

**输入**：
- `--repository_name`（必需）：代码仓完整路径
- `--mrId`（必需）：MR ID
- `--configPath`（可选）：config.json路径
- `--format`（可选）：输出格式，可选`human`或`json`，默认`human`
- `--outputFile`（可选）：输出文件路径

**输出**：
- 包含MR标题、描述（已过滤）、diffs、作者信息、目标分支等

---

#### mr_repo_manager.py

**作用**：克隆或更新本地代码仓库，切换到目标分支。

**输入**：
- `--repository_name`（必需）：代码仓名称
- `--branch`（必需）：目标分支名称
- `--repoPath`（可选）：本地代码仓基础路径
- `--configPath`（可选）：config.json路径
- `--format`（可选）：输出格式，可选`human`或`json`，默认`json`

**输出**：
- 包含`repo_path`的JSON对象

---

#### mr_rules_loader.py

**作用**：加载检视规则，按照通用规则、代码仓规则（`mr_reviewer_rules.md`或`mr_reviewer_tips.md`）、linked repo规则、语言规则的优先级顺序。

**输入**：
- `--repoPath`（必需）：代码仓本地路径
- `--repoName`（可选）：代码仓名称
- `--mrInfoFile`（必需）：MR信息JSON文件路径
- `--targetBranch`（可选）：目标分支
- `--format`（可选）：输出格式，可选`json`或`human`，默认`json`

**输出**：
```json
{
  "all_rules_combined": "所有规则合并内容...",
  "all_tips_combined": "（已废弃，同all_rules_combined）",
  "rule_ids": ["COM-001", "JAVA-SEC-001", ...]
}
```

---

### 2-ai-analysis/ - AI分析支持

#### mr_diff_reader.py

**作用**：从协调器输出的JSON文件中读取完整的diff内容。解决AI直接读取JSON文件时因Read工具输出限制导致diff信息不完整的问题。

**输入**：
- 第一个参数（必需）：协调器输出的JSON文件路径
- `--file`（可选）：只输出指定文件的diff

**输出格式**：
```
---DIFF_START---
<完整的diff内容>
---DIFF_END---
---METADATA---
{
  "total_files": <文件数>,
  "files": [...],
  "total_diff_length": <总diff长度>
}
---METADATA_END---
```

**使用示例**：
```bash
# 方式1：使用repo和mrId参数（推荐）
python scripts/2-ai-analysis/mr_diff_reader.py --repo "NCE-T_TxL0L1ServiceV3" --mrId 15217

# 方式2：使用完整文件路径（兼容旧方式）
python scripts/2-ai-analysis/mr_diff_reader.py ~/.mr-reviewer/temp/mr_NCE-T_TxL0L1ServiceV3_15217/mr_coordinator.json
```

---

### 3-generate-report/ - 生成报告+上传OneBox

#### validate_report_format.py

**作用**：验证生成的MR检视报告是否符合格式要求，检查是否使用了markdown表格语法（禁止使用表格）。

**输入**：
- 第一个参数：报告文件路径

**输出**：
- 成功：打印`[PASS] 未发现表格语法`和`[RESULT] 验证通过!`
- 失败：打印`[FAIL] 发现表格语法:`和具体行号

**检查规则**：
- 扫描markdown文件中的表格语法 `| xxx |`
- 自动跳过代码块（```）内的内容

---

#### upload_report_to_onebox.py

**作用**：将生成的MR检视报告上传到OneBox指定目录，并生成全员可访问的分享链接。

**输入**：
- `--repo`（必需）：仓库名称
- `--mrId`（必需）：MR ID

**输出**：
- 成功：打印分享链接
- 失败：打印错误信息

---

### 4-submit-review/ - 提交MR评论

#### mr_note_poster.py

**作用**：提交Note全局评论到MR（检视完成通知），支持重复检测。

**输入**：
- `--mrInfoFile`（必需）：mr_coordinator.json文件路径
- `--shareUrl`（可选）：OneBox分享链接（未指定则从coordinator读取）
- `--configPath`（可选）：config.json路径
- `--force`（可选）：强制提交，跳过重复检测

**重复检测**：
- 检查MR是否已存在包含`MR代码检视完成`关键词的Note
- 如果存在则跳过提交，避免重复

**输出**：
- 成功：打印`[SUCCESS] Note posted successfully`
- 失败：打印错误信息

---

#### mr_discussion_poster.py

**作用**：读取mr_risks.json，按风险级别过滤后提交带位置的Discussion评论到MR。

**输入**：
- `--mrInfoFile`（必需）：mr_coordinator.json文件路径
- `--risksFile`（必需）：mr_risks.json文件路径
- `--configPath`（可选）：config.json路径
- `--force`（可选）：强制提交，跳过重复检测

**过滤规则**：
- 从config.json读取`send_discussion_level`配置（默认`["高", "中"]`）
- 只提交符合配置级别的风险
- 部分失败跳过继续下一条，不回退

**severity映射**：
- 高 → major
- 中 → minor
- 低 → suggestion

**输出**：
- 成功：打印成功/失败统计
- 失败：打印错误信息

---

### 5-welink-notify/ - 发送WeLink通知

#### mr_welink_notifier.py

**作用**：发送Welink消息通知MR检视结果，可自动识别接收者UID。

**输入**：
- `--mrInfoFile`（可选）：MR信息JSON文件路径
- `--mrInfo`（可选）：MR信息JSON字符串
- `--mrTitle`（可选）：MR标题
- `--mrUrl`（可选）：MR链接
- `--riskLevel`（可选）：风险等级，可选`高`、`中`、`低`
- `--authorName`（可选）：MR提交者姓名
- `--authorId`（可选）：MR提交者工号
- `--reportPath`（可选）：检视报告文件路径
- `--configPath`（可选）：config.json路径
- `--shareUrl`（可选）：OneBox分享链接

**输出**：
- 成功：打印`[SUCCESS] Notification sent successfully`
- 失败：打印错误信息

---

#### mr_notify_after_analysis.py

**作用**：AI分析完成后发送WeLink通知，从coordinator读取risk_level和report_share_url。

**输入**：
- `--mrInfoFile`（必需）：mr_coordinator.json文件路径
- `--reportPath`（必需）：检视报告文件路径
- `--configPath`（可选）：config.json路径

**执行流程**：
1. 从coordinator读取risk_level和report_share_url
2. 调用mr_welink_notifier.py发送通知

---

### common/ - 通用脚本

#### temp_file_path_helper.py

**作用**：生成正确的临时文件路径，供AI直接写入JSON文件使用。避免Shell转义问题。

**输入**：
- `--type`（必需）：文件类型，如`analysis_stage0`、`analysis_stage1`、`analysis_stage2`、`coordinator`、`mr_risks`
- `--repo`（必需）：代码仓名称
- `--mrId`（必需）：MR ID

**输出**：
- 返回完整的文件路径（绝对路径）

**文件路径**：`~/.mr-reviewer/temp/mr_{repo}_{mrId}/{type}.json`

**使用示例**：
```bash
# 步骤1：获取路径
python scripts/common/temp_file_path_helper.py --type analysis_stage1 --repo "NCE-T/TransCapacityMapService" --mrId 1830
# 输出: C:\Users\username\.mr-reviewer\temp\mr_NCE-T_TransCapacityMapService_1830\analysis_stage1.json

# 步骤2：AI使用write工具直接写入
write("C:\\Users\\username\\.mr-reviewer\\temp\\mr_NCE-T_TransCapacityMapService_1830\\analysis_stage1.json", json_content)
```

---

#### temp_file_reader.py

**作用**：临时文件读取器，统一的临时文件读取脚本。

**输入**：
- `--type`（必需）：文件类型
- `--repo`（必需）：代码仓名称
- `--mrId`（必需）：MR ID
- `--raw`（可选）：输出原始文本内容，不解析 JSON（用于处理格式错误的 JSON）

**输出**：
- 默认：文件内容（JSON 格式）
- 使用 `--raw`：原始文本内容

**文件路径**：`~/.mr-reviewer/temp/mr_{repo}_{mrId}/{type}.json`

**使用示例**：
```bash
# 正常模式（JSON 格式）
python scripts/common/temp_file_reader.py --type coordinator --repo "NCE-T/TxL0L1ServiceV3" --mrId 15273

# 原始模式（处理 JSON 格式错误）
python scripts/common/temp_file_reader.py --type coordinator --repo "NCE-T/TxL0L1ServiceV3" --mrId 15273 --raw
```

---

#### check_prerequisites.py

**作用**：检查运行环境和依赖配置。

**输入**：
- `--fix`（可选）：自动修复某些问题
- `--skill_dir`（可选）：skill根目录路径

**输出**：
- 检查结果报告

---

## 依赖关系

各脚本的调用顺序和数据流：

```
步骤0: cleanup_temp.py（清理过期临时文件，每次启动skill时自动执行）

步骤1: mr_coordinator.py（协调器，一键执行以下4步）
    ├── Step 1: mr_parse.py（解析MR URL）
    │       ↓ 输出: repository_name, mr_id
    ├── Step 2: mr_fetcher.py（获取MR信息）
    │       ↓ 输出: mr_info（含target_branch）
    ├── Step 3: mr_repo_manager.py（准备代码仓）
    │       ↓ 输出: repo_path
    └── Step 4: mr_rules_loader.py（加载检视规则）
            ↓ 输出: rules
                ↓ 输出统一JSON: ~/.mr-reviewer/temp/mr_{repo}_{mrId}/mr_coordinator.json

步骤2: AI深度分析（由模型执行，读取协调器输出JSON）
    ├── mr_diff_reader.py（读取完整diff内容）
    ├── temp_file_path_helper.py（生成文件路径）
    ├── AI通过write工具直接写入各阶段输出（避免Shell转义）
    └── 阶段输出文件: ~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage{0,1,2}.json

步骤3: 生成报告+上传OneBox
    ├── temp_file_reader.py（读取阶段3输出）
    ├── AI生成报告
    ├── validate_report_format.py（验证报告格式）
    ├── upload_report_to_onebox.py（上传报告到OneBox）
    ├── AI更新coordinator（写入risk_level和report_share_url）
    └── AI生成mr_risks.json

步骤4: 提交MR评论
    ├── mr_note_poster.py（提交Note全局评论）
    └── mr_discussion_poster.py（提交Discussion带位置评论，条件执行）

步骤5: 发送WeLink通知
    └── mr_notify_after_analysis.py
        └── 调用 mr_welink_notifier.py（发送Welink通知）

临时文件由步骤0的cleanup_temp.py统一清理
```

**关键数据文件**：
- `~/.mr-reviewer/temp/mr_{repo}_{mrId}/mr_coordinator.json` - 协调器输出文件
- `~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage0.json` - 阶段0分析输出（理解与文件检视）
- `~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage1.json` - 阶段1分析输出（规则检视）
- `~/.mr-reviewer/temp/mr_{repo}_{mrId}/analysis_stage2.json` - 阶段2分析输出（风险评估与报告格式化）
- `~/.mr-reviewer/temp/mr_{repo}_{mrId}/mr_risks.json` - 风险数据文件（供Discussion提交使用）
- 检视报告路径 - `~/.mr-reviewer/temp/mr_{repo}_{mrId}/mr_review_report_{repo}_{mr_id}_{risk_level}.md`

---

## 配置依赖

所有脚本均依赖 `config.json` 配置文件（位于skill根目录），详细配置说明请参考 [SKILL.md](../SKILL.md#配置说明)。

```json
{
  "codehub_token": "YOUR_CODEHUB_TOKEN_HERE",
  "welink_token": "YOUR_WELINK_TOKEN_HERE",
  "onebox_share_directory_url": "https://onebox.huawei.com/#file/1/xxx",
  "onebox_username": "your_w3_username",
  "onebox_password": "your_w3_password",
  "exclude_file_suffix": ".flex,.lightdt",
  "welink_notify_ids": "s00633127,93065411204198",
  "send_discussion_level": ["高", "中"]
}
```

**文件存储路径**：
- 临时文件：`~/.mr-reviewer/temp/mr_{repo}_{mrId}/`
- 代码仓：`~/.mr-reviewer/project/`