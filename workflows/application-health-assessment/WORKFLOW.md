---
name: application-health-assessment
description: Optional portable multi-agent orchestration for the app-check skill. Allocate only relevant investigation lanes, challenge consequential findings in independent contexts, reconcile evidence, and deliver a read-only application-health assessment.
version: "1.0.0"
---

# Application Health Assessment Orchestration

## Invocation and ownership

This workflow is invoked by `skills/app-check/SKILL.md` **only when** multi-agent investigation offers material coverage benefits and the runtime actually supports isolated contexts. The skill owns applicability, questioning, health judgments and output. This workflow owns delegation, independent review, task budgets and evidence reconciliation. It is **not** an automatic checklist fan-out or implementation workflow.

## Preconditions

Obtain a compact application fingerprint, authorized repo roots/snapshots, implicated user journeys and risks, selected relevant lenses, known and uncertain workload facts, read-only permissions, and current evidence gaps. Exclude categories marked `NOT_APPLICABLE`; do not delegate them. Do not create artificial investigative tasks to fill a budget.

Separate **coordination cost** from engineering benefit: if the examination is local/narrow or one worker can validate all claims quickly, use one investigator and report the absence of independent verification. Do not fake parallelism. A useful small report is preferable to duplicated investigation.

## Agent task contract

All workers are read-only. A delegated task must include: task ID; precise single investigation question; application/repository boundary; inspected revision; necessary entrypoints/artifacts; relevant observable failure or uncertainty; permitted tools and safety restrictions; evidence format; explicit exclusions; stop condition and output budget. Workers may not write shared result artifacts or invoke nested workers without coordinator approval.

- **Focused investigator instances:** assigned distinct behavioral or operational questions, not permanent technology-based personas. Check source and authorized diagnostics; return findings plus counterevidence and `NOT_APPLICABLE` conclusions. Do not recommend a new architecture by default.
- **Test evidence investigator (conditional):** inspect test oracles and representative meaningful outcomes, execution logs and missing critical cases. Do not produce test files or claim a historical TDD cycle. This is a *lane*, not an additional mandatory agent definition.
- **Independent challenger/verifier:** a fresh context receives important hypothesis/location bundles, current application fingerprint, and original evidence access; it challenges applicability, severity, actual mechanism, test validity, simpler alternatives and false absences. Do not hand it an investigator verdict as a fact.

The coordinator owns one deduplicated evidence register. It must not count parallel agreement based on shared unverified summaries as independent evidence.

## Scheduling

Default budget ceiling: at most **three concurrent investigation instances**, **six total delegated tasks including retries and verification**, and **one follow-up wave**. Scale down for small apps, increase only with explicit justification and available runtime/tool budgets. Reserve one verification slot when there is a material finding. Prefer parallel tasks with disjoint source/uncertainty boundaries; serialize when they contend for a shared test environment or measurements.

Investigation order:

1. Coordinator selects applicable lenses using the canonical skill's application fingerprint.
2. Assign the highest-value unknowns whose answers could change a current decision, using separate bounded contexts only where beneficial.
3. Collect findings with evidence provenance, counterevidence and explicit limitation/coverage notes.
4. Challenge all P0/P1 candidates, disputed numerical claims, architecture-change recommendations and strong "no issue" claims. Independently reopen original code or artifacts whenever possible.
5. Deduplicate common causes; remove irrelevant findings; downgrade false certainty; use remaining budget to resolve only consequential gaps.
6. Return a single coherent executive assessment and detailed findings through the skill's report template.

## Stop, failure, and verification honesty

Stop when investigation is sufficient to distinguish NOW/NEXT/DEFER/NO_CHANGE for the relevant issues. Do not explore unaffected subsystems for completeness theater. If a verifier contradicts an investigator and reconciliation is impossible, report `DISPUTED`/`UNRESOLVED`, not a fabricated consensus.

When a tool is absent, permission denied, runtime inaccessible, or isolated delegation unsupported, preserve `LIMITED` or `BLOCKED` assessment status as applicable. Tool logs must identify the producing process and environment. A passing report validator proves structural consistency only. An independent verifier requires a genuinely separate context; coordinator self-review is labeled `SELF_CHECKED`.

The workflow never patches the application, provisions infrastructure, executes production load, changes test files, starts services, contacts external systems, or runs commands with side effects without separately authorized safe diagnostic scope. A suggested fix may be handed to `/code` only after explicit user instruction.
