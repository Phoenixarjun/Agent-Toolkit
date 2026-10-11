# Security Invariant and Operation-Path Mapping

Load when building a full security audit's coverage model. This is an *operational reasoning pattern*, not a replacement for ASVS or a vulnerability taxonomy.

## Begin with assets and authority

Ask which principals can act on which resources, in which states, across which trust boundaries. Translate policy into **falsifiable security properties**. Distinguish product policy (requires product owner evidence) from default-deny requirements at a genuine private-data boundary. Do not invent a rule merely to make a test fail.

### Operation record

```
ID: O-001
Principal: tenant-A/user-A (synthetic)
Action: READ
Resource: tenant-B/private-invoice
Context: cross-tenant, authenticated, user role
Expected: DENY
Observed: UNKNOWN until tested
Invariant: I-tenant-isolation
Surface: GET /invoices/{id}
Enforcement: controller -> policy -> resource query
Evidence: static trace / approved HTTP observation
```

For an action with both valid and invalid actors, pair **ALLOW** and **DENY** probes when useful; an endpoint returning universal 403 is not proof that authorization works. Also check the **side effect**, not just the status code for writes.

## Two-direction reasoning

**Forward:** For each entry point, track input origin, authentication/session binding, role/attribute scope, validation/serialization, side effects and eventual stored/readable data.

**Backward:** From each important resource/sink (secret, private record, payment/refund, delete, privileged tool, cloud credential, export file) enumerate reachable callers, including indirect workers, event handlers, webhooks, admin/debug endpoints and alternate API versions.

Questions at every edge:
- What authority crosses this boundary, and who checks it?
- Can identity, tenant, role, object ID, amount or intent be chosen by the caller?
- Is enforcement server-side and applied at this path, not only UI/gateway?
- Is the access policy still valid after retries, concurrency, state transition, replays or delegation?
- Is a downstream service incorrectly trusting caller-supplied context?
- Does an overlooked read/list/export reveal private information?

## No meaningless Cartesian explosion

Select operation combinations by consequence and representative policy classes. E.g., same tenant owner/non-owner; cross-tenant; anonymous; privileged vs unprivileged; stale/revoked identity. Broaden only when differentiated behavior or different enforcement points justify it.

## Coverage closure

- A covered operation has a documented expected policy, source path/boundary and meaningful observation. `VERIFIED` requires actual supporting evidence for **that operation**, not nearby middleware.
- Mark missing authorization policy `UNDETERMINED`; consult authoritative spec or owner instead of guessing.
- Unknown alternate entry points remain a coverage gap. A source tree grep with no hits does not prove a public route cannot exist in a different build.
- Failing negative probe with incorrect test credentials or unprovisioned fixture is `INCONCLUSIVE`, not `FAILED`.
- Disclose how many material operations were examined, which were blocked, and why. The count is a scope measure, not a security score.
