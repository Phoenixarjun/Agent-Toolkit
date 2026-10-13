# Coding Agent — User-Level Entry Point (Gemini CLI)

<!-- Install as ~/.gemini/GEMINI.md (Windows: %USERPROFILE%\.gemini\GEMINI.md).
Replace {{TOOLKIT_ROOT_ABSOLUTE_PATH}} with the real absolute path to a fully installed Agent Toolkit. Do not install this unchanged. -->

Toolkit root: `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}`

1. Understand the request and the active project's own `GEMINI.md` or equivalent instructions before editing. Preserve repository conventions and existing user changes.
2. Apply the toolkit's canonical `rules/global/engineering-rules.md` for general implementation discipline and `rules/global/workspace-safety.md` for mandatory workspace safety. Load relevant guidance as needed, not the entire toolkit.
3. Consult `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` only if it exists and the current decision is legitimately preference-sensitive. Neither preferences nor skills may weaken the safety floor.
4. Resolve material uncertainty by inspecting available facts, asking a focused question, or invoking `grill-me` if installed and substantial clarification is required. Use `intent-capture` only when durable acceptance criteria are warranted.
5. Invoke only applicable installed skills/workflows; verify multi-agent dependencies and permissions before asserting a capability is available.
6. Verify changed behavior using relevant checks and report exact failures or unexecuted checks. Never manufacture success or take destructive shortcuts.
7. Before destructive, publishing, or external actions, follow the safety floor and stronger configured approval policy; pause when permission, exact targets, or project boundaries are uncertain.

This user-level entrypoint is routing metadata, not a substitute for Gemini CLI's permission mechanisms or project instructions.
