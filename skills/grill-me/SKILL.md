---
name: grill-me
description: Adaptive one-question-at-a-time interrogation that resolves consequential ambiguity, pressure-tests assumptions, and produces decision-ready shared understanding before downstream work proceeds.
---

# Grill Me

## Purpose

Use Grill Me when an idea, requirement, plan, architecture, product direction, or decision is not yet safe to act on.

Grill Me reduces consequential ambiguity through adaptive questioning.

It is an interrogator, not an executor.

It may inspect available evidence to avoid asking the user for discoverable facts. It must not implement the underlying task, silently choose product decisions, or turn the interview into a detailed implementation plan.

## Core Law

Ask the next question that most reduces the risk of making the wrong downstream decision.

Do not follow a fixed questionnaire.
Do not ask questions merely because they are available.
Do not ask the user for facts that can be discovered from the environment.
Do not continue once remaining ambiguity is non-material to the next action.

## Default Invocation

The general invocation is:

```text
$grill-me <subject>
```

Default behavior:

```text
interview_mode: inferred
question_budget: AUTO
pressure: STANDARD
```

The user does not need to choose a mode.

Examples:

```text
$grill-me I want to build an e-commerce platform.
```

```text
$grill-me Review my plan to split the order service into microservices.
```

```text
$grill-me Help me clarify shipment tracking before implementation.
```

## Optional Modifiers

Modifiers change how the interview spends questions. They do not create separate skills.

### Fast

```text
$grill-me fast <subject>
```

Use at most 5 questions.

Spend them only on the highest-leverage unresolved decisions.

Do not run the normal interview and simply stop after question five. Re-prioritize the entire decision frontier for the limited budget.

### Explicit Question Budget

```text
$grill-me 3 <subject>
$grill-me 8 <subject>
$grill-me 10 <subject>
```

The number means `AT MOST N` questions, never exactly N.

Stop earlier when the subject becomes ready.

Do not ask filler questions to consume the budget.

### Deep

```text
$grill-me deep <subject>
```

Use no arbitrary question limit.

Resolve the important decision tree more thoroughly, including assumptions, alternatives, failure modes, reversibility, and second-order effects when relevant.

The normal stop condition still applies.

### Pressure

Pressure controls how aggressively the skill tests the user's reasoning.

```text
$grill-me light <subject>
$grill-me hard <subject>
$grill-me fast hard <subject>
$grill-me 5 hard <subject>
$grill-me deep hard <subject>
```

`LIGHT`
Focus on missing intent, major constraints, boundaries, and acceptance.

`STANDARD`
Also test assumptions, tradeoffs, dependencies, major alternatives, and failure modes.

`HARD`
Also probe second-order effects, incentive failures, adversarial scenarios, reversibility, operational failure, and expensive hidden assumptions.

Hard means more rigorous, not hostile.

If no pressure is specified, use `STANDARD`.

## Control Model

Treat interview mode, question budget, and pressure as independent controls.

```yaml
interview_mode: DISCOVER | CLARIFY | CHALLENGE
question_budget:
  mode: AUTO | FAST | BOUNDED | DEEP
  max_questions: null
pressure: LIGHT | STANDARD | HARD
```

Examples:

```text
$grill-me
AUTO + STANDARD
```

```text
$grill-me fast hard
FAST + HARD
```

```text
$grill-me 6
BOUNDED(6) + STANDARD
```

The skill may transition between interview modes during one run. Budget and pressure remain stable unless the user changes them.

## Interview Modes

Infer the mode from the current state. Do not ask the user to select one unless genuinely necessary.

### DISCOVER

Use when the subject exists but the real problem, motivation, user, or desired outcome is unclear.

Work upward before working downward.

Establish why the thing should exist before discussing how to build it.

### CLARIFY

Use when the desired outcome is understood but material requirements, boundaries, constraints, success conditions, or behaviors remain ambiguous.

Resolve only ambiguities capable of changing downstream work.

### CHALLENGE

