# Product Showcase — Direction / Audit Report

Use for `CONCEPT`, `AUDIT`, or an authorized implementation handoff. Fill only applicable fields. **Record evidence, not plausible-looking fictional details.** Do not omit the Section → Layout → Page passes; mark unavailable inspection explicitly. Audience perspectives are simulated heuristics unless actual human testing occurred.

## 1. Decision summary

```yaml
report_version: "1.0"
mode: CONCEPT | AUDIT | AUTHORIZED_BUILD
status: REPORT_READY | IMPLEMENTED_VERIFIED | IMPLEMENTED_UNVERIFIED | NEEDS_USER | BLOCKED
scope:
primary_visitor_job:
primary_action:
recommended_decision:
critical_findings:
  - finding_id:
    reason:
approval_required_for:
```

State which pages/routes are in scope and the website capture or repository revision, if available. Summarize what should be preserved and what should change. Do not present the report as approval to implement.

## 2. Product understanding and evidence

| ID | Fact, differentiator or claim | Evidence status | Actual source/proof asset | Limitation |
| --- | --- | --- | --- | --- |
| F-01 | | VERIFIED / USER_PROVIDED_UNVERIFIED / HYPOTHESIS / UNKNOWN | | |

Primary audience(s), product/substitute context, brand constraints, conversion/adoption step, available real proof and absent proof. Separate marketing propositions from factual claims.

## 3. Inspection scope and coverage

| Page ID | URL/route or concept name | Captured version/time | Sections checked | Layouts/viewports checked | Interaction coverage | Gaps |
| --- | --- | --- | --- | --- | --- | --- |
| P-01 | | | | | | |

```yaml
browser_rendering: VERIFIED | UNAVAILABLE | NOT_APPLICABLE
source_inspection: VERIFIED | UNAVAILABLE | NOT_APPLICABLE
ui_critic: INDEPENDENT | NOT_RUN | DEGRADED_SINGLE_CONTEXT
content_verifier: INDEPENDENT | DEGRADED_SINGLE_CONTEXT | NOT_RUN
audience_instances_requested:
audience_instances_completed:
review_snapshot_id:
```

Do not mark source-only, static comp, or generated imagery as rendered validation.

## 4. Pass S — Section-by-section analysis

For **each inspected or proposed section** in reading order, provide the following. Repeat per page in scope; the example table is a structure, not a quota.

| Page / section ID | Existing/proposed message | Visitor purpose | Proof / CTA | Observed weakness or strength | Evidence reference | Recommended change | Finding ID |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P-01/S-01 | | | | | | | |

Include meaningful current text excerpts when a copy change is proposed. Label concept-only sections as proposals, not observations. For every substantive rewrite, supply the **exact suggested headline**, supporting copy length/content, proof slot and CTA wording or an explicit evidence-needed placeholder.

## 5. Pass L — Layout-by-layout analysis

Evaluate the relationship of sections and representative responsive arrangements **after** Pass S.

| Page / layout ID | Sections and viewport | Composition/hierarchy | Spacing/type/color/imagery | Motion and interaction | Evidence | Problem or strength | Direction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P-01/L-01 | | | | | | | |

Record any visually generic pattern **and what job it fails to perform**. A familiar font, a card, a gradient or a Lucide icon is not by itself a defect. Specify product-specific alternatives where supported.

## 6. Pass P — Page-by-page synthesis

| Page ID | First impression and intended job | Narrative progression | Trust/proof sequence | CTA and navigation | Page-level decision | Supporting section/layout IDs |
| --- | --- | --- | --- | --- | --- | --- |
| P-01 | | | | | | |

After individual pages: document cross-page journey, consistency, gaps and route transitions where in scope. Don't call unseen pages or states complete.

## 7. Content and claim audit

| Claim/copy location | Exact relevant text | Classification | Evidence ID | Risk | Safe revision or evidence request |
| --- | --- | --- | --- | --- | --- |
| | | SUPPORTED / USER_ASSERTED / UNVERIFIED / CONTRADICTED / NONFACTUAL_OPINION | | | |

