# Security Audit

**Independently examine the security boundaries that matter to this application.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/security-audit/SKILL.md) |
| **Best for** | Authorized application security assessments |
| **Execution cost** | High to very high due to independent investigation |
| **Output** | Security assurance report, evidence ledger, confirmed and unresolved findings |

## The problem

Generic checklists can demand irrelevant controls while missing a real authorization bypass or exposed data path. One investigator may also overlook routes or become attached to its first hypothesis.

## When to use it

Use Security Audit when you need a documented, risk-proportionate examination of an application's actual security properties. Impact and audit depth are separate: a small app can contain a critical vulnerability, and a regulated product does not need unrelated controls.

## How it works

1. Define the authorized target, impact, depth, sensitive assets, and trust boundaries.
2. Map the security properties and operations that must be allowed or denied.
3. Run independent Authority and Trust-Path investigations.
4. Use a separate Coverage Critic to challenge missing paths and a fresh Verifier to challenge material findings.
5. Reconcile controls, evidence, unresolved gaps, and the final assurance conclusion.

## Modes

| Audit depth | Meaning |
| --- | --- |
| Sanity | Narrow, explicit assurance scope |
| Standard | Normal risk-based assessment |
| Deep | Wider threat-driven coverage for consequential targets |

**Independent contexts are mandatory for a completed audit in every mode.** A runtime without actual isolation can produce preliminary observations, not a completed independent audit.

## Example request

> Audit this multi-tenant API at Deep depth. Verify cross-tenant reads, exports, privileged actions, and asynchronous workers. Use only the authorized staging environment. Report findings without implementing fixes.

## What you get

A plain-language security conclusion with findings and their evidence, coverage limitations, and a remediation handoff. A later implementation must happen in a **fresh context**, followed by another independent audit of the changed revision.

## Boundaries and dependencies

This capability is **audit-only**. It is not a certification, automatic compliance judgment, or permission to attack production. A complete installation needs the Security Audit workflow, specialist agents, host subagent isolation, and the appropriate validator. See the [canonical skill](../../skills/security-audit/SKILL.md) for exact contracts.

**Cost guidance:** High relative cost reflects parallel or separate reviews, not a quoted currency or token amount.
