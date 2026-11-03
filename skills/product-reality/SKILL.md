---
name: product-reality
description: Assess whether a proposed, evolving, or existing product delivers meaningful real-world value, why users would choose it over substitutes, and what would invalidate its future viability. Use for product thesis, differentiation, adoption, commercial viability, AI-wrapper exposure, or go/no-go evaluation; not code health, solution-space brainstorming, or implementation.
compatibility: Works without companion capabilities. For missing creator-owned decisions, Grill Me is optional. For material external claims, Research is optional when accessible. Fresh-context criticism requires actual context isolation; never imply it occurred without support.
metadata:
  version: "1.0.0"
  maturity: "experimental"
  category: "product-discovery"
---

# Product Reality

## Job and boundary

Answer: **Does this specific product deliver a meaningful outcome for its intended users, why would they choose it, and what could make that advantage disappear?** Recommend the smallest evidence-justified next decision, not the most elaborate product plan.

Assess an idea, feature, MVP, product, or changing competitive position. Establish its purpose before selecting evaluation lenses. Do not generate a solution catalog, build a business plan, invent user research, inspect code for technical health, implement changes, or label a product "AI slop" based on its use of AI. The output belongs to this skill even if another skill supplies questions or evidence.

A personal tool, open-source utility, internal product, and commercial venture have different success conditions. Never require revenue, a moat, or market size where the actual goal does not require them.

## Procedure

### 1. Anchor reality and the product thesis

Identify the product's current stage, intended users and beneficiaries, job/outcome, current substitute or workaround, value promise, actual success condition, constraints, and what is deployed versus merely proposed. Inspect supplied product artifacts and past evidence first. Distinguish `OBSERVED`, `RESEARCHED`, `INFERRED`, and `UNVALIDATED` statements. State the assessment's scope and as-of date.

Do not allow a feature description, slogan, AI model choice, or technological novelty to stand in for a user outcome. If the fundamental product or purpose cannot be established, return `NEEDS_CONTEXT` rather than fabricate a thesis.

### 2. Resolve only decision-changing unknowns

Discover available facts independently. Ask only for missing creator-owned information that could change the judgment: real customer observations, why users choose the product, success criteria, economics or launch constraints not publicly available. Default to **zero questions**; budget up to **eight total**, never a quota. Ask one decision question at a time; accept ranges and `unknown`.

Optionally invoke `grill-me` with the **remaining question budget** when several consequential user-owned assumptions need structured challenge. Its `DISCOVER`, `CLARIFY`, or `CHALLENGE` modes and bounded one-question-at-a-time procedure already cover product decisions. Prefer a bounded `$grill-me <N>` (optionally `hard` when pressure-testing an existing thesis); do not invoke its exhaustive mode by default. Incorporate its results, but do not delegate the product verdict or reset the budget. If unavailable, ask directly under the same limits.

When a missing answer would change the verdict and cannot be obtained, proceed conditionally or return `INSUFFICIENT_EVIDENCE` instead of interviewing indefinitely.

### 3. Investigate the real-world decision, proportionately

Use the six lenses as a **thinking sequence**, not six required report sections or agents:

1. **Reality:** What do users demonstrably do, need, avoid or use instead? What evidence exists beyond the founder's story?
2. **Purpose:** Who specifically benefits, from what outcome, how often, and by what success criterion?
3. **Structure:** Who discovers, adopts, uses, decides, pays, integrates, trusts and influences the product? Where does value move or get blocked?
4. **Leverage:** Which defensible benefit or smallest focused effort changes user outcomes most? Is the claimed difference valuable to customers, not merely novel?
5. **Consequences:** What if demand, pricing, access, AI providers or key assumptions change? How reversible is the investment?
6. **Evolution:** What observation, competitor change, experiment or threshold should trigger the next decision?

Use only applicable lenses in depth. Consider current workarounds, direct competitors, substitute workflows, general-purpose AI, incumbent feature absorption, adoption friction, customer trust, distribution, dependencies, and costs **when they affect the real decision**. Apply the substitution test from [evidence-and-substitution.md](references/evidence-and-substitution.md) when genericity, AI wrappers, or incumbent exposure are material.

