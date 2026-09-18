# Visual System Reference

Load this reference when establishing or auditing a visual design system from scratch, or when detail on typography roles, color token architecture, spacing rules, shape/elevation, or icon language is needed to make specific design decisions.

## Typography

Choose typography from content and product character. Establish roles only for what the interface needs:

```text
display/hero     — only when justified by marketing or brand expression
page-title       — primary surface or screen label
section-heading  — major content divisions
body             — primary reading text
label/control    — form labels, button text, nav items
caption/metadata — secondary descriptive text
data/code        — when the product handles structured data or code
```

Build hierarchy with size, weight, line-height, letter-spacing, and contrast together — not size alone.

**Font selection rule:** A familiar font is valid when legibility, performance, platform familiarity, international coverage, or dense application UI makes it the better choice. A distinctive font is valid when brand expression materially benefits. Never choose or reject a font solely because other AI agents often use it.

**Minimum:** body text at 16px equivalent, 4.5:1 contrast against background.

## Color System

Build color around semantic roles, not raw values:

```text
background       — page or surface base
surface          — elevated containers, cards, panels
surface-raised   — modals, popovers, higher elevation
text-primary     — primary reading and content text
text-secondary   — supporting labels, metadata, placeholder
border           — dividers, input outlines, separators
brand            — primary brand expression
accent           — secondary brand or highlight
interactive      — links, clickable controls
interactive-hover — hover state of interactive
success          — positive state or confirmation
warning          — caution, non-blocking alert
danger/error     — destructive action or failure
focus            — keyboard focus ring
overlay          — scrim, backdrop, modal overlay
```

Use semantic tokens throughout components — never scatter raw hex values.

Use one dominant visual relationship (e.g., brand-on-surface). Additional accent colors weaken hierarchy.

Dark mode: maintain the same semantic roles; swap surface and background values; adjust text contrast; do not simply invert.

## Spacing

Use a consistent spacing scale (e.g., multiples of 4px or 8px). Apply it to margins, padding, gaps, and layout gutters uniformly.

```text
xs   4px    inline details, icon gaps
sm   8px    tight component internals
md   16px   standard component padding
lg   24px   section internal spacing
xl   32px   between major components
2xl  48px   section breaks
3xl  64px+  page-level sections (spacious density)
```

Choose layout from content hierarchy, not from a default component showcase.

Vary composition when it improves the product: asymmetric emphasis, split layouts, editorial rhythm, dense application grids, anchored side navigation, full-bleed media, intentional quiet single-column layouts.

Novel composition must not make navigation, reading order, or interaction ambiguous.

## Shape and Elevation

Decide the shape language once and apply it consistently:

- **corner language** — choose one radius character: sharp (0px), soft (4–6px), rounded (8–12px), pill (full). Do not mix extreme radii without a reason.
- **border language** — use borders for separation or definition, not decoration. Avoid adding borders where surface contrast already separates layers.
- **elevation model** — use shadow or background color to signal elevation. Do not stack both indiscriminately.
- **layering** — establish a clear z-index intention: base, sticky, dropdown, modal, toast.

Avoid giving every container the same rounded floating-card treatment. A section does not need a card merely because it contains related information.

## Icons and Imagery

**Icons:** Use a coherent, single icon set. Apply consistent size, stroke weight, and optical centering. Fill vs. outline should have a semantic meaning (e.g., selected vs. unselected) or remain consistently one style.

**Imagery:** Prefer real product imagery, meaningful illustration, charts, diagrams, or photography when they carry information or brand character. Do not add decorative imagery that competes with the primary task.

**Illustration style:** Choose one illustration language — line, filled, isometric, abstract, photographic. Do not mix styles without a product reason.

**AI-generated imagery:** Acceptable when it matches the product's visual language and does not introduce false authority (fake logos, testimonials, or data).
