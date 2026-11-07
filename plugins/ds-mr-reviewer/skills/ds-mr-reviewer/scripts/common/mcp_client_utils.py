#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP 客户端工具库

提供认证、网络层、MCP 客户端创建与工具调用等基础设施，
供 mr-status-analyzer 下各脚本复用。

用法:
    from mcp_client_utils import get_auth_token, build_mcp_headers, create_mcp_client, call_mcp_tool, call_mcp_tool_with_retry

依赖:
    pip install httpx fastmcp
    Windows 环境还需 pywin32 (用于 DPAPI 解密 auth token)
"""

import asyncio
import base64
import json
import platform
import sys
import time
from pathlib import Path


# ======================== 依赖检查 ========================


def _check_dependencies() -> None:
    """运行前检查必要依赖是否已安装及版本是否满足要求

    在模块首次导入时自动调用。缺失依赖时打印安装指引并退出，
    版本不满足时打印警告但不阻止运行。
    """
    import importlib.metadata

    REQUIRED = {
        "httpx": ("0.27", "pip install httpx>=0.27"),
        "fastmcp": ("2.0", "pip install fastmcp>=2.0"),
    }
    PLATFORM_REQUIRED = {
        "win32": {"pywin32": ("306", "pip install pywin32>=306")},
    }

    errors: list[str] = []
    warnings: list[str] = []

    # 检查 Python 版本
    if sys.version_info < (3, 10):
        errors.append(
            f"Python 版本不满足: 当前 {sys.version_info.major}.{sys.version_info.minor}，要求 >= 3.10"
        )

    # 检查通用依赖
    for pkg, (min_ver, install_hint) in REQUIRED.items():
        try:
            version = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"缺少依赖: {pkg}（{install_hint}）")
            continue
        # 简单版本比较：取主版本号部分
        try:
            installed_parts = [int(x) for x in version.split(".")[:2]]
            required_parts = [int(x) for x in min_ver.split(".")[:2]]
            if installed_parts < required_parts:
                warnings.append(
                    f"依赖版本偏低: {pkg} 当前 {version}，建议 >= {min_ver}"
                )
        except (ValueError, IndexError):
            warnings.append(f"依赖版本无法解析: {pkg}={version}，建议 >= {min_ver}")

    # 检查平台特定依赖
    platform_deps = PLATFORM_REQUIRED.get(sys.platform, {})
    for pkg, (min_ver, install_hint) in platform_deps.items():
        try:
            version = importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError:
            errors.append(f"缺少依赖: {pkg}（{install_hint}，Windows 必需）")
            continue
        try:
            installed_parts = [int(x) for x in version.split(".")[:2]]
            required_parts = [int(x) for x in min_ver.split(".")[:2]]
            if installed_parts < required_parts:
                warnings.append(
                    f"依赖版本偏低: {pkg} 当前 {version}，建议 >= {min_ver}"
                )
        except (ValueError, IndexError):
            warnings.append(f"依赖版本无法解析: {pkg}={version}，建议 >= {min_ver}")

    if warnings:
        for w in warnings:
            print(f"  [依赖警告] {w}")
    if errors:
        print("\n❌ 环境依赖检查失败：")
        for e in errors:
            print(f"  - {e}")
        print("\n安装所有依赖: pip install -r scripts/requirements.txt")
        sys.exit(1)


# 模块导入时自动检查
_check_dependencies()


import httpx
from fastmcp import Client
from fastmcp.client import StreamableHttpTransport


# ======================== 配置 ========================

# MCP Server URLs
CI_GATE_MCP_URL = "http://tianzhou-gamma.huawei.com/ci-gate-mcp/mcp"
CLOUD_PIPELINE2_MCP_URL = (
    "http://mcpgateway.his.huawei.com/mcp/69de02f93ac5640c0f61a91f/2004014288555036674"
)
BUILD_PROJECT_MCP_URL = (
    "http://mcpgateway.his.huawei.com/mcp/69dcd8343ac5640c0f61a8ed/2004014288555036674"
)
CODEHUB_MCP_URL = (
    "http://mcpgateway.his.huawei.com/mcp/69dce0c73ac5640c0f61a8f0/1"
)
CODEDETECTION_MCP_URL = (
    "http://tianzhou.huawei.com/panlong/api/code_detection/mcp"
)

# 认证文件
AUTH_FILE = Path("~/.local/share/opencode/auth.json").expanduser()
CAC_CREDENTIALS_FILE = Path("~/.cac/.credentials.json").expanduser()

# 重试默认配置
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_INTERVAL = 3  # 秒


# ======================== MR URL 解析 ========================


def parse_mr_url(merge_request_url: str) -> dict[str, str]:
    """从 MR URL 中提取 codehub_host / project_id / merge_request_iid

    Args:
        merge_request_url: MR 链接，如
            https://codehub-g.huawei.com/tianzhou/development/code-detection/cds-backend/merge_requests/2

    Returns:
        {"codehub_host": "codehub-g.huawei.com",
         "project_id": "tianzhou/development/code-detection/cds-backend",
         "merge_request_iid": "2"}
    """
    repo_path = merge_request_url.split("/merge_requests")[0].split(".com/")[1]
    mr_iid = merge_request_url.split("/")[-1]
    codehub_host = merge_request_url.split("://")[1].split("/")[0]

    return {
        "codehub_host": codehub_host,
        "project_id": repo_path,
        "merge_request_iid": mr_iid,
    }


# ======================== 认证 ========================


def _is_expired(expires_at_ms: int | float) -> bool:
    """检查毫秒级时间戳是否已过期"""
    return time.time() * 1000 > expires_at_ms


def _try_read_cac_credentials() -> str | None:
    """尝试从 ~/.cac/.credentials.json 读取 token

    支持两种凭据结构（按优先级尝试）:
        1. idaasOAuth.xAuthToken — 新格式，Windows DPAPI 加密 / Linux 明文
           过期: idaasOAuth.xAuthExpires 或 idaasOAuth.expiresAt
        2. devUCOAuth.accessToken — 旧格式，Windows DPAPI 加密
           过期: devUCOAuth.expiresAt

    Returns:
        解密后的 token 字符串，或 None（文件不存在/读取失败/已过期）
    """
    try:
        with open(CAC_CREDENTIALS_FILE, "r", encoding="utf-8") as f:
            cac_data = json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"  [认证] {CAC_CREDENTIALS_FILE} 格式错误，降级到 auth.json: {e}")
        return None

    # 路径1: idaasOAuth.xAuthToken（新格式，Windows DPAPI 加密 / Linux 明文）
    try:
        idaas = cac_data["idaasOAuth"]
        raw_token = idaas["xAuthToken"]
        if raw_token and isinstance(raw_token, str) and len(raw_token) > 10:
            # 检查过期时间
            expires_at = idaas.get("xAuthExpires") or idaas.get("expiresAt")
            if expires_at and _is_expired(expires_at):
                print(f"  [认证] {CAC_CREDENTIALS_FILE} idaasOAuth token 已过期，降级到 auth.json")
                return None

            # Windows: xAuthToken 是 DPAPI 加密，需要解密
            if platform.system() == "Windows":
                try:
                    encrypted_bytes = base64.b64decode(raw_token)
                    import win32crypt
                    _, decrypted = win32crypt.CryptUnprotectData(
                        encrypted_bytes, None, None, None, 0
                    )
                    token_value = decrypted.decode("utf-8")
                except Exception as e:
                    # 解密失败，可能是明文 token，直接使用
                    token_value = raw_token
                    print(f"  [认证] {CAC_CREDENTIALS_FILE} idaasOAuth.xAuthToken DPAPI 解密失败，尝试明文: {e}")
            else:
                token_value = raw_token

            print(f"  [认证] {CAC_CREDENTIALS_FILE} 使用 idaasOAuth.xAuthToken")
            return token_value
    except (KeyError, TypeError):
        pass  # 无 idaasOAuth，尝试下一条路径

    # 路径2: devUCOAuth.accessToken（旧格式，DPAPI 加密）
    try:
        token_value = cac_data["devUCOAuth"]["accessToken"]
    except KeyError:
        print(f"  [认证] {CAC_CREDENTIALS_FILE} 缺少可用凭据字段 (idaasOAuth.xAuthToken / devUCOAuth.accessToken)，降级到 auth.json")
        return None

    # 检查 expiresAt 过期时间
    try:
        expires_at = cac_data["devUCOAuth"]["expiresAt"]
        if _is_expired(expires_at):
            print(f"  [认证] {CAC_CREDENTIALS_FILE} token 已过期，降级到 auth.json")
            return None
    except (KeyError, TypeError):
        pass  # 无过期字段，假设有效，继续使用

    if platform.system() == "Windows":
        try:
            encrypted_bytes = base64.b64decode(token_value)
        except Exception as e:
            print(f"  [认证] {CAC_CREDENTIALS_FILE} Base64 解码失败，降级到 auth.json: {e}")
            return None

        try:
            import win32crypt
            _, decrypted = win32crypt.CryptUnprotectData(
                encrypted_bytes, None, None, None, 0
            )
            return decrypted.decode("utf-8")
        except Exception as e:
            print(f"  [认证] {CAC_CREDENTIALS_FILE} DPAPI 解密失败，降级到 auth.json: {e}")
            return None
    else:
        # Linux: accessToken 为明文 token
        return token_value


def _try_read_auth_json() -> str:
    """从 ~/.local/share/opencode/auth.json 读取 token（原逻辑）

    路径: w3.access
    过期: w3.expires (毫秒级时间戳)
    Windows: DPAPI 解密
    Linux: 明文直接读取

    Raises:
        FileNotFoundError: auth.json 不存在
        ValueError: 格式错误或解密失败
    """
    try:
        with open(AUTH_FILE, "r", encoding="utf-8") as f:
            auth_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"认证文件不存在: {AUTH_FILE}\n"
            "请确认 opencode 已登录（w3 login）"
        )
    except json.JSONDecodeError as e:
        raise ValueError(
            f"认证文件格式错误: {AUTH_FILE}\n"
            f"JSON 解析失败: {e}"
        )

    try:
        token_value = auth_data["w3"]["access"]
    except KeyError:
        raise ValueError(
            f"认证文件缺少必要字段: {AUTH_FILE}\n"
            "期望路径: auth_data['w3']['access']，请确认登录状态"
        )

    # 检查 expires 过期时间
    try:
        expires_at = auth_data["w3"]["expires"]
        if _is_expired(expires_at):
            print(f"  [认证] {AUTH_FILE} token 已过期，请重新登录 (w3 login)")
    except (KeyError, TypeError):
        pass  # 无过期字段，假设有效

    if platform.system() == "Windows":
        try:
            encrypted_bytes = base64.b64decode(token_value)
        except Exception as e:
            raise ValueError(
                f"Base64 解码失败，认证数据可能已损坏: {e}"
            )

        try:
            import win32crypt
            _, decrypted = win32crypt.CryptUnprotectData(
                encrypted_bytes, None, None, None, 0
            )
            return decrypted.decode("utf-8")
        except Exception as e:
            raise ValueError(
                f"DPAPI 解密失败，认证数据可能已损坏或用户上下文变更: {e}"
            )
    else:
        # Linux: w3.access 为明文 token
        return token_value


def get_auth_token() -> str:
    """从凭据文件读取 W3 access token

    优先级:
        1. ~/.cac/.credentials.json → devUCOAuth.accessToken
           - 过期检查: devUCOAuth.expiresAt (毫秒级时间戳)
           - Windows: DPAPI 解密
           - Linux: 明文直接读取
           - 读取失败或已过期时降级到 auth.json
        2. ~/.local/share/opencode/auth.json → w3.access
           - 过期检查: w3.expires (毫秒级时间戳)
           - Windows: DPAPI 解密
           - Linux: 明文直接读取
           - 已过期时打印警告但仍返回 token（让服务端做最终判定）

    Raises:
        FileNotFoundError: 所有凭据文件均不可用
        ValueError: 所有凭据文件格式错误或解密失败
    """
    # 优先级 1: .cac/.credentials.json
    token = _try_read_cac_credentials()
    if token is not None:
        return token

    # 优先级 2: auth.json（原逻辑）
    return _try_read_auth_json()


# ======================== 网络层 ========================


def create_direct_http_client(**kwargs) -> httpx.AsyncClient:
    """创建直连内网的 httpx AsyncClient（绕过系统代理）

    Windows 系统代理 proxy.huawei.com:8080 对内网请求返回 504,
    必须使用 AsyncHTTPTransport(proxy=None) 显式绕过。

    fastmcp 会传入 follow_redirects 等额外参数，用 **kwargs 接收。
    """
    # 强制使用无代理的 transport，覆盖可能传入的 transport
    kwargs["transport"] = httpx.AsyncHTTPTransport(proxy=None)
    kwargs.setdefault("timeout", httpx.Timeout(60.0, read=120.0))
    return httpx.AsyncClient(**kwargs)


# ======================== MCP 客户端 ========================


def build_mcp_headers(token: str) -> dict[str, str]:
    """构建 MCP 请求头（ci-gate-mcp / cloud-pipeline2-mcp / build-project-mcp 通用）"""
    return {
        "x-auth-group-id": "",
        "x-auth-user-name": "",
        "x-auth-token": token,
    }


def create_mcp_client(url: str, headers: dict[str, str]) -> Client:
    """创建 FastMCP Client（Streamable HTTP，直连内网）"""
    transport = StreamableHttpTransport(
        url=url,
        headers=headers,
        httpx_client_factory=create_direct_http_client,
    )
    return Client(transport)


async def call_mcp_tool(client: Client, tool_name: str, arguments: dict) -> dict | None:
    """调用 MCP 工具并返回解析后的 JSON 结果

    Returns:
        解析后的 dict，或 None（调用失败 / 非 JSON 响应）
        当接口返回多行JSON（多个TextContent）时，返回解析后的列表
    """
    try:
        result = await client.call_tool(tool_name, arguments)
    except Exception as e:
        print(f"  [MCP 调用异常] {tool_name}: {type(e).__name__}: {e}")
        return None

    all_items = []
    for content in result.content:
        text = getattr(content, "text", None)
        if text is not None:
            try:
                all_items.append(json.loads(text))
            except json.JSONDecodeError:
                # 尝试多行JSON格式（每行一个JSON对象）
                lines = text.strip().split('\n')
                if len(lines) > 1:
                    for line in lines:
                        if line.strip():
                            try:
                                all_items.append(json.loads(line))
                            except json.JSONDecodeError:
                                pass
                else:
                    print(f"  [MCP 响应解析失败] {tool_name}: 返回非 JSON 内容 (前100字符: {text[:100]})")

    if not all_items:
        print(f"  [MCP 响应为空] {tool_name}: 无有效 JSON 内容")
        return None

    # 如果只有一个元素，返回单个对象（保持向后兼容）
    if len(all_items) == 1:
        return all_items[0]

    # 多个元素时，返回列表
    return all_items


async def call_mcp_tool_with_retry(
    client: Client,
    tool_name: str,
    arguments: dict,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_interval: float = DEFAULT_RETRY_INTERVAL,
) -> dict | None:
    """带重试的 MCP 工具调用

    Args:
        max_retries: 最大重试次数，默认 3
        retry_interval: 重试间隔秒数，默认 3
    """
    for attempt in range(1, max_retries + 1):
        try:
            result = await call_mcp_tool(client, tool_name, arguments)
            if result is not None:
                return result
        except Exception as e:
            print(f"  [重试 {attempt}/{max_retries}] {tool_name} 调用异常: {e}")

        if attempt < max_retries:
            await asyncio.sleep(retry_interval)

    return None
