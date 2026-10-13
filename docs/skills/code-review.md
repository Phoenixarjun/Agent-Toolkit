# Code Review

**Decide whether a change is faithful, correct, and ready to commit.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/code-review/SKILL.md) |
| **Best for** | Pre-commit review of staged, unstaged, and relevant untracked changes |
| **Execution cost** | Moderate; increases with change size and test cost |
| **Output** | Evidence-backed findings, requirement coverage, commit readiness decision |

## The problem

A code diff can look reasonable while omitting requirements, including unrelated changes, or breaking contracts and edge cases. Reviewing only the staged lines or treating style preferences as defects misses the real risks.

## When to use it

Use after implementation and before commit when the review needs to judge the *complete candidate change* against the original intent. It is not a substitute for implementing the change or running a full security assessment.

## How it works

1. Reconstruct the user request and any acceptance criteria.
2. Inspect Git state, including staged, unstaged, and relevant untracked changes.
3. Evaluate each intended outcome and identify scope drift.
4. Examine correctness, error paths, security, data integrity, compatibility, and relevant architectural effects.
5. Verify claims using available checks and return actionable findings with evidence.

## Review behavior

The reviewer prioritizes material problems over cosmetic changes. A finding should point to an actual failure scenario or violated contract. If evidence is insufficient to make a safe commit decision, the review should say so.

## Example request

> Review the complete working tree before commit. Check the invoice-export change against the agreed requirements and tell me what blocks committing.

## What you get

A decision-oriented review: acceptance coverage, concrete findings, risks, verification results, and a bounded correction request when needed. An empty findings section must not be manufactured into a list of style complaints.

## Boundaries and dependencies

Code Review is **review-only** under the provided implementation: it does not edit, delete, reset, or commit code. Actual validation depends on the repository toolchain. Pair it with [TDD](tdd.md) for development proof, and use [Security Audit](security-audit.md) for dedicated independent security assurance.

**Cost guidance:** Relative only, not a measured token or compute estimate. Read the [canonical skill](../../skills/code-review/SKILL.md) for status vocabulary and exact decision rules.
