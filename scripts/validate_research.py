#!/usr/bin/env python3
"""Structural consistency checks for Agent Toolkit Research ledger v1.

This is NOT source-truth verification or an independent-agent attestation.
Exit 0 means that data relationships and report-generation prerequisites passed.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

ID_PATTERNS = {"questions": r"Q-\d{3,}", "sources": r"S-\d{3,}", "claims": r"C-\d{3,}", "findings": r"F-\d{3,}", "charts": r"CH-\d{3,}"}
STATUSES = {"supported", "qualified", "disputed", "unverified"}
QSTATUSES = {"answered", "partial", "unanswered"}
OUTCOMES = {"complete", "partial", "blocked"}


def check_record(record: dict) -> list[str]:
    errors: list[str] = []
    def err(path: str, message: str):
        errors.append(f"{path}: {message}")
    def require_dict(obj, path):
        if not isinstance(obj, dict):
            err(path, "expected object")
            return {}
        return obj
    def required_str(obj, field, path):
        val = obj.get(field)
        if not isinstance(val, str) or not val.strip():
            err(f"{path}.{field}", "required non-empty string")
            return ""
        return val
    def date_field(obj, field, path, mandatory=False):
        s = obj.get(field)
        if s is None or s == "":
            if mandatory: err(f"{path}.{field}", "date required")
            return None
        try:
            if not isinstance(s, str): raise ValueError()
            return dt.date.fromisoformat(s)
        except ValueError:
            err(f"{path}.{field}", "must be ISO YYYY-MM-DD")
            return None
    if not isinstance(record, dict):
        return ["root: expected JSON object"]
    if record.get("schema_version") != "1.0.0": err("schema_version", "unsupported version; expected 1.0.0")
    research = require_dict(record.get("research"), "research")
    execution = require_dict(record.get("execution"), "execution")
    for field in ("id", "title", "question", "summary"): required_str(research,field,"research")
    as_of = date_field(research,"as_of","research",True)
    outcome = research.get("outcome")
    if outcome not in OUTCOMES: err("research.outcome", "invalid outcome")
    if not isinstance(research.get("synthetic"),bool): err("research.synthetic","must explicitly be true or false")
    scope = require_dict(research.get("scope"), "research.scope")
    for k in ("included","excluded"):
        if not isinstance(scope.get(k),list) or any(not isinstance(x,str) or not x for x in scope.get(k, [])):
            err(f"research.scope.{k}","expected list of text entries")
    mode = execution.get("mode")
    if mode not in ("focused","standard","deep"): err("execution.mode","invalid mode")
    independence = execution.get("independence")
    if independence not in ("independent","unavailable"): err("execution.independence","invalid state")
    scouts = execution.get("scout_contexts")
    if not isinstance(scouts,list) or any(not isinstance(x,str) or not x.strip() for x in scouts):
        err("execution.scout_contexts","expected list of actual context IDs")
        scouts=[]
    critic = execution.get("critic_context")
    verifier = execution.get("verifier_context")
    for k, val in (("critic_context",critic),("verifier_context",verifier)):
        if val is not None and (not isinstance(val,str) or not val.strip()):err(f"execution.{k}","expected nonempty context ID or null")
    if len(set([*scouts,*([critic] if isinstance(critic,str) else []),*([verifier] if isinstance(verifier,str) else [])])) != (len(scouts)+int(isinstance(critic,str))+int(isinstance(verifier,str))):
        err("execution", "role contexts must be unique (cannot manufacture independence through shared context)")
    if not isinstance(execution.get("coverage_reviewed"),bool):err("execution.coverage_reviewed","must be boolean")
    budget = require_dict(execution.get("budget"),"execution.budget")
    for maxk,usedk in (("max_scout_tasks","scout_tasks_used"),("max_tool_calls","tool_calls_used")):
        a,b=budget.get(maxk),budget.get(usedk)
        if type(a)!=int or a<0 or type(b)!=int or b<0 or b>a:
            err(f"execution.budget.{usedk}",f"expected integer 0 <= consumed <= {maxk}")
    mc=budget.get("max_concurrent_scouts")
    if type(mc)!=int or mc<0:err("execution.budget.max_concurrent_scouts","must be nonnegative int")
    if len(scouts)>budget.get('scout_tasks_used',-1) and not research.get('synthetic'):
        err("execution.scout_contexts","context count cannot exceed reported dispatched Scout tasks")
    if not isinstance(execution.get("limitations"),list) or any(not isinstance(x,str) for x in execution.get("limitations",[])):
        err("execution.limitations","expected list of strings")

    tables={}
    for table, pattern in ID_PATTERNS.items():
        rows=record.get(table)
        if not isinstance(rows,list):err(table,"required array");rows=[]
        index={}
        for idx,row in enumerate(rows):
            p=f"{table}[{idx}]"
            if not isinstance(row,dict):err(p,"expected object");continue
            id_=row.get("id")
            if not isinstance(id_,str) or not re.fullmatch(pattern,id_):err(p+".id",f"invalid {table} ID");continue
            if id_ in index:err(p+".id","duplicate ID")
            index[id_]=row
        tables[table]=index
    qs,ss,cs,fs,chs=(tables[k] for k in ID_PATTERNS)
    for qid,q in qs.items():
        p=f"questions.{qid}"
        required_str(q,'text',p)
        if q.get('status') not in QSTATUSES:err(p+'.status','invalid state')
        ids=q.get('claim_ids')
        if not isinstance(ids,list):err(p+'.claim_ids','must be list');ids=[]
        if len(ids)!=len(set(map(str,ids))):err(p+'.claim_ids','duplicate claim reference')
        for cid in ids:
            if cid not in cs:err(p+'.claim_ids',f'unknown claim {cid}')
            elif cs[cid].get('question_id')!=qid:err(p+'.claim_ids',f'claim {cid} belongs to other question')
        if q.get('status')=='answered' and not ids:err(p+'.claim_ids','answered requires supporting claim')
        if q.get('status')!='answered' and not isinstance(q.get('gap'),str):err(p+'.gap','unanswered or partial requires gap')
    for sid,s in ss.items():
        p=f'sources.{sid}'
        for f in ('title','publisher','kind','lineage_id','locator','excerpt'):required_str(s,f,p)
        url=s.get('url')
        if url is not None:
            if not isinstance(url,str):err(p+'.url','URL must be string')
            else:
                parsed=urlsplit(url)
                if parsed.scheme not in ('https','http') or not parsed.netloc or parsed.username or parsed.password:
                    err(p+'.url','external URL must be HTTP(S) without embedded credentials')
        if not url and not isinstance(s.get('local_locator'),str):err(p,'source must have URL or local_locator')
        pub=date_field(s,'published_at',p)
        access=date_field(s,'accessed_at',p, True)
        if as_of and access and access>as_of:err(p+'.accessed_at','access cannot postdate report as_of')
        if pub and access and pub>access:err(p+'.published_at','publication cannot postdate access')
        if 'limitations' not in s or not isinstance(s['limitations'],str):err(p+'.limitations','required string, empty allowed')
    for cid,c in cs.items():
        p=f'claims.{cid}'
        required_str(c,'text',p)
        qid=c.get('question_id')
        if qid not in qs:err(p+'.question_id','unknown question')
        elif cid not in qs[qid].get('claim_ids',[]):err(p+'.question_id','missing reciprocal question reference')
        status=c.get('status')
        if status not in STATUSES:err(p+'.status','invalid status')
        ids=c.get('source_ids')
        if not isinstance(ids,list):err(p+'.source_ids','expected list');ids=[]
        if status in ('supported','qualified') and not ids:err(p+'.source_ids','supported/qualified requires evidence')
        for sid in ids:
            if sid not in ss:err(p+'.source_ids',f'unknown source {sid}')
        if not isinstance(c.get('material'),bool):err(p+'.material','boolean required')
        lim=c.get('limitations')
        if not isinstance(lim,list) or any(not isinstance(x,str) for x in lim):err(p+'.limitations','expected string list');lim=[]
        if status in ('qualified','disputed','unverified') and not any(x.strip() for x in lim):
            err(p+'.limitations','uncertainty requires explicit limitation')
        ver=require_dict(c.get('verification'),p+'.verification')
        required_str(ver,'method',p+'.verification')
        rv=ver.get('reviewer_context')
        sc=c.get('scout_context')
        if rv is not None and (not isinstance(rv,str) or not rv.strip()):err(p+'.verification.reviewer_context','nonempty context ID or null')
        if sc is not None and (not isinstance(sc,str) or not sc.strip()):err(p+'.scout_context','nonempty context ID or null')
        if rv and sc and rv==sc:err(p+'.verification.reviewer_context','must differ from discoverer context')
        if mode=='deep' and outcome=='complete' and c.get('material'):
            if not rv or rv!=verifier:err(p+'.verification.reviewer_context','deep complete requires independent verifier role')
            if not sc or sc not in scouts:err(p+'.scout_context','deep complete requires actual Scout context')
    for fid,f in fs.items():
        p=f'findings.{fid}'
        for k in ('title','body','category'):required_str(f,k,p)
        refs=f.get('claim_ids')
        if not isinstance(refs,list) or not refs:err(p+'.claim_ids','finding needs one or more claim IDs');refs=[]
        for cid in refs:
            if cid not in cs:err(p+'.claim_ids',f'unknown claim {cid}')
        if outcome=='complete' and any(cs[cid].get('status') in ('disputed','unverified') for cid in refs if cid in cs):
            err(p+'.claim_ids','complete finding cannot rely on unverified or disputed claim')
    for chid,ch in chs.items():
        p=f'charts.{chid}'
        for k in ('title','unit','method'):required_str(ch,k,p)
        series=ch.get('series')
        if not isinstance(series,list) or not series:err(p+'.series','expected one or more series');series=[]
        for i,s in enumerate(series):
            sp=f'{p}.series[{i}]'
            required_str(s,'name',sp)
            source_ids=s.get('source_ids')
            if not isinstance(source_ids,list) or not source_ids:err(sp+'.source_ids','chart series requires source IDs');source_ids=[]
            for sid in source_ids:
                if sid not in ss:err(sp+'.source_ids',f'unknown source {sid}')
            points=s.get('points')
            if not isinstance(points,list) or not points:err(sp+'.points','requires observation points');points=[]
            prev=None
            for j,pt in enumerate(points):
                pp=f'{sp}.points[{j}]'
                if not isinstance(pt,dict):err(pp,'not an object');continue
                d=date_field(pt,'x',pp,True)
                y=pt.get('y')
                if type(y) not in (int,float) or not math.isfinite(y):err(pp+'.y','must be finite numeric observation')
                if d and prev and d<=prev:err(pp+'.x','series must have strictly increasing unique dates')
                if d:prev=d
                if as_of and d and d>as_of:err(pp+'.x','future observation relative to as_of')
    # Optional numeric assertions bind narrative changes to the exact chart observations.
    # This checks internal arithmetic, not source authenticity.
    for cid,c in cs.items():
        assertion=c.get('numeric_assertion')
        if assertion is None:continue
        p=f'claims.{cid}.numeric_assertion'
        if not isinstance(assertion,dict):err(p,'expected object');continue
        ch=chs.get(assertion.get('chart_id'))
        if ch is None:err(p+'.chart_id','unknown chart');continue
        chosen=[s for s in ch.get('series',[]) if s.get('name')==assertion.get('series_name')]
        if len(chosen)!=1:err(p+'.series_name','must identify exactly one chart series');continue
        pts=chosen[0].get('points',[])
        if not pts:err(p,'chart series has no observations');continue
        if not set(chosen[0].get('source_ids',[])).intersection(set(c.get('source_ids',[]))):
            err(p,'claim and chart series must share at least one evidence source')
        try:
            first,last,delta=(assertion[k] for k in ('first','last','delta'))
            if any(type(v) not in (int,float) or not math.isfinite(v) for v in (first,last,delta)):
                raise ValueError('numbers required')
            if not (math.isclose(first,pts[0]['y'],rel_tol=1e-10,abs_tol=1e-8)
                    and math.isclose(last,pts[-1]['y'],rel_tol=1e-10,abs_tol=1e-8)
                    and math.isclose(delta,last-first,rel_tol=1e-10,abs_tol=1e-8)):
                err(p,'first/last/delta do not match chart observations')
        except (KeyError,TypeError,ValueError):
            err(p,'require finite numeric first, last and delta')

    if mode=='deep' and outcome=='complete':
        if independence!='independent' or not scouts or not critic or not verifier or not execution.get('coverage_reviewed'):
            err('execution','deep complete requires actual independent Scouts, Critic and Verifier plus coverage review')
        if any(q.get('status')!='answered' for q in qs.values()):err('questions','deep complete requires answered mandatory questions')
    if outcome=='complete' and any(q.get('status')!='answered' for q in qs.values()):
        err('research.outcome','complete cannot contain partial/unanswered required questions')
    if outcome=='complete' and any(c.get('status') in ('disputed','unverified') and c.get('material') for c in cs.values()):
        err('research.outcome','complete cannot leave material disputed/unverified claims')
    if research.get('synthetic') and outcome=='complete':
        err('research.outcome','synthetic fixtures cannot assert complete research assurance')
    return errors


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('record',type=Path)
    args=ap.parse_args(argv)
    try:
        r=json.loads(args.record.read_text(encoding='utf-8'))
    except (OSError,ValueError) as e:
        print(f'INVALID: could not load JSON: {e}',file=sys.stderr);return 2
    errors=check_record(r)
    if errors:
        print(f'INVALID: {len(errors)} issue(s)',file=sys.stderr)
        for e in errors:print(' - '+e,file=sys.stderr)
        return 1
    print('STRUCTURALLY VALID (not a fact-check, source verification, or agent execution attestation)')
    return 0
if __name__=='__main__':sys.exit(main())
