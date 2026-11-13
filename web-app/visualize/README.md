# Visualize architecture viewer

A local, read-only 2D/3D architecture explorer for `/visualize`. This website renders a validated model. It does not discover, execute, patch, or contact the inspected application. The skill and workflow remain responsible for gathering and verifying source evidence.

## Run

```bash
cd agent-toolkit/web-app/visualize
python3 -m http.server 4173
```

Open `http://localhost:4173`. On Windows use `py -m http.server 4173`. No third-party packages or network services are required. Use **Import model** to read a local JSON document. Nothing is uploaded. The bundled model is entirely fictional and its behavior is illustrative.

## Explore

The top bar contains repository breadcrumbs, architecture search (Ctrl/⌘+K), and the light/dark theme toggle. The left navigation is collapsed by default; expand it for labeled Architecture, Flows, Catalog, Findings, Coverage, Import, Help, 2D/3D mode, Flow Focus and Reset 2D layout controls. All sidebar actions have accessible labels and hover/focus tooltips.

Use 3D to orbit, pan, zoom, and enter logical components. Use 2D to drag component cards, pan, zoom, select typed directed connections, and enter component internals. Node dragging changes only the local 2D diagram arrangement. Use Reset 2D layout or Ctrl/⌘+Z while focused on the diagram to revert positions.

Choose a discovered journey from Flows. The viewer de-emphasizes unrelated components and edges but preserves confirmed defects and documented alternatives. Flow Focus can be disabled to reveal the complete graph. The contextual inspector explains each stage, input/output shape, conditions, responsibilities, dependencies, and source evidence where available. Playback is illustrative, never a claim of measured runtime behavior.

For a causal graph with branching, fan-out, retries or parallel tasks, select an explicitly modeled path using Choose path. The viewer does not invent a linear order for concurrent operations. If a real source transition is unresolved or contradicted, automatic playback pauses. Use Steps for the full accessible textual description and causal edge list.

Large architectures use declared domains/ownership or connectivity-based groups. Edges to other groups remain visible as boundary handoffs, not as proof of outages. Search can locate a component in another group.

## Scaling and model semantics

Containment is a logical hierarchy. Communication is a directed graph and may cross repositories or hierarchy levels. A repository is not automatically a service, and components are never inferred solely from `.git` paths. Large single-level views are displayed in **groups of 40** without inventing domain boundaries. A relation pointing to another group is shown as an off-page connection; it is not classified as broken. Search and selected stage navigation can move between groups. A cached deterministic layout is maintained per group to reduce repeated work.

The input model supports 2,000 components, 10,000 relations, 400 journeys, and 5,000 stages per journey. These are validation limits, **not production performance guarantees**. The 30-repository test generates 180 logical components and confirms that the model and hierarchy can be navigated; it does not prove automatic discovery or measured FPS for a live 30-repository system. Cross-repository reconciliation, version pinning, and independent investigation remain upstream responsibilities.

You may optionally supply `scope.environment`, relation `protocol`, `channel`, and `contract`, and stage `explanation` (up to 1,200 characters). The viewer only presents information declared by the model; it cannot establish runtime truth from static code or invent performance measurements. Explicit `via_relation_id` identifies a specific relationship when multiple plausible links exist. Without one, ambiguous paths remain uncertain.

## Validation

```bash
node --test tests/*.test.mjs
node scripts/validate-model.mjs data/demo.json
```

These tests check model correctness, 2D layout and arc-length animation, 3D geometry, deterministic simulation, 30-repository navigation, transition integrity, UI structure and both themes. A local browser interaction smoke test verified the interactive SVG graph, component dragging, zoom, search, flow selection and theme switching. The test browser did not provide WebGL2, so full GPU/WebGL visual acceptance and frame-rate measurements still require a graphics-capable browser.

## Safety

The viewer never writes to application source, opens external endpoints, publishes messages, runs live load tests, or executes imported JavaScript. Model fields are displayed as text rather than injected HTML. Declarative 3D recipes are validated. Source refs are metadata. Payload redaction is defense-in-depth, not a guarantee against every sensitive value; avoid importing real secrets or personal data. A synthetic scenario is explicitly labeled and must never be presented as observed production behavior.
