# Coverage, Findings, and Multi-Agent Evidence

Load for every full audit. A completed audit needs attributable critic evidence and an independently checked final record, **even when findings are empty**. The parent orchestrator is **the only writer** of the canonical ledger and report. Subagents work in independent contexts and return bounded evidence.

## Ledger dimensions

- **Invariant**: one security property with an independent oracle, assets and boundary.
- **Operation**: one representative `principal × action × resource × context`, with expected ALLOW or DENY and observed result; reference its invariant and coverage evidence.
- **Coverage**: source/attack surface × boundary × applicable class, with state `planned | covered | candidate | blocked | deferred | not_applicable | out_of_scope`.
- **Control**: applicability + implementation + verification, never collapsed into one traffic-light color.
- **Finding**: independently challenged candidate with `confirmed | needs_validation | rejected`.
- **Evidence**: attributable to source revision, runtime build when used, agent context, method, observation and sanitized locator.

`covered` means materially inspected and evidenced—not proof the route is safe. `VERIFIED` means the *specific property* is supported by appropriate independent proof. `NOT_APPLICABLE` must follow a grounded trigger check, not the absence of a test.

## Investigation independence

Use distinct real contexts for authority investigator, trust-path investigator, coverage critic and finding verifier. Parallelism is optional; **isolation is not**. Parent owns reconciliation. The critic must challenge coverage claims from a context different from the hunters. The finding verifier must be different from the hunter who generated the finding. Independent verification means original source/evidence reinspection, not repeating the hunter's summary.

## Findings

- `confirmed`: specific authorization/trust boundary violation and evidenced effect; severity based on impact and feasibility.
- `needs_validation`: source-grounded concern, exactly what is unknown and how to verify safely; no severity.
- `rejected`: disproved, effective compensating controls, wrong policy or unreachable path, with evidence.

Static scanner output **alone** is not enough to confirm an exploit. An absent REQUIRED control may warrant correction without being called an exploitable vulnerability. Repeated findings from one root cause should be merged with affected instances listed separately.

## Source and deployment consistency

A record must point to a pinned source revision. Dynamic evidence must include a corresponding runtime build identity when available; otherwise disclose the missing linkage and avoid inferring that deployed behavior represents checked-out code. Evidence copied from older assessments is a lead until revalidated against the assessed revision.

## Gap closure

Coverage critic proposes concrete gaps and why they matter. Parent either delegates targeted follow-up or records `blocked/deferred` with a defensible rationale. A high-impact unverified boundary precludes a positive overall assurance outcome.

## Validator scope

`python scripts/validate_security_audit.py audit.json` checks schema version 2, referential integrity, unique context IDs, role presence, op/control/coverage consistency, and verdict logic. It **cannot** prove that a tool was called, a source line supports the claim, an agent context was actually isolated, or a vulnerability is real. Never confuse syntactic validation with audit correctness.
