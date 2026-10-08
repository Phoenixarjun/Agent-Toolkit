# Application, API, Distributed and Agentic Boundaries

Load the relevant sections only. Prefer security invariants and actual exposed paths over broad scanner categories.

## Request and business invariants

Trace untrusted input from entry point through validation, authorization, use in queries/commands/templates/URLs, and resulting side effects.

Select as applicable:
- input processing, injection at parser/query/command/template boundaries
- response encoding, XSS and client-side trust violations
- CORS, CSRF and credential flow alignment
- file upload validation, storage permissions and serving policy
- SSRF controls for URL fetching/webhooks
- serialization/deserialization and unsafe redirects
- API inventory, object/property/function authorization
- rate limiting and abuse resistance proportionate to exposure
- idempotency, replay, sequence manipulation, state transition integrity
- price/quantity/refund/discount manipulation where money flows exist

Use denied outcomes or preserved invariants as oracles. Do not use scanner alerts alone to infer exploitability.

## Service and event boundaries

Map which component is trusted to assert a caller's identity and which independently enforces access. Inspect machine identity, token forwarding/delegation, authorization at worker/resource, replay handling, event provenance, webhook signatures, retries, partial failure and idempotency.

Do not assume a private network, API gateway, or message broker provides authorization automatically.

## AI/LLM/agents and MCP

Only if applicable, evaluate:
- whether untrusted prompt/tool output is treated as authority
- independent permission checks on tools and resource access
- isolation of tenant/user data and secrets from model context
- limits on autonomous high-impact actions and approvals
- prompt-injection-driven cross-boundary instructions
- tool/plugin permissions, execution scope, egress and credential use
- logging with least-necessary sensitive content

Test safely using controlled synthetic data and benign boundary challenges. Avoid encouraging autonomous destructive tool invocation. Tool refusal alone is not proof: verify the backend enforcement boundary.

## Evidence pitfalls

- UI blocks tampered input but direct API accepts it.
- API auth passes in synchronous route while worker path bypasses checks.
- Validation exists but effect persists before denial.
- HTTP error code looks correct while data is still leaked in body/log.
- WAF blocks one payload while vulnerable application logic remains.
- “No prompt injection occurred” from one sample does not verify all agent tool boundaries.

Target remediation recommendations to the real failing security property, not the technology brand.
