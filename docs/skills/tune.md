# Tune

**Purpose:** Adapt one installed Agent Toolkit capability to a developer's working preferences while preserving its engineering guarantees.

## Invocation

Request the `tune` skill explicitly with a target, such as `tune code-review` or `tune ui-ux-design`. The exact UI command differs by coding assistant; see the installed adapter. Tune does not automatically run after ordinary task feedback.

## What Tune examines

The target skill, its references and evals, active repository instructions, an existing engineering-preferences record, and only the history/feedback the user authorizes and the harness actually exposes. A developer with no history can still tune by explicitly stating preferences. Tune never assumes its history access is complete.

Tune separates **personal preferences** from **context-specific conventions**, **questionable engineering habits**, **conflicts with mandatory contracts**, and **possible defects in the canonical skill**. It keeps questionable habits in a separate advisory section rather than turning them into new instructions.

## What Tune changes

The default is a proposed, narrowly scoped change to the existing `.agent-toolkit/ENGINEERING-PREFERENCES.md` in the consuming project, provided the installed capability actually loads it. The source skill remains unchanged. An isolated personal fork is an exceptional, explicitly requested route requiring actual behavior and activation verification.

The default invocation does not write. Approval must cover the precise diff and location. Tune can correctly conclude `NO_CHANGE`, and it reports honestly when testing or activation could not be verified.

## What Tune does not do

It does not improve the shared canonical toolkit, fix application code, rewrite safety rules, convert every habit into a rule, scan inaccessible private conversations, or automatically invoke itself or other skills. Evidence is summarized, not copied as raw private history.

See `skills/tune/SKILL.md` for the operational procedure. The canonical preference owner is `templates/documents/ENGINEERING-PREFERENCES.md` in the Operating Foundation, copied deliberately into a consuming project's configured location.
