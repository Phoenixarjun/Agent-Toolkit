# Tune

**Personalize a skill to the engineer without importing bad habits.**

| | |
| --- | --- |
| **Capability** | [Canonical skill](../../skills/tune/SKILL.md) |
| **Best for** | Adapting one installed capability to an individual's preferences |
| **Interaction cost** | Moderate; higher for evidence-rich histories or forks |
| **Output** | Evidence-led customization proposal, approved preferences diff, or no change |

## The problem

A good general-purpose skill may not match every engineer's preferred working style. But blindly learning from a user's past chats can encode historical mistakes, agent-generated behavior, or unsafe shortcuts as permanent instructions.

## When to use it

Invoke Tune explicitly for **one installed skill** when you want it adapted to available, authorized evidence of how you work. It works for developers with no history as well as those with many accessible sessions. It does not automatically run after negative feedback.

## How it works

1. Inspect the target skill, rules, known preferences, and actually accessible history or feedback.
2. Distinguish explicit user choices from agent behavior and one-off context.
3. Classify compatible preferences, questionable habits, missing evidence, and invariant conflicts.
4. Propose the smallest non-duplicating change, usually to the existing preferences owner.
5. Show the exact diff and request approval before writing; test activation and behavior where possible.

## Example request

> Tune my installed code-review skill using my explicit preferences and authorized work history. Keep evidence requirements and safety rules intact. Propose changes before applying them.

## What you get

A transparent recommendation, not a magic rewrite. Tune may legitimately return **no change**, request a clarification, or report that the installed harness does not actually consume the target preference file.

## Boundaries and dependencies

Tune v1 personalizes a **consuming developer's copy**, not Agent Toolkit's shared canonical skill. It cannot assume access to private conversations, weaken mandatory safeguards, or rewrite its own procedure. A procedural fork is exceptional and needs stronger evaluation.

**Cost guidance:** Depends on evidence access and evaluation tools; estimates are qualitative. See the [canonical skill](../../skills/tune/SKILL.md) for approval and fallback states.
