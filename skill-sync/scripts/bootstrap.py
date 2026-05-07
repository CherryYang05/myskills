#!/usr/bin/env python3
"""
skill-sync bootstrap
在新环境安装 skill-sync，使用 git clone（git 需已配置）
"""
import argparse, json, os, shutil, stat, sys, tempfile
from pathlib import Path

CONFIG_FILE = Path.home() / ".skill-sync-config.json"
SKILL_NAME = "skill-sync"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--install-to", default=None)
    parser.add_argument("--profile", default="default")
    args = parser.parse_args()

    install_to = Path(args.install_to) if args.install_to else (
        Path(os.environ.get("USERPROFILE", Path.home())) / ".claude" / "skills"
    skill_path = install_to / SKILL_NAME

    # git clone 到临时目录
    tmp = Path(tempfile.mkdtemp())
    repo_url = f"https://{args.token}@github.com/{args.repo}.git"
    os.system(f"git clone --depth=1 {repo_url} {tmp}/{args.repo.split('/')[1]}")

    # 复制 skill-sync 到安装路径
    src = tmp / args.repo.split("/")[1] / SKILL_NAME
    if src.exists():
        shutil.copytree(src, skill_path, dirs_exist_ok=True)
    else:
        print(f"[ERROR] 仓库中未找到 {SKILL_NAME}/")
        sys.exit(1)

    # 清理临时目录
    shutil.rmtree(tmp, ignore_errors=True)

    # 写入配置
    config = json.load(open(CONFIG_FILE)) if CONFIG_FILE.exists() else {}
    config["github_token"] = args.token
    config["github_repo"] = args.repo
    profiles = config.setdefault("profiles", {})
    profiles[args.profile] = {"local_skills_path": str(install_to), "description": f"bootstrapped on {sys.platform}"}
    config["active_profile"] = args.profile
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    try: os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)
    except: pass

    print(f"[OK] 安装完成: {skill_path}")

if __name__ == "__main__":
    main()
