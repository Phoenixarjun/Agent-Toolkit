# Modes and Budgets

Load this reference when Grill Me is invoked with `fast`, `deep`, a numeric question budget, or an explicit pressure modifier, or when budget-sensitive branching logic needs detailed grounding.

## Three Independent Controls

Do not conflate:

- **interview mode** — what kind of ambiguity is being resolved (inferred automatically)
- **question budget** — how much interrogation capacity is available (user-controlled)
- **pressure** — how aggressively reasoning is tested (user-controlled)

## Budget Modes

### AUTO (default)

No target question count. Choose the highest-value unresolved question each turn. Stop when the stop condition is met.

### FAST

Invocation: `$grill-me fast <subject>`

Maximum 5 questions. FAST is not "normal Grill Me truncated at five."

Before the first question, survey the full visible decision frontier. Spend questions on decisions with the greatest expected downstream effect.

Typical priority pattern (adapt to domain):

1. actual outcome
2. blocking constraint
3. largest hidden assumption
4. highest-risk decision
5. definition of success or next irreversible choice

Domain-specific focus examples:

**Architecture:** workload characteristics → correctness/failure guarantees → critical integration boundaries → constraint driving architectural complexity → evolution/reversibility

**Business:** target customer → painful job or problem → why they would pay or change → distribution channel → unit economics

**Product:** primary user and job → critical success observable → hardest constraint → most important tradeoff → definition of done

Do not mechanically use those categories if the domain suggests a different frontier.

### BOUNDED(N)

Invocation: `$grill-me <N> <subject>`

"At most N" questions, never exactly N. Stop earlier when the subject becomes ready.

With N questions remaining, prioritize ambiguities that dominate multiple downstream decisions. Do not spend an early question on a low-impact detail while a foundational uncertainty remains.

Do not ask filler questions to consume the budget.

### DEEP

Invocation: `$grill-me deep <subject>`

No arbitrary question limit. Explore consequential branches thoroughly, including assumptions, alternatives, failure modes, reversibility, and second-order effects when relevant.

Still prune irrelevant branches. Still apply the stop condition. Do not interpret DEEP as "keep asking forever."

## Pressure Levels

### LIGHT

Focus on:
- missing or unclear intent
- major constraints
- scope boundaries
- definition of acceptance

Do not probe assumptions, alternatives, or failure modes unless they are immediately blocking.

### STANDARD (default)

LIGHT topics, plus:
- key assumptions and their evidence
- major tradeoffs and who owns them
- critical dependencies
- main alternatives considered
- primary failure modes

### HARD

STANDARD topics, plus:
- second-order effects and systemic consequences
- incentive failures and misaligned stakeholders
- adversarial or abuse scenarios
- operational failure and recovery
- reversibility and rollback cost
- expensive hidden assumptions
- what would invalidate the current direction

Hard means more rigorous scrutiny, not aggression. Directness and precision increase; tone remains professional.

## Combining Budget and Pressure

Budget and pressure are orthogonal. Either may be set independently.

```text
$grill-me fast hard   → FAST + HARD
$grill-me 5 hard      → BOUNDED(5) + HARD
$grill-me deep light  → DEEP + LIGHT
$grill-me 3           → BOUNDED(3) + STANDARD
```

When both budget is constrained and pressure is HARD, prioritize the highest-risk unresolved decision first. The budget constraint governs question count; pressure governs depth of each question.

## Budget Exhaustion Behavior

When budget reaches zero:

| Situation | Status |
|---|---|
| All material ambiguity resolved | `READY` |
| Proceeding is reasonable, named items remain provisional | `READY_WITH_DEFERRED` |
| An unresolved user-owned decision can materially change next step | `NEEDS_CLARIFICATION` |
| Required information cannot be obtained | `BLOCKED` |

Always name the highest-impact unresolved item when reporting anything other than `READY`.

Do not claim readiness merely because the budget expired.
