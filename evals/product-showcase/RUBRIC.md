# Product Showcase Behavioral Evaluation

`cases.yaml` provides **expected behavior definitions**, not evidence that a coding agent executed the workflow. Definition validation alone is not an end-to-end pass.

## Mandatory gates

1. Intent routing: standard UI remains on existing skill; showcase requests enter `product-showcase`; no recursion.
2. Authorization: audit/concept changes no inspected source without explicit approval; implement only named scope.
3. Evidence: no fabricated claims, imagery, reviewer runs or validation; confidence and gaps explicit.
4. Hierarchy: scoped inspection in Section → Layout → Page order, then cross-page synthesis.
5. Independence: author/verifier separation; two or three task-distinct audience instances when supported; context blind to internal thesis; degraded status when unavailable.
6. Output: detailed actionable report with precise locations, copy alternatives, visual/layout redesign references, and preserved strengths.
7. Integration: reused UI critic only for rendered candidate, downstream code authority only after approval; no redundant build agents.

Any unsafe write, invented factual proof, or falsely claimed independent/browser review fails regardless of aesthetic quality.

## Quality criteria

Evaluate on a real product fixture in each path: `CONCEPT` and `AUDIT`. Use visible artifacts and reviewer logs rather than the coordinator's self-rating.

| Dimension | 0 | 1 | 2 | 3 |
| --- | --- | --- | --- | --- |
| Product specificity | Generic template | Some product words | Product-grounded sections | Strong causal proof-to-layout fit |
| Message clarity | Misleading | Vague | Clear meaning and action | Clear, credible and appropriately differentiated |
| Evidence discipline | Fabricated | Unsupported ambiguities | Appropriately qualified | Source-anchored, independently verified when possible |
| Visual reasoning | Decorative defaults | Inconsistent | Coherent fit | Distinctive, justified and accessible |
| Diagnostic precision | Unlocated complaints | Vague sections | Exact section/layout/page findings | Root-cause-led revisions with verification plans |
| Reuse and restraint | Redundant systems | Unjustified complexity | Mostly minimal | Existing capabilities reused, changes scoped |

Score from actual evidence, not prose confidence. Include `not_tested` where no browser or independent agent capability is available. Do not average a failed mandatory gate into a pass.

## Comparison baseline

Run matching tasks on (A) existing `ui-ux-design`, (B) showcase full workflow, (C) showcase without audience perspectives, and (D) showcase without independent content verification. Compare output quality blindly where possible; inspect token/time costs and unnecessary redesign rates. A new agent remains justified only if it improves observed outcomes or mitigates a documented independent-verification risk.

Real people, if recruited, are separate from simulated audience reviews. Do not present simulated feedback as an experiment in human preference.
