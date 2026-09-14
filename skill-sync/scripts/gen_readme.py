#!/usr/bin/env python3
"""
生成 skills 仓库的 README.md：安装说明、Skills 表格、更新与维护说明。

从脚本所在的 Git 工作树定位仓库根与 GitHub slug，拒绝在技能安装目录中生成。
由 pre-commit 钩子在每次提交时自动调用，也可手动运行刷新。
"""
import re, subprocess
from pathlib import Path


# README 使用独立的中文概括；各 skill 的触发描述仍由 SKILL.md 维护。
README_SUMMARIES = {
    "humanizer": "识别并改写夸张措辞、空泛表达、重复句式和多余套话，在保留原意、事实与作者风格的基础上减少 AI 写作痕迹，让文字自然、清晰。",
    "skill-creator": "创建、改进和评测 Agent Skills，优化技能的执行效果与触发准确性。",
}


def repo_root():
    root = Path(__file__).resolve().parents[2]
    r = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True)
    if r.returncode != 0 or Path(r.stdout.strip()).resolve() != root:
        raise SystemExit("[gen_readme] 请在已克隆的源码仓库中运行 skill-sync/scripts/gen_readme.py。")
    return root


def repo_slug(root):
    r = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"],
                       capture_output=True, text=True)
    m = re.search(r"github\.com[:/]([^/]+/[^/]+?)(?:\.git)?$", r.stdout.strip())
    return m.group(1) if m else "<owner>/<repo>"


def read_desc(skill_md):
    try:
        text = Path(skill_md).read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r"^---\s*$(.*?)^---\s*$", text, re.S | re.M)
    fm = m.group(1) if m else text
    dm = re.search(r"^description:\s*(.*)$", fm, re.M)
    if not dm:
        return ""

    raw = dm.group(1).strip()
    if raw in {"|", ">", "|-", ">-", "|+", ">+"}:
        block = []
        for line in fm[dm.end():].splitlines():
            if not line.strip():
                if block:
                    break
                continue
            if not line[0].isspace():
                break
            block.append(line.strip())
        desc = " ".join(block)
    else:
        desc = raw.strip("\"'")

    first = re.split(r"[。！？]|——|\.\s|;\s", desc)[0].strip().rstrip("，,、；; ")
    return first


def skill_dirs(root):
    return sorted(d.name for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def build_table(root):
    rows = ["| Skill | 简介 |", "|-------|------|"]
    for n in skill_dirs(root):
        desc = README_SUMMARIES.get(n)
        if desc is None:
            desc = read_desc(root / n / "SKILL.md")
        rows.append(f"| [{n}](./{n}) | {desc} |")
    return "\n".join(rows)


def render(root, slug):
    name = slug.split("/")[-1]
    table = build_table(root)
    return f"""# {name}

> 个人 Agent Skills 仓库，通过 [skills CLI](https://github.com/vercel-labs/skills) 安装和更新，可按需选择技能及 Claude Code、OpenCode 等 Agent。

## 一、安装

准备好 Node.js、npm 和 Git，在终端运行：

```bash
npx skills add {slug} --global
```

按提示选择要安装的 skill 和使用的 Agent。`--global` 表示用户级安装，可跨项目使用；去掉该参数则安装到当前项目。

常用安装方式：

```bash
# 查看仓库中可安装的 skills
npx skills add {slug} --list

# 只安装 MR 代码检视 skill
npx skills add {slug} --skill ds-mr-reviewer --global

# 只安装 humanizer
npx skills add {slug} --skill humanizer --global

# 为 Claude Code 和 OpenCode 安装仓库中的全部 skills
npx skills add {slug} --skill '*' --agent claude-code opencode --global
```

`--skill` 使用各 `SKILL.md` 的 `name` 字段，可能与文件夹名称不同；请以 `--list` 显示的名称为准。安装位置由 CLI 根据所选 Agent 和安装范围管理，完成后会显示实际路径。

## 二、已收录的 Skills

{table}

## 三、更新与管理

```bash
# 查看已安装的全局 skills
npx skills list --global

# 更新已安装的 humanizer
npx skills update humanizer --global

# 更新 CLI 管理的全部全局 skills（包含其他仓库的 skills）
npx skills update --global
```

更新当前项目的 skills 时，进入项目目录并使用 `npx skills update --project`。若在安装目录中改过 skill，更新前先保存这些改动；需要长期维护的修改应提交到源码仓库。

## 四、维护仓库

需要新增或修改 skill 时，在独立的 Git 工作树中维护源码，例如：

```bash
git clone https://github.com/{slug}.git ~/code/{name}
cd ~/code/{name}
git config core.hooksPath skill-sync/hooks
```

已有源码工作树可以继续使用。源码通过 `git add`、`git commit`、`git push` 推送，拉取远端修改使用 `git pull`；提交后再用 `npx skills update` 更新本机已安装的技能。

- 本 README 由 `skill-sync/scripts/gen_readme.py` 整体生成。修改安装说明请编辑脚本模板；技能简介优先使用脚本中的中文概括，其余取自各 `SKILL.md`。
- 在源码仓库中运行 `python3 skill-sync/scripts/gen_readme.py` 可手动刷新 README；启用上述 pre-commit 钩子后，每次提交会自动刷新。
- 切勿把 token、密钥等敏感信息提交进任何 skill；本仓库公开可见。
- 完整安装、同步命令与 Agent 行为约定见 [skill-sync](./skill-sync) 的 SKILL.md。
"""


def main():
    root = repo_root()
    slug = repo_slug(root)
    (root / "README.md").write_text(render(root, slug), encoding="utf-8")
    print(f"[gen_readme] 已更新 {root / 'README.md'}（{len(skill_dirs(root))} 个 skill）")


if __name__ == "__main__":
    main()
