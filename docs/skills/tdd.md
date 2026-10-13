# TDD

**Develop through independent behavioral evidence, not self-agreeing tests.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/tdd/SKILL.md) |
| **Best for** | Features, bug fixes, high-risk behavior changes |
| **Execution cost** | Moderate to high; varies by runtime and depth |
| **Output** | Working change plus development, runtime, and adversarial verification evidence |

## The problem

An agent can write an implementation and tests that merely confirm each other. A green test suite might miss real behavior, incorrect assumptions, failure paths, or integration problems.

## When to use it

Use TDD when behavior has an independently knowable expected outcome and you want a test-first development loop. The depth should fit the risk. It is not a generic demand to maximize coverage or write tests for trivial wiring.

## How it works

1. Select one externally meaningful behavior and establish the expected result **before** implementation.
2. Write a relevant test and observe **RED for the intended reason**.
3. Make the smallest correct implementation and reach **GREEN**.
4. Challenge important tests with controlled mutations, alternate oracles, or boundary cases.
5. Verify meaningful behavior through the actual UI, API, CLI, event interface, or library boundary.
6. Run proportionate adversarial and regression checks, then report what was actually verified.

## Modes

| Mode | Intended depth |
| --- | --- |
| Quick | Primary path, meaningful negative path, focused runtime check |
| Standard | Relevant boundaries, state and failure behavior, nearby regressions |
| Hard | Risk-focused attempts to falsify important behavior |

Hard mode is appropriate for issues such as authorization, payments, destructive changes, concurrency, and data integrity. It does not authorize unsafe attacks on production.

## Example request

> Use TDD hard for the idempotent payment endpoint. Derive expected outcomes from the contract, prove red and green, then challenge retries, duplicates, and partial failures in an authorized test environment.

## What you get

Implemented behavior with separate claims for tested, runtime-verified, and adversarially checked work. Failed or unavailable checks remain visible.

## Boundaries and dependencies

TDD can modify application code as authorized. It does not replace an independent [Code Review](code-review.md) or full [Security Audit](security-audit.md). Complex work may use a test ledger; see the [canonical skill](../../skills/tdd/SKILL.md).

**Cost guidance:** Relative resource use reflects development iterations and runtime tests, not a guaranteed token count.
