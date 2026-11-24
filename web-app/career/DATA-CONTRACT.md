# Career viewer data contract — schema v1

This is a derived read-only projection, not another source of career truth. The coordinator creates a snapshot only from authorized, committed records and explicitly identified proposals. It owns the projection. Subagents cannot update private workspace files or the viewer independently. Keep canonical files and their histories unchanged. No real candidate data belongs in the toolkit repository. Do not copy secrets, restricted claims, unnecessary contact details or raw private transcripts. An exported file is not encrypted.

## Root object

| Field | Required shape |
|---|---|
| schema_version | Integer 1 |
| mode | `demo` for synthetic data; `workspace` for actual authorized records |
| as_of | ISO calendar date YYYY-MM-DD; date against which progress and deadlines are interpreted |
| generated_at | ISO timestamp with timezone |
| candidate | Object with `current_role` and `target` strings or null |
| plan | Canonical plan v1 object from `skills/career/references/adaptive-planning.md`, or null; never invent one |
| plan_state | `APPROVED`, `PROPOSED` or `UNKNOWN`; set APPROVED only from verified active pointer and matching approval |
| next_review | YYYY-MM-DD or null |
| progress | Object keyed by stable milestone IDs, each with status `NOT_STARTED`, `IN_PROGRESS`, `COMPLETED` or `BLOCKED`; completion requires `completed_at` ISO date no later than as_of and nonempty string `evidence_refs` |
| sections | Object with zero or more keys: `projects`, `presence`, `content`, `resumes`, `opportunities`, `companies`, `applications`, `interviews`, `offers`. Values are record arrays. |
| documents | Array of document records, possibly empty |
| activity | Array of recorded events, possibly empty |
| overview_blocks | Optional array of declarative blocks |
| extensions | Optional array of extension pages |
| routines | Optional array of recorded cadence summaries |

Use stable IDs matching `[A-Za-z0-9][A-Za-z0-9_-]{0,79}` and unique within their collection. Use null for unknown field values rather than invented estimates. Required strings may be short; prefer precise summaries. Omit unused optional fields. Full working example: `data/demo.json`.

The plan is displayed, not activated or semantically approved by the viewer. Validate canonical plans separately with the career plan helper. A projection of a revised plan includes its current milestones; previous completed milestones remain in canonical progress history and can appear in a linked history report. Do not count historical milestones as part of a new plan unless present in it. If the source progress shape differs, normalize it without upgrading statuses or inventing evidence. Do not copy a proposal into the approved plan slot. Link proposed revision reports from `overview_blocks` or Research and label their state explicitly; the viewer never approves changes.

## Section records

```json
{
  "id": "retrieval-post",
  "title": "Retrieval evaluation notes",
  "status": "DRAFT",
  "updated": "2026-11-24",
  "summary": "Research-backed draft, not yet published.",
  "fields": [
    {"label": "Platform", "value": "LinkedIn"},
    {"label": "Publication date", "value": null},
    {"label": "Impressions", "value": null}
  ],
  "document_ids": ["retrieval-research"],
  "blocks": []
}
```

`id`, `title`, `status`, `updated`, `summary` are required. `fields`, `document_ids` and `blocks` are optional. Field values must be string, finite number, boolean or null. Status is the actual recorded state; keep domain vocabulary rather than inventing a universal lifecycle. All document IDs must resolve. Content list explicitly renders the `Platform` and `Publication date` fields when present. Other section data remains accessible in each detail view. Suitable fields and linked reports:

| Section | Typical fields / documents |
|---|---|
| Projects | Repository, target-role relevance, acceptance, evaluation, next improvement, actual evidence |
| Presence | Platform, sections reviewed, current vs proposed wording, fact checks, audience/critique |
| Content | Platform, topic, draft status, publication date, actual URL and observed metrics, research, final draft |
| Résumés | Version, target role, related opportunity, claim audit, export availability |
| Opportunities | Employer, role, requisition, location, source and checked time, listing status, fit decision, blockers |
| Companies | Business model, evidence date, engineering signals, uncertainty, reality report |
| Applications | Opportunity ID, submitted résumé version, confirmed status, event time, next follow-up |
| Interviews | Role, stage, scheduled date, panel coverage, feedback, readiness evidence |
| Offers | Role, currency, compensation components, unresolved terms, tradeoffs and negotiation draft |

Record dates, source references and provenance inside reports; use source URLs as document `sources` to create validated clickable links. Status PUBLISHED or APPLIED requires the same user confirmation as canonical records. Never infer them from a draft. Analytics are observed values with dates and source, not predictions; unknown counts are null. `summary` should not include confidential raw evidence. Put long text into documents rather than table cells.

## Documents and activity

```json
{
  "id": "retrieval-research",
  "title": "Retrieval research",
  "category": "Content",
  "updated": "2026-11-24",
  "markdown": "# Findings\n\nCandidate-approved report text.",
  "sources": []
}
```

Sources, when available, are objects `{ "label": "Original source", "url": "https://example.com/" }`; only HTTP(S) URLs without embedded credentials are allowed. No automatic source fetch, HTML execution, scripts, iframes or relative file references. Reports may link to other records via declarative document blocks. Use the category and title to make research searchable. Large binary artifacts are not embedded.

```json
{
  "id": "run-20261124-01",
  "timestamp": "2026-11-24T10:00:00+05:30",
  "agent": "Career content manager",
  "summary": "Research shortlist recorded",
  "status": "COMPLETED",
  "document_ids": ["retrieval-research"]
}
```

