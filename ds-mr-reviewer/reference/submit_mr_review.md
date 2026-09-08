> **【强制声明】本文档为步骤4（提交MR评论）的完整执行流程。AI在执行步骤4时，必须完整阅读本文档并严格按照所有规定执行，不得跳过任何步骤或修改既定逻辑。**

# 提交MR检视评论流程

本文档描述步骤4的详细执行流程：提交Note全局评论和Discussion带位置评论。

## 步骤4：提交MR评论

### 4.1 提交Note评论

Note是MR的全局评论，用于通知MR作者检视已完成。

```bash
python scripts/4-submit-review/mr_note_poster.py --repo "{repo}" --mrId {mrId}
```

---

### 4.2 判断是否需要提交Discussion

**执行脚本**：
```bash
python scripts/4-submit-review/check_send_discussion.py \
    --mode <review|fix|local> \
    --mrInfoFile <coordinator路径> \
    --riskLevel <高|中|低>
```

**参数说明**：
- `--mode`：运行模式，与步骤4.5的`--mode`保持一致
- `--mrInfoFile`：mr_coordinator.json路径
- `--riskLevel`：当前MR风险等级（高/中/低），用于判断是否需要提交Discussion

**AI判断逻辑**：
- 脚本输出`SKIP_DISCUSSION` → **结束步骤4，无需提交Discussion**
- 脚本输出`send_discussion_level=...`（无`SKIP_DISCUSSION`）→ **继续执行步骤4.3**
- 如果输出`EMPTY`（配置为空或不存在）→ **结束步骤4，无需提交Discussion**

---

### 4.3 生成mr_risks.json

**前置条件**：步骤4.2判断需要提交Discussion

**执行步骤**：

1. 获取路径：
   ```bash
   python scripts/common/temp_file_path_helper.py --type mr_risks --repo "{repo}" --mrId {mrId}
   ```

2. 从analysis_stage2.json提取风险数据，生成mr_risks.json：
   - 读取analysis_stage2.json
   - 提取high_risks、medium_risks、low_risks数组
   - 合并为risks数组，每条风险添加risk_level字段
   - 统计total_count和summary（high/medium/low数量）

**mr_risks.json格式**：
```json
{
  "risks": [
    {
      "id": 1,
      "risk_level": "高",
      "problem": "问题描述",
      "file_path": "src/main/java/com/huawei/SomeFile.java",
      "line_number": 131,
      "description": "风险详情",
      "mitigation": "消减措施"
    }
  ],
  "total_count": 2,
  "summary": {
    "high": 0,
    "medium": 2,
    "low": 0
  }
}
```

**完成标志**：
- [ ] mr_risks.json已生成到正确路径
- [ ] 所有风险已包含risk_level字段
- [ ] total_count和summary统计正确

---

### 4.4 行号校验与修正

**前置条件**：步骤4.2判断需要提交Discussion

**目的**：基于MR diff重新计算并修正mr_risks.json中的行号，确保提交到正确的行

**执行步骤**：

1. 调用行号校验脚本：
   ```bash
   python scripts/4-submit-review/check_and_fix_line_numbers.py \
       --mrInfoFile <coordinator路径> \
       --risksFile <mr_risks路径>
   ```

2. 检查脚本返回结果：
   - **退出码0**：脚本成功完成，所有行号已自动修正，无需人工介入 → 继续步骤4.5
   - **退出码2**：脚本输出`[MANUAL_CHECK_REQUIRED]`，需要AI人工确认并修正剩余行号

3. **AI兜底逻辑**（当脚本无法自动处理时）：
   - 读取coordinator.json获取MR diffs信息
   - 对每条需要人工确认的风险，根据风险描述中的关键代码片段在diff的new版本中搜索定位
   - 直接修正mr_risks.json中的line_number字段
   - 使用write工具重新写入修正后的mr_risks.json

**完成标志**：
- [ ] 行号校验脚本已执行
- [ ] 脚本无法处理的行号已由AI人工修正
- [ ] 所有风险的position参数对应的行号在diff中确实存在

---

### 4.4.5 选择需要转 Issue 的检视意见

**本地模式跳过此步骤。**

**执行步骤**：

1. 读取 mr_risks.json，提取所有风险的摘要（序号、级别、问题描述、文件:行号）
2. 按级别排序：高 → 中 → 低
3. 使用交互工具向用户提问，要求一次性展示所有批次，不要分多次调用。每个批次作为一个独立的问题，所有批次在同一轮交互中一起呈现给用户。
4. 收集所有批次中用户选中的风险序号
5. 汇总所有选中的序号，传给步骤 4.5 的 `--issueRisks` 参数

**【强制】每批提问必须包含检视报告路径**：

