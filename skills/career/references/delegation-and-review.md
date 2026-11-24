# Delegation, review and rubric contract

Lead coordinator owns routing and reconciliation. An agent receives an assignment, not the entire career history. All agents read `rules/career/career-integrity.md`. No agent writes shared files, modifies rubrics, publishes, submits or launches subagents by itself; nested delegation is a request to the lead. Platform coordinators are logical workflow stages, not unrestricted autonomous agents.

## Assignment envelope

Provide `run_id`, `agent_id`, instance_id, objective, role/lens, scope (platform, section, role, question or source range), authorized evidence IDs and snapshot version, required output, frozen rubric/version, exclusions, time/iteration budget and permissions. Withhold unnecessary personal data, other reviewer findings, writer rationale and intended score. One author per section; other agents propose patches, never mutate it directly. Inspect actual isolation capability; if absent perform sequential bounded passes with DEGRADED status, not independent verification. Independent final verification of material external-facing factual claims and independent review of major plan revisions are hard gates for fully verified PASS. If isolation is unavailable, deliver draft/needs verification rather than PASS. Narrow low-risk presentation work without material claims need not invoke a verifier merely to satisfy a count.

Reuse existing `research` workflow and scout/verifier roles for external facts if their contracts fit. Do not ask a subagent to bypass its own restrictions or recursively load `career`. For 2–3 research scouts assign complementary queries (technical significance, production evidence, role/audience relevance) rather than duplicate search. For profile sections instantiate one optimizer per materially distinct selected section, not every possible section. For interview panels choose 2–4 competencies based on role/stage and use multiple instances only when responsibilities differ. Limit concurrency to supported runtime; batch when needed. Maintain comparable snapshots per round.

## Review envelope

Return scope, status (PASS | REVISE | BLOCKED | NEEDS_USER), evidence references, findings with severity (BLOCKER | HIGH | MEDIUM | LOW | PREFERENCE), observed problem, criterion, impact, smallest correction, uncertainty, and validation limitations. PASS is legitimate without findings. Blockers: false/conflicting material claims, confidentiality or authorization violations, missing essential evidence, confirmed hard eligibility conflict for a recommendation. High: materially wrong target, misleading presentation, unreachable primary outcome, feasibility problem. Medium/low are bounded improvements. Preference is optional and not a failure.

## Rubric and acceptance

Freeze invariants, domain anchors and task-specific requirements before reviewing. Rate applicable dimensions 0 (fails), 1 (weak), 2 (adequate), 3 (strong), 4 (exceptional with evidence), or NOT_ASSESSED / NOT_APPLICABLE with explanation. Not a hiring probability. Required dimensions must be at least 2 with adequate evidence; dimensions explicitly central to target may require 3, declared before review. A hard gate cannot be averaged away. A supported observation beats a confident unsupported preference. Do not force a numerical score for unobservable properties.

Use `quality-rubrics.md` for domain criteria. Custom criteria may be proposed before a run; record them and ask approval if they change the agreed outcome. After run, propose versioned rubric patch with failure case, reason, before/after criteria and regression examples; keep current version until approval. Never alter rubric mid-review to manufacture pass or failure. Rubric overrides cannot weaken integrity rules.

## Reconciliation

Collect isolated returns, deduplicate issues while preserving dissent. Identify owner (facts, positioning, content, presentation, capability, timeline or external source). Resolve highest-impact defects first; never use vote count as truth. Require evidence or label competing interpretations. Send the smallest targeted revision to the owner and reverify changed claims and cross-artifact consistency. Default max two correction rounds after first review; a third only if user explicitly extends scope. Stop on PASS or when only preferences remain. If material issue persists, return REVISE/BLOCKED with unresolved issue and next action; do not endlessly criticize. Scope and evidence may justify re-opening a prior pass, not subjective churn.
