# Coding Agent - User-Level Entry Point (Codex)

<!-- Install as ~/.codex/AGENTS.md (Windows: %USERPROFILE%\.codex\AGENTS.md).
Replace {{TOOLKIT_ROOT_ABSOLUTE_PATH}} with the real absolute path to a fully installed Agent Toolkit. Do not install this unchanged. -->

Toolkit root: `{{TOOLKIT_ROOT_ABSOLUTE_PATH}}`

1. Understand the request and the active project's existing instructions before editing; reuse established code and tests. Do not assume every vague request requires an interview.
2. Follow the toolkit's canonical `rules/global/engineering-rules.md` for general implementation discipline and `rules/global/workspace-safety.md` for non-negotiable workspace safety. Read the applicable sections when working, not every reference indiscriminately.
3. For a choice the project leaves open, consult `<active-project>/.agent-toolkit/ENGINEERING-PREFERENCES.md` when present. A preference cannot override the safety floor, project contract, or a skill invariant.
4. For consequential ambiguity, inspect discoverable facts first; ask one focused question or use the installed `grill-me` capability when substantial decisions remain. Use `intent-capture` only when a durable change contract is useful.
5. Use installed skills and workflows only when their triggers match the task. Do not pretend a skill's cross-directory agents, scripts, or workflow dependencies exist unless installed and supported.
6. Preserve pre-existing user changes, verify relevant behavior, and report checks actually executed. Do not claim completion from unrun tests.
7. Before destructive or external operations, apply the safety floor and any explicitly selected stricter approval mode. Never use a broad or unverified deletion target; stop and ask when required approval or scope is missing.

This entrypoint routes to canonical artifacts; it does not redefine their procedures. Agent Toolkit's repository-root `AGENTS.md` governs contributors to **that repository**, not every project consuming its skills.
