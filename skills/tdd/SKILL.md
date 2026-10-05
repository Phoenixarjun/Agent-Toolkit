---
name: tdd
description: Develop concrete behavior through test-first vertical slices, prove the tests can detect failure, verify the real runtime surface, and apply risk-proportional adversarial testing. Use for features or bug fixes when behavior can be observed, when the user asks for TDD/red-green, or when strong implementation verification is required.
---

# TDD

TDD is a development procedure, not a test-generation task.

Build one observable behavior at a time, use tests as sensors rather than proof by themselves, verify the real runtime surface, and increase falsification effort with risk.

## Invocation

Default:

```text
$tdd
```

uses `STANDARD` depth.

Modifiers:

```text
$tdd quick
$tdd hard
```

Depth controls how aggressively the feature is challenged, not a fixed number of tests.

If the user does not choose a depth:
- use `STANDARD` normally
- recommend or select `HARD` for high-risk behavior such as authentication, authorization, payments, financial calculations, data deletion, migrations, concurrency, security boundaries, or irreversible state changes
- use `QUICK` only when the change is low-risk or the user explicitly prioritizes speed

## Preconditions

Before writing a test, establish:
- the behavior being built or fixed
- the observable outcome
- the source of truth for the expected result
- the public seam through which the behavior can be exercised
- the strongest practical runtime surface for independent verification

Inspect existing tests, domain vocabulary, repository rules, ADRs, and nearby behavior before inventing new conventions.

If expected behavior is too ambiguous to derive an independent assertion, stop with `NEEDS_SPEC`. Do not invent an oracle from the implementation you are about to write.

If the change has no meaningful independent behavior to test, do not force TDD merely for coverage.

## Core model

Every meaningful behavior should accumulate evidence through up to three layers:

```text
DEVELOPMENT PROOF
red -> green at a fast public seam
        |
        v
RUNTIME PROOF
observe the actual user/system-facing behavior
        |
        v
ADVERSARIAL PROOF
try to falsify the feature proportionally to risk
```

These layers may use different tools and seams.

A green unit suite alone is not sufficient evidence that a feature works.

## Procedure

### 1. Define the behavior slice

Choose the smallest externally meaningful behavior that moves the feature forward.

Prefer vertical slices over writing a batch of tests first.

State:
- behavior
- input/precondition
- observable outcome
- oracle source
- test seam
- runtime seam

The oracle must be independent of the implementation under test.

Valid oracle sources include:
- explicit acceptance criteria
- protocol or domain rules
- worked examples
- existing externally observable behavior
- authoritative fixtures or contracts

Do not compute the expected value with the same algorithm the production code uses.

### 2. Choose the inner-loop seam

Use the narrowest public seam that gives fast, meaningful feedback.

Examples of seam classes:
- exported domain/library interface
- service boundary
- HTTP/API contract
- command-line interface
- rendered user interaction
- event input/output boundary

Prefer behavior over implementation details.

Do not assert private calls, internal object shape, CSS classes, or incidental implementation structure unless those details are themselves contractual.

Mock only genuine external boundaries or nondeterministic dependencies when necessary. Do not mock the code whose collaboration is the behavior being tested.

### 3. RED

Write one test for the current behavior slice.

Run only the smallest relevant test target.

Confirm that it fails:
- before the implementation exists
- for the expected reason
- at the intended seam

A syntax error, broken fixture, missing environment, unrelated failure, or incorrect assertion is not a valid RED.

If the test passes before the behavior is implemented, investigate whether:
- behavior already exists
- the test is not exercising the intended path
- the assertion is too weak
- the setup bypasses the real behavior

Do not proceed until RED is meaningful.

### 4. GREEN

Implement only enough production behavior to make the current test pass while respecting repository architecture and rules.

Do not pre-build speculative future cases.

Run:
- the focused test
- nearby relevant tests when the change can affect them
- type/lint/build checks when appropriate to the repository

Do not write the next behavior test until the current slice is green.

### 5. Test the sensor

Ask whether the test would notice a meaningful defect in the behavior it claims to protect.

For important behavior, strengthen confidence using one or more of:
- demonstrate that removing/bypassing the new behavior makes the test fail
- vary a boundary value that should change the result
- introduce a controlled local mutation and confirm the relevant test detects it
- use an existing mutation-testing tool when the repository already supports one
- compare against an independently derived expected result

Always revert manual mutations immediately after the check.

Do not run broad mutation campaigns by default. Target changed or high-risk behavior.

A covered line whose meaningful mutation survives is weak evidence.

### 6. Runtime proof

Verify behavior through the strongest practical external surface.

