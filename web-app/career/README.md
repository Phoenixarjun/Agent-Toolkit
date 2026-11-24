# Career — offline workspace viewer

A read-only companion for Agent Toolkit's `career` skill. Open `index.html` directly in a normal browser. No server, build, npm install, React, network dependency or account is required. All screens use one static HTML shell and hash navigation, with local CSS, JavaScript and data files. The bundled workspace is explicitly fictional sample data, not a candidate's actual work.

## Use with your own career workspace

1. Keep the canonical career records in an explicitly authorized private workspace, outside Agent Toolkit and any source repository. Ask the career coordinator to prepare a redacted display snapshot following `DATA-CONTRACT.md`.
2. Open the viewer, select **Open snapshot**, and choose that JSON file. The browser validates the snapshot, renders it locally and keeps it only in memory. Reloading resets to the default snapshot. No data is uploaded or written by the browser.
3. For a persistent default, copy the entire `web-app/career/` directory into your private workspace (for example `career-workspace/viewer/`). With Python 3.10+ and Node 18+ (only for the optional validated export helper), optionally run:

```bash
python viewer/scripts/export_snapshot.py career-view.json viewer
```

Run the command from the private workspace. This serializes an already prepared `mode: workspace` JSON snapshot into `viewer/data/workspace.js` using an atomic replacement. The helper validates the display contract before replacing the last export, and the viewer validates it again at load time. Refresh the browser after each authorized export. The helper does not read or alter the canonical plan, evidence, progress, or activity records; it does not automatically discover them.

Only use the exporter for a trusted private copy of the viewer. Do not publish `data/workspace.js` containing real information or manually write arbitrary JavaScript into it. The checked-in version is `null`. Use the JSON picker if an export helper is unavailable. The viewer does not watch files, execute agents, or schedule future work; its activity feed shows timestamped recorded events, not a live process status.

## Screens

Overview, Roadmap, Tasks, Projects, Presence, Content, Résumés, Opportunities, Companies, Applications, Interviews, Offers, Research and Activity. Detail views are opened from record and document links. Tables have text search and status/category filtering. Presence can contain multiple platform records. Content supports drafts, published posts, research and user-supplied publication statistics. The sample also includes a YouTube extension page, which demonstrates the declarative extension contract; it does not imply a bundled YouTube workflow.

The overview progress is the fraction of completed milestones in the displayed plan, not a candidate readiness score. Ready milestones require an approved plan, an elapsed start date, satisfied dependencies and no recorded blocker; conditional work also requires recorded trigger evidence. Recurring work appears separately in Overview and Tasks when the snapshot contains routines. Open milestones include scheduled and conditional work. Unknown information remains unknown. Timeline bars are derived from date ranges, not manually invented positions.

## Rendering components

The reusable component library is `scripts/components.js`. It provides DOM-safe metric groups, tables, status labels, progress indicators, panels, timelines, document rendering, record links and declarative block rendering. The agent normally extends data, not executable code. Additional pages can be declared in `extensions`, using text, list, metrics, table, document and quiz blocks. See `DATA-CONTRACT.md` for required shape, supported fields and constraints.

Markdown viewing supports headings, paragraphs, basic lists, fenced code and simple pipe tables. Raw HTML is literal text; inline formatting, Mermaid rendering, embedded media and PDF rendering are not implemented. Source links are separate explicit HTTP(S) links. Keep documents and their full-fidelity originals in the private workspace; the viewer stores only authorized text excerpts or copies. No arbitrary HTML or script execution is permitted in generated report data.

## Tests

No test tools are required to use the viewer. For development, Node 18+ and Python 3.10+ can run the dependency-free contract and export tests:

```bash
node --test tests/components.test.cjs
python -m unittest discover -s tests -p 'test_export.py' -v
```

Optional Chromium rendering tests use Python Playwright and a locally available Chromium executable. Run `python tests/browser_check.py`; this loads the same checked-in assets into an in-memory browser page to test rendering and interactions without a server. It does not exercise direct `file://` asset loading. Manually double-click `index.html` on the target machine as a release smoke check, since managed browser policies can restrict local pages.

Interview records can include interactive objective and written practice questions. Answers and self-check results are transient, not saved or sent; copy responses manually if you want an agent to evaluate them. No AI engine, exam security or automatic grading of written answers. Once opted in, the Career coordinator can export a refreshed snapshot after saved runs; the viewer still needs refresh/import. The browser itself does not execute agents.
