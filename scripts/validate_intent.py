from argparse import ArgumentParser
from pathlib import Path
import re
import sys
import yaml

REQUIRED_SECTIONS = [
    "Outcome",
    "Context",
    "In Scope",
    "Acceptance Criteria",
    "Must Preserve",
    "Constraints",
    "Quality Constraints",
    "Approval Boundaries",
    "Out of Scope",
    "Assumptions",
    "Open Decisions",
    "Source References",
    "Amendments",
]

VALID_STATUS = {"draft", "ready", "completed", "superseded", "cancelled"}
ID_RE = re.compile(r"^INT-\d{8}-\d{3}$")
FILE_RE = re.compile(r"^(INT-\d{8}-\d{3})-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
AC_RE = re.compile(r"^- (AC-\d{3}):\s+(.+)$", re.MULTILINE)
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}|<[^>]+>|\bTBD\b|\bTODO\b", re.IGNORECASE)


def parse(path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated YAML frontmatter")
    data = yaml.safe_load(text[4:end])
    if not isinstance(data, dict):
        raise ValueError("frontmatter must be a mapping")
    return data, text[end + 5 :]


def sections(body):
    found = {}
    matches = list(re.finditer(r"^# ([^\n]+)\s*$", body, re.MULTILINE))
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        found[match.group(1).strip()] = body[start:end].strip()
    return found


def validate(path, strict):
    errors = []
    warnings = []

    try:
        data, body = parse(path)
    except Exception as exc:
        return [str(exc)], []

    intent_id = data.get("id")
    if not isinstance(intent_id, str) or not ID_RE.fullmatch(intent_id):
        errors.append("frontmatter id must match INT-YYYYMMDD-NNN")

    match = FILE_RE.fullmatch(path.name)
    if not match:
        errors.append("filename must match INT-YYYYMMDD-NNN-short-slug.md")
    elif isinstance(intent_id, str) and match.group(1) != intent_id:
        errors.append("frontmatter id must match filename intent id")

    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        errors.append("title is required")

    status = data.get("status")
    if status not in VALID_STATUS:
        errors.append(f"status must be one of {sorted(VALID_STATUS)}")

    revision = data.get("revision")
    if not isinstance(revision, int) or revision < 1:
        errors.append("revision must be an integer >= 1")

    source = data.get("source")
    if not isinstance(source, str) or not source.strip():
        errors.append("source is required")

    created = data.get("created")
    if not isinstance(created, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", created):
        errors.append("created must use YYYY-MM-DD")
    elif isinstance(intent_id, str) and ID_RE.fullmatch(intent_id):
        if intent_id[4:12] != created.replace("-", ""):
            errors.append("intent id date must match created date")

    supersedes = data.get("supersedes")
    if supersedes is not None and (not isinstance(supersedes, str) or not ID_RE.fullmatch(supersedes)):
        errors.append("supersedes must be null or a valid INT-YYYYMMDD-NNN id")

    found = sections(body)
    for name in REQUIRED_SECTIONS:
        if name not in found:
            errors.append(f"missing section: {name}")

    acs = AC_RE.findall(found.get("Acceptance Criteria", ""))
    ac_ids = [item[0] for item in acs]
    if not acs:
        errors.append("at least one acceptance criterion with a stable AC-NNN id is required")
    if len(ac_ids) != len(set(ac_ids)):
        errors.append("acceptance criterion ids must be unique")

    acceptance_text = found.get("Acceptance Criteria", "")
    for index, (ac_id, _) in enumerate(acs):
        start = acceptance_text.find(f"- {ac_id}:")
        next_start = acceptance_text.find("- AC-", start + 1)
        block = acceptance_text[start: next_start if next_start != -1 else len(acceptance_text)]
        if "Evidence:" not in block:
            errors.append(f"{ac_id} is missing expected evidence")

    if strict or status == "ready":
        for name in ["Outcome", "In Scope", "Must Preserve", "Out of Scope"]:
            value = found.get(name, "")
            if not value or PLACEHOLDER_RE.search(value):
                errors.append(f"{name} must be resolved before ready")

        if PLACEHOLDER_RE.search(body):
            errors.append("ready contract contains placeholder content")

        open_decisions = found.get("Open Decisions", "").strip().lower()
        if open_decisions not in {"- none", "- none."}:
            errors.append("ready contract must have no unresolved Open Decisions")

        assumptions = found.get("Assumptions", "")
        if "material" in assumptions.lower() and assumptions.strip().lower() not in {"- none", "- none."}:
            warnings.append("review assumptions manually; material assumptions should normally be Open Decisions")

        if isinstance(revision, int) and revision > 1:
            amendments = found.get("Amendments", "").strip().lower()
            if amendments in {"- none", "- none."}:
                errors.append("revision > 1 requires an Amendments entry")

    return errors, warnings


def duplicate_ids(path):
    matches = []
    parent = path.parent
    if parent.name != "intents":
        return matches
    ids = {}
    for candidate in parent.glob("INT-*.md"):
        match = FILE_RE.fullmatch(candidate.name)
        if not match:
            continue
        ids.setdefault(match.group(1), []).append(candidate.name)
    for intent_id, names in ids.items():
        if len(names) > 1:
            matches.append(f"duplicate intent id {intent_id}: {', '.join(sorted(names))}")
    return matches


def main():
    parser = ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    path = Path(args.path).resolve()
    if not path.is_file():
        print("FAIL")
        print(f"- file not found: {path}")
        return 1

    errors, warnings = validate(path, args.strict)
    errors.extend(duplicate_ids(path))

    if errors:
        print("FAIL")
        for error in errors:
            print(f"- {error}")
        for warning in warnings:
            print(f"- warning: {warning}")
        return 1

    print("PASS")
    for warning in warnings:
        print(f"- warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
