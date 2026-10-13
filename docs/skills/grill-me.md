# Grill Me

**Resolve consequential uncertainty before committing to a direction.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/grill-me/SKILL.md) |
| **Best for** | Discovery, requirement clarification, design challenge |
| **Interaction cost** | Low to moderate; depends on unanswered decisions |
| **Output** | Clarified decisions, assumptions, risks, and unresolved questions |

## The problem

Agents can accept a vague goal or a preferred design too quickly. The result may be a polished implementation of the wrong thing. A fixed questionnaire is not the answer either, because it wastes time on details that do not change the decision.

## When to use it

Use it when the objective is unclear, a requirement has material gaps, or a proposed solution needs pressure-testing. Skip it when the task is already sufficiently specified and a further interview adds little value.

## How it works

1. Identify whether the missing work is **discovery**, **clarification**, or **challenge**.
2. Inspect available facts rather than asking the user to repeat discoverable information.
3. Ask one high-value question at a time, prioritizing downstream risk.
4. Update the decision map, distinguish facts from assumptions, and stop when uncertainty no longer blocks the next step.

## Modes

| Mode | Focus |
| --- | --- |
| Discover | What problem actually matters, and to whom? |
| Clarify | Which requirements and boundaries change execution? |
| Challenge | Which assumptions or trade-offs could invalidate the proposal? |

The mode can change during a conversation. Question count is a budget, not a target.

## Example request

> Grill me on this architecture. Ask the most consequential question first, one at a time. Stop when the remaining unknowns would not change the decision.

## What you get

A better-defined direction, explicit uncertainties, and decisions that downstream skills can use. The capability does not implement, author a full solution plan, or silently choose product requirements.

## Boundaries and dependencies

No special subagent is required. If the user is asking for a durable implementation acceptance contract, [Intent Capture](intent-capture.md) is the better next step. For exploring alternative solution mechanisms, use [Problem to Solution](problem-to-solution.md).

**Cost guidance:** Relative interaction cost describes expected turns and reasoning, not a measured token price. Read the [canonical skill](../../skills/grill-me/SKILL.md) for precise invocation and stopping rules.
