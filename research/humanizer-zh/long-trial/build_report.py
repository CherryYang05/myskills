import json
import re

from audit import cases, read_case, read_edit, root, version_names


outputs = root.parents[1] / "outputs"
labels = {
    "zh1": ("中文技术复盘", "字"),
    "zh2": ("中文随笔", "字"),
    "en1": ("英文技术复盘", "词"),
    "en2": ("英文随笔", "词"),
}
key = json.loads((root / "key.json").read_text(encoding="utf-8"))
structure = json.loads((root / "structure.json").read_text(encoding="utf-8"))


def judgment_sections(language):
    source = (root / f"judgment-{language}.md").read_text(encoding="utf-8")
    chunks = re.split(r"^## ((?:zh|en)[12])\s*$", source, flags=re.M)
    return {chunks[index]: chunks[index + 1].strip() for index in range(1, len(chunks), 2)}


def display_order(groups):
    return " ＞ ".join(" ＝ ".join(version_names[version] for version in group) for group in groups)


judgments = judgment_sections("zh") | judgment_sections("en")
assert set(judgments) == set(cases)
rankings = {}
rows = ["| 样稿 | 篇幅 | 盲评排序 | 微调初稿结构检查 |", "| --- | ---: | --- | --- |"]
appendix = []
for case in cases:
    request, source = read_case(case)
    first_line, _, reasons = judgments[case].partition("\n")
    order = first_line.replace(" ", "").replace("＞", ">").replace("＝", "=")
    groups = [[key[case][label] for label in group.split("=")] for group in order.split(">")]
    assert sorted(version for group in groups for version in group) == sorted(version_names)
    rankings[case] = {version: rank for rank, group in enumerate(groups) for version in group}

    title, unit = labels[case]
    token_pattern = r"[\u4e00-\u9fff]" if case.startswith("zh") else r"\b[A-Za-z]+(?:['’][A-Za-z]+)?\b"
    count = len(re.findall(token_pattern, source))
    flags = structure[case]["final"]["structure_issues"]
    status = "、".join(flags) if flags else "通过"
    rows.append(f"| {title} | {count:,} {unit} | {display_order(groups)} | {status} |")

    appendix.extend([f"### {title}", "**改稿要求**", request, "**原稿**", f"```markdown\n{source}\n```"])
    for version, name in version_names.items():
        edit = read_edit(version, case)
        details = structure[case][version]
        unchanged = details["verbatim_paragraphs"]
        total = details["source_paragraphs"]
        appendix.extend([f"**{name}**（正文逐字保留 {unchanged}/{total} 段）", f"```markdown\n{edit}\n```"])
    resolved = re.sub(r"\b[ABCD]\b", lambda match: version_names[key[case][match[0]]], reasons.strip())
    appendix.extend(["**盲评依据**", resolved])

pairs = ["| 微调初稿对照对象 | 中文胜／平／负 | 英文胜／平／负 |", "| --- | ---: | ---: |"]
for version in ("upstream", "previous", "plain"):
    counts = []
    for language in ("zh", "en"):
        differences = [ranks["final"] - ranks[version] for case, ranks in rankings.items() if case.startswith(language)]
        counts.append("／".join(str(sum(comparison for comparison in check)) for check in (
            [difference < 0 for difference in differences],
            [difference == 0 for difference in differences],
            [difference > 0 for difference in differences],
        )))
    pairs.append(f"| {version_names[version]} | {counts[0]} | {counts[1]} |")

template = (root / "report-template.md").read_text(encoding="utf-8")
summary = (root / "assessment.md").read_text(encoding="utf-8").strip()
holdout = (root / "holdout-assessment.md").read_text(encoding="utf-8").strip()
replacements = {"CASE_TABLE": "\n".join(rows), "PAIR_TABLE": "\n".join(pairs), "ASSESSMENT": summary, "HOLDOUT": holdout, "SAMPLES": "\n\n".join(appendix)}
for token, text in replacements.items():
    template = template.replace("{{" + token + "}}", text)
assert "{{" not in template
(outputs / "humanizer-long-comparison.md").write_text(template, encoding="utf-8")
print("\n".join(rows + [""] + pairs))
