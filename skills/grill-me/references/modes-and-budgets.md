# Modes and Budgets

Use this reference when Grill Me is invoked with `fast`, `deep`, a numeric question budget, or an explicit pressure modifier.

## Three Independent Controls

Do not conflate:

- interview mode: what kind of ambiguity is being resolved
- question budget: how much interrogation capacity is available
- pressure: how aggressively the reasoning should be tested

The user may control budget and pressure. Interview mode is normally inferred.

## General Default

Invocation:

```text
$grill-me <subject>
```

Behavior:

```text
interview_mode: inferred
question_budget: AUTO
pressure: STANDARD
```

AUTO is the canonical default.

There is no target number of questions.

The skill stops when readiness is reached.

## Fast

Invocation:

```text
$grill-me fast <subject>
```

Behavior:

```text
question_budget: FAST
max_questions: 5
pressure: STANDARD unless overridden
```

FAST is not "normal Grill Me truncated at five questions."

Before the first question, identify the highest-impact uncertainties visible from current context.

Spend questions on decisions with the greatest expected downstream effect.

Typical priority pattern when applicable:

1. actual outcome
2. blocking constraint
3. largest hidden assumption
4. highest-risk decision
5. definition of success or next irreversible choice

Do not mechanically use those five categories if the domain suggests a different frontier.

Examples of domain-specific focus:

Architecture:
- workload
- correctness/failure guarantees
- critical integration boundaries
- constraint driving architectural complexity
- evolution/reversibility

Business:
- target customer
- painful job/problem
- buyer/payer
- acquisition/distribution
- economics or adoption blocker

Product/UI:
- primary user
- primary job
- critical journey
- trust/device/accessibility constraint
- success behavior

Security-sensitive system:
- protected asset
- trust boundary
- authorization model
- failure/abuse consequence
- compliance or recovery constraint

## Numeric Budget

Invocation:

```text
$grill-me 3 <subject>
$grill-me 7 <subject>
```

Interpretation:

```text
mode: BOUNDED
max_questions: N
```

`N` is a ceiling, not a target.

Stop before N if ready.

When N is small, prioritize root decisions that collapse multiple later branches.

Never use a final question on a cosmetic preference while a foundational ambiguity remains unresolved.

If a numeric budget is unreasonable for the requested depth, respect it and make unresolved risk explicit rather than silently exceeding it.

## Deep

Invocation:

```text
$grill-me deep <subject>
```

Behavior:

```text
question_budget: DEEP
max_questions: null
```

DEEP increases branch coverage, not verbosity per question.

Probe when relevant:

- hidden assumptions
- credible alternatives
- failure modes
- edge conditions
- reversibility
- migration
- operational ownership
- incentive mismatches
- second-order consequences
- evidence that would falsify the current direction

Still ask one primary question per turn.

Still prune irrelevant branches.

Still stop when further questioning would not materially change the next action.

## Pressure Levels

### LIGHT

Use when the user wants quick clarification with minimal adversarial testing.

Focus on:

- intent
- outcome
- scope
- major constraints
- obvious blockers

Do not expand into speculative edge cases.

### STANDARD

Default.

Also test:

- assumptions
- tradeoffs
- dependencies
- important alternatives
- major failure modes

### HARD

Use when the user explicitly asks to be challenged hard or when a calling workflow deliberately requests adversarial pressure.

Also test when relevant:

- second-order effects
- incentive failures
- adversarial behavior
- operational failure
- irreversible decisions
- migration traps
- expensive hidden assumptions
- false scalability arguments
- organizational capability mismatch
- what evidence would invalidate the plan

Hard pressure must remain respectful.

Do not confuse aggression with rigor.

## Modifier Composition

Valid combinations include:

```text
$grill-me fast hard
$grill-me 5 hard
$grill-me 3 light
$grill-me deep hard
```

Resolution order:

1. parse budget modifier
2. parse pressure modifier
3. infer interview mode from subject/context
4. begin questioning

If multiple incompatible budget modifiers are supplied, use the most explicit numeric budget when present. Otherwise prefer `fast` over `auto`; `deep` should not be combined with a numeric ceiling unless the user explicitly explains the intent.

When ambiguity remains, choose the interpretation that places the tighter bound on question count and state it briefly.

## Budget Exhaustion Output

When the ceiling is reached, never infer readiness from exhaustion.

Return the real state.

Example:

```text
Status: READY_WITH_DEFERRED
Questions used: 5/5
Resolved: target user, primary outcome, current scale, delivery constraint
Deferred: disaster-recovery requirement
Impact: resilience decisions remain provisional
```

Or:

```text
Status: NEEDS_CLARIFICATION
Questions used: 5/5
Blocking uncertainty: payment consistency requirement
Impact: this can materially change the transaction design
```

## User Changes Budget Mid-Run

If the user says:

```text
make it fast
```

switch the remaining run to FAST and count already asked primary questions against the new ceiling only if doing so still leaves at least one useful question. Otherwise summarize current understanding and unresolved items.

If the user says:

```text
go deeper
```

switch to DEEP and continue from the current decision map rather than restarting.

If the user supplies a new numeric ceiling, apply it to total primary questions for the current Grill Me run unless they explicitly say "N more questions."
