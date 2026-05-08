#!/usr/bin/env python3
"""
skill-sync -- 管理 skills 与 GitHub 仓库的同步
"""
import json, os, shutil, subprocess, sys, tempfile, urllib.error, urllib.request
from pathlib import Path

CONFIG_FILE = Path.home() / ".skill-sync-config.json"
SKIP = {"__pycache__", ".git", "node_modules"}

def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0 and check:
        print(f"  [ERROR] {r.stderr.strip()}")
    return r

def gh(token, method, url, data=None):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json"}
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r: return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read()), e.code
        except: return {"error": str(e)}, e.code

def load_config():
    if not CONFIG_FILE.exists(): return {}
    with open(CONFIG_FILE) as f: return json.load(f)

def require_config():
    c = load_config()
    if not c.get("github_token") or not c.get("github_repo"):
        print("[ERROR] 未配置，请运行 python skill_sync.py config set"); sys.exit(1)
    profile = c.get("active_profile", "default")
    profiles = c.get("profiles", {})
    if profile not in profiles:
        lp = c.get("local_skills_path", str(Path.home() / ".claude" / "skills"))
        return {"github_token": c["github_token"], "github_repo": c["github_repo"], "local_skills_path": lp}
    lp = profiles[profile].get("local_skills_path", "")
    return {"github_token": c["github_token"], "github_repo": c["github_repo"], "local_skills_path": str(Path(lp).expanduser()) if lp else str(Path.home() / ".claude" / "skills")}

def config_show():
    c = load_config()
    if not c: print("[WARN] 未配置"); return
    token = c.get("github_token", ""); masked = ("*" * max(0, len(token)-4) + token[-4:]) if token else "(未设置)"
    print(f"github_token : {masked}")
    print(f"github_repo  : {c.get('github_repo', '(未设置)')}")
    print(f"active_profile: {c.get('active_profile', 'default')}")
    profiles = c.get("profiles", {})
    for n, i in profiles.items():
        m = " *" if n == c.get("active_profile") else "  "
        print(f"{m} {n}: {i.get('local_skills_path', '')}")

def config_set(args):
    c = load_config()
    cur = c.get("github_token", ""); hint = f"当前: ...{cur[-4:]}" if len(cur) > 4 else "未设置"
    val = input(f"GitHub Token ({hint}): ").strip()
    if val: c["github_token"] = val
    val = input(f"GitHub 仓库 (user/repo) [{c.get('github_repo', '')}]: ").strip()
    if val: c["github_repo"] = val
    profiles = c.setdefault("profiles", {})
    if not profiles:
        lp = str(Path.home() / ".claude" / "skills")
        profiles["default"] = {"local_skills_path": lp, "description": "默认"}
        c["active_profile"] = "default"
    with open(CONFIG_FILE, "w") as f: json.dump(c, f, indent=2)
    print(f"[OK] 配置已保存")

