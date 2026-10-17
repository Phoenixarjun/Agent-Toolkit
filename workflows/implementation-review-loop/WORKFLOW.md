---
name: implementation-review-loop
description: Portable execution workflow for one accepted implementation intent, with bounded builder tasks, safe integration, selective post-implementation TDD-informed testing, independent verification, and intent-aligned review.
version: "1.2.0"
---

# Implementation Review Loop

This **extends** v1.1.0. It is not a second implementation workflow. Existing callers can still invoke it directly. `/code` is an explicit user-facing entrypoint which invokes this workflow.

## Goal and invariant

Implement one accepted outcome using the smallest defensible changes, preserve the existing workspace, and establish fresh independent evidence for the **final integrated candidate**. Never mistake an agent handoff for system-level correctness.

## Entry and authorities

Prefer a ready Change Intent Contract from `.agent-toolkit/intents/`, or establish an equivalent accepted contract. It must identify outcome, acceptance criteria with stable IDs, must-preserve guarantees, non-goals, approved repositories, action limits and intended behavior. If a material product decision remains unresolved, `NEEDS_DECISION` before writes.

Use repository instructions and engineering rules as governing constraints. Code Explore and the previous plan are **optional inputs**, not requirements. Adopt the approved plan without re-exploring everything; inspect only enough baseline to safely execute it. TDD and Code Review keep their own procedures.

## Coordinator state machine

```text
INTENT_LOCKED
  -> BASELINED
  -> TASKS_ALLOCATED
  -> BUILDING
  -> IMPLEMENTED
  -> POST_BUILD_TEST_DECIDED
  -> INTEGRATED_VERIFICATION
  -> INTEGRATED_REVIEW
  -> VERIFIED / IMPLEMENTED_UNVERIFIED / FAILED_VERIFICATION / BLOCKED / NEEDS_DECISION
```

At `BUILDING`, a task failure may return one bounded correction to its owner. After `IMPLEMENTED`, any candidate change invalidates affected checks and resets integrated verification. One correction round by default; additional rounds require explicit justification and bounded scope.

## Roles and separation

- **Coordinator (main agent):** owns intent, task dependency graph, file ownership, source baseline, safe delegation, integration, candidate identity, final acceptance and communication. Does not certify its own code via an invented independent verifier.
- **Scout:** optional read-only investigation for unknown paths and contracts. Reuse Code Explore where a deep dependency investigation is necessary.
- **Builder:** implements only a contracted slice. Canonical role `agents/code-builder/AGENT.md`.
- **Independent Verifier:** fresh context validates observable integrated behavior, affected invariants, testing evidence, and risks. Canonical role `agents/code-verifier/AGENT.md`.
- **Reviewer:** invokes canonical `skills/code-review/SKILL.md`, independently where supported. Do not create a redundant review methodology.

## Phase A: Lock intent and baseline

- Freeze selected intent and source of truth, criteria, preservation invariants, repository access and explicit out-of-scope actions.
- Capture relevant per-repository HEAD or snapshot identity, initial Git status, dirty files, available tests and external environment constraints. No reset, clean, stash, checkout or deletion to obtain a clean slate.
- Resolve collisions with pre-existing changes before editing. If unsafe, block rather than overwrite.
- Decide actual availability of independent contexts and workspace/runtime isolation. Never label sequential self-critique as independent.

## Phase B: Plan bounded implementation

- Create a task DAG for necessary change slices, assign one writer per file, define allowed paths and required prerequisites.
- Shared interface or version decisions precede consumers. Explicitly address migrations, backcompat, error paths, downstream effects and existing ownership when relevant.
- Prefer one Builder unless real independent workspaces, nonoverlapping resources and deterministic integration exist. For Standard/Deep, agent budget is adaptive, never a count to satisfy mechanically. Deep verification may use multiple **instances** of the same canonical Verifier role for distinct high-risk contract surfaces; each must inspect the integrated candidate and the Coordinator reconciles disagreements. Do not create another permanent agent definition per domain.
- Issue per-task `references/task-contract.md` via the skill. No undocumented write scope.

## Phase C: Implement

- Builders apply authorized code changes and run appropriate low-cost sanity checks; **no mandatory TDD/test-first loop** during initial feature implementation.
- Each worker hands off exact changed files, candidate identification, actual executed checks, unresolved risks and acceptance IDs.
- Coordinator checks diff attribution, workspace contamination, task boundaries and dependency order before integrating next task. Worker success does not imply acceptance.

## Phase D: Declare completed feature and test decision

- Once all required tasks are integrated, identify final candidate across all relevant repositories.
- `IMPLEMENTED` means code exists, not that it passed behavioral verification.
- **Now**, decide whether to bring in canonical `skills/tdd/` as a testing resource. For sufficiently observable/high-risk behavior, consult its test-quality, runtime and adversarial procedures and run meaningful post-build probes. For purely mechanical changes, log `NOT_APPLICABLE` and run suitable static checks. If blocked by missing oracle/environment, report `BLOCKED` rather than fabricating evidence.
- Tests written *after* completed implementation are correctly labeled post-implementation verification, never falsely claimed as a past red-green TDD cycle. A new bug fix can start genuine red-green TDD after the fact.
- Test authoring requires separately authorized test paths and isolation; otherwise request a bounded task. Verifier does not silently edit production code.

## Phase E: Independent integrated verification

- Verify the final integrated revision(s), not isolated Builder snapshots. Independent Verifier must inspect original evidence and test external surfaces when feasible.
- Map every acceptance and affected must-preserve ID to fresh evidence. Record commands, results, environment identity, runtime outcomes, skips, and limitations.
- Verify cross-component integration and regressions, not only new unit tests. Choose risk-proportional depth.
- An inaccessible external repo, contract, runtime or test environment is `BLOCKED` for that required check, not `PASS`.

## Phase F: Canonical pre-commit review

- Run the `code-review` skill against the accepted intent plus the complete relevant diff. Include unstaged/untracked/deleted/renamed files and mixed-intent contamination.
- Verify scope classifications (`REQUIRED`, `SUPPORTING`, `BENIGN_EXTRA`, `MATERIAL_EXTRA`, `UNRELATED`, `UNCLEAR`) according to Code Review ownership. Required approvals may not be inferred from passing tests.
- No commit, push or deployment by default. User must separately authorize any such action, even after verification.

## Corrections

A verifier or reviewer failure creates a bounded correction request with failing criterion/check and an allowed delta. Assign to the original Builder where practical. After correction, create a new integrated candidate identity, rerun affected tests and repeat independent verification/review. Default at most one correction cycle; unresolved risk or scope expansion escalates.

## Final outcomes

- `VERIFIED`: actual independent context evaluated the final integrated candidate; required acceptance/preservation evidence and risk-appropriate checks pass; canonical review gate passed; no unresolved mandatory blocker.
- `IMPLEMENTED_UNVERIFIED`: code exists but independence, necessary evidence, or complete review is unavailable; do not describe as fully done.
- `FAILED_VERIFICATION`: relevant executed checks disproved required behavior and correction has not passed.
- `BLOCKED`: missing access, required tools, isolation, reliable candidate boundary, or safe execution prevents progress/required evidence.
- `NEEDS_DECISION`: ambiguity, scope expansion, material extra, contract conflict or irreversible operation requires user instruction.

Return accurate human report and optional structured ledger. The validator can reject contradictory metadata but cannot independently prove the software works.

## Safety law

Never overwrite user changes, silently retire existing enforcement, alter unapproved repo boundaries, run destructive commands, perform production operations or invent independent validation. Parallelism is an optimization, not a correctness requirement.
