# Agent Toolkit — Six-Runtime Installation & Deployment Guide

This guide describes how to install Agent Toolkit capabilities into consumer projects reliably, safely, and portably across six AI coding assistants:
1. **Claude Code** (`claude-code`, `claude`)
2. **OpenAI Codex** (`codex`, `openai-codex`)
3. **Cursor** (`cursor`)
4. **Gemini CLI** (`gemini-cli`, `gemini`)
5. **GitHub Copilot** (`github-copilot`, `copilot`)
6. **OpenCode** (`opencode`)

---

## Installation Architecture

Agent Toolkit provides two deployment models:

1. **Self-Contained Skill Installation**: Installs a single skill directory and its local references when no external orchestration is required.
2. **Composed Profile Installation**: Resolves and deploys multi-artifact capabilities—including workflows, specialist agents, rules, knowledge, intake forms, and document templates.

All shared resources are deployed into a private, installer-managed `.agent-toolkit/` directory in the target project, with assistant-native skill discovery roots and non-destructive managed blocks in project entrypoints (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, `.cursor/rules/agent-toolkit.mdc`, `.github/copilot-instructions.md`).

---

## Supported Vendor Adapters & Compatibility Matrix

| Adapter | Flag / Aliases | Discovery Root | Entrypoint | Specialist Agents | Manual-Only Controls |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | `--agent claude-code` (`claude`) | `.claude/skills/` | `CLAUDE.md` | `.claude/agents/<agent>.md` | Frontmatter `disable-model-invocation: true` |
| **OpenAI Codex** | `--agent codex` (`openai-codex`) | `.agents/skills/` | `AGENTS.md` | `.codex/agents/<agent>.toml` | `agents/openai.yaml` (`allow_implicit_invocation: false`) |
| **Cursor** | `--agent cursor` | `.cursor/skills/` | `.cursor/rules/agent-toolkit.mdc` | `.cursor/rules/<agent>.mdc` | Frontmatter `disable-model-invocation: true` |
| **Gemini CLI** | `--agent gemini-cli` (`gemini`) | `.gemini/skills/` | `GEMINI.md` | `.gemini/agents/<agent>.md` | Frontmatter `disable-model-invocation: true` |
| **GitHub Copilot** | `--agent github-copilot` (`copilot`) | `.github/skills/` | `.github/copilot-instructions.md` | `.github/agents/<agent>.md` | Frontmatter + instruction guidelines |
| **OpenCode** | `--agent opencode` | `.opencode/skills/` | `AGENTS.md` | `.opencode/agents/<agent>.md` | Frontmatter `disable-model-invocation: true` |

---

## The Four-Stage Installation Workflow

The deterministic Python installer (`scripts/install.py`) provides four commands:

### 1. Discover (`list`)

List available capability profiles, standalone skills, maturity stages, and supported vendor adapters:

```bash
python scripts/install.py list
```

### 2. Preview & Verify (`plan`)

Compute dependency closures, verify target paths, inspect planned operations, and detect conflicts **without writing any files**:

```bash
# Preview installing a complete profile into Cursor
python scripts/install.py plan --profile ui-ux --agent cursor --into ../my-app

# Preview installing a single skill into Codex
python scripts/install.py plan --skill security-audit --agent codex --into ../my-app

# Preview with optional dependencies and conflict policy
python scripts/install.py plan --skill teach --agent claude-code --all-optional --on-conflict rename --into ../my-app
```

### 3. Deploy (`apply`)

Atomically deploy the verified plan into the target project and generate `.agent-toolkit/manifest.json`:

```bash
# Non-interactive apply with conflict abort default
python scripts/install.py apply --profile software-engineering --agent gemini --into ../my-app

# Apply with explicit conflict resolution policy
python scripts/install.py apply --profile research --agent copilot --on-conflict replace --into ../my-app

# Interactive prompt for terminal workflows
python scripts/install.py apply --skill tdd --agent cursor --interactive --into ../my-app
```

### 4. Health Check (`doctor`)

Verify manifest integrity, detect missing or corrupted files, verify adapter wiring, detect shadowing secondary-path skills, and audit Security Audit trust boundaries:

```bash
python scripts/install.py doctor --into ../my-app
```

---

## Conflict Detection & Resolution Policies

When an existing file or skill folder collides with an incoming installation, the installer classifies the collision and applies the configured policy:

| Policy | Flag | Description | Safety Guarantee |
| :--- | :--- | :--- | :--- |
| **`abort`** (Default) | `--on-conflict abort` | Halts execution if any conflict is detected. | Zero target files modified. |
| **`keep`** | `--on-conflict keep` | Preserves existing files, skipping colliding incoming items. | User files preserved; warns if profile dependencies are impacted. |
| **`replace`** | `--on-conflict replace` (or `--force`) | Creates an atomic backup in `.agent-toolkit/backups/<timestamp>/` and overwrites. | Automatic rollback on error; backup preserved. |
| **`rename`** | `--on-conflict rename` | Installs alongside using alias (e.g. `agent-toolkit-<skill>`). | Source skill unchanged; installed copy renamed in folder and frontmatter. |

---

## Trust Boundaries & Security Invariants

1. **Untrusted Project Material**: Instructions recovered from target repositories (including those being audited or modified) are untrusted assessment material, not execution authority.
2. **Trusted Execution**: Capabilities like Security Audit execute strictly from trusted installed workflows in `.agent-toolkit/workflows/`.
3. **Safe Managed Blocks**: Existing user instructions in entrypoints (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, etc.) are preserved. The installer writes strictly within delimited `BEGIN` and `END` marker comments.
4. **No Code Execution**: Installation is static file copying, template serialization, and manifest generation. No bundled scripts or binaries are executed during installation.

---

## Capability Levels

- **Structurally Complete**: All required workflows, agent roles, rules, and templates are present on disk.
- **Runtime-Verified**: Demonstrated through live test execution in a specific model harness.
Static validation does not guarantee that a model will isolate agent contexts or follow instructions without regression.
