#!/usr/bin/env python3
"""Offline Evidence Audit HTML renderer, from a structurally validated research record.

Does not fetch, research, independently verify or certify claims.
"""
from __future__ import annotations
import argparse
import html
import json
import math
import sys
from pathlib import Path

from validate_research import check_record

HERE=Path(__file__).resolve()
TEMPLATE=HERE.parents[1]/'templates'/'documents'/'RESEARCH-REPORT.html'

def e(v): return html.escape(str(v),quote=True)

def tag_chip(text,klass=''): return f'<span class="chip {e(klass)}">{e(text)}</span>'

def render_lines(items):
    items=[str(x) for x in items if str(x).strip()]
    return '<ul class="bullets">'+''.join('<li>'+e(x)+'</li>' for x in items)+'</ul>' if items else '<p class="muted">None recorded.</p>'

def render_chart(chart,src_map):
    # One SVG drawn from *only* the actual numeric observations. Table repeats all points.
    series=chart['series']; xs=sorted(set(p['x'] for s in series for p in s['points']))
    ys=[p['y'] for s in series for p in s['points']]
    min_y,max_y=min(ys),max(ys);span=max(max_y-min_y,1)
    bottom=min_y-max(span*.15,abs(min_y)*.025);top=max_y+span*.2
    if len(ys)==1:bottom=min_y-1;top=max_y+1
    W,H,L,R,T,B=760,260,65,18,19,40
    def X(d):return L+(xs.index(d)/max(1,len(xs)-1))*(W-L-R)
    def Y(v):return T+(top-v)/max(.001,top-bottom)*(H-T-B)
    color=['#8a593b','#1f756a','#647b98','#c18b30','#875a84']
    svg=[f'<svg role="img" aria-label="{e(chart["title"])}. Numeric values are also available in the data table below." viewBox="0 0 {W} {H}">']
    for i in range(5):
        val=bottom+(top-bottom)*i/4;yy=Y(val)
        svg.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W-R}" y2="{yy:.1f}" stroke="#e8e1d9" stroke-dasharray="4 5"/>')
        svg.append(f'<text x="{L-12}" y="{yy+4:.1f}" font-size="11" text-anchor="end" fill="#6b726c">{e(f"{val:,.1f}")}</text>')
    for idx,d in enumerate(xs):
        if len(xs)>8 and idx not in {0,len(xs)//2,len(xs)-1}:continue
        svg.append(f'<text x="{X(d):.1f}" y="{H-14}" font-size="10.5" text-anchor="middle" fill="#76736b">{e(d[:7])}</text>')
    for i,s in enumerate(series):
        pts=' '.join(f'{X(p["x"]):.1f},{Y(p["y"]):.1f}' for p in s['points']);col=color[i%len(color)]
        svg.append(f'<polyline fill="none" stroke="{col}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="{pts}"/>')
        for p in s['points']:
            svg.append(f'<circle cx="{X(p["x"]):.1f}" cy="{Y(p["y"]):.1f}" r="3.5" fill="{col}" stroke="white" stroke-width="1"><title>{e(s["name"])}: {e(p["x"])} = {e(p["y"])} {e(chart["unit"])}</title></circle>')
    svg.append('</svg>')
    point_map={s['name']:{p['x']:p['y'] for p in s['points']} for s in series}
    headers='<th scope="col">Period</th>'+''.join(f'<th scope="col">{e(s["name"])} ({e(chart["unit"])})</th>' for s in series)
    rows=''.join('<tr><th scope="row">'+e(d)+'</th>'+''.join('<td>'+ (e(f'{point_map[s["name"]][d]:,.3f}'.rstrip('0').rstrip('.')) if d in point_map[s['name']] else 'No observation') + '</td>' for s in series)+'</tr>' for d in xs)
    legends=' '.join(f'<span><span class="swatch" style="background:{color[i%len(color)]}"></span>{e(s["name"])}</span>' for i,s in enumerate(series))
    source_ids=sorted(set(sid for s in series for sid in s['source_ids']))
    src_links=' '.join(f'<a href="#source-{e(sid)}">{e(sid)}</a>' for sid in source_ids)
    return f'''<article class="chart-card" id="{e(chart['id'])}"><h3>{e(chart['title'])}</h3><p class="chart-sub">Units: {e(chart['unit'])} · Method: {e(chart['method'])} · Sources: {src_links}</p><div class="chart-legend">{legends}</div>{''.join(svg)}<details><summary>View source observations as a table</summary><div style="overflow-x:auto"><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div></details><p class="chart-sub">{e(chart.get('note',''))}</p></article>'''

def render(record:dict, template:str)->str:
    research=record['research'];ex=record['execution'];questions=record['questions'];claims=record['claims'];sources=record['sources'];findings=record['findings'];charts=record['charts']
    src_index={s['id']:s for s in sources};cl_index={c['id']:c for c in claims}
    esc=e
    blocks=[]
    blocks.append('<div class="shell"><aside aria-label="Report navigation"><div class="side-label">Document sections</div><nav aria-label="Report sections">')
    nav=[('Overview','overview'),('Findings','findings'),('Charts','charts'),('Claims','claims'),('Evidence','sources'),('Method','method')]
    blocks.extend(f'<a href="#{ident}"><span>{i:02d}</span>{text}</a>' for i,(text,ident) in enumerate(nav,1))
    blocks.append('</nav><div class="side-info"><h4>Research record</h4>')
    blocks.append(f'<p>ID: {esc(research["id"])}</p><p>Mode: {esc(ex["mode"].title())}</p><p>As of: {esc(research["as_of"])}</p><p>Evidence: {len(sources)} sources</p><p>Report: {esc(research["outcome"])}</p></div></aside><main>')
    blocks.append(f'<header class="hero"><div class="eyebrow">Research dossier / evidence audit</div><h1>{esc(research["title"])}</h1><p class="subtitle">{esc(research["question"])}</p><div class="hero-meta">{tag_chip(research["outcome"],research["outcome"])}{tag_chip(ex["mode"]+" research")}<span>As of <strong>{esc(research["as_of"])}</strong></span><span>{len(sources)} source records</span><span>{len(claims)} claims</span></div></header>')
    if research['synthetic']:
        blocks.append('<div class="note" role="note" style="margin-top:20px"><strong>SYNTHETIC DEMO.</strong> Sources, observations, context IDs, and findings are illustrative fixtures, not factual external research or executed independent reviews.</div>')
    blocks.append('<section id="overview"><div class="eyebrow">01 / Brief</div><h2>Executive assessment</h2><p class="section-intro">Conclusions are limited to the declared scope and evidence status.</p>')
    blocks.append(f'<div class="report-card"><div class="statement">{esc(research["summary"])}</div><h3>What was investigated</h3>{render_lines(research["scope"]["included"])}<h3>Excluded from this assessment</h3>{render_lines(research["scope"]["excluded"])}')
    blocks.append('<div class="coverage">')
    answered=sum(q['status']=='answered' for q in questions)
    blocks.extend([f'<div class="metric"><strong>{answered} / {len(questions)}</strong><span>Questions answered</span></div>',f'<div class="metric"><strong>{len(sources)}</strong><span>Source records</span></div>',f'<div class="metric"><strong>{len(claims)}</strong><span>Claims tracked</span></div>'])
    blocks.append('</div></div></section>')
    blocks.append('<section id="findings"><div class="eyebrow">02 / Conclusions</div><h2>Key findings</h2><p class="section-intro">Each conclusion links back to its supporting claims.</p><div class="finding-grid">')
    for f in findings:
        links=''.join(f'<a class="pill-link" href="#claim-{esc(cid)}">{esc(cid)} ↗</a>' for cid in f['claim_ids'])
        blocks.append(f'<article class="finding"><span class="flag">{esc(f["category"])}</span><h3>{esc(f["title"])}</h3><p>{esc(f["body"])}</p>{links}</article>')
    if not findings:blocks.append('<div class="empty">No evidence-backed findings are available.</div>')
    blocks.append('</div></section>')
    blocks.append('<section id="charts"><div class="eyebrow">03 / Reproducible observations</div><h2>Data and comparisons</h2><p class="section-intro">Chart series use only supplied observations. Expand each chart to inspect its data.</p>')
    blocks.extend(render_chart(ch,src_index) for ch in charts)
    if not charts:blocks.append('<div class="empty">No supported quantitative series. No chart was generated.</div>')
    blocks.append('</section>')
    blocks.append('<section id="claims"><div class="eyebrow">04 / Claim ledger</div><h2>What the evidence supports</h2><div class="claims-bar"><p class="section-intro" style="margin:0">Source-linked claims, review states and caveats.</p><div class="filters"><label class="sr-only" for="claim-filter">Filter claims by status</label><select id="claim-filter" class="filter"><option value="all">All claims</option>'+''.join(f'<option value="{a}">{a.title()}</option>' for a in ('supported','qualified','disputed','unverified'))+'</select></div></div>')
    for c in claims:
        status=c['status'];refs=''.join(f'<button class="source-btn" type="button" data-source-id="{esc(sid)}" aria-label="Jump to source {esc(sid)}">{esc(sid)} ↗</button>' for sid in c['source_ids'])
        limit=' '.join(c.get('limitations',[])) or 'No additional limitation recorded.'
        blocks.append(f'<article class="claim" id="claim-{esc(c["id"])}" data-claim-status="{esc(status)}"><div class="claim-head"><span class="claim-id">{esc(c["id"])} / {esc(c["question_id"])}</span><span class="status status-{esc(status)}">{esc(status)}</span></div><p>{esc(c["text"])}</p><div>{refs}</div><div class="limitation"><strong>Verification:</strong> {esc(c["verification"]["method"])} · <strong>Limits:</strong> {esc(limit)}</div></article>')
    blocks.append('</section>')
    blocks.append('<section id="sources"><div class="eyebrow">05 / Provenance</div><h2>Evidence register</h2><p class="section-intro">Open a source to inspect its location, dated context, supporting excerpt and limitations.</p><div class="source-list">')
    for s in sources:
        url=s.get('url');link=f'<a href="{esc(url)}" rel="noopener noreferrer" target="_blank">Visit original source ↗</a>' if url else f'<span>{esc(s.get("local_locator","Private/local locator"))}</span>'
        blocks.append(f'<article class="source-row"><div class="source-num">{esc(s["id"])}</div><div><h3>{esc(s["title"])}</h3><p>{esc(s["publisher"])} · {esc(s["kind"])} · Accessed {esc(s["accessed_at"])} · Origin {esc(s["lineage_id"] )}</p><p>{link}</p><details id="source-{esc(s["id"])}" class="source-detail"><summary>View provenance and limitations</summary><p><strong>Exact locator:</strong> {esc(s["locator"])}</p><p><strong>Publication date:</strong> {esc(s.get("published_at") or "Not specified")} · <strong>Measurement period:</strong> {esc(s.get("measurement_period") or "Not specified")}</p><blockquote class="quote">{esc(s["excerpt"])}</blockquote><p><strong>Limits:</strong> {esc(s["limitations"])}</p></details></div></article>')
    blocks.append('</div></section>')
    blocks.append('<section id="method"><div class="eyebrow">06 / Accountability</div><h2>Methods, gaps and limits</h2><div class="report-card"><h3>Question coverage</h3><div style="overflow-x:auto"><table><thead><tr><th scope="col">Question</th><th scope="col">Status</th><th scope="col">Remaining gap</th></tr></thead><tbody>')
    for q in questions:blocks.append(f'<tr><th scope="row">{esc(q["id"])} · {esc(q["text"])}</th><td>{esc(q["status"])}</td><td>{esc(q.get("gap") or "None")}</td></tr>')
    blocks.append('</tbody></table></div><h3 style="margin-top:24px">Investigation metadata</h3>')
    b=ex['budget']
    blocks.append(f'<p class="muted">Execution: {esc(ex["mode"])} · Independent contexts: {esc(ex["independence"])} · Coverage critic executed: {"yes" if ex["coverage_reviewed"] else "no"}. Scout tasks: {b["scout_tasks_used"]}/{b["max_scout_tasks"]}. Tool calls: {b["tool_calls_used"]}/{b["max_tool_calls"]}.</p><h3>Limitations</h3>{render_lines(ex["limitations"])}')
    blocks.append('<p class="note"><strong>Assurance boundary:</strong> This file is a presentation of supplied records. Structural validation and chart display do not independently prove the authenticity, completeness or truth of upstream sources.</p></div></section>')
    blocks.append(f'<div class="footer">Generated as an offline Evidence Audit report · Record {esc(research["id"])} · As of {esc(research["as_of"])} · No remote scripts, analytics or external assets.</div></main></div>')
    page=template.replace('{{PAGE_TITLE}}',esc(research['title'])+' | Research Evidence Audit').replace('{{REPORT_BODY}}',''.join(blocks))
    return page

def render_markdown(record:dict)->str:
    """Portable text projection from the same ledger; no independent source verification."""
    def clean(value):
        import re
        text=' '.join(str(value).split())
        return re.sub(r'([\\`*_\[\]#|<>])',r'\\\1',text)
    r=record['research'];ex=record['execution'];lines=[
        '# '+clean(r['title']),'',
        '**Research question:** '+clean(r['question'])+'  ',
        '**As of:** '+clean(r['as_of'])+'  ',
        '**Mode:** '+clean(ex['mode'])+'  ',
        '**Outcome:** '+clean(r['outcome'])+'  ',
        '**Independent review:** '+clean(ex['independence']),'',
    ]
    if r['synthetic']:lines+=['> SYNTHETIC DEMO. The following data and sources are fictional, not externally verified.','']
    lines+=['## Answer','',clean(r['summary']),'','## Findings','']
    for f in record['findings']:
        ids=', '.join('['+clean(cid)+'](#claim-'+cid.lower()+')' for cid in f['claim_ids'])
        lines+=['- **'+clean(f['title'])+':** '+clean(f['body'])+' ('+ids+')']
    lines+=['','## Claim ledger','']
    src={s['id']:s for s in record['sources']}
    for c in record['claims']:
        source_ids=', '.join('['+clean(sid)+']('+src[sid]['url']+')' if src[sid].get('url') else clean(sid) for sid in c['source_ids'])
        lines+=['<a id="claim-'+c['id'].lower()+'"></a>', '### '+clean(c['id'])+' | '+clean(c['status']), '',clean(c['text']), '',
                '**Sources:** '+source_ids+'  ',
                '**Verification:** '+clean(c['verification']['method'])+'  ',
                '**Limitations:** '+clean('; '.join(c['limitations'])),'']
    lines+=['## Dated chart observations','']
    for ch in record['charts']:
        lines+=['### '+clean(ch['title']), '', '**Units:** '+clean(ch['unit'])+'  ',
                '**Method:** '+clean(ch['method']),'']
        all_dates=sorted(set(p['x'] for ser in ch['series'] for p in ser['points']))
        hdr=['Period']+[clean(x['name']) for x in ch['series']]
        lines+=['| '+' | '.join(hdr)+' |','| '+' | '.join('---' for _ in hdr)+' |']
        for date in all_dates:
            cells=[date]
            for ser in ch['series']:
                obs=next((pt['y'] for pt in ser['points'] if pt['x']==date),None)
                cells.append(str(obs) if obs is not None else 'No observation')
            lines+=['| '+' | '.join(cells)+' |']
        lines+=['',clean(ch.get('note','')),'']
    lines+=['## Question coverage','']
    for q in record['questions']:
        lines+=['- **'+clean(q['id'])+' ('+clean(q['status'])+'):** '+clean(q['text'])+ (' | Gap: '+clean(q.get('gap','')) if q.get('gap') else '')]
    lines+=['','## Source register','']
    for source in record['sources']:
        url=source.get('url')
        link='['+clean(source['title'])+']('+url+')' if url else clean(source['title'])
        lines+=['- **'+clean(source['id'])+':** '+link+' | '+clean(source['publisher'])+' | accessed '+clean(source['accessed_at'])+' | '+clean(source['locator'])+' | '+clean(source['limitations'])]
    lines+=['','## Methods and limitations','',
            'Budget: '+str(ex['budget']['scout_tasks_used'])+'/'+str(ex['budget']['max_scout_tasks'])+' Scout tasks, '
            +str(ex['budget']['tool_calls_used'])+'/'+str(ex['budget']['max_tool_calls'])+' tool calls.','']
    lines+=['- '+clean(lim) for lim in ex.get('limitations',[])]
    lines+=['','Structural validation is not source-truth verification or an agent execution attestation.','']
    return '\n'.join(lines)

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('record',type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--template',type=Path,default=TEMPLATE)
    p.add_argument('--format',choices=('html','markdown'),default='html')
    args=p.parse_args(argv)
    try:
        record=json.loads(args.record.read_text(encoding='utf-8'))
        errors=check_record(record)
        if errors:
            print('INVALID RESEARCH RECORD; HTML NOT WRITTEN',file=sys.stderr)
            for x in errors:print(' - '+x,file=sys.stderr)
            return 1
        if args.format=='html':
            template=args.template.read_text(encoding='utf-8')
            for tok in ('{{PAGE_TITLE}}','{{REPORT_BODY}}'):
                if tok not in template:raise ValueError('Template missing marker '+tok)
            page=render(record,template)
        else:
            page=render_markdown(record)
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(page,encoding='utf-8')
        print(f'Rendered {args.format.upper()} {args.output} from structurally valid ledger. External factual truth NOT verified.')
        return 0
    except (OSError,ValueError) as ex:
        print(f'RENDER FAILED: {ex}',file=sys.stderr)
        return 2
if __name__=='__main__':sys.exit(main())
