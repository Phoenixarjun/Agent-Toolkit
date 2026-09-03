# Task Contracts

## Scout packet

```text
Task ID: <id>
Objective: <what must be discovered>
Read scope: <repository areas or external docs>
Do not touch: <all tracked files>
Required output: scout-result-v1
```

## Scout result

```text
Task ID: <id>
Status: PASS | BLOCKED
Relevant paths: <compact list>
Relevant symbols: <compact list>
Current behavior: <concise summary>
Constraints: <concise list>
Recommended write scope: <exact paths>
Recommended verification: <commands or procedures>
Risks: <concise list or None>
Sources: <internal paths or external references>
Blocker: <None or concrete blocker>
```

## Builder packet

```text
Task ID: <id>
Objective: <bounded implementation objective>
Context: <only required scout evidence>
Write scope: <exact writable paths>
Do not touch: <excluded paths and effects>
Acceptance criteria: <observable behavior>
Required verification: <focused checks>
Required output: builder-result-v1
```

## Builder result

```text
Task ID: <id>
Status: PASS | BLOCKED
Summary: <implemented behavior>
Changed paths: <exact paths or None>
Checks run: <commands or procedures>
Check results: <concise exact outcomes>
Acceptance coverage: <criterion -> evidence>
Evidence digest: <compact evidence>
Residual risks: <concise list or None>
Blocker: <None or concrete blocker>
```

Builder `PASS` applies only to the assigned task.

## Validator packet

```text
Task ID: <id>
Goal: <expected user-visible result>
Candidate paths: <builder-reported paths>
Acceptance criteria: <complete relevant criteria>
Required checks: <commands or procedures>
Restrictions: Do not intentionally modify tracked files
Required output: validator-result-v1
```

## Validator result

```text
Task ID: <id>
Status: PASS | FAIL | BLOCKED
Candidate identity: <commit, diff identity, or changed-path snapshot>
Checks run: <commands or procedures>
Results: <concise exact outcomes>
Acceptance coverage: <criterion -> PASS/FAIL + evidence>
Regression signals: <concise list or None>
Tracked files modified by validator: <None or exact list>
Failure class: implementation | test | build | lint | type | environment | dependency | scope | unknown | none
Recommended next action: <None or one bounded correction>
Blocker: <None or concrete blocker>
```

## Reviewer packet

```text
Task ID: <id>
Goal: <user goal>
Candidate identity: <candidate>
Review areas: <specific risk dimensions>
Restrictions: Read-only
Required output: reviewer-result-v1
```

## Reviewer result

```text
Task ID: <id>
Status: PASS | FINDINGS | BLOCKED
Candidate identity: <candidate>
Findings:
  - severity: critical | high | medium | low
    path: <path>
    issue: <concrete issue>
    evidence: <concise evidence>
    required_action: <specific correction or None>
Requirement gaps: <list or None>
Residual risks: <list or None>
Blocker: <None or concrete blocker>
```

## Correction packet

```text
Task ID: <original-id>
Failure class: <class>
Observed failure: <concise validator evidence>
Delta: <exact bounded correction>
Write scope: <unchanged original scope>
Do not touch: <unchanged exclusions>
Acceptance criteria: <affected criteria>
Required verification: <affected checks>
Required output: builder-result-v1
```

The original builder owns the correction when available.

After correction, run fresh validation against the new final candidate.

## Missing result

If a worker exits without the required structured result:

1. ask the same worker once for a result-only response
2. authorize no new writes
3. if the result is still missing, mark the task `BLOCKED`

Do not repeatedly respawn workers to recover a missing report.