def cmd_list_local(args, cfg):
    path = Path(cfg["local_skills_path"])
    if not path.exists(): print("本地暂无 skills"); return
    skills = sorted(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    print(f"本地 skills ({len(skills)} 个)  路径: {cfg['local_skills_path']}")
    for s in skills: print(f"  - {s}")

def cmd_list_remote(args, cfg):
    url = f"https://api.github.com/repos/{cfg['github_repo']}/contents/"
    data, st = gh(cfg["github_token"], "GET", url)
    if st != 200: print(f"[ERROR] 获取失败: {data.get('message')}"); return
    dirs = sorted(i["name"] for i in data if i["type"] == "dir")
    print(f"GitHub skills ({len(dirs)} 个)  仓库: {cfg['github_repo']}")
    for s in dirs: print(f"  - {s}")

def cmd_diff(args, cfg):
    path = Path(cfg["local_skills_path"])
    local = set(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if path.exists() else set()
    url = f"https://api.github.com/repos/{cfg['github_repo']}/contents/"
    data, st = gh(cfg["github_token"], "GET", url)
    remote = set(i["name"] for i in data if i["type"] == "dir") if st == 200 else set()
    print(f"[DIFF] 本地: {len(local)} 个  GitHub: {len(remote)} 个")
    for s in sorted(local - remote): print(f"  [LOCAL] {s}")
    for s in sorted(remote - local): print(f"  [REMOTE] {s}")
    for s in sorted(local & remote): print(f"  [BOTH] {s}")

def _skill_files(skill_dir):
    for fp in sorted(skill_dir.rglob("*")):
        if not fp.is_file(): continue
        parts = fp.relative_to(skill_dir).parts
        if any(p in SKIP for p in parts): continue
        yield fp, fp.relative_to(skill_dir.parent).as_posix()

def _read_skill_desc(skill_dir):
    """从 SKILL.md frontmatter 读取 description"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists(): return ""
    content = skill_md.read_text(encoding="utf-8")
    if not content.startswith("---"): return ""
    parts = content.split("---", 2)
    if len(parts) < 3: return ""
    for line in parts[1].strip().split("\n"):
        if line.strip().startswith("description:"):
            return line.split(":", 1)[1].strip()
    return ""

def _update_readme(repo_dir):
    """根据仓库中的 skills 自动更新 README.md"""
    skills = []
    for d in sorted(repo_dir.iterdir()):
        if not d.is_dir() or d.name.startswith(".") or d.name in SKIP: continue
        if not (d / "SKILL.md").exists(): continue
        desc = _read_skill_desc(d)
        skills.append((d.name, desc))
    if not skills: return
    table = "\n".join(f"| {name} | {desc} |" for name, desc in skills)
    readme = f"""# myskills

个人 Agent Skills 仓库，支持 Claude Code、OpenCode、Codex 等 Agent。

## 第一次安装

将以下提示词粘贴给 Agent，让她自动完成安装：

---

**请帮我安装 skills 仓库：**

~~~text
请执行以下步骤：
1. 运行：git clone https://github.com/CherryYang05/myskills.git ~/.claude/skills
2. 运行：python ~/.claude/skills/skill-sync/scripts/skill_sync.py config
3. 如果提示未配置，请运行：python ~/.claude/skills/skill-sync/scripts/skill_sync.py config set
4. 输入 GitHub Token（如果需要）：YOUR_GITHUB_TOKEN
5. 输入仓库名：CherryYang05/myskills
6. 完成后运行 list-local 验证
~~~

---

## 已收录的 Skills

| Skill | 说明 |
|-------|------|
{table}

## 常用同步命令

~~~bash
# 上传本地 skills 到 GitHub
python ~/.claude/skills/skill-sync/scripts/skill_sync.py upload <name>
python ~/.claude/skills/skill-sync/scripts/skill_sync.py do-upload <name>

# 从 GitHub 安装 skills 到本地
python ~/.claude/skills/skill-sync/scripts/skill_sync.py install <name>
python ~/.claude/skills/skill-sync/scripts/skill_sync.py do-install <name>
~~~

## 注意

- git 需已配置（Agent 会提示用户配置）
- 配置文件：`~/.skill-sync-config.json`
"""
    (repo_dir / "README.md").write_text(readme, encoding="utf-8")
    print("  [OK] README.md 已更新")

def cmd_upload(args, cfg):
    path = Path(cfg["local_skills_path"])
    local = sorted(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if path.exists() else []
    url = f"https://api.github.com/repos/{cfg['github_repo']}/contents/"
    data, st = gh(cfg["github_token"], "GET", url)
    remote = set(i["name"] for i in data if i["type"] == "dir") if st == 200 else set()
    targets = [s for s in (args or local) if s in local and s not in remote]
    if not targets: print("[OK] 无新 skills"); return
    print(f"[UPLOAD] 将上传 {len(targets)} 个: {', '.join(targets)}")
    print(f"##CONFIRM_UPLOAD## {json.dumps(targets)}")

def cmd_do_upload(args, cfg):
    if not args: return
    token, repo, base = cfg["github_token"], cfg["github_repo"], Path(cfg["local_skills_path"])
    tmp = Path(tempfile.mkdtemp())
    run(f"git clone --depth=1 https://{token}@github.com/{repo}.git {tmp}/repo")
    repo_dir = tmp / "repo"
    uploaded = []
    for name in args:
        src = base / name
        if not src.exists(): print(f"[ERROR] 不存在: {src}"); continue
        files = list(_skill_files(src))
        if not files: print(f"[WARN] {name} 无文件"); continue
        dst = repo_dir / name
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src, dst)
        uploaded.append(name)
        for _, rel in files: print(f"  [OK] {rel}")
    if uploaded:
        _update_readme(repo_dir)
        os.chdir(repo_dir)
        run("git add .")
        msg = "sync: upload " + ", ".join(uploaded)
        r = run(f'git commit -m "{msg}"')
        if r.returncode == 0:
            r = run("git push")
        if r.returncode != 0:
            print(f"  [ERROR] 推送失败")
    os.chdir("/")
    shutil.rmtree(tmp, ignore_errors=True)

def cmd_install(args, cfg):
    url = f"https://api.github.com/repos/{cfg['github_repo']}/contents/"
    data, st = gh(cfg["github_token"], "GET", url)
    if st != 200: print(f"[ERROR] 获取失败: {data.get('message')}"); return
    targets = args or [i["name"] for i in data if i["type"] == "dir"]
    print(f"[INSTALL] 将安装到 {cfg['local_skills_path']}: {', '.join(targets)}")
    print(f"##CONFIRM_INSTALL## {json.dumps(targets)}")

def cmd_do_install(args, cfg):
    if not args: return
    token, repo, base = cfg["github_token"], cfg["github_repo"], Path(cfg["local_skills_path"])
    tmp = Path(tempfile.mkdtemp())
    run(f"git clone --depth=1 https://{token}@github.com/{repo}.git {tmp}/repo")
    for name in args:
        src = tmp / "repo" / name
        if not src.exists(): print(f"[ERROR] GitHub 上不存在: {name}"); continue
        dst = base / name
        if dst.exists(): shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"[OK] {name} -> {dst}")
    shutil.rmtree(tmp, ignore_errors=True)

def cmd_update(args, cfg):
    path = Path(cfg["local_skills_path"])
    local = set(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if path.exists() else set()
    url = f"https://api.github.com/repos/{cfg['github_repo']}/contents/"
    data, st = gh(cfg["github_token"], "GET", url)
    remote = set(i["name"] for i in data if i["type"] == "dir") if st == 200 else set()
    targets = sorted(s for s in (args or local) if s in local and s in remote)
    if not targets: print("[OK] 无可更新"); return
    print(f"[UPDATE] 将更新: {', '.join(targets)}")
    print(f"##CONFIRM_UPDATE## {json.dumps(targets)}")

def cmd_do_update(args, cfg):
    cmd_do_upload(args, cfg)

COMMANDS = {
    "config": (config_show, config_set),
    "list-local": (cmd_list_local,),
    "list-remote": (cmd_list_remote,),
    "diff": (cmd_diff,),
    "upload": (cmd_upload,),
    "do-upload": (cmd_do_upload,),
    "install": (cmd_install,),
    "do-install": (cmd_do_install,),
    "update": (cmd_update,),
    "do-update": (cmd_do_update,),
}

if __name__ == "__main__":
    if len(sys.argv) < 2: print(__doc__); sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "config":
        if len(sys.argv) > 2 and sys.argv[2] == "set":
            config_set(sys.argv[2:])
        else:
            config_show()
    elif cmd in COMMANDS:
        cfg = require_config()
        COMMANDS[cmd][0](sys.argv[2:], cfg)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
