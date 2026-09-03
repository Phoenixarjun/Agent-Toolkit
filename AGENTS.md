# Agent Base Repository Instructions

## Purpose

This repository is the canonical source for personal coding-agent behavior.

Preserve the boundary between portable artifacts and vendor-specific adapters.

## Required engineering behavior

Before changing this repository:

1. Understand the requested outcome and affected artifact type.
2. Prefer the smallest change that satisfies the request cleanly.
3. Keep responsibilities modular and avoid duplicating canonical content.
4. Preserve unrelated user changes.
5. Validate the repository before declaring completion.

Read `rules/global/engineering-rules.md` when implementing or modifying executable repository code.

## Artifact rules

- Skills must be specific, task-oriented, and concise.
- Do not add persona fluff such as years of experience as a substitute for instructions.
- Skill descriptions must say what the skill does and when it should be used.
- Keep primary `SKILL.md` files below 500 lines; prefer substantially less.
- Move deep supporting material to one-level-deep `references/` files.
- Workflows own sequencing and coordination, not domain tutorials.
- Rules must be short, durable, and genuinely global within their scope.
- Agents must have explicit responsibilities, non-responsibilities, and output contracts.
- Prompts must remain explicit reusable requests rather than hidden policy.
- Knowledge files explain principles and tradeoffs; they do not silently create mandatory behavior.
- Vendor model IDs, installation paths, proprietary config, and runtime assumptions belong under `adapters/`.
- Do not duplicate a canonical artifact inside multiple adapters unless the target runtime requires a transformed copy.

## Quality gate

Run:

```bash
python scripts/validate.py
```

Do not claim success if validation fails.
