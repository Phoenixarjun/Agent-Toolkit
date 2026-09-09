---
name: ui-design-build-review
description: "End-to-end UI workflow for substantial interface work: establish design intent, choose a direction, implement a bounded vertical slice, render at representative viewports, independently critique the result, revise blocking issues, and validate usability/accessibility before handoff."
---

# UI Design → Build → Review

Use for substantial page, feature, or application UI work where rendered quality matters.

Do not use for a one-line CSS fix.

## Stage 1 — Context

Collect only relevant evidence:

- request and acceptance criteria
- existing product/design guidance
- representative UI and components
- target files and architecture
- actual content shape
- technical constraints

Output:

```yaml
intent:
constraints:
existing_design_language:
open_material_unknowns:
```

If a material product decision is unknowable, ask one grouped question.

Otherwise infer reversible details.

## Stage 2 — Design brief

Apply `ui-ux-design`.

Produce an internal normalized brief using `templates/DESIGN-BRIEF.md`.

Set:

```text
creative_latitude: 0..3
motion_level: 0..3
density: compact | balanced | spacious
```

For substantial greenfield surfaces, internally create three distinct directions and choose one.

Freeze the selected direction before broad implementation.

## Stage 3 — Vertical slice

Implement the smallest slice that proves:

- hierarchy
- typography
- palette
- shape/elevation
- primary interaction
- responsive strategy
- motion philosophy

Prefer a representative section or primary screen over building the entire application before visual verification.

## Stage 4 — Rendered inspection

If browser/render tools are available, capture representative states at:

```text
mobile: 375–430px
desktop: 1280–1440px
```

Add other viewports when the product requires them.

Inspect actual pixels, not only source.

If browser tools are unavailable, mark rendered validation as unavailable instead of pretending.

## Stage 5 — Independent critique

When subagents are supported, dispatch `ui-critic` read-only against the rendered candidate and relevant intent.

The critic evaluates:

```text
intent fit
task clarity
hierarchy
responsive behavior
interaction states
accessibility signals
visual coherence
product specificity
generic-agent patterns
unnecessary complexity
```

The critic must separate blocking findings from preference.

## Stage 6 — Bounded refinement

Fix:

- requirement gaps
- usability defects
- accessibility defects
- broken responsive behavior
- incoherent visual-system choices
- clearly generic/unearned patterns
- implementation mismatch with the approved direction

Do not redo the whole aesthetic because of subjective preference.

Default correction budget:

```text
2 rendered refinement cycles
```

A third cycle requires a concrete unresolved outcome-level defect.

## Stage 7 — Quality gates

Verify what is available:

- keyboard operation for important flows
- visible focus
- semantic labels
- contrast
- reduced motion
- content overflow
- loading/empty/error states
- touch targets
- responsive layout
- actual primary task
- framework/build/type checks required by the repository

Automated accessibility checks are useful but do not replace judgment about task clarity or assistive-technology experience.

## Final state

Return one of:

```text
PASS
FIX
BLOCKED
NEEDS_USER
```

`PASS` requires the implemented candidate to satisfy the design intent and available validation gates.

`FIX` means one bounded correction remains.

`BLOCKED` means required evidence or tooling cannot be obtained safely.

`NEEDS_USER` means a real product decision materially changes the design and cannot be inferred.

## Handoff

```text
Status:
Direction:
Implemented:
Rendered:
Validated:
Remaining:
```
