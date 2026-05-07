#!/usr/bin/env python3
"""
skill-sync bootstrap -- 在新环境上安装 skill-sync 本身
无外部依赖，仅使用 Python 标准库，Python 3.6+ 均可运行

用法:
  python bootstrap.py --token ghp_xxx --repo user/skills-repo
  python bootstrap.py --token ghp_xxx --repo user/skills-repo --install-to /custom/path

环境变量（优先级低于命令行参数）:
  SKILL_SYNC_TOKEN   GitHub Personal Access Token
  SKILL_SYNC_REPO    仓库，格式 user/repo-name

安装完成后会在安装路径下创建 skill-sync/ 目录，并初始化 ~/.skill-sync-config.json。
"""

import argparse
import base64
import json
import os
import stat
import sys
import urllib.error
import urllib.request
from pathlib import Path


CONFIG_FILE  = Path.home() / ".skill-sync-config.json"
SKILL_NAME   = "skill-sync"


# 向 GitHub API 发送请求，返回 (响应 dict, HTTP 状态码)
def gh_request(token, method, url, data=None):
    headers = {
        "Authorization": f"token {token}",
        "Accept":        "application/vnd.github.v3+json",
        "Content-Type":  "application/json",
        "User-Agent":    "skill-sync-bootstrap/1.0",
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


# 验证 Token 是否有效，并打印仓库基本信息
def verify_token(token, repo):
    url  = f"https://api.github.com/repos/{repo}"
    data, status = gh_request(token, "GET", url)
    if status == 200:
        print(f"[OK] 认证成功，仓库: {data.get('full_name')}  (private: {data.get('private')})")
        return True
    elif status == 401:
        print("[ERROR] Token 无效或已过期，请检查后重试")
    elif status == 404:
        print("[ERROR] 仓库不存在或 Token 无权访问该仓库")
    else:
        print(f"[ERROR] 验证失败 (HTTP {status}): {data.get('message', data)}")
    return False


# 获取仓库完整文件树（recursive）
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


# 从文件树中提取 skill-sync/ 下的所有 blob，下载并写入 install_path
def download_skill_sync(token, repo, install_path, tree):
    prefix = SKILL_NAME + "/"
    blobs  = [(item["path"], item["sha"]) for item in tree
              if item["type"] == "blob" and item["path"].startswith(prefix)]

    if not blobs:
        print(f"[ERROR] 仓库中未找到 {SKILL_NAME}/ 目录，请确认 skill 已上传到 GitHub")
        return False

    print(f"[FETCH] 找到 {len(blobs)} 个文件，开始下载...")
    for path, sha in blobs:
        content = download_blob(token, repo, sha)
        if content is None:
            print(f"  [ERROR] 下载失败: {path}")
            continue
        target = Path(install_path) / path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(content)
        print(f"  [OK] {path}")

    return True


# 读取已有配置文件，合并写入新的 token/repo/profile，并设置文件权限 600
def write_config(token, repo, install_path, profile_name):
    # 保留已有配置，只追加/更新必要字段
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {}

    config["github_token"] = token
    config["github_repo"]  = repo

    profiles = config.setdefault("profiles", {})
    profiles[profile_name] = {
        "local_skills_path": str(install_path),
        "description":       f"bootstrapped on {sys.platform}",
    }
    if "active_profile" not in config:
        config["active_profile"] = profile_name

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    try:
        os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass

    print(f"[OK] 配置已写入: {CONFIG_FILE}  (profile: {profile_name})")


# 平台默认的 skills 安装路径
def default_install_path():
    if sys.platform == "win32":
        base = Path(os.environ.get("USERPROFILE", Path.home()))
    else:
        base = Path.home()
    return base / ".claude" / "skills"


def main():
    parser = argparse.ArgumentParser(
        description="在新环境上安装 skill-sync（无需已有 skill-sync）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--token",      help="GitHub Personal Access Token (或设置 SKILL_SYNC_TOKEN)")
    parser.add_argument("--repo",       help="GitHub 仓库，格式 user/repo (或设置 SKILL_SYNC_REPO)")
    parser.add_argument("--install-to", help=f"skills 安装路径 (默认: {default_install_path()})")
    parser.add_argument("--profile",    default="default", help="写入配置时使用的 profile 名称 (默认: default)")
    args = parser.parse_args()

    token      = args.token or os.environ.get("SKILL_SYNC_TOKEN", "")
    repo       = args.repo  or os.environ.get("SKILL_SYNC_REPO",  "")
    install_to = Path(args.install_to).expanduser() if args.install_to else default_install_path()

    if not token:
        print("[ERROR] 请通过 --token 参数或 SKILL_SYNC_TOKEN 环境变量提供 GitHub Token")
        print("        获取方式: https://github.com/settings/tokens  (需要 repo 权限)")
        sys.exit(1)
    if not repo:
        print("[ERROR] 请通过 --repo 参数或 SKILL_SYNC_REPO 环境变量提供仓库名 (user/repo)")
        sys.exit(1)

    print(f"skill-sync bootstrap")
    print(f"  仓库       : {repo}")
    print(f"  安装路径   : {install_to}")
    print(f"  Profile    : {args.profile}")
    print()

    # 1. 验证 Token
    if not verify_token(token, repo):
        sys.exit(1)

    # 2. 获取文件树
    print("[FETCH] 获取仓库文件树...")
    tree = get_repo_tree(token, repo)
    if tree is None:
        sys.exit(1)

    # 3. 下载 skill-sync
    print(f"[FETCH] 下载 {SKILL_NAME} ...")
    ok = download_skill_sync(token, repo, install_to, tree)
    if not ok:
        sys.exit(1)

    # 4. 写入配置
    write_config(token, repo, install_to, args.profile)

    script_path = install_to / SKILL_NAME / "scripts" / "skill_sync.py"
    print()
    print("[OK] Bootstrap 完成！")
    print(f"     运行以下命令验证：")
    print(f"     python {script_path} config")
    print(f"     python {script_path} list-remote")


if __name__ == "__main__":
    main()
