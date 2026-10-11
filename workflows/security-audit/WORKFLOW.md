# Security Audit — Independent Multi-Agent Workflow

**Entry:** `skills/security-audit/SKILL.md` → this workflow for a full audit.  **Owner:** parent coordinator. **Purpose:** produce an evidence-backed security assurance record without fixing the target.

## Required execution topology

```text
Parent coordinator (scope, invariant map, authoritative ledger)
  ├─ Authority investigator [separate context]
  ├─ Trust-path investigator [separate context]
  ├─ Coverage critic [separate context, blind to early conclusions]
  └─ Independent finding verifier [separate context, original evidence]
            ↓
Parent reconciles → deterministic validation → audit report → STOP
```

Never let a role verify its own finding. Spawn separate real contexts, not simulated viewpoints. Parent may run delegated roles **sequentially** if parallelism is unavailable; it may not replace them by reasoning alone. Reuse the same role in fresh contexts for independent second passes only when useful. No role except parent publishes the final report.

**Role definitions (exact canonical paths):**
- `agents/security-authority-investigator/AGENT.md`
- `agents/security-trust-path-investigator/AGENT.md`
- `agents/security-coverage-critic/AGENT.md`
- `agents/security-auditor/AGENT.md` (independent finding verifier; reused from v1.1)

If the harness cannot spawn independent contexts: parent may do a limited passive inspection, but **must not** claim the workflow completed. Record `orchestration.mode=unavailable`, `run_status=incomplete`, `report_outcome=INSUFFICIENT_EVIDENCE`, and the precise blocker. Do not fabricate subagent IDs.

## 0. Permission and immutability gates

- Scope = explicit repository/revision, paths, cloud/runtime assets and excluded third-party systems. Confirm ownership or authorization for target.
- Passive source/config analysis is the default; active tests require authorized environment and appropriate scope. Request explicit permission for mutating, aggressive, third-party, financially significant or availability-affecting probes.
- No source edits, remediations, dependency installs with side effects, deployments or risk acceptance.
- Reports and ledgers live outside the target source tree, unless a user-approved audit-output destination exists. Agents return structured summaries; do not paste entire secrets or sensitive data into parent context.
- Pin commit and working tree identity. Cross-check deployment build/revision before claiming runtime corroboration.

## 1. Reconnaissance and scope decision

Parent:
1. Read relevant project instructions and codebase facts first.
2. Discover architecture: principals, roles, resources, stores, sensitive data, entry points, privileged sinks, session/token boundaries, cloud permissions, webhooks, async consumers and CI supply chain when present.
3. Determine application impact tier independently from audit depth. Recommend and explain `SANITY`, `STANDARD` or `DEEP`; honor user selection but report assurance limits.
4. Resolve only material unknowns that change applicability, expected authority, allowed targets or test safety; otherwise proceed with labeled assumptions.
5. Screen conditional standards/regulations and business policy without inferring legal applicability solely from a sector name.
6. Capture target revision/build and explicit active-testing permissions. Do not infer permission from possession of credentials.

Output: `target`, provisional asset/actor map, known constraints, obligation candidates, unverified assumptions.

## 2. Construct the invariant / operation / coverage map

For each *material* attack surface, record:
- security invariant (which unauthorized outcome must never occur)
- applicable control and why it is required/recommended
- entry surface(s) and sensitive resource/sink
- trust boundary and enforcement point(s)
- operation: `principal`, `resource`, `action`, `context`, `expected=ALLOW|DENY`
- independent oracle: policy/spec/contract or justified security invariant
- proof route (static trace and, when authorized, consumer-facing probe)

Map operations in both directions:

```text
entry point -> identity -> policy/enforcement -> resource/side effect
resource/privileged sink -> all reachable callers -> each enforcement boundary
```

Include reads/list/search/export, writes, deletes, background jobs, webhooks, administrative paths, cross-tenant paths and indirect AI/tool invocations **when present**. Select representative cases by risk, not combinatorial product explosion. Uncertainty about an intended business authorization rule is not license to invent it.

Assign stable IDs: `I-*` invariant, `O-*` operation, `C-*` coverage, `CTRL-*` control, `E-*` evidence, `F-*` finding. Parent creates one canonical ledger before delegation; investigators may propose additions but cannot mutate it directly.

## 3. Delegate isolated investigation

Dispatch **both** investigative roles for every completed audit, even SANITY. Separate context IDs, bounded tasks, same pinned revision:

| Role | Primary job | What it must not do |
|---|---|---|
| Authority investigator | Trace principal/tenant/object/role/session authorization and negative paths | Claim all entry paths are covered from UI middleware alone |
| Trust-path investigator | Trace untrusted inputs and sensitive sinks in both directions, including alternate routes/async execution | Equate a scanner hit or sink use with an exploitable vulnerability |

Each dispatch specifies: paths and attack surfaces; material invariants; source revision; permitted tools and runtime targets; **safe action budget**; expected proof/denial; output schema; disallowed test types; stop triggers. Work partition is by boundary and attack path, not superficial file ownership. The two investigations may intentionally overlap on critical high-consequence paths to supply independent corroboration.

Delegates return only:
- paths examined and paths missed
- observed code/control behavior and exact source location/revision
- operations attempted and their expected/observed results
- candidate findings with alternate explanations
- new paths or invariants the parent should add
- evidence IDs and redacted proof
- blockers and assurance limits

**Forbidden:** writing source; fabricating browser/scanner runs; doing other agents' review; editing shared audit.json; including credentials or undisclosed exploit payloads.

