import difflib
import json
import random
import re
from pathlib import Path


root = Path(__file__).resolve().parent
cases = ("zh1", "zh2", "en1", "en2")
version_names = {
    "plain": "仅用改稿要求",
    "upstream": "上游 Humanizer",
    "previous": "上一版",
    "final": "微调初稿",
}


def read_case(case):
    fixture = (root / "cases" / f"{case}.md").read_text(encoding="utf-8")
    request, source = fixture.split("\n# Source\n", 1)
    return request.removeprefix("# Request").strip(), source.strip()


def read_edit(version, case):
    return (root / version / f"{case}.md").read_text(encoding="utf-8").strip()


def paragraphs(source):
    return [part for part in source.split("\n\n") if part and not part.startswith(("#", "|"))]


def protected(source):
    return {
        "标题": re.findall(r"^#+ .+$", source, flags=re.M),
        "表格": re.findall(r"^\|.+\|$", source, flags=re.M),
        "链接目标": re.findall(r"\]\(([^)]+)\)", source),
        "行内命令": re.findall(r"`[^`\n]+`", source),
        "引文": [quote for quote in re.findall(r"“[^”]+”", source) if quote != "“任务完成”"],
    }


def check_structure(case, source, edit):
    original_protected, edited_protected = protected(source), protected(edit)
    issues = [key for key in original_protected if original_protected[key] != edited_protected[key]]
    original_paragraphs, edited_paragraphs = paragraphs(source), paragraphs(edit)
    if case.endswith("2") and len(original_paragraphs) != len(edited_paragraphs):
        issues.append("随笔段落数")
    shared = difflib.SequenceMatcher(a=original_paragraphs, b=edited_paragraphs, autojunk=False)
    unchanged = sum(block.size for block in shared.get_matching_blocks())
    return {"structure_issues": issues, "verbatim_paragraphs": unchanged, "source_paragraphs": len(original_paragraphs)}


def make_blind_inputs():
    rng = random.Random(1839)
    key = {}
    audit = {}
    for language in ("zh", "en"):
        parts = ["# Anonymous long-form editorial comparison"]
        for case in (item for item in cases if item.startswith(language)):
            request, source = read_case(case)
            order = list(version_names)
            rng.shuffle(order)
            key[case] = dict(zip("ABCD", order))
            audit[case] = {}
            parts.extend([f"## Case {case}", "### Request", request, "### Source", source])
            for label, version in key[case].items():
                edit = read_edit(version, case)
                parts.extend([f"### Candidate {label}", edit])
                audit[case][version] = check_structure(case, source, edit)
        (root / f"anonymous-{language}.md").write_text("\n\n".join(parts) + "\n", encoding="utf-8")
    (root / "key.json").write_text(json.dumps(key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (root / "structure.json").write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    make_blind_inputs()
