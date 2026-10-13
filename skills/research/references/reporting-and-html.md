# Output and Evidence Audit HTML

Load when publishing or rendering a report. **Same canonical ledger, multiple presentations.**

## Markdown

Lead with answer and as-of; give scope/coverage, material findings with adjacent source citations, what remains disputed, calculation methods and source list. No unsupported assertions in headlines. No fabricated sources. Use the result directly in Teach handoffs: Teach receives an evidence summary, not Scout transcripts.

## Deep HTML (optional)

Use a **single stable Evidence Audit aesthetic**: warm off-white canvas, ivory paper cards, restrained bronze accents, editorial serif headings, compact sans-serif data labels, consistent spacing, clear research status and evidence provenance. It is *not* an excuse to invent metrics. Reuse `templates/documents/RESEARCH-REPORT.html` through the canonical renderer when installed, rather than describing an imaginary page.

Layout order: masthead (title, as-of and status); left document navigation; executive answer and coverage; key finding cards each linked to claims/sources; data/visuals with method and accessible tables; claims and unresolved issues; evidence register with provenance; methodology, budgets and limitations. Citations must be close to claims, with working links where authorized.

Interactions: accessible section navigation, claim status filter, expandable evidence metadata, chart/source links, print stylesheet. No network-dependent scripts, tracking, inline external resources, autoplay, fabricated hover data or unsafe `innerHTML` from retrieved evidence. User-supplied strings are escaped. Links must not execute scripts. Keyboard users and small screens receive useful layout, and chart values are available in tables, not only color lines.

Only Deep mode may produce the HTML deliverable in v1, and it remains optional. If HTML is requested with Focused/Standard, offer an explicit choice: keep the mode and deliver Markdown, or switch to Deep with a disclosed budget (do not escalate silently). If the HTML renderer, template, or deterministic checks are missing, provide Markdown and report the rendering limitation.

The static HTML renderer validates the record before writing, and always labels example fixture data **synthetic**. The renderer cannot validate the truth of source quotations or observed values. Rendering/printing is not an assurance certification.
