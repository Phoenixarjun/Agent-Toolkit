# Test Quality

Use this reference when a test is difficult to trust, when assertions risk mirroring implementation, or when deciding whether mutation/property-based techniques add value.

## Tests are sensors

A test is useful when a meaningful defect changes its result.

Passing tests are evidence only to the extent that the tests are capable of detecting the failures that matter.

Coverage answers whether code executed. It does not prove that the assertions protect the behavior.

## Independent oracle

The expected result must come from a source independent of the implementation algorithm.

Strong sources:
- explicit requirement
- business/domain invariant
- protocol contract
- worked example with known result
- trusted fixture
- prior externally observable behavior

Weak sources:
- calling the same helper as production code
- reimplementing the production algorithm inside the test
- snapshotting output without knowing why it is correct
- asserting only that something is non-null/successful when stronger behavior matters
- mocking the unit under test until the result is predetermined

## Behavior over internals

Prefer tests that survive refactoring.

Good targets:
- returned result
- visible UI behavior
- public state transition
- emitted contract/event
- persisted externally meaningful outcome
- error semantics

Avoid binding tests to:
- private function names
- call order without contract significance
- internal collection/object shape
- CSS structure
- arbitrary implementation decomposition

## Mocking

Mock when control of a true external dependency is necessary for a deterministic test:
- clock
- third-party API
- network boundary
- external queue/service
- nondeterministic system facility

Avoid mocks around owned modules merely to make tests easier. That often proves the mock arrangement rather than the behavior.

Prefer fakes or controlled local dependencies when interaction behavior matters.

## Meaningful RED

A failing test is valid only when the feature behavior is the reason it fails.

Reject RED caused by:
- compilation/setup failure
- missing fixture
- wrong import
- unavailable test environment unrelated to the feature
- assertion typo
- unrelated pre-existing failure

## Mutation testing

Mutation testing changes production behavior deliberately and asks whether the suite notices.

Use it selectively:
- critical business rules
- authorization
- boundaries
- financial calculations
- conditions with many branches
- tests generated primarily by an agent
- areas where coverage is high but confidence is low

Useful manual mutations:
- `>=` -> `>`
- invert/remove condition
- alter returned constant
- skip state write
- remove validation
- change branch result

Immediately revert manual mutations.

If a meaningful mutant survives, improve the sensor or explain why the mutation is equivalent/irrelevant.

Do not optimize blindly for mutation score.

## Property-based and fuzz testing

Use when the behavior is naturally described by invariants or has a large input space.

Examples:
- parsers/serializers
- normalization
- arithmetic invariants
- state machines
- validation
- protocol encoders
- search/sort transformations

Property tests need a real invariant. Random input without an oracle is noise.

## Flakiness

A flaky test is a weak sensor.

Prefer:
- deterministic data
- isolated state
- explicit readiness conditions
- observable synchronization
- controlled time

Avoid:
- arbitrary sleeps
- dependence on test order
- shared mutable fixtures
- production network dependencies in ordinary test runs

## Review questions

Before trusting a test, ask:
1. What exact defect would make this fail?
2. Where did the expected result come from?
3. Would an internal refactor break this without changing behavior?
4. Does the setup predetermine the assertion?
5. Can a meaningful mutation survive?
6. Is the test exercising the same seam the behavior promises?
