#!/usr/bin/env python3
"""
skill-sync -- 本地 skills 与 GitHub 仓库同步

设计要点：
  * 全程走 git（HTTPS + token），不依赖 GitHub REST API
  * 持久缓存仓库 ~/.skill-sync-cache/<repo>，仅首次 clone，之后 fetch + reset
  * push / pull 默认只预览，加 --apply 才真正写入/推送
  * README 的「已收录的 Skills」表格与「常用同步命令」段由脚本自动生成
"""
import filecmp, json, os, re, shutil, subprocess, sys
from pathlib import Path

CONFIG_FILE = Path.home() / ".skill-sync-config.json"
CACHE_ROOT = Path.home() / ".skill-sync-cache"
SKIP = {"__pycache__", ".git", "node_modules", ".DS_Store", ".pytest_cache"}
SCRIPT_REF = "python ~/.claude/skills/skill-sync/scripts/skill_sync.py"

# ----------------------------- 配置 -----------------------------
def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)

def save_config(c):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(c, f, indent=2, ensure_ascii=False)

def require_config():
    c = load_config()
    if not c.get("github_token") or not c.get("github_repo"):
        print("[ERROR] 未配置，请运行：", SCRIPT_REF, "config set")
        sys.exit(1)
    profile = c.get("active_profile", "default")
    prof = c.get("profiles", {}).get(profile, {})
    lp = prof.get("local_skills_path") or c.get("local_skills_path") or str(Path.home() / ".claude" / "skills")
    return {
        "github_token": c["github_token"],
        "github_repo": c["github_repo"],
        "local_skills_path": str(Path(lp).expanduser()),
    }

# ----------------------------- git -----------------------------
def authed_url(cfg):
    return f"https://{cfg['github_token']}@github.com/{cfg['github_repo']}.git"

def clean_url(cfg):
    return f"https://github.com/{cfg['github_repo']}.git"

def scrub(text, token):
    return (text or "").replace(token, "***")

