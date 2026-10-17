# Impact Planning and Handoff

Separate **current system facts** from **future plan proposals**. An evidence-backed graph may establish existing ownership; it cannot itself decide that a new architecture is the only correct choice.

For each material responsibility:

1. Identify current owner(s), enforcement points, upstream/downstream consumers, and observed invariants.
2. State intended owner and reason. Distinguish logically duplicate behavior from necessary independent enforcement and defense-in-depth.
3. List required adjustments and any transitional compatibility path (old/new formats, dual-read or dual-write hazards, request authentication vs per-resource authorization, schema migration, deploy ordering, staged rollout).
4. For removals, require a retirement proof checklist: replacement behavior validated, no active consumers still depend on it, authorization and error handling remain effective, fallback/rollback plan exists. Do not present deletion as authorized.
5. Order changes by dependency and safe rollout, not folder order. Explain parallelizable steps and integration gates.
6. Identify tests at public seams, contract tests, negative/error paths, migration/backward compatibility, and required human approval or separate Security Audit.
7. Reference supporting claim IDs from the ledger. OPTIONAL improvements must not be represented as essential requirements. Expose undecidable trade-offs.

Output an implementation plan that another agent can use in a new context without inheriting your unverified guesses. The implementing agent should independently recheck the repository revision and evidence, capture or reconcile intent, and use appropriate development/quality skills. Exploration is not authorization to edit, commit, deploy or remove code.
