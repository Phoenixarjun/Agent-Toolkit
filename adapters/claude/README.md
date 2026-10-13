# Claude Code Adapter

Runtime-specific wiring and user-level entrypoint templates for [Claude Code](https://docs.anthropic.com/en/docs/agents-and-tools/claude-code).

## Contents

- `CLAUDE.template.md` - Scaffold for the user-level global instruction file (`~/.claude/CLAUDE.md` or `%USERPROFILE%\.claude\CLAUDE.md`).
- `tune/INVOCATION.md` - Invocation policy guidelines for the installed Tune skill in Claude Code (`disable-model-invocation: true`).

## Installation

1. Copy `CLAUDE.template.md` to your user-level configuration path:
   - **Linux / macOS**: `~/.claude/CLAUDE.md`
   - **Windows**: `%USERPROFILE%\.claude\CLAUDE.md`
2. Replace `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}` with the absolute path to your cloned Agent Toolkit repository.
3. Verify that the referenced paths (`rules/global/engineering-rules.md`, `rules/global/workspace-safety.md`) resolve cleanly from that root.

## Runtime Behavior

When installed as the global user instruction file, Claude Code:

1. **Routes to canonical rules**: Applies portable engineering discipline from `rules/global/engineering-rules.md` and the mandatory safety floor from `rules/global/workspace-safety.md`.
2. **Honors project-level preferences**: Loads optional choices from `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` if present, without allowing preferences to weaken the safety floor.
3. **Preserves project context**: Prioritizes the active project's own repository instructions and existing conventions before making changes.
4. **Enforces destructive-action gates**: Applies the workspace safety floor (standard or strict mode) before performing deletions or irreversible operations.

## Architectural Boundaries

- This adapter is routing metadata and a safety reminder. It does not replace Claude Code's native permissions, tool approvals, or project-level instructions.
- Portable skills, rules, and workflows reside under their respective repository directories (`skills/`, `rules/`, `workflows/`).
