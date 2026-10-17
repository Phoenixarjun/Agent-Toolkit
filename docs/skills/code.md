# Code

**Canonical procedure:** [`skills/code/SKILL.md`](../../skills/code/SKILL.md)

## The problem

Coding agents often jump from a plan directly into multi-file edits, call individual worker reports success, and claim completion without verifying the actual integrated feature. Multiple agents writing in one workspace can overwrite each other's changes or accidentally absorb unrelated user work.

## What `/code` does

`/code` is an **opt-in implementation** capability. The Coordinator locks a concrete authorized outcome, allocates bounded tasks, assigns Builders, safely integrates their code, and uses an independent Verifier plus existing Code Review to check the final integrated candidate.

## When to use

Use when you deliberately want a feature, fix or approved change implemented with task ownership and independent verification. Use `/code-explore` first when the code impact needs substantial investigation, but it is not mandatory. Ordinary coding remains possible without this skill.

## How it works

1. Establish accepted behavior and affected repositories; preserve pre-existing changes.
2. Allocate smallest cohesive write tasks; use parallel Builders only when real isolation is available.
3. Implement the initial feature **without imposing TDD or test-first work**.
4. Integrate the feature.
5. Decide whether to invoke existing TDD guidance for **post-implementation** behavioral, runtime and adversarial testing. This is not retroactive test-driven development.
6. Independently verify the integrated result, execute existing Code Review and report exactly what passed or could not be tested.

## Modes

- `FOCUSED`: Small low-risk change; lean discovery and focused verification.
- `STANDARD`: Normal implementation with acceptance and regression checks.
- `DEEP`: Complex changes with stronger negative, cross-component and runtime verification.

## Example

```text
/code STANDARD
Implement the accepted change described in INT-012.
Allowed repositories: <roots>
Preserve existing authorization and public contracts.
After implementation, decide whether deeper test verification is warranted.
Do not commit, deploy or modify unrelated files.
```

## Outputs and cost

A code diff plus acceptance evidence, changed-path summary, independent verification verdict, relevant executed tests, skipped/blocked checks and remaining risks. `STANDARD` has moderate overhead; `DEEP` may be expensive where real services and multiple agents are justified. Neither mode guarantees a fixed number of agents.

## Boundaries

No automatic commit/deploy, arbitrary refactoring, unsanctioned cleanup, destructive migration or test claims not backed by execution. If genuine independent contexts are absent, report `IMPLEMENTED_UNVERIFIED` or `BLOCKED` instead of a fabricated verified result.

## Related owners

Existing `skills/tdd/`, `skills/code-review/`, `rules/global/engineering-rules.md`, `knowledge/engineering/solution-design-principles.md`, and `workflows/implementation-review-loop/WORKFLOW.md` remain authoritative for their respective responsibilities.
