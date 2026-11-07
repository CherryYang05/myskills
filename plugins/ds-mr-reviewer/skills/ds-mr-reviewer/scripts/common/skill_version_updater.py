#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DS MR Reviewer Skill 版本自动更新脚本

在前置条件检查阶段被调用，自动检测市场最新版本并升级。

用法:
    python skill_version_updater.py --version 3.4.0

流程:
    1. 通过 MCP 查询 skill 市场中 ds-mr-reviewer 的最新版本号
    2. 与本地版本对比
    3. 若本地版本落后，通过 nga 和 codeagent 两个平台分别自动安装最新版

依赖:
    pip install httpx fastmcp
    Windows 环境还需 pywin32 (用于 DPAPI 解密 auth token)
"""

import argparse
import asyncio
import io
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

# 使用系统默认编码输出（Windows 为 GBK，Linux 为 UTF-8）
# 不要强制 UTF-8，否则在 GBK 终端会乱码

# 确保 common 目录在 sys.path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from mcp_client_utils import (
    get_auth_token, build_mcp_headers, create_direct_http_client,
)

from fastmcp import Client
from fastmcp.client import StreamableHttpTransport


# ======================== 常量 ========================

SKILL_NAME = "ds-mr-reviewer"
SKILL_TYPE = "skill"
TZ_AI_MCP_URL = "http://tianzhou.huawei.com/agent/tools/common/mcp"
QUERY_TOOL_NAME = "querySkills"

# nga 安装交互控制字符
ENTER = b"\r"
DOWN_ARROW = b"\x1b[B"

# codeagent 安装命令
CODEAGENT_SKILLS_ADD = 'powershell -Command "codeagent skills add {skill_name}@{version}"'


# ======================== 版本号比较 ========================


def parse_version(version_str: str) -> tuple[int, ...]:
    """将版本字符串解析为可比较的元组

    Args:
        version_str: 版本号，如 "3.4.0"

    Returns:
        (3, 4, 0)
    """
    parts = []
    for part in version_str.strip().split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def is_newer(remote_version: str, local_version: str) -> bool:
    """判断 remote_version 是否比 local_version 更新

    Args:
        remote_version: 市场版本号
        local_version: 本地版本号

    Returns:
        True 表示市场版本更新
    """
    return parse_version(remote_version) > parse_version(local_version)


# ======================== MCP 查询市场版本 ========================


async def _query_latest_version(local_version: str) -> dict:
    """通过 MCP 查询 skill 市场中 ds-mr-reviewer 的最新版本

    Args:
        local_version: 当前本地版本号

    Returns:
        {
            "status": "up_to_date" / "update_available" / "query_failed",
            "local_version": ...,
            "latest_version": ... or None,
            "msg": ...
        }
    """
    try:
        token = get_auth_token()
    except (FileNotFoundError, ValueError) as e:
        return _build_result("query_failed", local_version, None, f"获取认证 token 失败: {e}")

    headers = build_mcp_headers(token)

    try:
        transport = StreamableHttpTransport(
            url=TZ_AI_MCP_URL,
            headers=headers,
            httpx_client_factory=create_direct_http_client,
        )

        async with Client(transport) as client:
            result = await client.call_tool(QUERY_TOOL_NAME, {
                "keyword": SKILL_NAME,
                "pageNum": 1,
                "pageSize": 5,
            })

            if not result or not result.content:
                return _build_result("query_failed", local_version, None, "MCP 返回为空")

            # 解析返回内容
            text = getattr(result.content[0], "text", None)
            if not text:
                return _build_result("query_failed", local_version, None, "MCP 返回内容为空")

            # 尝试解析 JSON
            try:
                data = json.loads(text)
            except json.JSONDecodeError:
                # 尝试多行 JSON
                latest_version = None
                for line in text.strip().split("\n"):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            break
                        except json.JSONDecodeError:
                            continue
                else:
                    return _build_result("query_failed", local_version, None, f"无法解析 MCP 返回: {text[:200]}")

            # 从返回数据中提取最新版本号
            latest_version = _extract_version_from_response(data)
            if not latest_version:
                return _build_result("query_failed", local_version, None, f"未在市场数据中找到版本号: {json.dumps(data, ensure_ascii=False)[:300]}")

            # 版本对比
            if is_newer(latest_version, local_version):
                return _build_result("update_available", local_version, latest_version,
                                     f"发现新版本: {latest_version}（当前: {local_version}）")
            else:
                return _build_result("up_to_date", local_version, latest_version,
                                     f"当前已是最新版本: {local_version}")

    except Exception as e:
        return _build_result("query_failed", local_version, None, f"MCP 查询异常: {type(e).__name__}: {e}")


def _extract_version_from_response(data) -> str | None:
    """从 MCP querySkills 返回数据中提取最新版本号

    返回数据结构示例:
    {
        "code": 200,
        "data": {
            "pageNum": 1,
            "pageSize": 5,
            "total": 1,
            "data": [
                {
                    "name": "ds-mr-reviewer",
                    "latestVersion": "3.5.0",
                    ...
                }
            ]
        }
    }

    版本字段可能是 latestVersion 或 version，需灵活解析。

    Args:
        data: MCP 返回的解析后 JSON 数据

    Returns:
        版本号字符串，或 None
    """
    # 递归搜索：找到第一个包含 skill 名的 dict，提取版本
    items = _find_items_list(data)
    if not items:
        return None

    for item in items:
        if isinstance(item, dict):
            name = item.get("name", "")
            if SKILL_NAME in name or name == SKILL_NAME:
                return item.get("latestVersion") or item.get("version")

    # 若没找到精确匹配，取第一个的版本
    first = items[0]
    if isinstance(first, dict):
        return first.get("latestVersion") or first.get("version")

    return None


def _find_items_list(data, depth: int = 0) -> list | None:
    """递归搜索嵌套结构中的 skill 列表

    处理 data.data.data / result.data / 直接列表等多种嵌套方式，
    最多递归 5 层避免无限循环。

    Args:
        data: 待搜索的数据
        depth: 当前递归深度

    Returns:
        找到的列表，或 None
    """
    if depth > 5:
        return None

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        # 优先搜索包含 skill 数据的 key
        for key in ("data", "list", "items", "result"):
            val = data.get(key)
            if val is None:
                continue
            if isinstance(val, list):
                return val
            if isinstance(val, dict):
                result = _find_items_list(val, depth + 1)
                if result:
                    return result

    return None


def query_latest_version(local_version: str) -> dict:
    """查询最新版本的同步封装"""
    return asyncio.run(_query_latest_version(local_version))


# ======================== nga 安装 ========================


def find_nga() -> str | None:
    """查找 nga 可执行文件路径

    查找顺序:
        1. 当前 Python 解释器的父目录的父目录 (OCHOME)
        2. 用户主目录下 OCHOME
        3. 常见盘符 D:/C:/E: 下 OCHOME

    Returns:
        nga 可执行文件路径，或 None
    """
    python_dir = Path(sys.executable).parent
    parent_dir = python_dir.parent
    ochome_candidates = [parent_dir]

    home_dir = Path.home()
    ochome_candidates.extend([
        home_dir / "OCHOME",
        Path("D:/OCHOME"),
        Path("C:/OCHOME"),
        Path("E:/OCHOME"),
    ])

    for candidate in ochome_candidates:
        abs_dir = candidate.resolve()
        if abs_dir.exists():
            for suffix in ("", ".cmd", ".exe"):
                nga_path = abs_dir / f"nga{suffix}"
                if nga_path.exists():
                    print(f"  [OK] Found nga: {nga_path}")
                    return str(nga_path)

    print("  [INFO] nga 未安装")
    return None


def nga_global_install(item_name: str, item_type: str, version: str) -> dict:
    """自动化执行 nga add 命令，自动选择 Global 安装位置

    通过 stdin 注入模拟用户交互:
        - Version 提示 → 回车（使用默认版本）
        - Custom name 提示（仅 MCP）→ 回车（跳过）
        - Location 菜单 → ↓ 切到 Global + 回车确认
        - 是否覆盖安装 → 回车（默认 Yes）

    Args:
        item_name: 资产名称
        item_type: 资产类型 (skill/mcp/subagent/command)
        version: 版本号

    Returns:
        {"status": "success"/"failed", "item_name": ..., "item_type": ..., "version": ..., "msg": ...}
    """
    nga_path = find_nga()
    if not nga_path:
        return _build_result("failed", None, version, "nga 未安装，无法自动升级")

    full_item_name = f"/{item_name}" if item_type == "command" else item_name
    print(f"\n  [步骤] 开始全局安装: {full_item_name}@{version}...")

    def _safe_stdin_write(proc, data: bytes):
        """安全写入 stdin，Windows shell=True 下 flush 可能抛 OSError"""
        try:
            proc.stdin.write(data)
            proc.stdin.flush()
        except (OSError, BrokenPipeError, ValueError):
            pass  # 进程可能已结束或管道已关闭

    try:
        proc = subprocess.Popen(
            [nga_path, item_type, "add", f"{full_item_name}@{version}"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env={**os.environ, "FORCE_COLOR": "true"},
        )
    except Exception as e:
        return _build_result("failed", None, version, f"启动 nga 进程失败: {e}")

    # 状态标志
    step_flags = {"version": False, "name": False, "location": False, "overwrite": False}

    stdout_lines: list[str] = []
    stderr_lines: list[str] = []

    def _reader(pipe, sink: list[str]):
        try:
            for line in iter(pipe.readline, b""):
                text = line.decode("utf-8", errors="replace")
                sink.append(text)
        finally:
            pipe.close()

    stdout_thread = threading.Thread(target=_reader, args=(proc.stdout, stdout_lines), daemon=True)
    stderr_thread = threading.Thread(target=_reader, args=(proc.stderr, stderr_lines), daemon=True)
    stdout_thread.start()
    stderr_thread.start()

    # 主循环：检查输出并注入交互
    timeout = 120
    start_time = time.monotonic()

    while proc.poll() is None and (time.monotonic() - start_time) < timeout:
        combined = "".join(stdout_lines)

        # 1. Version 提示 → 回车确认
        if "Version" in combined and not step_flags["version"]:
            step_flags["version"] = True
            time.sleep(0.2)
            _safe_stdin_write(proc, ENTER)

        # 2. Custom name 提示（仅 MCP 类型）→ 回车跳过
        if item_type == "mcp" and "Custom name" in combined and not step_flags["name"]:
            step_flags["name"] = True
            time.sleep(0.2)
            _safe_stdin_write(proc, ENTER)

        # 3. Location 菜单 → ↓ 切到 Global + 回车确认
        if "Location" in combined and not step_flags["location"]:
            step_flags["location"] = True
            time.sleep(0.4)
            _safe_stdin_write(proc, DOWN_ARROW)
            time.sleep(0.2)
            _safe_stdin_write(proc, ENTER)

        # 4. 覆盖安装提示 → 回车确认（默认 Yes）
        if "是否覆盖安装" in combined and not step_flags["overwrite"]:
            step_flags["overwrite"] = True
            time.sleep(0.2)
            _safe_stdin_write(proc, ENTER)

        time.sleep(0.3)

    # 等待进程结束
    try:
        proc.stdin.close()
    except Exception:
        pass

    proc.wait(timeout=10)
    stdout_thread.join(timeout=5)
    stderr_thread.join(timeout=5)

    # 打印输出供调试（GBK 终端无法编码 Unicode 特殊字符，用 replace 处理）
    _enc = getattr(sys.stdout, 'encoding', '') or 'utf-8'
    for line in stdout_lines:
        try:
            print(f"    {line}", end="")
        except UnicodeEncodeError:
            print(f"    {line.encode(_enc, errors='replace').decode(_enc)}", end="")
    for line in stderr_lines:
        try:
            print(f"    {line}", end="", file=sys.stderr)
        except UnicodeEncodeError:
            print(f"    {line.encode(_enc, errors='replace').decode(_enc)}", end="", file=sys.stderr)

    if proc.returncode not in (0, None):
        return _build_result("failed", None, version, f"nga 进程异常退出，状态码: {proc.returncode}")

    # 验证安装结果
    verified = _verify_installation(item_name, item_type, nga_path)
    if verified:
        return _build_result("success", None, version, "升级安装成功")
    else:
        return _build_result("failed", None, version, "安装后验证未通过，请检查 nga skill list")


def _verify_installation(item_name: str, item_type: str, nga_path: str) -> bool:
    """通过 nga {type} list 验证安装结果

    Args:
        item_name: 资产名称
        item_type: 资产类型
        nga_path: nga 可执行文件路径

    Returns:
        True 表示安装成功
    """
    print(f"  [步骤] 正在验证安装结果 (nga {item_type} list)...")
    try:
        result = subprocess.run(
            [nga_path, item_type, "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            timeout=30,
        )
        output = (result.stdout or "") + (result.stderr or "")
        if item_name in output:
            print(f"  [验证成功] 列表已存在该 {item_type}: \"{item_name}\"")
            return True
        else:
            print(f"  [验证失败] 列表中未找到该 {item_type}: \"{item_name}\"")
            return False
    except Exception as e:
        print(f"  [验证异常] {e}")
        return False


# ======================== codeagent 平台安装 ========================


def codeagent_install(item_name: str, version: str) -> dict:
    """通过 codeagent CLI 安装 skill

    无需用户交互，一条命令完成：
        powershell -Command "codeagent skills add {name}@{version}"
    命令执行成功（returncode == 0）即代表安装成功。

    Args:
        item_name: 资产名称
        version: 版本号

    Returns:
        {"status": "success"/"failed"/"skipped", ...}
    """
    add_cmd = CODEAGENT_SKILLS_ADD.format(skill_name=item_name, version=version)
    print(f"\n  [步骤] codeagent 平台安装: {item_name}@{version}...")

    try:
        result = subprocess.run(
            add_cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            timeout=120,
        )
        output = (result.stdout or "") + (result.stderr or "")

        # 打印输出供调试
        for line in output.strip().split("\n"):
            try:
                print(f"    {line}")
            except UnicodeEncodeError:
                _e = getattr(sys.stdout, 'encoding', '') or 'utf-8'
                print(f"    {line.encode(_e, errors='replace').decode(_e)}")

        if result.returncode != 0:
            # 判断是否是 codeagent 未安装
            if "not recognized" in output.lower() or "无法识别" in output or "找不到" in output:
                return _build_result("skipped", None, version, "codeagent CLI 未安装，跳过 codeagent 平台安装")
            return _build_result("failed", None, version,
                                 f"codeagent skills add 退出码 {result.returncode}: {output.strip()[:200]}")

        return _build_result("success", None, version,
                             f"codeagent 平台安装成功: {item_name}@{version}")

    except subprocess.TimeoutExpired:
        return _build_result("failed", None, version, "codeagent skills add 超时")
    except FileNotFoundError:
        return _build_result("skipped", None, version, "codeagent CLI 未安装，跳过 codeagent 平台安装")
    except Exception as e:
        return _build_result("failed", None, version, f"codeagent 安装异常: {type(e).__name__}: {e}")


# ======================== 辅助函数 ========================


def _build_result(
    status: str, local_version: str | None, latest_version: str | None, msg: str
) -> dict:
    """构建统一输出 JSON"""
    return {
        "status": status,
        "local_version": local_version,
        "latest_version": latest_version,
        "msg": msg,
    }


# ======================== 主流程 ========================


def check_and_update(local_version: str) -> dict:
    """检查市场版本并自动更新

    同时通过 nga 和 codeagent 两个平台安装。

    Args:
        local_version: 本地版本号（从 SKILL.md 的 version 字段传入）

    Returns:
        结果字典，包含 status/local_version/latest_version/msg/install_results
    """
    print(f"[INFO] 当前本地版本: {local_version}")
    print("[INFO] 正在查询市场最新版本...")

    # Step 1: 查询市场最新版本
    query_result = query_latest_version(local_version)

    if query_result["status"] == "query_failed":
        print(f"[WARN] 版本查询失败: {query_result['msg']}")
        print("[INFO] 跳过自动更新，继续使用当前版本")
        return query_result

    if query_result["status"] == "up_to_date":
        print(f"[OK] {query_result['msg']}")
        return query_result

    # Step 2: 发现新版本，执行双平台安装
    latest_version = query_result["latest_version"]
    print(f"[INFO] {query_result['msg']}")
    print(f"[INFO] 开始自动升级: {local_version} → {latest_version}")

    install_results = {}

    # 2a: nga 平台安装
    print("\n[INFO] === nga 平台安装 ===")
    nga_result = nga_global_install(SKILL_NAME, SKILL_TYPE, latest_version)
    install_results["nga"] = nga_result
    if nga_result["status"] == "success":
        print(f"[OK] nga 平台升级成功: {local_version} → {latest_version}")
    else:
        print(f"[WARN] nga 平台升级失败: {nga_result['msg']}")
        print(f"[INFO] 可手动执行: nga skill add {SKILL_NAME}@{latest_version}")

    # 2b: codeagent 平台安装
    print("\n[INFO] === codeagent 平台安装 ===")
    codeagent_result = codeagent_install(SKILL_NAME, latest_version)
    install_results["codeagent"] = codeagent_result
    if codeagent_result["status"] == "success":
        print(f"[OK] codeagent 平台升级成功: {local_version} → {latest_version}")
    elif codeagent_result["status"] == "skipped":
        print(f"[INFO] codeagent 平台跳过: {codeagent_result['msg']}")
    else:
        print(f"[WARN] codeagent 平台升级失败: {codeagent_result['msg']}")
        print(f"[INFO] 可手动执行: powershell -Command \"codeagent skills add {SKILL_NAME}@{latest_version}\"")

    # 汇总结果
    any_success = any(r["status"] == "success" for r in install_results.values())
    all_skipped = all(r["status"] in ("skipped", "failed") for r in install_results.values())

    if any_success:
        final_status = "success"
        final_msg = f"升级完成: {local_version} → {latest_version}"
        print(f"\n[OK] {final_msg}")
        print("[INFO] 新版本将在下次启动时生效")
    elif all_skipped:
        final_status = "failed"
        final_msg = f"所有平台安装均失败（版本: {latest_version}）"
    else:
        final_status = "failed"
        final_msg = f"升级失败: {local_version} → {latest_version}"

    result = _build_result(final_status, local_version, latest_version, final_msg)
    result["install_results"] = install_results
    return result


def main():
    parser = argparse.ArgumentParser(description="DS MR Reviewer Skill 版本自动更新")
    parser.add_argument("--version", required=True, help="当前本地版本号（从 SKILL.md 传入）")
    args = parser.parse_args()

    result = check_and_update(args.version)

    print("\n" + "=" * 60)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    # 只要查询到新版本（无论安装是否成功），都不阻断主流程
    sys.exit(0)


if __name__ == "__main__":
    main()
