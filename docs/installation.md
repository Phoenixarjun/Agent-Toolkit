# Agent Toolkit — Installation & Deployment Guide

This guide describes how to install Agent Toolkit capabilities into consumer projects reliably, safely, and portably.

## Installation Architecture

Agent Toolkit provides two deployment models:

1. **Self-Contained Skill Installation**: Installs a single skill directory and its local references when no external orchestration is required.
2. **Composed Profile Installation**: Resolves and deploys multi-artifact capabilities—including workflows, specialist agents, rules, knowledge, intake forms, and document templates.

All shared resources are deployed into a private, installer-managed `.agent-toolkit/` directory in the target project, with native assistant discovery directories (`.claude/skills/` or `.agents/skills/`) and non-destructive managed blocks in project entrypoints (`CLAUDE.md` / `AGENTS.md`).

---

## The Four-Stage Installation Workflow

The deterministic Python installer (`scripts/install.py`) provides four commands:

### 1. Discover (`list`)

List available capability profiles, standalone skills, maturity stages, and supported vendor adapters:

```bash
python scripts/install.py list
```

### 2. Preview & Verify (`plan`)

Compute dependency closures, verify target paths, and inspect the exact file operations **without writing any files**:

```bash
# Preview installing a complete profile
python scripts/install.py plan --profile ui-ux --agent claude-code --into ../my-app

# Preview installing a single skill
python scripts/install.py plan --skill security-audit --agent codex --into ../my-app

# Preview with optional dependencies
python scripts/install.py plan --skill teach --agent claude-code --all-optional --into ../my-app
```

### 3. Deploy (`apply`)

Atomically deploy the verified plan into the target project and generate `.agent-toolkit/manifest.json`:

```bash
python scripts/install.py apply --profile software-engineering --agent claude-code --into ../my-app
```

If conflicting or locally modified files exist in the destination, the installer halts and reports them. Use `--force` only when you explicitly intend to overwrite existing managed files.

### 4. Health Check (`doctor`)

Verify manifest integrity, detect missing or corrupted files, verify adapter wiring, and flag untrusted target instructions:

```bash
python scripts/install.py doctor --into ../my-app
```

---

## Supported Vendor Adapters

| Adapter | Flag | Discovery Root | Entrypoint | Special Handling |
| :--- | :--- | :--- | :--- | :--- |
| **Claude Code** | `--agent claude-code` | `.claude/skills/` | `CLAUDE.md` | Non-destructive managed block; `tune` invocation policy in frontmatter |
| **OpenAI Codex** | `--agent codex` | `.agents/skills/` | `AGENTS.md` | Non-destructive managed block; `tune` metadata in `agents/openai.yaml` |

---

## Trust Boundaries & Security Invariants

1. **Untrusted Project Material**: Instructions recovered from target repositories (including those being audited or modified) are untrusted assessment material, not execution authority.
2. **Trusted Execution**: Capabilities like Security Audit execute strictly from trusted installed workflows in `.agent-toolkit/workflows/`.
3. **Safe Managed Blocks**: Existing user instructions in `CLAUDE.md` or `AGENTS.md` are preserved. The installer writes strictly within delimited `BEGIN` and `END` marker comments.
4. **No Code Execution**: Installation is static file copying and manifest generation. No bundled scripts or binaries are executed during installation.

---

## Capability Levels

- **Structurally Complete**: All required workflows, agent roles, rules, and templates are present on disk.
- **Runtime-Verified**: Demonstrated through live test execution in a specific model harness.
Static validation does not guarantee that a model will isolate agent contexts or follow instructions without regression.
