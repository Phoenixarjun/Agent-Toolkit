# Intent Capture

**Preserve the intended change as an explicit acceptance contract.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/intent-capture/SKILL.md) |
| **Best for** | Nontrivial changes that must survive handoffs and reviews |
| **Interaction cost** | Low to moderate |
| **Output** | A project-local Change Intent Contract, when authorized |

## The problem

A coding agent may implement something plausible but different from what the user meant. In a long or multi-session task, requirements, exclusions, and acceptance criteria can also drift or disappear.

## When to use it

Use Intent Capture when the requested change is clear enough to specify and needs a durable agreement before implementation. Use ordinary conversation for trivial changes. If the goal itself remains unclear, resolve discovery first rather than inventing a specification.

## How it works

1. Classify the request as ready, needing clarification, or needing discovery.
2. Recover the desired outcome, constraints, scope, must-preserve behavior, and approval boundaries.
3. Convert requirements into **observable acceptance criteria** with stable IDs.
4. Identify unresolved decisions without pretending they are settled.
5. Persist the contract only in the authorized project location.

## Readiness states

| State | Meaning |
| --- | --- |
| Direct | Material outcomes and boundaries are clear enough to document |
| Needs clarification | A decision that affects the change is missing |
| Needs discovery | The actual desired outcome is not yet established |

## Example request

> Capture the intent for adding invoice exports. Preserve existing authorization and CSV compatibility. Define acceptance criteria before coding.

## What you get

A reviewable contract identifying *what must become true* and *what must not change*. It is not a file-by-file implementation plan or an authorization to begin coding automatically.

## Boundaries and dependencies

The skill may inspect project context. Writing to the target project's intent directory requires permission. It must not invent product decisions, store secrets, or edit accepted criteria retroactively to match an incorrect implementation. Use [Grill Me](grill-me.md) if important choices need to be resolved.

**Cost guidance:** Qualitative only. See the [canonical skill](../../skills/intent-capture/SKILL.md) for the contract schema and persistence behavior.
