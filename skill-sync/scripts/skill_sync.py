#!/usr/bin/env python3
"""
skill-sync -- 管理 Claude skills 与 GitHub 仓库的同步
跨平台支持: Windows, Linux, macOS（仅使用标准库）

用法:
  python skill_sync.py [--profile NAME] config                      # 查看当前配置
  python skill_sync.py [--profile NAME] config set                  # 交互式设置配置
  python skill_sync.py config profile list                          # 列出所有 profiles
  python skill_sync.py config profile add NAME PATH [DESCRIPTION]   # 新增 profile
  python skill_sync.py config profile set NAME                      # 切换活跃 profile
  python skill_sync.py config profile remove NAME                   # 删除 profile
  python skill_sync.py [--profile NAME] list-local                  # 列出本地 skills
  python skill_sync.py [--profile NAME] list-remote                 # 列出 GitHub 上的 skills
  python skill_sync.py [--profile NAME] diff                        # 对比本地与 GitHub 的差异
  python skill_sync.py [--profile NAME] upload [name ...]           # 预览上传（仅上传 GitHub 没有的）
  python skill_sync.py [--profile NAME] do-upload name [name ...]   # 确认后实际执行上传
  python skill_sync.py [--profile NAME] install [name ...]          # 预览安装（从 GitHub 下载到本地）
  python skill_sync.py [--profile NAME] do-install name [name ...]  # 确认后实际执行安装
  python skill_sync.py [--profile NAME] update [name ...]           # 预览更新（本地 -> GitHub，覆盖已有）
  python skill_sync.py [--profile NAME] do-update name [name ...]   # 确认后实际执行更新

--profile NAME 可缩写为 -p NAME，用于临时指定路径 profile，不改变配置中的 active_profile。
"""

import json
import sys
import base64
import urllib.request
import urllib.error
import os
import stat
from pathlib import Path

# 配置文件路径（跨平台，存放在用户主目录）
CONFIG_FILE = Path.home() / ".skill-sync-config.json"

# 上传/安装时忽略的文件和目录
SKIP_DIRS  = {"__pycache__", "node_modules", ".git", "evals"}
SKIP_FILES = {".DS_Store", ".gitkeep"}
SKIP_EXTS  = {".pyc"}


# ─────────────────────────── 配置管理 ───────────────────────────

# 从磁盘读取配置文件，不存在时返回空 dict
def load_config():
    if not CONFIG_FILE.exists():
        return {}
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# 将配置写入磁盘，并设置 600 权限保护 Token
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    try:
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass  # Windows 下 chmod 可能不生效，忽略
    print(f"[OK] 配置已保存到: {CONFIG_FILE}")


# 读取配置，若必要字段缺失则打印错误并退出
# profile_name 为 None 时使用 active_profile
def require_config(profile_name=None):
    config = load_config()
    missing_global = [k for k in ("github_token", "github_repo") if not config.get(k)]
    if missing_global:
        print(f"[ERROR] 配置缺失: {', '.join(missing_global)}")
        print("  请运行: python skill_sync.py config set")
        sys.exit(1)

    profile_name = profile_name or config.get("active_profile", "default")
    profiles = config.get("profiles", {})

    if profile_name not in profiles:
        # 兼容旧格式：直接使用顶层 local_skills_path
        legacy_path = config.get("local_skills_path")
        if legacy_path:
            return {
                "github_token":      config["github_token"],
                "github_repo":       config["github_repo"],
                "local_skills_path": legacy_path,
                "profile_name":      "default (legacy)",
            }
        print(f"[ERROR] Profile '{profile_name}' 不存在，请先运行: python skill_sync.py config profile add")
        sys.exit(1)

    local_path = profiles[profile_name].get("local_skills_path", "")
    if not local_path:
        print(f"[ERROR] Profile '{profile_name}' 缺少 local_skills_path")
        sys.exit(1)

    return {
        "github_token":      config["github_token"],
        "github_repo":       config["github_repo"],
        "local_skills_path": str(Path(local_path).expanduser()),
        "profile_name":      profile_name,
    }


