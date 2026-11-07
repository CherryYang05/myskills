#!/usr/bin/env python3
"""Smoke-check that Skills CLI discovers every canonical Skill in myskills."""
import argparse
import re
import sys
from pathlib import Path

from verify import inventory

ANSI = re.compile(r"\x1b\[[0-9;]*m")


def check_cli_output(text, packages):
    text = ANSI.sub("", text)
    names = sorted({fields["name"] for _, _, fields in packages})
    missing = [
        name for name in names
        if not re.search(r"(?<![a-z0-9-])" + re.escape(name) + r"(?![a-z0-9-])", text)
    ]
    if missing:
        raise ValueError(f"Skills CLI did not discover {missing}; see CLI output")
    return len(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("cli_stdout", type=Path)
    args = parser.parse_args()
    found = check_cli_output(args.cli_stdout.read_text(encoding="utf-8"), inventory())
    print(f"Skills CLI discovery verified for all {found} canonical Skill names")


if __name__ == "__main__":
    try:
        main()
    except ValueError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
