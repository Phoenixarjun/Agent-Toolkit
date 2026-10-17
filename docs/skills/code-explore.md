# Code Explore | Implementation impact discovery

**Status:** Experimental v1.0.1  
**Canonical skill:** [`skills/code-explore/SKILL.md`](../../skills/code-explore/SKILL.md)

## Problem it solves

A coding agent can implement the requested feature without discovering an existing owner, downstream service, hidden consumer or compatibility contract. Code Explore investigates the actual relevant system **before** anyone edits it. It produces a source-backed change-impact map and implementation plan, not a code review or implementation.

## When to use it

Use it before a change with significant indirect effects, integrations, changes in responsibility ownership, nontrivial data/state transitions, or cross-repository contracts. Skip it for obvious local changes where evidence already establishes impact. Scope must name authorized repositories; the skill does not grant access to sibling repos or entire drives.

## How it works

It traces execution forward and dependent consumers backward, maps ownership and contracts, reconciles relevant architecture decisions with observed code, and checks version-specific external contracts when necessary. It challenges blind spots in an isolated context and independently rechecks material claims. A parent coordinator reconciles evidence and produces a plan. Separate workers are not an excuse to read every file or use every available agent slot.

| Mode | Typical effort | Assurance expectation | Output |
| --- | --- | --- | --- |
| Focused | Low to medium | Bounded tracing and targeted independent verification where supported | Short source-backed impact plan |
| Standard | Medium to high | Distinct coverage critic and verifier | Structured impact map and ordered plan |
| Deep | High | Multi-wave bounded exploration across permitted repositories | Comprehensive impact and compatibility plan |

Effort is qualitative. Agent limits and cost are configured separately; Deep does not mean unlimited delegation.

## Usage

```text
/code-explore Deep
Goal: <the behavior I want later>
Authorized repositories: <exact paths>
Preserve: <existing user-visible and API contracts>
No source modifications. Max 5 concurrent and 10 total agent tasks.
```

The exact invocation depends on the coding assistant. Antigravity-specific installation and `flash` routing belong to its adapter. Codex and other harnesses need corresponding adapters.

## Deliverables and trust

The human report contains the existing flow, affected components, ownership/overlap, source-backed findings, actual independent-review verdicts, a proposed implementation order and verification gates, and explicit gaps. A structured evidence ledger can be checked with `scripts/validate_code_exploration.py` for internal consistency. Neither a plausible plan nor a valid ledger proves the system actually works as described.

**Read-only:** no source changes, code removal, deployments, commits, destructive commands or unauthorized runtime probes. Any eventual implementation and review happens in a separate task/context. The skill remains separate from Security Audit, TDD and Code Review.

**Dependencies:** a complete multi-agent installation includes `workflows/code-impact-exploration/`, four `agents/code-*/` roles and actual isolated subagent support. `SKILL.md` alone cannot provide independent assurance.
