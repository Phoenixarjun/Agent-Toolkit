# Teaching strategies | conditional reference

Read when choosing a non-obvious instructional method. This file **does not** define technical facts, permanent personas, or mandatory response formatting. The core sequence and learner contract are owned by `../SKILL.md`.

## Select an instructional lens from the learning objective

| Learner must be able to... | Prefer | Strong learning check |
| --- | --- | --- |
| Build a conceptual mental model | Start from a failure/problem; use one accurate analogy and name its limits | Explain how a change in assumptions alters the result |
| Understand code or systems behavior | Trace actual control/data flow, state transitions, edge cases, and runnable code where feasible | Predict program behavior or locate the failing step |
| Understand mathematical mechanisms | Motivate variables, derive incrementally, connect visual intuition to formal result, test counterexample | Re-derive one step and apply it to a changed case |
| Make engineering trade-offs | Compare requirements, constraints, failure behavior, and alternatives; use concrete scenarios | Defend a choice when a constraint changes |
| Perform a procedure safely | Demonstrate exact steps and conditions; identify irreversible steps and verification points | Perform a safe subset and interpret observable outcome |
| Communicate, negotiate, or lead | Explain principle briefly; roleplay authentic scenarios; critique concrete phrasing and consequences | Produce and revise a response to a changed audience |
| Build creative judgment | Analyze representative examples and their effects; contrast options; iterate from feedback | Make and defend a revision to the user's own artifact |
| Learn vocabulary or factual distinctions | Use short contextual examples, discriminations, low-stakes retrieval, and spaced reviews | Recall and apply distinctions without hints |

## Practical rules

1. **Mechanism before taxonomy.** Introduce names when they help explain an existing idea, not as an alphabetical prerequisite list.
2. **Examples must be local to the learner's goal.** Reuse relevant stack/background only when established. Don't invent employer affiliations or projects.
3. **Demonstrate only what can be demonstrated.** Mark hypothetical traces as examples. Do not present illustrative benchmarks, incidents, or interview questions as verified history.
4. **Diagram when the layout carries information.** Use a sequence diagram for message ordering, state diagram for states/transitions, graph for dependencies, table for comparison; skip decoration for one-dimensional explanations.
5. **Analogies are tools, not facts.** Point out where the analogy fails, especially for concurrency, security, ML, and distributed consistency.
6. **Let the learner do intellectual work.** Worked example -> faded hints -> independent attempt is a useful progression, but not mandatory for a one-off explanation.
7. **No fictional credentials.** Describe a domain lens (e.g., production operator, mathematical derivation, software debugger, communication coach) instead of claiming to be an engineer with a specific employer or decades of lived experience. Fictional roleplay characters must be clear as fictional.
8. **No universal diagram/code mandate.** Use code for executable mechanisms; simulation/roleplay/visuals for non-coding concepts. Choose what reduces cognitive load.

## Worked method selection

- **Concurrency:** show two legal interleavings of the same operations; let learner predict the outcome; then introduce the synchronization mechanism and its boundaries.
- **Database isolation:** start from the anomaly a transaction can observe, then show transaction timeline and explain what the isolation level prevents and does not prevent.
- **Backpropagation:** motivate optimization, derive gradients through a small graph, then check a sign/dimension assumption using an alternate example.
- **Constructive feedback at work:** show a problematic conversation, teach the specific change in wording, let the learner draft a response, then critique its effect and specificity.
- **System design interview:** when learning interview technique, simulate the interviewer and score what was demonstrated; when the user instead wants to pressure-test a proposed architecture, refer to `grill-me` rather than reimplement its procedure.

Use a perspective only while it changes a teaching decision. Do not create a permanent agent per subject.
