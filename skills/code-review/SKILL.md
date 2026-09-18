---
name: code-review
description: Reviews repository changes before commit by verifying the complete candidate against the active Change Intent Contract or equivalent user requirements, detecting missing acceptance criteria and scope drift, assessing correctness and risk, and validating relevant checks. Use after implementation and before commit when a commit/no-commit decision is needed.
compatibility: Requires a Git repository and access to inspect changed files. Running tests, builds, lint, type checks, or runtime checks requires the repository toolchain.
metadata:
  version: "1.2.0"
  category: "quality"
  stage: "pre-commit"
---

# Code Review

## Purpose

Decide whether the current candidate faithfully satisfies the authorized intent and is safe to commit.

This is a review gate, not an implementation pass. Do not edit source files, fix findings, commit, stash, or discard changes. Return a bounded correction prompt instead.

## Non-goals

Do not:

- silently amend the intent contract
- infer new product requirements from the implementation
- attribute pre-existing dirty work to the current agent without evidence

## 1. Select the intent being reviewed

Prefer a project-local Change Intent Contract:

```text
.agent-toolkit/intents/INT-*.md
```

Authority order:

1. explicit current user correction or amendment
2. the selected ready Change Intent Contract
3. explicit task, issue, specification, or acceptance criteria
4. the original implementation request and follow-up constraints
5. repository evidence only when no better source exists

If a current user instruction materially conflicts with a ready contract, do not silently choose one. The contract must be amended or superseded before making a commit-safety decision.

If multiple intents exist and attribution is ambiguous, return `BLOCKED`.

## 2. Establish the acceptance contract

When a Change Intent Contract is available, preserve its stable acceptance IDs and scope boundaries.

Otherwise derive a compact equivalent:

```text
outcome
acceptance criteria
must preserve
constraints
approval boundaries
out of scope
```

Do not add requirements merely because they would be nice to have.

If intent cannot be established confidently, return `BLOCKED`.

## 3. Establish the complete candidate

Bind the review to an exact intent identity and candidate boundary:

```text
intent ID + revision
HEAD commit
commit candidate boundary
changed-path snapshot
```

If the user explicitly asks to review staged changes, the staged diff is the proposed commit candidate. Still inspect unstaged and untracked state for dependencies or omitted required work. Never call a staged subset safe when it depends on required unstaged changes.

Otherwise treat the complete relevant worktree as the candidate.

Use Git operations to inspect state:

```text
git status --short
git diff --stat && git diff
git diff --cached
git ls-files --others --exclude-standard
```

Review staged, unstaged, deleted, renamed, and relevant untracked changes.

Inspect enough surrounding code, tests, callers, contracts, configuration, and entry points to understand the effect of each change.

If the worktree contains changes for several intents, isolate the candidate only when reliable evidence supports the separation. Do not manufacture attribution from filenames alone.

If the candidate modifies the selected ready intent contract itself, verify the modification corresponds to an explicit user-authorized amendment. Otherwise classify the contract mutation as `MATERIAL_EXTRA` or `UNCLEAR`.

## 4. Classify every changed path or behavior

Use exactly one disposition:

**REQUIRED** — directly implements an acceptance criterion or in-scope behavior.

**SUPPORTING** — not explicitly requested but genuinely necessary to make requested behavior correct, buildable, testable, or safely integrated.

**BENIGN_EXTRA** — small, local, reversible addition related to the requested work that does not materially alter behavior, contracts, data, security, dependencies, configuration, architecture, or user scope. Disclose it; does not block commit.

**MATERIAL_EXTRA** — unrequested work that materially changes behavior or system commitments: new persistence, migrations, external side effects, dependencies, APIs, schema, security behavior, or substantial user-facing scope. Require explicit user acceptance, separation, or removal before committing.

**UNRELATED** — no defensible relationship to the selected intent. Do not include without explicit user direction.

**UNCLEAR** — available evidence cannot establish why the change exists. Do not guess.

## 5. Verify acceptance coverage

Evaluate every acceptance criterion independently:

```text
PASS       fully satisfied with evidence
PARTIAL    some required behavior exists but criterion is incomplete
FAIL       required behavior is missing or contradicted
UNKNOWN    evidence is insufficient
WITHDRAWN  explicitly removed by an authorized intent amendment
```

Evidence must point to concrete behavior, paths, symbols, tests, or runtime observations. "Feature implemented" is not evidence.

Also verify `Must Preserve` conditions when the candidate could affect them.

## 6. Review implementation risk

Review dimensions relevant to the candidate. For complex risk domains — security, auth, data integrity, migrations, distributed systems, public contracts — load `references/review-risk.md`.

For each concrete finding report:

```text
severity: critical | high | medium | low
path: <path or behavior>
issue: <what is wrong>
evidence: <why this is real>
required_action: <specific correction or decision>
```

Treat crossing an explicit approval boundary without authorization as a blocking finding.

Do not manufacture findings to appear thorough.

## 7. Validate the final candidate

Run the smallest relevant checks that can prove the requested behavior, then widen when risk warrants it. Use repository-documented commands when available.

Never report a check as passed unless it actually ran against the current candidate.

If the candidate changes after validation, affected evidence is stale and must be rerun.

If a validation command unexpectedly modifies tracked files, report it and do not silently discard those changes.

## 8. Make the commit decision

### PASS

Use only when:

- every active acceptance criterion is `PASS`
- required `Must Preserve` conditions hold
- no critical, high, or correctness-blocking finding remains
- changed work is `REQUIRED`, `SUPPORTING`, or only disclosed `BENIGN_EXTRA`
- required validation passed
- no material attribution uncertainty remains

### NEEDS_CONFIRMATION

Intent is otherwise satisfied but the candidate contains `MATERIAL_EXTRA`, `UNRELATED`, or consequential `UNCLEAR` work requiring user acceptance, separation, or removal.

### FIX

- any active criterion is `PARTIAL` or `FAIL`
- a correctness, security, integrity, compatibility, or regression issue blocks acceptance
- required supporting implementation or tests are missing
- an approval boundary was crossed without authorization

### BLOCKED

Reliable review cannot be completed: intent selection, repository state, attribution, required tooling, or required evidence is unavailable.

## Correction prompt

Return only for `FIX`. The prompt must:

- continue from the current worktree
- preserve completed correct work
- reference unresolved acceptance IDs
- list only concrete blocking findings
- keep accepted intent and scope unchanged
- preserve unrelated user changes
- name required validation
- forbid unrelated refactoring and committing

## Output contract

```text
Status: PASS | NEEDS_CONFIRMATION | FIX | BLOCKED
Intent: <intent ID + revision + title, or derived request>
Candidate: <HEAD/candidate identity + boundary>

Acceptance coverage:
- <AC-ID> <PASS/PARTIAL/FAIL/UNKNOWN/WITHDRAWN> — <evidence>

Change disposition:
- REQUIRED: <paths/behaviors or none>
- SUPPORTING: <paths/behaviors or none>
- BENIGN_EXTRA: <paths/behaviors or none>
- MATERIAL_EXTRA: <paths/behaviors or none>
- UNRELATED: <paths/behaviors or none>
- UNCLEAR: <paths/behaviors or none>

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

Do not bury the decision in prose.
