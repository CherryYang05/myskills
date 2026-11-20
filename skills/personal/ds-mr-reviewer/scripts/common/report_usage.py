"""运维数据上报脚本 - 表1(调用统计) + 表2(场景统计)"""
import sys
import json
import os
import urllib.request

BASE_URL = "https://tianzhou.huawei.com/panlong/api/code_detection"


def report_access(type_, skill_name):
    """表1：调用统计"""
    data = json.dumps({
        "type": type_,
        "account": os.environ.get("USERNAME", ""),
        "skillName": skill_name
    }).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/skill-access/record",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def report_scenario(payload):
    """表2：场景统计"""
    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{BASE_URL}/scenario-usage/record",
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  report_usage.py access <TYPE> <SKILL_NAME>")
        print("  report_usage.py scenario '<JSON_PAYLOAD>'")
        sys.exit(1)

    mode = sys.argv[1]

    if mode == "access":
        if len(sys.argv) < 4:
            print("Usage: report_usage.py access <TYPE> <SKILL_NAME>")
            sys.exit(1)
        report_access(sys.argv[2], sys.argv[3])

    elif mode == "scenario":
        if len(sys.argv) < 3:
            print("Usage: report_usage.py scenario '<JSON_PAYLOAD>'")
            sys.exit(1)
        payload = json.loads(sys.argv[2])
        report_scenario(payload)
