#!/usr/bin/env python3
"""Render README and OpenAI Marketplace from the same validated Skill inventory."""
import argparse
import json
import re
import shutil
from pathlib import Path

from sync import ROOT, CONFIG, local_snapshot
from verify import inventory

MARKETPLACE = ".agents/plugins/marketplace.json"
CLAUDE_MARKETPLACE = ".claude-plugin/marketplace.json"
CURSOR_MARKETPLACE = ".cursor-plugin/marketplace.json"
SKILLS_CLI_CONFIG = "skills.sh.json"
README = "README.md"

# Source Skills remain unchanged; these folders only install the source on
# other platforms and do not belong in a ChatGPT plugin package.
OTHER_PLATFORM_INSTALL_DIRS = frozenset({".claude-plugin", ".cursor-plugin"})


def source_link(source):
    url = f"https://github.com/{source['repo']}"
    path = source["path"]
    if path:
        url += f"/tree/{source['ref']}/{path}"
    return url


def short_description(description, limit=88):
    """Compact README summaries and avoid breaking English words."""
    text = re.sub(r"\s+", " ", description).strip()
    text = re.split(r"\. |。", text, maxsplit=1)[0].strip()
    if len(text) > limit:
        shortened = text[:limit]
        if (shortened[-1].isascii() and shortened[-1].isalnum()
                and text[limit].isascii() and text[limit].isalnum()):
            last_space = shortened.rfind(" ")
            if last_space > limit // 2:
                shortened = shortened[:last_space]
        text = shortened.rstrip(" ,.;:，。；：、") + "…"
    return text.replace("|", r"\|").replace("`", "'")


