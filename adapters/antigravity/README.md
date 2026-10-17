# Antigravity Adapter

Runtime-specific configuration, subagent routing, and installation guidelines for Google Antigravity 2.0 and the Antigravity CLI (`agy`).

## Contents

- [`code-explore/INSTALL.md`](code-explore/INSTALL.md) - Installation procedure and runtime wiring for the Code Impact Explorer capability in Antigravity.
- `code-explore/agents/` - Custom subagent definitions configured for Antigravity with `model: flash`, read-only tools (`view_file`, `grep_search`), and `commandExecutionPolicy: "off"`.

## Installation

Capabilities can be installed directly into any target workspace using the Agent Toolkit installer:

```bash
# Preview installation for Antigravity
python scripts/install.py plan --skill code-explore --agent antigravity --all-optional --into <target-dir>

# Apply installation
python scripts/install.py apply --skill code-explore --agent antigravity --all-optional --into <target-dir>
```

## Runtime Behavior

When deployed into an Antigravity workspace:

1. **Skill Discovery**: Skills are placed in `<target>/.agents/skills/<skill>/` and invoked explicitly via slash commands (e.g., `/code-explore`). Legacy `.agents/workflows/` entrypoints are deprecated.
2. **Specialist Subagents**: Specialist agents are defined in `<target>/.agents/agents/<agent>.md` with frontmatter declaring `mainAgent: false` and `subagent: true`.
3. **Model Tiering**: Agent definitions declare `model: flash`. The active Flash model variant is mapped by the Antigravity model selector rather than a hardcoded model identifier.
4. **Tool Allowlist & Safety**: Exploratory workers are restricted to read-only inspection tools (`view_file`, `grep_search`) with `commandExecutionPolicy: "off"`. Shell command execution is disabled.
5. **Trusted Capabilities**: Canonical role definitions, workflows, scripts, and templates reside under `.agent-toolkit/`, isolating trusted procedures from target repository content.

## Architectural Boundaries

- This adapter provides instruction routing, subagent definitions, and tool boundaries. It does not replace Antigravity's native filesystem sandbox or approval gates.
- Canonical skills, rules, and workflows reside under their respective repository directories (`skills/`, `rules/`, `workflows/`).
