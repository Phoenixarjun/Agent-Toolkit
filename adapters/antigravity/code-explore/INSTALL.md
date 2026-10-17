# Antigravity Adapter: Code Impact Explorer

This is **runtime wiring only**. The canonical skill, workflow, evidence contract and agent behavior remain vendor-independent.

## Verified conventions (Google Antigravity 2.0 app and CLI)

- Skills: workspace `.agents/skills/code-explore/SKILL.md` or user-global `~/.gemini/config/skills/code-explore/SKILL.md`. The `/code-explore` command is used to explicitly invoke a discovered skill.
- Custom subagents: workspace `.agents/agents/<name>.md` or global `~/.gemini/config/agents/<name>.md`.
- Custom agent YAML `model` is a tier: `inherit`, `flash`, or `pro`. Do not place a human-facing model label or an unverified API ID in this field. Here it is `flash` by default; select the preferred available Flash variant in the application model selector. The user mentioned "Gemini 3.8 Flash I reasoning SABS"; the suffix is not an established custom-agent YAML identifier.
- Tool allowlist uses documented `view_file`, `grep_search`; `commandExecutionPolicy: off` for worker agents. No `run_command` granted by this adapter. Parent coordinator must use separately approved read-only repository status/navigation tools and cannot treat this configuration as a complete filesystem sandbox.
- Confirm agent discovery, `invoke_subagent` behavior, and exact model actually selected in the user's installed IDE and CLI. Do not claim live isolation from YAML alone.

Official references (review when integrating):
- https://www.antigravity.google/docs/skills
- https://www.antigravity.google/docs/subagents/
- https://www.antigravity.google/docs/migration/workflows-to-skills/

## Installation contract

Do **not** put canonical runtime procedures in a legacy `.agents/workflows/` command file. Antigravity's legacy workflow discovery is scheduled to end October 19, 2026. The portable skill is the user entrypoint; the toolkit's canonical workflow remains in its own artifact directory.

A complete project-local installation must make all of these readable to the main agent and workers:

```text
<target>/.agents/skills/code-explore/               # complete skill with references
<target>/.agents/agents/agent-toolkit-code-*.md     # four Antigravity custom subagent definitions
<target>/.agent-toolkit/agents/code-*/AGENT.md      # four canonical roles
<target>/.agent-toolkit/workflows/code-impact-exploration/WORKFLOW.md
<target>/.agent-toolkit/scripts/validate_code_exploration.py
<target>/.agent-toolkit/templates/documents/CODE-IMPACT-REPORT.md
```

If an existing `scripts/install.py` supports dependency closure, prefer that installer and adapt the paths. Do not use the above mapping to overwrite the target's `.agents/agents/`, `.agents/skills/`, or `.agent-toolkit/` content. Resolve conflicts explicitly, back up replacements if approved, and test real discovery and relative paths.

The four adapter agent files use workspace-local canonical role locations above; if the installer chooses another layout, update **only adapter references**, never fork the canonical roles. Validate that all four files load in the actual target context before Deep use. A missing role instruction means the worker must stop with a configuration error, not improvise a replacement.

## Example invocation

```text
/code-explore Deep
Goal: <desired behavior>
Authorized repositories: <exact roots>
Must preserve: <contracts/invariants>
Max concurrent subagents: 5
Max total delegated tasks: 10
Output location: <authorized path outside application source>
No code changes, commits, deployments, or cleanup.
```

When an additional repository is not explicitly in scope, the parent asks for authorization before inspecting it. Separate IDE/CLI installs may require different path configuration and access checks. Generic providers require their own adapter; do not pretend Antigravity YAML is portable.

## Smoke test before trusting the orchestration

1. Install one project-local copy and inspect the actual resolved skill and role paths.
2. Invoke `/code-explore` on a small known-safe fixture. Confirm the command is available and the skill is loaded.
3. Verify each custom agent can be selected or invoked and reports a **distinct real context ID**, without writable tools.
4. Run a low-budget multi-agent exploration and ensure the parent merges only source-backed observations.
5. Confirm a separate critic flags a deliberately missing downstream consumer and verifier rejects a deliberately false high-impact claim.
6. Confirm no source/config/test file is modified; check Git status before and after.
7. Run `python .agent-toolkit/scripts/validate_code_exploration.py <record.json>` and record the actual result.

Do not claim Antigravity or any other harness guarantees safe read-only execution without tool and filesystem permission verification. Do not claim benchmark quality before executing the behavioral evaluations.