# 获取当前活跃 profile 的本地路径（用于交互提示的默认值）
def _default_skills_path():
    if sys.platform == "win32":
        return str(Path(os.environ.get("USERPROFILE", Path.home())) / ".claude" / "skills")
    return str(Path.home() / ".claude" / "skills")


# ─────────────────────────── GitHub API ───────────────────────────

# 通用 GitHub API 请求（仅使用标准库 urllib）
# 返回 (响应 dict, HTTP 状态码)
def gh_request(token, method, url, data=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
        "Content-Type":  "application/json",
        "User-Agent":    "skill-sync/2.0",
    }
    body = json.dumps(data).encode("utf-8") if data else None
    req  = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8")), resp.status
    except urllib.error.HTTPError as e:
        try:
            return json.loads(e.read().decode("utf-8")), e.code
        except Exception:
            return {"error": str(e)}, e.code


# 列出 GitHub 仓库根目录下所有 skill 文件夹（含 SKILL.md 的一级子目录）
def list_remote_skills(token, repo):
    url  = f"https://api.github.com/repos/{repo}/contents/"
    data, status = gh_request(token, "GET", url)
    if status != 200:
        print(f"[ERROR] 获取 GitHub 内容失败 (HTTP {status}): {data.get('message', data)}")
        return None
    return sorted(item["name"] for item in data if item["type"] == "dir")


# 获取 GitHub 上某文件当前的 SHA（PUT 更新文件时必须提供）
def get_file_sha(token, repo, path):
    url  = f"https://api.github.com/repos/{repo}/contents/{path}"
    data, status = gh_request(token, "GET", url)
    if status == 200 and "sha" in data:
        return data["sha"]
    return None


# 上传或更新 GitHub 上的单个文件
# sha 非空时为更新已有文件，为空时为新建文件
def put_file(token, repo, path, content_bytes, message, sha=None):
    url     = f"https://api.github.com/repos/{repo}/contents/{path}"
    payload = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("utf-8"),
    }
    if sha:
        payload["sha"] = sha
    return gh_request(token, "PUT", url, payload)


# 获取仓库完整文件树（recursive），用于批量下载时一次性拿到所有 blob 路径
def get_repo_tree(token, repo):
    url  = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
    data, status = gh_request(token, "GET", url)
    if status != 200:
        print(f"[ERROR] 获取文件树失败 (HTTP {status}): {data.get('message', data)}")
        return None
    return data.get("tree", [])


# 通过 blob SHA 下载单个文件内容，返回 bytes；失败返回 None
def download_blob(token, repo, sha):
    url  = f"https://api.github.com/repos/{repo}/git/blobs/{sha}"
    data, status = gh_request(token, "GET", url)
    if status != 200:
        return None
    raw = data.get("content", "").replace("\n", "")
    return base64.b64decode(raw)


# ─────────────────────────── 本地操作 ───────────────────────────

# 列出本地 skills 目录下所有有效 skill（含 SKILL.md 的一级子目录）
def list_local_skills(local_path):
    path = Path(local_path)
    if not path.exists():
        return []
    return sorted(d.name for d in path.iterdir() if d.is_dir() and (d / "SKILL.md").exists())


# 遍历 skill 目录下所有需要同步的文件
# yield (Path 对象, 相对于 skills 根目录的 POSIX 路径字符串)
def iter_skill_files(skill_dir):
    for fp in sorted(skill_dir.rglob("*")):
        if not fp.is_file():
            continue
        parts = fp.relative_to(skill_dir).parts
        if any(p in SKIP_DIRS for p in parts):
            continue
        if fp.name in SKIP_FILES or fp.suffix in SKIP_EXTS:
            continue
        rel = fp.relative_to(skill_dir.parent).as_posix()
        yield fp, rel


