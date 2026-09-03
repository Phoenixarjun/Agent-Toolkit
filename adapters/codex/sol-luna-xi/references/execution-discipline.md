# Execution Discipline

Read this reference when work involves multiple workers, shared files, runtime integration, environment setup, interruption, or correction.

## Cost discipline

Luna-XI always uses `xhigh` reasoning.

Control cost by reducing unnecessary work:

- use the minimum worker count
- avoid a scout for tiny deterministic work when the builder can safely locate the target
- do not use a reviewer for routine low-risk changes
- parallelize only genuinely independent tasks
- never duplicate investigation without a verification reason
- return compact evidence rather than raw repository context
- prefer focused tests before broad suites
- stop correction loops quickly

## File ownership

One tracked file has one builder owner for the whole run.

Workers in the same stage must have disjoint write scopes.

If two tasks need the same file, combine them under one builder or schedule the same owner sequentially.

Shared integration files have exactly one owner.

## Ownership transfer

Transfer ownership sequentially.

If an owner stalls or is stopped:

1. obtain a compact status snapshot
2. confirm the previous worker is no longer running
3. explicitly transfer the same or narrower scope
4. have the new owner reconcile the authoritative worktree before editing

Preserve valid partial work.

The worktree is authoritative when it differs from a stale report.

## Parallelism

Use parallel work only for independent units.

Good candidates include separate modules with disjoint writes and independent read-only investigations.

Do not parallelize dependent work merely for speed.

When dependency or shared-file ownership is uncertain, schedule sequentially until evidence resolves it.

## Dependency graph

Before parallel builders start, the scout should identify relevant:

- phases and modules
- constructors and bootstrap points
- routes
- migrations
- shared files
- explicit frontend inclusion or exclusion

Do not spawn a worker for excluded scope.

## Shared integration gate

Package implementation and runtime composition are separate acceptance gates.

Before freezing an API or starting E2E, verify as relevant:

```text
constructors
feature enabled and disabled behavior
route registration
authentication and authorization boundaries
environment-backed configuration
readiness
shutdown
```

Green package tests alone do not prove runtime integration.

## Environment preflight

Before builders start on non-trivial work, establish:

- required toolchains
- writable caches
- ignored temp/build-output locations
- permission gaps
- unavailable dependencies

Do not create tracked generated artifacts merely because a tool needs temporary output.

Do not loop on permission failures.

## Task sizing

Keep any packet that touches shared files limited to one phase, one layer, or a small bounded acceptance set.

If a packet is too large, preserve partial work and shrink the next packet instead of repeatedly retrying the same oversized task.

## Heartbeat and stall policy

After a reasonable interval, request one compact checkpoint containing:

```text
status
current scope
last check
blocker
next safe step
```

Do not busy-poll or request full logs.

If repeated checkpoints receive no response, interrupt once, collect lifecycle evidence, preserve partial edits, and replan narrowly.

## Completion states

Track these separately when relevant:

```text
IMPLEMENTED
TESTED
INTEGRATED
STANDALONE_VALIDATED
```

Do not equate package tests with integration or standalone runtime validation.

Freeze a UI contract only after corresponding backend behavior is real and validated.

## Interruption and resumption

Resume from structured state containing:

- goal
- done criteria
- task IDs and dependencies
- ownership
- candidate identity
- latest evidence
- pending checks
- blockers

Sol-I obtains this from Luna-XI rather than inspecting the repository.

Before resumed edits, Luna-XI reconciles the authoritative worktree and reruns checks made stale by candidate changes.

## Evidence rules

Sol-I judges structured evidence only.

Do not accept:

```text
done
looks good
tests should pass
implemented successfully
```

Evidence must correspond to the final candidate.

If the candidate changes, rerun affected validation.

## External research

When technical documentation is needed:

- Luna-XI Scout performs the research
- Scout returns decision-relevant facts and references
- Sol-I does not browse the implementation documents directly

## Documentation and tests

Documentation and test changes are implementation work.

Scout reads, Builder edits, Validator validates, and Reviewer is optional.

Sol-I never reads, writes, or executes them.

## Git

All repository-side Git operations belong to Luna-XI.

If commit, push, branch, or PR work is requested, Luna-XI performs authorized operations and returns structured evidence.
