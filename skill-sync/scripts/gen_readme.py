#!/usr/bin/env python3
"""
生成 skills 仓库的 README.md：安装提示词 / Skills 表格 / 注意事项 三段。

无需任何配置，在仓库内任意目录运行即可（自动定位仓库根与 GitHub slug）。
由 pre-commit 钩子在每次提交时自动调用，也可手动运行刷新。
"""
import re, subprocess
from pathlib import Path


def repo_root():
    r = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    if r.returncode == 0 and r.stdout.strip():
        return Path(r.stdout.strip())
    return Path(__file__).resolve().parents[2]


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
    if len(first) > 60:
        cut = first[:60]
        m2 = re.search(r"^(.*[\s，,、；;])\S+$", cut)
        if m2 and len(m2.group(1).strip()) >= 20:
            cut = m2.group(1)
        first = cut.rstrip("，,、；; ") + "…"
    return first


def skill_dirs(root):
    return sorted(d.name for d in root.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())


def build_table(root):
    rows = ["| Skill | Description |", "|-------|-------------|"]
    for n in skill_dirs(root):
        rows.append(f"| [{n}](./{n}) | {read_desc(root / n / 'SKILL.md')} |")
    return "\n".join(rows)


def render(root, slug):
    name = slug.split("/")[-1]
    table = build_table(root)
    return f"""# {name}

> 个人 Agent Skills 仓库，多机同步。`~/.claude/skills` 本身是本仓库的 git 工作树；Claude Code 与 OpenCode 都直接读取该目录，一份源两个工具共用。

## 一、安装（交给 Agent）

把下面整段发给你的 Agent，它会自动完成安装：

```text
请帮我安装 skills 仓库 {slug}（它会成为我本机 ~/.claude/skills 的 git 工作树）：
1. 若 ~/.claude/skills 已存在且非空：进入该目录依次执行
   git init && git remote add origin https://github.com/{slug}.git
   && git fetch origin && git reset --hard origin/master
   && git branch --set-upstream-to=origin/master master
   若不存在：直接 git clone https://github.com/{slug}.git ~/.claude/skills
2. 启用 README 自动生成钩子：git -C ~/.claude/skills config core.hooksPath skill-sync/hooks
3. 运行 git -C ~/.claude/skills status 验证
（OpenCode 用户无需额外配置：OpenCode 会自动识别 ~/.claude/skills）
```

## 二、已收录的 Skills

{table}

## 三、注意事项

- **同步即原生 git**：改完某 skill 后 `git add <skill> && git commit -m "…" && git push`；拉取用 `git pull`（覆盖本地前先 `git fetch && git diff HEAD origin/master` 确认）。
- 本 README 的表格由 `skill-sync/scripts/gen_readme.py` 自动生成（pre-commit 钩子每次提交时刷新），**请勿手改表格**。
- 切勿把 token、密钥等敏感信息提交进任何 skill；本仓库公开可见。
- 完整同步命令与 Agent 行为约定见 [skill-sync](./skill-sync) 的 SKILL.md。
"""


def main():
    root = repo_root()
    slug = repo_slug(root)
    (root / "README.md").write_text(render(root, slug), encoding="utf-8")
    print(f"[gen_readme] 已更新 {root / 'README.md'}（{len(skill_dirs(root))} 个 skill）")


if __name__ == "__main__":
    main()
