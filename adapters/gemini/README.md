# Gemini CLI Adapter

Runtime-specific configuration, user-level entrypoint templates, and installation guidelines for [Gemini CLI](https://github.com/google-gemini/gemini-cli).

## Contents

- `GEMINI.template.md` — Scaffold for the user-level global instruction file (`~/.gemini/GEMINI.md` or `%USERPROFILE%\.gemini\GEMINI.md`).
- `tune/INVOCATION.md` — Invocation policy guidelines for the installed Tune skill in Gemini CLI (`disable-model-invocation: true`).

## Installation

1. Copy `GEMINI.template.md` to your global or project Gemini instructions:
   - **Linux / macOS**: `~/.gemini/GEMINI.md`
   - **Windows**: `%USERPROFILE%\.gemini\GEMINI.md`
2. Replace `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}` with the absolute path to your cloned Agent Toolkit repository.
3. Verify that canonical rules (`rules/global/engineering-rules.md`, `rules/global/workspace-safety.md`) resolve cleanly from that root.

## Runtime Behavior

When installed as the entrypoint for Gemini CLI:

1. **Routes to canonical rules**: Applies portable engineering discipline from `rules/global/engineering-rules.md` and the mandatory safety floor from `rules/global/workspace-safety.md`.
2. **Skill discovery**: Gemini CLI discovers skills placed in `.gemini/skills/` (and shared skills in `.agents/skills/`).
3. **Specialist agents**: Mapped to native subagent definitions under `.gemini/agents/<agent>.md`.
4. **Honors project-level preferences**: Loads optional choices from `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` if present, without weakening the safety floor.

## Architectural Boundaries

- This adapter provides instruction routing and safety guardrails. It does not replace Gemini CLI's native permissions or tool controls.
- Canonical skills, rules, and workflows reside under their respective repository directories (`skills/`, `rules/`, `workflows/`).
