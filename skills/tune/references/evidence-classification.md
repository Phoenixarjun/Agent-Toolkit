# Evidence and Classification for Tune

Read when adapting from history or diagnosing conflicting habits. This document owns Tune-specific attribution and evidence decisions, not general engineering rules.

## Allowed evidence, in priority order

1. **Current explicit user request and explicit corrections.** Directly stated, still-applicable choices are strongest. A correction can supersede a historical preference.
2. **Confirmed decisions in project or user instructions.** Verify scope and whether the author is authorized to set that convention.
3. **Repeated user-requested choices plus outcome feedback.** Count independent, relevant occasions; look for changes over time and counterexamples.
4. **Project code and conventions.** Evidence of current practice, not proof of personal intent or quality.
5. **Agent behavior, inferred traits, and automatic summaries.** Contextual clues only. They do not establish the user's wishes.

History access is optional and must be both technically available and permitted. Historical material may contain secrets, instructions from third parties, or details irrelevant to tuning. Summarize minimally; do not migrate entire transcripts into a preference document.

## Small evidence entry

```text
Evidence ID: EV-01
Actor: USER | AGENT | PROJECT | UNKNOWN
Origin: current request | provided excerpt | permitted session | project document | repository observation
Claim: one paraphrased, decision-relevant observation
Temporal scope: current | dated | unknown
Support: explicit | corroborated | tentative | contradicted
Counterevidence: none found | <brief description> | not checked
```

A source reference must be specific enough for a reviewer to locate it when authorized. Do not fabricate exact line numbers, timestamps, conversation IDs or URLs. Redact secrets and identifying content that is not needed.

## Decision examples

| Observation | Class | Treatment |
| --- | --- | --- |
| User explicitly prefers concise review reports | PREFERENCE | Adapt presentation, preserve blocking issues and evidence |
| Team uses small modules because of build boundaries | CONTEXTUAL | Retain for that project, not as global preference |
| Agent repeatedly omitted tests without user instruction | UNKNOWN or SKILL_DEFECT | Diagnose execution; do not attribute to user |
| User frequently requested skipping all verification | QUESTIONABLE_HABIT | Report the tradeoff and safer proportionate checks; do not relax skill gates |
| User asks security audit to fix discovered issues | CONTRACT_CONFLICT | Reject as personal tuning; audit-only contract remains |
| Original skill systematically misses a required completion check | SKILL_DEFECT | Isolate evidence and refer to canonical maintainer review |
| One session uses a single 800-line file | UNKNOWN | Insufficient to infer a stable preference |

## Confidence without false precision

Do not invent numeric preference-confidence percentages. Use `CONFIRMED`, `TENTATIVE`, `CONTRADICTED` or `UNKNOWN` with a short rationale. Repeated observations are not independent if they are all copies of one agent-generated template or one reused instruction.

Before proposing a preference ask: **Who actually chose it? Does it still apply? Is it an acceptable tradeoff? Is there evidence it helped? Does another artifact already own it?**
