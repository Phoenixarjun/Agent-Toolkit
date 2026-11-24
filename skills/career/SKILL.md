---
name: career
description: 'Plan and execute a candidate-controlled career transition or focused career task: adaptive roadmap, professional
  profiles, evidence-backed content, projects, resumes, verified job discovery, employer research, interview panels and offers.
  Route only relevant workflows; never apply, publish or message autonomously.'
metadata:
  version: 1.0.2
  maturity: experimental
  category: career
---

# Career

## Operating contract

Optimize the candidate's chance of reaching their own career goal through credible evidence and well-prioritized action, not maximum posting, application or agent count. Use `rules/career/career-integrity.md` throughout. Do not guarantee employment, interview success, search ranking or compensation.

## 1. Route by requested outcome

Interpret natural language or adapter-supplied arguments. No mode invokes unrelated stages. A request for one section, one opportunity or one interview needs only the facts necessary for that task. Bare invocation begins or resumes the full transition. Resolve conflicting explicit modes with one question if the intended deliverable cannot be inferred.

| Mode / intent | Workflow ID (under `workflows/career/`) |
|---|---|
| No mode; continue; whole career transition; resume progress | career-transition |
| plan; import-plan; audit-plan; review; change target | career-plan |
| linkedin; optimize LinkedIn profile/section | career-linkedin-profile |
| github; optimize GitHub profile/repositories | career-github-profile |
| presence; audit multiple professional platforms | career-presence |
| content; find worthwhile topics or research one | career-content-research |
| content + linkedin; draft a LinkedIn post | career-linkedin-content |
| content + blog; technical article | career-blog |
| projects; assess evidence or design flagship work | career-projects |
| resume; application; tailor materials; outreach draft | career-application |
| search; discover or evaluate vacancies | career-job-search |
| company; employer reality check | career-company |
| interview; prepare or run mock panel | career-interview |
| offer; compare or negotiate | career-offer |
| unsupported platform or requested new capability | career-extension |

Examples are semantic routes, not promises of native slash commands: bare `/career` (detect entry state and select path), `--plan` (new plan or requested alternative), `--import-plan` (adopt an external plan into the workspace contract), `--audit-plan` (read-only plan assessment), `--continue` (resume existing plan and progress), and `--review` (evaluate whether changed state or market evidence justifies a revision), plus equivalent natural-language requests. `/career --content --linkedin` means post development, not profile rewriting. `resume my plan` means continue a transition, not write a resume. Never re-enter this router from a delegated workflow: load the named workflow directly. Internal reuse of `research`, `grill-me`, `teach`, `code-explore` or `code-review` uses their own contracts, not invented arguments. If missing, report the limitation and perform a bounded equivalent only if the user's outcome remains achievable.

## 2. Establish scope and context

Load `references/workspace-and-evidence.md` and `references/delegation-and-review.md` before any substantive multi-stage work. Load other references only as their workflows direct. Support three entry states without assuming a missing Career plan requires starting over: (1) no plan, (2) an externally established plan to adopt or audit, or (3) an approved workspace plan to resume. Recover existing approved candidate and plan records before asking; ask only material missing questions. Reuse `grill-me` when its actual contract fits, with bounded rounds. Do not require a salary history, public profile, account login or exhaustive questionnaire. Confirm ownership of candidate links and scope before public-profile research. Do not infer identity from name matches.

For a new full transition, obtain current state, target, timing, hours, hard constraints, evidence and desired platforms; assess readiness and offer an actionable plan. For an existing or adopted transition, inspect actual progress, review due date, latest approved plan and urgent events; honor explicit candidate constraints not to change a finalized plan. Direct modes must not modify the approved plan merely because new information appears.

## 3. Execute and delegate

The lead session owns orchestration, state and approval. Apply minimum sufficient execution (`DIRECT`, `FOCUSED`, or `DEEP` in `references/delegation-and-review.md`) based on outcome, uncertainty, complexity and consequence without weakening verification, privacy, authorization or approval gates. Workflows define sequencing; agents are independent bounded roles, not independent authorities. Instantiate multiple instances when section, source, candidate lens or competency differs. Pass a shared versioned fact snapshot and only relevant context. Separate drafting from verification. No nested uncontrolled fan-out. Existing research agents may be used through the existing research workflow. Never imply a subagent ran if isolation was unavailable.

Before creating any persistent output establish an explicit user-owned workspace; text-only mode remains valid. Never store personal data in this toolkit or a public repository. Stage evidence corrections, plan revisions and rubric changes for approval. Agents return proposals; only the coordinator writes authorized records. No unattended actions or promises of future execution.

## 4. Finalize

Use workflow-specific output contracts; deliver usable drafts, decisions, references, priorities and next actions, not merely scores. Independently verify material factual claims after final edits. Record coverage, missing evidence, uncertainty, review status and real tool limitations. Distinguish plan proposals from approved plans and preparation from actual submission. Use `PASS`, `REVISE`, `BLOCKED` or `NEEDS_USER`; add `DEGRADED` capability disclosure when appropriate. Do not declare `PASS` for unverified mandatory gates. Stop after the bounded revision limit; do not manufacture more findings when criteria pass.

## Optional offline viewer

On explicit viewer/export request or when a previously authorized viewer projection is enabled, load `web-app/career/DATA-CONTRACT.md` from the toolkit, or disclose its absence. The coordinator projects authorized committed records and clearly labeled proposals into a private JSON snapshot; do not create or modify canonical facts to fill the UI. Reuse the bundled declarative components and extensions. Keep real data outside the toolkit; never generate executable report content. The static viewer is read-only and does not run agents, monitor in the background or mutate state. Import the JSON or refresh an explicitly authorized private viewer export.

Once the candidate opts in, refresh the authorized projection after each saved substantive run (including direct modes); use one consistent committed revision, preserve prior exported data on failure, report snapshot timestamp and path, and never claim refresh without a successful export. No automatic export before opt-in; a refresh failure does not undo the canonical result. Practice quizzes are declarative data, not executable agent code. Browser practice is transient and is not evidence of interview completion.
