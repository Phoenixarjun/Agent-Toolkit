# Problem to Solution

**Explore the right solution space before paying for deep design.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/problem-to-solution/SKILL.md) |
| **Best for** | Product ideas, ambiguous opportunities, significant solution decisions |
| **Interaction cost** | Moderate to high, depending on research depth |
| **Output** | Problem Brief, Solution Options, Decision Brief |

## The problem

Teams often jump from a symptom to a favorite implementation. The opposite failure is equally costly: spending weeks evaluating technology before checking whether a simpler operational or product change could solve the problem.

## When to use it

Use this capability when the *problem* is reasonably identifiable, but the best solution mechanism is not. It is useful for product discovery, architecture alternatives, and questions about whether a new system is necessary. Do not use it for a straightforward coding request or a single factual answer.

## How it works

1. Check the problem framing and separate evidence from assumptions.
2. Explore **meaningfully different mechanisms**, including non-software options when relevant.
3. Screen cheaply and retain a small set of defensible finalists.
4. Research only questions that could change the decision.
5. Challenge assumptions, failure modes, and feasibility before synthesizing a recommendation.

## Decision depth

The default progression is **cheap breadth → narrower shortlist → targeted depth**. Clarification with [Grill Me](grill-me.md) is conditional, not automatic. Deeper research is a later step, not the first response to every idea.

## Example request

> Our support team spends hours manually triaging incidents. Explore several genuinely different ways to reduce that burden, including process changes, before proposing an architecture.

## What you get

A concise problem definition, clearly differentiated solution directions, exposed trade-offs, and a Decision Brief. When evidence cannot justify a winner, the output should state what further evidence would change the decision.

## Boundaries and dependencies

This capability does not own final architecture or implementation. It can use Grill Me to resolve material ambiguity and Research for selected uncertainties. It does not assume that every problem should be solved with software.

**Cost guidance:** It can become expensive if the shortlist warrants substantial research. See the [canonical skill](../../skills/problem-to-solution/SKILL.md) for artifact contracts and precise steps.
