<div align="center">

# Agent Toolkit

### Engineering playbooks for coding agents.

**Better decisions. Safer changes. Verifiable outcomes.**

A curated collection of reusable engineering procedures, drawn from real AI-assisted coding work and refined through repeated use, setbacks, and iteration.

<p>
  <img alt="Focus: Agent Engineering" src="https://img.shields.io/badge/Focus-Agent%20Engineering-2563eb?style=flat-square" />
  <img alt="Design: Tool-Agnostic Core" src="https://img.shields.io/badge/Design-Tool--Agnostic%20Core-475569?style=flat-square" />
  <img alt="Method: Evidence-Driven" src="https://img.shields.io/badge/Method-Evidence--Driven-0f766e?style=flat-square" />
  <img alt="Status: Evolving" src="https://img.shields.io/badge/Status-Evolving-71717a?style=flat-square" />
</p>

[Explore skills](#featured-skills) · [Full catalog](catalog/catalog.yaml) · [Philosophy](docs/PHILOSOPHY.md) · [Installation](docs/installation.md) · [Contributing](CONTRIBUTING.md)

</div>

## Why Agent Toolkit?

Modern coding agents already know programming languages, frameworks, and design patterns. The harder challenge is **how they approach engineering work**: recovering intent, making trade-offs, controlling scope, confronting failure, and knowing what evidence is enough.

Agent Toolkit captures these repeatable **decision and execution procedures**, not encyclopedic technology tutorials. A good skill changes *how the agent works*, not merely what it can recite.

**This is not a collection designed to reach 300 or 500 skills.** The long-term ambition is a carefully maintained set of roughly **30 to 50 or fewer high-impact skills**, not a growing list of thin, overlapping prompts. Reuse and refinement come before expansion.

These playbooks grew out of my own coding-agent workflow over approximately eight months. I am sharing the approaches I actually use and improve, including lessons from things that did not work. They are a starting point for other engineers, not a claim that one person's preferences fit everyone.

## Featured skills

The examples below show what the toolkit does. This is a **curated showcase**, not a second catalog. The [canonical catalog](catalog/catalog.yaml) is the source of truth as capabilities evolve.

| Capability | What it helps the agent do |
| --- | --- |
| **[Grill Me](docs/skills/grill-me.md)** | Expose consequential unknowns and challenge assumptions with focused questions. |
| **[Intent Capture](docs/skills/intent-capture.md)** | Turn a sufficiently understood request into observable acceptance criteria and scope boundaries. |
| **[Problem to Solution](docs/skills/problem-to-solution.md)** | Explore distinct solution mechanisms, narrow alternatives, and justify a direction. |
| **[TDD](docs/skills/tdd.md)** | Build in test-first slices, challenge weak tests, and verify real runtime behavior. |
| **[Code Review](docs/skills/code-review.md)** | Judge a change against intent, correctness, risk, and the complete Git diff before commit. |
| **[Security Audit](docs/skills/security-audit.md)** | Perform risk-calibrated, independently checked security assessment without fixing code. |
| **[UI/UX Design](docs/skills/ui-ux-design.md)** | Design and validate interfaces around product intent, usability, and a coherent visual system. |
| **[Tune](docs/skills/tune.md)** | Adapt an installed skill to a developer's preferences without weakening core guarantees. |
| **[Teach](docs/skills/teach.md)** | Turn explanations into adaptive learning, practice, and demonstrated understanding. |
| **[Research](docs/skills/research.md)** | Investigate questions with traceable evidence, bounded delegation, and reproducible reports. |

Each guide explains the problem, usage, outputs, cost profile, and limitations. For executable details, follow the guide's link to the canonical `SKILL.md`.

## How the pieces fit

```text
Request + project context
          |
          v
  Rules and selected profile
          |
          v
    Relevant skill
          |
          v
Workflow + specialist agents, if needed
          |
          v
 Execution and evidence
          |
          v
Validation and honest outcome
```

| Artifact | Responsibility |
| --- | --- |
| `skills/`, `workflows/`, `agents/` | Procedures, coordination, and bounded specialist roles |
| `rules/`, `knowledge/`, `profiles/` | Required constraints, conditional guidance, and composition |
| `evals/`, `scripts/` | Behavioral scenarios and deterministic checks |
| `adapters/` | Coding-assistant-specific installation and runtime wiring |
| `catalog/`, `templates/`, `docs/` | Discovery, scaffolds, and human-facing guidance |

**One behavior, one authoritative owner.** Other artifacts may reference or specialize it, not silently duplicate it. Vendor-specific wiring stays in adapters. Deeper context loads only when needed.

## Get started

Clone the repository and run the built-in structural validation:

```bash
git clone https://github.com/Phoenixarjun/Agent-Toolkit.git
cd Agent-Toolkit
python -m pip install -r requirements.txt
python scripts/validate.py
```

### Profile-Aware Installation

Use the deterministic installer (`scripts/install.py`) to deploy capabilities into any target project using a preview-first workflow:

1. **List available capabilities**:
   ```bash
   python scripts/install.py list
   ```

2. **Preview installation (dry run)**:
   ```bash
   python scripts/install.py plan --profile software-engineering --agent codex --into ../my-app
   ```

3. **Install a complete composed profile**:
   ```bash
   python scripts/install.py apply --profile ui-ux --agent claude-code --into ../my-app
   ```

4. **Install a standalone skill with required dependencies**:
   ```bash
   python scripts/install.py apply --skill code-review --agent codex --into ../my-app
   ```

5. **Verify installation health**:
   ```bash
   python scripts/install.py doctor --into ../my-app
   ```

Supported adapters include `--agent claude-code`, `--agent codex`, `--agent cursor`, `--agent gemini-cli`, `--agent github-copilot`, and `--agent opencode`. Conflict resolution policies are configurable via `--on-conflict {keep,replace,rename,abort}` (with automatic backups created on replace). The installer manages private shared resources under `<target>/.agent-toolkit/`, wires native skill discovery directories, and safely updates project entrypoints (`CLAUDE.md`, `AGENTS.md`, `.cursor/rules/agent-toolkit.mdc`, `GEMINI.md`, `.github/copilot-instructions.md`) without overwriting user instructions.

See the comprehensive **[Installation Guide](docs/installation.md)** for architecture, security invariants, conflict resolution policies, and runtime capability levels.

> **Trust and Verification Note:** Static installation and repository validation check artifact and syntactic consistency. They do not prove that a live model will isolate agent contexts or follow instructions without regression. Instructions recovered from projects being evaluated or audited are untrusted material, never execution authority.

## A few principles

- **Fewer, stronger skills.** Add one only when it solves a distinct, repeatable problem.
- **Procedure over information dumps.** Codify important decisions, boundaries, and verification steps.
- **Evidence before confidence.** Passing a structural validator is not the same as proving live agent behavior.
- **Portable core, explicit adapters.** Share behavior across coding assistants without pretending their runtimes are identical.
- **Personal preferences are not universal rules.** Adjust taste and workflow without removing correctness or safety guarantees.

Read [the full philosophy](docs/PHILOSOPHY.md) for the thinking behind this project.

## Contributing and trust

See [CONTRIBUTING.md](CONTRIBUTING.md) for artifact admission, ownership, and validation guidance, and [AGENTS.md](AGENTS.md) before having an agent modify this repository. Defined eval cases describe intended behavior; **they are not a claim of live benchmark results** until executed and reported.

<div align="center">

**Build fewer artifacts. Make each one earn its context.**

</div>