## 4. Targeted verification and evidence capture

Parent reconciles candidate signals without promoting them to verified facts. Authorized agents may perform safe, targeted runtime tests through the real consumer seam if the delegation includes explicit permission. Track tool calls and artifacts at assessed revision/environment; distinguish static observation, dynamic observation and inference.

Required evidence for material claims includes source locator/commit or runtime target/build, method, observation, and time/context if available. For denied operations, independently identify actor identity, protected object, attempted action and observed denial. A status code alone can be misleading; validate the correct identity, object, route and side effect.

Load `skills/security-audit/references/native-protocol-and-client.md` if native code, proxy/protocol translation, browser messaging, or other specialized surfaces are present. Use synthetic fixtures and non-destructive probes; stop on unexpected real data, environmental instability, third-party effects or unclear scope. Do not claim code static review alone proves all deployed paths safe.

## 5. Coverage critic — separate context

Pass a **coverage-focused handoff**, not the investigators' confidence adjectives: discovered surfaces, invariant/operation map, attempted coverage, raw evidence refs, source architecture and known exclusions. Critic independently looks for:

- sensitive sinks with no traced caller; entry points with no enforcement trace
- missing `READ`, list/search/export, mutation, job/webhook/tool paths
- absent user/tenant/privilege combinations and bypassable client-only checks
- unexamined policy/context states, cross-service delegation and replay
- controls marked verified without sufficient proof or wrong build identity
- unexplained `NOT_APPLICABLE`, `covered`, or omitted categories
- scanner candidates not correlated with reachable paths

It returns gap IDs ranked by consequence, exact source anchors, and proposed check—not a new final report. Parent routes material gaps back to an appropriate investigator (ideally fresh context for changed scope), or marks `blocked/deferred` with reason. Bound the extra pass: one mandatory criticism pass, at least one targeted follow-up for a material reachable gap if safe and feasible; never spin forever. Unresolved high-impact gaps prevent an `ACCEPTABLE` outcome.

## 6. Independent finding verification

Give `agents/security-auditor` a **fresh** context, baseline revision, original source/evidence, suspected invariant and smallest reproducible claim. Do **not** hand the investigator's preferred severity, expected verdict or persuasive narrative as ground truth.

Verifier must:
1. reconstruct entry → effect and reverse resource access paths as relevant
2. search for effective gate, object-scope filters, compensating controls and unreachable code
3. check whether user/business policy actually permits the behavior
4. distinguish fixture/config/build mismatch from vulnerability
5. independently corroborate with permitted safe evidence when possible
6. return `confirmed`, `needs_validation`, or `rejected` with dissent/counter-evidence

Every **material candidate** requires independent review, including gaps surfaced by the critic. Reviewer and original hunter context IDs must differ. If the verifier disputes a candidate, parent reconciles the evidence; cannot override disagreement without explaining the stronger evidence. No confirmed severity without the factual boundary and impact.

## 7. Machine reconciliation and stop conditions

Obtain a distinct coverage-critic observation and a final source-to-report consistency review from the verifier even for a clean assessment. Record their evidence IDs in `orchestration.coverage_critique_evidence_refs` and `orchestration.record_review_evidence_refs`. Do not assume an empty findings list establishes a safe application.

Construct `audit.json` under schema version `2`, using `evals/security-audit/fixtures/SECURITY-AUDIT-DATA.example.json` for *shape only*. Populate actual facts only from this run. Include:
- target scope/revision/depth/impact
- real orchestration participants and distinct context IDs
- invariants, operations, controls, coverage, evidence and findings
- outcome and blocked/incomplete conditions

Run:

```text
python scripts/validate_security_audit.py path/to/audit.json
```

The validator requires attributable coverage-critic evidence and fresh final-record review evidence **even when findings are empty**. It checks structure, cross-references and logical consistency, **not truth or security**. Resolve validator errors before issuing a validated report. If machine validation unavailable, declare that explicitly and do not label record mechanically validated.

Outcome rules:
- `ACCEPTABLE_WITHIN_ASSESSED_SCOPE`: required material controls verified; no material unresolved finding or high-impact coverage gap within claimed scope.
- `REMEDIATION_REQUIRED`: independently confirmed defect or demonstrably absent/failed required control needing correction.
- `INSUFFICIENT_EVIDENCE`: required runtime, independent agents, scope, or material coverage proof unavailable.
- `SCOPE_UNRESOLVED`: cannot establish an authorized, meaningful target.

`run_status=complete` means the *audit workflow was performed*, not that the product passed. It is compatible with `REMEDIATION_REQUIRED`; unresolved material coverage may instead require incomplete status.

## 8. Human report and independent handoff

Derive `templates/documents/SECURITY-AUDIT-REPORT.md` from the reconciled record. Begin with one plain-language paragraph, project name/tier/depth/outcome. Show existing controls in a small table (applicability, implementation, verification). Then findings, required corrections vs optional improvements, what does **not** need added, blocked checks, remaining uncertainty and next steps. Put detailed traces in a restricted evidence appendix, not in the executive view.

**STOP after report.** The report can be explained but not implemented here. For remediation, initiate a new context with only the report, scoped code, and independent review instructions. The implementation agent may disagree with findings when it has evidence; it should use TDD where relevant. A *new* audit instance assesses the changed revision independently.

## Repeat-run rule

Old reports are leads, not proof. Revalidate unchanged-revision assumptions, reassess changed code, and use prior gaps to guide exploration. Never reuse a finding as confirmed without examining the present source/environment.
