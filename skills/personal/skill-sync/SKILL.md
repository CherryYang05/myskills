---
name: skill-sync
description: 维护个人 GitHub Agent Skills 仓库，安装、更新、检查 Skills 来源和同步状态。支持通过 npx skills 安装，以及在已验证的 Git 源码工作树中提交和拉取；同步外部上游时遵守仓库中的自动校验与限域合并策略。
---

# Skill 同步与仓库维护

源码仓库：`CherryYang05/myskills`。已安装 Skill 的目录不能直接当作源码仓库操作；先用 `git rev-parse --show-toplevel` 和 `git remote -v` 验证远端、当前分支及未提交变更。外部 Skill 位于 `skills/external/`，自研 Skill 位于 `skills/personal/`。

## 安装及更新

```bash
npx skills add CherryYang05/myskills --list
npx skills add CherryYang05/myskills --global
npx skills add CherryYang05/myskills --skill humanizer --global
npx skills list --global
npx skills update humanizer --global
```

用户授权修改仓库源码前，先查看 `git status` 与 diff，并检查敏感信息和文件范围。人工提交或删除前对用户概述真正的内容差异；未经明确授权不要执行推送或覆盖本地改动。

## 两阶段同步

上游维护从 `automation/upstreams.json` 读取所有外部来源。每周五 `.github/workflows/sync-upstream.yml` 先检查再通过独立 CI 验证候选并自动合并。这项固定范围的自动上游替换已获得授权，但不可写入自研 Skill 或篡改同步控制代码。新增第三方 Skill 必须登记真实来源；上游来源的完整 `sha` 代表已落地版本。报告位于根目录 `UPSTREAM_SYNC_REPORT.md`。

工作区 ChatGPT Marketplace 从 GitHub `master` 更新时使用 `.agents/plugins/marketplace.json`。它是第二阶段，由支持该功能且已导入本仓库的工作区平台负责，不要宣称个人 ChatGPT 空间上传的插件也会自动更新。

## 本地维护

```bash
python3 -m pip install pyyaml
python3 -m unittest discover -s automation/tests -v
python3 automation/scripts/verify.py
python3 automation/scripts/generate.py
python3 automation/scripts/generate.py --check
python3 automation/scripts/sync.py --check-config
```

README 和 Marketplace 是生成物；不要直接编辑并强制绕过生成校验。自动合并必须通过候选准确 SHA 的 CI，且不能修改自研 Skill、同步脚本、Action 工作流、上游仓库配置或保留的许可文件。失败时阅读 Actions 和对应 Issue，修复后重试，绝不伪称已经完成同步。

更多细节见仓库 `docs/architecture.md`。