Prefer:
- web UI -> browser automation against the running application
- HTTP service -> real HTTP request against a running test/local instance
- CLI -> invoke the executable/process
- event system -> publish/trigger input and observe downstream externally visible effect
- library -> exercise the exported public interface
- persistence feature -> drive behavior through its public interface, then observe the allowed persisted/resulting state

For browser verification, prefer existing Playwright/browser tooling and interact through user-visible roles, labels, text, and flows rather than implementation selectors.

Canonical TDD behavior is tool-agnostic. Use the browser/MCP/web capability available in the current harness.

Do not fake runtime proof with a mocked unit test.

Runtime proof may be performed:
- on the first tracer slice
- at meaningful integration boundaries
- at the end of the feature

Do not make slow end-to-end tooling the mandatory inner loop when a faster behavioral seam gives the same development signal.

### 7. Continue vertically

Repeat:

```text
behavior
-> RED
-> GREEN
-> sensor check when warranted
-> runtime proof when warranted
-> next behavior
```

Let each completed slice inform the next.

Do not batch all tests before all implementation.

### 8. Adversarial pass

After the requested behavior works, attempt to falsify it according to depth.

#### QUICK

Use for low-risk or time-constrained work.

Cover:
- primary happy path
- one material negative/failure path
- basic runtime proof
- focused regression check

#### STANDARD

Default.

Select relevant cases across:
- expected success paths
- invalid input
- meaningful boundaries
- state transitions
- duplicate/retry behavior
- dependency failure
- persistence consistency
- runtime behavior
- regression risk

Do not mechanically exercise every category.

#### HARD

Perform a small failure/threat analysis before testing.

Select relevant attack lenses such as:
- boundary extremes
- malformed or unusual input
- state interruption and stale state
- retries, replay, duplicate actions
- concurrency and races
- dependency timeout/unavailability
- authorization and privilege boundaries
- injection/tampering where applicable
- partial persistence or invalid transitions
- locale/timezone/Unicode where applicable
- compatibility or responsive behavior where applicable
- abuse of allowed sequences
- recovery after failure

Use fuzzing, property-based testing, mutation testing, or security-oriented probes when they materially increase confidence and suitable tooling exists.

`HARD` means try to break the feature, not generate a large arbitrary test count.

### 9. Handle failures

When a test or runtime probe exposes a defect:
1. preserve a reproducible sensor for the failure when practical
2. identify whether the fix is within the current feature scope
3. fix through the same red-green procedure
4. rerun the failed probe
5. rerun affected regression checks

If the failure reveals a materially different architecture, product decision, security model, migration, or scope expansion, stop and report `ESCALATE` rather than silently redesigning the system.

### 10. Final verification

Before declaring completion:
- run focused tests for changed behavior
- run the repository's appropriate broader test suite
- run relevant type/lint/build checks
- perform final runtime verification
- complete the requested adversarial depth
- inspect failures, skips, and blocked cases
- confirm no temporary mutations/test data/debug instrumentation remain

Do not use coverage percentage as the primary completion criterion.

## Test ledger

For normal work, track the active behavior and evidence in context.

For `HARD`, long-running, or multi-surface features, maintain a durable test ledger when it will prevent lost state. Use `templates/TEST-PLAN.md` when available.

Allowed case states:

```text
PLANNED
RUNNING
PASS
FAIL
BLOCKED
SKIPPED
```

A skipped or blocked case must include a reason.

The ledger is evidence bookkeeping, not a requirement to pre-write every test.

## Safety

Adversarial testing is allowed only within the authorized development/test scope.

Do not:
- attack production or unrelated systems
- use real user data for destructive probes
- run destructive payloads against shared infrastructure
- bypass repository or environment safety controls
- perform irreversible security tests merely to demonstrate a weakness

Prefer non-destructive probes that demonstrate the failure safely.

## Completion states

Report evidence explicitly.

Use:

- `IMPLEMENTED` — requested behavior exists
- `TESTED` — automated behavioral sensors pass
- `RUNTIME_VERIFIED` — behavior was observed through the real runtime surface
- `ADVERSARIAL_VERIFIED` — requested depth pass completed without unresolved failures
- `BLOCKED` — required evidence could not be obtained
- `ESCALATE` — discovered issue requires a decision or scope change outside TDD

Do not collapse missing evidence into `PASS`.

## Output

Return:
- depth used
- behaviors implemented
- test seams used
- runtime surfaces exercised
- adversarial areas exercised
- defects found and fixed
- blocked/skipped checks
- validation commands or observable evidence
- completion states
- residual risks

Read references only when needed:
- `references/test-quality.md` for oracle quality, mocks, mutation testing, and weak-test detection
- `references/runtime-verification.md` for selecting and validating real runtime surfaces
- `references/adversarial-testing.md` for deeper QUICK/STANDARD/HARD attack selection