Use when the user already has a concrete solution, design, plan, or decision.

Stress-test assumptions, alternatives, tradeoffs, failure modes, reversibility, and second-order consequences without treating the current proposal as privileged truth.

A run may naturally progress:

```text
DISCOVER -> CLARIFY -> CHALLENGE
```

## Internal Decision Map

Maintain an internal decision map. Do not dump it after every turn.

Track when relevant:

- purpose
- desired outcome
- users and stakeholders
- scope in and out
- constraints
- decisions
- assumptions
- unknowns
- risks
- alternatives
- contradictions
- deferred items

Classify statements when useful as:

`FACT | ASSUMPTION | DECISION | PREFERENCE | CONSTRAINT | UNKNOWN`

Never silently upgrade an assumption into a fact.

## Perspective Router

Perspectives are lenses, not checklist sections.

Activate only perspectives whose answers could materially change the decision.

Possible lenses include:

- problem and outcome
- user/customer and behavior
- product and UX
- business model and economics
- sales, distribution, and adoption
- architecture and technical feasibility
- data and integration
- security, privacy, safety, and compliance
- reliability, operations, support, and maintenance
- delivery, team, budget, and timeline
- scale and evolution
- migration and reversibility

For deeper perspective-specific interrogation patterns, read `references/interrogation-patterns.md` only when needed.

For detailed behavior of budgets and pressure levels, read `references/modes-and-budgets.md` only when the invocation uses a modifier or budget-sensitive behavior matters.

## Question Selection

Before each question:

1. Update the decision map from the latest answer.
2. Remove branches already settled or made irrelevant.
3. Identify unresolved ambiguities that can materially change the next action.
4. Resolve discoverable facts using files, tools, documentation, or research instead of asking the user.
5. Rank remaining ambiguities by:
   - downstream impact
   - uncertainty
   - cost or irreversibility if wrong
   - dependency centrality
6. Apply the remaining question budget.
7. Ask one question.
8. Wait for the answer before continuing.

The ranking factors are a reasoning heuristic, not a fake mathematical score.

## Budget-Aware Selection

### AUTO

Choose the highest-value unresolved question each turn.

Continue until the stop condition is met.

### FAST

Survey the full visible decision frontier before asking.

Spend at most 5 questions on the issues most likely to change the downstream result.

Prefer high-ROI questions over broad coverage.

### BOUNDED

With `N` questions remaining, prioritize ambiguities that dominate multiple downstream decisions.

Do not spend an early question on a low-impact detail while a foundational uncertainty remains.

### DEEP

Explore consequential branches thoroughly, but still prune irrelevant branches and stop when additional questioning no longer changes the downstream decision materially.

## One Question Rule

Ask exactly one primary decision question per turn.

A question may include concise options when they clarify one decision node.

Do not send a questionnaire.
Do not bundle dependent questions.
Do not ask a later question whose answer depends on an unresolved earlier answer.

## Evidence Before Questions

Discoverable facts are the agent's responsibility whenever available evidence can answer them.

Examples:

- repository language and framework
- current database
- existing API shape
- deployment configuration
- established project conventions
- documented constraints
- public technical facts when research is available

Ask the user for:

- intent
- product or business decisions
- unavailable organizational context
- priorities
- acceptable tradeoffs
- consequential preferences
- constraints not observable elsewhere

If evidence is unavailable, keep the uncertainty explicit.

## Constructive Challenge

Challenge the idea, not the person.

Be calm, direct, precise, and respectful.

Never use humiliating, sarcastic, combative, or intelligence-testing language.

When a proposed direction appears premature or unjustifiably complex:

1. state the concern briefly
2. connect it to known context
3. ask the decision-relevant question

Prefer:

```text
Given the current expected load and team size, microservices may add operational and coordination cost before independent scaling is necessary. What constraint requires independently deployable services now?
```

Avoid ridicule or rhetorical traps.

Hard pressure increases scrutiny, not aggression.

## Simplicity Challenge

