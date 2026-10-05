# Adversarial Testing

Use this reference for STANDARD/HARD failure selection. Choose only lenses relevant to the feature.

The purpose is falsification: find a realistic way the feature could be wrong despite the happy path working.

## Depth

### QUICK

Seek:
- primary success path
- one material failure/negative path
- basic runtime proof
- focused regression

### STANDARD

Add the relevant subset of:
- invalid input
- boundary values
- duplicate/retry behavior
- state transition errors
- dependency failure
- persistence consistency
- interruption/recovery
- integration contract errors
- regression around nearby behavior

### HARD

Create a bounded failure/threat matrix before execution.

Prioritize by:
- impact if wrong
- likelihood
- irreversibility
- exposure to untrusted input
- concurrency/state complexity
- cost of recovery

## Attack lenses

### Boundary

Consider:
- empty/missing
- minimum/maximum
- just below/above boundary
- very large input
- Unicode/normalization
- locale/timezone
- unusual but valid values

### State

Consider:
- refresh/restart
- stale state
- invalid transition
- interrupted operation
- replay
- retry after partial success
- back/forward navigation where relevant

### Concurrency

Consider:
- double-submit
- simultaneous requests
- duplicate events
- race between read/write
- lost update
- out-of-order events

### Dependency

Consider:
- timeout
- 4xx/5xx
- malformed dependency response
- unavailable service
- delayed response
- partial downstream success

### Security

When the feature crosses a security boundary, consider:
- unauthenticated access
- horizontal authorization
- vertical authorization
- parameter tampering
- client-side validation bypass
- injection at untrusted-input boundaries
- replay/token/session misuse
- sensitive data exposure

Keep security probes non-destructive and inside authorized local/test scope.

### Persistence and consistency

Consider:
- duplicate write
- partial write
- rollback/compensation
- stale read
- invalid persisted state
- idempotency
- restart after write

### UX/runtime

Consider:
- rapid repeated action
- slow network
- offline/interruption
- disabled/invalid controls
- error recovery
- responsive viewport where relevant
- accessibility-critical interaction where relevant

### Abuse and sequence

Consider whether individually allowed operations become invalid when:
- reordered
- repeated
- skipped
- performed with a different identity
- performed after state has changed

## Selecting cases

Do not maximize case count.

Choose the smallest set that attacks the highest-risk assumptions.

Each HARD case should identify:
- target assumption
- attack/probe
- expected safe behavior
- evidence
- status

## Fuzzing

Use bounded fuzzing when:
- input space is broad
- parser/validation logic is important
- malformed input can expose meaningful defects

Do not send uncontrolled payloads into shared or production environments.

## Mutation testing

Use mutation testing to attack test quality rather than production security.

Target changed/high-risk logic rather than the entire repository unless the user requests a broad campaign.

## Escalation

Stop and escalate when a discovered problem requires:
- new product behavior
- architecture redesign
- new authorization model
- destructive migration
- change outside the current feature contract

TDD can reproduce and document the failure without silently expanding scope.
