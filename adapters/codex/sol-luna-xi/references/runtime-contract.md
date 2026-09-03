# Runtime Contract

## Parent requirement

The parent controller must be:

```text
model: gpt-5.6-sol
reasoning: high
```

Prefer a read-only parent sandbox.

Read-only sandboxing does not replace the behavioral rule that Sol-I must not inspect repository content.

If the host cannot establish the required parent runtime, fail closed with `BLOCKED`.

## Worker requirement

Install standalone custom agent definitions under:

```text
~/.codex/agents/
```

The exact registered names are:

```text
luna_scout_xi
luna_builder_xi
luna_validator_xi
luna_reviewer_xi
```

Every worker must pin:

```text
model: gpt-5.6-luna
reasoning: xhigh
```

Scout and reviewer use read-only sandboxes.

Builder uses the parent-authorized write sandbox.

Validator may use workspace write access only so repository checks can create ignored build artifacts or caches; it must not intentionally modify tracked files.

A renamed generic worker is not equivalent to selecting the registered custom agent.

If the current Codex session predates agent installation or does not expose the custom agent types, fail closed and start a fresh Codex task after installation.

## Installation assets

```text
agents/openai.yaml
runtime-agents/luna-scout-xi.toml
runtime-agents/luna-builder-xi.toml
runtime-agents/luna-validator-xi.toml
runtime-agents/luna-reviewer-xi.toml
install-windows.ps1
config-snippet.toml
INSTALL.md
```

## Routing law

All repository execution belongs to Luna-XI.

Never substitute:

```text
Terra
Sol
an unregistered generic worker
lower reasoning effort
```

If Luna-XI routing cannot be guaranteed, return `BLOCKED`.