Use readily accessible relevant evidence first. **Invoke `research` conditionally** only when an external claim or comparison is consequential, unresolved, and sufficiently complex to warrant its evidence-led procedure. Delegate an explicit bounded question, date window, source preference and appropriate `focused` or `standard` depth; use `deep` only for a user-authorized high-consequence decision that needs it. A simple current lookup does not need the full Research skill. Never claim current competitors, price, adoption or platform roadmaps were verified without actually checking. When research is unavailable, label external claims unverified and state how the decision is affected.

### 4. Attack the product thesis, then attack the complexity of the critique

Test, where relevant:

- **Problem proof:** Is the pain observed or only plausible?
- **Customer choice:** Why this product rather than doing nothing, the current workaround, an existing competitor or a general AI model?
- **Replication versus replacement:** Does easy code replication actually remove the user's reason to choose this product?
- **Platform absorption:** If an incumbent adds the headline feature, what value remains, if any? Treat this as a scenario, not a prediction.
- **Distinctiveness:** Is a claimed advantage meaningful, observed, and hard enough to substitute for the product's intended horizon? Distinctiveness is not mandatory for every product.
- **Economics:** Are cost, revenue, ROI, willingness to pay and margins measured, calculated from stated inputs, forecast, or unknown? Skip irrelevant commercial requirements.
- **Disconfirmation:** What cheapest credible observation could show the thesis is wrong?

Seek contrary evidence, not a forced negative verdict. A plain feature can be a good product; an elaborate AI application can be hollow. Do **not** infer market demand from LLM-generated personas, pretend a product's existence proves users prefer it, assume a new provider feature will certainly destroy a startup, or imply synthetic experiments are customer evidence.

After raising risks, perform a **proportionality pass**: discard recommendations whose added features, architecture, marketing or validation cost cannot plausibly change the product decision. The correct answer may be *keep building*, *test one assumption*, *change the audience*, or *do nothing for now*.

### 5. Optional fresh-context challenge

For materially costly, hard-to-reverse, or sharply disputed decisions, an actually isolated reviewer may receive only the product thesis, constraints, supporting evidence, preliminary judgment, and source locators. Ask: **"Which material conclusion could be wrong, and on what evidence or missing test?"** Require specific counterarguments, not a second generic market report. Reconcile each material objection against sources; do not let reviewer agreement substitute for customer evidence.

Never require a permanent agent roster or orchestration framework. If isolated delegation is unavailable or not justified, self-check and mark `independent_review: not_performed`. Do not claim fresh-context verification from a second prompt in the same context.

### 6. Deliver one decision-ready Product Reality Report

Use `templates/PRODUCT-REALITY-REPORT.md` if installed, or follow its headings: product thesis and success condition; evidence and substitutes; adoption/value and relevant economics; survival scenarios; verdict, what **not** to build, the smallest meaningful next experiment, and reassessment triggers. Cite material external claims close to the statement, with dates and source limitations. Distinguish what is known from what remains conditional.

Verdicts: `PROCEED`, `VALIDATE_FIRST`, `REPOSITION`, `PAUSE`, or `INSUFFICIENT_EVIDENCE`. `PAUSE` requires a positive reason supported by evidence; lack of evidence alone normally means `VALIDATE_FIRST` or `INSUFFICIENT_EVIDENCE`. No single numerical "AI-slop score", fake moat score, forced ROI, or guaranteed product survival.

Give at most **three** prioritized next actions. For each: why it matters, smallest possible proof, what success or failure would imply, and who needs to supply real-world evidence. Include explicit preservation/no-change decisions when appropriate. Stop when new investigation is unlikely to change the immediate product decision.

## Composition and stop rules

- `grill-me` owns optional adaptive questioning, not product analysis or report generation.
- `research` owns optional source-traceable external investigation, not product decisions or a mandatory research phase.
- `problem-to-solution` owns alternative solution mechanisms. Route there only when the problem or solution direction itself must be reopened; do not generate competing solutions here.
- `app-check` owns technical application health. `code-explore` owns code impact. `/code` owns implementation. No code edits, customer outreach, purchases, publishing, or production actions here.
- Missing tools, unauthenticated market facts, absent customers, or conflicting evidence must limit confidence, not trigger hallucinated verification.

Outcome: `DECISION_READY` when the scoped verdict and its basis are defensible, `LIMITED` when material evidence is missing but useful conditional judgment is possible, `NEEDS_CONTEXT` when product identity or purpose cannot be established, or `BLOCKED` when authorization or required evidence prevents meaningful work. These are **assessment assurance states**, not product verdicts.
