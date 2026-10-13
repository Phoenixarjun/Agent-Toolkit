from argparse import ArgumentParser
from datetime import date
from pathlib import Path
import os
import re


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:48] or "change"


def template_path():
    return Path(__file__).resolve().parents[1] / "templates" / "documents" / "CHANGE-INTENT.md"


def escape_yaml_string(value):
    # Strip newlines and control characters to prevent frontmatter injection
    cleaned = re.sub(r"[\r\n\x00-\x1f]", " ", str(value)).strip()
    return cleaned.replace("\\", "\\\\").replace('"', '\\"')


def render(template, intent_id, title, source, created):
    clean_title = escape_yaml_string(title)
    clean_source = escape_yaml_string(source)
    return (
        template.replace("{{INTENT_ID}}", intent_id)
        .replace("{{TITLE}}", clean_title)
        .replace("{{SOURCE}}", clean_source)
        .replace("{{CREATED_DATE}}", created)
    )


def main():
    parser = ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--title", required=True)
    parser.add_argument("--source", default="direct")
    parser.add_argument("--date")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Target root directory does not exist or is not a directory: {args.root}")

    target = (root / ".agent-toolkit" / "intents").resolve()
    if not target.is_relative_to(root):
        raise SystemExit(f"Refusing to write outside root directory: {target}")

    target.mkdir(parents=True, exist_ok=True)

    created = args.date or date.today().isoformat()
    compact = created.replace("-", "")
    slug = slugify(args.title)
    template = template_path().read_text(encoding="utf-8")

    for sequence in range(1, 1000):
        intent_id = f"INT-{compact}-{sequence:03d}"
        path = target / f"{intent_id}-{slug}.md"
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
        except FileExistsError:
            continue
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(render(template, intent_id, args.title, args.source, created))
        print(path)
        return 0

    raise SystemExit("No available intent sequence for the selected date")


if __name__ == "__main__":
    raise SystemExit(main())