# 将一个 skill 的全部文件上传到 GitHub
# overwrite=True 时跳过 GitHub 上已存在的文件；False 时仅新建
def do_upload_skill(token, repo, skill_name, local_path, overwrite=False):
    skill_dir = Path(local_path) / skill_name
    ok = True
    for fp, rel in iter_skill_files(skill_dir):
        sha = get_file_sha(token, repo, rel) if overwrite else None
        with open(fp, "rb") as f:
            content = f.read()
        action = "更新" if sha else "上传"
        resp, status = put_file(token, repo, rel, content, f"{action} {rel}", sha=sha)
        if status in (200, 201):
            print(f"    [OK] {action}: {rel}")
        else:
            print(f"    [ERROR] {action}失败: {rel} -- {resp.get('message', '')}")
            ok = False
    return ok


# 从 GitHub 下载一个 skill 并写入本地目录
# tree 来自 get_repo_tree，避免重复请求
def do_install_skill(token, repo, skill_name, local_path, tree):
    prefix = skill_name + "/"
    blobs  = [(item["path"], item["sha"]) for item in tree
              if item["type"] == "blob" and item["path"].startswith(prefix)]
    if not blobs:
        print(f"    [ERROR] GitHub 上未找到 {skill_name}")
        return False
    for path, sha in blobs:
        content = download_blob(token, repo, sha)
        if content is None:
            print(f"    [ERROR] 下载失败: {path}")
            continue
        target = Path(local_path) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(content)
        print(f"    [OK] 写入: {path}")
    return True


# ─────────────────────────── 命令处理 ───────────────────────────

# 显示或交互式修改配置
# args=[]        -> 显示当前配置
# args=["set"]   -> 交互式修改全局配置 + 当前 profile 路径
def cmd_config(args, profile_name=None):
    if not args or args[0] != "set":
        config = load_config()
        if not config:
            print("[WARN] 尚未配置。运行: python skill_sync.py config set")
            return
        active = config.get("active_profile", "default")
        token  = config.get("github_token", "")
        masked = ("*" * max(0, len(token) - 4) + token[-4:]) if len(token) > 4 else "(未设置)"
        print(f"github_token : {masked}")
        print(f"github_repo  : {config.get('github_repo', '(未设置)')}")
        print(f"active_profile: {active}")
        profiles = config.get("profiles", {})
        if profiles:
            print("profiles:")
            for name, info in profiles.items():
                marker = " *" if name == active else "  "
                desc   = f"  # {info['description']}" if info.get("description") else ""
                print(f"{marker} {name}: {info.get('local_skills_path', '')}{desc}")
        else:
            # 旧格式兼容
            lp = config.get("local_skills_path", "(未设置)")
            print(f"local_skills_path: {lp}  (旧格式，建议迁移到 profiles)")
        return

    # 交互式配置
    config = load_config()
    print("请输入配置（直接回车保留当前值）:\n")

    cur_token = config.get("github_token", "")
    hint = f"当前: ...{cur_token[-4:]}" if len(cur_token) > 4 else "未设置"
    val = input(f"GitHub Personal Access Token ({hint}): ").strip()
    if val:
        config["github_token"] = val

    cur_repo = config.get("github_repo", "")
    val = input(f"GitHub 仓库 (user/repo) [{cur_repo or '未设置'}]: ").strip()
    if val:
        config["github_repo"] = val

    # 确保至少有一个 profile
    profiles = config.get("profiles", {})
    if not profiles:
        # 兼容旧格式：迁移 local_skills_path 到 profiles
        legacy = config.get("local_skills_path", _default_skills_path())
        val = input(f"本地 skills 路径 (profile: default) [{legacy}]: ").strip()
        profiles["default"] = {"local_skills_path": val or legacy, "description": "默认"}
        config["profiles"]       = profiles
        config["active_profile"] = "default"
        config.pop("local_skills_path", None)
    else:
        active = config.get("active_profile", "default")
        cur_path = profiles.get(active, {}).get("local_skills_path", _default_skills_path())
        val = input(f"本地 skills 路径 (profile: {active}) [{cur_path}]: ").strip()
        profiles[active]["local_skills_path"] = val or cur_path

    save_config(config)


