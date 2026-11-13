# Visualize discovery and verification workflow

## Invocation and authority

Invoked by `skills/visualize/SKILL.md` for multi-boundary discovery or independent assessment. The calling agent is the **sole coordinator** and owns scope, task ledger, stable IDs, reconciliation, source pinning, output paths and final status. This workflow coordinates investigations; it does not redefine graph semantics or implement the renderer.

All workers operate read-only within the same authorized roots. No worker may create or edit files under inspected application roots, run the application, perform live probes, generate tests, invoke deploy tools, or alter infrastructure. Workers return structured findings to the coordinator; they do not write the shared graph or output artifacts.

## 1. Set bounded effort

Budget is a ceiling, not an agent count:

| Mode | Concurrent investigator/reviewer contexts | Total delegated tasks, including retries | Follow-up waves |
| --- | ---: | ---: | ---: |
| `focused` | 2 | 3 | 0 |
| `standard` | 3 | 6 | 1 |
| `deep` | 5 | 10 | 1 |

Inventory authorized repository roots deterministically and group investigation tasks by logical ownership or cross-boundary contract, not one task per repository. Record per-repository revisions, inaccessible roots and uncovered flows; do not claim exhaustive coverage merely because a fixed task budget is exhausted. Prioritize independent graph verification over parallel discovery when the task budget is constrained. A separate Failure Verifier is commissioned only when a consequential fault hypothesis exists. If multiple contexts are unavailable, the coordinator investigates serially and marks all self-checks as non-independent. Never claim a role executed merely because it was described in a file.

## 2. Partition by investigation question

Identify independent subsystem ownerships, actual entrypoints, external contracts, or unresolved flows. Assign each bounded task to the reusable `agents/visualize-explorer/AGENT.md` role. Include:

- Authorization boundary and pinned repository revision(s).
- Specific responsibility, route, queue/topic, data sink, or unresolved binding to investigate.
- Maximum depth and stopping condition.
- Existing candidate IDs to reuse, to reduce duplicate naming.
- Required evidence and negative/unknown findings to return.

Do not partition solely by file count, framework name or a fixed number of services. A worker should return early when a prerequisite is absent or the assigned boundary cannot be read.

## 3. Reconcile one source-backed graph

Maintain a canonical claim ledger keyed by stable component, relationship and journey IDs. Merge reports only after inspecting supporting source pointers. Reconcile overlapping ownership, duplicate nodes, competing relation directions, unresolved targets, source-vs-deployment differences, and incompatible revisions. Record disputed claims; never let an agent's confidence score substitute for evidence.

Retain validated `domain`, `owner`, and `group_id` where source evidence establishes them. For execution flows, reconcile exact relation IDs, source and sink direction, and separate causal edges for branching or parallel outcomes. Do not serialize an invented order between asynchronous consumers. Build a top-level semantic architecture first. Do not recursively expand every component just because time or agents remain. For a user-selected component or flow, issue a focused follow-up task if it changes the current view materially and the budget permits it.

## 4. Verify representation and failure claims separately

Assign `agents/visualize-graph-verifier/AGENT.md` the final material component/relation/journey claims, with original source locators and known uncertainty. The verifier checks evidence, logical ownership, source coverage, and level-projected journeys. Feed its challenges back into reconciliation, then recheck changed material claims with an independent context when available; otherwise lower assurance.

For each *consequential suspected defect* (for example, producer topic with no located consumer, apparently dead route, or contradictory binding), commission `agents/visualize-failure-verifier/AGENT.md` with a falsifiable claim and its scope. The verifier actively searches for disconfirming configurations, external consumers, alternative routing, deployment profiles and other explanations. Its outcome is `CONFIRMED`, `DISPROVEN`, or `INDETERMINATE`; keep a `SUSPECTED` tag while a verdict is pending. Do not treat absent evidence outside authorized scope as proof of absence.

No defect verdict authorizes repair. If investigation confirms an issue, record it in the visualization only; never trigger a code-editing or debugging skill automatically.

## 5. Validate and hand off

Check ID uniqueness, acyclic containment, relation endpoints, source/snapshot provenance, journey projections, verdict linkage, redaction and scenario-mode honesty against the skill references. When available, use a deterministic validator and compatible 3D renderer. If either is missing, disclose which gates were manual and which were not exercised.

Return to the calling skill: final normalized graph, investigated journeys, unresolved edges and coverage, verified fault verdicts, real subagent participation evidence, accepted source snapshot, model validation findings, and renderer readiness. Stop at the agreed detail and verification budget; do not pursue infinite repo-wide completeness.
