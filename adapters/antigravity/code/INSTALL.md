# Antigravity Adapter: `/code`

Only this adapter contains product-specific model tiers, tool names and discovery paths. Keep all canonical implementation behavior under `skills/`, `workflows/` and `agents/`.

## Source documentation

- https://www.antigravity.google/docs/skills
- https://antigravity.google/docs/cli/subagents
- https://www.antigravity.google/blog/introducing-custom-agents

## Installed workspace structure (proposed)

```text
<target>/.agents/skills/code/                  # complete skills/code bundle
<target>/.agents/agents/agent-toolkit-code-builder.md
<target>/.agents/agents/agent-toolkit-code-verifier.md
<target>/.agent-toolkit/workflows/implementation-review-loop/WORKFLOW.md
<target>/.agent-toolkit/agents/code-builder/AGENT.md
<target>/.agent-toolkit/agents/code-verifier/AGENT.md
<target>/.agent-toolkit/skills/tdd/SKILL.md     # existing canonical dependency; if installed here
<target>/.agent-toolkit/skills/code-review/SKILL.md # existing canonical dependency
```

If your existing installer maps toolkit artifacts differently, use its resolved paths and adjust only adapter references. Do not create parallel copies of the same canonical workflow in competing locations. Do not overwrite any existing `.agents` entry without inspecting differences and obtaining approval.

Workspace skills are documented under `.agents/skills/<name>/`; the desktop app and IDE may use global `~/.gemini/config/skills/`, while the CLI has its own global scope. Prefer project-local installation for reproducibility. Explicit slash invocation is `/code`. The skill description states deliberate use only; platform auto-selection cannot be assumed perfectly disabled solely through description. See product-specific configuration and smoke tests.

Custom agents are documented under `.agents/agents/` and `~/.gemini/config/agents/`, with custom-agent `model` values `flash`, `pro`, or `inherit`. These two roles use `flash`. They **do not** assert any unverified exact model ID; the application/CLI model selector controls the available Flash variant. Inspect actual routed model in a live run.

`tools` use documented `view_file`, `grep_search`, `replace_file_content`, `run_command`. `commandExecutionPolicy: sandbox` requests sandboxed command behavior but is **not** a guarantee of strict least-privilege isolation; verify the actual permissions in the selected surface. Explicit approval still governs destructive actions. The read-oriented verifier has no edit tool. Test artifacts require a separate scoped action.

## Integration steps

1. Inspect the actual target repository and its existing `/code`, workflows, TDD, code-review, `AGENTS.md`, rules, adapters, profiles and catalog. Extend or reconcile; no blind overwrite.
2. Install canonical skill and **replace the old workflow in its existing path**, preserving upstream repository-specific modifications by review.
3. Register canonical Builder and Verifier roles. Ensure both can read canonical instructions from their actual installed location.
4. Install the two custom subagent adapter files. Verify their YAML parses and runtime sees both.
5. Confirm TDD skill is accessible only on the post-build verification branch. Do not copy canonical TDD into `/code` and do not force it into the initial Builder stage.
6. Register `code` entry in existing catalog/index and installer dependency closure based on the actual schema; update software-engineering profile **only if** the profile is meant to advertise opt-in skills. Do not auto-activate `/code` on routine coding.
7. Run deterministic validator unit tests, then a minimal live `/code` fixture with pre-existing dirty files and real separate Verifier context. Confirm no commit, push, deployment or destructive cleanup.

## Smoke tests before enabling writes

- `/code FOCUSED` is discoverable and not automatically used without user invitation.
- A Builder receives a bounded write scope, refuses a prohibited path, and does not overwrite user work.
- The independent Verifier is actually a distinct context. Without it the result cannot say `VERIFIED`.
- Basic feature integration completes **before** optional TDD-assisted verification.
- The Verifier invokes approved checks, flags stale evidence after correction and does not edit source files.
- A deliberately failing external behavioral probe produces `FAILED_VERIFICATION`.
- A conflict between parallel tasks results in serialized execution or `BLOCKED`, not simultaneous unsafe writes.

Do not claim compatibility, tool containment or independence from static YAML review alone. Verify in the actual Antigravity IDE/app/CLI build used.