# 管理 profiles（list / add / set / remove）
def cmd_config_profile(args):
    if not args:
        print("用法: config profile <list|add|set|remove> ...")
        return

    sub = args[0]
    config = load_config()
    profiles = config.get("profiles", {})

    if sub == "list":
        if not profiles:
            print("(无 profiles)")
            return
        active = config.get("active_profile", "default")
        for name, info in profiles.items():
            marker = "[active]" if name == active else "        "
            desc   = f"  # {info['description']}" if info.get("description") else ""
            print(f"{marker} {name}: {info.get('local_skills_path', '')}{desc}")

    elif sub == "add":
        # add NAME PATH [DESCRIPTION]
        if len(args) < 3:
            print("用法: config profile add NAME PATH [DESCRIPTION]")
            return
        name, path = args[1], args[2]
        desc = " ".join(args[3:]) if len(args) > 3 else ""
        if name in profiles:
            print(f"[WARN] Profile '{name}' 已存在，将覆盖")
        profiles[name] = {"local_skills_path": path}
        if desc:
            profiles[name]["description"] = desc
        config["profiles"] = profiles
        if "active_profile" not in config:
            config["active_profile"] = name
        save_config(config)
        print(f"[OK] 新增 profile: {name} -> {path}")

    elif sub == "set":
        if len(args) < 2:
            print("用法: config profile set NAME")
            return
        name = args[1]
        if name not in profiles:
            print(f"[ERROR] Profile '{name}' 不存在")
            return
        config["active_profile"] = name
        save_config(config)
        print(f"[OK] 活跃 profile 已切换为: {name}")

    elif sub == "remove":
        if len(args) < 2:
            print("用法: config profile remove NAME")
            return
        name = args[1]
        if name not in profiles:
            print(f"[ERROR] Profile '{name}' 不存在")
            return
        del profiles[name]
        config["profiles"] = profiles
        if config.get("active_profile") == name:
            config["active_profile"] = next(iter(profiles), "")
            print(f"[WARN] 活跃 profile 已自动切换为: {config['active_profile']}")
        save_config(config)
        print(f"[OK] 已删除 profile: {name}")

    else:
        print(f"[ERROR] 未知子命令: {sub}")


# 列出本地 skills
def cmd_list_local(args, profile_name=None):
    config = require_config(profile_name)
    skills = list_local_skills(config["local_skills_path"])
    label  = f"[profile: {config['profile_name']}]"
    if not skills:
        print(f"本地暂无 skills  {label}  路径: {config['local_skills_path']}")
        return
    print(f"本地 skills ({len(skills)} 个)  {label}  路径: {config['local_skills_path']}")
    for s in skills:
        print(f"  - {s}")


# 列出 GitHub 上的 skills
def cmd_list_remote(args, profile_name=None):
    config = require_config(profile_name)
    skills = list_remote_skills(config["github_token"], config["github_repo"])
    if skills is None:
        return
    if not skills:
        print(f"GitHub 仓库暂无 skills  ({config['github_repo']})")
        return
    print(f"GitHub skills ({len(skills)} 个)  仓库: {config['github_repo']}")
    for s in skills:
        print(f"  - {s}")


