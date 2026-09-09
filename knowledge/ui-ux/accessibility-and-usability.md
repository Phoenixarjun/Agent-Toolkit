# Accessibility and Usability

Accessibility is a design input.

Automated tools catch only part of the problem.

## WCAG 2.2 baseline

For web product work, default to Level AA unless the product specifies another target.

Important areas:

```text
text alternatives
semantic relationships
meaningful sequence
color use
contrast
reflow
text spacing
keyboard access
focus order
focus visibility
focus not obscured
target size
labels
consistent navigation
error identification
error suggestion
accessible names/roles/values
status messages
```

## Semantic structure

Prefer native elements:

```text
button
a
input
label
select
textarea
details
table
heading elements
landmarks
```

Use ARIA to fill genuine semantic gaps, not to recreate semantics unnecessarily.

## Keyboard

The primary flow must work without a pointer.

Check:

- logical tab order
- visible focus
- dialogs trap and restore focus appropriately
- menus/listboxes follow expected keyboard patterns
- no keyboard traps
- focus is not hidden by sticky UI

## Touch

WCAG 2.2 defines a minimum target-size criterion at AA with exceptions.

For touch-first interfaces, comfortable platform-sized targets are preferable to designing exactly at the minimum.

Do not place important controls so tightly that accidental activation becomes likely.

## Text and zoom

Support:

- browser zoom
- text enlargement
- reflow
- localization expansion
- portrait/landscape when applicable

Do not disable zoom to protect a fragile layout.

## Status and errors

State changes need programmatically determinable communication when appropriate.

Error messages should identify the issue and help recovery.

## Nielsen heuristic lens

Use the following as a usability review frame:

1. system status is visible
2. language matches the user's world
3. users have control and freedom
4. conventions remain consistent
5. prevent errors where possible
6. prefer recognition over recall
7. support efficiency for frequent users
8. remove irrelevant competition
9. help users diagnose and recover
10. provide help when the system cannot be self-explanatory

## Human-required judgment

Do not claim that automated accessibility tooling proves an experience is accessible.

Human judgment remains necessary for:

- sensible screen-reader experience
- coherent keyboard flow
- understandable copy
- meaningful alt text
- real-world task usability
- cognitive load
- motion comfort
- product-specific assistive-technology use