Activity is an actual recorded event, not an invented agent trace. `document_ids` optional. Preserve timezone in the source; display timestamps use the viewer's local timezone. If a workflow writes progress events while running, another export can expose them; there is no live agent connection. Do not claim real-time updates.

## Declarative rendering

Use existing components first. Blocks work in `overview_blocks`, a section record's `blocks`, or an extension page's `blocks`. Every block requires `type` and `title`. Supported block types are `metrics`, `table`, `list`, `text`, `document` and `quiz`. Timeline, progress and panels are built-in layout renderers rather than arbitrary extension block types.

```json
[
  {"type":"metrics","title":"Recorded outcomes","items":[{"label":"Drafts","value":2,"detail":"As of snapshot date"}]},
  {"type":"table","title":"Review findings","columns":["Section","Status"],"rows":[["About","REVISE"],["Projects","PASS"]]},
  {"type":"list","title":"Next actions","items":["Verify project scope","Review wording"]},
  {"type":"text","title":"Summary","text":"## Conclusion\nPreserve the verified evidence."},
  {"type":"document","title":"Supporting report","document_id":"retrieval-research"}
]
```

Extension example:

```json
{
  "id":"youtube",
  "title":"YouTube",
  "description":"User-authorized video content records.",
  "blocks":[{"type":"table","title":"Video pipeline","columns":["Topic","State"],"rows":[["Distributed systems","DRAFT"]]}]
}
```

Append extensions only for relevant user-authorized capabilities; IDs must not collide with built-in pages or other extensions. Do not modify the navigation or source code to add ordinary data views. If a genuinely new rendering primitive is needed, propose a supervised code change with the contract, safe DOM rendering, responsive behavior and tests. Never execute agent-generated JS, HTML, CSS or external scripts as report data. No arbitrary dynamic component loading.

## Coordinator export procedure

- On explicit viewer/export request or after an opted-in committed run, obtain the private workspace and authorized scope. Read existing committed records and document references, verify plan state and progress, normalize into the schema, and omit secrets and unapproved private data. Preserve unresolved values and actual source dates. Do not create career records just to fill the dashboard.
- Use `data/demo.json` as a structural example, never as evidence. Mark the actual projection `mode: workspace`; avoid copying demo content. Save as `career-view.json` in the approved private workspace. Validate in the viewer. If no workspace access, provide JSON as a response artifact and state UNSAVED if not persisted.
- Let the candidate import it directly. If they authorize a persistent private viewer, copy the static viewer into that workspace and use `scripts/export_snapshot.py` to replace only that copy's `data/workspace.js`; refresh to load. Never write personal data into the checked-in viewer.
- Serialize one consistent snapshot from authorized revisions. If records change during export, reread or disclose staleness; no concurrent canonical writes. Exporter uses the same display validator as the browser (optional Node 18+ required for persistent export); it does not perform full semantic verification, locking across source records or approval. Invalid export preserves the previous display file. Browser errors retain the last loaded snapshot and explain the invalid fields. Repair the projection, never alter canonical truth to satisfy display.

## Recurring work and conditional activation

An optional `routines` array projects the authorized cadence records, independently of milestone completion. Example:

```json
{"id":"weekly-linkedin","plan_id":"v1-2","title":"LinkedIn content","workflow_id":"career-linkedin-content","cadence_days":7,"next_due":"2026-11-24","status":"ACTIVE","summary":"Draft and verify one selected topic; publishing is manual.","document_ids":[]}
```

Use actual approved plan ID, positive cadence days (1–366), ISO next due date, ACTIVE/PAUSED/ENDED/BLOCKED, optional resolving `document_ids`, and workflow ID or null. Due state derives from snapshot date and active approved plan ID; unmatched prior-plan routines are historical. Keep occurrence history in normal content/activity records; no invented catch-up. Due scheduled milestones appear in ready work without modifying the plan; conditional milestones additionally require `activation_confirmed_at` (ISO date at or before as_of) and nonempty `activation_evidence_refs` in the corresponding progress entry. Only coordinator-authorized observations populate these fields.

## Offline self-practice block

```json
{"type":"quiz","title":"Reliability practice","questions":[{"id":"q1","kind":"choice","competency":"Backend","prompt":"Which mechanism prevents duplicate effects during retries?","options":["Stable idempotency key with durable atomic recording","Longer timeout alone"],"correct_index":0,"explanation":"A timeout cannot determine whether the earlier effect committed."},{"id":"q2","kind":"written","competency":"System design","prompt":"How would you recover after a worker crashes?","criteria":["Identify durable state","Describe retry and idempotency"],"explanation":"Compare recovery tradeoffs and failure boundaries."}]}
```

Each block has 1–50 uniquely identified questions. `choice` needs 2–8 distinct nonempty options and a zero-based integer correct index. `written` needs nonempty criteria. Both require prompt, competency and explanation. Only include independently checked reference answers; use written criteria for ambiguous or subjective questions. The viewer reveals feedback on request, counts checked objective answers only, and provides a text area for manually copying practice responses to an agent. Written responses are not graded; answer keys are in the snapshot (not exam security). Answers reset when leaving the view, refreshing or importing a snapshot. Nothing writes to canonical interview records. Do not export live mock question keys as a quiz. This is an additive schema v1 extension; older snapshots remain valid.
