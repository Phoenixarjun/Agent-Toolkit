# Goal-Directed Graph Tracing

Read only when nontrivial source navigation, dynamic resolution or cross-repository effects matter. This is a tracing *procedure*, not an exhaustive catalog of technologies.

1. Define the starting behavior, observable endpoints, state transitions and contracts from the goal. Identify the smallest likely entrypoints and relevant sinks.
2. Resolve edges by evidence: symbol definition/reference, interface implementation, injected binding, concrete route mapping, event producer/topic/schema/consumer, DB read/write, job schedule, build/deployment config, generated contract source, or authorized runtime trace.
3. For each edge, record its type, source locator, target locator, binding context, and whether it is OBSERVED, INFERRED, UNRESOLVED or CONTRADICTED. Direct source presence is not necessarily deployment reachability.
4. Follow both directions. A changed producer requires its consumers; a changed shared contract requires producers and consumers; a removed responsibility requires locating every active owner and fallthrough path.
5. Use a visited set keyed by repository snapshot + symbol + relevant runtime binding. Cycles do not justify infinite traversal. Stop at a stable contract when internal details cannot affect the change; record the boundary reason and version.
6. When runtime behavior may select implementations dynamically, inspect the actual binding configuration. If unreachable, record candidate implementations and the missing observation rather than choosing one.
7. For cross-repo boundaries, use the consumer's pinned revision and declared schema/version independently. A code link or repo name is not proof of deployed compatibility. Mark inaccessible repositories as BLOCKED, not covered.
8. Search for negative space: bypass routes, old clients, alternative workers, scheduled jobs, code generation, migrations, integration tests, environment toggles, and shared-state readers. Only examine those whose boundary might change the outcome.
9. When the plan depends on a third-party API, protocol, SDK, or managed-service behavior, establish the *deployed/declared version* and check the applicable authoritative specification, API reference or release/migration note where accessible. Record the source, version and applicability; current documentation for a newer release does not prove behavior in the pinned system. If documentation or runtime version cannot be checked, mark that contract premise unresolved; do not make a confident migration claim.
10. Exclude irrelevant modules deliberately. Record reason if non-obvious. Do not claim to have read an entire repository.

Source identity includes repo ID, snapshot, relative path and exact line range or uniquely locatable symbol. For non-code contracts use an equivalent stable locator and version. Whitespace-sensitive line ranges may change in dirty worktrees; record dirty state and the actual inspected working-tree version.
