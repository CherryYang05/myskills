#!/usr/bin/env python3
"""
skill-sync -- 管理 skills 与 GitHub 仓库的同步
"""
import base64, json, os, re, shutil, subprocess, sys, tempfile, urllib.error, urllib.request
from pathlib import Path

CONFIG_FILE = Path.home() / ".skill-sync-config.json"
SKIP = {"__pycache__", ".git", "node_modules"}


def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if r.returncode != 0 and check:
        print(f"  [ERROR] {r.stderr.strip()}")
    return r


def gh(token, method, url, data=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read()), e.code
        except:
            return {"error": str(e)}, e.code
    except urllib.error.URLError:
        # api.github.com 可能被网络策略屏蔽
        return {"error": "network unreachable"}, 0


def _clone_repo(token, repo):
    """克隆仓库到临时目录，返回 Path。调用方负责 shutil.rmtree 清理。"""
    tmp = Path(tempfile.mkdtemp())
    r = run(f"git clone --depth=1 https://{token}@github.com/{repo}.git {tmp}/repo", check=False)
    if r.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        return None
    return tmp / "repo"


def _list_remote_skills_via_api(token, repo):
    """通过 API 获取远端 skill 列表，失败返回 None"""
    url = f"https://api.github.com/repos/{repo}/contents/"
    data, st = gh(token, "GET", url)
    if st == 200:
        return set(i["name"] for i in data if i["type"] == "dir")
    return None


def _list_remote_skills_via_git(token, repo):
    """通过 git clone 获取远端 skill 列表"""
    repo_dir = _clone_repo(token, repo)
    if not repo_dir:
        return None
    try:
        return set(d.name for d in repo_dir.iterdir()
                   if d.is_dir() and d.name not in SKIP and (d / "SKILL.md").exists())
    finally:
        shutil.rmtree(repo_dir.parent, ignore_errors=True)


def _list_remote_skills(token, repo):
    """获取远端 skill 列表，优先 API，失败回退 git clone"""
    result = _list_remote_skills_via_api(token, repo)
    if result is not None:
        return result
    return _list_remote_skills_via_git(token, repo) or set()


def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE) as f:
        return json.load(f)


def _detect_local_skills_path():
    """检测当前环境的 skills 路径"""
    if Path("/mnt/skills/user").exists():
        return "/mnt/skills/user"
    home = Path(os.environ.get("USERPROFILE", str(Path.home())))
    return str(home / ".claude" / "skills")


def require_config():
    c = load_config()
    if not c.get("github_token") or not c.get("github_repo"):
        print("[ERROR] 未配置，请运行: python skill_sync.py config init --token <TOKEN> --repo <OWNER/REPO>")
        sys.exit(1)
    profile = c.get("active_profile", "default")
    profiles = c.get("profiles", {})
    if profile not in profiles:
        lp = c.get("local_skills_path", _detect_local_skills_path())
        return {"github_token": c["github_token"], "github_repo": c["github_repo"], "local_skills_path": lp}
    lp = profiles[profile].get("local_skills_path", "")
    return {
        "github_token": c["github_token"],
        "github_repo": c["github_repo"],
        "local_skills_path": str(Path(lp).expanduser()) if lp else _detect_local_skills_path(),
    }


# ── config 命令 ──────────────────────────────────────────────

def config_show():
    c = load_config()
    if not c:
        print("[WARN] 未配置")
        return
    token = c.get("github_token", "")
    masked = ("*" * max(0, len(token) - 4) + token[-4:]) if token else "(未设置)"
    print(f"github_token  : {masked}")
    print(f"github_repo   : {c.get('github_repo', '(未设置)')}")
    print(f"active_profile: {c.get('active_profile', 'default')}")
    profiles = c.get("profiles", {})
    for n, i in profiles.items():
        m = " *" if n == c.get("active_profile") else "  "
        print(f"{m} {n}: {i.get('local_skills_path', '')}")


def config_init(args):
    """非交互式配置：config init --token <T> --repo <R> [--local-path <P>] [--profile <N>]"""
    token = repo = local_path = None
    profile = "default"
    i = 0
    while i < len(args):
        if args[i] == "--token" and i + 1 < len(args):
            token = args[i + 1]; i += 2
        elif args[i] == "--repo" and i + 1 < len(args):
            repo = args[i + 1]; i += 2
        elif args[i] == "--local-path" and i + 1 < len(args):
            local_path = args[i + 1]; i += 2
        elif args[i] == "--profile" and i + 1 < len(args):
            profile = args[i + 1]; i += 2
        else:
            i += 1
    if not token or not repo:
        print("[ERROR] 必须提供 --token 和 --repo")
        sys.exit(1)
    if local_path is None:
        local_path = _detect_local_skills_path()
    c = load_config()
    c["github_token"] = token
    c["github_repo"] = repo
    profiles = c.setdefault("profiles", {})
    profiles[profile] = {"local_skills_path": local_path, "description": f"init on {sys.platform}"}
    c["active_profile"] = profile
    with open(CONFIG_FILE, "w") as f:
        json.dump(c, f, indent=2)
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except:
        pass
    print(f"[OK] 配置已保存: repo={repo}, profile={profile}, path={local_path}")


