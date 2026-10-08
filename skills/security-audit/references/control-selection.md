# Risk-Calibrated Control Selection

Use this reference after mapping the application's actual boundaries. It is a **routing aid**, not a mandatory exhaustive checklist. Keep one canonical control for one underlying security property; attach multiple applicable standard mappings to it.

## Two independent axes

**Application impact (consequence of breach)**

| Tier | Typical consequences, subject to context |
|---|---|
| LOW | Limited private assets/exposure, little harm beyond local disruption; prototype with safe dummy data |
| MODERATE | User accounts and personal records; loss affects users or operations but limited systemic harm |
| HIGH | Valuable commercial workflows, sensitive personal data, privileged administration, multi-tenant exposure, money-related effects |
| CRITICAL | Potential catastrophic financial, safety, health, legal or systemic consequences; high-value state changes or broad privileged reach |

A payment provider can lower *card-data scope* while leaving order/price/refund/account security high. A fitness tracker may process sensitive health information. Labels such as “college,” “startup,” or “bank” are not sufficient classification evidence.

**Assessment depth (effort)**

- `SANITY`: read-only discovery and targeted high-value checks; only authorized, low-impact verification. Not a production assurance claim.
- `STANDARD`: comprehensive *applicable* controls, static/configuration review, targeted runtime proofs, risk-based negative testing.
- `DEEP`: threat/invariant-driven boundary analysis, stronger cross-role/tenant/failure/abuse scenarios, optional specialist tools when available. Never equal to an accredited penetration test.

Default `STANDARD`. High or critical impact suggests `DEEP` or specialist engagement, but doesn't forcibly trigger invasive activity. User depth cannot waive disclosure of material untested controls.

## Select controls in passes

1. **Universal exposure-aware baseline**: repo/secrets/dependencies/config, publicly reachable attack surface, input handling at trust boundaries, secure transport where data is exchanged, error leakage, and least-privilege access where identities exist.
2. **Capability triggers** (only if present):
   - accounts -> credential flows, login, recovery, sessions, account lifecycle
   - authorization roles -> function/object/property authorization and privilege boundaries
   - tenant segregation -> cross-tenant read/write/isolation including async flows
   - OAuth/OIDC/SSO -> redirect, state/nonce/PKCE as applicable, audience/issuer, token confusion, logout lifecycle
   - money/irreversible orders -> price/tamper/idempotency/replay/authorization/business invariants
   - sensitive information -> confidentiality, access, retention, logs, backups, deletion, key lifecycle
   - file upload -> file type/content/sanitization/access/storage controls
   - outbound URL/webhooks -> SSRF boundaries, callbacks/signatures/replay
   - queues/workers -> provenance, actor context, internal privilege and replay
   - cloud/Kubernetes/IaC -> IAM, network exposure, CI credentials, supply chain
   - AI/LLM/tools/MCP -> tool authorization, prompt-injection boundaries, data exfiltration, excessive agency, provenance
   - mobile/device -> platform storage, permissions, API binding, integrity as applicable
3. **Obligation triggers**: jurisdiction, customer/contract, regulated entity relationship, payment-data handling, sector rules. Verify applicability; do not equate technical security with legal compliance.
4. **Threat-driven delta**: prioritize critical assets, attack paths, state-changing boundaries and high-recovery-cost failures.

## Control decision record

```text
CONTROL-ID:
Property / asset:
Applicable? REQUIRED | RECOMMENDED | NOT_APPLICABLE | UNDETERMINED
Why / source / standard version:
Implementation: COMPLETE | PARTIAL | ABSENT | UNKNOWN
Verification: VERIFIED | FAILED | PARTIAL | NOT_VERIFIED | INCONCLUSIVE | BLOCKED | NOT_APPLICABLE
Evidence / candidate revision:
Risk / confidence:
Next verification or recommendation:
```

`REQUIRED` means justified by demonstrable security property or applicable obligation, not “appeared on a checklist.” A `RECOMMENDED` unimplemented control is not automatically a vulnerability. `NOT_APPLICABLE` requires a concrete negative applicability basis (e.g. no SSO flow), not lack of time to check it. `UNDETERMINED` is not `NOT_APPLICABLE`.

## Triage decisions

- Confirmed authorization bypass / data exposure / unsafe transaction -> finding with contextually supported severity.
- Required control missing -> gap; may be release-blocking based on impact and obligation.
- Implemented but not runtime tested -> `NOT_VERIFIED` with reason; not a PASS.
- Scanned library exists -> never a verification PASS.
- Framework/feature absent and not applicable -> explain exclusion; no finding.
- Control deliberately omitted with accepted residual risk -> record owner decision as an exception, **not** an independent auditor's safety endorsement.

## Relevant source categories

Technical requirements: [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) (verify current stable version; v5.0.0 was stable as of 2026-10-08).
Testing methodology: [OWASP WSTG](https://owasp.org/www-project-web-security-testing-guide/) (stable 4.2 as of 2026-10-08), [OWASP API Top 10 2023](https://owasp.org/API-Security/).
Identity guidelines: [NIST SP 800-63-4](https://csrc.nist.gov/pubs/sp/800/63/4/final).

Do not transplant obsolete ASVS 4.x identifiers into 5.x findings. Reference versions and precise control identifiers only when validated against the source.
