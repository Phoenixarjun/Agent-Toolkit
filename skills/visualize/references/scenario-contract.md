# Behavior and scenario contract

Load only when a journey needs payload inspection, animation, or a user-requested what-if scenario. This contract defines what may be represented; the renderer and deterministic runner are separate software.

## Behavior primitives

A semantic component may perform one or several behaviors: `receive`, `route`, `validate`, `decide`, `transform`, `process`, `read`, `write`, `enqueue`, `dequeue`, `delay`, `retry`, `reject`, `emit`, or `return`. Visual forms represent these behaviors, not particular frameworks or vendors. A database or queue can be a distinctive 3D form while retaining consistent generic behavior semantics. Add new behavior primitives only when the current set cannot faithfully describe the discovered operation.

The agent identifies the code-backed sequence and decision rules; it does **not** implement a bespoke simulation engine for each service. The companion runner under `web-app/visualize/src/core/simulation.js` evaluates an explicit bounded vocabulary (`token_bucket`, `transform`, `select_candidate`, `fifo_queue`, `partitioned_log`, `cache_ttl`, `worker_pool`) deterministically. If a rule cannot be represented faithfully, fall back to an illustrated stage rather than approximate it silently.

## Scenario modes

- `illustrative`: animates a documented or source-backed journey and optional redacted representative payloads. No claim of execution, throughput, latency, routing probability, or exact decision count.
- `synthetic`: evaluates explicit inputs, initial state, model rules, event ordering, and assumptions with deterministic semantics. Outputs are predictions **of the declared model only**, not measured application behavior.
- `observed_replay`: future optional mode for authorized, supplied and sanitized traces. Do not claim this mode is supported unless a renderer and trace adapter actually implement it.

For a synthetic scenario require `id`, `journey_id`, `mode`, `inputs`, `initial_state`, `rules`, `assumptions`, `expected_outputs`, and `provenance` of each rule. If any essential rule or input is unresolved, downgrade to `illustrative` or decline the scenario with the missing dependency stated. Use pseudodata only. Never invoke the running application to obtain sample payloads.

## Inspectable steps

A journey step contains `component_id`, `action`, `input_shape`, `output_shape`, `field_changes`, `conditions`, `outcome`, `source_refs`, and `certainty`. The shapes may be partial or symbolic. Mark transformations as source-backed, inferred, or synthetic; an agent-generated example is not an observed payload. Exclude secrets, identifiers, tokens, PII and sensitive values. For unknown fields, render `unknown` instead of guessing an object.

For branching (such as model selection), display the inspected candidate-generation/filter/selection stages **only if they exist in the code**. If runtime scoring depends on inaccessible data or remote providers, describe the decision contract and show the choice as unresolved or synthetic. Never invent a provider list to decorate the scene.

## Large-volume animation

Separate event count, concurrency, arrival rate, duration, and execution latency. A request for 10,000 events does not specify all of these. Once parameters are supplied or explicitly assumed for a **synthetic** scenario, compute model outcomes with bounded, deterministic state transitions; draw representative animated units or aggregated streams, not one mesh per event. Never infer system throughput, production scaling, SLA compliance, or failure rate from particle movement. Cap resource use, avoid unbounded loops and report truncation.

## Renderer contract

The renderer consumes the validated model without inventing topology or running application code. It supports real 3D geometry, component picking and camera navigation at all available hierarchy levels, source/evidence inspection in accessible HTML controls, a distinct legend for uncertainty and confirmed scoped defects, flow selection and level-aware highlighting, and playback derived from authored steps. If the viewer cannot perform these interactions, report the missing capability rather than label a static image a completed 3D experience.