def config_set(args):
    """交互式配置（仅本地终端环境可用）"""
    c = load_config()
    cur = c.get("github_token", "")
    hint = f"当前: ...{cur[-4:]}" if len(cur) > 4 else "未设置"
    val = input(f"GitHub Token ({hint}): ").strip()
    if val:
        c["github_token"] = val
    val = input(f"GitHub 仓库 (user/repo) [{c.get('github_repo', '')}]: ").strip()
    if val:
        c["github_repo"] = val
    profiles = c.setdefault("profiles", {})
    if not profiles:
        lp = _detect_local_skills_path()
        profiles["default"] = {"local_skills_path": lp, "description": "默认"}
        c["active_profile"] = "default"
    with open(CONFIG_FILE, "w") as f:
        json.dump(c, f, indent=2)
    print(f"[OK] 配置已保存")


# ── list / diff 命令 ─────────────────────────────────────────

def cmd_list_local(args, cfg):
    path = Path(cfg["local_skills_path"])
    if not path.exists():
        print("本地暂无 skills")
        return
    skills = sorted(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists())
    print(f"本地 skills ({len(skills)} 个)  路径: {cfg['local_skills_path']}")
    for s in skills:
        print(f"  - {s}")


def cmd_list_remote(args, cfg):
    remote = _list_remote_skills(cfg["github_token"], cfg["github_repo"])
    if not remote and remote is not None:
        print("GitHub 上暂无 skills")
        return
    dirs = sorted(remote)
    print(f"GitHub skills ({len(dirs)} 个)  仓库: {cfg['github_repo']}")
    for s in dirs:
        print(f"  - {s}")


def cmd_diff(args, cfg):
    path = Path(cfg["local_skills_path"])
    local = set(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if path.exists() else set()
    remote = _list_remote_skills(cfg["github_token"], cfg["github_repo"])
    print(f"[DIFF] 本地: {len(local)} 个  GitHub: {len(remote)} 个")
    for s in sorted(local - remote):
        print(f"  [LOCAL] {s}")
    for s in sorted(remote - local):
        print(f"  [REMOTE] {s}")
    for s in sorted(local & remote):
        print(f"  [BOTH] {s}")


# ── 通用 git push 逻辑 ──────────────────────────────────────

def _skill_files(skill_dir):
    for fp in sorted(skill_dir.rglob("*")):
        if not fp.is_file():
            continue
        parts = fp.relative_to(skill_dir).parts
        if any(p in SKIP for p in parts):
            continue
        yield fp, fp.relative_to(skill_dir.parent).as_posix()


def _git_push(token, repo, skill_name, src_dir):
    """通用 git clone → copy → commit → push"""
    tmp = Path(tempfile.mkdtemp())
    try:
        r = run(f"git clone --depth=1 https://{token}@github.com/{repo}.git {tmp}/repo")
        if r.returncode != 0:
            print(f"[ERROR] git clone 失败")
            return False
        dst = tmp / "repo" / skill_name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src_dir, dst)
        os.chdir(tmp / "repo")
        run("git add .")
        r = run(f'git commit -m "sync: update {skill_name}"')
        if r.returncode != 0:
            print(f"[INFO] {skill_name} 无变更")
            return True
        r = run("git push")
        if r.returncode == 0:
            files = list(_skill_files(dst))
            for _, rel in files:
                print(f"  [OK] {rel}")
            return True
        else:
            print(f"[ERROR] {skill_name} 推送失败")
            return False
    finally:
        os.chdir("/")
        shutil.rmtree(tmp, ignore_errors=True)


# ── upload / update / install 命令 ───────────────────────────

