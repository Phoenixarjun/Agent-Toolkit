# Global Engineering Rules

These rules apply to implementation work unless a more specific project rule explicitly overrides them.

## Core rule 1: Think before coding

Before editing code, understand:

- what the user is actually asking for
- what behavior must change
- what must remain unchanged
- which parts of the system are affected
- how the result will be verified

Do not start by writing code and discover the design afterward.

## Core rule 2: Prefer the simplest scalable solution

For a material design choice, consider more than one plausible implementation when useful and choose the smallest solution that:

- solves the current requirement correctly
- fits the existing architecture
- is maintainable by the current team
- has a clear path to scale when a real scaling trigger appears

Do not build complexity for hypothetical future requirements.

Simple does not mean fragile. Scalable does not mean over-engineered.

## Core rule 3: Keep responsibilities modular

Code must have clear ownership and responsibility boundaries.

Apply separation of concerns and SOLID principles where they improve maintainability.

Do not dump unrelated responsibilities into one file or component.

Keep API access, schemas, domain logic, persistence, UI composition, infrastructure concerns, and reusable components separated when they represent distinct responsibilities.

Do not create abstractions only for ceremony. A small cohesive file is better than unnecessary indirection.

## Supporting rule 4: Preserve scope

Change only what is required or genuinely necessary to support the requested outcome.

Do not perform unrelated refactors, dependency upgrades, formatting sweeps, or architecture redesigns without explicit need.

## Supporting rule 5: Verify before claiming completion

Completion requires evidence appropriate to the change.

Use focused tests, integration checks, build, lint, type checks, or runtime verification as relevant.

Never claim a check passed if it was not executed against the final candidate.
