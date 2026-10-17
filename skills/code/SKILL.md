---
name: code
description: Implements one authorized coding outcome through bounded delegated work, controlled integration, optional post-implementation TDD-informed behavioral testing, and independent verification of the final candidate. Invoke explicitly as /code when the user wants implementation rather than exploration or review alone.
metadata:
  version: "1.0.0"
  category: engineering
  invocation: explicit
---

# Code

**Contract:** Implement the approved outcome and demonstrate that the integrated candidate works without touching unrelated code. **Do not activate automatically** for ordinary requests; invoke only through explicit `/code` (or an equivalent deliberate invocation).

## Ownership

- This skill owns the **implementation entrypoint, selection and handoff**. The canonical `workflows/implementation-review-loop/WORKFLOW.md` owns sequencing, task assignment and final acceptance.
- `rules/global/engineering-rules.md` and applicable project instructions govern engineering behavior and scope. `knowledge/engineering/solution-design-principles.md` explains tradeoffs. Do not repeat or override their content.
- `skills/code-explore/` may supply a verified change-impact plan but is **optional**. An accepted plan, issue or direct user request can also establish intent.
- `skills/tdd/` owns test quality, runtime verification, adversarial testing and *actual test-first development* where invoked for new work. This `/code` procedure does **not** impose TDD during initial implementation.
- `skills/code-review/` owns independent pre-commit review. `/code` does not implement its method again.
- Model selection, tool names, agent discovery, sandbox paths and permissions belong to adapters.

## Activation and outcome

Use when the user explicitly asks `/code` to implement a feature, fix or accepted plan. Do not use it for read-only exploration (`code-explore`), review-only (`code-review`), research, or unsanctioned refactoring.

Default mode is `STANDARD`. `FOCUSED` is for tiny low-risk bounded edits. `DEEP` is for multi-component, cross-repository or high-risk work. Depth controls exploration, number of verification lenses and delegated task budget, **not** unconditional agent fan-out.

A successful run yields a working authorized change, acceptance-to-evidence mapping and a factual report of executed checks. It never automatically commits, pushes, deploys or promotes production state.

## Procedure

### 0. Establish authority and baseline

1. Read applicable repository instructions, existing intent or plan, engineering rules and minimal relevant context. Confirm the requested outcome, acceptance criteria, preservation invariants, scope, non-goals and approval boundaries. Keep stable criterion IDs. Do not rewrite an accepted plan to match code.
2. If no usable accepted plan exists, establish the smallest sufficient intent. Ask only about material unresolved decisions. If the work requires extensive cross-repository exploration, suggest `code-explore` or perform a bounded read-only discovery; do not require the skill by default.
3. Identify authorized repositories, dependency revisions, pre-existing modifications and safe test environment. Record Git state. **Preserve all pre-existing user work.** No reset, checkout, clean, stash, force push, bulk replacement, deletion or migration merely to simplify implementation.
4. Decide whether real independent subagents and safe write isolation exist. If not, report limitations: do not counterfeit multi-agent work. Builders may run sequentially if parallelism is unsafe. Independent verification is required for a `VERIFIED` result; otherwise return `BLOCKED`/`IMPLEMENTED_UNVERIFIED`.

### 1. Decompose into bounded change tasks

1. Build a task dependency graph from the required behavior and affected contracts. Partition by **independent write ownership and contract boundary**, not by arbitrary technology labels.
2. For each task, issue a contract with: task ID, accepted criterion IDs, prerequisites, allowed repositories/files, preserved invariants, observable completion conditions, approved commands/resources, forbidden edits, and handoff evidence. Use `references/task-contract.md`.
3. Assign one writer per file per integration window. Default to **one Builder at a time**. Parallel builders are permitted only where independent worktrees or equivalent isolation and conflict-free integration have been tested. Disjoint file lists alone do not isolate databases, ports or shared services.
4. Make an explicit choice about shared interfaces and migrations. Establish contracts before dependent tasks; do not let two workers independently redefine them.

### 2. Implement without compulsory TDD

1. Delegate bounded coding to Builder role `agents/code-builder/AGENT.md` where supported. The Builder reads only necessary code, changes the smallest justified surface, handles meaningful failure paths, keeps responsibilities cohesive, and obeys the task's write boundary.
2. **Do not invoke TDD by default while building the initial feature.** The Builder may run smoke/build/type checks and existing fast tests to avoid working blindly, but neither a test-first loop nor new test generation is obligatory during implementation.
3. After each task, require actual changed paths, contract changes, risks and executed check results. A Builder's statement that a feature is done is not validation.
4. If new information changes scope or ownership, stop that task and return to the Coordinator for a revised, authorized task contract.

