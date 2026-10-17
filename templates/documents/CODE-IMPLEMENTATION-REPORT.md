# Code Implementation Report

**Intent:** `<ID@revision>`  
**Mode:** `<FOCUSED|STANDARD|DEEP>`  
**Outcome:** `<VERIFIED|IMPLEMENTED_UNVERIFIED|FAILED_VERIFICATION|BLOCKED|NEEDS_DECISION>`  
**Candidate(s):** `<repo IDs, exact revision and diff identities>`

## Delivered change

Describe implemented behavior, not just edited files. List required and supporting changes and explain any authorized deletions or contract retirements.

## Task handoffs

| Task | Owner | Authorized write scope | Changed paths | Result |
| --- | --- | --- | --- | --- |
| | | | | |

## Acceptance and preservation

| Requirement ID | Status | Evidence and environment | Limitations |
| --- | --- | --- | --- |
| | | | |

## Post-build test decision

`USED / NOT_APPLICABLE / BLOCKED` with rationale. If used, state whether this was **post-implementation verification** or genuine later RED -> GREEN for a new behavior/defect. Never mislabel retrospective testing as original TDD.

## Independent verification

Verifier context ID and whether independent from Builder contexts. For each executed probe include actual command/tool, candidate binding, environment, observed outcome and known limitations. Note skipped or unavailable runtime/browser checks.

## Integrated review

Report `code-review` verdict and material findings on complete integrated diff, including pre-existing dirty state distinctions.

## Residual risks and next actions

List unresolved contract or runtime assumptions, authorization needs and any required follow-up. No commit/deployment unless user separately authorizes it.
