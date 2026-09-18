# Interrogation Patterns

Use this reference when the active subject requires deeper perspective coverage or the next useful question is not obvious.

## Principle

Perspectives are lenses, not checklist sections.

Activate a lens only when its answer could change the solution, scope, sequencing, architecture, risk, viability, or definition of success.

## Problem and Outcome

Use when the request starts with a solution, technology, or broad aspiration.

Explore:

- triggering problem or opportunity
- current behavior or workaround
- frequency and severity
- who experiences the problem
- consequence of doing nothing
- desired change in observable terms
- evidence versus assumption

High-value challenge:

```text
If we removed the proposed solution from the statement, what problem would still remain?
```

## User and Customer

Use when adoption, workflow, permissions, or UX depends on who is involved.

Distinguish where relevant:

- end user
- customer/buyer
- payer
- operator
- administrator
- approver
- support/maintainer
- affected non-user

Explore current workflow, motivation, switching cost, accessibility, trust, and failure tolerance.

## Product and UX

Use when behavior or experience is not obvious.

Explore:

- primary job-to-be-done
- critical user journey
- required versus optional behaviors
- empty/loading/error states
- device/context of use
- accessibility
- trust-sensitive moments
- what must remain simple

Avoid designing screens during interrogation unless a visual decision is the actual subject.

## Business and Economics

Use when the idea is a product, service, organizational investment, or cost-sensitive initiative.

Explore:

- who receives value
- who pays
- why they would pay or change
- current substitute and its cost
- unit or operating economics when material
- acquisition/distribution
- retention or repeat behavior
- incentives and conflicts
- opportunity cost

Do not ask for investor strategy unless financing is actually relevant.

## Sales, Distribution, and Adoption

Use when success depends on getting users or organizations to adopt the solution.

Explore:

- how first users discover it
- who must approve adoption
- procurement friction
- integration/onboarding effort
- training or behavior change
- switching cost
- trust barriers
- channel dependencies
- who loses convenience, control, money, or status if adoption succeeds

## Architecture and Technical Feasibility

Use only after the required outcome is sufficiently understood to evaluate technical choices.

Explore:

- workload characteristics
- consistency and durability needs
- latency expectations
- current and credible near-term scale
- failure tolerance
- integration boundaries
- data ownership
- deployment independence needs
- operational maturity
- team topology
- migration constraints

Challenge architecture labels by asking which concrete requirement demands them.

Example:

```text
What requirement needs independent deployment or scaling today?
```

Prefer workload evidence over fashionable patterns.

## Data and Integration

Use when correctness or feasibility depends on information moving between systems.

Explore:

- system of record
- producers and consumers
- freshness
- retention
- ownership
- reconciliation
- idempotency
- ordering
- schema evolution
- third-party availability
- import/export/migration

## Security, Privacy, Safety, and Compliance

Activate when the subject handles sensitive data, money, identity, permissions, regulated workflows, physical safety, or meaningful abuse risk.

Explore:

- protected assets
- actors and trust boundaries
- authorization model
- sensitive data
- abuse/misuse
- audit requirements
- regulatory constraints
- failure consequences
- human approval boundaries

Do not turn every ordinary feature into a security interrogation.

## Reliability, Operations, and Support

Use when the system must run continuously or failures create meaningful business or user impact.

Explore:

- availability expectation
- degraded behavior
- retry/recovery
- observability
- ownership/on-call
- support workflow
- backup/restore
- readiness and shutdown
- dependency failure
- operational cost

## Delivery and Team

Use when scope depends on available people, time, money, or expertise.

Explore:

- deadline and why it exists
- team size and skills
- budget
- dependencies on other teams
- build versus buy
- delivery sequence
- minimum useful slice
- test/validation environment

Do not invent artificial deadlines.

## Scale and Evolution

Use when future growth is being used to justify present complexity.

Separate:

- current load
- credible near-term load
- hypothetical distant load

Ask what measurable threshold would trigger the more complex architecture.

Prefer evolutionary paths where possible:

```text
current design -> measurable pressure -> scaling step -> architectural transition
```

Do not optimize the first release for an unsupported million-user scenario.

## Migration and Reversibility

Use for replacements, data migrations, infrastructure changes, architecture shifts, and difficult one-way decisions.

Explore:

- coexistence
- backward compatibility
- rollback
- data migration
- cutover
- stranded dependencies
- exit cost

## Question Shapes

Use the shape that resolves the current ambiguity.

Clarification:

```text
When you say "fast", what observable response time matters here?
```

Boundary:

```text
Does this apply to historical orders or only new ones?
```

Assumption:

```text
What evidence do we have that every courier exposes the tracking data this depends on?
```

Tradeoff:

```text
If improving same-day delivery increases fulfillment cost, which constraint should govern?
```

Counterexample:

```text
What should happen if payment succeeds but order creation fails?
```

Falsification:

```text
What evidence would make you abandon this approach?
```

Reversibility:

```text
If this rollout fails, how do you return to the current system?
```

Contradiction:

```text
Earlier you said updates need not be real-time, but this requirement needs immediate visibility. Which should govern?
```

Adoption:

```text
What behavior must the customer change for this to succeed?
```

Operations:

```text
Who owns recovery when this dependency is unavailable?
```

## Gentle Challenge Pattern

Use:

```text
<context-based concern>. <one decision-relevant question>
```

Good:

```text
At the current scale, independent services may add more operational cost than scaling benefit. What requirement needs independent deployment now?
```

Bad:

```text
Why would you use microservices for something this small?
```

The objective is better reasoning, not dominance.
