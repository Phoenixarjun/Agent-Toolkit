# OpenCode Adapter

Runtime-specific configuration, user-level entrypoint templates, and installation guidelines for [OpenCode](https://github.com/opencode-ai/opencode).

## Contents

- `AGENTS.template.md` - Scaffold for user-level global or project-level instruction file (`AGENTS.md` or `~/.config/opencode/AGENTS.md`).
- `tune/INVOCATION.md` - Invocation policy guidelines for the installed Tune skill in OpenCode (`disable-model-invocation: true`).

## Installation

1. Copy `AGENTS.template.md` to your OpenCode instructions path:
   - **Linux / macOS**: `~/.config/opencode/AGENTS.md` or project `AGENTS.md`
   - **Windows**: `%USERPROFILE%\.config\opencode\AGENTS.md` or project `AGENTS.md`
2. Replace `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}` with the absolute path to your cloned Agent Toolkit repository.
3. Verify that canonical rules (`rules/global/engineering-rules.md`, `rules/global/workspace-safety.md`) resolve cleanly from that root.

## Runtime Behavior

When installed as the entrypoint for OpenCode:

1. **Routes to canonical rules**: Applies portable engineering discipline from `rules/global/engineering-rules.md` and the mandatory safety floor from `rules/global/workspace-safety.md`.
2. **Skill discovery**: Discovers skills installed under `.opencode/skills/` (and shared skills in `.agents/skills/`).
3. **Specialist agents**: Mapped to native custom agent configurations under `.opencode/agents/<agent>.md`.
4. **Honors project-level preferences**: Loads optional choices from `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` if present, without weakening the safety floor.

## Architectural Boundaries

- This adapter provides instruction routing and safety boundaries. It does not replace OpenCode's native execution sandboxes or project instructions.
- Canonical skills, rules, and workflows reside under their respective repository directories (`skills/`, `rules/`, `workflows/`).
