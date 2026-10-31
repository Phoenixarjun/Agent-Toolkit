# Application Health Report

**Application:** <name or bounded component>
**Assessment date:** <date/time>
**Scope:** <authorized roots, features and deployment context>
**Inspected revisions:** <repository/revision/dirty state or unavailable>
**Assessment outcome:** SUFFICIENT | LIMITED | BLOCKED
**Verification:** INDEPENDENT | SELF_CHECKED | NOT_VERIFIED

## Executive assessment

**Fit for known purpose:** <one direct, evidence-bounded judgment; no invented numeric score>

**What is working:** <observed strengths, relevant current sufficiency, things not to change>

**What deserves attention:** <only consequential findings; say "No material issues identified in examined scope" if supported>

**Highest-value next step:** <one action or NO_CHANGE, conditional on missing user facts where relevant>

**Scope of confidence:** <source, run checks and runtime evidence used; unknowns; explicitly unmeasured capacity>

## Application fingerprint and applicability

| System property | Observed fact or unknown | Evidence |
| --- | --- | --- |
| User-critical behavior | | |
| State and persistence | | |
| External and runtime boundaries | | |
| Deployment and current use | | |
| Demand and resource ceilings | | |

| Investigative area | APPLICABLE / CONDITIONAL / NOT_APPLICABLE | Reason |
| --- | --- | --- |
| <investigated concern> | | |
| <materially excluded concern, only if needed to explain scope> | | |

List only concerns considered during scoping. Do not fill every possible category or turn exclusions into a checklist score.

## Recommended decisions

| Order | NOW / NEXT / DEFER / NO_CHANGE | Finding or evidence | Smallest next step | Proof or revisit trigger |
| --- | --- | --- | --- | --- |
| 1 | | | | |

Prefer at most five high-value actions. Include justified no-change and deferred decisions where helpful.

## Detailed findings

### <Finding ID> <Short grounded title>

- **Category and status:** CONFIRMED_DEFECT | SUPPORTED_RISK | HYPOTHESIS | OPPORTUNITY
- **Priority:** P0 | P1 | P2 | P3 | UNRATED
- **Affected behavior and scenario:** <specific observable consequence>
- **Evidence:** <repo/path/line/revision, or command/artifact/environment/time with provenance>
- **Confidence and limits:** <what is demonstrated vs not measured>
- **Independent verification:** <verdict and evidence, or explicit not performed>
- **Recommendation:** <smallest defensible action or diagnostic probe>
- **Why not a larger change:** <only if a real larger alternative was considered>
- **Reproduction or validation:** <safe reproducible check and expected observable result>

Repeat only for distinct material findings. Do not turn generic best practices into findings.

## Creator-owned questions and assumptions

Ask only decision-changing external questions, up to eight across the whole assessment. If none are needed, say none.

| Priority | Question | Recommendation affected | Answer / assumption status |
| --- | --- | --- | --- |

## Measurements and test evidence

| Claim | Value or NOT_MEASURED | Provenance and environment | Interpretation and limits |
| --- | --- | --- | --- |

Distinguish measured workload, evidence-backed forecast, hypothetical load, and unknown. A static code review cannot establish supported peak concurrency, memory leaks or throughput.

## Deferred / explicitly unnecessary changes

State what should not be implemented now, why, and what objective signal would justify revisiting it. Omit if not pertinent.

## Coverage, limitations, and handoff

**Examined:** <traced journeys, tests, artifacts, boundaries>

**Not examined / inaccessible:** <scopes and reasons>

**Contradictions and unresolved risks:** <material remaining uncertainty>

**Next action:** <NO_CHANGE, targeted diagnostic, /code-explore for uncertain blast radius, or user-approved /code later>

**No changes performed:** <confirm no application changes and disclose any authorized diagnostics or side effects>
