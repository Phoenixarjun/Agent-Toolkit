# Agent Base

Agent Base is a personal source-of-truth repository for reusable coding-agent skills, workflows, rules, agents, prompts, knowledge, evaluations, profiles, and vendor-specific adapters.

The repository is intentionally not an agent platform. It stores the engineering playbooks you want to own, improve, version, evaluate, and reuse across coding assistants.

## Design principles

1. Author canonical behavior once.
2. Keep vendor-specific wiring at the edges.
3. Keep each artifact responsible for one thing.
4. Prefer metadata over deep taxonomy.
5. Keep skills concise and use progressive disclosure.
6. Treat user intent as the acceptance contract.
7. Require evidence before claiming completion.
8. Do not invent portability where a tool has a proprietary format.

## Repository model

```text
agent-base/
├── skills/          reusable task capabilities
├── workflows/       ordered multi-step execution patterns
├── rules/           persistent engineering constraints
├── agents/          bounded specialist roles
├── prompts/         reusable explicit prompts
├── knowledge/       explanatory engineering references
├── profiles/        curated artifact bundles
├── evals/           regression cases for agent behavior
├── catalog/         searchable artifact registry
├── templates/       scaffolds for new artifacts
├── adapters/        vendor-specific runtime/configuration wiring
├── scripts/         repository utilities
├── AGENTS.md        instructions for agents editing this repository
└── CONTRIBUTING.md  quality and contribution contract
```

## Artifact boundaries

| Artifact | Use it for | Do not use it for |
|---|---|---|
| Skill | A repeatable task with a clear trigger and output | Permanent global policy |
| Workflow | Ordering and coordinating multiple steps or roles | Deep domain knowledge |
| Rule | A persistent non-negotiable behavior | Long tutorials |
| Agent | A specialist role with bounded responsibility | General-purpose prompting |
| Prompt | A reusable explicit request | Always-on behavior |
| Knowledge | Principles, explanations, references, tradeoffs | Mandatory execution policy |
| Profile | A curated bundle of artifacts for a working mode | Duplicating artifact content |
| Eval | Behavioral regression cases | Production implementation |
| Adapter | Tool-specific mapping, installation, or runtime configuration | Canonical cross-tool behavior |

## Included seed artifacts

- `skills/code-review`: intent-aligned pre-commit code review and commit gate
- `workflows/implementation-review-loop`: portable implementation -> validation -> review loop
- `rules/global/engineering-rules.md`: core engineering rules
- `agents/architect`: architecture specialist with anti-overengineering discipline
- `prompts/architecture-grill.md`: requirements pressure-test prompt
- `knowledge/engineering/solution-design-principles.md`: compact design principles
- `profiles/software-engineering.yaml`: initial bundle
- `evals/code-review/cases.yaml`: regression scenarios for the code-review skill
- `adapters/codex/sol-luna-xi`: Codex-specific Sol-I/Luna-XI orchestration package

## Validate

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
```

The validator checks skill frontmatter, Agent Skills naming constraints, skill size, YAML validity, catalog paths, and profile references.

## Create a new artifact

```bash
python scripts/new_artifact.py skill api-contract-review
python scripts/new_artifact.py workflow release-gate
python scripts/new_artifact.py agent security-reviewer
python scripts/new_artifact.py rule database-rules
python scripts/new_artifact.py prompt incident-triage
python scripts/new_artifact.py knowledge caching-principles
```

Scaffolding creates a minimal artifact. The author is still responsible for making the content specific and useful.

## Canonical versus vendor-specific

A portable capability belongs in the top-level artifact directories.

```text
skills/code-review/
```

A capability that depends on a specific model, agent runtime, installation path, or proprietary configuration belongs under an adapter.

```text
adapters/codex/sol-luna-xi/
```

Do not create separate copies of the same canonical skill for every assistant. Add an adapter only when the assistant requires additional wiring.

## Skill quality bar

A skill should answer five questions quickly:

1. When should this activate?
2. What exact job does it own?
3. What must it inspect or consume?
4. What sequence must it follow?
5. What evidence and output prove completion?

If a skill needs large rubrics, schemas, or runtime contracts, place them in `references/` and load them only when needed.

## Growth strategy

Keep the physical hierarchy shallow. Use catalog metadata and profiles for discovery instead of building a deep `technical/backend/java/...` folder tree.

Add categories when they help search. Do not move artifacts simply because they apply to multiple domains.
