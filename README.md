<div align="center">

# Agent Toolkit

### Engineering playbooks for coding agents.

**Better decisions. Safer changes. Verifiable outcomes.**

A focused collection of reusable procedures that help capable coding agents approach real engineering work with greater consistency and judgment.

<p>
  <img alt="Focus: Agent Engineering" src="https://img.shields.io/badge/Focus-Agent%20Engineering-2563eb?style=flat-square" />
  <img alt="Design: Tool-Agnostic Core" src="https://img.shields.io/badge/Design-Tool--Agnostic%20Core-475569?style=flat-square" />
  <img alt="Approach: Evidence-Driven" src="https://img.shields.io/badge/Approach-Evidence--Driven-0f766e?style=flat-square" />
  <img alt="Status: Evolving" src="https://img.shields.io/badge/Status-Evolving-71717a?style=flat-square" />
</p>

[Explore skills](#featured-skills) · [Browse catalog](catalog/catalog.yaml) · [Read the philosophy](docs/PHILOSOPHY.md) · [Contribute](CONTRIBUTING.md)

</div>

## Why Agent Toolkit?

Modern coding agents already know languages, frameworks, and patterns. Their harder challenge is deciding **what to build, why, how far to go, and what proves it works**.

Agent Toolkit captures repeatable engineering *behavior*, not technology tutorials. Each skill is a procedure with a clear purpose, decision boundaries, failure behavior, and completion criteria.

**The goal is not more skills. It is more useful behavior per skill.**

## Featured skills

| Skill | What it helps the agent do |
| --- | --- |
| **[Grill Me](skills/grill-me/SKILL.md)** | Expose important assumptions and resolve ambiguity through focused questions. |
| **[Intent Capture](skills/intent-capture/SKILL.md)** | Turn requests into explicit outcomes, constraints, and acceptance criteria. |
| **[Problem to Solution](skills/problem-to-solution/SKILL.md)** | Explore options, challenge premises, and justify a solution before committing. |
| **[TDD](skills/tdd/SKILL.md)** | Work in test-first slices and verify meaningful behavior beyond green tests. |
| **[Code Review](skills/code-review/SKILL.md)** | Find consequential defects against intent, correctness, and system boundaries. |
| **[Security Audit](skills/security-audit/SKILL.md)** | Assess security through risk-based coverage and independent evidence, without performing fixes. |
| **[UI/UX Design](skills/ui-ux-design/SKILL.md)** | Translate product intent into distinctive, usable interfaces and validate design decisions. |

These are **selected capabilities, not a complete or fixed list**. For the evolving inventory, see the **[canonical catalog](catalog/catalog.yaml)** or [skills directory](skills/). New skills appear there without requiring the README to become a long index.

> **Installation matters:** Some capabilities need companion workflows, agents, rules, scripts, or runtime support. Copying a `SKILL.md` alone may not install the complete capability. Review its dependencies and relevant adapter first.

## How the toolkit fits together

```text
Intent + project context
          ↓
     Rules + profile
          ↓
     Relevant skill
          ↓
 Workflow + agents (if required)
          ↓
   Execution + evidence
          ↓
  Validation + outcome
```

| Layer | Responsibility |
| --- | --- |
| `skills/` · `workflows/` · `agents/` | Procedures, coordination, and specialist roles |
| `rules/` · `knowledge/` · `profiles/` | Constraints, conditional guidance, and composition |
| `evals/` · `scripts/` | Behavioral scenarios and deterministic checks |
| `adapters/` | Vendor-specific installation and runtime integration |
| `catalog/` · `templates/` · `docs/` | Discovery, scaffolding, and human guidance |

**Canonical behavior has one owner.** Tool-specific wiring belongs in adapters, not duplicated skill definitions. Guidance is loaded when relevant rather than pushed into every task.

## Get started

```bash
git clone https://github.com/Phoenixarjun/Agent-Toolkit.git
cd Agent-Toolkit
python -m pip install -r requirements.txt
python scripts/validate.py
```

### Profile-Aware Installation

Use the deterministic installer (`scripts/install.py`) to deploy capabilities into any target project:

1. **List profiles and skills**:
   ```bash
   python scripts/install.py list
   ```

2. **Preview installation (dry run)**:
   ```bash
   python scripts/install.py plan --profile software-engineering --agent claude-code --into ../my-app
   ```

3. **Install a complete composed profile**:
   ```bash
   python scripts/install.py apply --profile ui-ux --agent claude-code --into ../my-app
   ```

4. **Install a standalone skill with required dependencies**:
   ```bash
   python scripts/install.py apply --skill security-audit --agent codex --into ../my-app
   ```

5. **Include optional dependencies**:
   ```bash
   python scripts/install.py apply --skill teach --agent claude-code --all-optional --into ../my-app
   ```

6. **Verify installation health**:
   ```bash
   python scripts/install.py doctor --into ../my-app
   ```

Supported adapters include `--agent claude-code`, `--agent codex`, `--agent cursor`, `--agent gemini-cli`, `--agent github-copilot`, and `--agent opencode`. Conflict resolution policies are configurable via `--on-conflict {keep,replace,rename,abort}` (with automatic backups created on replace). The installer manages private shared resources under `<target>/.agent-toolkit/`, wires native skill discovery directories, and safely updates project entrypoints (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/agent-toolkit.mdc`, `GEMINI.md`, `.github/copilot-instructions.md`) without overwriting user instructions.

See the comprehensive **[Installation Guide](docs/installation.md)** for architecture, security invariants, conflict resolution policies, and runtime capability levels.

> **Trust and Verification Note:** Static installation and repository validation check artifact and syntactic consistency. They do not prove that a live model will isolate agent contexts or follow instructions without regression. Instructions recovered from projects being evaluated or audited are untrusted material, never execution authority.

## The philosophy

**Fewer, stronger capabilities. One responsibility per artifact. Evidence before confidence.**

A new skill should exist only when it improves a repeatable decision or procedure that the model cannot reliably handle through ordinary context. Prefer improving an existing capability over creating an overlapping one. Make preferences adjustable without weakening correctness and safety boundaries.

Read the full **[Agent Toolkit Philosophy](docs/PHILOSOPHY.md)** for the reasoning behind these choices.

## Contributing and trust

See [CONTRIBUTING.md](CONTRIBUTING.md) for artifact admission and validation, and [AGENTS.md](AGENTS.md) for instructions when editing this repository with an agent.

**Review skills before enabling them.** Understand what they can read, modify, execute, and treat as completion. The right procedure for one engineering environment may not fit another.

<div align="center">

**Build fewer artifacts. Make each one earn its context.**

</div>
