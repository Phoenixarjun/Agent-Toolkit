# Product Showcase Workflow (UI/UX V2)

`product-showcase` is a specialized workflow **behind** the existing `ui-ux-design` skill, not a new competing user-facing skill. It serves product-marketing/showcase concept requests and audits of built product websites; standard application UI continues through `ui-design-build-review` when a substantial implementation loop is needed.

## Invocation by intent

- `ui-ux-design showcase concept for this developer tool` → `CONCEPT`, report-only unless a build is explicitly authorized.
- `ui-ux-design showcase audit this existing marketing website` → `AUDIT`, read-only by default.
- `ui-ux-design implement the approved showcase direction` → verified approval gate, existing `/code` and UI implementation workflow.
- `ui-ux-design fix button spacing` → direct skill, no showcase orchestration.

These strings illustrate intent; runtime command syntax is adapter-specific. The skill must not re-enter showcase when called by the showcase workflow for its design contribution.

## What it does

The coordinator uses source-grounded product truth and real proof assets, proposes factual messaging with an independent verifier, explores product-specific design directions through existing UI/UX, and commissions **two or three isolated simulated audience reviews** with distinct arrival tasks. These dynamic reviewers share one reusable contract, not a separate permanent role per fictional customer. Existing `ui-critic` reviews only actual rendered candidates. A coordinator reconciles substantive findings by root cause rather than agent vote counts.

Every scoped page is analyzed **section by section → layout by layout → page by page**, then across pages. The final `SHOWCASE-REPORT` contains detailed copy, proof, placement, responsive and motion recommendations, preserved strengths, alternative creative directions where justified, and optional properly labeled reference imagery. The report is the default deliverable, not source mutation.

## Fallback and approval

If isolated subagents, browser rendering, or image generation are unavailable, record the missing capability and the reduced assurance. Do not fabricate independent reviewers or claim a concept image is an implemented website. Actual source changes require explicit approval of direction, repository paths, preservation constraints and acceptance criteria. Implementation and review reuse the existing coding/UI capabilities.

## Installation and validation

The package adds canonical workflow, three bounded agents, one knowledge document, a report template and evaluations; adjusts UI/UX intent routing and a few existing knowledge references. Its catalog version proposes UI/UX **2.0.0** and marks the new workflow/agents experimental **0.1.0**. A repository maintainer must reconcile this candidate with the live `dev` branch and use the existing installer/validator; do not overwrite unrelated newer edits.

Run existing repository validation, definition-eval validation and representative runtime tests. Definition validation is **not** proof of agent output quality. Test a real pre-build product brief and a real existing-site audit before promoting workflow maturity.
