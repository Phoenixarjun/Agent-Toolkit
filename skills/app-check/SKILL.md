---
name: app-check
description: Assess an existing application's present engineering health and next justified actions. Inspect what the application actually does, select only relevant risk surfaces, ground findings in source and operational evidence, ask up to eight consequential user-owned questions, and return a prioritized read-only health report. Do not use for implementing fixes, generic code review, or a standalone security audit.
compatibility: Requires authorized repository read access. Diagnostics and independent subagents are optional and must be truthfully reported. Companion workflow, report template, and validation script enhance reproducibility but are not prerequisites for a useful limited assessment.
metadata:
  version: "1.0.0"
  maturity: "experimental"
  category: "engineering"
---

# Application Health Check

## Purpose and authority

Answer **"Given what this application is, what deserves attention now, what can wait, and why?"** Use the **smallest evidence-justified intervention**. The assessed system, not a generic production-readiness checklist, determines applicability.

Invoke explicitly for application health, bug/risk triage, engineering readiness, or prioritizing the next changes. Do not activate automatically for every coding request. Scope can be a bounded feature, application, or authorized group of services. Assessment is read-only: no product-code edits, dependency upgrades, test creation, migrations, restarts, production load, or external side effects. Only run diagnostics that are permitted, safe for the specified environment, and whose effects are understood.

## 1. Establish the application reality before choosing checks

Identify from available evidence: actual user journeys, process type and architecture, where state lives, persistence and network boundaries, deployment topology, usage stage, known failure symptoms, current test/observability surfaces, workload/resource limits when known, and inspected repository revisions and dirty state. Distinguish currently deployed behavior from dormant code and intended future architecture. Read the smallest relevant files first: entrypoints, data paths, configuration, tests, existing requirements/architecture records, metrics, incidents. Do not request facts already discoverable.

Classify every candidate concern as `APPLICABLE`, `CONDITIONAL`, or `NOT_APPLICABLE` with a one-line reason. **A concern becomes applicable because the system has the relevant behavior, resource, failure boundary, or user requirement**, not because its technology name appears in a checklist. A state-only local application must not acquire distributed persistence, idempotency, cache TTL, load-balancer, or production SLO findings in the absence of those actual responsibilities. Conversely, a simple system with a reproduced critical defect must not be dismissed merely because it is small.

Do not run all investigative lenses by default. Select only implicated concerns from correctness/user journeys, data lifecycle, resource lifecycle, performance/capacity, reliability/recovery, test validity, operations, and architectural friction. Security auditing belongs to its separate skill; surface an observed severe concern with its evidence and scope, and recommend a dedicated audit when appropriate.

## 2. Resolve decision-changing external uncertainty

Determine which missing facts are both **owned by the user/stakeholder** and likely to alter a concrete recommendation. Ask **zero to eight questions total**, as few as necessary; do not treat five or eight as a quota. Prioritize current/forecast peak load and shape, user-critical actions, persistence/loss tolerance, uptime/latency expectations, rollout or growth evidence, and constraints only when applicable. Discover code and deployed configuration instead of asking the creator to describe them.

For each selected question, state the decision it unlocks and accept ranges or "unknown." Ask one focused question at a time when interactive; for batch/automated runs, surface up to eight prioritized unanswered questions with conditional recommendations instead of blocking all analysis. Optionally reuse Grill Me's neutral decision questioning, but **retain this skill's question budget and assessment ownership**. Challenge unsupported forecasts by requesting their basis, not by demanding impossible certainty. Label numbers `MEASURED`, `FORECAST_WITH_BASIS`, `HYPOTHETICAL`, or `UNKNOWN`; never convert daily users to peak RPS or concurrency without workload evidence.

If missing information could reverse a material recommendation, make that decision `CONDITIONAL` or `UNRESOLVED`; do not fill the gap with a confident assumption.

## 3. Investigate proportionately

