---
name: code-review
description: Reviews repository changes before commit by verifying the complete candidate against the active Change Intent Contract or equivalent user requirements, detecting missing acceptance criteria and scope drift, assessing correctness and risk, and validating relevant checks. Use after implementation and before commit when a commit/no-commit decision is needed.
compatibility: Requires a Git repository and access to inspect changed files. Running tests, builds, lint, type checks, or runtime checks requires the repository toolchain.
metadata:
  version: "1.1.0"
  category: "quality"
  stage: "pre-commit"
---

# Code Review

## Purpose

Decide whether the current candidate faithfully satisfies the authorized intent and is safe to commit.

This is a review gate, not an implementation pass.

## Non-goals

Do not:

- edit source files
- fix findings
- commit, reset, clean, stash, checkout, or discard changes
- broaden the requested feature
- silently amend the intent contract
- infer new product requirements from the implementation
- attribute pre-existing dirty work to the current agent without evidence
- report style preferences as defects unless they violate an explicit rule or materially harm correctness or maintainability

If fixes are required, return a bounded correction prompt instead of changing code.

## 1. Select the intent being reviewed

Prefer a project-local Change Intent Contract when one exists:

```text
.agent-toolkit/intents/INT-*.md
```

A review must identify exactly one active intent or an explicit equivalent user request.

Use this authority order:

1. explicit current user correction or amendment
2. the selected ready Change Intent Contract
3. explicit task, issue, specification, plan, or acceptance criteria
4. the original implementation request and follow-up constraints
5. repository evidence only when no better intent source exists

If a current user instruction materially conflicts with a ready contract, do not silently choose one. The contract must be amended or superseded before making a commit-safety decision.

If multiple intents exist, do not guess which one owns the candidate. Select from explicit user context or reliable repository evidence. Otherwise return `BLOCKED`.

## 2. Establish the acceptance contract

When a Change Intent Contract is available, preserve its stable acceptance IDs and scope boundaries.

Otherwise derive a compact equivalent containing:

```text
outcome
acceptance criteria
must preserve
constraints
approval boundaries when relevant
out of scope
```

Do not add requirements merely because they would be nice to have.

If intent cannot be established confidently enough to judge the candidate, return `BLOCKED`.

## 3. Establish the complete candidate

Bind the review to an exact intent identity and candidate boundary.

Record when available:

```text
intent ID + revision
HEAD commit
commit candidate boundary
changed-path snapshot
```

If the user explicitly asks to review staged changes, the staged diff is the proposed commit candidate. Still inspect unstaged and untracked state for dependencies, interference, or omitted required work.

Otherwise treat the complete relevant worktree as the candidate.

Never call a staged subset safe when it depends on required unstaged changes that would be left behind.

Inspect repository state before judging individual files.

Use Git or equivalent host operations to inspect:

```text
git status --short
git diff --stat
git diff
git diff --cached
git ls-files --others --exclude-standard
```

Review staged, unstaged, deleted, renamed, and relevant untracked changes. Do not assume the staged diff is the whole worktree.

Inspect enough unchanged surrounding code, tests, callers, contracts, configuration, migrations, and entry points to understand the effect of each change.

If the worktree contains changes for several intents, isolate the candidate only when reliable evidence supports the separation. Do not manufacture attribution from filenames alone.

If the candidate modifies the selected ready intent contract itself, verify that the modification corresponds to an explicit user-authorized amendment. Otherwise classify the contract mutation as `MATERIAL_EXTRA` or `UNCLEAR` and do not let implementation rewrite its own acceptance target.

## 4. Classify every changed path or behavior

Use exactly one disposition where practical:

### REQUIRED

Directly implements an acceptance criterion or explicitly in-scope behavior.

### SUPPORTING

Not explicitly requested but genuinely necessary to make the requested behavior correct, buildable, testable, or safely integrated.

### BENIGN_EXTRA

A small, local, reversible addition related to the requested work that does not materially alter behavior, contracts, data, security, dependencies, configuration, architecture, operations, or user scope.

Disclose it. It does not block commit by itself.