每个批次的提问文字中**必须**包含本地检视报告的完整路径，供用户参考。路径格式固定为：

```
~/.mr-reviewer/temp/mr_{repo}_{mrId}/mr_review_report_{repo}_{mrId}_{risk_level}.md
```

其中 `{repo}` 中的 `/` 替换为 `_`，`{risk_level}` 为 `high`/`medium`/`low`（来自 analysis_stage2.json 的 risk_level 字段：高→high、中→medium、低→low）。

**每批选项格式**：

每条风险直接作为可勾选的选项展示，格式为：
```
   {序号}. [{级别}] {问题描述} ({文件}:{行号})
  ...
```

**选项内容**：直接把每条风险的序号、级别、问题描述、文件:行号作为选项label展示，不额外加工。

**分批规则**：
- 每批展示最多 4 条风险
- 按高级别优先顺序依次填充：高 → 中 → 低，每填满 4 条开新一批，最后一批不足 4 条也正常提交
- **批次数不固定**，由实际风险总数决定：N条风险需要 ceil(N/4) 批，必须覆盖全部风险，禁止遗漏任何一条

**单次交互效果示例**（假设有6条风险，分2批，仓库为 NCE-T_TransFeatureQKD，MR ID 1234，风险等级 medium）：

第1批（AskUserQuestion 工具参数）：
- **question**: "以下检视意见是否需要转 Issue？（可多选，详细内容可参考本地检视报告：~/.mr-reviewer/temp/mr_NCE-T_TransFeatureQKD_1234/mr_review_report_NCE-T_TransFeatureQKD_1234_medium.md）"
- **options**:
  - label: "1. [高] EncryptionPwd函数return语句缺少分号 (gaussdb_lib.c:63)"
  - label: "2. [高] 硬编码密钥存在泄露风险 (config.py:15)"
  - label: "3. [中] InitKmca调用和if判断合并到同一行 (gaussdb_lib.c:79)"
  - label: "4. [中] 日志描述不符合英文陈述句规范 (gaussdb_lib.c:89)"

第2批（AskUserQuestion 工具参数）：
- **question**: "以下检视意见是否需要转 Issue？（可多选，详细内容可参考本地检视报告：~/.mr-reviewer/temp/mr_NCE-T_TransFeatureQKD_1234/mr_review_report_NCE-T_TransFeatureQKD_1234_medium.md）"
- **options**:
  - label: "5. [低] DecryptionPwd函数中新增多余连续空行 (gaussdb_lib.c:74)"
  - label: "6. [低] hsw_main.c中空行位置调整无实质意义 (hsw_main.c:41)"

**用户未选中任何风险时**：`--issueRisks` 参数不传，所有风险仅提交 Discussion。

---

### 4.5 提交Discussion（条件执行）

**前置条件**：步骤4.2判断需要提交Discussion

Discussion是带位置的评论，直接定位到代码的具体文件和行号。

**执行步骤**：

1. 获取mr_risks.json路径：
   ```bash
   python scripts/common/temp_file_path_helper.py --type mr_risks --repo "{repo}" --mrId {mrId}
   ```

2. 调用mr_discussion_poster.py提交Discussion：
   ```bash
   python scripts/4-submit-review/mr_discussion_poster.py \
       --mrInfoFile <coordinator路径> \
       --risksFile <mr_risks.json路径> \
       --mode <review|fix|local> \
       --issueRisks <逗号分隔的序号，如1,3>
   ```

   **--issueRisks**：可选，步骤4.4.5中用户选择需要转Issue的风险序号(1-based)，逗号分隔。不传则所有风险仅提交Discussion。

**Discussion内容格式**：
```
⚠️ {emoji} {风险级别}风险问题

**问题位置：** {file_path}:{line_number}

**问题描述：** {description}

**消减措施：** {mitigation}
```

**severity映射**：
- 高 → major
- 中 → minor
- 低 → suggestion

**失败策略**：部分失败跳过继续下一条，统计成功/跳过重复/失败数。Discussion失败不影响Note。

**参数说明**：
- `--mrInfoFile`：必填，mr_coordinator.json路径
- `--risksFile`：必填，mr_risks.json路径
- `--force`：可选，强制提交跳过去重检测
- `--mode`：必填，运行模式，决定是否上报场景数据
- `--issueRisks`：可选，需要转Issue的风险序号列表(1-based)，逗号分隔，如`1,3,5`

**--mode 参数取值**：

| 值 | 模式 | 场景数据上报 |
|----|------|-------------|
| `review` | 检视模式（默认） | 提交Discussion后自动上报AI检视场景数据到表2 |
| `fix` | 修复模式 | 仅提交Discussion，不上报场景数据（由review-fix agent统一上报） |
| `local` | 本地模式 | 仅提交Discussion，不上报场景数据 |
