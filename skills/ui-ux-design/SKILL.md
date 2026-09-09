---
name: ui-ux-design
description: "Design and implement context-specific, production-quality web interfaces. Use when creating, redesigning, styling, or materially improving pages, components, applications, dashboards, forms, landing pages, design systems, responsive layouts, visual hierarchy, typography, color, interaction, or motion. Starts from product intent and existing project context, calibrates creativity and motion to the use case, avoids generic AI-default aesthetics, preserves established design systems, and validates usability, accessibility, responsiveness, and rendered quality."
---

# UI/UX Design

Create interfaces that feel designed for their product rather than generated from a generic frontend template.

## Core law

```text
product intent > aesthetic novelty
usability > decoration
coherence > number of effects
existing design system > personal preference
rendered evidence > code-only confidence
```

Never begin by choosing a fashionable visual style.

Begin by understanding what the interface must help a particular user accomplish, what the product should feel like, and what constraints make a design appropriate.

## 1. Establish context

Before changing UI, inspect the minimum relevant context available:

- user request and prior conversation
- existing `DESIGN.md`, brand guidance, screenshots, mockups, or design tokens
- current layout and representative screens
- existing shared components and interaction patterns
- target framework and styling approach
- device and accessibility constraints
- actual content or representative content shape

For existing products, preserve established visual language unless redesign is explicitly requested.

Do not introduce a second design system because another library or style is easier.

## 2. Recover design intent

Privately normalize the request into:

```yaml
product:
primary_user:
primary_job:
surface:
trust_level:
brand_character:
creative_latitude:
motion_level:
information_density:
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

### Ask or infer

Do not interrogate the user by default.

Ask a compact grouped question only when an unanswered choice would materially change the design and cannot be inferred from context.

High-value questions are:

1. Who is the primary user and what must they accomplish on this screen?
2. Should the product feel restrained/professional, expressive/brand-led, or experimental?
3. How much motion is appropriate: none, subtle, expressive, or immersive?
4. Is the experience dense and operational or spacious and presentation-led?
5. Is there an existing brand/design system or reference that must be preserved?
6. Are there accessibility, regulatory, device, or performance constraints that materially change the solution?

If sufficient context exists, infer sensible defaults and proceed.

Never ask a question merely to avoid making a reversible design decision.

## 3. Calibrate the design

Classify the surface before choosing aesthetics.

### Creative latitude

```text
0 — restrained
Enterprise, regulated, operational, high-trust, high-frequency tools.

1 — considered
Most product UI and SaaS. Distinctive details without sacrificing familiarity.

2 — expressive
Marketing, consumer, editorial, creator, launch, or brand-led experiences.

3 — experimental
Portfolio, campaign, art, entertainment, showcase, or explicitly unconventional work.
```

### Motion level

```text
0 — none
State changes remain clear without decorative motion.

1 — subtle
Fast feedback, opacity, small transforms, loading/state transitions.

2 — expressive
Choreographed reveals, spatial transitions, intentional scroll or section motion.

