import json
import re
from pathlib import Path


trial = Path(__file__).resolve().parent
outputs = trial.parents[1] / "outputs"


def passages(name):
    content = (trial / f"{name}.md").read_text(encoding="utf-8")
    sections = re.split(r"^## ([ZE][1-6])\s*$", content, flags=re.M)
    return {sections[i]: sections[i + 1].strip() for i in range(1, len(sections), 2)}


case_inputs = passages("cases")
versions = {
    "legacy": "上一版",
    "upstream-zh": "原版 humanizer-zh",
    "upstream-en": "原版 humanizer",
    "revised": "新版",
}
trial_edits = {version: passages(version) for version in versions}
key = json.loads((trial / "blind-key.json").read_text(encoding="utf-8"))
judgments = passages("blind-judgment")
assert list(case_inputs) == list(judgments) == list(key)
assert sum(len(items) for items in trial_edits.values()) == 35

ranks = {}
case_results = {}
for case in case_inputs:
    label_order = judgments[case].splitlines()[0]
    tie_groups = [[key[case][label] for label in group.split("=")] for group in label_order.replace(" ", "").split(">")]
    assert {version for group in tie_groups for version in group} == set(key[case].values())
    ranks[case] = {version: rank for rank, group in enumerate(tie_groups) for version in group}
    case_results[case] = " ＞ ".join(" ＝ ".join(versions[version] for version in group) for group in tie_groups)

comparisons = [
    ("中文", "legacy", "upstream-zh"),
    ("中文", "revised", "upstream-zh"),
    ("中文", "revised", "legacy"),
    ("英文", "legacy", "upstream-en"),
    ("英文", "revised", "upstream-en"),
    ("英文", "revised", "legacy"),
]
rows = ["| 样稿 | 左侧版本 | 右侧版本 | 左侧胜／平／负 |", "| --- | --- | --- | --- |"]
for language, left, right in comparisons:
    prefix = "Z" if language == "中文" else "E"
    differences = [rank[left] - rank[right] for case, rank in ranks.items() if case.startswith(prefix)]
    assert len(differences) == 5
    tally = "／".join(str(sum(predicate(diff) for diff in differences)) for predicate in (lambda d: d < 0, lambda d: d == 0, lambda d: d > 0))
    rows.append(f"| {language} | {versions[left]} | {versions[right]} | {tally} |")

case_sections = []
for case, request in case_inputs.items():
    case_sections.extend([f"### {case}", "**任务与原文**", request])
    for version, title in versions.items():
        if case in trial_edits[version]:
            case_sections.extend([f"**{title}**", trial_edits[version][case]])
    case_sections.append(f"**盲评排序**　{case_results[case]}")

retest = passages("notices-final")
holdouts = passages("notice-holdout")
assert list(retest) == ["Z2", "E2", "Z6", "E6"]
notice_sections = []
for case, final_edit in retest.items():
    notice_sections.append(f"**{case} 最终稿**")
    if case in holdouts:
        notice_sections.extend(["试改输入", holdouts[case]])
    notice_sections.append(final_edit)

template = (trial / "report-intro.md").read_text(encoding="utf-8")
report = template.replace("{{PAIRWISE}}", "\n".join(rows))
report = report.replace("{{ALL_CASES}}", "\n\n".join(case_sections))
report = report.replace("{{NOTICES}}", "\n\n".join(notice_sections))
assert "{{" not in report
(outputs / "humanizer-comparison.md").write_text(report, encoding="utf-8")
print("Comparison includes 10 original inputs, 35 first-pass edits, and 4 notice retests.")
print("\n".join(rows))
