---
name: career-plan
description: Create or review versioned career plans using durable pillars, market evidence, capacity and impact analysis.
---

# Career Plan

Load adaptive-planning, workspace, delegation and rubrics. Coordinator owns approval and storage; planner and critics are read-only.

## Initial plan

Recover known candidate facts. Use `grill-me` only as compatible bounded intake; otherwise ask at most two grouped rounds, focused on decisions. Request authorized public footprint audit through `career-presence` in audit-only mode when useful; no name-only identity assumptions. Request project evaluation or research only when material. Use `career-planner` for assessment and proposal with cited evidence. Derive durable pillars, role capabilities, milestones, capacity, reserve and review interval. Run independent `career-critic` as plan analyst with frozen plan rubric; verify calculations and missing prerequisites, revise at most twice. Show plan with assumptions, alternatives and exact version. Approval is required before activation; `--plan` alone is not approval. In chat-only mode present logical version and explicitly note no saved state.

## Import existing plan

Use for `--import-plan` or when a candidate brings an externally established roadmap. Inspect the original plan and supporting records; establish target, original duration, elapsed time, remaining deadline, completed work, ongoing work and remaining activities. Recover available candidate evidence before asking questions; ask only material missing questions. Preserve the original plan unchanged as historical evidence when persistence is authorized. Normalize remaining work into the supported Career plan contract (`scripts/career/plan_store.py`), preserving existing goals, priorities, pillars, milestones and decisions while recording confirmed progress separately from planned work. Calculate remaining capacity using actual remaining time rather than original full duration. If historical records cannot be represented losslessly in the plan schema, retain the original records and present a transparent mapping of remaining executable work without fabricating dates, effort or completion evidence or bypassing validation. If material information required for activation is unavailable, return a provisional import or text-only result listing unresolved requirements. Present the normalization mapping and unresolved details, and require explicit candidate approval before activating. Do not restart the preparation period, reintroduce completed learning, recommend new projects for onboarding, reset milestone completion, or automatically trigger presence, market research or unrelated workflows.

## Audit existing plan

Use for `--audit-plan` or read-only roadmap assessment requests. Evaluate alignment with target role, existing preparation and completed milestones, relevance of durable pillars, remaining role-specific capabilities, time and workload feasibility, dependencies, material gaps, risks and unresolved assumptions, and whether remaining work is sufficient for the intended transition. Do not modify the active plan, generate an unsolicited replacement, or activate a revision. Return one disposition: `KEEP`, `KEEP_WITH_OBSERVATIONS`, `REVISION_RECOMMENDED` or `INSUFFICIENT_EVIDENCE`, mapped consistently to existing review contracts. If the plan is sound, explicitly confirm no material change is necessary without forcing criticism. Any recommendation is advisory only; if the candidate explicitly requests a revision afterward, use the versioned proposal and approval process.

## Review / replan

Recover exact active version, progress and last completed review. If scheduled review due or material market claim, assign `career-market-analyst`; use `research` for dated relevant sources and independent source verification. If evidence inaccessible, label insufficient, do not pretend review passed. Candidate-state change alone can justify review without web research. Assign `career-critic` independently as plan analyst; compare no-change option A vs candidate alternative B. Require impact on pillars, dependencies, completed work, hours, deadlines, evidence assets, opportunity cost, risk and fallback. Verify new plan's feasibility and lineage. KEEP if no material change; record review and next due. PROPOSE only for meaningful change; preserve active pointer and existing milestones, retire or amend with explicit rationale. INSUFFICIENT_EVIDENCE: keep active and record follow-up, do not defer overdue review by pretending success.

## Approval and handoff

Use immutable IDs, parent reference and explicit candidate decision identifying exact version. For optional `scripts/career/plan_store.py`, follow documentation; approval record is bookkeeping, not a substitute for actual user authorization. Stale parent requires rebase and renewed approval. Preserve previous versions and progress. Never activate alternative automatically or write in direct mode without authorization.

Deliver: readiness assessment, three layers, milestones and feasibility, review cadence, risk and acceptance, A/B comparison/diff for revision, evidence/source dates, critic findings, approval state and next action.