def cmd_upload(args, cfg):
    path = Path(cfg["local_skills_path"])
    local = sorted(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if path.exists() else []
    remote = _list_remote_skills(cfg["github_token"], cfg["github_repo"])
    targets = [s for s in (args or local) if s in local and s not in remote]
    if not targets:
        print("[OK] 无新 skills")
        return
    print(f"[UPLOAD] 将上传 {len(targets)} 个: {', '.join(targets)}")
    print(f"##CONFIRM_UPLOAD## {json.dumps(targets)}")


def cmd_do_upload(args, cfg):
    if not args:
        return
    base = Path(cfg["local_skills_path"])
    for name in args:
        src = base / name
        if not src.exists():
            print(f"[ERROR] 不存在: {src}")
            continue
        _git_push(cfg["github_token"], cfg["github_repo"], name, src)


def cmd_install(args, cfg):
    remote = _list_remote_skills(cfg["github_token"], cfg["github_repo"])
    if not remote:
        print("[ERROR] 获取远端 skills 失败")
        return
    targets = args or sorted(remote)
    print(f"[INSTALL] 将安装到 {cfg['local_skills_path']}: {', '.join(targets)}")
    print(f"##CONFIRM_INSTALL## {json.dumps(targets)}")


def cmd_do_install(args, cfg):
    if not args:
        return
    token, repo, base = cfg["github_token"], cfg["github_repo"], Path(cfg["local_skills_path"])
    tmp = Path(tempfile.mkdtemp())
    run(f"git clone --depth=1 https://{token}@github.com/{repo}.git {tmp}/repo")
    for name in args:
        src = tmp / "repo" / name
        if not src.exists():
            print(f"[ERROR] GitHub 上不存在: {name}")
            continue
        dst = base / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        print(f"[OK] {name} -> {dst}")
    shutil.rmtree(tmp, ignore_errors=True)


def cmd_update(args, cfg):
    path = Path(cfg["local_skills_path"])
    local = set(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()) if path.exists() else set()
    remote = _list_remote_skills(cfg["github_token"], cfg["github_repo"])
    targets = sorted(s for s in (args or local) if s in local and s in remote)
    if not targets:
        print("[OK] 无可更新")
        return
    print(f"[UPDATE] 将更新: {', '.join(targets)}")
    print(f"##CONFIRM_UPDATE## {json.dumps(targets)}")


def cmd_do_update(args, cfg):
    cmd_do_upload(args, cfg)


# ── push 命令（从任意路径推送） ──────────────────────────────

def cmd_push(args, cfg):
    """从任意本地路径推送到 GitHub 仓库。
    用法: push <skill-name> <source-dir-or-file>
    如果 source 是目录，其中须含 SKILL.md；如果是 SKILL.md 文件本身，用其父目录。
    """
    if len(args) < 2:
        print("[ERROR] 用法: push <skill-name> <source-dir-or-file>")
        return
    name, src = args[0], Path(args[1])
    if not src.exists():
        print(f"[ERROR] 路径不存在: {src}")
        return
    # 如果是文件，转为其所在目录
    if src.is_file():
        if src.name == "SKILL.md":
            src = src.parent
        else:
            print(f"[ERROR] 文件必须是 SKILL.md，实际: {src.name}")
            return
    if not (src / "SKILL.md").exists():
        print(f"[ERROR] {src} 中未找到 SKILL.md")
        return
    print(f"[PUSH] 将推送 {name} (从 {src})")
    print(f"##CONFIRM_PUSH## {json.dumps([name, str(src)])}")


def cmd_do_push(args, cfg):
    """执行 push"""
    if len(args) < 2:
        return
    name, src = args[0], Path(args[1])
    if src.is_file():
        src = src.parent
    _git_push(cfg["github_token"], cfg["github_repo"], name, src)


# ── README 更新 ──────────────────────────────────────────────

def cmd_update_readme(args, cfg):
    """更新 GitHub 仓库 README.md 中的 skills 列表（优先 API，回退 git）"""
    token, repo = cfg["github_token"], cfg["github_repo"]

    # 尝试 API 方式
    url = f"https://api.github.com/repos/{repo}/contents/"
    data, st = gh(token, "GET", url)
    if st == 200:
        _update_readme_via_api(token, repo, data)
    else:
        _update_readme_via_git(token, repo)


def _read_skill_description(skill_dir):
    """从 SKILL.md frontmatter 读取描述，优先 short_description，回退 description"""
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return ""
    content = skill_md.read_text(encoding="utf-8", errors="replace")
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            fm = content[3:end]
            short_desc = desc = ""
            for line in fm.split("\n"):
                stripped = line.strip()
                if stripped.startswith("short_description:"):
                    short_desc = stripped.split(":", 1)[1].strip()
                elif stripped.startswith("description:"):
                    desc = stripped.split(":", 1)[1].strip()
            if short_desc:
                return short_desc
            return desc[:117] + "..." if len(desc) > 120 else desc
    return ""


def _generate_skills_table(skills_info):
    """生成 Markdown 表格"""
    lines = ["## 已收录的 Skills", "", "| Skill | Description |", "|-------|-------------|"]
    for name, desc in skills_info:
        lines.append(f"| [{name}](./{name}) | {desc} |")
    return "\n".join(lines)


def _apply_table_to_readme(readme_content, table_section, repo):
    """将表格写入 README 内容"""
    if readme_content:
        pattern = r"## 已收录的 Skills.*?(?=\n## |\Z)"
        if re.search(pattern, readme_content, re.DOTALL):
            return re.sub(pattern, table_section + "\n", readme_content, flags=re.DOTALL)
        else:
            return readme_content.rstrip() + "\n\n" + table_section + "\n"
    return f"# {repo.split('/')[-1]}\n\nAgent Skills 仓库。\n\n{table_section}\n"


def _update_readme_via_api(token, repo, root_data):
    """通过 GitHub API 更新 README"""
    dirs = sorted(i["name"] for i in root_data if i["type"] == "dir" and i["name"] not in SKIP)
    skills_info = []
    for d in dirs:
        skill_url = f"https://api.github.com/repos/{repo}/contents/{d}/SKILL.md"
        sdata, sst = gh(token, "GET", skill_url)
        desc = ""
        if sst == 200 and "content" in sdata:
            content = base64.b64decode(sdata["content"]).decode("utf-8", errors="replace")
            if content.startswith("---"):
                end = content.find("---", 3)
                if end != -1:
                    fm = content[3:end]
                    short_desc = full_desc = ""
                    for line in fm.split("\n"):
                        stripped = line.strip()
                        if stripped.startswith("short_description:"):
                            short_desc = stripped.split(":", 1)[1].strip()
                        elif stripped.startswith("description:"):
                            full_desc = stripped.split(":", 1)[1].strip()
                    desc = short_desc if short_desc else (full_desc[:117] + "..." if len(full_desc) > 120 else full_desc)
        skills_info.append((d, desc))

    table_section = _generate_skills_table(skills_info)
    readme_url = f"https://api.github.com/repos/{repo}/contents/README.md"
    rdata, rst = gh(token, "GET", readme_url)
    readme_content = base64.b64decode(rdata["content"]).decode("utf-8", errors="replace") if rst == 200 and "content" in rdata else ""
    sha = rdata.get("sha") if rst == 200 else None
    new_content = _apply_table_to_readme(readme_content, table_section, repo)
    put_data = {"message": "docs: update skills table in README", "content": base64.b64encode(new_content.encode()).decode()}
    if sha:
        put_data["sha"] = sha
    result, status = gh(token, "PUT", readme_url, put_data)
    if status in (200, 201):
        print(f"[OK] README 已更新 ({len(skills_info)} 个 skills)")
    else:
        print(f"[WARN] API 更新失败，回退到 git 方式")
        _update_readme_via_git(token, repo)


def _update_readme_via_git(token, repo):
    """通过 git clone → edit → push 更新 README"""
    repo_dir = _clone_repo(token, repo)
    if not repo_dir:
        print("[ERROR] git clone 失败")
        return

    try:
        # 扫描所有 skill 目录
        dirs = sorted(d.name for d in repo_dir.iterdir()
                       if d.is_dir() and d.name not in SKIP and (d / "SKILL.md").exists())
        skills_info = [(d, _read_skill_description(repo_dir / d)) for d in dirs]
        table_section = _generate_skills_table(skills_info)

        # 读取或创建 README
        readme_path = repo_dir / "README.md"
        readme_content = readme_path.read_text(encoding="utf-8", errors="replace") if readme_path.exists() else ""
        new_content = _apply_table_to_readme(readme_content, table_section, repo)
        readme_path.write_text(new_content, encoding="utf-8")

        # commit & push
        os.chdir(repo_dir)
        run("git add README.md")
        r = run('git commit -m "docs: update skills table in README"')
        if r.returncode != 0:
            print("[INFO] README 无变更")
            return
        r = run("git push")
        if r.returncode == 0:
            print(f"[OK] README 已更新 ({len(skills_info)} 个 skills)")
        else:
            print("[ERROR] README 推送失败")
    finally:
        os.chdir("/")
        shutil.rmtree(repo_dir.parent, ignore_errors=True)


# ── 入口 ─────────────────────────────────────────────────────

COMMANDS = {
    "list-local": (cmd_list_local,),
    "list-remote": (cmd_list_remote,),
    "diff": (cmd_diff,),
    "upload": (cmd_upload,),
    "do-upload": (cmd_do_upload,),
    "install": (cmd_install,),
    "do-install": (cmd_do_install,),
    "update": (cmd_update,),
    "do-update": (cmd_do_update,),
    "push": (cmd_push,),
    "do-push": (cmd_do_push,),
    "update-readme": (cmd_update_readme,),
}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]

    if cmd == "config":
        sub = sys.argv[2] if len(sys.argv) > 2 else "show"
        if sub == "init":
            config_init(sys.argv[3:])
        elif sub == "set":
            config_set(sys.argv[3:])
        else:
            config_show()
    elif cmd in COMMANDS:
        cfg = require_config()
        COMMANDS[cmd][0](sys.argv[2:], cfg)
    else:
        print(f"[ERROR] 未知命令: {cmd}")
