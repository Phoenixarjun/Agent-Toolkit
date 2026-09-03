from pathlib import Path
import re
import sys
import tomllib
import yaml

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

errors = []


def fail(message):
    errors.append(message)


def load_yaml(path):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def parse_frontmatter(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        fail(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return None, text
    end = text.find("\n---\n", 4)
    if end == -1:
        fail(f"{path.relative_to(ROOT)}: unterminated YAML frontmatter")
        return None, text
    raw = text[4:end]
    try:
        data = yaml.safe_load(raw)
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)}: invalid frontmatter YAML: {exc}")
        return None, text
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)}: frontmatter must be a mapping")
        return None, text
    return data, text


def validate_skill(path):
    data, text = parse_frontmatter(path)
    if data is None:
        return
    name = data.get("name")
    description = data.get("description")
    compatibility = data.get("compatibility")
    metadata = data.get("metadata")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        fail(f"{path.relative_to(ROOT)}: invalid skill name")
    elif path.parent.name != name:
        fail(f"{path.relative_to(ROOT)}: skill name must match parent directory")
    if not isinstance(description, str) or not description.strip() or len(description) > 1024:
        fail(f"{path.relative_to(ROOT)}: invalid skill description")
    if compatibility is not None and (not isinstance(compatibility, str) or not compatibility.strip() or len(compatibility) > 500):
        fail(f"{path.relative_to(ROOT)}: invalid compatibility field")
    if metadata is not None:
        if not isinstance(metadata, dict):
            fail(f"{path.relative_to(ROOT)}: metadata must be a mapping")
        else:
            for key, value in metadata.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    fail(f"{path.relative_to(ROOT)}: metadata keys and values must be strings")
    line_count = len(text.splitlines())
    if line_count > 500:
        fail(f"{path.relative_to(ROOT)}: {line_count} lines exceeds the 500-line skill limit")


def validate_toml_files():
    for path in ROOT.rglob("*.toml"):
        try:
            with path.open("rb") as handle:
                tomllib.load(handle)
        except Exception as exc:
            fail(f"{path.relative_to(ROOT)}: invalid TOML: {exc}")


def validate_yaml_files():
    for path in ROOT.rglob("*.yaml"):
        if ".git" not in path.parts:
            load_yaml(path)
    for path in ROOT.rglob("*.yml"):
        if ".git" not in path.parts:
            load_yaml(path)


def validate_catalog():
    path = ROOT / "catalog" / "catalog.yaml"
    data = load_yaml(path)
    if not isinstance(data, dict):
        return {}
    ids = {}
    for group in ["skills", "workflows", "rules", "agents", "prompts", "knowledge", "evals", "profiles", "adapters"]:
        entries = data.get(group, [])
        if not isinstance(entries, list):
            fail(f"catalog/catalog.yaml: {group} must be a list")
            continue
        group_ids = set()
        for entry in entries:
            if not isinstance(entry, dict):
                fail(f"catalog/catalog.yaml: invalid entry in {group}")
                continue
            artifact_id = entry.get("id")
            artifact_path = entry.get("path")
            if not isinstance(artifact_id, str) or not NAME_RE.fullmatch(artifact_id):
                fail(f"catalog/catalog.yaml: invalid id in {group}: {artifact_id}")
                continue
            if artifact_id in group_ids:
                fail(f"catalog/catalog.yaml: duplicate {group} id {artifact_id}")
            group_ids.add(artifact_id)
            if not isinstance(artifact_path, str) or not (ROOT / artifact_path).exists():
                fail(f"catalog/catalog.yaml: missing path for {artifact_id}: {artifact_path}")
        ids[group] = group_ids
    expected = {
        "skills": {str(path.parent.relative_to(ROOT)) for path in (ROOT / "skills").glob("*/SKILL.md")},
        "workflows": {str(path.relative_to(ROOT)) for path in (ROOT / "workflows").glob("*/WORKFLOW.md")},
        "rules": {str(path.relative_to(ROOT)) for path in (ROOT / "rules").rglob("*.md")},
        "agents": {str(path.relative_to(ROOT)) for path in (ROOT / "agents").glob("*/AGENT.md")},
        "prompts": {str(path.relative_to(ROOT)) for path in (ROOT / "prompts").glob("*.md")},
        "knowledge": {str(path.relative_to(ROOT)) for path in (ROOT / "knowledge").rglob("*.md")},
        "evals": {str(path.relative_to(ROOT)) for path in (ROOT / "evals").glob("*/cases.yaml")},
        "profiles": {str(path.relative_to(ROOT)) for path in (ROOT / "profiles").glob("*.yaml")},
    }
    for group, expected_paths in expected.items():
        registered_paths = {entry.get("path") for entry in data.get(group, []) if isinstance(entry, dict)}
        missing = sorted(expected_paths - registered_paths)
        for artifact_path in missing:
            fail(f"catalog/catalog.yaml: unregistered {group} artifact {artifact_path}")
    return ids


def validate_profiles(ids):
    mapping = {
        "rules": "rules",
        "skills": "skills",
        "workflows": "workflows",
        "agents": "agents",
        "prompts": "prompts",
        "knowledge": "knowledge",
    }
    for path in (ROOT / "profiles").glob("*.yaml"):
        data = load_yaml(path)
        if not isinstance(data, dict):
            continue
        for field, group in mapping.items():
            values = data.get(field, [])
            if not isinstance(values, list):
                fail(f"{path.relative_to(ROOT)}: {field} must be a list")
                continue
            for value in values:
                if value not in ids.get(group, set()):
                    fail(f"{path.relative_to(ROOT)}: unknown {field} reference {value}")


def main():
    skill_paths = [path for path in ROOT.rglob("SKILL.md") if "templates" not in path.parts]
    if not skill_paths:
        fail("No skills found")
    for path in skill_paths:
        validate_skill(path)
    validate_yaml_files()
    validate_toml_files()
    ids = validate_catalog()
    validate_profiles(ids)
    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"PASS: validated {len(skill_paths)} skills and repository metadata")
    return 0


if __name__ == "__main__":
    sys.exit(main())
