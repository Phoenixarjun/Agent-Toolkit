# The Agent Toolkit Philosophy

## Why I built this

AI coding models already know an extraordinary amount about languages, frameworks, and software design. What I kept needing in daily work was not another explanation of how to build an API. I needed **more consistent engineering behavior**: understanding what I meant, choosing proportionate solutions, questioning weak assumptions, protecting existing systems, and verifying the outcome.

Agent Toolkit is my attempt to make those behaviors reusable.

The collection comes from approximately eight months of working with coding assistants. It has been shaped by failed approaches, rework, unexpected behavior, repeated refinement, and practices I now return to deliberately. It is not a claim that every artifact has passed a controlled study or that my approach is universally correct.

## Curated, not collected

I do not believe that 300 or 500 skills automatically make an agent more capable. More files can mean overlapping triggers, conflicting advice, increased context use, and a harder system to maintain.

I would rather have **10 exceptional skills than 100 interchangeable ones**. The repository is intentionally aiming toward roughly **30 to 50 or fewer carefully selected skills** over time, with an even smaller collection if that is sufficient. That is a design target, not a quota to fill.

Every new capability must answer a difficult question: **What repeated decision or procedure will the agent handle materially better because this exists?**

If the answer is merely "it teaches Python" or "it says to write clean code," the model probably does not need a dedicated skill. If an existing capability can be improved, I prefer improving it.

## A skill is an engineering procedure

To me, a useful skill is a small behavioral program. It establishes the conditions for activation, the job it owns, the context to inspect, the decisions to make, the limits of its authority, the failure behavior, and the evidence required to finish.

That is different from a tutorial or a large prompt full of general advice. Good procedural guidance is useful because it changes decisions and actions at the moments that matter.

**Behavioral leverage matters more than length or artifact count.**

## How I want engineering work to happen

Start with the real goal. Understand the existing system before changing it. Prefer the smallest correct solution over unnecessary architecture. Keep responsibilities cohesive, but avoid inventing abstractions just to satisfy a principle or design pattern.

Look for failure paths, not only happy paths. Distinguish observed facts from assumptions. Use tests, runtime checks, source inspection, and independent review where appropriate. If a result is not verified, say so rather than dressing uncertainty up as completion.

These are guiding judgments. The enforceable procedures and safety requirements belong to their canonical rules and skills, not to this human-facing philosophy document.

## One owner, no instruction sprawl

The toolkit organizes artifacts by their responsibilities:

- **Skills** define repeatable capabilities.
- **Workflows** coordinate steps and specialist roles.
- **Rules** express enduring constraints.
- **Knowledge** provides deeper context and trade-offs.
- **Profiles** compose capabilities without copying them.
- **Evals and scripts** test behaviors and enforce deterministic requirements.
- **Adapters** translate canonical behavior into a particular coding assistant.

A principle should not be rewritten independently across several files. Reuse, reference, or genuinely specialize an existing owner. This makes updates safer and contradictions easier to detect.

## Evolve from evidence, not enthusiasm

An instruction is not better because it is longer. A skill is not better because it invokes more agents. I want to refine the smallest part of the system that caused a repeatable problem, then check whether the change actually helps.

The cycle is straightforward: **use, observe, diagnose, refine, evaluate, repeat**. Real-world feedback is valuable, but it does not automatically prove the cause of a failure. The model, context, tools, environment, and skill instructions can all contribute.

Whenever possible, mechanical checks should be performed by deterministic tools. Model reasoning should be reserved for work requiring judgment.

## My baseline, your engineering style

These playbooks reflect how I currently prefer to work, not how every engineer must work. Some people want fewer larger files; others prefer smaller modules. Some want concise findings; others want a detailed audit trail.

Those preferences can be tuned. **Correctness, safety, evidence, and the core guarantee of a capability should not be quietly tuned away.** That separation is the reason the toolkit keeps personal preferences distinct from canonical skill contracts.

## Before you adopt a skill

Read it. Check its trigger, file and tool access, permissions, dependencies, failure behavior, and completion criteria. Decide whether its assumptions are right for your project. Adopt one capability at a time and verify that it actually behaves as intended in your coding assistant.

This repository is not a promise that copying an instruction file produces reliable engineering automatically. It is a collection of procedures that I want to make increasingly clear, portable, and testable.

---

**The measure of Agent Toolkit is not how many instructions an agent receives. It is whether those instructions lead to better decisions and better evidence.**
