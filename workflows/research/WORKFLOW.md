# Research Workflow

## Invocation and owner

Used by `skills/research/SKILL.md` for scoped multi-question or Deep investigation when real independent contexts are supported. The parent orchestrator owns all mutable state, budget accounting, decisions and final report. This workflow is **not** a second skill and does not override the skill's evidence or safety contracts.

## Sequence and gates

1. **Scope**: Capture research question, stakeholder decision, temporal boundaries, source permissions, output, budget and exit criteria. Create `Q-...` ledger and mark required questions.
2. **Plan**: Assign disjoint subquestions and evidence perspectives to Scout instances, each with bounded tools, task tokens/searches, source and time requirements. Count every dispatched task, including retries. Save budget.
3. **Discover**: Spawn Scout contexts where available. Collect source and candidate claim records, never freeform ready-to-publish prose. Verify IDs, question ownership, sources and provenance before merging; repair/reject malformed records without changing source meaning.
4. **Critique coverage**: Fresh critic context maps required Q-IDs to findings and highlights omitted perspectives, source lineage duplication, conflict and temporal gaps. Parent approves at most the remaining budgeted follow-up wave for material gaps. Mark unanswered questions when more evidence is inaccessible or out of budget.
5. **Verify**: Fresh verification context receives evidence records and underlying source locators. Challenge material claims and chart calculations; confirm source correspondence or mark gaps. Do not describe parent self-review as independent verification. If external contexts are unavailable, record `independence=unavailable` and use partial assurance.
6. **Reconcile**: Parent resolves Q-ID coverage and claim statuses, preserves qualified/disputed data, checks that synthesis is possible without fabricating missing points. No new unsourced claims may be added during synthesis.
7. **Validate**: If available, run the canonical deterministic record validator. Failed structure blocks report rendering and final `complete`. Review semantic claims separately.
8. **Publish**: Produce one coherent report, use Markdown by default, Deep optional Evidence Audit HTML via canonical renderer. Check source links, numeric units and scope/as-of. Output `complete`, `partial`, or `blocked` with limitations; stop.

## Delegation contracts

| Role | Input | Allowed output | Boundary |
| --- | --- | --- | --- |
| Scout | Q IDs, included/excluded areas, time range, search budget | sources, candidate claims, gaps, calls used | No final report or source-free confidence |
| Coverage Critic | Research brief, Q ledger, source lineage summary, bounded findings | missing Q IDs, repeated or weak coverage, follow-up recommendations | Does not certify factual truth |
| Evidence Verifier | Candidate claim IDs and original source locators | per-claim verification verdict, caveat, check method | Independent context; cannot infer truth from schema alone |
| Parent/Synthesizer | Accepted/qualified evidence, unresolved questions, budget | reconciled ledger, coherent report | No parallel section-authoring; no invented facts |

## Assurance policy

For Deep `complete`, coverage critic and verifier must have actually executed in distinct contexts, all material claims must have independent verifications, all mandatory Q-IDs answered, and validated record must pass. A blocked independent context downgrades to `partial` even if some research is useful. A single-agent serial run may still return valuable analysis, but not the independent assurance label.

No mandatory fixed number of scouts. Focused needs no orchestration. Broad targets without independent agent support must report actual limitations, not spawn fictional agents. Do not edit production systems, expose private evidence or publish externally without permission.
