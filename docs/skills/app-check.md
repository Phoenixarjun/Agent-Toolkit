# App Check

**`/app-check`** assesses the engineering health of an existing application and identifies the smallest next actions justified by its actual design, usage and evidence.

## The problem

Generic audit checklists often treat a tiny local application like a highly trafficked distributed system, producing speculative warnings about caching, retries, databases, load balancing and scaling. The opposite failure also happens: a real correctness defect is ignored because a project seems small. Neither produces good engineering priorities.

## When to use

Use when you want to know what is already adequate, what may be broken, what could fail under credible conditions, whether your tests meaningfully verify behavior, and what should happen next. It is not a replacement for a dedicated security audit, feature code review, deep change-impact plan, or implementation.

## How it works

The skill first identifies the application's real boundaries and important user journeys. It selectively checks only applicable problem areas, asks the creator only for important external facts, tests claims against concrete evidence, challenges over-engineered recommendations, and delivers one executive summary plus a traceable technical report. When worthwhile and supported, it coordinates independently scoped investigators and an independent challenger; otherwise it clearly reports limited assurance.

## Questions and measurements

The question budget is **zero to eight**, not a compulsory questionnaire. Source-discoverable facts are not asked of the user. Peak load, user-critical journeys, loss tolerance and growth plans are examples of potentially user-owned facts, but only when they change a specific recommendation. Unknown numbers remain unknown; user forecasts are not field measurements.

## Output

The report separates confirmed defects, supported risks, hypotheses and optional improvements. It provides locations, evidence limitations, priority, smallest justified next step, validation or revisit conditions, good existing practices and sensible no-change conclusions. No invented engineering health scores.

## Cost and boundaries

Small scope: a short targeted pass. Broader scope: adaptive deeper investigation and optional subagents, capped by a shared task budget. Read-only by default. It never silently edits the application, changes architecture, executes unsafe load, or invokes `/code` to apply fixes. Full security assurance remains owned by Security Audit.

## Example invocation

```text
/app-check

Assess this application in its current stage and workload.
Identify the few consequential reliability, correctness, resource,
test, or operational issues that are actually applicable.
Ask only for decision-changing facts unavailable in the repository.
Do not implement changes or suggest unnecessary infrastructure.
```

## Canonical behavior

See [`skills/app-check/SKILL.md`](../../skills/app-check/SKILL.md) and the optional [`application-health-assessment` workflow](../../workflows/application-health-assessment/WORKFLOW.md). This guide is descriptive; behavior remains canonical in the skill.