### MATERIAL_EXTRA

Unrequested work that materially changes behavior or system commitments, including new persistence effects, migrations, external side effects, dependencies, APIs, schema, security behavior, configuration, infrastructure, or substantial user-facing scope.

Require explicit user acceptance, separation, or removal before committing the whole candidate.

### UNRELATED

No defensible relationship to the selected intent.

Do not include it in an intent-aligned commit without explicit user direction.

### UNCLEAR

Available evidence cannot establish why the change exists or whether it belongs to the intent.

Do not guess.

## 5. Verify acceptance coverage

Evaluate every acceptance criterion independently.

Use exactly:

```text
PASS       fully satisfied with evidence
PARTIAL    some required behavior exists but the criterion is incomplete
FAIL       required behavior is missing or contradicted
UNKNOWN    evidence is insufficient
WITHDRAWN  explicitly removed by an authorized intent amendment
```

Evidence should point to concrete behavior, paths, symbols, tests, runtime observations, or other relevant proof.

A statement such as `feature implemented` is not evidence.

Also verify `Must Preserve` conditions when the candidate could affect them.

## 6. Review implementation risk

Review only dimensions relevant to the candidate.

Prioritize:

- behavioral correctness
- edge cases and failure paths
- input validation
- authentication and authorization
- security and privacy
- data integrity
- concurrency and ordering
- API, schema, and compatibility impact
- migrations and rollback implications
- external side effects
- error handling and cleanup
- consistency with existing architecture
- modularity and responsibility boundaries
- tests for changed behavior
- accidental duplication
- scope drift

Treat crossing an explicit approval boundary without authorization as a blocking finding even when the change appears technically necessary.

For each concrete finding report:

```text
severity: critical | high | medium | low
path: <path or behavior>
issue: <what is wrong>
evidence: <why this is real>
required_action: <specific correction or decision>
```

Do not manufacture findings to make the review appear thorough.

## 7. Validate the final candidate

Run the smallest relevant checks that can prove the requested behavior, then widen when risk warrants it.

Possible checks include:

```text
focused tests
integration tests
build
lint
type-check
runtime reproduction
migration checks
contract tests
accessibility checks
```

Use repository-documented commands when available.

Never report a check as passed unless it actually ran against the current candidate.

If the candidate changes after validation, affected evidence is stale and must be rerun.

If a validation command unexpectedly modifies tracked files, report it and do not silently clean or discard those changes.

## 8. Make the commit decision

Use exactly one status.

### PASS

Use only when:

- every active acceptance criterion is `PASS`
- required `Must Preserve` conditions hold
- no critical, high, or correctness-blocking finding remains
- changed work is `REQUIRED`, `SUPPORTING`, or only disclosed `BENIGN_EXTRA`
- required validation passed
- no material attribution uncertainty remains

Meaning: safe to commit for the selected intent.

### NEEDS_CONFIRMATION

Use when the intent is otherwise satisfied but the candidate contains `MATERIAL_EXTRA`, `UNRELATED`, or consequential `UNCLEAR` work that the user must accept, separate, or remove.

Meaning: do not commit the whole candidate without an explicit decision.

### FIX

Use when:

- any active criterion is `PARTIAL` or `FAIL`
- a correctness, security, integrity, compatibility, or regression issue blocks acceptance
- required supporting implementation or tests are missing
- an approval boundary was crossed without authorization and the appropriate resolution is to remove or rework the implementation

Meaning: do not commit. Continue with a bounded correction.

### BLOCKED

Use when reliable review cannot be completed because intent selection, repository state, attribution, required tooling, or required evidence is unavailable.

Meaning: do not make a commit-safety claim.

## Correction prompt

Return a correction prompt only for `FIX`.

The prompt must:

- continue from the current worktree
- preserve completed correct work
- reference unresolved acceptance IDs
- list only concrete blocking findings
- keep the accepted intent and scope unchanged
- preserve unrelated user changes
- name required validation
- explicitly forbid unrelated refactoring and committing

## Output contract

Keep the result compact and traceable.

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
