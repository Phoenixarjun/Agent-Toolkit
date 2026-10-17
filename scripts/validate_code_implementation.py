#!/usr/bin/env python3
"""Validate the structure and internal consistency of /code implementation evidence.

This is not an attestation that code runs or checks were really executed.
Usage: python scripts/validate_code_implementation.py path/to/ledger.json
"""
import argparse
import json
import posixpath
import sys
from pathlib import Path

EVENTS = ("BUILD_COMPLETED", "TDD_ASSIST_STARTED", "FINAL_CANDIDATE_SELECTED", "INDEPENDENT_VERIFICATION_COMPLETED")
OUTCOMES = {"VERIFIED", "IMPLEMENTED_UNVERIFIED", "FAILED_VERIFICATION", "BLOCKED", "NEEDS_DECISION"}
STATES = {"PASS", "FAIL", "BLOCKED", "UNKNOWN"}


def valid_path(value):
    return (isinstance(value, str) and value and "\\" not in value and not value.startswith("/")
            and not value.startswith("~") and not value.startswith("./") and
            all(p not in {"", ".", ".."} for p in value.rstrip("/").split("/")) and
            posixpath.normpath(value.rstrip("/")) == value.rstrip("/"))


def in_scope(path, allowed):
    return any(path == a or (a.endswith("/") and path.startswith(a)) for a in allowed)


