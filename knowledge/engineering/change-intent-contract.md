# Change Intent Contract

A Change Intent Contract is the durable statement of what a coding change is authorized to accomplish.

It exists to prevent two common agent failures:

1. incomplete implementation that still looks plausible
2. implementation drift into behavior the user never authorized

## Contract boundary

The contract owns:

```text
desired outcome
observable acceptance
scope
must-preserve behavior
constraints
quality constraints
approval boundaries
non-goals
material decisions
```

The contract does not own:

```text
file-by-file implementation plans
agent assignments
session transcripts
worker logs
model choices
temporary checkpoints
raw test output
```

Those are execution state.

## Source of truth

A ready contract is normative for the current change until the user or an authoritative upstream source amends or supersedes it.

Code is never evidence that the contract should be weakened.

Repository structure can inform implementation, but it cannot silently redefine user intent.

## Readiness levels

### Direct

The outcome and material boundaries are already clear.

### Clarification required

The user knows the outcome, but a small number of material choices remain unresolved.

Ask only questions that can change what should be built or accepted.

### Discovery required

The user has named a broad product or idea but has not defined a sufficiently concrete outcome.

Do not manufacture requirements. Route to a discovery/interview capability before implementation.

## Acceptance design

Acceptance criteria should be:

```text
observable
independent enough to review
stable enough to reference later
specific without prescribing unnecessary implementation
```

Stable IDs create traceability:

```text
Intent AC -> changed behavior -> validation evidence -> review decision
```

The review may map several changed paths to one criterion or one path to several criteria. The contract should not predict file ownership.

## Scope taxonomy for review

A changed path or behavior can be classified as:

### REQUIRED

Directly implements an acceptance criterion or explicitly in-scope behavior.

### SUPPORTING

Not explicitly requested but genuinely necessary to make the requested behavior correct, testable, buildable, or safely integrated.

### BENIGN_EXTRA

A small, local, reversible addition that is related to the requested work and does not materially alter behavior, contracts, data, security, dependencies, configuration, architecture, operations, or user scope.

It must be disclosed but need not block commit by itself.

### MATERIAL_EXTRA

Unrequested work that changes externally meaningful behavior or system commitments, including new side effects, persistence behavior, dependencies, APIs, schema, security behavior, configuration, infrastructure, or substantial UX scope.

It requires explicit user acceptance, separation, or removal.

### UNRELATED

No defensible relationship to the active intent.

It should not ride with the candidate merely because it was convenient to change.

### UNCLEAR

Available evidence cannot establish why the change exists or whether it belongs to the intent.

Do not guess attribution.

## Multiple intents

One worktree may contain several valid changes.

A review must identify the intent being judged and the candidate attributable to it.

If multiple intents are mixed and cannot be separated confidently from repository evidence, staging state, or explicit user attribution, the reviewer must not claim the whole worktree is safe to commit as one intent.

## Existing dirty state

Intent alignment and authorship are different questions.

A file may be out of scope for the active intent without having been changed by the current agent.

Never attribute dirty work to an agent without a reliable baseline.

## Amendments

Small clarifications can revise the same intent.

Do not renumber existing acceptance IDs. Increment the revision and record the user-authorized change.

Use a new intent with `supersedes` when the goal has materially changed into a different task.

## Approval boundaries

An implementation may discover that a requested outcome appears to require a new side effect or contract change.

That discovery does not grant authority to perform it.

When a required implementation crosses an approval boundary, stop and surface the decision instead of reclassifying it as supporting work.

## Completion

A contract is not proof that the change is complete.

Completion requires fresh evidence against the final candidate.

If the final candidate changes, affected evidence must be rerun.
