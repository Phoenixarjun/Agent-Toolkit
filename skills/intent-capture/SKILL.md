---
name: intent-capture
description: Converts a sufficiently understood coding request into a durable project-local Change Intent Contract with stable acceptance criteria, scope boundaries, constraints, approval boundaries, and unresolved decisions. Use before implementation when the requested change must survive session resets or be reviewed later against exact user intent.
compatibility: Requires permission to inspect the current request and, when persisting the contract, write to the target project's .agent-toolkit/intents directory.
metadata:
  version: "1.0.0"
  category: "intent"
  stage: "pre-implementation"
---

# Intent Capture

## Purpose

Turn an implementation request into a small, durable contract that states what must become true, what must remain unchanged, and what is outside the change.

The contract is the source of truth for implementation and later review. It is not an implementation plan.

## Non-goals

Do not:

- design architecture unless a design decision is required to define the requested outcome
- choose files, classes, libraries, or implementation details merely to make the contract look complete
- invent requirements the user did not state or authorize
- silently resolve material product decisions
- start implementation
- rewrite an accepted contract to match code that already exists
- store temporary worker, session, or model state in the contract
- store credentials, secrets, tokens, or unnecessary sensitive data in the contract

## 1. Classify request readiness

Classify the request before creating a ready contract.

### DIRECT

The desired outcome, material boundaries, and observable completion conditions are clear enough to execute without guessing.

Proceed to contract synthesis.

### CLARIFY

The user knows the desired outcome, but one or more material choices are missing or ambiguous.

Ask only questions whose answers could materially change scope, behavior, acceptance, compatibility, security, data handling, or user experience.

Do not ask for details that can safely be discovered from the repository or chosen as a reversible implementation detail.

Return `NEEDS_CLARIFICATION` until those decisions are resolved.

### DISCOVERY

The desired outcome itself is not sufficiently defined. Examples include requests that name only a broad product or category without a clear user, job, or result.

Do not fabricate a specification.

Return `NEEDS_DISCOVERY` and identify the minimum topics a future discovery/interview capability must resolve.

## 2. Recover the actual intent

Extract only decision-relevant information:

```text
outcome
in-scope behavior
observable acceptance criteria
must-preserve behavior
constraints
quality constraints when material
approval boundaries
out-of-scope work
assumptions
open decisions
source references when available
```

Separate user requirements from implementation inference.

If repository inspection can answer a technical question without changing the product decision, do not ask the user merely to fill the contract.

## 3. Build acceptance criteria

Acceptance criteria describe observable truth, not implementation activity.

Good criteria answer:

```text
What must a user, caller, test, operator, or reviewer be able to observe when this change is correct?
```

Assign stable IDs:

```text
AC-001
AC-002
AC-003
```

For each criterion include the evidence expected to prove it.

Do not use criteria such as:

```text
write clean code
follow best practices
update files
implement feature
make it production ready
```

unless the request defines an observable meaning for them.

Once assigned, do not renumber existing acceptance IDs during later amendments.

## 4. Establish scope boundaries

### In Scope

List requested behavior and directly authorized outcomes.

### Must Preserve

List behavior, contracts, data, APIs, compatibility, or user flows that must not regress.

### Out of Scope

Record tempting adjacent work that should not be pulled into this change.

Do not turn `Out of Scope` into an exhaustive list of the entire system.

## 5. Record constraints and approval boundaries

Constraints are requirements that limit valid solutions.

Examples include compatibility, technology, performance, accessibility, security, deployment, or dependency constraints when the user or project makes them material.

Approval boundaries identify side effects that must not be introduced implicitly. Capture them when relevant, including:

```text
destructive operations
data or schema migrations
new external side effects
new dependencies
public API or contract changes
authentication or authorization changes
production configuration changes
cost-bearing infrastructure changes
```

`None` is valid when no special approval boundary exists.

## 6. Handle assumptions correctly

A low-risk reversible assumption may be recorded explicitly.

A material assumption that could change the product outcome, scope, data behavior, security posture, external contract, or acceptance criteria is not an assumption the agent may silently make. It is an open decision.

A contract cannot become `ready` while a material open decision remains unresolved.

## 7. Preserve contract authority

A `ready` contract represents accepted intent.

Implementation evidence must never be used to silently weaken, remove, or reinterpret its requirements.

When the user changes the request:

- preserve existing acceptance IDs
- increment `revision`
- record the change under Amendments
- add new acceptance IDs instead of renumbering old ones
- explicitly mark requirements withdrawn by the user

Create a new intent and use `supersedes` when the desired outcome has become a materially different task rather than an amendment of the same change.

Only explicit user direction or an authoritative upstream specification may change accepted intent.

## 8. Persist the contract

Canonical target-project location:

```text
.agent-toolkit/intents/
```

Canonical filename:

```text
INT-YYYYMMDD-NNN-short-slug.md
```

Prefer the deterministic repository helper when available:

```text
python scripts/new_intent.py --root <target-project> --title "<title>" --source <source>
```

Do not place canonical intent under `.claude/`, `.codex/`, `.cursor/`, or another vendor directory.

Temporary session state belongs elsewhere and must not be mixed into the durable intent contract.

## 9. Validate readiness

Before declaring the contract ready, verify:

- one clear outcome exists
- every acceptance criterion is observable and uniquely identified
- must-preserve behavior is explicit
- constraints do not contain hidden implementation guesses
- approval boundaries are explicit when material
- out-of-scope work is clear enough to prevent obvious scope creep
- material assumptions have been resolved
- open decisions are empty
- no placeholder content remains

Use the deterministic validator when available:

```text
python scripts/validate_intent.py <intent-file> --strict
```

## Output contract

Use exactly one status.

### READY

The contract is executable without a material product guess.

```text
Status: READY
Intent: <ID + revision + title>
Outcome: <one sentence>
Acceptance: <count>
Boundaries: <short summary>
Open decisions: None
Path: <persisted path or Not persisted>
```

### NEEDS_CLARIFICATION

The outcome is understood but one or more material decisions must be answered.

```text
Status: NEEDS_CLARIFICATION
Known outcome: <one sentence>
Questions:
- <only material question>
Reason: <what decision the answer changes>
```

### NEEDS_DISCOVERY

The request is too broad to form an honest executable contract.

```text
Status: NEEDS_DISCOVERY
Known intent: <what is actually known>
Discovery needed:
- <minimum topic>
Do not implement yet.
```

### BLOCKED

Required source information, project access, or persistence capability is unavailable and prevents a reliable contract.

Do not claim a contract is ready merely because a template was filled.