def git(cache, *args, check=False):
    r = subprocess.run(["git", "-C", str(cache), *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.stderr.write(scrub(r.stderr.strip(), _TOKEN) + "\n")
    return r

_TOKEN = ""  # 运行期填充，供 scrub 使用

def fetch_remote(cfg, cache):
    """用带 token 的 URL 拉取最新，但 token 不写入 .git/config。"""
    return subprocess.run(
        ["git", "-C", str(cache), "fetch", "--quiet", authed_url(cfg),
         "+refs/heads/*:refs/remotes/origin/*"],
        capture_output=True, text=True)

def push_remote(cfg, cache, branch):
    return subprocess.run(
        ["git", "-C", str(cache), "push", "--quiet", authed_url(cfg), branch],
        capture_output=True, text=True)

def ensure_cache(cfg):
    """确保缓存仓库存在并同步到远程最新，返回 (cache_path, branch)。"""
    global _TOKEN
    _TOKEN = cfg["github_token"]
    CACHE_ROOT.mkdir(exist_ok=True)
    cache = CACHE_ROOT / cfg["github_repo"].split("/")[1]

    if (cache / ".git").is_dir():
        if fetch_remote(cfg, cache).returncode != 0:
            shutil.rmtree(cache, ignore_errors=True)  # 缓存损坏，重建

    if not (cache / ".git").is_dir():
        print(f"[缓存] 首次克隆 {cfg['github_repo']} → {cache}")
        r = subprocess.run(["git", "clone", "--quiet", authed_url(cfg), str(cache)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print("[ERROR] clone 失败:", scrub(r.stderr.strip(), _TOKEN))
            sys.exit(1)
        # 抹掉 origin URL 里的 token，缓存仓库的 .git/config 只留干净地址
        git(cache, "remote", "set-url", "origin", clean_url(cfg))

    branch = git(cache, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip() or "master"
    git(cache, "reset", "--hard", "--quiet", f"origin/{branch}")
    git(cache, "clean", "-fd", "--quiet")
    return cache, branch

# ----------------------------- 工具 -----------------------------
def skills_in(path):
    path = Path(path)
    if not path.exists():
        return []
    return sorted(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").is_file())

def list_files(root):
    out = {}
    for p in Path(root).rglob("*"):
        rel = p.relative_to(root)
        if any(s in rel.parts for s in SKIP):
            continue
        if p.is_file():
            out[rel.as_posix()] = p
    return out

def same_tree(a, b):
    fa, fb = list_files(a), list_files(b)
    if set(fa) != set(fb):
        return False
    return all(filecmp.cmp(fa[k], fb[k], shallow=False) for k in fa)

def copy_skill(src, dst):
    if Path(dst).exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*SKIP))

def read_desc(skill_md):
    try:
        text = Path(skill_md).read_text(encoding="utf-8")
    except Exception:
        return ""
    m = re.search(r"^---\s*$(.*?)^---\s*$", text, re.S | re.M)
    fm = m.group(1) if m else text
    dm = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not dm:
        return ""
    desc = dm.group(1).strip().strip("\"'")
    # 取第一个句子单元：中文句末标点 / 破折号 / 英文句末
    first = re.split(r"[。！？]|——|\.\s|;\s", desc)[0].strip().rstrip("，,、；; ")
    if len(first) > 60:
        cut = first[:60]
        # 回退到最后一个空格或标点，避免砍断英文单词
        m = re.search(r"^(.*[\s，,、；;])\S+$", cut)
        if m and len(m.group(1).strip()) >= 20:
            cut = m.group(1)
        first = cut.rstrip("，,、；; ") + "…"
    return first

# ----------------------------- README -----------------------------
def build_skills_table(cache):
    rows = ["| Skill | Description |", "|-------|-------------|"]
    for name in skills_in(cache):
        desc = read_desc(cache / name / "SKILL.md")
        rows.append(f"| [{name}](./{name}) | {desc} |")
    return "\n".join(rows)

def commands_block():
    return f"""~~~bash
# 查看状态：本地 vs 仓库差异（只读，不改动任何东西）
{SCRIPT_REF} status

# 推送本地 skills 到 GitHub（默认仅预览，加 --apply 才推送）
{SCRIPT_REF} push              # 同步全部本地 skill
{SCRIPT_REF} push <name> ...   # 仅同步指定 skill
{SCRIPT_REF} push --apply      # 确认后执行

# 从 GitHub 拉取到本地（默认仅预览，加 --apply 才写入）
{SCRIPT_REF} pull              # 全部
{SCRIPT_REF} pull <name> ...   # 指定
{SCRIPT_REF} pull --apply      # 确认后执行
~~~"""

def replace_section(text, title, body):
    pat = re.compile(r"(^##\s+" + re.escape(title) + r"\s*\n)(.*?)(?=^##\s|\Z)", re.S | re.M)
    repl = lambda m: m.group(1) + "\n" + body + "\n\n"
    if pat.search(text):
        return pat.sub(repl, text)
    return text.rstrip() + "\n\n## " + title + "\n\n" + body + "\n"

def update_readme(cache):
    readme = cache / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# myskills\n"
    text = replace_section(text, "已收录的 Skills", build_skills_table(cache))
    text = replace_section(text, "常用同步命令", commands_block())
    readme.write_text(text, encoding="utf-8")

# ----------------------------- 命令 -----------------------------
def cmd_config(args):
    if args and args[0] == "profile":
        return cmd_profile(args[1:])
    if args and args[0] == "set":
        return config_set()
    c = load_config()
    if not c:
        print("[WARN] 未配置"); return
    tok = c.get("github_token", "")
    print(f"github_token : {'*' * max(0, len(tok) - 4) + tok[-4:] if tok else '(未设置)'}")
    print(f"github_repo  : {c.get('github_repo', '(未设置)')}")
    print(f"active_profile: {c.get('active_profile', 'default')}")
    for n, i in c.get("profiles", {}).items():
        mark = " *" if n == c.get("active_profile") else "  "
        print(f"{mark} {n}: {i.get('local_skills_path', '')}")

def config_set():
    c = load_config()
    cur = c.get("github_token", "")
    val = input(f"GitHub Token ({'...' + cur[-4:] if len(cur) > 4 else '未设置'}): ").strip()
    if val:
        c["github_token"] = val
    val = input(f"GitHub 仓库 (user/repo) [{c.get('github_repo', '')}]: ").strip()
    if val:
        c["github_repo"] = val
    if not c.get("profiles"):
        c["profiles"] = {"default": {"local_skills_path": str(Path.home() / ".claude" / "skills"), "description": "默认"}}
        c["active_profile"] = "default"
    save_config(c)
    print("[OK] 配置已保存")

def cmd_profile(args):
    c = load_config()
    profiles = c.setdefault("profiles", {})
    if not args or args[0] == "list":
        for n, i in profiles.items():
            mark = " *" if n == c.get("active_profile") else "  "
            print(f"{mark} {n}: {i.get('local_skills_path', '')}")
    elif args[0] == "add" and len(args) >= 3:
        profiles[args[1]] = {"local_skills_path": str(Path(args[2]).expanduser()), "description": ""}
        save_config(c); print(f"[OK] 已添加 profile {args[1]}")
    elif args[0] == "set" and len(args) >= 2:
        if args[1] not in profiles:
            print(f"[ERROR] 不存在的 profile: {args[1]}"); return
        c["active_profile"] = args[1]; save_config(c); print(f"[OK] 已切换到 {args[1]}")
    else:
        print("用法: config profile [list|add <name> <path>|set <name>]")

def cmd_status(args, cfg):
    cache, branch = ensure_cache(cfg)
    local = set(skills_in(cfg["local_skills_path"]))
    remote = set(skills_in(cache))
    print(f"[状态] 本地 {len(local)} 个  仓库 {len(remote)} 个  (分支 {branch})")
    for n in sorted(local | remote):
        if n in local and n not in remote:
            tag = "NEW    仅本地，可 push"
        elif n in remote and n not in local:
            tag = "REMOTE 仅远程，可 pull"
        elif same_tree(Path(cfg["local_skills_path"]) / n, cache / n):
            tag = "SAME   一致"
        else:
            tag = "MOD    内容不同"
        print(f"  {tag:<22} {n}")

def cmd_push(args, cfg):
    apply = "--apply" in args
    names = [a for a in args if not a.startswith("--")]
    cache, branch = ensure_cache(cfg)
    local = skills_in(cfg["local_skills_path"])
    targets = names or local
    bad = [n for n in targets if n not in local]
    for n in bad:
        print(f"[WARN] 本地不存在，跳过: {n}")
    targets = [n for n in targets if n in local]
    if not targets:
        print("[OK] 没有可推送的 skill"); return

    base = Path(cfg["local_skills_path"])
    for n in targets:
        dst = cache / n
        if dst.exists() and same_tree(base / n, dst):
            continue  # 内容已一致，跳过复制
        copy_skill(base / n, dst)
    update_readme(cache)
    git(cache, "add", "-A")
    stat = git(cache, "diff", "--cached", "--stat").stdout.strip()
    if not stat:
        print("[OK] 仓库已是最新，无变更"); git(cache, "reset", "--hard", "--quiet", f"origin/{branch}"); return

    if not apply:
        print(f"[预览] 将提交以下变更到 {cfg['github_repo']} ({branch})：")
        print(stat)
        print(f"\n确认无误后执行：{SCRIPT_REF} push {' '.join(names)} --apply".rstrip())
        git(cache, "reset", "--hard", "--quiet", f"origin/{branch}")
        git(cache, "clean", "-fd", "--quiet")
        return

    msg = f"sync: 更新 {', '.join(targets)}"
    git(cache, "commit", "--quiet", "-m", msg)
    r = push_remote(cfg, cache, branch)
    if r.returncode != 0:
        # 可能远程已被更新（非快进），同步后将本地提交 rebase 到最新再重试一次
        fetch_remote(cfg, cache)
        rb = git(cache, "rebase", f"origin/{branch}")
        if rb.returncode != 0:
            git(cache, "rebase", "--abort")
            print(f"[ERROR] 远程有新提交且无法自动合并，请手动处理缓存仓库：{cache}")
            return
        r = push_remote(cfg, cache, branch)
    if r.returncode == 0:
        print(f"[OK] 已推送 {len(targets)} 个 skill + README 到 {cfg['github_repo']}")
    else:
        print("[ERROR] 推送失败:", scrub(r.stderr.strip(), _TOKEN))

def cmd_pull(args, cfg):
    apply = "--apply" in args
    names = [a for a in args if not a.startswith("--")]
    cache, branch = ensure_cache(cfg)
    remote = skills_in(cache)
    base = Path(cfg["local_skills_path"])
    targets = names or remote
    plan = []
    for n in targets:
        if n not in remote:
            print(f"[WARN] 仓库不存在，跳过: {n}"); continue
        plan.append((n, "覆盖" if (base / n).exists() else "新增"))
    if not plan:
        print("[OK] 没有可拉取的 skill"); return
    if not apply:
        print(f"[预览] 将从 {cfg['github_repo']} 拉取到 {base}：")
        for n, act in plan:
            print(f"  {act}  {n}")
        print(f"\n确认无误后执行：{SCRIPT_REF} pull {' '.join(names)} --apply".rstrip())
        return
    for n, _ in plan:
        copy_skill(cache / n, base / n)
    print(f"[OK] 已拉取 {len(plan)} 个 skill 到 {base}")

# ----------------------------- 入口 -----------------------------
# 旧命令别名 → 新命令（向后兼容）
ALIASES = {
    "list-local": ("status", []), "list-remote": ("status", []), "diff": ("status", []),
    "upload": ("push", []), "update": ("push", []),
    "do-upload": ("push", ["--apply"]), "do-update": ("push", ["--apply"]),
    "install": ("pull", []), "do-install": ("pull", ["--apply"]),
}
NEED_CFG = {"status", "push", "pull"}

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    cmd, rest = sys.argv[1], sys.argv[2:]
    if cmd in ALIASES:
        cmd, extra = ALIASES[cmd]
        rest = rest + extra
    if cmd == "config":
        cmd_config(rest); return
    if cmd not in NEED_CFG:
        print(f"[ERROR] 未知命令: {cmd}"); sys.exit(1)
    cfg = require_config()
    {"status": cmd_status, "push": cmd_push, "pull": cmd_pull}[cmd](rest, cfg)

if __name__ == "__main__":
    main()