def render(root=ROOT):
    packages = inventory(root)
    config = json.loads((root / CONFIG).read_text(encoding="utf-8"))
    catalog = {"name": "cherry-myskills", "interface": {"displayName": "Cherry Skills"}, "plugins": []}
    claude_catalog = {
        "name": "cherry-skills",
        "description": "Curated external and personal Agent Skills",
        "owner": {"name": "CherryYang05", "url": "https://github.com/CherryYang05"},
        "plugins": [],
    }
    cursor_catalog = {
        "name": "cherry-skills",
        "owner": {"name": "CherryYang05"},
        "metadata": {"description": "Curated portable Agent Skills"},
        "plugins": [],
    }
    cli_paths = ["./skills/external", "./skills/personal"]
    rows = ["| Skill | 类型 | 来源 / 当前版本 | 说明 |", "|---|---|---|---|"]
    for group, directory, fields in packages:
        name = fields["name"]
        path = f"./skills/{group}/{directory}"
        plugin_path = f"./plugins/{name}"
        catalog["plugins"].append({
            "name": name,
            "source": {"source": "local", "path": plugin_path},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": "Productivity",
        })
        # Claude Code takes plugin names from marketplace entries when there is
        # no .claude-plugin/plugin.json; Cursor accepts root Agent Plugins.
        # Both platforms use the same generated self-contained plugin package.
        marketplace_desc = re.sub(r"\s+", " ", fields["description"]).strip()
        claude_catalog["plugins"].append({
            "name": name, "source": plugin_path, "description": marketplace_desc
        })
        cursor_catalog["plugins"].append({
            "name": name, "source": plugin_path, "description": marketplace_desc
        })
        desc = short_description(fields["description"])
        label = f"[{name}]({path})"
        if group == "external":
            info = config[directory]
            origin = f"[{info['repo']}]({source_link(info)}) · `{info['sha'][:12]}`"
            # GitHub Markdown tables may break Chinese at every character;
            # word-joiner entities keep the type label on one line without custom CSS.
            category = "外&#8288;部&#8288;同&#8288;步"
        else:
            origin = "自研"
            category = "自研"
        rows.append(f"| {label} | {category} | {origin} | {desc} |")
    readme = """# myskills

个人 Agent Skills 仓库。将第三方 Skill 的上游更新和自己的 Skill 统一管理，提供 GitHub Marketplace 清单供支持该功能的客户端和 ChatGPT 工作区使用。

## 安装与更新

本仓库有两种安装途径：

- **Skills CLI**：将原始 `SKILL.md` 和配套文件安装到本地代码 Agent（Codex、Claude Code、Cursor 等），支持选择 Skill、目标 Agent 和安装作用域。
- **Plugin Marketplace**：通过客户端自己的插件目录安装 `plugins/<name>/` 打包产物。导入 Marketplace 只注册可选来源，**还需要安装具体插件**。

### 方法一：npx skills（跨平台推荐）

需要 Node.js **22.20 或更高版本**。在目标项目目录执行表示项目级安装；加 `-g` 则表示当前用户全局安装。

```bash
# 列出仓库中所有 16 个 Skill（只查询，不安装）
npx skills add CherryYang05/myskills --list

# 交互式选择 Skill 和客户端（当前项目）
npx skills add CherryYang05/myskills

# 推荐：通过 -s 指定 Skill；无需填写很长的 GitHub 子目录 URL
npx skills add CherryYang05/myskills -s humanizer

# 给 Codex 全局安装指定 Skill
npx skills add CherryYang05/myskills -s humanizer -a codex -g -y

# 给 Claude Code 全局安装指定 Skill
npx skills add CherryYang05/myskills -s blog-writer -a claude-code -g -y

# 给 Cursor 当前项目安装指定 Skill
npx skills add CherryYang05/myskills -s impeccable -a cursor -y

# 同时将两个指定 Skill 安装到 Codex 和 Claude Code（当前项目）
npx skills add CherryYang05/myskills -s humanizer -s blog-writer -a codex -a claude-code -y

# 将本仓库全部 16 个 Skill 安装给三个指定客户端（全局）
npx skills add CherryYang05/myskills -s '*' -a codex -a claude-code -a cursor -g -y

# 在所有受支持的客户端安装全部 Skill（范围较大，谨慎使用）
npx skills add CherryYang05/myskills --all
```

**记忆方式：** `npx skills add CherryYang05/myskills -s <skill-name>`。例如只安装 Humanizer，直接用 `-s humanizer`；不需要记住 `skills/external/` 或 `skills/personal/` 的目录位置。

如果只是临时使用而不安装，Skills CLI 另有 `use` 命令（`@` 后面是 Skill 名称）：

```bash
npx skills use CherryYang05/myskills@humanizer -a codex
```

注意 `npx skills add humanizer@CherryYang05/myskills` 并非 CLI 支持的指定 Skill 语法；`add` 使用 `-s`，而 `use` 才使用 `owner/repo@skill`。

查看、更新和卸载通过 Skills CLI 安装的 Skill：

```bash
npx skills list                 # 当前项目已安装的 Skill
npx skills ls -g                # 全局已安装的 Skill
npx skills ls -a codex          # 只查看 Codex 的项目级 Skill
npx skills check                # 检查是否存在更新
npx skills update humanizer -g  # 更新全局安装的 humanizer
npx skills update -g            # 更新所有全局 Skill
npx skills remove humanizer -g  # 卸载全局安装的 humanizer
```

`-s`（或 `--skill`）选择名称，`-a` 选择目标客户端，`-g` 代表用户级安装，`-y` 跳过确认；`--all` 同时涵盖所有技能和所有受支持的客户端。可用 `--copy` 改用复制而非符号链接。更多参数见 [Skills CLI 官方命令文档](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)。

### 方法二：各客户端的 Plugin Marketplace

这条途径分发自动生成的 `plugins/<name>/`。**同一个 Skill 选用一种安装途径通常就够了**，以免出现本地和插件版重复加载或版本不一致。

**Codex CLI / ChatGPT 桌面版的 Codex 模式**

```bash
# 注册 GitHub 插件市场（仓库入口是 .agents/plugins/marketplace.json）
codex plugin marketplace add CherryYang05/myskills

# 查看已注册的市场
codex plugin marketplace list

# 刷新该市场的仓库快照
codex plugin marketplace upgrade cherry-myskills

# 启动 Codex
codex
```

然后在 Codex 交互界面输入 `/plugins`，切换到 **Cherry Skills**，选择 `humanizer`（或其他插件）并点击安装。官方文档提供了市场注册 CLI 和交互式插件安装入口；这里不使用未经核实的 `codex plugin install ...` 命令。ChatGPT 桌面版也可从「插件」目录选择 Cherry Skills 安装。详见 [OpenAI 插件打包与 Marketplace 文档](https://developers.openai.com/plugins/build/plugins)。

**Claude Code**

```bash
# 注册仓库中的 .claude-plugin/marketplace.json
claude plugin marketplace add CherryYang05/myskills

# 安装指定插件：名称@市场名称
claude plugin install humanizer@cherry-skills
claude plugin install blog-writer@cherry-skills
```

也可以在 Claude Code 交互界面使用 `/plugin marketplace add CherryYang05/myskills` 和 `/plugin install humanizer@cherry-skills`。这里的 `cherry-skills` 是 Claude Marketplace 的标识，和 Codex 使用的 `cherry-myskills` 不同。

**Cursor**

在 Cursor 的 **Customize → Plugins**（或团队的 **Dashboard → Plugins & MCPs**）中，从 GitHub 仓库导入 `https://github.com/CherryYang05/myskills`，然后选择需要的插件安装。入口为 `.cursor-plugin/marketplace.json`；团队 Marketplace 依赖 Teams / Enterprise 对应功能。当前不提供未经核实的 Cursor 命令行插件安装命令。个人用户可直接使用上面的 `npx skills add ... -a cursor`。参考 [Cursor 插件文档](https://cursor.com/docs/plugins)。

**ChatGPT 网页版 / Work**

在支持导入 GitHub Marketplace 的工作区中，进入 **Admin → Plugins → Add → Import marketplace**，输入仓库 `https://github.com/CherryYang05/myskills`，跟踪 `master`，随后从 **Cherry Skills** 安装所需插件。导入和 GitHub 更新并不会自动替换网页版此前手动上传的同名插件。

## Skill 清单

""" + "\n".join(rows) + """

## 两阶段同步

1. **外部上游 → 本仓库**：每周五北京时间 20:30，Sync Skill Upstreams 从 `automation/upstreams.json` 读取全部外部 Skill 来源，按上游 Git 提交获取完整技能目录；生成候选 PR。只有通过精确提交的 Validate Skills 校验后才自动合并，更新 README、Marketplace 清单及根目录 `UPSTREAM_SYNC_REPORT.md`。自研 Skill 不在自动覆盖范围内。
2. **本仓库 → ChatGPT**：`.agents/plugins/marketplace.json` 指向生成的 `plugins/<name>/` 安装包；每个包包含 `plugin.json`、`skills/<name>/SKILL.md` 和运行相关文件，自动排除 Claude/Cursor 专用的安装元数据（源 Skill 完整保留）。支持 GitHub Marketplace 导入的 ChatGPT 工作区管理员可导入仓库并跟踪 `master`，平台通常每日同步，也可手动 Sync now。仓库更新不代表个人 ChatGPT Plus 空间中手动上传的插件已更新。

工作区导入：**Admin → Plugins → Add → Import marketplace**；Source 为 `https://github.com/CherryYang05/myskills`，Path 留空，Branch 填 `master`。已有手动上传插件的身份迁移需要单独处理。详见 [OpenAI 官方导入文档](https://learn.chatgpt.com/docs/enterprise/plugin-management)。

## 维护原则

- `automation/upstreams.json` 是外部 Skill 的唯一来源注册表。外部目录和注册表必须一一对应；新增第三方 Skill 必须同时登记。
- `automation/scripts/` 管理上游检查、来源安全、版本报告、校验及自动合并；`automation/tests/` 是回归测试。
- `README.md`、`skills.sh.json`、三个平台的 Marketplace 清单和 `plugins/` 都是生成产物。修改 Skill 或配置后执行 `python3 automation/scripts/generate.py`，再运行 `python3 automation/scripts/generate.py --check` 验证。
- `UPSTREAM_SYNC_REPORT.md` 是 GitHub 上游检查生成的根目录报告。成功合并才代表相应 Skill 已实际同步。
- 自动流程只读取和复制上游文件，绝不执行上游脚本。外部 Skill 的自动替换可能删除旧的本地定制，历史可由 Git 恢复。
- GitHub Actions 故障会保留候选 PR 并创建故障 Issue，不绕过校验。

仓库的 Agent 维护约定见 [AGENTS.md](./AGENTS.md)，生成器、Actions 触发条件和验证步骤见 [docs/architecture.md](./docs/architecture.md)。
"""
    return {
        README: readme,
        MARKETPLACE: json.dumps(catalog, ensure_ascii=False, indent=2) + "\n",
        CLAUDE_MARKETPLACE: json.dumps(claude_catalog, ensure_ascii=False, indent=2) + "\n",
        CURSOR_MARKETPLACE: json.dumps(cursor_catalog, ensure_ascii=False, indent=2) + "\n",
        SKILLS_CLI_CONFIG: json.dumps({
            "$schema": "https://skills.sh/schemas/skills.sh.schema.json",
            "paths": cli_paths,
        }, ensure_ascii=False, indent=2) + "\n",
    }



