#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MR URL Parser

Usage:
    python mr_parse.py --mrUrl <MR_URL>

This script parses MR URL and extracts repository name (full path), MR ID and domain.

    Example MR URL:
        https://open.codehub.huawei.com/NCE-T/TxL0L1ServiceV3/merge_requests/15217
        https://codehub-y.huawei.com/NCE-T/TxL0L1ServiceV3/merge_requests/15217
        https://codehub-y.huawei.com/NCE-TCMC/AIAssets/AICommonAssets/merge_requests/19
        https://cr-y.codehub.huawei.com/CBG_CR/huawei/hap/HMOS_base_OH/ParentControl/-/change_requests/19181
    """

import argparse
import re
import json
import sys
import os
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'common'))


class MRUrlParser:
    """解析MR URL获取代码仓和MR ID信息"""

    def __init__(self, mrUrl):
        self.mrUrl = mrUrl
        self.parsedUrl = urlparse(mrUrl)
        self.repositoryName = None
        self.mrId = None
        self.domain = None

    def parse(self):
        """解析MR URL，提取代码仓名称、MR ID 和域名"""
        path = self.parsedUrl.path
        self.domain = self.parsedUrl.netloc

        patterns = [
            r'^/(.+)/merge_requests/(\d+)/?.*$',
            r'^/(.+)/pull/(\d+)/?.*$',
            r'^/(.+)/-/change_requests/(\d+)/?.*$',
        ]

        for pattern in patterns:
            match = re.match(pattern, path)
            if match:
                self.repositoryName = match.group(1)
                self.mrId = match.group(2)
                return True

        return False

    def to_dict(self):
        """返回解析结果的字典"""
        return {
            "repository_name": self.repositoryName,
            "mr_id": self.mrId,
            "mr_url": self.mrUrl,
            "domain": self.domain
        }

    def to_json(self):
        """返回解析结果的JSON字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description='MR URL Parser - Parse MR URL and extract repository name and MR ID')
    parser.add_argument('--mrUrl', required=True, help='MR URL (CodeHub/GitLab/GitHub), supports: merge_requests, pull, change_requests')

    args = parser.parse_args()

    mrParser = MRUrlParser(args.mrUrl)

    if not mrParser.parse():
        print(json.dumps({
            "error": f"无法解析MR URL: {args.mrUrl}",
            "expected_format": "https://open.codehub.huawei.com/group/project/merge_requests/123 OR https://codehub-y.huawei.com/group/project/merge_requests/123 OR https://cr-y.codehub.huawei.com/org/repo/-/change_requests/456"
        }, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)

    print(mrParser.to_json())


if __name__ == '__main__':
    main()