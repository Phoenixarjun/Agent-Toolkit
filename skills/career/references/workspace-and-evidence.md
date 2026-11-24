# Workspace and candidate evidence

Load when persisting or consuming candidate state. The coordinator is the only writer; agents receive read-only snapshots. In chat-only mode produce equivalent records in the response and say persistence unavailable. Never claim the session can wake itself later.

## Storage boundaries

Resolve an explicitly selected workspace outside Agent Toolkit and outside source repositories that may be published. Do not use the installed skill folder, plugin cache, working repo or a silently selected home directory. Reuse an approved workspace only after verifying the target. Check path traversal, symlinks and authorization before writing. Keep it private; do not sync or commit by default. Never put passwords, access tokens, identity documents or unnecessary personal contact details in run logs. Record references to confidential material rather than copying it. Files are created lazily; do not create a folder tree for every possible capability. A direct request may run without persistent storage.

Suggested logical layout (JSON for machine records, Markdown for reports):

```text
career-workspace/
  candidate/profile.json
  candidate/evidence.json
  candidate/preferences.json
  candidate/voice.md
  strategy/assessment.md
  strategy/plans/<plan-id>.json
  strategy/active-plan.json
  strategy/reviews/<review-id>.md
  strategy/decisions/<decision-id>.json
  strategy/progress.json
  strategy/review-state.json
  presence/<platform>/
  content/topics/<topic-id>/
  projects/
  resumes/
  companies/
  opportunities/
  applications/
  interviews/
  offers/
  rubrics/
  runs/YYYY-MM-DD/<unique-run-id>/
```

Record ISO dates with timezone for events. Use a unique run ID, not date alone. Reuse stable topic, opportunity and evidence IDs. Link to reusable topic research rather than copy it into each run. Store only necessary input references, source metadata, findings, decisions, artifact paths, actual checks and limitations. Do not store hidden reasoning or unrestricted transcripts. If no writes authorized, return the artifacts as text and mark UNSAVED.

## Candidate profile and evidence

Separate candidate goals/preferences from facts and public wording. Candidate profile fields: current role/status, target roles, location/remote constraints, work authorization if relevant, transition deadline, weekly time budget, hard requirements, preferences, platform links with confirmed ownership, evidence IDs, confidentiality constraints. Unknown is valid. Current pay is optional, never required just because compensation target matters.

Evidence snapshot is JSON object `schema_version: 1`, `revision`, `records` list. Each record: stable `id`, `statement`, `provenance` (VERIFIED | USER_REPORTED | ESTIMATED | INFERRED | UNKNOWN | CONTRADICTED), `sources` (references and observed date), `scope` (ownership, period, units, comparator), `confidentiality` (PUBLIC | PRIVATE | RESTRICTED), optional `calculation`, `allowed_disclosure`, `supersedes`. Preserve previous revisions when updating. A verified source proves only what it actually shows; a repository does not prove sole authorship or production impact. User-reported statements may be usable if specific, consistent and defensible. Estimates require an actual measurement basis and uncertainty. Do not promote inferred facts to evidence. A candidate correction overrides old claims only after confirming the corrected wording. A public page can support observable facts, not unverified personal achievement or identity.

For each external-facing draft record `claim_id`, exact wording, evidence IDs, disposition (VERIFIED | SUPPORTED | ESTIMATED | UNSUBSTANTIATED | CONTRADICTED), allowed wording and defense question if material. Source status and claim disposition are distinct: evidence can be user-reported and a claim supported, never independently verified merely because it is plausible. For approximate metrics retain before/after, units, timeframe, comparable workload, calculation, precision limits and scope of contribution. If not defensible, remove number or state qualitative improvement supported by evidence. Do not invent a range. For conflicting facts, freeze the affected claim and ask a targeted question; unrelated work can continue.

Stage a diff against the current revision, identify dependent drafts/plan milestones, obtain approval, then record a new snapshot. Do not overwrite facts from scraped sources, automatic email classification or inferred learning. Explicit user correction may authorize the specific update; do not require redundant confirmation. Track freshness and flag dependent artifacts stale rather than silently rewrite them.

## Opportunity and application records

Opportunity fields: stable ID, employer, role, requisition ID if available, location(s), canonical application URL, source URLs, checked timestamp, published/closing date if stated, JD snapshot/reference, listing status, fit decision, hard blockers, uncertainty and next action. Deduplicate by employer requisition ID first, then normalized title/location/content with caution; different requisitions can share title. Verify liveness again before preparation/submission if stale. Employer listing live does not prove active headcount.

Review state records active plan ID, last completed review date, next due date, attempted review dates and unresolved evidence; an incomplete attempt does not reset the due date.

Application records link opportunity ID, submitted material version, status, event date, candidate-confirmed action or source of proposed update, next follow-up and outcome. State may include DISCOVERED, SHORTLISTED, PREPARED, APPLIED, SCREEN, INTERVIEW, OFFER, ACCEPTED, DECLINED, REJECTED, WITHDRAWN, NO_RESPONSE; distinguish inferred no response from explicit rejection. Never mark APPLIED or an offer accepted without confirmation. Keep event history; correct errors with explicit correction. For externally reported status propose updates; candidate can confirm them. No autonomous status polling.

## Shared output envelope

Each run records mode, scope, candidate snapshot revision, plan ID if applicable, input and source IDs, agent coverage/isolation, observations, recommendations, approval state, actual validations, residual uncertainty and next action. Use workflow's content sections. A run must not be considered saved unless the write succeeded. On concurrent edits reload and reconcile; do not overwrite stale records. If optional helper is unavailable, maintain immutable versions by hand and state which checks were manual.

## Continuity and optional viewer

Persist recurring work in `strategy/routines.json` with stable IDs, approved plan linkage, cadence, next due, actual occurrence status/history and references to accepted outputs. For a recurring content run retain the topic dossier, selected channel, draft/version, source/claim checks, publication status and actual confirmation date separately. For interviews retain practice sets, actual answers only when authorized, and feedback distinct from completed mock outcomes. A generated question bank is not an interview result.

On opt-in store viewer preference and approved export target/scope with candidate preferences. After a committed substantive run, project current facts, plan/progress, routines, section records, documents and recorded activity using the viewer contract. Include only approved disclosure; an export failure leaves canonical files and last successful projection intact. The browser imports or refreshes a snapshot; it does not monitor agents or write candidate records. Never require viewer setup for direct or chat-only use.
