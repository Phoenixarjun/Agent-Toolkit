# Claim and evidence contract

This describes the portable research record, not a runtime graph platform. A structured ledger is the authority; Markdown and HTML are derived projections.

## Core relations

`research` → `questions` → `claims` → `sources`; `charts` → `series` → `source_ids`. Every report finding must cite claim IDs, and every claim must have a question owner, evidence source and precise source locator when supported. Sources may share `lineage_id` to identify syndicated dependence.

Record top-level fields: `schema_version`, `research`, `execution`, `questions`, `sources`, `claims`, `findings`, and `charts`. The source-controlled example in `evals/research/fixtures/research-example.json` illustrates a non-authoritative **synthetic dataset**; never convert it into a factual report.

**IDs**: `Q-001`, `S-001`, `C-001`, `F-001`, `CH-001`. Stable within one revision. Preserve mappings when updating records. Report/research ID is arbitrary readable text.

**Questions**: `id`, `text`, `status` (`answered|partial|unanswered`), `claim_ids`, `gap` when partial/unanswered. Coverage means all explicitly scoped questions have a status, not that the answer is necessarily correct.

**Sources**: `id`, `title`, `url` or authorized locator, `publisher`, `kind`, `published_at`, `accessed_at`, `measurement_period` where material, `lineage_id`, `locator`, `excerpt`, `limitations`. For external source links permit only `https://` or `http://`. Missing dates/fields must be represented explicitly as unknown or absent, not invented.

**Claims**: `id`, `question_id`, `text`, `source_ids`, `status` (`supported|qualified|disputed|unverified`), `observed_period` if relevant, `material` boolean, `scout_context`, `verification` (`reviewer_context`, `method`, `note`), `limitations`. `supported` asserts cited source support after review, **not guaranteed truth**. Material claims in Deep require reviewer distinct from Scout and source evidence with locators; otherwise record research `partial`.

**Numeric assertions (optional on claims)**: `numeric_assertion` with `chart_id`, `series_name`, `first`, `last`, `delta`. The validator recomputes these from the cited series without inventing data; external source truth remains independently unverified.

**Findings**: `id`, `title`, `body`, `claim_ids`, `category`; do not give any conclusion no accepted supporting claim. Qualified, disputed and unverified claims require visible qualifications in report.

**Charts**: `id`, `title`, `unit`, `series` with `name`, `source_ids`, and timestamped finite numeric `points` (sorted and unique), `note` and `method`. Every chart has a numeric data table matching its series. Report methods for derived metrics. Rendering code only displays these observations; it must not invent missing interpolation points.

**Execution**: `mode`, `independence` (`independent|unavailable`), `scout_contexts`, `critic_context`, `verifier_context`, `coverage_reviewed`, `budget` (caps/consumption), `limitations`. Distinct context IDs represent actual separate invocations, never an imagined role. `outcome` (`complete|partial|blocked`) on `research`. All checks operate on this record plus authorized source snapshots, not prose alone.

## Preservation

Keep source text excerpts brief, use stable URLs/locators, honor licensing and private-data controls, and make the report's *as-of* date explicit. Changes to source measurements or units must invalidate and re-run dependent charts and calculations. Retain contradictions rather than deleting inconvenient claims.
