---
name: implementation-review-loop
description: Portable workflow for turning an implementation request into a bounded change, independent validation, intent-aligned pre-commit review, and at most one focused correction cycle.
version: "1.0.0"
---

# Implementation Review Loop

## Goal

Produce the smallest correct implementation of the user's request and finish with evidence that the final candidate satisfies the original intent.

## Entry condition

Use when code must be created, changed, fixed, or completed and the result should be independently validated before commit.

## Roles

```text
orchestrator  owns intent, decomposition, routing, and final decision
scout         gathers repository evidence when needed
builder       implements one bounded write scope
validator     independently tests the final candidate
reviewer      reviews risk-sensitive changes when justified
```

A runtime may combine roles only when it cannot provide independent workers. Never pretend independence exists when it does not.

## Stage 1: Intent contract

Convert the user request into:

```text
goal
observable acceptance criteria
must-preserve constraints
explicit non-goals
```

Do not add speculative requirements.

## Stage 2: Discovery

Inspect only enough repository context to establish:

```text
relevant paths
existing behavior
architecture constraints
safe write scope
verification commands
shared-file dependencies
```

Skip a separate discovery role for tiny deterministic changes when the builder can safely establish this context without broadening scope.

## Stage 3: Implementation

Assign one owner to each tracked file for the duration of the run.

Parallel writers are allowed only when exact write scopes are disjoint.

The builder must:

- implement the smallest defensible change
- preserve unrelated user changes
- stay inside the assigned scope
- add or update tests when needed
- run focused checks before handing off

Builder completion is not final acceptance.

## Stage 4: Independent validation

Validate the actual final candidate, not a plan or stale diff.

Map every acceptance criterion to evidence.

Start with focused checks and widen based on risk.

If the candidate changes after validation, affected validation is stale and must be rerun.

## Stage 5: Pre-commit review

Run the canonical `code-review` skill against the final candidate and the original intent.

The review must check:

- intent coverage
- complete Git change scope
- extra or unexplained changes
- correctness and regression risk
- relevant validation evidence

## Stage 6: Correction

Allow one focused correction cycle by default.

```text
review or validation failure
        -> bounded delta
        -> original owner fixes
        -> fresh validation
        -> fresh code review
```

Do not restart the whole implementation when a bounded correction is sufficient.

Do not loop indefinitely.

## Reviewer trigger

Add a dedicated reviewer when the change materially affects:

```text
authentication or authorization
security boundaries
data integrity
concurrency
distributed consistency
migrations
public API compatibility
billing or payments
infrastructure
shared contracts
large cross-module behavior
```

## Final states

```text
PASS        implementation and final evidence satisfy intent
FIX         one bounded correction remains appropriate
BLOCKED     required evidence or safe execution is unavailable
NEEDS_USER  a real product decision cannot be inferred safely
```

## Evidence law

Do not treat statements such as `done`, `looks good`, or `tests should pass` as completion evidence.

Final evidence must correspond to the final candidate.
