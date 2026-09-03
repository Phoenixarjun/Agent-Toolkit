from pathlib import Path
import argparse
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

CONFIG = {
    "skill": ("templates/skill/SKILL.template.md", "skills/{name}/SKILL.md"),
    "workflow": ("templates/workflow/WORKFLOW.template.md", "workflows/{name}/WORKFLOW.md"),
    "agent": ("templates/agent/AGENT.template.md", "agents/{name}/AGENT.md"),
    "rule": ("templates/rule/RULES.template.md", "rules/{name}.md"),
    "prompt": ("templates/prompt/PROMPT.template.md", "prompts/{name}.md"),
    "knowledge": ("templates/knowledge/KNOWLEDGE.template.md", "knowledge/{name}.md"),
    "profile": ("templates/profile/PROFILE.template.yaml", "profiles/{name}.yaml"),
    "eval": ("templates/eval/EVAL.template.yaml", "evals/{name}/cases.yaml"),
}


def title_from_name(name):
    return " ".join(part.capitalize() for part in name.split("-"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=CONFIG)
    parser.add_argument("name")
    args = parser.parse_args()

    if not NAME_RE.fullmatch(args.name) or len(args.name) > 64:
        print("Artifact name must be lowercase kebab-case and at most 64 characters.")
        return 1

    template_rel, target_pattern = CONFIG[args.kind]
    template = ROOT / template_rel
    target = ROOT / target_pattern.format(name=args.name)

    if target.exists():
        print(f"Target already exists: {target.relative_to(ROOT)}")
        return 1

    content = template.read_text(encoding="utf-8")
    content = content.replace("{name}", args.name).replace("{title}", title_from_name(args.name))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    print(f"Created {target.relative_to(ROOT)}")
    print("Add the artifact to catalog/catalog.yaml before considering it complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
