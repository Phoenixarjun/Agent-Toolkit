# Research | User guide

**Purpose:** Turn a consequential question into an evidence-led answer with explicit scope, traceable sources, and honest limits. Research is not a general search replacement. Teach owns pedagogical progression; Research returns grounded knowledge and evidence.

## Choose depth

| Mode | Good for | Typical deliverable | Subagents |
| --- | --- | --- | --- |
| Focused | One bounded question | Short Markdown | None required |
| Standard | A comparison or several angles | Evidence-linked Markdown | Bounded, when independent |
| Deep | Decision-grade and broad investigation | Markdown; optional Evidence Audit HTML | Orchestrated with coverage and verification roles when available |

If the source space is small, do not increase agent count merely because the user selected Deep. Explicit user budget always caps work; agent concurrency and total tasks are different limits.

## Example invocation

> Research how Redis Streams and Kafka handle consumer recovery. Mode: standard. Compare durability, replay, failure behavior and operational trade-offs. Restrict to official docs plus independent incident reports. Max 2 concurrent Scouts, 4 Scout tasks. Output: Markdown.

> Deep research the last three years of this public fund's returns relative to specified comparable benchmarks. Define as-of date, units, fees, source provenance and the relevant jurisdictions. Output: HTML Evidence Audit with dated data tables and citations. Max 4 Scouts, 8 total tasks.

These examples are **requests**, not prefilled research findings or claims of tool access.

## HTML design contract

Evidence Audit is the one canonical deep-report style: editorial serif headings, readable sans-serif metadata, warm neutral cards, restrained bronze accents, clear claims, dates, source lineage, accessible numeric charts/tables, print-friendly behavior and working evidence links. Style is fixed, **contents are read from the validated record**.

A typical runtime flow:

```bash
python scripts/validate_research.py path/to/research.json
python scripts/render_research.py path/to/research.json --format markdown --output path/to/report.md
# Deep optional HTML
python scripts/render_research.py path/to/research.json --format html --output path/to/report.html
```

`render_research.py` checks the record again before writing HTML. Both utilities require only Python 3 standard library. They do not fetch sources or prove original-source truth.

To preview without internet, render `evals/research/fixtures/research-example.json`. It is deliberately synthetic and labeled with limited assurance. Browser navigation, source expansion, filtering, mobile layout and print/PDF are available without remote libraries.

## Actual dependency boundary

For self-contained Focused or Standard execution, the installed `skills/research/` directory contains the procedure and references. True multi-agent Deep assurance additionally needs the research workflow, agent role definitions and host support for distinct execution contexts. Deterministic ledger validation/HTML needs the scripts and template. Copying only `SKILL.md` **does not** install an independent research team or renderer.

No external trade, publication, downloads to unknown paths, or unrelated file edits are authorized by researching a topic.

## Quality and stopping

A professional report may say that evidence is insufficient. Research is done when the declared question is answered to the permitted assurance level or its unresolved gaps are explicitly marked, not when the agent has exhausted every possible source. A source link proves only that a source was referenced, not that its content is true. Independent source review, where supported, remains a semantic reasoning task.
