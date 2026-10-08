# Data, Cryptography, Supply Chain and Operations

Apply controls where the assets, infrastructure and deployment model warrant them.

## Data lifecycle

Map classification, owners, authorized readers/writers, retention, backups, deletion, export, third parties, and logging. Inspect confidentiality/integrity controls at rest and in transit, data minimization, secret leakage in errors/logs, cross-tenant queries and privileged exports.

Where relevant check actual exposure paths rather than merely confirming an encryption library or an environment variable exists. Encryption at rest does not compensate for broken authorization.

## Credentials and cryptography

Inspect secret creation/storage/injection, access scope, rotation, leakage via source/history/CI/logs, and revocation. Use managed identity/secrets facilities when justified; do not assert all environment variables are inherently insecure or that every small app needs a vault.

Identify custom cryptographic protocols and key management as specialist-review candidates. Do not claim mathematical security from a superficial static review.

## Build and dependency supply chain

Use existing scanners where available for:
- pinned/locked dependency provenance and known advisories
- secret exposure in source and CI artifacts
- container/IaC misconfiguration
- CI token scope, untrusted PR execution and release provenance
- dangerous build hooks, unverified upstream artifacts and unsafe scripts

Distinguish severity from reachability and applicability. Report stale or unavailable advisory feeds, scan limitations and unresolved dependency reachability. A scanned SBOM is inventory, not a guarantee of safety.

## Infrastructure

When present inspect:
- public ingress/egress and TLS termination
- cloud IAM least privilege and workload identities
- runtime identities, network policy/segmentation, Kubernetes RBAC
- exposed admin/metrics/debug routes
- configuration and environment drift
- file/object storage access and backup isolation

Lack of source-controlled infrastructure is not proof of secure production configuration: mark outside scope or not verified.

## Security operations

Prioritize auditability for material security events (privilege change, access denial, credential change, money movement, sensitive exports). Examine monitoring, incident procedures, recovery and critical backup restorability only when evidence is accessible or specifically in scope.

Do not require an SIEM, WAF, SOC or formal incident team for all small applications. Do not imply code inspection proves organizational incident-response readiness.

## Evidence pitfalls

- Secret scanner clean != no secret in external storage/logs.
- Dependency scan clean != no vulnerable code or zero-days.
- TLS configured in source != live edge certificate verified.
- Encrypted database != confidentiality with compromised application authorization.
- Security logs enabled != sensitive values are redacted and alerts acted upon.
