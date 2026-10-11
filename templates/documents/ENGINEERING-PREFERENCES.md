# Engineering Preferences

> Optional user/project-specific choices. Copy deliberately to `<project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` (or an explicitly configured user location). This is a preference record, not a replacement for project instructions, capability invariants, or safety policy. Unset choices defer to the project's conventions and canonical engineering guidance.

## Provenance

- Scope: `project` <!-- project | user -->
- Owner: <!-- person/team responsible -->
- Last confirmed: <!-- YYYY-MM-DD or unknown -->
- Evidence: <!-- explicit user/team decision or source; never silently infer from unrelated chats -->

## Configurable preferences

Record **only** material deviations from existing conventions. Remove rows that do not affect the agent's choice.

| Decision area | Chosen preference | Scope/when applicable | Rationale or source |
|---|---|---|---|
| Module granularity | Unset | When multiple cohesive layouts are correct | |
| Abstraction threshold | Unset | When several maintainable designs are viable | |
| Architectural conservatism | Unset | When topology is not specified by project constraints | |
| Third-party dependencies | Unset | When an existing solution and a new dependency both fit | |
| Test emphasis | Unset | Within mandatory correctness and evidence requirements | |
| Explanatory detail | Unset | Reports and design trade-offs | |

## Optional stronger safety preference

`Destructive-action approval: standard`

Allowed values:
- `standard` — follow `rules/global/workspace-safety.md`; high-impact/uncertain operations still require approval.
- `strict` — require exact, command-specific approval for every destructive operation, including verified in-workspace files. Approval is **not** implied by full access or generic task approval.

**Important:** The safety mode may only strengthen, never weaken, the mandatory workspace safety floor. A changed preference cannot authorize an out-of-scope operation or override sandbox restrictions.

## Non-overlap and conflict handling

1. Do not restate global engineering rules, project constraints, or skill procedures here. Name a concrete optional choice that may legitimately vary between engineers.
2. If a preference conflicts with a safety rule, project requirement, contract, or skill invariant, do not apply it. Report the conflict and identify the controlling artifact.
3. If current code and explicit project conventions already determine the choice, prefer those over an unset or inferred preference.
4. Propose preference changes for approval; do not infer permanent preferences from one correction or task.
5. Do not use this document as a substitute for `grill-me`, `intent-capture`, or a project-specific plan.
