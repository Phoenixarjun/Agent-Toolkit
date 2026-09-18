---
name: problem-to-solution
description: Orchestrate a problem from initial framing through divergent solution exploration, focused research, pressure-testing, and a decision-ready handoff.
---

# Problem to Solution Workflow

Use when the user wants to move from a real problem toward a researched product or solution direction.

The workflow deliberately spends cheap reasoning breadth before expensive research depth.

## 1. Problem sanity gate

Classify the input:
- observed problem
- symptom
- solution disguised as a problem
- aspiration
- insufficient

Do not continue from a solution label alone.

If material intent is unclear, invoke `grill-me` with the smallest sufficient mode:

- normal ambiguity → `$grill-me`
- time-constrained clarification → `$grill-me fast`
- user-specified budget → `$grill-me <N>`
- concrete solution that needs challenge → `$grill-me hard`
- high-stakes/exhaustive clarification explicitly requested → `$grill-me deep`

GrillMe is conditional, not mandatory.

Do not ask the user for facts that can be discovered from available artifacts or research.

Produce or update a `PROBLEM-BRIEF`.

## 2. Evidence snapshot

Record:
- evidence-backed facts
- assumptions
- unknowns
- hard constraints
- current workaround or status quo
- cost of doing nothing
- who bears the current cost
- who benefits if the problem is solved

This is a confidence map, not exhaustive research.

## 3. Opportunity decomposition

Break the problem into outcomes or opportunity areas without prescribing implementations.

Identify:
- highest-value pain or loss
- controllable areas
- prerequisites
- likely symptoms versus root causes

## 4. Solution-space exploration

Invoke `problem-to-solution`.

Explore broadly without requiring user steering unless a blocker prevents valid exploration.

Keep raw breadth cheap.

Output:
- explored directions
- eliminations
- decision-ready shortlist

## 5. User checkpoint

Present the finalists and their core tradeoffs before expensive research.

The user may:
- choose one finalist to deepen
- request several finalists be researched
- add a preferred candidate
- reject or modify candidates
- request autonomous continuation

A user-supplied candidate remains a candidate, not privileged truth.

If preference conflicts with unresolved material assumptions, use `$grill-me hard` before convergence.

## 6. Targeted research

Research only questions capable of changing the decision.

Select applicable lanes:
- user/problem
- market/alternatives
- business/viability
- technical feasibility
- risk/governance
- delivery/operations

Run independent lanes in parallel when supported and genuinely independent.

Prefer primary evidence.

Keep evidence, inference, assumption, and unknown distinct.

## 7. Feasibility sketch

For each serious finalist, create only enough architecture or operating-model detail to expose feasibility, cost, and critical dependencies.

Capture:
- major components or actors
- hard dependencies
- data and integration requirements
- expensive infrastructure
- critical operational constraints
- credible evolution path

Reuse the existing architect capability when available.

Do not produce final architecture or premature stack selection.

## 8. Assumption attack

For each finalist:
- identify assumptions whose failure would invalidate it
- state current confidence
- state evidence basis
- define the cheapest falsifying experiment

## 9. Pre-mortem

Assume each finalist failed after deployment.

Identify plausible causes from only the relevant perspectives:
- user adoption
- economics
- technology
- operations
- safety/security
- regulation/governance
- organizational change

Do not invent exotic risks for coverage.

## 10. Hybrid check

Only after independent evaluation, test whether finalists contain complementary strengths.

Create a hybrid only when it removes a meaningful weakness without merely combining complexity.

Re-evaluate it as a new candidate.

## 11. Decision synthesis

Produce a `DECISION-BRIEF`.

For every finalist include:
- problem coverage
- key evidence
- tradeoffs
- critical assumptions
- confidence
- major risks
- feasibility summary
- adoption burden
- cheapest next experiment

Do not hide uncertainty behind a single weighted score.

Recommend one option only when evidence materially supports it.

## 12. Handoff

Stop before detailed product architecture or implementation planning.

Make the next action explicit:
- validate the problem further
- run a specific experiment
- deepen one candidate
- make a product decision
- begin detailed architecture
- abandon the problem

## Invariants

- Validate the problem before optimizing a solution.
- Diverge before converging.
- Use GrillMe only when clarification or challenge materially improves the decision.
- Spend tokens after narrowing the search space.
- Prefer simplicity over novelty when outcomes are comparable.
- Keep user preference from becoming confirmation bias.
- Keep evidence traceable to decisions.
- Keep architecture proportional to decision maturity.
