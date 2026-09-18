# Review Risk Reference

Load this reference when the candidate touches a high-risk domain or when classifying finding severity requires explicit anchoring.

## High-Risk Domains

Treat crossing an explicit approval boundary in any of these domains as a blocking finding even when the change appears technically necessary:

```text
authentication and authorization
security and privacy boundaries
data integrity and correctness
concurrency and ordering
distributed consistency
schema changes and migrations
public API and contract compatibility
billing and payments
infrastructure and production configuration
external side effects
shared contracts and interfaces
large cross-module behavior
```

## Severity Classification

**critical** — exploitable security vulnerability, data loss or corruption, broken auth, unrecoverable state, regression in a core user flow with no workaround.

**high** — significant correctness failure, missing required validation or error path, compatibility break, unauthorized approval-boundary crossing, stale validation against a changed candidate.

**medium** — partial coverage of a requirement, missing tests for changed behavior, accidental duplication, scope drift with low-blast-radius.

**low** — style violation that materially harms readability, minor inconsistency, non-blocking refinement opportunity.

## Risk Heuristics

When a changed path touches a high-risk domain, expand inspection to:

- the full code path from entry point to effect
- all callers and downstream consumers
- existing tests and whether they cover the changed behavior
- rollback and recovery implications
- whether the change is reversible without a migration

Do not report style preferences as high or critical findings.

Do not manufacture findings to make the review appear thorough.

## Approval Boundary Protocol

When the candidate crosses an approval boundary listed in the intent contract without documented user authorization:

1. Classify as a `FIX` finding regardless of technical correctness.
2. Name the specific boundary crossed.
3. State the required resolution: user authorization, removal, or separation.
4. Do not offer to "document it and proceed."
