import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def package_skill(outputs, name):
    skill = outputs / name
    entrypoint = (skill / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = re.fullmatch(r"---\n(.*?)\n---\n(.*)", entrypoint, re.S).groups()
    name_line, description_line = frontmatter.splitlines()
    assert re.fullmatch(r"name: ([a-z0-9]+(?:-[a-z0-9]+)*)", name_line)[1] == name
    assert len(name) <= 64
    description = re.fullmatch(r"description: ([^:#<>]+)", description_line)[1]
    assert 0 < len(description) <= 1024 and "TODO" not in body

    targets = re.findall(r"\]\((references/[^)]+)\)", body)
    assert targets == ["references/examples.md"]
    assert all((skill / target).is_file() for target in targets)

    interface = (skill / "agents/openai.yaml").read_text(encoding="utf-8").splitlines()
    assert interface[0] == "interface:"
    fields = {}
    for line in interface[1:]:
        key, literal = re.fullmatch(r'  ([a-z_]+): (".+")', line).groups()
        assert key not in fields
        fields[key] = json.loads(literal)
    assert set(fields) == {"display_name", "short_description", "default_prompt"}
    assert 25 <= len(fields["short_description"]) <= 64
    assert f"${name}" in fields["default_prompt"]

    files = sorted(path for path in skill.rglob("*") if path.is_file())
    expected = {"SKILL.md", "agents/openai.yaml", "references/examples.md"}
    assert {path.relative_to(skill).as_posix() for path in files} == expected
    archive_path = outputs / f"{name}.zip"
    with ZipFile(archive_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, arcname=path.relative_to(outputs).as_posix())
    with ZipFile(archive_path) as archive:
        assert archive.testzip() is None
        for path in files:
            assert archive.read(path.relative_to(outputs).as_posix()) == path.read_bytes()
    print(f"{archive_path.name}: validated skill metadata, local reference, and {len(files)} archived files")


if __name__ == "__main__":
    outputs = Path(__file__).resolve().parents[2] / "outputs"
    for name in ("humanizer-edit-zh", "humanizer-edit-en"):
        package_skill(outputs, name)
