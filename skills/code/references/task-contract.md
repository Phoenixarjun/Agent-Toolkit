# Scoped Implementation Contract

The Coordinator issues a contract **before** any delegated write. A worker may not redefine its acceptance target.

Required fields:

```yaml
task_id: CODE-001
intent_ref: INT-014@2
repository_revisions:
  app: <actual-sha-or-snapshot>
acceptance_ids: [AC-01]
prerequisites: []
allowed_write_paths:
  app: [src/feature/, tests/feature/]
reserved_shared_files: []
must_preserve: [INV-01]
forbidden:
  - unapproved contract changes
  - unrelated cleanup
completion_proof:
  - exact changed paths
  - acceptance behavior implemented
  - risk and unknowns
  - commands actually run
resources:
  allowed_test_environments: [local]
```

## Routing discipline

- One owner for each canonical write path, including generated files; do not allow overlapping directory patterns that could authorize the same file.
- A task may have multiple affected repositories only when each repository is explicitly authorized and separately snapshotted.
- Default serialized writes. Parallel independent worktrees require checked checkout roots, unique writable resources, an integration owner and explicit conflict-handling plan.
- Worker sends `DONE`, `BLOCKED`, or `NEEDS_DECISION`; the Coordinator must inspect changed paths and check results before marking a task accepted.
- Shared contracts and migrations are predecessor tasks; downstream Builders wait for their accepted versions.
- If task touches a path or responsibility outside scope, **stop**, describe the required change and ask Coordinator for amendment. Do not quietly expand `allowed_write_paths`.
- Existing dirty files are not fair game. Changes to these require an explicit integration/ownership decision preserving the user's baseline.

## Handoff

Report only observed facts:

```text
task_id
base revision and final candidate identity
changed files (including new/deleted/renamed)
acceptance IDs implemented
preserved constraints and supporting evidence
checks: exact command, environment, result, skips
new dependencies or side effects
uncertainties, conflicts, blocked follow-up
```

Never invent check output, working-directory state, or confidence percentages.
