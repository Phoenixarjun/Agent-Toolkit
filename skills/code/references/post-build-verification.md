# Post-Build Verification Policy

## Ordering

The initial `/code` feature is implemented **before** optional deeper TDD-assisted testing begins. Basic existing checks during implementation are still allowed; they are not a mandatory RED/GREEN development loop.

1. Coordinator marks complete feature `IMPLEMENTED` after integrated candidate is identified.
2. Evaluate whether a meaningful, independent behavioral oracle exists and whether the impact justifies deeper verification.
3. When warranted, load `skills/tdd/SKILL.md` and relevant `skills/tdd/references/` for test-quality, runtime, and adversarial guidance. **Do not rewrite that skill.** Do not tell it to fabricate test-first history for already completed behavior.
4. Independent verifier runs/coordinates appropriate probes on the final integrated candidate; tests may be authored only in a separately controlled test-write scope.
5. If a genuinely new behavior slice or subsequent defect fix is needed, the canonical TDD RED -> GREEN development loop may begin *at that point*, after the initial feature.
6. Reintegrate test changes, fixes and evidence. Re-run relevant checks after every candidate change.

## Decision table

| Condition | Decision | Required action |
| --- | --- | --- |
| Changed observable feature with reliable oracle | `USED` | TDD-informed test quality, runtime and risk-based adversarial verification |
| High-risk auth, payment, deletion, migration or distributed contract | `USED` or `BLOCKED` | Harder negative and integration probes; no production destructive testing |
| Trivial format/comment-only change | `NOT_APPLICABLE` | Explain why behavioral testing has no independent seam; run appropriate static/diff checks |
| Behavioral specification ambiguous | `BLOCKED` | Request missing oracle or accepted requirement; do not infer from implementation |
| Tool/environment unavailable | `BLOCKED` | Report exact missing capability; do not invent results |

## Surface selection

Choose the **strongest feasible external seam**, not the largest number of tests:

- HTTP service: local/test deployment plus real HTTP responses, auth and failure behavior.
- User interface: actual running UI using approved browser/DevTools automation or manual recorded steps, responsive state, console/network failures and keyboard/accessibility flows where relevant.
- Event workflow: real or controlled broker/test transport, retries and downstream observable effects.
- Database logic: authorized test database and visible persisted state through a public API; never use production data for destructive trials.
- CLI/library: executable or public exported interface with independent expected results.

Browser or DevTools MCP tools are optional adapters. Container/images and ports must be authorized. If the only environment is production, use non-destructive checks or block the unsafe probe.

## Separate evidence levels

`IMPLEMENTED`: code exists. `AUTOMATED_TESTED`: tests were executed and passed. `RUNTIME_VERIFIED`: an actual running surface was observed. `ADVERSARIAL_VERIFIED`: relevant risk-based attempts to falsify were executed. None implies the others. Record skipped/blocked cases and why.

Independent verifier may not declare its own tests proof if it computed expectations using the very implementation being tested. Avoid excess mocks that bypass the integration under assessment.
