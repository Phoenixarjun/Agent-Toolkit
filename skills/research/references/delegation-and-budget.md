# Delegation and resource budgets

Load only when work has independent research questions or resource constraints.

## Separation contract

- Parent coordinates and owns Q-ID coverage, deduped source lineage, scope, budget and report. The parent does not claim an agent role it did not run.
- Scouts are replicated instances of one role. Give each only its own bounded question list and local evidence pointers. Return source records, candidate claim records, open questions and resource usage, not report sections.
- Coverage Critic checks *search-space sufficiency*, not claim correctness. This is a distinct task from Evidence Verifier.
- Verifier receives candidate claims and underlying source locators, without treating Scout confidence as proof. Independent context IDs must differ from Scout context IDs; same-session self-review cannot be reported as independent.
- Synthesizer creates one report after reconciliation; avoid parallel report-writing.

## Budgets: defaults, not entitlements

| Mode | Maximum concurrent scouts | Total scout task cap | Follow-up policy |
| --- | ---: | ---: | --- |
| Focused | 1 | 1 | None unless user expands |
| Standard | 2 | 4 | Up to one targeted wave |
| Deep | 4 | 8 | Up to two bounded waves |

These caps are **conservative proposed defaults**, subject to lower user/tool limits. Counts are upper bounds, not mandatory work; `0` delegated scouts is valid for focused research. The total cap counts retries and aborted tasks. Track actual searches/tool calls if available and stop within budget. A model name is not a portability contract; adapters may route roles based on actual model capabilities and pricing. Material synthesis and contradiction resolution require competent reasoning, not blindly choosing the cheapest model.

Scout output budget: return at most the minimal records needed for Q-ID coverage and claim provenance, with stable IDs. Keep long raw documents at origin; return excerpts/locators, not full scraped copies.

## Routing and failure

If a question is not decomposable, use one evidence lane. If independent context spawning is unsupported, execute serially with explicit `independence=unavailable` and no claim of multi-agent review. If a Scout runs out of budget, parent marks unanswered Q-IDs and does not silently reassign unlimited work. Only request additional authorization for gaps whose resolution may change a material conclusion.
