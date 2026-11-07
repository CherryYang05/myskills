# MR检视报告

**MR信息：**
- MR链接：{{mr_url}}
- 目标分支：{{target_branch}}
- 标题：{{mr_title}}
- 作者：{{author_name}}

---

## 一、变更概要

- 修改文件数：{{changed_files_count}}

**变更文件列表：**
{{changed_files_list}}

---

## 二、结论

**风险等级：{{risk_level}}**
**问题数量：{{issue_count}}**

**建议操作：{{recommended_action}}**

---

## 三、风险发现

### 高风险问题

{{high_risk_section}}

### 中风险问题

{{medium_risk_section}}

### 低风险问题

{{low_risk_section}}

---

## 四、详细分析

**本次MR的意图：**
{{change_intention}}

**核心修改：**
{{core_changes}}

**潜在问题：**
{{potential_issues}}

---

## 五、验证场景建议

**基于风险点的测试场景：**
{{dimension1_scenarios}}

**功能拓展场景：**
{{dimension2_scenarios}}

**基于变更与项目上下文的测试场景：**
{{dimension3_scenarios}}

---

>Powered By [ds-mr-reviewer SKILL](https://agent.huawei.com/ai/skills/ds-mr-reviewer)