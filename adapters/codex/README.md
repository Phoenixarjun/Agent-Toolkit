# Codex Adapter

Runtime-specific configuration, user-level entrypoint templates, and installation assets for OpenAI Codex environments.

## Contents

- `AGENTS.template.md` — Scaffold for the user-level global instruction file (`~/.codex/AGENTS.md` or `%USERPROFILE%\.codex\AGENTS.md`).
- `sol-luna-xi/` — Codex custom-agent bundle pinning OpenAI model IDs, reasoning levels, sandbox modes, and Windows installation scripts.
- `tune/openai.yaml` — Invocation policy metadata (`allow_implicit_invocation: false`) for the installed Tune skill in OpenAI Codex.

## Components & Installation

### 1. User-Level Entry Point (`AGENTS.template.md`)

Routes arbitrary projects to the Agent Toolkit rules and preferences:

1. Copy `AGENTS.template.md` to your global Codex configuration directory:
   - **Linux / macOS**: `~/.codex/AGENTS.md`
   - **Windows**: `%USERPROFILE%\.codex\AGENTS.md`
2. Replace `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}` with the absolute path to your cloned Agent Toolkit repository.
3. The template instructs Codex to:
   - Apply `rules/global/engineering-rules.md` and `rules/global/workspace-safety.md`.
   - Consult `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` when present.
   - Enforce the workspace safety floor before executing destructive or external operations.

> **Note:** Agent Toolkit's repository-root `AGENTS.md` governs contributors to *this* repository. The adapter template `AGENTS.template.md` governs coding agents operating across other projects.

### 2. Runtime Agent Bundle (`sol-luna-xi`)

The `sol-luna-xi` subfolder provides multi-agent role configurations (`luna-builder-xi`, `luna-reviewer-xi`, `luna-scout-xi`, `luna-validator-xi`) designed for Codex CLI runtime environments.

See [`sol-luna-xi/INSTALL.md`](sol-luna-xi/INSTALL.md) for execution discipline, model parameters, and setup instructions.

## Architectural Boundaries

- Vendor model IDs, sandbox flags, proprietary agent definitions, and local installation scripts belong under `adapters/codex/`.
- Portable capabilities, workflows, and global engineering rules remain under their canonical repository roots (`skills/`, `workflows/`, `rules/`).
