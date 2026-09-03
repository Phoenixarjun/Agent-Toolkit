# Install Sol Luna XI in Codex

## Runtime mapping

```text
Sol-I
model: gpt-5.6-sol
reasoning: high
role: orchestrator only

Luna-XI
model: gpt-5.6-luna
reasoning: xhigh
role: repository execution
```

## Package

```text
sol-luna-xi/
├── SKILL.md
├── references/
│   ├── runtime-contract.md
│   ├── task-contracts.md
│   └── execution-discipline.md
├── agents/
│   └── openai.yaml
├── runtime-agents/
│   ├── luna-scout-xi.toml
│   ├── luna-builder-xi.toml
│   ├── luna-validator-xi.toml
│   └── luna-reviewer-xi.toml
├── install-windows.ps1
├── config-snippet.toml
└── INSTALL.md
```

## Windows setup

Open PowerShell inside this folder and run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows.ps1
```

The installer copies the full skill package to:

```text
%USERPROFILE%\.agents\skills\sol-luna-xi\
```

and the four custom agent definitions to:

```text
%USERPROFILE%\.codex\agents\
```

It does not overwrite the main Codex `config.toml`.

## Parent runtime

Start the Codex session with:

```text
Model: GPT-5.6 Sol
Reasoning: High
```

The custom worker definitions pin Luna-XI to:

```text
Model: GPT-5.6 Luna
Reasoning: xhigh
```

If desired, merge `config-snippet.toml` into the existing Codex config instead of selecting the parent runtime manually.

Do not blindly replace an existing config file.

## Invoke

```text
$sol-luna-xi Implement <task>.
```

After installation, start a fresh Codex task so the custom agent definitions are loaded.

If the custom Luna-XI agent types cannot be resolved, the skill must fail closed rather than silently degrading to another model or reasoning level.
