from argparse import ArgumentParser
from datetime import date
from pathlib import Path
import os
import re


def slugify(value):
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value[:48] or "change"


def template_path():
    return Path(__file__).resolve().parents[1] / "templates" / "CHANGE-INTENT.md"


def render(template, intent_id, title, source, created):
    return (
        template.replace("{{INTENT_ID}}", intent_id)
        .replace("{{TITLE}}", title.replace('"', "'"))
        .replace("{{SOURCE}}", source.replace('"', "'"))
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
    target = root / ".agent-toolkit" / "intents"
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
