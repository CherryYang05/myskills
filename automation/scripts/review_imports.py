#!/usr/bin/env python3
"""Static import gate for registered third-party Skills.

This intentionally never executes upstream scripts. It checks reproducible,
high-confidence safety signals; a passing check is not a full security audit.
"""
import re
from pathlib import Path

from sync import ROOT, load_config
from verify import inventory

LEGAL_FILES = {"LICENSE", "LICENSE.txt", "LICENSE.md", "LICENSE.upstream.txt", "NOTICE", "NOTICE.md", "COPYING"}
CODE_SUFFIXES = {".sh", ".bash", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx"}
SEVERE = {
    "piped remote shell": re.compile(r"\b(?:curl|wget)\b[^\n]{0,180}\|\s*(?:bash|sh)\b", re.I),
    "destructive root deletion": re.compile(r"\brm\s+-[a-z]*r[a-z]*f[a-z]*\s+/(?:\s|$)", re.I | re.M),
    "encoded shell execution": re.compile(r"\b(?:base64\s+--decode|base64\s+-d)\b[^\n]{0,100}\|\s*(?:bash|sh)\b", re.I),
}


def review(root=ROOT):
    config = load_config(root)
    entries = {directory: fields["name"] for group, directory, fields in inventory(root)
               if group == "external"}
    if set(entries) != set(config):
        raise ValueError("Registered and imported Skills disagree")

    for directory, name in sorted(entries.items()):
        source = root / "skills" / "external" / directory
        files = [p for p in source.rglob("*") if p.is_file()]
        legal = [p for p in files if p.name in LEGAL_FILES]
        if config[directory].get("root_license") and not (source / "LICENSE.upstream.txt").is_file():
            raise ValueError(f"{name}: missing required upstream root license")
        # Older tracked Skills may not include an upstream legal file. Record
        # a warning, but require new imports to specify root_license in review.
        if not legal:
            print(f"WARNING {name}: no bundled license file; review upstream license")
        for file in files:
            if file.suffix.lower() not in CODE_SUFFIXES:
                continue
            # A large generated design checker is normal for Taste. The
            # aggregate import quota remains enforced by sync.py.
            if file.stat().st_size > 16 * 1024 * 1024:
                raise ValueError(f"{name}: oversized source script: {file.name}")
            code = file.read_text(encoding="utf-8", errors="replace")
            for label, pattern in SEVERE.items():
                if pattern.search(code):
                    raise ValueError(f"{name}: {label} found in {file.relative_to(source)}")
        print(f"{name}: reviewed {len(files)} untrusted files; {len(legal)} legal file(s)")
    print("Static import review passed; manual review is still required for new upstream sources.")


if __name__ == "__main__":
    review()
