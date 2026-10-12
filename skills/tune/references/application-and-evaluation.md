# Application and Evaluation for Tune

Read when a proposed change affects installed routing, skill instructions, or measurable execution behavior.

## Selecting an owner

- Choose the **existing** preference owner for legitimate optional choices. If `ENGINEERING-PREFERENCES.md` exists, add or refine one scoped row; do not copy the same sentence into `AGENTS.md`, a profile, skill references and project policy.
- A preference must state the **choice**, its **scope**, and provenance. Do not repeat the full general procedure or reimplement a skill inside the preference file.
- Repository requirements, task acceptance criteria, explicit user constraints, global safety rules and skill-defining invariants can each be controlling in their respective domains. Do not silently solve a real conflict by assuming arbitrary document precedence.
- If instructions genuinely conflict, stop and identify both sources; the user cannot use personal tuning to weaken a non-negotiable capability or safety boundary.

## Overlay versus fork

**Overlay (default):** A user/project preference, consumed by the skill through actual installed context routing. Verify which entrypoint reads it and that the target capability honors the choice without skipping essential procedures. An inert file is not a successful tuning result.

**Isolated personal fork (exception):** Only when a user explicitly needs a changed procedure and a valid fork can preserve required safety and capability contracts. Use a distinct installed skill identity to prevent collision with the canonical name; pin source revision and copy necessary dependency closure into a permitted local install location. Do not commit user-specific changes upstream or overwrite the original skill. A folder outside the harness's discovered skill paths is not proof of activation.

If an exception cannot be implemented safely, keep the original skill and provide a proposal, or return `BLOCKED`.

## Baseline comparison

For the actual selected skill, reuse its eval suite where available and include at least:

- a **preference-fit** case that differentiates baseline and candidate;
- a **contract-protection** case (e.g., TDD retains essential verification; Security Audit remains independent and audit-only);
- a **counterexample** where blindly applying the preference would harm an otherwise valid outcome;
- a **routing** check to establish that the installed skill loads the applicable preference or fork.

Run baseline and candidate in comparable contexts with matching case inputs and available tools. Record which cases actually ran. Never claim that static checks prove runtime adoption. If the available harness cannot run behavior, mark `NOT_VERIFIED`.

## Rollback and failure

- Before any authorized file edit, preserve a verifiable baseline (Git diff/revision or an appropriately scoped backup); never make backups in unexpected directories.
- Detect prior uncommitted modifications and user-owned files before writing. Do not reset or clean to obtain a neat diff.
- If a preference update fails checks, do not activate it. If the change was applied, offer a minimal reversal limited to the exact approved change and obtain additional permission where the safety policy requires it.
- If a fork fails evaluation or cannot be discovered by the harness, leave it inactive and keep the original available.
- User approval of a proposal authorizes only the listed paths and effects, not wholesale edits to the repo or global agent installation.

## Evidence and reporting boundaries

Results must distinguish: `SYNTAX_VALID`, `DIFF_REVIEWED`, `EVALS_RUN`, `ACTIVATION_VERIFIED` and `NOT_VERIFIED`. A user can accept a preference-only edit with unverified behavior, but a procedural fork needs actual regression and activation checks before being presented as active.
