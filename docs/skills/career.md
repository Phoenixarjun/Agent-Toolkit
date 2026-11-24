# Career — v1.0.1 experimental

One entry skill, independent focused workflows, reusable role contracts, adaptive plan and candidate-controlled output. This is a feature overlay, not a career SaaS, always-on agent, or auto-apply tool.

## Invoke

Use natural language or the runtime's actual skill mechanism. Conceptual examples: `/career`, `/career --plan`, `/career --review` (review plan), `/career --linkedin`, `/career --github`, `/career --presence`, `/career --content`, `/career --content --linkedin`, `/career --content --blog`, `/career --projects`, `/career --resume`, `/career --search`, `/career --company`, `/career --interview`, `/career --offer`. Other channels route through capability extension. Arguments are conceptual; adapters must map them to actual supported syntax. Explicit requests override unrelated roadmap stages. Bare invocation resumes full transition; not an instruction to run every role in one call.

## State and planning

Choose a private user-owned workspace outside the toolkit/source repositories if persistence is desired. The skill works in text-only mode. Use the workspace/evidence and adaptive-planning references for records and review cadence. Never publish or submit automatically. Plans have durable foundations, role capabilities and adaptive work. Revisions are proposals until approved; track progress separately. The career coordinator checks overdue reviews upon invocation; recurring monitoring needs a separate authorized scheduler.

## Optional deterministic plan helper

Python 3.10+ standard library only; no network, API keys or dependency install. User creates the private workspace explicitly. Prepare a plan JSON using `skills/career/references/adaptive-planning.md` (see synthetic fixture in tests). For direct candidate work use null `workflow_id`, otherwise confirm actual registered workflow ID. The helper checks data structure, plan lineage, date/dependency ranges, rough capacity (uniform daily effort, conditional work reserves capacity), hashes and local locking. It cannot establish human approval, evidence validity, actual availability or protection from hostile concurrent local processes. Use a trusted local directory with appropriate OS access permissions; no promise of encryption or multi-user security.

```bash
python scripts/career/plan_store.py validate path/to/proposal.json
python scripts/career/plan_store.py stage path/to/private-workspace path/to/proposal.json
python scripts/career/plan_store.py status path/to/private-workspace
python scripts/career/plan_store.py activate path/to/private-workspace v1 path/to/approval.json
python -m unittest discover -s tests/career -v
```

`stage` writes proposal only. After explicit candidate approval of exact version/hash, prepare a record with `plan_id`, `plan_sha256` from validate/stage, `decision: APPROVE`, timezone-aware `approved_at` and `approval_reference` identifying actual decision. Do not invent that decision or run activation before approval. The helper preserves snapshots and refuses stale parent/changed IDs. If a writer crashes, inspect `.plan.lock` and workspace manually; remove a stale lock only after confirming no writer is active. Decisions can persist after an interrupted pointer update; retry the same approved record. Workload math is conservative; actual nonuniform weekly capacity may warrant manual assessment rather than bypassing structural checks. Human review still decides feasibility.

## Shared roles and extensions

Use lead coordinator and fresh role contexts where supported. Candidate-specific assignment includes scope, evidence version, task rubric and constraints. No permanent agent per section/platform. Full LinkedIn optimization can fan out by section; mock interviews can instantiate 2–4 competency lenses. Existing research skills and agents are reused, not redefined. Platform-specific procedures have distinct workflow files. The extension resolver creates only bounded run-local compositions; new permanent toolkit artifacts require separate maintainership approval and evaluation.

## Validation and limits

Behavioral expectations are under `evals/career/`; deterministic local helper tests under `tests/career/`. Actual agent performance, supported runtime subagent isolation, web sources, exports and repository-wide integration require live verification. Missing browser, scheduling, scraping or image tools do not imply capability. No bundled scraping service, auto-publisher, form submitter, data backend or GitHub automation. Existing optional skill contracts must be checked before using them; no assumption about proprietary runtime commands.

## Optional static workspace viewer

Open `web-app/career/index.html` locally to explore the clearly labeled demo. The viewer uses plain HTML, CSS and JavaScript; no server or dependencies. For real records, explicitly authorize a private JSON projection using `web-app/career/DATA-CONTRACT.md`, then import it or export into a private copy using the optional serializer. Refer to `web-app/career/README.md` for setup, limitations and checks. This is a read-only view of recorded events and documents; it does not change canonical files or run agents.

For recurring career work, preserve approved cadence and occurrence history in `strategy/routines.json`; due scheduled work becomes ready on invocation, and conditional work requires evidence of its trigger. An opted-in viewer projection refreshes after saved runs. Interview preparation can return a verified self-practice quiz for the offline viewer; actual mocks remain interactive in the agent and are never marked completed from a generated quiz.
