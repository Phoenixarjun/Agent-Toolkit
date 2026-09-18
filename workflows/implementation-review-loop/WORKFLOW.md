---
name: implementation-review-loop
description: Portable workflow for executing an accepted Change Intent Contract or equivalent request through bounded implementation, independent validation, intent-aligned pre-commit review, and at most one focused correction cycle.
version: "1.2.0"
---

# Implementation Review Loop

## Goal

Produce the smallest correct implementation of one selected intent and finish with fresh evidence that the final candidate satisfies it without unauthorized scope drift.

## Entry condition

Use when code must be created, changed, fixed, or completed and the result should be independently validated before commit.

Prefer a ready Change Intent Contract under `.agent-toolkit/intents/`. If no formal contract exists, establish an equivalent using `intent-capture` before implementation.

Do not begin implementation while a material product decision is unresolved.

## Roles

```text
orchestrator  owns intent selection, decomposition, routing, and final decision
scout         gathers repository evidence when needed
builder       implements one bounded write scope
validator     independently tests the final candidate
reviewer      reviews risk-sensitive changes when justified
```

A runtime may combine roles only when independent workers are unavailable. Never claim independent review when the same context performed both implementation and review.

## Stage 1: Lock the intent

Select exactly one intent for the run.

Capture or load:

```text
outcome
stable acceptance criteria
must-preserve constraints
approval boundaries
explicit non-goals
```

A ready intent is normative. The implementation may not rewrite it to fit the code.

If the user materially changes the request during implementation, amend or supersede the intent before continuing.

## Stage 2: Establish repository baseline

Before writes begin, establish enough baseline evidence to distinguish new work from pre-existing dirty state.

Record at minimum:

```text
current commit or candidate identity
initial git status
pre-existing changed paths
```

Do not erase or absorb unrelated user changes. The baseline is execution state, not part of the durable intent contract.

## Stage 3: Discovery

Inspect only enough repository context to establish:

```text
relevant paths
existing behavior
architecture constraints
safe write scope
verification commands
shared-file dependencies
approval-boundary risks
```

Skip a separate discovery role for tiny deterministic changes when the builder can safely establish this context without broadening scope.

## Stage 4: Implementation

Assign one owner to each tracked file for the duration of the run. Parallel writers are allowed only when exact write scopes are disjoint.

The builder must:

- implement the smallest defensible change
- satisfy the selected acceptance criteria
- preserve must-preserve behavior
- stay inside authorized scope
- stop rather than silently cross an approval boundary
- preserve unrelated user changes
- add or update tests when needed
- run focused checks before handoff

Builder completion is not final acceptance.

## Stage 5: Independent validation

Validate the actual final candidate, not a plan or stale diff.

Map each active acceptance criterion to fresh evidence. Also verify must-preserve behavior when affected.

Start with focused checks and widen based on risk.

If the candidate changes after validation, affected evidence becomes stale and must be rerun.

## Stage 6: Intent-aligned code review

Run the `code-review` skill against the selected intent, final candidate identity and boundary, current repository state, and fresh validation evidence.

If several intents are mixed in the worktree and the selected candidate cannot be isolated reliably, do not declare the entire worktree safe to commit.

## Stage 7: Correction

Allow one focused correction cycle by default.

```text
review or validation failure
        -> bounded delta tied to failed AC IDs/findings
        -> original owner fixes
        -> fresh validation
        -> fresh code review
```

Do not restart the whole implementation when a bounded correction is sufficient. Do not loop indefinitely.

## Reviewer trigger

Add a dedicated reviewer when the change materially affects a high-risk domain. See the `code-review` skill's `references/review-risk.md` for domain classification.

## Final states

```text
PASS                candidate satisfies selected intent and is safe to commit
FIX                 one bounded correction remains appropriate
BLOCKED             required evidence, isolation, or safe execution is unavailable
NEEDS_CONFIRMATION  material extra/unrelated scope needs an explicit user decision
NEEDS_USER          the intent itself requires a product decision before execution can continue
```

## Evidence law

Do not treat statements such as `done`, `looks good`, or `tests should pass` as completion evidence.

Final evidence must correspond to the final candidate and selected intent.
