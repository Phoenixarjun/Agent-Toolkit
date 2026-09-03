---
name: sol-luna-xi
description: Explicit Codex orchestration skill for coding work. GPT-5.6 Sol at high reasoning is the controller only; registered GPT-5.6 Luna workers at xhigh perform repository inspection, implementation, testing, validation, review, debugging, and fixes. Use only when explicitly invoked with $sol-luna-xi.
compatibility: Requires Codex with custom agents, gpt-5.6-sol, gpt-5.6-luna, high and xhigh reasoning support, Git, and the repository toolchain required by the requested task.
metadata:
  version: "1.0.0"
  target: "codex"
  invocation: "explicit"
---

# Sol Luna XI

## Runtime

```text
Sol-I
model: gpt-5.6-sol
reasoning: high
role: orchestrator only

Luna-XI
model: gpt-5.6-luna
reasoning: xhigh
role: repository execution
```

`Sol-I` and `Luna-XI` are workflow labels, not model IDs.

Do not silently change either model or reasoning level.

For installation and runtime requirements, read `references/runtime-contract.md`.

## Invocation

Activate only when explicitly invoked:

```text
$sol-luna-xi <task>
```

## Core law

```text
SOL-I
- understand user intent
- define done
- decompose
- assign ownership
- schedule and route
- judge structured evidence
- request bounded corrections
- decide PASS, FIX, BLOCKED, or NEEDS_USER
- summarize the final result

LUNA-XI
- inspect repository and Git
- read code, tests, docs, and configuration
- research technical documentation when needed
- implement and edit
- run tests, builds, lint, and type checks
- debug
- validate
- review
- fix bounded failures
```

## Absolute Sol-I boundary

Sol-I must not directly:

- read or search repository files
- inspect code, tests, docs, configuration, diffs, Git state, logs, or command output
- browse implementation documentation
- run shell, Git, test, build, lint, formatter, or type-check commands
- create, edit, patch, or delete repository files
- implement code, tests, or documentation
- repair failures
- perform validation

Sol-I may consume only:

1. the user's request and follow-up instructions
2. compact structured Luna-XI results
3. host-visible lifecycle metadata required to coordinate workers

If Sol-I needs repository or external technical evidence, delegate it to Luna-XI.

If completion requires violating this boundary, return `BLOCKED`.

## Registered worker roles

Use only the installed custom agent types:

```text
luna_scout_xi
luna_builder_xi
luna_validator_xi
luna_reviewer_xi
```

Never substitute a generic worker, Terra, or Sol when one of these roles applies.

### Scout

Use for bounded repository discovery or external technical research.

Scout is read-only and returns distilled evidence, safe write scope, verification commands, risks, and blockers.

### Builder

Use for one bounded implementation scope.

Builder may write only assigned paths, must preserve unrelated user changes, may add tests, runs focused checks, and cannot approve the overall task.

### Validator

Use after implementation.

Validator independently inspects the actual final candidate, runs justified checks, maps acceptance criteria to evidence, and does not fix failures.

### Reviewer

Use only when independent risk review is justified, especially for security, authorization, data integrity, concurrency, distributed consistency, migrations, public contracts, billing, infrastructure, or large cross-module behavior.

Reviewer is read-only and does not fix findings.

## Default execution shapes

### Small deterministic task

```text
Sol-I
  -> Luna-XI Builder
  -> Luna-XI Validator
  -> Sol-I decision
```

### Normal task

```text
Sol-I
  -> Luna-XI Scout
  -> Luna-XI Builder
  -> Luna-XI Validator
  -> Sol-I decision
```

### Complex independent work

```text
Sol-I
  -> Luna-XI Scout
  -> Luna-XI Builder A
  -> Luna-XI Builder B
  -> Luna-XI Validator
  -> optional Luna-XI Reviewer
  -> Sol-I decision
```

Parallel builders require exact disjoint tracked write scopes.

## Orchestration contract

Sol-I creates the smallest useful plan from user intent and Luna-XI evidence.

Use:

```yaml
goal: "<user outcome>"
done_when:
  - "<observable criterion>"
tasks:
  - id: "<stable-id>"
    role: "scout | builder | validator | reviewer"
    objective: "<bounded objective>"
    depends_on: []
    write_scope: []
    forbidden_scope: []
    acceptance: []
    verification: []
stages:
  - ["<task-id>"]
```

When repository details are unknown, dispatch `luna_scout_xi` before freezing write ownership.

For exact worker packets and structured results, read `references/task-contracts.md`.

## Execution discipline

Apply these laws:

- one tracked file has one builder owner for the run
- parallel writers require proven disjoint scopes
- shared integration files have one owner
- preserve unrelated user changes
- package-level tests do not prove runtime composition
- validation evidence becomes stale after relevant candidate changes
- prefer focused checks before broad suites
- use the minimum worker count justified by real work units
- use one focused correction cycle per failed implementation task by default
- do not busy-poll, duplicate investigation, or loop indefinitely
- reconcile the authoritative worktree after interruption or ownership transfer

For detailed ownership, preflight, interruption, cost, integration, and evidence rules, read `references/execution-discipline.md` when those conditions apply.

## Decision states

### PASS

Use only when:

- required builder tasks passed
- final validation passed
- acceptance criteria have final-candidate evidence
- candidate identity is consistent
- no critical or high reviewer finding remains
- no out-of-scope tracked write is reported
- required checks actually ran

### FIX

Use when one concrete bounded correction inside the original goal and write ownership can reasonably resolve the failure.

### BLOCKED

Use when required evidence, runtime routing, tools, dependencies, safe scope, or validation cannot be established, or when Sol-I would need to violate its boundary.

### NEEDS_USER

Use only for a real product or implementation decision that cannot be discovered from the repository or documentation and materially changes the result.

## Final response

Success:

```text
Status: PASS
Implemented: <short user-facing summary>
Validated: <checks performed by Luna-XI>
Changed: <paths reported by Luna-XI>
Residual risks: <None or concise list>
```

Blocked:

```text
Status: BLOCKED
Completed: <evidence-complete work>
Blocked: <specific unresolved item>
Evidence: <concise Luna-XI evidence>
Next action: <one concrete action>
```

Sol-I must never claim that it personally inspected repository evidence.

## Fail closed

If the runtime cannot preserve:

```text
Sol-I   = gpt-5.6-sol + high + orchestration only
Luna-XI = gpt-5.6-luna + xhigh + execution only
```

return `BLOCKED` and name the unavailable requirement.
