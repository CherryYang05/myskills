#!/usr/bin/env python3
"""
生成 skills 仓库的 README.md：安装说明、Skills 表格、更新与维护说明。

从脚本所在的 Git 工作树定位仓库根与 GitHub slug，拒绝在技能安装目录中生成。
由 pre-commit 钩子在每次提交时自动调用，也可手动运行刷新。
"""
import json
import re, subprocess
from pathlib import Path


# README 使用独立的中文概括；各 skill 的触发描述仍由 SKILL.md 维护。
README_SUMMARIES = {
    "impeccable": "Impeccable 界面设计、UX 评审、技术审计与精修技能；包含完整参考资料及固定版本引擎启动器。",
    "mermaid-diagrams": "社区 Mermaid 图表技能，指导流程图、时序图、类图、数据库关系图和 C4 架构图；保留完整参考文档。",
    "shadcn": "shadcn/ui 官方组件与项目技能，包含配置、主题、组件组合、表单和聊天界面规则；含 Codex 适配。",
    "frontend-design": "Anthropic 官方界面设计指南，指导视觉方向、字体、配色、布局、响应式设计及自我评审。",
    "web-design-guidelines": "Vercel 官方 UI 审查技能，检查可访问性、交互、表单、性能等 Web 界面规范。",
    "humanizer": "识别并改写夸张措辞、空泛表达、重复句式和多余套话，在保留原意、事实与作者风格的基础上减少 AI 写作痕迹，让文字自然、清晰。",
    "skill-creator": "创建、改进和评测 Agent Skills，优化技能的执行效果与触发准确性。",
}

# README 与 GitHub 上游检查共用此配置；版本只表示已同步基线。
EXTERNAL_SOURCES = json.loads(
    (Path(__file__).resolve().parents[1] / "upstreams.json").read_text(encoding="utf-8")
)


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
    rows = ["| Skill | 来源 | 同步版本 | 简介 |", "|-------|------|----------|------|"]
    for n in skill_dirs(root):
        desc = README_SUMMARIES.get(n)
        if desc is None:
            desc = read_desc(root / n / "SKILL.md")
        source_info = EXTERNAL_SOURCES.get(n)
        source = f"[外部参考]({source_info['url']})" if source_info else "自研"
        version = f"`{source_info['version']}`" if source_info else "—"
        rows.append(f"| [{n}](./{n}) | {source} | {version} | {desc} |")
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

GitHub marketplace 清单位于 [`.agents/plugins/marketplace.json`](./.agents/plugins/marketplace.json)，提供各技能的独立条目。工作区管理员可通过 **Admin → Plugins → Add → Import marketplace** 导入本仓库，并跟随 `master` 分支接收每日同步。个人空间手动上传的技能不会因此自动更新；完整的安装、迁移边界及维护步骤见 [marketplace 使用说明](./docs/marketplace.md)。

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

- 本 README 由 `skill-sync/scripts/gen_readme.py` 整体生成。修改安装说明请编辑脚本模板；技能简介优先使用脚本中的中文概括，其余取自各 `SKILL.md`；外部参考 Skill 的上游 GitHub 地址和当前同步版本维护在 `skill-sync/upstreams.json` 中（脚本导出 `EXTERNAL_SOURCES` 供兼容使用），未登记项默认标记为“自研”。有正式版本号时记录版本号；没有版本号时记录已同步的上游 commit 短 SHA。同步版本仅表示本仓库已同步的状态，并不保证它仍是上游最新版本。
- 在源码仓库中运行 `python3 skill-sync/scripts/gen_readme.py` 可手动刷新 README；启用上述 pre-commit 钩子后，每次提交会自动刷新。
- 新增、删除技能或修改技能名称后，运行 `python3 skill-sync/scripts/gen_marketplace.py` 重新生成 marketplace 清单（需要 PyYAML）；CI 使用 `--check` 检查清单是否完整且与源码一致。
- 每周五北京时间 20:30（UTC 12:30），GitHub Actions 检查 `skill-sync/upstreams.json` 登记的全部外部 Skill，自研 Skill 不参与同步。发现变化后生成实际更新候选，通过精确提交 CI 和范围校验后自动合并，同时更新本 README 的来源和同步版本、Marketplace 清单及根目录[同步与修正报告](./UPSTREAM_SYNC_REPORT.md)。报告包含全部外部 Skill 的检查结果、更新前后版本、上游提交和文件变化；逐项明细保留在 `docs/upstream-reports/`。手动运行及失败处理见 [上游同步](./docs/upstream-sync.md)。
- 两段同步链路为：外部上游 → 本 GitHub 仓库 → ChatGPT 工作区 Marketplace。通过 Admin → Plugins → Marketplaces 导入本仓库并跟踪 `master` 后，工作区 Marketplace 默认每日检查更新，也可手动 Sync now。无需让 GPT 定时任务重复检查或修改原始上游；GitHub Actions 的失败由工作流日志和仓库 issue 报告。此说明不代表目标工作区的实际同步开关已经核验。
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
