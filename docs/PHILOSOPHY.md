# Agent Toolkit Philosophy

## Why this project exists

Capable coding models already possess broad technical knowledge. Agent Toolkit exists to improve how they **apply** that knowledge: how they interpret intent, examine trade-offs, respect boundaries, perform work, and verify outcomes.

This is a curated engineering playbook, not a race to accumulate skills. A repository containing 500 or more skills is not necessarily more useful than one with a small number of precise, tested capabilities.

## What earns a place here

A skill is justified when a repeatable procedure makes agent behavior materially more reliable, focused, or verifiable. It should establish when to activate, what job it owns, which context matters, how decisions are made, when to stop or escalate, and what counts as evidence of completion.

A generic `FastAPI` or `backend` tutorial rarely qualifies on its own. If the model already knows the information, repeating it in a skill consumes context without necessarily improving execution.

**Behavioral leverage matters more than artifact count or document length.**

## How I want agents to engineer

Understand the actual goal before changing code. Inspect the existing system before inventing a new design. Choose the simplest correct solution that respects current constraints and reasonable future change. Prefer cohesive modules and explicit boundaries, but do not impose patterns or abstractions without a reason.

Be skeptical of your own work. Check failure paths and unintended effects. Verify outcomes with appropriate evidence, and report what remains uncertain. A persuasive explanation is not a substitute for a working result.

These are guiding judgments, not a mandate to apply every design pattern or checklist on every task. The applicable technical requirements remain in the repository's canonical rules and skills.

## How the toolkit stays lean

- **One responsibility, one owner.** Reuse, extend, or reference an existing artifact before adding another. Avoid duplicate or contradictory instructions.
- **Progressive disclosure.** Keep essential behavior close to execution; load deeper references only when needed.
- **Deterministic when possible.** Use scripts, schemas, and tests for checks that do not need model judgment.
- **Portable at the core.** Keep general behavior independent of Codex, Claude Code, or other runtimes. Place vendor wiring in adapters.
- **Evolve through evidence.** Investigate failures, change the smallest responsible behavior, and check for regressions. More instructions are not automatically better.

## A personal baseline, not a universal preference

My engineering preferences are a starting point, not an obligation for everyone who installs the toolkit. Developers may prefer different module sizes, reporting detail, or design conventions while still producing reliable systems.

Customization should affect legitimate choices, not silently remove safety guarantees or the essential contract of a skill. The toolkit should make that distinction explicit.

---

**The measure of Agent Toolkit is not how many instructions an agent receives. It is whether the agent makes better decisions and produces more reliable evidence because of them.**