Start with cheap, goal-relevant source and test inspection. Follow suspicious behavior through only the required callers, effects, lifecycle, and test or runtime boundaries. Deep trace a material uncertain dependency via Code Explore **only when needed**, never as an automatic prerequisite or full-system inventory. Consult TDD's test-quality/runtime references to assess whether existing tests prove behavior; an `assert true`, success-only mock, or line-coverage percentage is not itself proof. Do not claim test-first development occurred or create tests without approval.

For a suspected defect, seek a specific triggering condition, affected behavior, and reproducible or directly demonstrated evidence. For a suspected resource leak, distinguish bounded retention from actual unbounded growth and require suitable lifecycle or diagnostic evidence before declaring a **confirmed memory leak**. For performance or capacity, treat static code patterns as risk hypotheses until supported by measurements or workload-specific experiments. Use production data only through authorized, appropriately protected access and do not expose secrets or personal data in reports.

If genuine isolated agents are available and separate investigations promise useful coverage, use `workflows/application-health-assessment/WORKFLOW.md`. Delegate different material questions, then independently verify consequential findings. If subagents are unavailable or would add no value, perform one bounded assessment, explicitly label verification as `SELF_CHECKED` or `NOT_VERIFIED`, and never fabricate independent review. There is no minimum agent count.

## 4. Challenge every proposed finding

For each material claim, require exact applicable source/revision or runtime artifact, cause or triggering condition, current user/business impact, evidence type, and what remains unproven. Classify as `CONFIRMED_DEFECT`, `SUPPORTED_RISK`, `HYPOTHESIS`, or `OPPORTUNITY`; assign priority separately based on **current impact, likelihood, affected critical journey, and cost of deferral**, not on architectural fashion. Reserve P0 for substantiated currently critical impact; do not mark hypothetical traffic or an unmeasured cache pattern P0. De-duplicate multiple paths to one root cause.

Before recommending change, apply the counterfactual: **"What happens if we leave this as it is given the evidenced present and credible near-term demand?"** Prefer keeping the current design or a local, reversible correction over new services, queues, replicas, caching, sharding, observability stacks, or abstractions unless a specific bottleneck or requirement justifies the added operational burden. Classify actions `NOW`, `NEXT`, `DEFER`, or `NO_CHANGE`; show why more complex alternatives were rejected only when seriously considered.

Load [evidence-and-prioritization.md](references/evidence-and-prioritization.md) if severity, measurement provenance, confidence, or disputed prioritization requires more detail.

## 5. Produce one decision-ready report and stop

Use `templates/APP-HEALTH-REPORT.md` or equivalent with:

- Scope and evidence provenance; verified coverage, excluded surfaces, unknown runtime properties.
- Executive judgment on current fitness **for the known purpose**, never an invented numeric health score.
- What is working and not worth changing.
- Up to five distinct priority actions, each with impact, evidence, smallest corrective move, how to verify, and cost/complexity; keep other material findings in the detailed section, even when several are critical.
- Detailed actionable findings, their confidence and status, and relevant exact locations.
- Decision-changing unanswered questions (maximum eight across the assessment), deferred opportunities and no-change calls.
- Observed versus unmeasured capacity; assessment limitations and whether verification was truly independent.

Do not claim "no bugs," production readiness, maximum supported load, memory leak, or successful tests without sufficient current evidence. If there are no substantiated material issues, report **"No material issues identified in the examined scope"** plus coverage limitations and explicitly recommend no extra engineering. A single useful finding may be the complete outcome.

When a structured evidence ledger is produced, optionally validate it with `scripts/validate_app_check.py`. A passing structural validation does not verify engineering truth. Never require a ledger to answer a small assessment. Route an approved change to `/code`; request `/code-explore` only when deeper implementation impact is unknown. Do not fix issues within this assessment.

## Outcomes

`SUFFICIENT`: relevant requested scope was examined with evidence and material claims assessed; does **not** mean the whole application is universally healthy. `LIMITED`: some useful evidence but missing significant runtime, external, or independent verification. `BLOCKED`: permissions or essential system identity prevent a defensible assessment. Distinguish these from application health itself. Stop once the likely next engineering decisions are grounded, not once every possible concern has been cataloged.
