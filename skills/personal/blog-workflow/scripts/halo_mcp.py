#!/usr/bin/env python3
"""Expose Bearguin's stateless Halo MCP to a desktop MCP client over stdio."""

import json
import re
import subprocess
import sys
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener


ENDPOINT = "https://bearguin.cn/mcp"
MAX_REPLY = 32 * 1024 * 1024


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def keychain_token():
    if sys.platform != "darwin":
        raise RuntimeError("Blog's Bearguin Halo connection requires macOS Keychain.")
    try:
        token = subprocess.check_output(
            ["/usr/bin/security", "find-generic-password", "-a", "blog",
             "-s", "bearguin-halo-mcp", "-w"],
            text=True, stderr=subprocess.DEVNULL, timeout=15,
        ).strip()
    except (OSError, subprocess.SubprocessError):
        raise RuntimeError("Could not read the bearguin-halo-mcp item from macOS Keychain.") from None
    if not re.fullmatch(r"hmcp_[A-Za-z0-9_-]+", token):
        raise RuntimeError("The bearguin-halo-mcp Keychain item is not a Halo MCP key.")
    return token


def read_reply(response, request_id):
    if response.headers.get_content_type() == "text/event-stream":
        data = []
        remaining = MAX_REPLY
        while remaining > 0:
            line = response.readline(remaining + 1)
            remaining -= len(line)
            if not line or remaining < 0:
                break
            if line.startswith(b"data:"):
                data.append(line[5:].lstrip(b" ").rstrip(b"\r\n"))
            elif not line.strip() and data:
                reply = json.loads(b"\n".join(data))
                if reply.get("id") == request_id:
                    return reply
                data.clear()
        raise ValueError("No matching Halo reply in the event stream.")

    body = response.read(MAX_REPLY + 1)
    if len(body) > MAX_REPLY:
        raise ValueError("Halo reply exceeded the size limit.")
    reply = json.loads(body)
    if reply.get("id") != request_id:
        raise ValueError("Halo returned an unexpected reply ID.")
    return reply


def serve(client, headers):
    for line in sys.stdin:
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if not isinstance(message, dict) or not isinstance(message.get("method"), str):
            continue
        request_id = message.get("id")
        has_id = "id" in message
        request = Request(ENDPOINT, data=line.encode("utf-8"), headers=headers, method="POST")
        try:
            with client.open(request, timeout=25) as response:
                if not has_id:
                    continue
                reply = read_reply(response, request_id)
                if message["method"] == "initialize" and "result" in reply:
                    headers["MCP-Protocol-Version"] = reply["result"]["protocolVersion"]
            error = None
        except HTTPError as exc:
            exc.close()
            error = f"Halo MCP returned HTTP {exc.code}."
        except (OSError, ValueError, AttributeError, KeyError):
            error = "Halo MCP request failed or returned an invalid reply."
        if has_id:
            if error:
                reply = {
                    "jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32000, "message": error},
                }
            print(json.dumps(reply, ensure_ascii=True), flush=True)
        elif error:
            print(error, file=sys.stderr, flush=True)


if __name__ == "__main__":
    try:
        authorization = "Bearer " + keychain_token()
    except RuntimeError as exc:
        sys.exit(str(exc))
    serve(build_opener(NoRedirect()), {
        "Authorization": authorization,
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    })
