# Interaction and Motion

## Interaction feedback

Every consequential action should produce timely feedback.

Feedback may be:

```text
state change
status text
progress
toast
inline confirmation
navigation
optimistic update
```

Choose the form that best preserves context.

## User control

Users need clear escape routes from temporary or destructive states.

Support undo when practical.

Confirm actions when the cost of an accidental action is high; do not add confirmation friction to harmless reversible actions.

## Recognition

Prefer visible choices, labels, history, recent items, sensible defaults, and contextual help over forcing users to remember information.

## Forms

- visible labels
- useful helper text where needed
- errors near the affected field
- preserve user input after recoverable errors
- explain required formats before failure when possible
- use specific action labels rather than generic "Continue" when a clearer verb exists
- do not rely on placeholders as labels
- minimize redundant entry

## Loading

Avoid replacing a stable interface with a full-page spinner when local progress can be shown.

Prevent layout jumps where possible.

Communicate long-running operations.

## Empty states

An empty state should explain:

```text
what is empty
why that matters
what the user can do next
```

Do not turn every empty state into a marketing illustration.

## Motion purposes

Good motion can:

- connect source and destination
- reveal hierarchy
- show state transition
- preserve continuity
- focus attention
- reinforce product character

Bad motion:

- blocks action
- repeats on every element
- creates unrelated movement
- hides state
- triggers unexpectedly
- ignores reduced-motion settings

## Timing

Use duration and easing by purpose.

Fast feedback should feel immediate.

Larger spatial transitions may take longer than small state changes.

Do not use one duration for every animation.

## Choreography

When several elements move, they should communicate one event.

One coordinated transition is usually stronger than many independent effects.

## Reduced motion

Reduced-motion mode must remain understandable.

Remove or simplify large movement, parallax, repeated motion, or unnecessary spatial animation.

Keep essential state communication through non-motion cues.
