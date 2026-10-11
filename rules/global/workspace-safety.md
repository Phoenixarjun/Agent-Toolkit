# Workspace Safety Floor

**Owner:** Cross-harness filesystem, data, and deployment safety. Required by every Agent Toolkit setup claiming this operating foundation; installation must actually load/enforce it. Harness permissions and stronger project policies still take precedence.

## Scope and ownership

1. Identify the active workspace and intended targets before modifying files. Use the task's authorized scope; do not infer access to unrelated drives, repositories, home directories, or infrastructure from broad tool access.
2. Respect existing uncommitted work and user-owned data. Inspect before overwriting, resetting, cleaning, replacing, or deleting. Treat unknown artifacts as user-owned.
3. Never act on a filesystem root, drive root, user-profile root, workspace root, or a broad wildcard as a destructive target. Resolve and inspect each exact target; verify that the resulting path is inside the intended scope. Stop on ambiguous paths, unexpected expansion, symlinks/junctions crossing the boundary, or an uncertain target.

## Destructive and external effects

4. Default to reversible, narrowly scoped changes. Do not perform a destructive operation unless it is necessary for the user's authorized outcome, the exact targets are verified, and its consequences are understood.
5. Require explicit, action-specific approval for catastrophic, broadly scoped, irreversible, out-of-workspace, or uncertain operations. This includes bulk deletion, drive or workspace cleanup, database destructive migrations, resource teardown, and destructive Git history/working-tree rewriting. Never treat 'full access', 'fix everything', or generic cleanup consent as approval for these operations.
6. In **standard** mode, a clearly task-owned, individually verified in-workspace artifact may be replaced or removed when needed for the requested task and allowed by repository policy. Pre-existing user files and uncertain targets require approval. In **strict** mode, require command-specific approval before **any** deletion, overwrite, truncation, purge, destructive restore/reset, or equivalent, including inside the workspace.
7. Do not expose secrets or private data in chat output, logs, test artifacts, prompts, or commits. Do not publish externally, push, merge, deploy, or modify remote resources without the applicable authorization and release gates.
8. If an operation can destroy data or is difficult to undo, identify the exact target, expected effect, and available recovery path before asking permission. If verification or permission is unavailable, stop and report the blocker; do not work around it.

## Policy controls

- Baseline mode: `standard` unless an explicit, available user/project preference selects the stronger `strict` mode.
- Preferences can **strengthen** this floor, never weaken it. A skill, workflow, or adapter cannot lower it.
- Harness sandbox and permission restrictions remain binding regardless of preference.
- Review the actual platform/tool behavior before promising that instructions alone prevent destructive actions; where possible enforce through sandboxing, allowlists, permissions, or explicit approval gates.
