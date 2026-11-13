# Visualize

`/visualize` discovers the logical architecture of an authorized codebase, supports semantic drill-down from high-level components to internal behavior, and prepares an evidence-backed model for a local 3D exploration renderer. Flow selection highlights a source-backed request, event, or data journey at the current architecture depth. Synthetic scenarios model explicitly declared rules only.

## What is different

- **Not AAM:** does not govern future architecture or write architectural constraints into the application.
- **Not Code Explore:** does not deliver change-impact or implementation plans.
- **Not an observability platform:** does not instrument services or infer runtime health from static source.
- **Not a bug fixer:** records broken or unresolved connections without touching application code.
- **Not a diagram generator first:** builds one evidence-backed model so hierarchy, flows and simulations cannot quietly disagree across views.

## Typical invocation

`/visualize this repository` starts at the highest useful semantic level. `/visualize the model selection path` focuses discovery on an actual reachable flow. `/visualize the Kafka producer and its downstream consumers` investigates a bounded event boundary without assuming that absent consumers are defects.

## Model and interaction

The 3D renderer, when installed, owns geometry, camera movement, interaction, animation and accessible side inspectors. The skill owns safe discovery, bounded investigation, evidence, graph reconciliation and scenario preparation. The model's containment tree determines navigation; its communication relations and journey paths are separate graphs. A child view contains logical modules/behaviors, not just source files. Every visible relation supports a traceable explanation or is labeled uncertain.

Visual primitives correspond to behaviors and roles, not vendors. A processing module can represent candidate selection; an integration can represent a model provider. A datastore has storage semantics and metadata that distinguish SQL, NoSQL, graph or vector systems when supported by code. A new primitive is justified only by behavior that current primitives misrepresent.

The reader can inspect component responsibility, why it exists, parent/child relationships, links, journey participation, redacted input/output shapes, source locations and uncertainty. A static browser cannot scan local code or summon agents: absent an authorized host bridge, additional drill-down requires a fresh `/visualize` invocation and regenerated model. Flow playback at the overview level shows coarse transitions; entering a component reveals its relevant internal stages while preserving order and branch meaning.

## Safety and assurance

Inspected roots are immutable. No package installation, test generation, source formatting, application execution, credentials discovery for replay, live traffic, Kafka publishes, deployment, or self-remediation is permitted. Output must be placed outside scanned source roots and must be approved before replacing an existing artifact.

Two verification roles exist: Graph Verifier checks whether the picture agrees with source; Failure Verifier investigates suspected defects with independent evidence and alternative explanations. Only the second may adjudicate a broken-link hypothesis, and missing scope can require `INDETERMINATE`. Independent assurance requires genuinely separate agent context, not a simulated role.

## Installation boundaries

Install `skills/visualize/` alongside `workflows/visualize/` and the three `agents/visualize-*/` role files if the host supports companion agents. The coordinator can still run without subagents, but its assurance is limited. Host-specific delegation, paths, 3D viewer installation and command wiring belong in vendor adapters, not in these canonical files.

The companion viewer is included at `web-app/visualize/`. It implements native WebGL2 3D primitives, hierarchy navigation, flow playback, evidence inspection and a bounded deterministic synthetic runner. It consumes a validated local `visualize.json` and includes a fictional demo fixture. The existence of the viewer does not mean an arbitrary repository has been scanned or rendered: report `rendered` only after checking an actual generated model in a functioning browser. Run the viewer locally through `python3 -m http.server 4173` from its directory; see `web-app/visualize/README.md`.

## Expected quality gates

Inspect model IDs, acyclic containment, source/snapshot references, unresolved edges, journey projection, secret redaction, scenario mode, cross-agent reconciliation, verification independence, and output path. Then check actual 3D interactions if a renderer exists. `python scripts/validate.py` remains the repository integration gate after copying this package into the real Agent Toolkit checkout.


## Viewer integration (v0.6)

The local viewer now includes a centered search field, theme toggle in the top bar, collapsible tooltip-enabled sidebar, and 2D/3D modes. Selecting a journey focuses its supported components and edges while keeping confirmed defects visible; the full graph can be restored through the sidebar. In 2D, node movement is local to the view, does not change the source model, and can be undone or reset. Cross-group handoffs are represented explicitly. Declared non-linear flows require a selected path before illustrative playback; unsupported transfers do not autoplay. Source claims are never promoted into live runtime observations.

The viewer accepts a model prepared by the skill. It does not scan arbitrary repositories, run applications, measure throughput, or confirm production health. Production acceptance requires source-grounded integration evaluations, real browser/WebGL checks, and performance benchmarks on representative authorized systems.
