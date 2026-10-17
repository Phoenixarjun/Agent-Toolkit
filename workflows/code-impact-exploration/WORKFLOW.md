# Code Impact Exploration Workflow

## Invocation and boundaries

Invoked by `skills/code-explore/SKILL.md` for changes requiring source-backed impact mapping. The **parent coordinator**, not a worker, owns scope, budgets, scheduling, canonical evidence ledger, synthesis and final plan. Requires an actual multi-agent harness for independent assessment. No application edits or runtime mutation. If real isolation or read-only permissions cannot be established, return `limited`/`blocked`, not a fictional full team.

## Phase A: Intent and snapshot

1. Acquire feature goal, explicit must-preserve requirements and non-goals from user/intent artifact. Resolve only consequential ambiguity.
2. Declare authorized repository roots and no-go zones. Collect repo identity, HEAD or other pinned revision, dirty worktree status, relevant build/deploy state and unavailable dependencies.
3. Locate likely entrypoints and changed resource/contract boundaries via symbol search and manifests, not exhaustive directory crawling. Inspect relevant architecture decisions, active specs and migration notices; record contradictions with observed code or requested intent as explicit decision questions.
4. Write a **coverage seed**: each material obligation expressed as an inspectable question, with priority and acceptance evidence.
5. Decide lane count from independent boundaries, not requested maximum. Allocate worker concurrency and total tasks including retries. Reserve budget for critic and verifier; do not consume all slots on Scouts.

## Phase B: Exploration waves

1. Launch `code-path-explorer` instances for distinct forward/reverse execution slices and `code-contract-explorer` instances for independent API/event/schema/repo boundaries. Each task contains explicit questions, roots, revision, stop conditions, tool limits and the expected evidence IDs.
2. Workers independently inspect **original files**. They must not rely on sibling narratives, claim entire repo coverage, invent consumer repositories, or modify files. Return bounded observations, edges, unknowns and counterevidence.
3. Coordinator checks result conformance and merges individual records into the canonical ledger. On invalid/incomplete evidence, request a targeted correction only within remaining budget.
4. Parent reconciles overlapping edges and contradictory findings; no majority-vote truth. A precise conflict becomes a verifier hypothesis.

## Phase C: Coverage critique and correction

1. Spawn `code-coverage-critic` in a distinct context, giving it the *goal, pinned roots, declared coverage matrix and condensed evidence summary*, not a directive to approve the plan.
2. Critic looks for missing reverse consumers, alternate implementations, trust/identity boundaries, storage/event side effects, unexamined deploy/feature-flag paths, unexplained exclusions, and repeated investigations with no marginal gain.
3. Critic returns specific, priority-ranked new questions and exact search starting points. Parent either delegates a bounded follow-up, documents an authorized exclusion, or records unresolved blocker.
4. At most the allowed waves; budget exhaustion closes exploration with explicit gaps.

## Phase D: Independent finding verification

1. Spawn `code-evidence-verifier` in a fresh isolated context. Feed each high-impact claim as a hypothesis, location(s), original revision and concrete counterexample question, not the original worker's verdict.
2. Verifier independently opens original source to reconstruct relevant edges, actual dispatch or boundary, and contrary explanations. Return `confirmed`, `contradicted`, or `unresolved`; record a **different real context ID** and independent evidence refs.
3. Verify high-impact plan premises, retirement assumptions and disputed observations, plus final material evidence even when no material concerns were discovered. Avoid redundant check of every low-risk direct import.
4. Coordinator revises the ledger and plan to match verdicts. Do not erase rejected claims or promote unresolved assumptions to proven premises.

## Phase E: Ownership analysis and handoff

1. Create current-owner vs proposed-owner map by responsibility. Distinguish duplicate code from intentional defense-in-depth and safe transition needs.
2. Mark required, conditional and optional candidate changes. Sequence them by dependency and runtime rollout, preserving existing behavior and backward compatibility where justified.
3. Identify integration/public-seam tests, negative paths, consumer contract tests, migration safety, observability, rollback, and validation gates. Do not attempt these changes during exploration.
4. Produce the canonical ledger and human Code Impact Report. If validator available, run it and reconcile any errors; do not claim structural passing proves semantic truth.
5. Report `complete`, `limited`, or `blocked` with actual coverage, agent execution and unresolved questions. Stop. Fresh implementation context required.

## Anti-failure rules

- **No folder-based quota:** workers get graph slices and precise questions. A 10-agent run that duplicates findings is a failure of allocation.
- **No circular delegation:** only parent launches workers, applies budgets, updates ledger, and decides stop.
- **No fabricated independence:** contexts are separate only if actual harness supplies isolation; a role heading is not another agent.
- **No false source precision:** source path with no exact snapshot or inspected evidence is unresolved.
- **No destructive "cleanup" plan:** code removal is only a conditional proposal with contract-based proof obligations.
- **No conflation:** source exploration and change planning are different outputs; full Security Audit and actual coding remain separate capabilities.

## Valid completion gates

`focused`: real source trace, explicit coverage, independently verified material plan premises where contexts exist, honest limited status otherwise.

`standard` / `deep`: at least one path or contract investigator, distinct critique context, distinct verifier context that reviews final material claims, no material uncovered obligation presented as complete, evidence and plans internally consistent. More workers alone never satisfy assurance.
