# Graph and evidence contract

Load when preparing `visualize.json`, reconciling worker results, projecting flows, or validating links. This is the canonical semantic model consumed by the local SVG/WebGL2 viewer, not a UI layout specification.

## Required model

The top-level document contains `schema_version`, `scope`, `snapshots`, `components`, `relations`, `journeys`, `scenarios`, `findings`, and `coverage`. Lists may be empty only when accompanied by an explicit reason in `coverage`.

- `scope`: authorized roots, excluded roots, investigation limits and output destination; do not serialize credentials or private absolute paths intended for sharing.
- `snapshots`: stable repository key, relative root alias, revision when available, dirty state if known, and availability. No Git metadata means `revision: null`, not failure.
- `components`: stable `id`, `name`, semantic `role`, `responsibility`, `parent_id` or `null`, `source_refs`, `evidence_status`, and optional technology `attributes`. Optional `variant` and declarative `visual_recipe` can only refine display semantics; see `web-app/visualize/README.md` for the bounded viewer vocabulary and recipe constraints. Optional `domain`, `owner`, `group_id`, and `repository` identify source-backed architectural grouping for large-level navigation. Optional bounded `capabilities` represent behavior without creating a vendor-specific 3D model. Root components have no parent. Logical containment must be acyclic; one owned parent at most. Shared dependencies should normally be linked, not nested under competing owners.
- `relations`: stable `id`, `from`, `to` or unresolved target descriptor, directed `kind`, `source_refs`, `evidence_status`, and optional `finding_id`. Use `interaction` when the meaningful distinction is request/response, publish, consume, read, write, replication, routing, scheduling, authentication, discovery, or notification. Keep unresolved edges visible instead of joining them to a guessed component.
- `journeys`: stable `id`, source-backed entry/trigger, known outcomes, ordered step and branch references, coverage, and evidence. Steps reference component IDs and may reference child stages. When the causal shape is not linear, use optional `execution_edges` with `id`, `from_step_id`, `to_step_id`, `type`, and optional `via_relation_id` and `condition`. Supported types include sequence, branch, fan-out, fan-in, retry, timeout, fallback, compensate, return, and async. Optional `playback_path` is an explicit ordered sequence of step IDs whose consecutive pairs must appear in `execution_edges`. Without a supported path, do not autoplay branched or parallel stages as a single chronology. Preserve repeated visits and asynchronous handoffs.
- `scenarios`: synthetic or illustrative scenario definitions governed by `scenario-contract.md`; scenarios must not add components or relations to the structural graph.
- `findings`: independent fault claims, disconfirming evidence, scope of verification, reviewer identity when real, and verdict.
- `coverage`: for each relevant boundary/flow, `covered`, `partial`, `unknown`, `blocked`, or `out_of_scope`, with reason.

## Relations and states

Choose relation kinds from the smallest relevant vocabulary: `calls`, `routes_to`, `publishes_to`, `consumes_from`, `reads_from`, `writes_to`, `depends_on`, `transforms_to`, `emits_to`. Introduce another kind only if existing kinds misstate semantics. A Kafka topic and producer-consumer paths are separate relationships; never turn a producer into a direct consumer call without evidence.

`evidence_status` describes how a statement is supported:

- `SOURCE_VERIFIED`: actual inspected code/config declares or establishes the stated relationship. Not proof of runtime health.
- `INFERRED`: reasoned from indirect evidence; show uncertainty and the alternative.
- `UNRESOLVED`: an expected target, binding, branch, or implementation could not be established within authorized scope.
- `CONTRADICTED`: available inspected evidence conflicts; keep both interpretations and pointers until resolved.

`fault_status` describes an investigated defect, **not** evidence quality: `NONE`, `SUSPECTED`, `CONFIRMED`, `DISPROVEN`, or `INDETERMINATE`. Set `CONFIRMED` only with reproducible source/config contradiction or supplied runtime evidence sufficient for the **specific** scoped claim. Never infer a live outage, missing deployed consumer, or production capacity from source alone. An unlocated Kafka consumer is `UNRESOLVED`; it is not a confirmed broken link.

Each consequential claim references `source_refs` with repository key, relative path, line or symbol locator, and snapshot revision where available. Config and docs are attributed as config/docs, not silently promoted to executable proof. If line numbers are unavailable, use an unambiguous symbol or file locator and disclose reduced precision.

## Semantic zoom and flow projection

Containment defines zoom; relations define cross-boundary communication; journeys define execution order. Do not collapse these into one tree. Every zoom view shows its direct logical children and relevant external links, not source files as nodes. A leaf may be a behavior stage; deeper levels are optional.

To project a journey to a visible level, map each step's component to its nearest visible ancestor, preserve chronological order and branch identities, and collapse only consecutive identical projected components when no decision/handoff information is lost. Preserve re-entry into a component and off-level links as boundary ports. If a projection would imply an unproven direct connection, render it as a journey transition with source uncertainty rather than add a structural edge. Use the exact declared relationship when multiple connections are possible. Projected edges across graph groups remain boundary handoffs, not evidence of a broken deployment. Focused views de-emphasize unrelated nodes and connections but preserve confirmed defects and supported alternative branches.

## Model integrity checks

Reject duplicate IDs, dangling resolved references, parent cycles, out-of-scope evidence, unsourced verified claims, incompatible snapshots silently merged, secret-bearing sample data, and any scenario that mutates structural facts. Mark incomplete findings explicitly. Normalize identities when several agents describe the same responsibility; never merge merely on matching names or framework labels.