# 对比本地与 GitHub 的 skill 差异
def cmd_diff(args, profile_name=None):
    config      = require_config(profile_name)
    local       = set(list_local_skills(config["local_skills_path"]))
    remote_list = list_remote_skills(config["github_token"], config["github_repo"])
    if remote_list is None:
        return
    remote      = set(remote_list)
    only_local  = sorted(local - remote)
    only_remote = sorted(remote - local)
    both        = sorted(local & remote)

    print(f"[DIFF] profile: {config['profile_name']}  本地: {len(local)} 个  GitHub: {len(remote)} 个")
    if only_local:
        print(f"\n仅在本地，可上传 ({len(only_local)} 个):")
        for s in only_local:
            print(f"  [LOCAL] {s}")
    if only_remote:
        print(f"\n仅在 GitHub，可下载 ({len(only_remote)} 个):")
        for s in only_remote:
            print(f"  [REMOTE] {s}")
    if both:
        print(f"\n两边都有 ({len(both)} 个):")
        for s in both:
            print(f"  [BOTH] {s}")
    if not only_local and not only_remote and not both:
        print("两边均无 skills。")


# 预览上传：列出将要上传的 skills（仅 GitHub 上没有的），输出 CONFIRM 标记供 Claude 解析
def cmd_upload(args, profile_name=None):
    config      = require_config(profile_name)
    local       = list_local_skills(config["local_skills_path"])
    remote_list = list_remote_skills(config["github_token"], config["github_repo"])
    if remote_list is None:
        return
    remote = set(remote_list)

    if args:
        targets = [s for s in args if s in local]
        missing = [s for s in args if s not in local]
        if missing:
            print(f"[WARN] 本地不存在: {', '.join(missing)}")
    else:
        targets = [s for s in local if s not in remote]

    already  = [s for s in targets if s in remote]
    new_ones = [s for s in targets if s not in remote]

    if already:
        print(f"[WARN] 以下 skills 在 GitHub 已存在，跳过（如需覆盖请用 update）: {', '.join(already)}")
    if not new_ones:
        print("[OK] 没有新 skills 需要上传。")
        return

    print(f"\n[UPLOAD] 将上传以下 {len(new_ones)} 个 skills 到 GitHub ({config['github_repo']}):")
    for s in new_ones:
        print(f"  [NEW] {s}")
    print("\n请告知 Claude 是否确认上传。")
    print(f"##CONFIRM_UPLOAD## {json.dumps(new_ones)}")


# 实际执行上传（Claude 获得用户确认后调用）
def cmd_do_upload(args, profile_name=None):
    if not args:
        print("用法: python skill_sync.py do-upload name [name ...]")
        return
    config = require_config(profile_name)
    for name in args:
        print(f"\n[UPLOAD] 上传 {name} ...")
        ok = do_upload_skill(config["github_token"], config["github_repo"], name,
                             config["local_skills_path"], overwrite=False)
        print(f"[{'OK' if ok else 'ERROR'}] {name} 上传{'完成' if ok else '失败'}")


# 预览安装：列出将要从 GitHub 安装的 skills，输出 CONFIRM 标记
def cmd_install(args, profile_name=None):
    config      = require_config(profile_name)
    remote_list = list_remote_skills(config["github_token"], config["github_repo"])
    if remote_list is None:
        return

    if args:
        targets = [s for s in args if s in remote_list]
        missing = [s for s in args if s not in remote_list]
        if missing:
            print(f"[WARN] GitHub 上不存在: {', '.join(missing)}")
    else:
        targets = remote_list

    if not targets:
        print("没有可安装的 skills。")
        return

    print(f"\n[INSTALL] 将从 GitHub ({config['github_repo']}) 安装以下 {len(targets)} 个 skills:")
    for s in targets:
        print(f"  - {s}")
    print(f"安装位置: {config['local_skills_path']}  [profile: {config['profile_name']}]")
    print("\n请告知 Claude 是否确认安装。")
    print(f"##CONFIRM_INSTALL## {json.dumps(targets)}")