Describe whether messaging makes a truthful and specific promise, what qualifications are missing, and which CTA wording matches the actual next step. No invented features, metrics, testimonials, logos, warranties or performance claims.

## 8. Independent and simulated perspectives

| Reviewer | Context isolation | Artifact observed | What they understood | Main friction or positive signal | Supporting IDs | Uncertainty |
| --- | --- | --- | --- | --- | --- | --- |
| Content verifier | | | | | | |
| UI critic (rendered candidates only) | | | | | | |
| Audience evaluator A (simulated) | | | | | | |
| Audience evaluator B (simulated) | | | | | | |
| Audience evaluator C (optional, simulated) | | | | | | |

Each audience record must show distinct arrival job, familiarity and objection; never imply real interviews or conversion measurement. A first-impression concept review is weaker evidence than an actual rendered page. Record material disagreements; do not use vote counts as market evidence.

## 9. Reconciled findings and action plan

| Finding ID | Severity | Page/section/layout | Evidence and affected user job | Root cause owner | Change requested | Verification method | Decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| | BLOCKER / HIGH / MEDIUM / LOW / PREFERENCE | | | PRODUCT_POSITIONING / CONTENT / PROOF / VISUAL_HIERARCHY / INTERACTION_ACCESSIBILITY / TECHNICAL | | | ACCEPT / REJECT / NEEDS_EVIDENCE |

Explain why conflicting recommendations were accepted or rejected. Identify what must be preserved, and choose `NO_REDESIGN`, `TARGETED_REFINEMENT`, or `JUSTIFIED_REDESIGN`. Subjective aesthetic preferences do not block completion without an outcome-level rationale.

## 10. Detailed redesign reference

**Target:** Relevant page(s)/section(s), not necessarily the whole site.

**Rationale:** Which observed problem, missing proof or opportunity is being addressed, linked to evidence and visitor jobs.

**Recommended direction:** One concise identity thesis derived from product facts. Include the intended tone, proof mechanism, narrative order and one distinctive visual/interaction signature.

**Concrete content and composition:** For every affected section specify:

```text
Page/section ID:
Exact proposed headline:
Proposed supporting copy:
Primary/secondary action:
Real proof asset or explicit missing-proof requirement:
Layout/composition and adjacent-section relationship:
Typographic role, color relationship, imagery/icon rationale:
Motion intent or explicit static choice:
Responsive behavior and accessibility fallback:
Why this differs from an interchangeable template:
```

**Alternatives:** Where the user requested options or a redesign is justified, describe up to three structurally distinct directions with tradeoffs; alternatives differ in proof format, page rhythm and visual character, not merely color.

**Reference imagery (optional):** State for each reference `RETRIEVED_REFERENCE`, `GENERATED_CONCEPT`, `EDITABLE_PROTOTYPE`, `REAL_IMPLEMENTATION_SCREENSHOT`, or `TEXTUAL_WIREFRAME`; include provenance/licensing and what specifically is being borrowed as a principle. Generated imagery is never represented as implemented code or verified responsive behavior. Provide precise textual references when image tools are unavailable.

## 11. Execution and verification (only if approved)

```yaml
approval_record:
approved_direction:
allowed_paths:
required_preservations:
implementation_executor:
implementation_diff_or_revision:
checks_actually_run:
rendered_mobile:
rendered_desktop:
keyboard_and_accessibility:
reduced_motion:
links_forms_handlers_preserved:
ui_critic_result:
code_review_result:
unverified_checks:
```

If no implementation authorization exists, state **NO SOURCE CHANGES AUTHORIZED OR PERFORMED**.

## 12. Final status and decision requested

```text
Status:
Scope completed:
Strongest product-specific decision:
Top corrections and expected user outcome (not claimed measured uplift):
What stays unchanged:
Reference directions offered:
Reviewers actually run and their isolation status:
Validation actually performed:
Known limitations and evidence gaps:
User approval choices:
Next safe step:
```