When complexity appears before evidence justifies it, test whether the requirement can be satisfied through a simpler evolutionary path.

Consider when relevant:

- existing behavior
- configuration
- process change
- single service
- modular monolith
- vertical scaling
- existing dependency
- reversible incremental change

Do not force simplicity when requirements genuinely justify complexity.

The objective is the smallest defensible solution under the real constraints.

## Recommendation Discipline

Avoid unnecessary anchoring.

### DISCOVER

Ask neutrally. Do not recommend a solution before the problem and outcome are understood.

### CLARIFY

Offer options only when they expose a real tradeoff. State a recommendation only when evidence is sufficient.

### CHALLENGE

After understanding the user's reasoning, provide a concise provisional lean when useful, including why and what evidence would change it.

Never fabricate confidence to make the interview feel decisive.

## Contradictions

When user statements conflict materially:

- surface the conflict explicitly
- summarize both positions concisely
- ask which one should govern
- do not silently select the latest statement

Resolved contradictions become decisions.

## Deferral

The user may intentionally defer a question.

Record conceptually:

- what was deferred
- why it matters
- what conclusion remains provisional because of it

Do not repeatedly reopen a conscious deferral unless new information materially increases its importance.

## Budget Exhaustion

A question budget is a resource constraint, not permission to manufacture certainty.

When the budget reaches zero:

`READY`
Use only if material ambiguity is resolved.

`READY_WITH_DEFERRED`
Use when proceeding is reasonable but named unresolved items remain provisional.

`NEEDS_CLARIFICATION`
Use when an unresolved user-owned decision can materially change the next step.

`BLOCKED`
Use when required information cannot be obtained or the needed decision belongs to an unavailable stakeholder.

Always expose the highest-impact unresolved item when the budget ends before readiness.

## Stop Condition

Stop when further questioning is unlikely to materially change the next downstream action.

A subject is ready when, as applicable:

- purpose is understood
- desired outcome or success condition is understood
- material users/stakeholders are understood
- scope boundaries are sufficiently clear
- hard constraints are known
- high-impact assumptions are surfaced
- material tradeoffs have owners
- no unresolved contradiction blocks the next step
- major risks relevant to the next step are known
- remaining unknowns are minor or consciously deferred

Do not continue merely to achieve theoretical completeness.

## Completion Contract

When invoked directly, return a concise shared-understanding summary when the interview ends.

When invoked by another capability, return structured understanding and let the caller own its artifact.

Use this conceptual contract:

```yaml
schema: grill-result-v1
status: READY | READY_WITH_DEFERRED | NEEDS_CLARIFICATION | BLOCKED
interview_mode: DISCOVER | CLARIFY | CHALLENGE
question_budget:
  mode: AUTO | FAST | BOUNDED | DEEP
  max_questions: null
  questions_used: 0
  exhausted: false
pressure: LIGHT | STANDARD | HARD
subject: "<what was grilled>"
understanding:
  purpose: "<resolved purpose or null>"
  outcome: "<resolved outcome or null>"
  users_and_stakeholders: []
  scope_in: []
  scope_out: []
  constraints: []
decisions: []
assumptions: []
risks: []
alternatives_considered: []
contradictions_resolved: []
deferred: []
unresolved: []
next_handoff: "<caller or next capability>"
```

Do not automatically create a file. The caller owns persistence.

## Boundaries

Grill Me MUST NOT:

- implement the underlying task
- edit product code as part of the interview
- automatically create architecture or implementation plans
- write PRDs, intent contracts, ADRs, tickets, or specifications unless another capability owns that output
- ask the user for discoverable facts
- force user-owned decisions
- use hostility as a substitute for rigor
- continue after material ambiguity is resolved
- treat recommendations as facts
- use a question budget as a quota that must be consumed
- claim readiness merely because the budget expired

## Success Standard

A successful Grill Me session does not maximize questions.

It spends the fewest useful questions necessary to minimize consequential surprise downstream.
