# Assessment, hints and comprehension recovery | conditional reference

Owns operational details of learner checks, feedback, misconception repair, and evidence states. `../SKILL.md` owns when teaching/assessment occurs.

## Calibration evidence ladder

- **Explicit learner statement:** useful starting hypothesis; never treat it as proof of deep mastery.
- **Observed past attempt:** may support a claim only when available in current authorized context. Separate learner answers from model-generated output.
- **Live demonstration:** strongest available evidence for the criterion tested, not for all related skills.
- **Delayed demonstration:** evidence of some retention only when there is a real time gap and independence from hints.

A learner's prior *use* of a tool is not a proof that they understand its internal mechanism; avoid the opposite error of ignoring genuinely demonstrated prior knowledge.

## Pick a check that discriminates understanding

Match question to intended capability:

- **Explain:** "Why can't the previous implementation guarantee X?" Ask for a causal explanation.
- **Predict:** "If we change this constraint/state/timing, what happens and why?" A predicted consequence tests a mental model.
- **Transfer:** "Apply the same mechanism to this unfamiliar but related case." Avoid matching the original example with renamed variables only.
- **Perform:** "Show the change, trace, calculation, script, spoken response, or decision." Inspect the output, not only the learner's confidence.

Prefer a single revealing prompt to a barrage of recall trivia. For a short Explain response, no check may be appropriate. In Practice and Mastery, wait for the learner to act before judging.

## Feedback contract

1. State what the learner's attempt demonstrates correctly.
2. Identify the **first material error**, with a specific counterexample, trace, or criterion.
3. Give the smallest next action that lets the learner correct it.
4. Recheck on the same underlying mechanism in a changed example.

Do not label a learner's entire reasoning as wrong because one step failed. Conversely, don't declare mastery because their final answer matches the expected answer if their explanation is incorrect.

## Hint ladder (Practice and Socratic)

Give only what is required; advance when the learner remains stuck or requests more help.

1. **Attention:** point to the failing condition or missing invariant.
2. **Contrast:** offer a counterexample or two alternative interpretations.
3. **Structure:** show a partial trace or decomposition with a missing step.
4. **Worked correction:** demonstrate the missing mechanism and give a related independent challenge.

If the learner expressly asks for the full solution, comply when permitted; do not prolong a forced coaching loop. Some important safety knowledge should be explained directly rather than withheld as a quiz.

## "Wait, what?" recovery

Classify the problem using observable evidence, and pick a **different representation**:

| Symptom | Likely gap | Recovery |
| --- | --- | --- |
| "I don't know that term" | Undefined prerequisite or jargon | Define the prerequisite in context and continue |
| "I followed the example but not why" | Missing causal model | Reverse the example; explain what breaks without the mechanism |
| "I don't see how it runs" | Unclear sequence or state | Use concrete timeline, table, code trace or simulation |
| "This contradicts what I know" | Misconception or legitimate discrepancy | Compare assumptions and check against evidence |
| "Too easy / too hard" | Level mismatch | Change starting point or scaffolding, not merely verbosity |
| "I can't apply it" | Weak transfer | Give a nearby task with fading hints, then a new task |

A repeated identical explanation is a failed recovery. Don't always ask a new question: sometimes the learner needs one precise missing step.

## Learning evidence states

- `EXPLAINED`: The agent delivered an explanation. **Not evidence that learner understood.**
- `ATTEMPTED`: Learner produced an attempt. Record observed work and feedback.
- `DEMONSTRATED`: Learner independently met a **specific, named criterion**.
- `RETAINED`: Learner later retrieved/applied without the earlier aid. Record gap and criterion.
- `UNVERIFIED`: No meaningful attempt or evidence available.

Do not fabricate test scores, numerical confidence, dates, or completion certificates. In human skills, some outcomes require external practice and feedback; a chat simulation has limited ecological validity.

## Stop conditions

- The learner achieved the requested scope and wants to stop: finish.
- An unclear prerequisite blocks progress: target that prerequisite or ask one focused question.
- Two successive checks fail for the same reason: change strategy or reduce task complexity.
- The user wants factual reference, not instruction: provide the reference answer, avoid involuntary exercises.
- The lesson is drifting into a plan critique: suggest `grill-me` only if the user wants that other outcome.