# 实际执行安装（Claude 获得用户确认后调用）
def cmd_do_install(args, profile_name=None):
    if not args:
        print("用法: python skill_sync.py do-install name [name ...]")
        return
    config = require_config(profile_name)
    print("[FETCH] 获取 GitHub 文件树...")
    tree = get_repo_tree(config["github_token"], config["github_repo"])
    if tree is None:
        return
    for name in args:
        print(f"\n[INSTALL] 安装 {name} ...")
        ok = do_install_skill(config["github_token"], config["github_repo"],
                              name, config["local_skills_path"], tree)
        print(f"[{'OK' if ok else 'ERROR'}] {name} 安装{'完成' if ok else '失败'}")


# 预览更新：用本地 skills 覆盖 GitHub 上的同名 skills，输出 CONFIRM 标记
def cmd_update(args, profile_name=None):
    config      = require_config(profile_name)
    local       = set(list_local_skills(config["local_skills_path"]))
    remote_list = list_remote_skills(config["github_token"], config["github_repo"])
    if remote_list is None:
        return
    remote = set(remote_list)

    if args:
        targets    = [s for s in args if s in local and s in remote]
        not_local  = [s for s in args if s not in local]
        not_remote = [s for s in args if s in local and s not in remote]
        if not_local:
            print(f"[WARN] 本地不存在: {', '.join(not_local)}")
        if not_remote:
            print(f"[WARN] GitHub 不存在（请用 upload）: {', '.join(not_remote)}")
    else:
        targets = sorted(local & remote)

    if not targets:
        print("没有可更新的 skills。")
        return

    print(f"\n[UPDATE] 将用本地内容覆盖更新 GitHub ({config['github_repo']}) 上的以下 {len(targets)} 个 skills:")
    for s in targets:
        print(f"  - {s}")
    print("\n请告知 Claude 是否确认更新。")
    print(f"##CONFIRM_UPDATE## {json.dumps(targets)}")


# 实际执行更新（Claude 获得用户确认后调用）
def cmd_do_update(args, profile_name=None):
    if not args:
        print("用法: python skill_sync.py do-update name [name ...]")
        return
    config = require_config(profile_name)
    for name in args:
        print(f"\n[UPDATE] 更新 {name} ...")
        ok = do_upload_skill(config["github_token"], config["github_repo"], name,
                             config["local_skills_path"], overwrite=True)
        print(f"[{'OK' if ok else 'ERROR'}] {name} 更新{'完成' if ok else '失败'}")


# ─────────────────────────── 入口 ───────────────────────────

COMMANDS = {
    "config":       cmd_config,
    "list-local":   cmd_list_local,
    "list-remote":  cmd_list_remote,
    "diff":         cmd_diff,
    "upload":       cmd_upload,
    "do-upload":    cmd_do_upload,
    "install":      cmd_install,
    "do-install":   cmd_do_install,
    "update":       cmd_update,
    "do-update":    cmd_do_update,
}


# 解析命令行：支持 --profile NAME / -p NAME 全局选项，在命令名之前或之后均可
def parse_args(argv):
    args        = argv[1:]
    profile     = None
    clean_args  = []

    i = 0
    while i < len(args):
        if args[i] in ("--profile", "-p") and i + 1 < len(args):
            profile = args[i + 1]
            i += 2
        else:
            clean_args.append(args[i])
            i += 1

    return profile, clean_args


if __name__ == "__main__":
    profile_name, clean_args = parse_args(sys.argv)

    if not clean_args:
        print(__doc__)
        sys.exit(1)

    cmd = clean_args[0]
    rest = clean_args[1:]

    # config profile 是两级子命令，特殊处理
    if cmd == "config" and rest and rest[0] == "profile":
        cmd_config_profile(rest[1:])
        sys.exit(0)

    if cmd not in COMMANDS:
        print(f"[ERROR] 未知命令: {cmd}")
        print(__doc__)
        sys.exit(1)

    # config 不需要 profile（它管理 profile 配置本身）
    if cmd == "config":
        COMMANDS[cmd](rest, profile_name)
    else:
        COMMANDS[cmd](rest, profile_name)
