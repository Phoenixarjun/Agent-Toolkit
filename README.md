<div align="center">

# Agent Toolkit

### Engineering playbooks for coding agents.

**A personal source of truth for reusable skills, workflows, rules, agents, prompts, knowledge, evaluations, profiles, and runtime adapters.**

<br />

![Status](https://img.shields.io/badge/status-evolving-111111?style=for-the-badge)
![Focus](https://img.shields.io/badge/focus-agent%20engineering-111111?style=for-the-badge)
![Design](https://img.shields.io/badge/design-tool--agnostic-111111?style=for-the-badge)
![Codex](https://img.shields.io/badge/Codex-adapter%20included-111111?style=for-the-badge)
![Validation](https://img.shields.io/badge/validation-automated-111111?style=for-the-badge)

<br />

![Skills](https://img.shields.io/badge/skills-procedural-blue?style=flat-square)
![Workflows](https://img.shields.io/badge/workflows-composable-blueviolet?style=flat-square)
![Evals](https://img.shields.io/badge/evals-regression%20tested-success?style=flat-square)
![Profiles](https://img.shields.io/badge/profiles-curated-orange?style=flat-square)
![Adapters](https://img.shields.io/badge/adapters-vendor%20specific-red?style=flat-square)

</div>

---

## What is Agent Toolkit?

Agent Toolkit is the repository where I keep the engineering behavior I want coding agents to reuse.

It is **not an agent platform**, a framework, a prompt marketplace, or a collection built to maximize the number of skills.

It is a deliberately small and evolving set of engineering playbooks extracted from real work.

The repository exists to answer a different question:

> **How do I make a capable coding agent approach recurring engineering problems in a consistently better way?**

Modern coding models already know Java, Python, React, FastAPI, Spring Boot, databases, APIs, testing, and thousands of other technologies.

I do not need a separate skill to teach a capable model what a REST endpoint is.

What is much more valuable is teaching the agent **how I want it to approach a problem**.

How should it recover intent?

How should it pressure-test a design?

How should it decide whether complexity is justified?

How should it review a change against the original request?

What evidence must exist before it claims the work is complete?

Those repeatable procedures are what this repository calls **skills**.

---

> [!IMPORTANT]
> ## Do not copy skills blindly.
>
> A skill is not harmless text.
>
> It can influence how an agent reasons, reads files, modifies code, invokes tools, executes commands, interprets requirements, and decides that work is complete.
>
> Treat skills the same way you would treat executable engineering logic.
>
> **Read them end-to-end before using them.**
>
> Understand their assumptions, boundaries, permissions, failure modes, dependencies, and expected outputs.
>
> Then decide whether that behavior actually belongs in **your** engineering workflow.
>
> A skill that works well for me may encode decisions that are wrong for you.
>
> Reuse the ideas. Adapt the procedure. Evaluate the behavior.
>
> **Never inherit an agent's thinking process without understanding what you are inheriting.**

---

## This repository is intentionally small

You will not find hundreds of thin skills organized like:

```text
backend/
frontend/
python/
fastapi/
spring-boot/
postgresql/
react/
docker/
```

That is mostly domain knowledge.

Capable models already possess a significant amount of it, and reusable technical knowledge can be placed in `knowledge/` when additional context is genuinely useful.

Agent Toolkit instead optimizes for **behavioral leverage**.

A skill earns its place when it gives the agent a reusable procedure that materially changes the quality, consistency, safety, or reliability of its work.

The goal is not:

```text
more skills
more prompts
more agents
more files
```

The goal is:

```text
fewer artifacts
stronger behavior
clearer boundaries
better evidence
measurable improvement
```

Every artifact should justify the context it consumes.

---

## Skills are behavioral programs

A skill in this repository is best thought of as a small behavioral program for a capable model.

It defines things such as:

```text
trigger
   ↓
required context
   ↓
decision process
   ↓
execution procedure
   ↓
validation
   ↓
completion evidence
```

A good skill should quickly answer:

1. **When should this activate?**
2. **What exact job does it own?**
3. **What information must it inspect?**
4. **What procedure must it follow?**
5. **What decisions can it make?**
6. **Where must it stop or escalate?**
7. **What evidence proves completion?**

The objective is not to tell the model everything it knows.

The objective is to constrain the parts of its behavior where consistency matters.

---

## Skills evolve

The skills here are not intended to become frozen documents.

They come from real engineering use.

```text
use
 ↓
failure
 ↓
observation
 ↓
refinement
 ↓
evaluation
 ↓
reuse
```

When an agent makes a recurring mistake, the first question is not necessarily:

> "How do I make the prompt longer?"

It is:

> "What decision rule, boundary, missing context, validation step, or artifact is responsible for this failure?"

The repository evolves from those observations.

That means a skill you see today may be different later.

Not because it is being expanded indefinitely, but because unnecessary instructions are removed, weak instructions are tightened, failure modes are discovered, and better abstractions replace poorer ones.

**The repository is versioned engineering behavior.**

---

## Design philosophy

Agent Toolkit follows a few core principles.

### 1. Author canonical behavior once

Cross-tool engineering behavior should have one authoritative definition.

Do not maintain separate copies of the same skill for Codex, Claude Code, Cursor, Gemini CLI, or another coding assistant.

---

### 2. Keep vendor behavior at the edges

Portable behavior belongs in canonical artifact directories.

Vendor-specific configuration belongs in `adapters/`.

```text
Canonical behavior
        │
        ├── skills/
        ├── workflows/
        ├── rules/
        ├── agents/
        └── profiles/
                │
                ▼
           adapters/
                │
                ▼
        Coding assistant
```

---

### 3. One artifact, one responsibility

A skill should not become a workflow.

A workflow should not become a knowledge base.

A rule should not become a tutorial.

A profile should not duplicate the artifacts it composes.

Clear boundaries make behavior easier to understand, evaluate, and evolve.

---

### 4. Treat intent as the acceptance contract

Implementation is not successful merely because the code runs.

The result must satisfy the user's actual intent.

Where appropriate, Agent Toolkit captures that intent explicitly and uses it as an authority during implementation and review.

---

### 5. Require evidence before completion

Agents should not confuse:

```text
"I changed the code."
```

with:

```text
"I proved the requested outcome."
```

Claims of completion should be grounded in appropriate evidence such as tests, commands, diffs, runtime behavior, validation results, or source inspection.

---

### 6. Prefer progressive disclosure

Agent context is finite.

Always-needed behavior stays close to the skill.

Conditional depth moves outward.

```text
SKILL.md
   │
   ├── references/
   ├── knowledge/
   ├── scripts/
   └── external sources when required
```

Load complexity only when the task actually needs it.

---

### 7. Prefer deterministic mechanisms when reasoning adds no value

If something can be reliably checked by a validator, schema, script, or rule, use that instead of spending model reasoning on it repeatedly.

Models should reason where judgment matters.

Machines should verify what can be verified deterministically.

---

## Repository architecture

```text
agent-toolkit/
├── .github/
│   └── workflows/        repository automation
│
├── adapters/             vendor-specific runtime/configuration wiring
├── agents/               bounded specialist roles
├── catalog/              searchable artifact registry
├── docs/                 supporting repository documentation
├── evals/                behavioral regression cases
├── forms/                structured engineering intake forms
├── knowledge/            reusable engineering references
├── profiles/             curated working-mode bundles
├── prompts/              explicit reusable prompts
├── rules/                persistent engineering constraints
├── scripts/              deterministic repository utilities
├── skills/               reusable agent capabilities
├── templates/            scaffolds for new artifacts
├── workflows/            multi-step execution patterns
│
├── AGENTS.md              instructions for agents editing this repository
├── CONTRIBUTING.md        artifact quality and contribution contract
├── README.md
└── requirements.txt
```

The physical hierarchy stays intentionally shallow.

Discovery belongs primarily in metadata, the catalog, and profiles rather than increasingly deep directory trees.

---

## Artifact model

| Artifact | Owns | Does not own |
|---|---|---|
| **Skill** | A repeatable capability with a defined trigger, procedure, and output | Permanent global policy |
| **Workflow** | Ordering and coordinating multiple steps or capabilities | Deep domain knowledge |
| **Rule** | Persistent non-negotiable engineering behavior | Long explanations |
| **Agent** | A bounded specialist role | General-purpose prompting |
| **Prompt** | A reusable explicit request | Always-on behavior |
| **Knowledge** | Principles, references, tradeoffs, and explanatory depth | Mandatory execution policy |
| **Profile** | Composition of artifacts for a working mode | Copies of those artifacts |
| **Eval** | Behavioral regression scenarios | Production implementation |
| **Adapter** | Vendor-specific installation, runtime, or configuration mapping | Canonical engineering behavior |
| **Script** | Deterministic repository mechanics | Judgment-heavy agent behavior |
| **Template** | Minimal scaffolding for new artifacts | Canonical implementation guidance |

---

## How the pieces compose

A typical execution path looks like this:

```text
User intent
    │
    ▼
Profile
    │
    ├── Rules
    ├── Skills
    ├── Workflows
    ├── Agents
    └── Knowledge
          │
          ▼
      Adapter layer
          │
          ▼
     Coding assistant
          │
          ▼
   Evidence + Evals
```

Profiles compose behavior.

Adapters translate that behavior into the requirements of a particular runtime.

The canonical artifacts remain independent from the vendor whenever possible.

---

## Current capabilities

The repository currently includes capabilities around areas such as:

### Engineering

```text
intent capture
code review
implementation/review loops
architecture pressure testing
problem-to-solution exploration
test-driven development (TDD)
security audit
```

### Product and solution discovery

```text
problem framing
solution exploration
option evaluation
decision support
```

### UI engineering

```text
UI/UX design
design review
visual-system guidance
accessibility
interaction and motion
anti-generic interface design
```

### Specialist agents

```text
architect
UI critic
security auditor
```

### Runtime integration

```text
Codex-specific Sol / Luna orchestration adapter
```

These are examples of the current repository state, not a commitment to build a large taxonomy around them.

New artifacts are added when repeated real-world use demonstrates that a reusable capability deserves to exist.

---

## Canonical vs vendor-specific

Portable behavior belongs at the repository root.

```text
skills/code-review/
```

Vendor-specific wiring belongs under an adapter.

```text
adapters/codex/sol-luna-xi/
```

The adapter may define things such as:

```text
runtime configuration
installation
model routing
vendor-specific agent definitions
filesystem placement
tool wiring
proprietary configuration
```

It should not fork the canonical behavior unnecessarily.

If a platform needs special wiring, adapt the behavior.

Do not duplicate the behavior.

---

## Example: what belongs where?

Suppose an agent should review code before a commit.

The reusable review methodology belongs in:

```text
skills/code-review/
```

The sequence:

```text
implement
validate
review
repair
revalidate
```

belongs in:

```text
workflows/implementation-review-loop/
```

A permanent rule such as:

```text
Do not claim completion without evidence.
```

belongs in:

```text
rules/
```

Explanations about review risk belong in:

```text
knowledge/
```

or a skill's conditional:

```text
references/
```

Codex-specific installation or runtime configuration belongs in:

```text
adapters/codex/
```

That separation is intentional.

---

## Profiles

Profiles are curated working modes.

Instead of manually assembling many artifacts every time, a profile defines the combination appropriate for a particular kind of work.

Current examples include:

```text
profiles/
├── product-discovery.yaml
├── security-audit.yaml
├── software-engineering.yaml
└── ui-ux.yaml
```

Profiles reference canonical artifacts.

They do not duplicate them.

---

## Evals

A reusable agent behavior should be testable.

```text
evals/
├── code-review/
├── grill-me/
├── intent-capture/
├── problem-to-solution/
├── security-audit/
├── tdd/
└── ui-ux-design/
```

Evals exist to catch behavioral regressions as artifacts evolve.

They help answer questions such as:

```text
Did the skill activate correctly?

Did it gather the required context?

Did it violate its boundary?

Did it over-engineer the solution?

Did it accept unsupported assumptions?

Did it claim completion without evidence?

Did a recent edit make previously correct behavior worse?
```

Agent behavior should evolve with feedback, not intuition alone.

---

## Creating an artifact

Use the repository scaffolder:

```bash
python scripts/new_artifact.py skill api-contract-review
python scripts/new_artifact.py workflow release-gate
python scripts/new_artifact.py agent security-reviewer
python scripts/new_artifact.py rule database-rules
python scripts/new_artifact.py prompt incident-triage
python scripts/new_artifact.py knowledge caching-principles
```

Scaffolding only creates the structure.

It does not prove that the artifact should exist.

Before introducing something new, ask:

```text
Does this already exist?

Can an existing artifact be extended?

Is this actually a skill?

Is this reusable enough to deserve a canonical artifact?

Does it materially improve agent behavior?

Can its behavior be evaluated?

Is this canonical behavior or vendor-specific wiring?
```

If those questions do not have good answers, the artifact probably does not belong here.

---

## Validation

Install repository requirements:

```bash
python -m pip install -r requirements.txt
```

Run validation:

```bash
python scripts/validate.py
```

The validator checks repository invariants such as artifact structure, metadata, YAML validity, catalog references, profile references, naming constraints, and skill requirements.

Repository validation also runs through GitHub Actions.

---

## Skill quality bar

Before a skill is considered useful, it should have:

### Clear invocation

The agent can determine when the capability should and should not activate.

### Precise ownership

The skill owns one coherent job.

### Required context

The skill identifies what must be inspected before reasoning or acting.

### Procedural value

The instructions materially change how the agent approaches the problem.

### Decision boundaries

The skill explains where judgment is allowed and where hard constraints apply.

### Failure behavior

The agent knows what to do when required context, evidence, permissions, or dependencies are missing.

### Completion criteria

There is an observable condition that distinguishes completed work from attempted work.

### Evidence

The agent can support important claims with something verifiable.

### Regression coverage

Important behavior can be represented in evaluations where practical.

---

## The no-op test

Every instruction consumes context.

For each line in a skill, ask:

> **If this line disappeared, would the agent's behavior become meaningfully worse?**

If the answer is no, remove it.

This repository optimizes for behavioral density rather than document length.

A short skill that reliably changes agent behavior is more valuable than a thousand-line skill containing information the model already knows.

---

## What Agent Toolkit is not

It is not:

- a collection of hundreds of generated skills
- a directory of technology tutorials
- a replacement for model knowledge
- an autonomous agent framework
- a universal prompt library
- a vendor abstraction layer pretending every runtime is identical
- a benchmark optimized for repository size
- a place to encode every engineering opinion as permanent policy

It is an engineering system for owning the reusable parts of **how agents work**.

---

## Trust model

Anything that changes agent behavior deserves review.

Before adopting an artifact from this repository or any other repository inspect:

```text
what activates it
what context it reads
what tools it can use
what files it can modify
what commands it may execute
what assumptions it makes
what decisions it can take autonomously
what it considers "complete"
what happens when it fails
```

Then test it against your own workflow.

Do not evaluate a skill only by how convincing its Markdown looks.

Evaluate the behavior it produces.

---

## Growth strategy

Agent Toolkit grows from repeated engineering needs.

The process is intentionally conservative:

```text
real problem
    ↓
repeated pattern
    ↓
identify reusable behavior
    ↓
choose the correct artifact
    ↓
implement minimally
    ↓
use in real work
    ↓
observe failures
    ↓
refine
    ↓
evaluate
```

The repository should become **better**, not merely larger.

Deep folder hierarchies and large artifact counts are not signs of maturity.

Reliable behavior is.

---

## Guiding idea

> **Capable models already know a lot.**
>
> The highest-leverage agent engineering often comes from improving how they approach the work not from restating everything they already know.

Agent Toolkit is where those approaches are captured, tested, refined, and reused.

---

<div align="center">

### Build fewer artifacts. Make each one earn its context.

**Intent → Procedure → Evidence → Evaluation → Improvement**

</div>