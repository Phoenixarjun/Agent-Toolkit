# UI/UX Design

**Create interfaces that belong to the product, not a generic template.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/ui-ux-design/SKILL.md) |
| **Best for** | Building, redesigning, or materially improving web interfaces |
| **Execution cost** | Moderate to high; rises with iteration and browser testing |
| **Output** | Implemented UI or design decisions with rendered validation |

## The problem

Coding agents can produce technically valid interfaces that feel generic, ignore a project's visual language, and remain untested on real screens or devices.

## When to use it

Use for product UI, dashboards, forms, landing pages, responsive layouts, design-system decisions, visual hierarchy, typography, interaction, or motion. For small content changes that do not affect design intent, a full design procedure may be unnecessary.

## How it works

1. Read product intent, users, constraints, and the existing design system.
2. Choose a visual direction appropriate to the product, not to current trends.
3. Calibrate creative latitude, information density, and motion to context.
4. Design and implement accessible, coherent UI using the established stack and components.
5. Inspect rendered behavior and revise meaningful usability or visual issues.

## Design controls

| Dimension | Example range |
| --- | --- |
| Creative latitude | Restrained enterprise through expressive brand-led experience |
| Motion | None through immersive, only where justified |
| Information density | Compact operational through spacious editorial |

These are *decision aids*, not a requirement to add animation or novelty.

## Example request

> Design the incident overview page for an operations console. Keep the existing design system, optimize for dense scanning, and verify the final screen at desktop and mobile widths.

## What you get

Context-specific UI decisions, implementation when requested, and a rendered quality check where the necessary tools are available. The result should prioritize usability and product character over fashionable effects.

## Boundaries and dependencies

Existing branding and shared components take precedence unless redesign is authorized. The skill may need browser/runtime access for reliable validation. It should not quietly replace a design system or claim the screen is verified from code inspection alone.

**Cost guidance:** Relative only. Read the [canonical skill](../../skills/ui-ux-design/SKILL.md) for detailed implementation and verification rules.
