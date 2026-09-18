---
name: problem-to-solution
description: Turn a sufficiently understood problem into a small set of materially different, evidence-aware solution directions before committing to one. Use when the user wants to explore how a problem could be solved, compare approaches, avoid premature solution lock-in, or narrow a problem into decision-ready options.
---

# Problem to Solution

Move from a real problem to a decision-ready set of solution directions without prematurely committing to architecture, technology, or the user's first idea.

## Entry Gate

Start by determining whether the problem is understood well enough to explore.

Require enough clarity on:
- who or what is affected
- the undesirable current condition
- why it matters
- the desired outcome
- known hard constraints

If a material gap would change the solution space, use `grill-me` rather than inventing the missing intent.

Use GrillMe selectively:
- `$grill-me` for normal ambiguity
- `$grill-me fast` when time is constrained and only the highest-impact gaps matter
- `$grill-me <N>` when the user gives a question budget
- `$grill-me hard` when a concrete proposed solution needs pressure-testing
- `$grill-me deep` only when the user explicitly wants exhaustive clarification or the decision is high-stakes enough to justify it

Do not invoke GrillMe when the missing information is discoverable from available evidence.

## Procedure

### 1. Anchor the problem

Restate the problem without embedding a preferred solution.

Separate:
- facts
- assumptions
- unknowns
- hard constraints

Treat any user-proposed solution as a candidate, not as the destination.

### 2. Decompose the opportunity

Identify the important outcomes, bottlenecks, or opportunity areas inside the problem.

Distinguish root causes from symptoms where evidence permits.

Do not prescribe implementations yet.

### 3. Diverge by mechanism

Explore materially different ways to change the current condition.

Seek different mechanisms, not cosmetic variants.

Applicable mechanisms may include:
- process or operational change
- simplification of the current system
- software
- automation
- hardware or physical infrastructure
- behavior or incentives
- policy or governance
- platform or marketplace
- hybrid approaches

Do not force every category to appear.

Include the status quo or incremental improvement when it is a credible option.

### 4. Normalize candidates

For each serious candidate, capture:
- mechanism
- problem coverage
- key dependencies
- major assumptions
- adoption burden
- major cost or complexity drivers
- principal failure mode
- cheapest useful experiment

Keep this lightweight. Do not design final architecture or select detailed technologies.

### 5. Hard-filter invalid paths

Reject a candidate only when available evidence shows that it:
- does not materially solve the problem
- violates a fixed constraint
- depends on unavailable capability or infrastructure
- creates an unacceptable legal, regulatory, safety, or operational condition
- has no credible adoption path

Record the reason. Do not hide eliminations behind scores.

### 6. Compare survivors

Choose comparison dimensions from the actual problem.

Typical dimensions:
- problem coverage
- simplicity
- time-to-value
- implementation and operating cost
- adoption friction
- feasibility
- reliability
- security or privacy
- maintainability
- reversibility
- scalability
- experimentability

Do not treat novelty as value by itself.

Prefer qualitative assessment with confidence and basis over unsupported numeric scoring.

### 7. Shortlist

Return the smallest set that preserves the meaningful trade space, usually 2-4 candidates.

Do not force exactly three.

If a user strongly prefers one candidate but consequential assumptions remain, use `$grill-me hard` before allowing preference to collapse the exploration.

### 8. Consider hybrids

Only after independent evaluation, consider whether finalists contain complementary strengths.

Create a hybrid only when it removes a meaningful weakness without merely combining complexity.

Evaluate the hybrid as a new candidate.

## Invariants

- Diverge before converging.
- Prefer the simplest solution that sufficiently solves the problem under real constraints.
- Do not privilege the user's initial solution.
- Do not deep-research every raw direction.
- Do not choose technologies before requirements justify them.
- Do not turn exploration into final architecture.
- Keep facts, assumptions, and unknowns distinct.
- Preserve uncertainty when evidence is weak.
- Spend depth after narrowing the search space.

## Completion

Finish when:
- the problem is sufficiently understood
- the major solution mechanisms have been explored
- invalid paths have explicit elimination reasons
- survivors represent materially different tradeoffs
- important assumptions and uncertainty remain visible
- the next research or decision step is clear

Return:
- problem anchor
- opportunity breakdown
- explored directions
- eliminated directions with reasons
- shortlist
- tradeoffs and confidence
- assumptions and unknowns
- cheapest useful experiment for each finalist
- recommended next step

Read `references/exploration-lenses.md` only when the solution space is narrow, repetitive, or difficult to evaluate.
