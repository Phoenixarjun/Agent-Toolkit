# Contributing

## Contribution rule

Every new artifact must earn its existence by owning a distinct responsibility.

Do not add a new artifact when an existing one can be extended without becoming ambiguous or bloated.

## Instruction ownership and admission

Before introducing or changing an instruction, inspect the current `AGENTS.md`, applicable `rules/`, `skills/`, `workflows/`, `knowledge/`, profiles, and installed adapter entrypoints.

Every behavioral requirement must have **one canonical owner**. Other artifacts may point to it or specialize its procedure only when they add a necessary, testable behavior. Do not paraphrase the same rule across files.

Classify the proposed change:

- **REUSE** — an existing owner already covers the behavior; reference it, do not add another instruction.
- **REFINE** — the existing owner is incomplete; improve it in place.
- **SPECIALIZE** — the behavior applies only to a named skill/workflow/domain; add the conditional detail there without copying the general rule.
- **REJECT** — no distinct behavior, evidence, or applicability justifies the addition.

Use these ownership boundaries:

- `AGENTS.md`: instructions for agents maintaining the Agent Toolkit repository.
- `rules/global/engineering-rules.md`: portable engineering requirements.
- `rules/global/workspace-safety.md`: mandatory filesystem/data/external-effect safety floor.
- `knowledge/engineering/solution-design-principles.md`: explanatory trade-offs, not new obligations.
- `skills/` and `workflows/`: conditional procedures and orchestration.
- `profiles/`: compose capability IDs, do not duplicate instructions.
- `templates/documents/ENGINEERING-PREFERENCES.md`: optional user/project choices when more than one correct approach exists.
- `adapters/`: runtime-specific routing and transformations, never the canonical home for portable rules.

Before accepting a change, establish its owner, trigger, non-goal, interaction with existing instructions, conflict precedence, and behavioral verification method. Resolve contradictory instructions rather than silently choosing one; never permit preferences to weaken safety or capability invariants.

### Scope of Agent Toolkit

Admit reusable artifacts that demonstrably improve a coding agent's decisions, execution, verification, or maintenance. Reject duplicated knowledge dumps, speculative category hierarchies, generic personas, vendor-specific logic in canonical files, and one-off user preferences embedded in shared skills. Record the rationale for consequential rejections in the change discussion or an existing decision log; do not create a permanent `SCOPE.md` or rejection directory without demonstrated retrieval value.

## Naming

Use lowercase kebab-case for artifact identifiers.

Good:

```text
code-review
api-contract-review
implementation-review-loop
```

Avoid:

```text
CodeReviewer
my_new_skill
review-v2-final
```

## Skill standard

A skill must contain a `SKILL.md` with:

- a precise `name`
- a trigger-oriented `description`
- one primary responsibility
- explicit non-goals when scope could drift
- a deterministic execution sequence
- a clear output contract
- evidence requirements
- failure or blocked behavior

Prefer a short `SKILL.md`. Add `references/`, `scripts/`, or `assets/` only when the task truly needs them.

## Workflow standard

A workflow must define:

- goal
- entry condition
- stages
- ownership
- dependency or parallelism constraints when relevant
- stop conditions
- correction behavior
- final states

Do not bind a canonical workflow to a specific model or vendor unless the workflow itself exists only for that runtime.

## Rule standard

A rule must be:

- broadly applicable within its declared scope
- short enough to remember
- specific enough to enforce
- stable enough to remain useful across projects

Do not turn preferences into global rules.

## Agent standard

An agent definition must include:

- mission
- responsibilities
- boundaries
- decision method
- when it may ask the user questions
- required output

A specialist agent should not quietly become a general-purpose agent.

## Prompt standard

A prompt should be directly reusable and have one clear outcome.

If the prompt becomes an always-repeated process with activation logic and structured checks, promote it to a skill.

## Knowledge standard

Knowledge files explain concepts, decision criteria, tradeoffs, or reference material.

Keep mandatory instructions in rules, skills, workflows, or agents instead.

## Adapter standard

Adapters may contain tool-specific:

- configuration
- installation scripts
- runtime agent definitions
- model mappings
- discovery metadata
- transformed output required by the target tool

Adapters must not become the canonical home of a generally portable idea.

## Evaluation standard

Add or update eval cases when changing behavior that could regress.

For a skill, cover at least:

- expected activation/use case
- incomplete or failing case
- scope-drift case when relevant
- blocked/insufficient-evidence case when relevant

## Validation

Run:

```bash
python scripts/validate.py
```

A change is not complete until repository validation passes.
