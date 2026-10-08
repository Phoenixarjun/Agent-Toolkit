# Security Audit — <Project>

**Application impact:** <LOW | MODERATE | HIGH | CRITICAL> — <why>  
**Assessment depth:** <SANITY | STANDARD | DEEP>  
**Outcome:** <ACCEPTABLE_WITHIN_ASSESSED_SCOPE | REMEDIATION_REQUIRED | INSUFFICIENT_EVIDENCE | SCOPE_UNRESOLVED>  
**Assessed:** <date/time> · **Code revision:** <commit/build> · **Runtime target:** <environment/build if known>

> Independent, point-in-time technical security assessment of the stated scope—not certification, complete penetration-test coverage, or a legal compliance determination.

## 1. Executive assessment

<2–5 sentences: what is already adequately secured, material defects/gaps, what remains unverified, and what decision is needed. Avoid exaggeration.>

## 2. Scope and risk rationale

- **Product and sensitive assets:** <...>
- **Actors and trust boundaries:** <...>
- **Included:** <...>
- **Excluded:** <...>
- **Authorized runtime actions/environments:** <...>
- **Impact rationale:** <observed consequences, exposure, sensitive-data/financial/safety impact>
- **Depth limitation:** <...>

## 3. Existing controls and verification

| ID | Security property / control | Applicability | Implementation | Verification | Evidence | Next action |
|---|---|---|---|---|---|---|
| SEC-001 | <property> | REQUIRED | COMPLETE | VERIFIED | <link/command/result> | None |
| SEC-002 | <property> | REQUIRED | PARTIAL | FAILED | <evidence> | Correct defect |
| SEC-003 | <property> | RECOMMENDED | ABSENT | NOT_VERIFIED | <reason> | Optional decision |

**Applicability:** REQUIRED / RECOMMENDED / NOT_APPLICABLE / UNDETERMINED.  
**Implementation:** COMPLETE / PARTIAL / ABSENT / UNKNOWN.  
**Verification:** VERIFIED / FAILED / PARTIAL / NOT_VERIFIED / INCONCLUSIVE / BLOCKED / NOT_APPLICABLE.

## 4. Confirmed findings

### F-001 — <short title>

- **Severity / confidence:** <CRITICAL | HIGH | MEDIUM | LOW | INFORMATIONAL> / <HIGH | MEDIUM | LOW>
- **Control / affected boundary:** <...>
- **Expected security invariant:** <...>
- **Observed failure:** <...>
- **Evidence:** <redacted reproduction + path/line/test + candidate/target identity>
- **Business impact:** <...>
- **Root cause or uncertainty:** <...>
- **Recommended remediation objective:** <what property must be restored; avoid mandating an arbitrary technology>
- **Retest criterion:** <observable pass condition>

<Repeat only for materially distinct findings; deduplicate by root cause.>

## 5. Required corrections vs optional improvements

**Required corrections (security properties violated or applicable requirements unmet)**
- <priority, property, why required, minimum adequate outcome>

**Contextual improvements (beneficial but not required)**
- <tradeoff/cost/expected risk reduction>

**Not needed / excluded controls**
- <control, why not relevant now>

## 6. Evidence gaps and limitations

- **Unverified/blocked controls:** <why, what would unblock them>
- **Coverage exclusions:** <assets, trust boundaries, inaccessible deployment/configuration>
- **Scanner/runtime limitations:** <...>
- **Regulatory applicability screen:** <candidate obligations, evidence, official sources/dates, need for human confirmation>
- **Residual risk:** <...>

## 7. Recommended next action

<The smallest defensible action: fix a confirmed defect, obtain missing verification, preserve current design, or seek specialist assessment.>

**Follow-up:** Would you like a detailed explanation of any finding or a prioritized remediation brief for a separate implementation agent? This audit will not change code.

---

## Restricted evidence appendix (optional)

| Control / finding | Source/revision | Tool or method | Authorized target | Time | Sanitized evidence | Confidence |
|---|---|---|---|---|---|---|
| <...> | <...> | <...> | <...> | <...> | <...> | <...> |

> Never include credentials, live session tokens, PHI, financial account data or unnecessary exploit artifacts in the general report.