def validate(doc):
    errors = []

    def fail(reason):
        errors.append(reason)

    if not isinstance(doc, dict):
        return ["Ledger must be a JSON object"]
    if doc.get("schema_version") != "1.0":
        fail("schema_version must be '1.0'")
    intent = doc.get("intent", {})
    if not isinstance(intent, dict):
        intent = {}
    ac = intent.get("acceptance_ids", [])
    inv = intent.get("preservation_ids", [])
    if not isinstance(intent.get("id"), str) or not intent.get("id") or not str(intent.get("revision", "")):
        fail("intent id and revision required")
    if not isinstance(ac, list) or not ac or not all(isinstance(x, str) and x for x in ac):
        fail("at least one acceptance ID required")
        ac = []
    if not isinstance(inv, list) or not all(isinstance(x, str) and x for x in inv):
        fail("preservation_ids must be an array of IDs")
        inv = []
    if len(set(ac + inv)) != len(ac + inv):
        fail("acceptance and preservation IDs must be unique")

    baseline = doc.get("baseline", {})
    repos = baseline.get("repositories", []) if isinstance(baseline, dict) else []
    if not isinstance(repos, list) or not repos:
        fail("baseline.repositories must be nonempty")
        repos = []
    known_repo, dirty = set(), set()
    for r in repos:
        if not isinstance(r, dict):
            fail("invalid repository entry"); continue
        rid = r.get("id")
        if not isinstance(rid, str) or not rid or rid in known_repo or not str(r.get("revision", "")):
            fail("repository id must be unique and revision recorded")
        known_repo.add(rid)
        for p in r.get("dirty_paths", []):
            if not valid_path(p): fail(f"unsafe baseline dirty path: {p!r}")
            dirty.add((rid, p))

    tasks = doc.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        fail("at least one task required"); tasks = []
    ids, builder_contexts, owner, task_deps = set(), set(), {}, {}
    candidate_paths = set()
    for t in tasks:
        if not isinstance(t, dict):
            fail("invalid task entry"); continue
        tid, rid, b = t.get("id"), t.get("repository"), t.get("builder_context")
        if not tid or tid in ids: fail(f"duplicate/missing task ID: {tid!r}")
        ids.add(tid)
        if rid not in known_repo: fail(f"task {tid}: unknown repository {rid!r}")
        if not isinstance(b, str) or not b: fail(f"task {tid}: missing builder context")
        else: builder_contexts.add(b)
        if t.get("status") != "DONE":
            if doc.get("outcome") == "VERIFIED": fail(f"task {tid}: non-DONE task for VERIFIED result")
        allowed = t.get("allowed_paths", [])
        paths = t.get("changed_paths", [])
        if not isinstance(allowed, list) or not isinstance(paths, list):
            fail(f"task {tid}: invalid paths"); continue
        for p in allowed:
            if not valid_path(p): fail(f"task {tid}: unsafe allowed path: {p!r}")
        for p in paths:
            if not valid_path(p):
                fail(f"task {tid}: unsafe changed path: {p!r}"); continue
            if not in_scope(p, allowed): fail(f"task {tid}: changed path outside write scope: {p}")
            pair = (rid, p)
            if pair in owner: fail(f"overlapping writers: {p} ({owner[pair]} and {tid})")
            owner[pair] = tid
            candidate_paths.add(pair)
        if not set(t.get("acceptance_ids", [])).issubset(set(ac)):
            fail(f"task {tid}: unknown acceptance ID")
        task_deps[tid] = t.get("depends_on", [])
    for tid, dep in task_deps.items():
        if not isinstance(dep, list): fail(f"task {tid}: depends_on must be array"); continue
        if any(d not in ids or d == tid for d in dep): fail(f"task {tid}: invalid prerequisite")
    visited, visiting = set(), set()
    def walk(tid):
        if tid in visiting:
            fail(f"task dependency cycle at {tid}"); return
        if tid in visited: return
        visiting.add(tid)
        for d in task_deps.get(tid, []):
            if d in task_deps and d not in visited: walk(d)
        visiting.discard(tid)
        visited.add(tid)
    for tid in ids: walk(tid)

    candidate = doc.get("candidate", {})
    cid = candidate.get("id") if isinstance(candidate, dict) else None
    if not isinstance(cid, str) or not cid: fail("candidate.id required")
    claimed_paths = set()
    for entry in candidate.get("paths", []) if isinstance(candidate, dict) else []:
        if not isinstance(entry, dict): fail("invalid candidate path entry"); continue
        pair = (entry.get("repository"), entry.get("path"))
        if pair[0] not in known_repo or not valid_path(pair[1]): fail(f"invalid candidate path: {pair!r}")
        claimed_paths.add(pair)
    if candidate_paths != claimed_paths:
        fail("candidate paths must exactly match task changed paths")
    approvals = set()
    for entry in doc.get("dirty_path_approvals", []):
        if not isinstance(entry, dict) or not str(entry.get("approval_ref", "")).strip():
            fail("dirty-path approval requires an explicit approval_ref"); continue
        approvals.add((entry.get("repository"), entry.get("path")))
    for p in claimed_paths & dirty:
        if p not in approvals: fail(f"changed pre-existing dirty path without explicit approval: {p}")

    events = doc.get("events", [])
    event_seq = {}
    if not isinstance(events, list):
        fail("events must be an array"); events = []
    numbers = []
    for evt in events:
        if not isinstance(evt, dict): fail("invalid event"); continue
        seq, typ = evt.get("seq"), evt.get("type")
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < 1:
            fail("event seq must be positive integer"); continue
        numbers.append(seq)
        if typ not in EVENTS: fail(f"unknown event type {typ!r}")
        if typ in event_seq: fail(f"duplicate event {typ}")
        event_seq[typ] = seq
    if numbers != sorted(set(numbers)):
        fail("event seq must be strictly increasing")
    for typ in ("BUILD_COMPLETED", "FINAL_CANDIDATE_SELECTED"):
        if typ not in event_seq: fail(f"missing event {typ}")
    if event_seq.get("BUILD_COMPLETED", 0) >= event_seq.get("FINAL_CANDIDATE_SELECTED", 10**10):
        fail("final candidate must follow completed implementation")
    if "INDEPENDENT_VERIFICATION_COMPLETED" in event_seq and event_seq["INDEPENDENT_VERIFICATION_COMPLETED"] <= event_seq.get("FINAL_CANDIDATE_SELECTED", 0):
        fail("independent verification must follow final candidate")

    assist = doc.get("post_build_testing", {})
    if not isinstance(assist, dict): assist = {}
    decision = assist.get("decision")
    if decision not in {"USED", "NOT_APPLICABLE", "BLOCKED"} or not str(assist.get("reason", "")).strip():
        fail("post_build_testing requires decision and reason")
    if decision == "USED":
        if assist.get("mode") != "post_implementation": fail("TDD-assisted checks must be labeled post_implementation")
        if "TDD_ASSIST_STARTED" not in event_seq: fail("USED requires TDD_ASSIST_STARTED event")
        elif event_seq["TDD_ASSIST_STARTED"] <= event_seq.get("BUILD_COMPLETED", 10**10):
            fail("TDD assistance cannot start before implementation completed")
    elif "TDD_ASSIST_STARTED" in event_seq:
        fail("TDD_ASSIST_STARTED conflicts with unused TDD assistance")

    checks = doc.get("checks", [])
    if not isinstance(checks, list): checks = []
    checks_by_id = {}
    for check in checks:
        if not isinstance(check, dict): fail("invalid check"); continue
        chkid = check.get("id")
        if not chkid or chkid in checks_by_id: fail(f"duplicate/missing check ID {chkid!r}")
        checks_by_id[chkid] = check
        if check.get("candidate_id") != cid: fail(f"check {chkid}: stale candidate evidence")
        if check.get("status") not in STATES: fail(f"check {chkid}: invalid status")
        if not str(check.get("runner_context", "")).strip() or not str(check.get("evidence", "")).strip():
            fail(f"check {chkid}: actual runner and evidence required")

    verifier = doc.get("verification", {})
    if not isinstance(verifier, dict): verifier = {}
    vctx = verifier.get("context")
    if not vctx or vctx in builder_contexts:
        fail("verifier must have a distinct real context from every builder")
    if verifier.get("candidate_id") != cid: fail("verifier evaluated stale candidate")
    if verifier.get("status") not in {"PASS", "FAIL", "BLOCKED"}: fail("verification.status invalid")

    if decision == "USED" and not any(
        c.get("status") == "PASS" and c.get("runner_context") == vctx and
        c.get("kind") in {"behavior_test", "runtime", "integration", "unit", "adversarial"}
        for c in checks_by_id.values()
    ):
        fail("USED TDD-assisted verification requires independent successful behavior/runtime check")

    evidence = doc.get("requirements", [])
    req_ids = set(ac + inv)
    recorded = {}
    if not isinstance(evidence, list): evidence = []
    for item in evidence:
        if not isinstance(item, dict): fail("invalid requirement evidence"); continue
        eid = item.get("id")
        if eid in recorded: fail(f"duplicate requirement evidence {eid}")
        recorded[eid] = item
        if eid not in req_ids: fail(f"unexpected requirement ID {eid}")
        if item.get("status") not in STATES: fail(f"requirement {eid}: invalid status")
        refs = item.get("check_ids", [])
        if not isinstance(refs, list) or not refs: fail(f"requirement {eid}: no check evidence"); continue
        for ref in refs:
            if ref not in checks_by_id: fail(f"requirement {eid}: missing check {ref}")
        if item.get("status") == "PASS":
            if not any(checks_by_id.get(ref, {}).get("status") == "PASS" and checks_by_id.get(ref, {}).get("runner_context") == vctx for ref in refs):
                fail(f"requirement {eid}: PASS requires independent verifier's passing check")
    if set(recorded) != req_ids: fail("all acceptance/preservation IDs require explicit evidence entries")

    review = doc.get("review", {})
    if not isinstance(review, dict): review = {}
    if review.get("candidate_id") != cid: fail("review bound to stale candidate")
    if review.get("status") not in {"PASS", "FAIL", "BLOCKED"}: fail("review.status invalid")
    if review.get("status") == "PASS" and not str(review.get("evidence", "")).strip():
        fail("review PASS needs observed evidence")

    outcome = doc.get("outcome")
    if outcome not in OUTCOMES: fail("invalid outcome")
    if outcome == "VERIFIED":
        if verifier.get("status") != "PASS" or review.get("status") != "PASS": fail("VERIFIED requires passing verification and review")
        if "INDEPENDENT_VERIFICATION_COMPLETED" not in event_seq: fail("VERIFIED requires independent verification event")
        if decision == "BLOCKED": fail("VERIFIED cannot have blocked post-build testing")
        for rid in req_ids:
            if recorded.get(rid, {}).get("status") != "PASS": fail(f"VERIFIED requires PASS for {rid}")
        if any(c.get("status") == "FAIL" for c in checks_by_id.values()):
            fail("VERIFIED conflicts with failing check on final candidate")
        if doc.get("unsafe_actions"):
            fail("VERIFIED conflicts with unsafe or unapproved actions")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="JSON implementation evidence ledger")
    args = parser.parse_args()
    try:
        doc = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    except (OSError, ValueError) as ex:
        print(f"INVALID: could not load ledger: {ex}", file=sys.stderr)
        return 2
    errors = validate(doc)
    if errors:
        for err in errors: print(f"ERROR: {err}", file=sys.stderr)
        print(f"INVALID: {len(errors)} issue(s)")
        return 1
    print("VALID: ledger internally consistent (not proof of actual software correctness)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
