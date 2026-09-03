---
name: code-review
description: Reviews repository changes before commit by reconstructing the user's implementation intent, inspecting the complete Git change set, checking requirement coverage and scope drift, assessing correctness and maintainability, and validating relevant checks. Use after code has been changed and before committing when a commit/no-commit decision is needed.
compatibility: Requires a Git repository and access to inspect changed files. Running tests, builds, lint, or type checks requires the repository toolchain.
metadata:
  version: "1.0.0"
  category: "quality"
  stage: "pre-commit"
---

# Code Review

## Purpose

Decide whether the current repository changes faithfully implement the user's intent and are safe to commit.

This is a review gate, not an implementation pass.

## Non-goals

While reviewing, do not:

- edit source files
- fix findings
- commit, reset, clean, stash, checkout, or discard changes
- broaden the requested feature
- invent new requirements
- report style preferences as defects unless they violate an explicit rule or materially harm maintainability

If fixes are required, return a bounded correction prompt instead of changing the code.

## 1. Establish the intent contract

Use this priority:

1. the user's implementation request and follow-up constraints
2. an explicitly supplied task, issue, plan, or acceptance criteria
3. repository evidence only when the original request is unavailable

Convert the intent into a compact checklist of observable outcomes.

For each item capture:

```text
ID
Requirement
Expected observable result
Must preserve
```

Do not add requirements merely because they would be nice to have.

If intent cannot be established confidently enough to judge the change, return `BLOCKED`.

## 2. Establish the complete candidate

Inspect the repository state before judging individual files.

Use Git or equivalent host operations to inspect:

```text
git status --short
git diff --stat
git diff
git diff --cached
git ls-files --others --exclude-standard
```

When needed, compare tracked changes against `HEAD` and inspect relevant untracked files.

Review staged, unstaged, and relevant untracked changes. Do not assume the staged diff is the whole candidate.

Inspect enough unchanged surrounding code, tests, contracts, configuration, and callers to understand the effect of each change.

For every changed path classify its reason as:

```text
required       directly implements an intent item
supporting     necessary to make the requested change correct
extra          not required by the stated intent
unclear        attribution or necessity cannot be established
```

Do not claim that an existing dirty change was created by the current implementation unless evidence establishes that attribution.

## 3. Verify intent coverage

Evaluate every intent item independently.

Use exactly:

```text
PASS       fully implemented with evidence
PARTIAL    some required behavior exists but the item is incomplete
FAIL       required behavior is missing or contradicted
UNKNOWN    evidence is insufficient
```

Evidence should point to concrete paths, symbols, behavior, or test results.

A summary such as "feature implemented" is not evidence.

## 4. Review the implementation

Review only dimensions relevant to the candidate.

Prioritize:

- behavioral correctness
- edge cases and error paths
- input validation
- security and authorization
- data integrity
- concurrency or ordering when relevant
- API, schema, and compatibility impact
- failure handling and cleanup
- consistency with existing architecture
- modularity and separation of responsibilities
- tests for changed behavior
- accidental duplication
- scope drift

For modularity, reject obvious responsibility dumping. UI components should not absorb unrelated API, schema, domain, or infrastructure responsibilities merely for convenience. Apply SOLID principles where they improve boundaries; do not create abstractions only to satisfy a pattern.

For each concrete finding report:

```text
severity: critical | high | medium | low
path: <path>
issue: <what is wrong>
evidence: <why this is a real issue>
required_action: <specific correction>
```

Do not manufacture findings to make the review look thorough.

## 5. Validate the candidate

Run the smallest relevant checks that can prove the requested behavior, then widen only when risk warrants it.

Possible checks include:

```text
focused tests
integration tests
build
lint
type-check
runtime reproduction
```

Use repository-documented commands when available.

Never report a check as passed unless it actually ran against the current candidate.

If a required check cannot run, record the exact reason and decide whether the missing evidence makes the review `BLOCKED`.

If a validation command unexpectedly modifies tracked files, report it and do not silently clean or discard those changes.

## 6. Make the commit decision

Use exactly one status.

### PASS

Use only when:

- every intent item is `PASS`
- no critical, high, or correctness-blocking finding remains
- all changed paths are required or justified supporting changes
- required validation passed
- no material attribution uncertainty remains

Meaning: safe to commit.

### NEEDS_CONFIRMATION

Use when the requested intent is fully implemented but the candidate contains material `extra` or `unclear` changes that the user should explicitly accept, separate, or remove before committing.

Meaning: implementation may be correct, but do not commit the entire candidate without user confirmation.

### FIX

Use when:

- any intent item is `PARTIAL` or `FAIL`
- a correctness, security, integrity, compatibility, or regression issue blocks acceptance
- required supporting implementation or tests are missing

Meaning: do not commit. Continue implementation with a bounded correction.

### BLOCKED

Use when the review cannot be completed reliably because intent, repository state, required tooling, or required evidence is unavailable.

Meaning: do not make a commit-safety claim.

## Correction prompt

Return a correction prompt only for `FIX`.

The prompt must:

- continue from the current worktree
- preserve completed correct work
- list only unresolved requirements and concrete findings
- keep the original scope
- name required validation
- explicitly forbid unrelated refactoring and committing

## Output contract

Keep the final review compact.

```text
Status: PASS | NEEDS_CONFIRMATION | FIX | BLOCKED

Intent coverage:
- <ID> <PASS/PARTIAL/FAIL/UNKNOWN> — <evidence>

Change scope:
- required: <paths or none>
- supporting: <paths or none>
- extra: <paths or none>
- unclear: <paths or none>

Findings:
- <severity + path + issue + required action>
- None

Validation:
- <check -> result>

Commit decision:
<one direct sentence>

Correction prompt:
<only when Status is FIX>
```

Do not bury the commit decision in prose.
