"""Keep a repository-owned, append-only revision log for each Skill."""
import argparse
from datetime import date
from pathlib import Path
import re
import subprocess


CHANGELOGS = Path("skill-changelogs")
ENTRY = re.compile(r"- (\d{4}-\d{2}-\d{2}) — (\S.*)")


def record_path(group, directory):
    return CHANGELOGS / group / f"{directory}.md"


def validate(root, packages, base=None):
    active = {record_path(group, directory) for group, directory, _ in packages}
    affected = set()
    edited = set()
    if base:
        subprocess.run(["git", "rev-parse", "--verify", f"{base}^{{commit}}"],
                       cwd=root, check=True, capture_output=True)
        changed = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-only", "-z", base, "--",
             "skills/personal", "skills/external", str(CHANGELOGS)], cwd=root
        ).decode().split("\0")
        for name in filter(None, changed):
            parts = Path(name).parts
            if parts[0] == "skills" and len(parts) >= 4:
                affected.add(record_path(parts[1], parts[2]))
            elif parts[0] == str(CHANGELOGS) and len(parts) == 3:
                edited.add(Path(name))

    for path in sorted(active | affected | edited):
        file = root / path
        if not file.is_file() or file.is_symlink():
            raise ValueError(f"Missing Skill revision log: {path}")
        content = file.read_text(encoding="utf-8")
        lines = content.splitlines()
        if len(lines) < 3 or not lines[0].startswith("# ") or lines[1] or not content.endswith("\n"):
            raise ValueError(f"Expected a heading and dated entries in {path}")
        for line in lines[2:]:
            match = ENTRY.fullmatch(line)
            if not match:
                raise ValueError(f"Invalid revision entry in {path}; use '- YYYY-MM-DD — summary'")
            date.fromisoformat(match[1])

        if base and path in (affected | edited):
            previous = subprocess.run(["git", "show", f"{base}:{path.as_posix()}"],
                                      cwd=root, capture_output=True, text=True)
            if previous.returncode == 0:
                if not content.startswith(previous.stdout):
                    raise ValueError(f"Keep prior revision entries intact in {path}")
                if path in affected and content == previous.stdout:
                    raise ValueError(f"Skill changed; append a revision entry to {path}")
    return len(active)


def main():
    from verify import ROOT, inventory

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git commit to compare with the checkout")
    args = parser.parse_args()
    try:
        count = validate(ROOT, inventory(), args.base)
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")
    print(f"Validated revision logs for {count} Skills.")


if __name__ == "__main__":
    main()
