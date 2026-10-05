# Runtime Verification

Use this reference when choosing the strongest practical way to observe the completed behavior outside the inner test loop.

## Principle

The runtime verifier should interact with the system as close as practical to the real consumer.

It is independent evidence, not a replacement for fast development tests.

## Surface selection

### Web UI

Prefer a real running application and browser automation.

Interact through:
- accessible roles
- labels
- user-visible text
- semantic controls
- real navigation

Observe:
- rendered result
- navigation/state
- errors
- persistence visible to the user
- network-visible outcomes when relevant

Avoid relying on:
- private component state
- CSS class selectors when semantic selectors exist
- direct invocation of event handlers
- mocked browser state that bypasses the feature

Use Playwright, browser MCP, web/computer-use tooling, or the equivalent available in the current harness.

### HTTP/API

Start the real service in a safe local/test environment when practical.

Exercise:
- route
- authentication/authorization context
- request validation
- response contract
- externally visible side effect

Prefer real HTTP over directly calling the controller when verifying the API boundary.

### CLI

Invoke the command/process as a user would.

Observe:
- exit code
- stdout/stderr
- files/artifacts
- externally visible state

### Event-driven systems

Trigger through the public producer/input boundary when feasible.

Observe:
- emitted/consumed event contract
- resulting public state
- idempotency/retry behavior when relevant

Do not prove an event flow only by mocking both producer and consumer.

### Persistence

Drive persistence through the owning public behavior first.

Inspect storage directly only when persistence itself is part of the contract or when it provides necessary diagnostic evidence.

Do not make database internals the primary proof of a user-facing capability.

### Libraries

Exercise exported/public interfaces.

Use representative consumer behavior when integration semantics matter.

## Tracer slice

For a new feature with multiple layers, use an early tracer slice to prove that the main runtime path can work end-to-end.

Then return to the fast inner loop.

Do not force slow browser/system tests on every micro-step.

## Isolation

Runtime tests should isolate:
- accounts/identities
- cookies/session/local storage
- test data
- mutable shared state

A passing test that depends on prior runs is unreliable evidence.

## Failure diagnosis

When runtime verification fails, distinguish:
- product defect
- test/probe defect
- environment/setup failure
- dependency failure
- stale build/deployment

Do not repair production behavior until the failure source is understood.

## Evidence

Capture enough evidence to reproduce the claim:
- command/request
- test/probe identifier
- relevant response/output
- screenshot or browser state when useful
- resulting externally visible state

Do not replace evidence with "works on my machine."
