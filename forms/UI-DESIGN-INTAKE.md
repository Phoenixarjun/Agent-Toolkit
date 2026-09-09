# UI Design Intake

Use only the questions needed to resolve material ambiguity.

## Minimal intake

```text
1. What is this interface for, and what is the single most important thing the user must accomplish?
2. Who is the primary user?
3. Which direction is closer: restrained/professional, expressive/brand-led, or experimental?
4. Motion: none, subtle, expressive, or immersive?
5. Is there an existing design system, brand guide, screenshot, or product style that must be preserved?
```

## Extended intake

Use when product/design constraints are genuinely unknown.

```yaml
product:
surface:
primary_user:
primary_job:
secondary_jobs:
business_goal:
trust_or_risk_level:
brand_character:
creative_latitude: 0 | 1 | 2 | 3
motion_level: 0 | 1 | 2 | 3
density: compact | balanced | spacious
device_priority:
accessibility_or_regulatory_target:
existing_design_system:
existing_component_library:
content_available:
imagery_available:
must_preserve:
must_avoid:
reference_products:
technical_stack:
performance_constraints:
deadline_or_scope:
```

## Question discipline

Do not ask all questions automatically.

Ask when the answer changes architecture, hierarchy, trust treatment, visual direction, or interaction.

Infer reversible choices.

For autonomous execution, record assumptions instead of blocking on preference-level unknowns.