### 3. Integrate the completed feature

1. Coordinator integrates task results in dependency order; it alone owns final candidate selection and conflict resolution. No blind merges. Ensure pre-existing user changes remain distinguishable.
2. Establish a **single integrated candidate identity** including repository revision and changed-path snapshot; for multiple repositories record one identity per repository and the compatible version set.
3. Run baseline compile/type/smoke checks where safe. The feature is now `IMPLEMENTED`, **not yet `VERIFIED`**. Failure returns a bounded correction task; do not skip verification.

### 4. Post-implementation test decision

After the feature is implemented, explicitly decide whether deeper testing is warranted. This is a **selective gate**, not compulsory for every code change.

- Invoke canonical `tdd` guidance **now**, where available, for observable, sufficiently specified feature behavior, regression exposure, or significant risk. Use its oracle quality, real runtime, and adversarial testing procedures. A completed feature checked afterward is **post-implementation behavioral verification**, not historical RED -> GREEN TDD.
- Use the canonical TDD skill's genuine RED -> GREEN cycle only if **new missing behavior or a defect fix** is subsequently developed using a failing test first. Do not create a fictional past RED result.
- Skip deeper TDD-assisted work for no independent behavior seam, a purely mechanical edit already covered by adequate checks, or unavailable authorized tooling. Record `NOT_APPLICABLE` or `BLOCKED` with a reason. Relevant basic checks and acceptance mapping remain mandatory.
- The Verifier can write *candidate-specific verification tests* only in a truly isolated authorized test-only workspace, or by requesting a separate scoped test-authoring task. It cannot silently edit application source, overwrite Builder changes or mutate live data.
- Browser/devtools/MCP probes, images/containers and service startup are **capabilities, not assumptions**. Use only if available, authorized, isolated and reasonably necessary. Do not issue destructive probes against production or shared state.

Read `references/post-build-verification.md` for gates, modes and failure conditions.

### 5. Independent candidate verification

1. Delegate `agents/code-verifier/AGENT.md` in a **fresh independent context**, passing accepted intent, final integrated candidate and source locations; do not pass the Builder's claims as established facts.
2. Verify acceptance and preservation invariants through the strongest feasible external seam, plus appropriate static/build/unit/integration/browser/service tests. Check failures, skipped checks, regressions, and unexpected changes.
3. If verification exposes a defect, create a **bounded correction task**. The Builder corrects it; all affected evidence must be rerun on the new candidate. Default maximum **one** correction round; escalate rather than loop endlessly.
4. Invoke canonical `code-review` for integrated, intent-aligned risk/scope assessment prior to any commit decision. Avoid claiming commit safety where the candidate or mixed dirty work cannot be isolated.
5. Validate the structured ledger with `python scripts/validate_code_implementation.py <ledger.json>` if available. This detects inconsistent reporting; it **cannot certify program correctness**.

### 6. Report precisely and stop

Return: change summary, changed paths, accepted criterion coverage, preservation evidence, commands and runtime surfaces **actually exercised**, optional TDD assistance decision, verifier independence, review findings, skipped/blocked checks, remaining risks and next steps.

Use these outcomes: `VERIFIED`, `IMPLEMENTED_UNVERIFIED`, `FAILED_VERIFICATION`, `BLOCKED`, `NEEDS_DECISION`. `VERIFIED` requires independently verified **final integrated candidate**, relevant acceptance and preservation checks, and a passed code-review gate. Never infer success from a worker's confidence or green unit tests alone.

## Safety boundaries

- No implicit approval to delete/disable old behavior, rewrite shared contracts, change security ownership, modify production config, run migrations, install unknown software, access other repositories or create external side effects.
- Use approved local/test environments. Stop for credentials, irreversible actions, external services, data handling or production operations not explicitly authorized.
- A multi-agent workflow is not intrinsically safer than a single agent. File ownership, runtime isolation, independent source evidence and final integrated checks provide the protection.

## References

- `references/task-contract.md`: bounded handoff and ownership protocol.
- `references/post-build-verification.md`: selective post-implementation testing decision.
- `workflows/implementation-review-loop/WORKFLOW.md`: canonical coordinator state machine.
- `templates/documents/CODE-IMPLEMENTATION-REPORT.md`: human-facing output.
