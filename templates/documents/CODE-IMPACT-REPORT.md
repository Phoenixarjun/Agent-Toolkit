# Code Impact Report

**Goal:** <intended user-visible/system outcome>  
**Mode and assurance:** <focused|standard|deep> / <complete|limited|blocked>  
**Inspected as of:** <date/time and repository revisions; dirty state>  
**Authorized scope:** <repo IDs and paths>  
**Non-goals:** <out of scope>

## Decision summary

<What needs to change, why, what must not change, and whether the plan is ready for a separate implementation context. Avoid unsupported certainty.>

## Existing behavior and relevant paths

| Path/contract | Current owner | Verified source evidence | State |
| --- | --- | --- | --- |
| <trace> | <component> | <repository@revision:path:lines or ledger ID> | OBSERVED / INFERRED / UNRESOLVED |

Explain the important forward **and reverse** paths, not every unrelated file. Link to the exact record IDs.

## Ownership and compatibility

| Responsibility | Current owner(s) | Intended owner | Preserve or transition | Overlap risk |
| --- | --- | --- | --- | --- |
| <responsibility> | <component> | <component> | <contract/guard> | <why duplication may be necessary or removable> |

Explicitly identify **retirement candidates** as conditional. Never confuse centralized authentication with removing required downstream authorization.

## Impact and coverage

| Obligation | Affected repositories/contracts | Status | Evidence / blocker |
| --- | --- | --- | --- |
| <question> | <names/IDs> | covered / partial / blocked / not_applicable / out_of_scope | <IDs or reason> |

Disclose missing repos, dynamic-resolution uncertainty, unverified deployment assumptions and incompatible snapshots.

## Proposed implementation sequence (NO changes executed)

| Order | Type | Proposed action | Prerequisites / contract | Proof required |
| --- | --- | --- | --- | --- |
| 1 | REQUIRED / CONDITIONAL / OPTIONAL | <bounded change> | <verified premise IDs> | <test/check> |

List decisions requiring user approval separately. Include rollout, backwards compatibility and rollback proof for migrations and removals.

## Independent challenge and verification

**Explorers:** <actual context identifiers and assigned questions>  
**Coverage critic:** <actual context, gaps and resolution>  
**Evidence verifier:** <actual context, challenged claim IDs, verdicts>  
**Mechanical validation:** <actual command/result or NOT RUN>

Do not claim independent assurance if workers did not execute in separate contexts. Never treat script PASS as proof of source truth.

## Risks and unresolved decisions

- <material uncertainty and effect on proposed plan>
- <what authorized access or evidence would resolve it>

## Handoff

The separate implementation agent must inspect the **current** code and reconcile revisions before editing. Exploration authorizes **no** file deletion, source edits, commits or deployment. Verify the implementation via relevant TDD, integration tests, Code Review and independent Security Audit when appropriate.
