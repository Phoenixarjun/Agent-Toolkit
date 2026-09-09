# UI/UX Review Rubric

Score each dimension from 0–4.

```text
0 — broken
1 — materially weak
2 — acceptable
3 — strong
4 — exceptional for this context
```

## Dimensions

### Task clarity

Can the primary user identify the purpose and next action quickly?

### Information hierarchy

Do visual relationships match actual importance?

### Usability

Are interactions predictable, efficient, recoverable, and understandable?

### Accessibility

Are semantic, keyboard, focus, contrast, motion, and content fundamentals handled?

### Responsive behavior

Does the design intentionally adapt without losing priority or functionality?

### Visual coherence

Do typography, color, spacing, shape, elevation, imagery, and motion behave as one system?

### Product fit

Does the interface fit the audience, trust level, workflow, and brand?

### Product specificity

Does it contain meaningful decisions that would change for a different product?

### Content resilience

Does realistic, long, empty, loading, error, and dynamic content survive?

### Implementation fit

Does the implementation reuse the existing architecture/design system and avoid unnecessary complexity?

## Gate

A candidate should not pass with:

```text
Task clarity < 3
Usability < 3
Accessibility < 3
Responsive behavior < 3
```

unless a dimension is genuinely not applicable.

A high visual-coherence score cannot compensate for a broken task.

## Preference separation

A reviewer must label subjective alternatives as `PREFERENCE`.

Examples:

```text
"I prefer less rounding."
"I would use another font."
"I like the dark theme more."
```

These are not defects unless the current choice contradicts intent, evidence, or system rules.
