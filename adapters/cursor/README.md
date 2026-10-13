# Cursor Adapter

Runtime-specific configuration, user/global rule templates, and installation guidelines for [Cursor](https://cursor.com).

## Contents

- `agent-toolkit.template.mdc` - Scaffold for Cursor rule files (`.cursor/rules/agent-toolkit.mdc` or user-level rules).
- `tune/INVOCATION.md` - Invocation policy guidelines for the installed Tune skill in Cursor (`disable-model-invocation: true`).

## Installation

1. Copy `agent-toolkit.template.mdc` to your Cursor rules directory:
   - **Project-level**: `.cursor/rules/agent-toolkit.mdc`
   - **User-level / Global**: User global rules directory or settings.
2. Replace `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}` with the absolute path to your cloned Agent Toolkit repository.
3. Verify that canonical rules (`rules/global/engineering-rules.md`, `rules/global/workspace-safety.md`) resolve cleanly from that root.

## Runtime Behavior

When installed as an active rule in Cursor:

1. **Routes to canonical rules**: Applies portable engineering discipline from `rules/global/engineering-rules.md` and the mandatory safety floor from `rules/global/workspace-safety.md`.
2. **Skill discovery**: Cursor discovers project-level skills placed in `.cursor/skills/` (and shared skills in `.agents/skills/`).
3. **Specialist agents**: Mapped as targeted `.cursor/rules/<agent>.mdc` rules with `alwaysApply: false`.
4. **Honors project-level preferences**: Loads optional choices from `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` if present, without weakening the safety floor.

## Architectural Boundaries

- This adapter provides rule routing metadata and safety boundaries. It does not replace Cursor's native tool permissions or project instructions.
- Portable skills, rules, and workflows reside under their respective repository directories (`skills/`, `rules/`, `workflows/`).
