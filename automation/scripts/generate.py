#!/usr/bin/env python3
"""Render README and OpenAI Marketplace from the same validated Skill inventory."""
import argparse
import json
import re

from sync import ROOT, CONFIG
from verify import inventory

MARKETPLACE = ".agents/plugins/marketplace.json"
README = "README.md"


def source_link(source):
    url = f"https://github.com/{source['repo']}"
    path = source["path"]
    if path:
        url += f"/tree/{source['ref']}/{path}"
    return url


def render(root=ROOT):
    packages = inventory(root)
    config = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    catalog = {"name": "cherry-myskills", "interface": {"displayName": "Cherry Skills"}, "plugins": []}
    rows = ["| Skill | 类型 | 来源 / 当前版本 | 说明 |", "|---|---|---|---|"]
    for group, directory, fields in packages:
        name = fields["name"]
        path = f"./skills/{group}/{directory}"
        catalog["plugins"].append({
            "name": name,
            "source": {"source": "local", "path": path},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        })
        raw = re.sub(r"\s+", " ", fields["description"]).strip()
        desc = raw.split(". ")[0].split("。")[0][:160].replace("|", r"\|").replace("`", "'")
        label = f"[{name}]({path})"
        if group == "external":
            info = config[directory]
            origin = f"[{info['repo']}]({source_link(info)}) · `{info['sha'][:12]}`"
            category = "外部同步"
        else:
            origin = "自研"
            category = "自研"
        rows.append(f"| {label} | {category} | {origin} | {desc} |")
    readme = """# myskills

个人 Agent Skills 仓库。将第三方 Skill 的上游更新和自己的 Skill 统一管理，提供 GitHub Marketplace 清单供支持该功能的客户端和 ChatGPT 工作区使用。

## 安装

使用 [Skills CLI](https://github.com/vercel-labs/skills) 按需安装：

```bash
npx skills add CherryYang05/myskills --list
npx skills add CherryYang05/myskills --global
npx skills add CherryYang05/myskills --skill humanizer --global
```

技能位于 `skills/external/` 和 `skills/personal/`，保持每个技能内的相对目录与脚本。两个分类均可被 Skills CLI 发现。

## Skill 清单

""" + "\n".join(rows) + """

## 两阶段同步

1. **外部上游 → 本仓库**：每周五北京时间 20:30，Sync Skill Upstreams 从 `automation/upstreams.json` 读取全部外部 Skill 来源，按上游 Git 提交获取完整技能目录；生成候选 PR。只有通过精确提交的 Validate Skills 校验后才自动合并，更新 README、Marketplace 清单及根目录 `UPSTREAM_SYNC_REPORT.md`。自研 Skill 不在自动覆盖范围内。
2. **本仓库 → ChatGPT**：`.agents/plugins/marketplace.json` 由 Skill 目录自动生成。支持 GitHub Marketplace 导入的 ChatGPT 工作区管理员可导入仓库并跟踪 `master`，平台通常每日同步，也可手动 Sync now。仓库更新不代表个人 ChatGPT Plus 空间中手动上传的插件已更新。

工作区导入：**Admin → Plugins → Add → Import marketplace**；Source 为 `https://github.com/CherryYang05/myskills`，Path 留空，Branch 填 `master`。已有手动上传插件的身份迁移需要单独处理。详见 [OpenAI 官方导入文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

## 维护原则

- `automation/upstreams.json` 是外部 Skill 的唯一来源注册表。外部目录和注册表必须一一对应；新增第三方 Skill 必须同时登记。
- `automation/scripts/` 管理上游检查、来源安全、版本报告、校验及自动合并；`automation/tests/` 是回归测试。
- `README.md` 和 `.agents/plugins/marketplace.json` 都是生成文件。修改 Skill 或配置后执行 `python3 automation/scripts/generate.py`。
- `UPSTREAM_SYNC_REPORT.md` 是 GitHub 上游检查生成的根目录报告。成功合并才代表相应 Skill 已实际同步。
- 自动流程只读取和复制上游文件，绝不执行上游脚本。外部 Skill 的自动替换可能删除旧的本地定制，历史可由 Git 恢复。
- GitHub Actions 故障会保留候选 PR 并创建故障 Issue，不绕过校验。

仓库的 Agent 维护约定见 [AGENTS.md](./AGENTS.md)，架构与分发细节见 [docs/architecture.md](./docs/architecture.md)。
"""
    return {README: readme,
            MARKETPLACE: json.dumps(catalog, ensure_ascii=False, indent=2) + "\n"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render()
    for name, content in generated.items():
        target = ROOT / name
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Generated file is stale: {name}. Run python3 automation/scripts/generate.py")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    print(f"Generated artifacts {'verified' if args.check else 'updated'} ({len(generated)} files).")


if __name__ == "__main__":
    main()
