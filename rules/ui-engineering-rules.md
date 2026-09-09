# UI Engineering Rules

These are durable defaults for interface work. Existing product requirements may be stricter.

## Intent

1. Understand the primary user task before changing visual design.
2. Preserve an established design system unless redesign is requested.
3. Prefer the simplest design that satisfies the product rather than the most decorated design.
4. Do not invent product requirements, user research findings, testimonials, metrics, or brand claims.

## Structure

5. Use semantic HTML before ARIA.
6. Use existing accessible component primitives for composite interactions.
7. Keep DOM order compatible with reading and keyboard focus order.
8. Keep presentation, reusable UI, data access, schemas, and business logic separated according to the project's architecture.
9. Centralize reusable design tokens rather than scattering arbitrary visual constants.
10. Do not create a new shared abstraction from one local use without evidence that reuse is needed.

## Interaction

11. Every interactive control must have an understandable purpose.
12. Keyboard users must be able to complete the primary flow.
13. Focus must be visible and must not disappear behind sticky or overlay UI.
14. Important actions require immediate, understandable feedback.
15. Errors must identify the problem and provide a recovery path when one exists.
16. Destructive actions must make consequence and recovery clear.
17. Do not use color as the only carrier of status or meaning.

## Accessibility

18. Target WCAG 2.2 AA unless the product specifies otherwise.
19. Text and essential UI graphics must maintain sufficient contrast.
20. Provide appropriate text alternatives for meaningful non-text content.
21. Decorative media must not create assistive-technology noise.
22. Respect zoom, reflow, text scaling, and reduced-motion preferences.
23. Touch targets must satisfy the applicable accessibility/platform baseline; prefer comfortable targets on touch surfaces rather than merely meeting the minimum.
24. Never disable user zoom to preserve a layout.

## Responsive behavior

25. Design responsive behavior intentionally rather than shrinking a desktop composition.
26. The primary task must remain available on small screens.
27. No accidental horizontal scrolling.
28. Long labels, localization expansion, dynamic values, and user-generated content must not break layout.
29. Preserve reasonable content priority across breakpoints.

## Visual system

30. Use hierarchy through typography, spacing, scale, contrast, position, and grouping rather than decoration alone.
31. Apply color semantically and consistently.
32. Use a deliberate spacing rhythm.
33. Use corner radius, borders, shadows, and elevation as a system.
34. Do not turn every group into a floating card.
35. Do not add visual effects that have no relationship to product intent.

## Motion

36. Motion must communicate state, continuity, hierarchy, attention, or deliberate brand character.
37. Do not delay a primary action for decorative animation.
38. Avoid unrelated simultaneous movement.
39. Provide a usable reduced-motion experience.
40. Prefer no animation over meaningless animation.

## Validation

41. A visually significant change is not complete until the rendered result is inspected when rendering tools are available.
42. Review at mobile and desktop at minimum for responsive web work.
43. Validate important states, not only the happy-path resting state.
44. Do not claim accessibility, browser, or device validation that was not performed.
45. Fix outcome-level defects before preference-level polish.
