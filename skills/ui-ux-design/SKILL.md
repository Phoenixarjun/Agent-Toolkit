---
name: ui-ux-design
description: "Design and implement context-specific, production-quality web interfaces. Use when creating, redesigning, styling, or materially improving pages, components, applications, dashboards, forms, landing pages, design systems, responsive layouts, visual hierarchy, typography, color, interaction, or motion. Starts from product intent and existing project context, calibrates creativity and motion to the use case, avoids generic AI-default aesthetics, preserves established design systems, and validates usability, accessibility, responsiveness, and rendered quality."
---

# UI/UX Design

## Core Law

```text
product intent > aesthetic novelty
usability > decoration
coherence > number of effects
existing design system > personal preference
rendered evidence > code-only confidence
```

Never begin by choosing a visual style. Begin by understanding what the interface must help a particular user accomplish.

## 1. Establish context

Inspect minimum relevant context before changing UI:

- user request and prior conversation
- existing `DESIGN.md`, brand guidance, screenshots, mockups, or design tokens
- current layout and representative screens
- existing shared components and interaction patterns
- target framework and styling approach
- device and accessibility constraints
- actual or representative content shape

For existing products, preserve established visual language unless redesign is explicitly requested. Do not introduce a second design system.

## 2. Recover design intent

Privately normalize the request:

```yaml
product:
primary_user:
primary_job:
surface:
trust_level:
brand_character:
creative_latitude:       # 0-3
motion_level:            # 0-3
information_density:     # compact | balanced | spacious
device_priority:
accessibility_target:
existing_system:
technical_constraints:
content_constraints:
must_preserve:
must_avoid:
distinctive_hook:
```

Use `templates/DESIGN-BRIEF.md` when the task warrants a persistent brief.

Do not interrogate the user by default. Ask a compact grouped question only when an unanswered choice would materially change the design and cannot be inferred from context.

## 3. Calibrate the design

Classify the surface before choosing aesthetics.

**Creative latitude:**

```text
0 — restrained    Enterprise, regulated, operational, high-trust, high-frequency tools.
1 — considered    Most product UI and SaaS. Distinctive details without sacrificing familiarity.
2 — expressive    Marketing, consumer, editorial, creator, launch, or brand-led experiences.
3 — experimental  Portfolio, campaign, art, entertainment, showcase, or unconventional work.
```

**Motion level:**

```text
0 — none       State changes clear without decorative motion.
1 — subtle     Fast feedback, opacity, small transforms, loading/state transitions.
2 — expressive Choreographed reveals, spatial transitions, intentional scroll motion.
3 — immersive  Motion is part of the experience. Use only when the product justifies it.
```

**Density:** `compact` (expert tools, dashboards) | `balanced` (general product) | `spacious` (marketing, editorial, premium)

Do not equate "premium" with dark backgrounds, giant text, glass, or excessive whitespace. Do not equate "professional" with visually anonymous.

## 4. Explore directions before coding

For substantial new UI, generate three meaningfully different directions internally.

Each direction must specify: hierarchy and composition, typography character, color strategy, shape/elevation strategy, imagery or graphic language, motion philosophy, one memorable product-specific idea, and major risk.

Do not create three cosmetic variants of the same layout.

Evaluate each against: product fit, user-task clarity, trust fit, brand fit, distinctiveness, accessibility, responsive viability, implementation cost.

Commit to one direction. If the user explicitly asks for options, show them before implementation. Otherwise choose internally.

## 5. Build a coherent visual system

Define only what the interface needs. Load `references/visual-system.md` when establishing or auditing a visual system from scratch or when detail on typography roles, color tokens, spacing, shape, or icon language is needed.

Core constraints regardless:

- use semantic color tokens, not raw values scattered through components
- use one dominant visual relationship rather than distributing many accent colors evenly
- do not use color as the only carrier of status or meaning
- use a repeatable spacing rhythm
- use native semantic controls before recreating them
- do not use emoji as default interface icons
- do not add decorative imagery that competes with the primary task

## 6. Design interaction states

For each important interaction, cover all states: `rest | hover | focus | active | selected | disabled | loading | empty | success | error`.

The user must understand what is interactive, what happened, what the system is doing, what changed, what can be undone, and how to recover from an error.

Prefer recognition over recall. For destructive operations, make consequences and recovery explicit.

## 7. Use motion intentionally

Motion must do at least one job: show cause and effect, preserve spatial continuity, establish hierarchy, explain state change, direct attention, or express brand character without blocking the task.

Do not animate simply because a library is available. Avoid motion that delays primary actions. Avoid simultaneous unrelated movement. Respect reduced-motion preferences.

For restrained products, excellent static hierarchy is better than unnecessary animation.

## 8. Avoid generic agent aesthetics

Before finalizing, check whether the interface depends on several of these without a product-specific reason:

- centered hero + badge + gradient headline + two CTA buttons
- identical rounded cards for every section
- purple/blue glow on a neutral dark background
- glassmorphism without a layering reason
- excessive gradient text or oversized radius everywhere
- floating mock dashboard cards or bento grids used only for fashion
- icon-in-colored-circle repeated across every feature
- decorative blobs unrelated to brand
- fake metrics, testimonials, logos, or charts
- huge headings compensating for weak hierarchy
- every section using the same spacing, rhythm, and animation
- visual complexity unsupported by the product

None is universally forbidden. The failure is unearned repetition.

Ask: *If the logo and copy were replaced, could this UI belong to almost any AI-generated SaaS site?* If yes, strengthen product specificity.

Read `knowledge/ui-ux/anti-generic-ui.md` when a design feels generic.

## 9. Implementation discipline

- reuse existing primitives before creating replacements
- separate page composition, reusable components, data access, and business logic per project architecture
- keep visual tokens centralized
- preserve responsive behavior from the beginning
- use semantic HTML and accessible primitives for composite interactions
- keep DOM order consistent with reading and focus order
- support real content lengths, not only ideal demo strings
- do not hard-code desktop assumptions
- avoid large dependencies for small visual effects

## 10. Render and judge

Code completion is not visual completion.

When rendering tools are available, inspect at minimum mobile (375–430px) and desktop (1280–1440px). Check:

- hierarchy is obvious within seconds
- primary action is discoverable
- spacing groups related content correctly
- typography remains readable
- content does not clip or overflow
- controls have clear states
- mobile composition is intentional, not merely stacked
- empty/loading/error states fit the system
- focus is visible and keyboard interaction works
- contrast is adequate and reduced motion remains usable
- long labels and realistic content survive
- the chosen design direction is still visible after implementation

If screenshots contradict the intended design, trust the screenshots and revise.

## 11. Review priority order

```text
1. task completion
2. usability
3. accessibility
4. hierarchy
5. responsive behavior
6. consistency
7. product specificity
8. visual refinement
9. motion
10. decorative detail
```

Do not polish shadows while the task flow is unclear. Do not trade accessibility for novelty.

## 12. Stop condition

A UI is ready when:

- the primary user task is clear
- the chosen design direction is coherent
- important states are covered
- responsive behavior is deliberate
- accessibility fundamentals are satisfied
- implementation matches the existing architecture
- no obvious generic-agent pattern dominates without justification
- rendered review reveals no blocking visual or interaction defect
- additional changes would be preference-level rather than outcome-level

## Final response

```text
Direction: <one sentence>
Implemented: <key surfaces>
Validated: <rendered sizes / interaction / accessibility checks actually performed>
Assumptions: <only material inferred decisions>
Residual: <real remaining risk or None>
```

Never claim browser, accessibility, or visual validation that was not actually performed.
