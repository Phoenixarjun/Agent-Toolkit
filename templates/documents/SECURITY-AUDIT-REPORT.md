# Security Audit — <Project> (Impact <LOW | MODERATE | HIGH | CRITICAL>)

**Outcome:** <ACCEPTABLE_WITHIN_ASSESSED_SCOPE | REMEDIATION_REQUIRED | INSUFFICIENT_EVIDENCE | SCOPE_UNRESOLVED>  
**Depth:** <SANITY | STANDARD | DEEP> · **Assessed revision:** <commit and dirty state> · **Date:** <date>  
**Runtime identity:** <build / target / not available> · **Audit execution:** <complete | incomplete>

> Independent point-in-time *technical security assurance within the stated scope*. Not a security certification, legal compliance determination, guarantee of security, or substitute for professional regulated assurance.

## 1. Executive assessment

<In 3–5 plain-language sentences: what works, what is actually unsafe, what should change, and whether current controls are sufficient for the application's real risk. Do not claim “secure” universally.>

**Important unresolved uncertainty:** <none within assessed scope | concise description>

## 2. Scope and assurance basis

- **What the product does:** <...>
- **Why this impact tier:** <assets, actors, exposure, money/health/safety/data impact>
- **Selected assessment depth and limits:** <...>
- **Included and excluded boundaries:** <...>
- **Architecture / sensitive resources:** <...>
- **Approved test environments and probe limits:** <...>
- **Source/runtime correspondence:** <...>
- **Independent execution:** <authority context, trust-path context, coverage critic context, verifier context; or stated isolation blocker>

## 3. Implemented security controls

| Control / property | Applicability | Implementation | Verification | Evidence / next action |
|---|---|---|---|---|
| <e.g. Cross-user private data isolation> | REQUIRED | COMPLETE | VERIFIED | <E-...> |
| <e.g. Session revocation> | REQUIRED | PARTIAL | INCONCLUSIVE | <why> |
| <e.g. SSO> | NOT_APPLICABLE | ABSENT | NOT_APPLICABLE | <scope rationale> |

**Dimensions must stay separate.** An implemented library does not equal a verified control. Failed required controls are not optional improvements. Explain `UNDETERMINED`, `BLOCKED` and `NOT_VERIFIED` in plain language.

## 4. Sensitive operation verification

| Operation ID | Principal → action → resource | Expected | Observed | Assessment | Evidence |
|---|---|---|---|---|---|
| O-001 | <User A → READ → user B record> | DENY | <...> | <VERIFIED/FAILED/...> | <...> |

**Path accounting:** <key entry → sink and sink → entry examinations; number of distinct *material* operations covered, failed, unverified/blocked; explain sampling, do not convert counts to a security score.>

## 5. Confirmed security findings

### F-001 — <short specific violated invariant>

- **Severity:** <CRITICAL/HIGH/MEDIUM/LOW/INFORMATIONAL> (only for confirmed findings)
- **Affected boundary / actor / operation:** <...>
- **Expected invariant and observed violation:** <...>
- **Corroborated evidence:** <redacted evidence IDs, source revision and runtime identity>
- **Independent verification and counter-evidence:** <verifier result and alternatives checked>
- **Why the impact matters in this application:** <...>
- **Minimum remediation objective:** <observable property to restore, not prescriptive tech bloat>
- **Retest acceptance criteria:** <...>

<Repeat only for independently corroborated, distinct root causes.>

## 6. What to implement — and what not to

**Required corrections:** <demonstrable defect or applicable requirement gap with smallest defensible outcome>.

**Optional improvements:** <contextually beneficial hardening, cost and expected gain; never present as confirmed vulnerability>.

**Already sufficient / unnecessary additions:** <explain why no added SSO/MFA/WAF/etc is warranted when evidence supports that decision>.

## 7. Open candidates, gaps and limitations

- **Needs validation:** <each source-grounded candidate, blocker, safe next verification; no vulnerability severity>
- **Rejected findings:** <concise rejection reasons when material>
- **Coverage critic gaps and disposition:** <closed by new evidence, blocked or deferred>
- **Uninspected or blocked surfaces:** <...>
- **Regulatory applicability:** <potentially applicable regime, triggering facts, official source version/date, human confirmation needed; never state legal compliance>
- **Tooling/authorization/test limits:** <...>
- **Residual risks:** <...>

## 8. Recommended decision and handoff

<Minimal meaningful next action. If controls are sufficient within tested scope, say so; don't invent a security upgrade.>

**Separate-context remediation:** This audit did **not** modify source. Implementing agents must independently examine this report and the actual repository; request a *new* audit on the changed revision.

**Optional follow-up:** Would you like a detailed explanation of an identified finding or an implementation-neutral remediation brief for another session?

---

## Restricted evidence appendix (only when authorized)

| Evidence ID | Kind | Agent context | Source/revision or build | Method | Sanitized observation |
|---|---|---|---|---|---|
| E-... | <static/dynamic/...> | <real context> | <...> | <...> | <...> |

Never include live secrets, real session cookies, unnecessary exploit payloads, PHI, personal identifiers or customer data in a general report. Generate human claims from validated `audit.json`; the validator checks structural consistency, not whether claims are true.
