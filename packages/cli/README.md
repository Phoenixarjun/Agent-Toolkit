# @agent-toolkit-core/cli

The official npm distribution and CLI for **Agent Toolkit** — reusable engineering procedures, skills, workflows, specialist agents, and companion applications for AI coding assistants.

## Supported Coding Assistants

- **Anthropic Claude Code CLI** (`claude-code`)
- **OpenAI Codex CLI** (`codex`)
- **Cursor IDE** (`cursor`)
- **Google Gemini CLI** (`gemini-cli`)
- **GitHub Copilot** (`github-copilot`)
- **OpenCode CLI** (`opencode`)
- **Google Antigravity 2.0** (`antigravity`)

## Usage

Run directly with `npx` (zero prerequisites required on consumer machine):

```bash
# List all available skills, profiles, and supported adapters
npx @agent-toolkit-core/cli list

# Inspect capability details and required resources
npx @agent-toolkit-core/cli inspect --skill code-review
npx @agent-toolkit-core/cli inspect --profile software-engineering

# Preview installation plan without modifying files (dry-run)
npx @agent-toolkit-core/cli plan --skill code-review --adapter claude-code

# Install a standalone skill or profile into current project
npx @agent-toolkit-core/cli install --skill code-review --adapter claude-code
npx @agent-toolkit-core/cli install --profile software-engineering --adapter cursor

# Install into a specific project directory
npx @agent-toolkit-core/cli install --skill career --adapter claude-code --into ./my-project

# Include all optional dependencies
npx @agent-toolkit-core/cli install --profile software-engineering --adapter claude-code --all-optional

# Validate installed project integrity
npx @agent-toolkit-core/cli doctor
npx @agent-toolkit-core/cli doctor --into ./my-project

# Launch local companion viewers
npx @agent-toolkit-core/cli open career
npx @agent-toolkit-core/cli open visualize
```

## Safety & Data Protection

- **No Overwriting User Files**: Unmanaged file collisions safely abort by default.
- **Managed Blocks Only**: Assistant entrypoint files (`CLAUDE.md`, `AGENTS.md`) preserve all custom user instructions outside the managed block markers.
- **User Data Isolation**: Generated career plans, resumes, and architecture graphs stay strictly in user space; upgrading capabilities never touches user records.
- **100% Offline & Private**: Zero network calls during installation, zero telemetry, and zero model execution during setup.

## License

MIT © 2026 Naresh.B.A
