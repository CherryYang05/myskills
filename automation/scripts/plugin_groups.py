"""Map canonical Skill directories to explicitly reviewed plugin bundles."""
import json
import re
from urllib.parse import urlsplit

from sync import ROOT
from verify import inventory

CONFIG = "automation/plugin-groups.json"
NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SOURCE = re.compile(r"(?:external|personal)/[a-z0-9]+(?:-[a-z0-9]+)*\Z")


def parse_groups(data):
    if (not isinstance(data, dict) or set(data) != {"schemaVersion", "plugins"}
            or type(data["schemaVersion"]) is not int or data["schemaVersion"] != 1
            or not isinstance(data["plugins"], dict)):
        raise ValueError("Plugin groups must define schemaVersion 1 and plugins")
    assigned = set()
    for name, group in data["plugins"].items():
        if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64:
            raise ValueError(f"Invalid plugin group name: {name!r}")
        if not isinstance(group, dict) or set(group) != {"displayName", "description", "homepage", "skills"}:
            raise ValueError(f"{name}: expected displayName, description, homepage and skills")
        for field, limit in (("displayName", 64), ("description", 1024)):
            value = group[field]
            if not isinstance(value, str) or not value.strip() or len(value) > limit:
                raise ValueError(f"{name}: invalid {field}")
        homepage = group["homepage"]
        url = urlsplit(homepage) if isinstance(homepage, str) else None
        if not url or url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError(f"{name}: homepage must be an HTTPS URL without credentials")
        members = group["skills"]
        if not isinstance(members, list) or len(members) < 2:
            raise ValueError(f"{name}: a plugin group needs at least two Skills")
        for member in members:
            if not isinstance(member, str) or not SOURCE.fullmatch(member):
                raise ValueError(f"{name}: invalid canonical Skill path: {member!r}")
            if member in assigned:
                raise ValueError(f"Skill belongs to multiple plugin groups: {member}")
            assigned.add(member)
    return data["plugins"]


def load_groups(root=ROOT):
    path = root / CONFIG
    return parse_groups(json.loads(path.read_text(encoding="utf-8"))) if path.exists() else {}


def plugin_inventory(root=ROOT, packages=None):
    """Keep individual Skills intact while selecting one installable package each."""
    packages = inventory(root) if packages is None else packages
    sources = {f"{group}/{directory}": (group, directory, fields)
               for group, directory, fields in packages}
    groups = load_groups(root)
    skill_names = {fields["name"] for _, _, fields in packages}
    membership = {}
    for name, group in groups.items():
        if name in skill_names:
            raise ValueError(f"Plugin group conflicts with an existing Skill name: {name}")
        for member in group["skills"]:
            if member not in sources:
                raise ValueError(f"{name}: unknown canonical Skill: {member}")
            membership[member] = name
    plugins = []
    emitted = set()
    for category, directory, fields in packages:
        source = f"{category}/{directory}"
        name = membership.get(source, fields["name"])
        if name in emitted:
            continue
        emitted.add(name)
        if source in membership:
            group = groups[name]
            plugins.append({"name": name, **group,
                            "skills": [sources[member] for member in group["skills"]]})
        else:
            plugins.append({
                "name": name, "displayName": name, "description": fields["description"],
                "homepage": f"https://github.com/CherryYang05/myskills/tree/master/skills/{source}",
                "skills": [(category, directory, fields)],
            })
    return plugins