3 — immersive
Motion is part of the experience itself. Use only when the product justifies it.
```

### Density

```text
compact — expert tools, dashboards, operations
balanced — general product UI
spacious — marketing, editorial, premium presentation
```

Do not equate "premium" with dark backgrounds, giant text, glass, gradients, or excessive whitespace.

Do not equate "professional" with visually anonymous.

## 4. Explore directions before coding

For substantial new UI, generate three meaningfully different directions internally.

Each direction must specify:

- hierarchy and composition
- typography character
- color strategy
- shape/elevation strategy
- imagery or graphic language
- motion philosophy
- one memorable product-specific idea
- major risk

Do not create three cosmetic variants of the same centered hero or card grid.

Evaluate each direction against:

```text
product fit
user-task clarity
trust fit
brand fit
distinctiveness
accessibility
responsive viability
implementation cost
```

Commit to one direction.

If the user explicitly asks for options, show them before implementation. Otherwise choose internally.

## 5. Build a coherent visual system

Define only what the interface needs.

### Typography

Choose typography from the content and product character.

Establish roles for:

- display/hero when justified
- page title
- section heading
- body
- label/control
- caption/metadata
- data/code when needed

Use size, weight, line-height, width, spacing, and contrast together to establish hierarchy.

A familiar font is valid when legibility, performance, platform familiarity, international coverage, or dense application UI makes it the better choice.

A distinctive font is valid when brand expression materially benefits.

Never choose or reject a font solely because other AI agents often use it.

### Color

Build color around roles:

```text
background
surface
text-primary
text-secondary
border
brand
accent
interactive
success
warning
danger
focus
```

Prefer semantic tokens over raw values scattered through components.

Use one dominant visual relationship rather than distributing many accent colors evenly.

Do not use color as the only carrier of status or meaning.

### Spacing and layout

Use a repeatable spacing rhythm.

Choose layout from the content hierarchy, not from a default component showcase.

Vary composition when it improves the product:

- asymmetric emphasis
- split layouts
- editorial rhythm
- dense application grids
- anchored side navigation
- full-bleed media
- controlled overlap
- intentionally quiet single-column layouts

Novel composition must not make navigation, reading order, or interaction ambiguous.

### Shape and depth

Decide:

- corner language
- border language
- elevation
- layering
- surface contrast

Avoid giving every container the same rounded floating-card treatment.

A section does not need a card merely because it contains related information.

### Icons and imagery

Use a coherent icon language.

Prefer real product imagery, meaningful illustration, charts, diagrams, or photography when they carry information or brand character.

Do not use emoji as default interface icons.

Do not add decorative imagery that competes with the primary task.

## 6. Design interaction, not only appearance

For each important interaction define:

```text
rest
hover
focus
active
selected
disabled
loading
empty
success
error
```

The user must understand:

- what is interactive
- what happened after an action
- what the system is doing
- what changed
- what can be undone
- how to recover from an error
- what to do next

Prefer recognition over recall.

Use native semantic controls before recreating them.

For destructive or consequential operations, make consequences and recovery explicit.

## 7. Use motion intentionally

Motion must do at least one job:

- show cause and effect
- preserve spatial continuity
- establish hierarchy
- explain state change
- direct attention
- express brand character without blocking the task

Prefer a few coordinated moments over animation on every element.

Do not animate simply because a motion library is available.

Avoid motion that delays primary actions.

Avoid simultaneous unrelated movement.

Respect reduced-motion preferences.

For restrained products, excellent static hierarchy is better than unnecessary animation.

## 8. Avoid generic agent aesthetics

Before finalizing, check whether the interface depends on several of these without a product-specific reason:

- centered hero + badge + gradient headline + two CTA buttons
- identical rounded cards for every section
- default three-column feature grids
- bento grids used only because they are fashionable
- purple/blue glow on a neutral dark background
- glassmorphism without a layering reason
- oversized radius everywhere
- pill-shaped controls everywhere
- excessive gradient text
- floating mock dashboard cards
- icon-in-colored-circle repeated across every feature
- decorative blobs and grids unrelated to brand
- fake metrics, testimonials, logos, or charts
- huge headings compensating for weak hierarchy
- every section using the same spacing and rhythm
- every interaction using the same animation
- arbitrary stock illustration
- visual complexity unsupported by the product

None is universally forbidden.

The failure is unearned repetition.

Ask:

> If the logo and copy were replaced, could this UI belong to almost any AI-generated SaaS site?

If yes, strengthen product specificity.

Read `knowledge/ui-ux/anti-generic-ui.md` when a design feels generic.

## 9. Implementation discipline

When implementing:

- reuse existing primitives before creating replacements
- separate page composition, reusable components, data access, schemas, and business logic according to the project's architecture
- keep visual tokens centralized
- preserve responsive behavior from the beginning
- use semantic HTML
- use accessible primitives for composite interactions
- keep DOM order consistent with reading and focus order
- do not hard-code desktop assumptions
- support real content lengths, not only ideal demo strings
- avoid introducing a large dependency for a small visual effect
- match implementation complexity to the chosen direction

For React/Next.js, follow the project's existing engineering rules and performance guidance rather than embedding framework-specific rules into this skill.

## 10. Render and judge

Code completion is not visual completion.

When rendering/browser tools are available, inspect at minimum:

```text
mobile
desktop
```

Add tablet or wide desktop when layout behavior materially changes.

Check:

- hierarchy is obvious within seconds
- primary action is discoverable
- spacing groups related content correctly
- typography remains readable
- content does not clip or overflow
- controls have clear states
- mobile composition is intentional, not merely stacked
- empty/loading/error states fit the system
- focus is visible
- keyboard interaction works
- contrast is adequate
- reduced motion remains usable
- long labels and realistic content survive
- the design direction is still visible after implementation

If screenshots contradict the intended design, trust the screenshots and revise.

## 11. Review against intent

Use this order:

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

Do not polish shadows while the task flow is unclear.

Do not trade accessibility for novelty.

Do not preserve a clever visual idea that weakens the product.

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

Avoid endless aesthetic churn.

## Final response

Keep the handoff concise.

Report:

```text
Direction: <one sentence>
Implemented: <key surfaces>
Validated: <rendered sizes / interaction / accessibility checks actually performed>
Assumptions: <only material inferred decisions>
Residual: <real remaining risk or None>
```

Never claim browser, accessibility, or visual validation that was not actually performed.
