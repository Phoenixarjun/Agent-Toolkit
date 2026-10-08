# Safe Independent Verification

Use this reference when active verification is authorized. This is an **audit-only** method: do not patch source code or deploy changes during testing.

## Authorization before execution

Record explicit approved target/environment, authorized accounts/fixtures, allowed operations, rate limits and stop conditions. Distinguish owning a repository from owning a deployed service. A hostname containing `dev`, `staging`, or `localhost` does not itself prove scope authorization.

Passive inspections can proceed without runtime authorization. Mutating, high-volume, availability-impacting, or external-network probes require separate affirmative approval, even on a test environment. When uncertain, mark blocked; never improvise beyond scope.

## Test selection

Choose high-impact falsifiable invariants. Match each with:
- independent expected secure behavior
- permitted stimulus
- observed actual result
- source/config corroboration when relevant
- bounded scope and cleanup plan

Representative techniques in authorized isolated fixtures:
- differential access by two test identities/roles or tenants
- token/session expiration, tampering and revocation where applicable
- direct API behavior versus frontend restrictions
- replay/duplicate requests with non-sensitive synthetic objects
- invalid business transitions and input boundaries
- dependency-failure behavior using controlled stubs in test environment

Do not send real credential dumps, enumerate real user records, or exploit to obtain sensitive data as proof.

## Tool choice

Use a browser tool/Playwright for UI and session transitions; HTTP clients for API authorization and state invariants; configuration evidence for non-runtime controls; existing SAST/SCA/secret/IaC tooling for targeted static categories. Prefer stable existing tools to generated attack scripts.

A browser pass cannot prove an API is secure. A static assertion cannot prove a running instance enforces it. Combine independent sources where needed.

## Proof and falsification

Treat a `PASS` as a bounded statement: the defined property held under the tested conditions for the recorded candidate and environment. Look for contradictory evidence. If an apparent denial still causes a side effect, the control failed. A scanner warning requires triage; it isn't a confirmed exploit. A compensating control changes the observed exploitability/impact but does not automatically eliminate root-cause risk.

## Stop gates

Immediately stop active tests if:
- target/scope/permission is uncertain
- real user data or production assets unexpectedly appear
- tests degrade application or third-party health
- repeated 5xx, unexpected rate limits or abnormal behavior signal instability
- evidence suggests irreversible change or harm
- credentials or private data risk being leaked by tooling

Report the blocked check, last safe observation, and the decision required to continue.

## Evidence chain

Attach or describe, with secrets redacted:
- candidate identifier (commit or build/deploy hash if available)
- target/environment and test timestamp
- control ID and security invariant
- preconditions and synthetic identity class
- safe request/action and response/outcome
- actual side effect or preserved state
- tool/command identifier and limitations

A later code or deployment change invalidates affected prior verification unless re-run or justified unaffected. Do not paste live bearer tokens, exploit-bearing URLs or customer data into broad reports.
