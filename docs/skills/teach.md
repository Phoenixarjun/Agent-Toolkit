# Teach | Adaptive learning and mastery

**Status:** Experimental v1.0.0  
**Canonical skill:** [`skills/teach/SKILL.md`](../../skills/teach/SKILL.md)

Teach helps an agent explain, coach, and develop **demonstrable understanding** instead of merely generating information. It serves both technical domains and human skills through one adaptive procedure.

## Use Teach when

- "Teach me what makes a database transaction serializable."
- "Explain concurrency deeply, then check whether I can reason about interleavings."
- "Practice giving critical feedback at work. Don't write the answer before I try."
- "I want to master machine learning systems over multiple sessions. Build a learning map."
- "Wait, I don't understand why the token is still valid." (Inside an active teaching session.)

For short standalone fact retrieval, normal assistance is enough. For adversarial critique of a user's existing plan, use `grill-me`. For a source-backed briefing without instructional practice, use Research once it exists, or ordinary source investigation in the meantime.

## Operating modes

| Mode | Designed for | Common interaction |
| --- | --- | --- |
| Explain | One clear concept | Brief explanation and example |
| Deep Dive | First principles and internal mechanisms | Trace, derived mechanism, boundary, optional check |
| Practice | Independent reasoning or performance | User attempts, receives specific feedback, tries again |
| Mastery | Long-term subject development | Learning map, compact lessons, progress evidence |

The user can change modes mid-session. Socratic questioning is a method available across modes, not a required interrogation. Avoid forcing questions after every paragraph.

## Grounding

For established concepts, use a truthful, well-calibrated explanation and verify through simple experiments where appropriate. For changing or consequential material, verify current primary sources. A future `research` skill can provide evidence, but is **not required to install or operate Teach**.

## Continuity

Teach does not automatically access previous conversations or create a project directory. It can summarize a short checkpoint in chat. For persistent records, the user must designate an authorized learning workspace. The default is no file writes.

## What is verified?

`EXPLAINED` means the lesson was delivered; `ATTEMPTED` means a learner tried; `DEMONSTRATED` means the learner independently met a named criterion; `RETAINED` requires later retrieval/application with an actual time gap. None is a certification.

## Installation notes

The canonical `SKILL.md` and referenced files must remain available to the target agent. Register Teach using the live repository's `catalog/catalog.yaml` schema and validate via `python scripts/validate.py`. No new agent, workflow, permanent learning workspace, or Research stub is required. Availability and invocation methods vary by coding assistant; confirm the installed path through the applicable harness.

## Sources informing method (not hard dependencies)

- [Carnegie Mellon University, Learning Principles](https://www.cmu.edu/teaching/principles/learning.html)
- [Carnegie Mellon University, Retrieval Practice](https://www.cmu.edu/teaching/resources/instructionalstrategies/activelearningstrategies/retrievalpractice/index.html)
- [Carnegie Mellon University, Spaced Practice](https://www.cmu.edu/teaching/resources/instructionalstrategies/activelearningstrategies/spacedopractice/index.html)
- [Agent Skills specification](https://agentskills.io/specification)

These references motivate teaching strategies. They do not guarantee a live agent's instruction quality. Evaluate with the cases in `evals/teach/cases.yaml`.
