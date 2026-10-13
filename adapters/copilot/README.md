# GitHub Copilot Adapter

Runtime-specific configuration, instruction templates, and installation guidelines for [GitHub Copilot](https://github.com/features/copilot).

## Contents

- `copilot-instructions.template.md` - Scaffold for project or repository instruction file (`.github/copilot-instructions.md`).
- `tune/INVOCATION.md` - Invocation policy guidelines for the installed Tune skill in GitHub Copilot (`disable-model-invocation: true`).

## Installation

1. Copy `copilot-instructions.template.md` to your repository instructions path:
   - **Project-level**: `.github/copilot-instructions.md`
2. Replace `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}` with the absolute path to your cloned Agent Toolkit repository.
3. Verify that canonical rules (`rules/global/engineering-rules.md`, `rules/global/workspace-safety.md`) resolve cleanly from that root.

## Runtime Behavior

When installed as the instruction file for GitHub Copilot:

1. **Routes to canonical rules**: Applies portable engineering discipline from `rules/global/engineering-rules.md` and the mandatory safety floor from `rules/global/workspace-safety.md`.
2. **Skill discovery**: Discovers skills installed under `.github/skills/` (and shared skills in `.agents/skills/`).
3. **Specialist agents**: Mapped to native custom agent configurations under `.github/agents/<agent>.md`.
4. **Honors project-level preferences**: Loads optional choices from `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` if present, without weakening the safety floor.

## Architectural Boundaries

- This adapter provides instruction routing and safety boundaries. It does not replace GitHub Copilot's repository settings, review workflows, or security filters.
- Canonical skills, rules, and workflows reside under their respective repository directories (`skills/`, `rules/`, `workflows/`).