def omit_from_chatgpt_plugin(relative):
    """Exclude only root-level, platform-specific installer metadata."""
    return relative.split("/", 1)[0] in OTHER_PLATFORM_INSTALL_DIRS


def render_plugin_files(root=ROOT):
    """Produce portable installable plugin packages from canonical Skill sources.

    The generated plugins/ tree contains ordinary files so a downloaded plugin
    remains self-contained; source Skill packages are never rewritten.
    Other platforms\u0027 installer metadata is omitted from the generated packages.
    """
    generated = {}
    for group, directory, fields in inventory(root):
        name = fields["name"]
        source = root / "skills" / group / directory
        plugin_root = f"plugins/{name}"
        homepage = f"https://github.com/CherryYang05/myskills/tree/master/skills/{group}/{directory}"
        description = re.sub(r"\s+", " ", fields["description"]).strip()
        subtitle = description[:117].rstrip() + ("…" if len(description) > 117 else "")
        manifest = {
            "$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
            "name": name,
            "version": "1.0.0",
            "description": description,
            "author": {
                "name": "CherryYang05",
                "url": "https://github.com/CherryYang05"
            },
            "homepage": homepage,
            "repository": "https://github.com/CherryYang05/myskills",
            "extensions": {
                "com.openai": {
                    "interface": {
                        "displayName": name,
                        "shortDescription": subtitle,
                        "longDescription": description,
                        "developerName": "CherryYang05",
                        "category": "Productivity",
                        "websiteURL": homepage
                    }
                }
            }
        }
        generated[f"{plugin_root}/plugin.json"] = (
            "100644", (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )
        for relative, (mode, content) in sorted(local_snapshot(source).items()):
            if omit_from_chatgpt_plugin(relative):
                continue
            generated[f"{plugin_root}/skills/{name}/{relative}"] = (mode, content)
    return generated


def check_or_write_plugin_files(root, generated, check):
    """Detect stale or missing plugin files and preserve executable bits."""
    folder = root / "plugins"
    if folder.is_symlink():
        raise ValueError("Generated plugin directory must not be a symlink")
    if check:
        present = {}
        if folder.exists():
            for path in folder.rglob("*"):
                if path.is_symlink():
                    raise ValueError(f"Generated plugin contains symlink: {path}")
                if path.is_file():
                    if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                        continue
                    relative = path.relative_to(root).as_posix()
                    mode = "100755" if path.stat().st_mode & 0o111 else "100644"
                    present[relative] = (mode, path.read_bytes())
        if present != generated:
            missing = sorted(set(generated) - set(present))
            extra = sorted(set(present) - set(generated))
            changed = sorted(p for p in set(present) & set(generated) if present[p] != generated[p])
            raise SystemExit(
                f"Generated plugin packages are stale (missing={missing[:5]}, "
                f"extra={extra[:5]}, modified={changed[:5]}). "
                "Run python3 automation/scripts/generate.py"
            )
        return
    if folder.exists():
        shutil.rmtree(folder)
    for relative, (mode, content) in sorted(generated.items()):
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        target.chmod(0o755 if mode == "100755" else 0o644)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render()
    plugin_files = render_plugin_files()
    for name, content in generated.items():
        target = ROOT / name
        if args.check:
            if not target.is_file() or target.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Generated file is stale: {name}. Run python3 automation/scripts/generate.py")
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
    check_or_write_plugin_files(ROOT, plugin_files, args.check)
    print(f"Generated artifacts {'verified' if args.check else 'updated'} "
          f"({len(generated)} indexes, {len(plugin_files)} plugin files).")


if __name__ == "__main__":
    main()
