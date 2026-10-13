# Long-term learning paths | conditional reference

Only load for Mastery or explicitly requested syllabus, learning plan, progress tracking, or continued lessons. This is not a requirement for ordinary explanations.

## 1. Establish a mission and evidence of starting level

Capture, briefly:

- **Learning outcome:** what the learner wants to *do*, not only the topic name.
- **Application context:** work, personal use, exam, project, or general curiosity, if relevant.
- **Desired depth and available time:** only if supplied or necessary for planning.
- **Starting point:** claimed familiarity, demonstrated strengths, unknown gaps.
- **Constraints:** tools, time, access, prerequisites, learning preferences.

Do not force an interview when the goal is clear; offer a provisional plan for refinement. Do not inject an unrelated person's career goals, company targets, or assumed technology stack.

## 2. Build a dependency-aware learning map

Prefer **outcomes and essential mechanisms** over alphabetical concepts. Each node should answer:

1. What can the learner explain or perform after this unit?
2. What prerequisites are actually required?
3. How can success be observed?
4. Why does this unit matter for the learner's mission?

For a broad domain, tiers such as Fundamentals -> Working Systems -> Internals -> Advanced Judgment can help organize a map, but are optional and need not be four fixed tiers. Allocate units based on dependency and goal, not equal counts. Present concise milestones first; expand only the next relevant module.

If a specific company or certification matters, use *verified* official requirements or credible public material before claiming a named employer commonly asks particular questions. Without evidence, label the weighting a generic recommendation.

### Skips

Honor explicit learner skip requests as **self-reported known**, preserve them in the map, and avoid re-teaching. If later performance reveals a blocking gap, explain why a prerequisite deserves a short revisit. "Skipped" is not interchangeable with "independently demonstrated".

## 3. Lesson loop

- Select a next reachable unit with one tangible result.
- Teach a coherent slice using the strategy appropriate to the unit.
- Give an application or retrieval attempt when appropriate.
- Record what was attempted, demonstrated, uncertain, and worth revisiting.
- Advance, repair a prerequisite, or schedule a self-directed review suggestion based on evidence, not on an arbitrary lesson count.

Interleave prior relevant concepts when it helps transfer, but don't derail the learner's main goal. Favor revisits spread over days/weeks for durable retention. **Never claim a future reminder was scheduled** unless an authorized scheduling mechanism really did so.

## 4. State across sessions

**Chat-only is the default.** At the end of a meaningful Mastery segment, supply a compact user-visible checkpoint if durable state is not available.

If the user wants file-based continuity, ask them to designate and authorize a learning workspace. Use existing compatible project state if present. Do not write learning files inside an active code repository merely because it is the current working directory.

A minimal workspace may contain only:

```text
learning-workspace/
  LEARNING-PLAN.md         # Mission, map, priorities, prerequisites, learner-approved changes
  LEARNING-CHECKPOINT.md   # Latest topic, evidence state, gaps, sources, next action
```

**These are examples of generated user state, not new canonical Agent Toolkit templates.** Create only with user authorization and only if existing files don't already own the same responsibility. Avoid collecting sensitive learning histories by default.

Minimal checkpoint shape:

```text
Topic:
Goal:
Covered:
Attempt / evidence:
Status: EXPLAINED | ATTEMPTED | DEMONSTRATED | RETAINED | UNVERIFIED
Current misconception or open question:
Next useful action:
Source/verification note (if source-sensitive):
```

For continuation, read the authorized checkpoint, confirm it still applies, then resume. If the record is absent, request the minimal recap. Don't invent earlier progress.

## 5. When to switch from new material to review

Switch to practice/retrieval instead of automatically generating another lesson if:

- key prerequisites are not independently demonstrated;
- the learner has completed the map but cannot apply it to a new case;
- previous units haven't been revisited despite the stated retention goal;
- the learner requests a mock interview, simulation, or practice session.

For mastery completion, require evidence proportionate to the original outcome. Do not equate "all syllabus items covered" with "competent in the domain".
