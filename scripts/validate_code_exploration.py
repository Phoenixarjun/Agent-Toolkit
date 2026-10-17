#!/usr/bin/env python3
"""Structural/code-impact consistency validator. Does NOT verify source truth."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import PurePosixPath

MODES = {"focused", "standard", "deep"}
OUTCOMES = {"complete", "limited", "blocked"}
ROLES = {"path_explorer", "contract_explorer", "coverage_critic", "evidence_verifier"}
STATES = {"OBSERVED", "INFERRED", "UNRESOLVED", "CONTRADICTED"}
IMPACTS = {"low", "medium", "high", "critical"}
COVERAGE = {"covered", "partial", "blocked", "not_applicable", "out_of_scope"}
EDGE_KINDS = {"CALLS", "IMPLEMENTS", "READS", "WRITES", "EMITS", "CONSUMES", "DEPENDS_ON", "CONFIGURES", "EXPOSES", "RESOLVES"}
PLAN_KINDS = {"REQUIRED", "CONDITIONAL", "OPTIONAL"}
VERDICTS = {"confirmed", "contradicted", "unresolved"}
HEX_SHA = re.compile(r"^[0-9a-fA-F]{7,40}$")


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def is_bool(value):
    return isinstance(value, bool)


def unique_index(items, namespace, errors):
    result = {}
    if not isinstance(items, list):
        errors.append(f"{namespace}: expected list")
        return result
    for i, entry in enumerate(items):
        if not isinstance(entry, dict):
            errors.append(f"{namespace}[{i}]: expected object")
            continue
        ident = entry.get("id")
        if not nonblank(ident):
            errors.append(f"{namespace}[{i}]: missing id")
        elif ident in result:
            errors.append(f"{namespace}: duplicate id {ident}")
        else:
            result[ident] = entry
    return result


def path_safe(path):
    if not nonblank(path) or "\\" in path or "\x00" in path or ":" in path:
        return False
    p = PurePosixPath(path)
    return not p.is_absolute() and all(part not in ("", ".", "..") for part in path.split("/")) and path != "."


def ids_valid(values, index, where, errors, allow_empty=False):
    if not isinstance(values, list) or (not values and not allow_empty):
        errors.append(f"{where}: expected {'possibly empty' if allow_empty else 'nonempty'} list")
        return
    for value in values:
        if not isinstance(value, str) or value not in index:
            errors.append(f"{where}: dangling or invalid reference {value!r}")


def validate(record):
    errors = []
    if not isinstance(record, dict):
        return ["root must be an object"]
    if record.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not nonblank(record.get("goal")):
        errors.append("goal missing")
    mode, outcome = record.get("mode"), record.get("outcome")
    if mode not in MODES:
        errors.append("invalid mode")
    if outcome not in OUTCOMES:
        errors.append("invalid outcome")

    budget = record.get("budget", {})
    if not isinstance(budget, dict):
        errors.append("budget must be object")
        budget = {}
    for field in ("max_concurrent", "max_tasks", "max_followup_waves"):
        v = budget.get(field)
        if type(v) is not int or v < (0 if field == "max_followup_waves" else 1):
            errors.append(f"budget.{field}: invalid nonnegative/positive integer")
    if isinstance(budget.get("max_concurrent"), int) and isinstance(budget.get("max_tasks"), int):
        if budget["max_concurrent"] > budget["max_tasks"]:
            errors.append("max_concurrent cannot exceed max_tasks")

    repos = unique_index(record.get("repositories"), "repositories", errors)
    if not repos:
        errors.append("no repositories declared")
    for rid, repo in repos.items():
        if not nonblank(repo.get("locator")):
            errors.append(f"repository {rid}: missing locator")
        rev = repo.get("revision")
        if rev is not None and (not nonblank(rev) or not HEX_SHA.fullmatch(rev)):
            errors.append(f"repository {rid}: revision must be hex Git SHA or null")
        if repo.get("dirty") not in (True, False, "unknown"):
            errors.append(f"repository {rid}: dirty must be true/false/unknown")
        if not isinstance(repo.get("authorized"), bool):
            errors.append(f"repository {rid}: authorized must be boolean")
        if outcome == "complete" and (rev is None or repo.get("dirty") == "unknown" or repo.get("authorized") is not True):
            errors.append(f"complete requires pinned, authorized and dirty-status-known repo {rid}")

    participants = unique_index(record.get("participants", []), "participants", errors)
    seen_contexts = {}
    for pid, participant in participants.items():
        if participant.get("role") not in ROLES:
            errors.append(f"participant {pid}: invalid role")
        context_id = participant.get("context_id")
        if not nonblank(context_id):
            errors.append(f"participant {pid}: missing actual context ID")
        elif context_id in seen_contexts:
            errors.append(f"context {context_id} reused by {pid} and {seen_contexts[context_id]}")
        else:
            seen_contexts[context_id] = pid
        if participant.get("context_origin") != "harness":
            errors.append(f"participant {pid}: context_origin must be harness (self-asserted metadata, not proof)")

    tasks = unique_index(record.get("tasks", []), "tasks", errors)
    if isinstance(budget.get("max_tasks"), int) and len(tasks) > budget["max_tasks"]:
        errors.append("total delegated tasks exceeds max_tasks")
    for tid, task in tasks.items():
        if task.get("participant_id") not in participants:
            errors.append(f"task {tid}: dangling participant")
        ids_valid(task.get("repository_ids"), repos, f"task {tid}.repository_ids", errors)
        if not nonblank(task.get("question")) or task.get("status") not in ("completed", "partial", "blocked"):
            errors.append(f"task {tid}: missing question or invalid status")

    evidence = unique_index(record.get("evidence", []), "evidence", errors)
    for eid, ev in evidence.items():
        rid = ev.get("repository_id")
        if rid not in repos:
            errors.append(f"evidence {eid}: invalid repository")
        elif ev.get("revision") != repos[rid].get("revision"):
            errors.append(f"evidence {eid}: revision does not match pinned repository")
        if not path_safe(ev.get("path")):
            errors.append(f"evidence {eid}: unsafe or invalid relative path")
        start, end = ev.get("line_start"), ev.get("line_end")
        if type(start) is not int or type(end) is not int or start < 1 or end < start:
            errors.append(f"evidence {eid}: invalid line span")
        if ev.get("participant_id") not in participants:
            errors.append(f"evidence {eid}: invalid participant")
        if not nonblank(ev.get("observation")):
            errors.append(f"evidence {eid}: no observation")

    claims = unique_index(record.get("claims", []), "claims", errors)
    verifications = unique_index(record.get("verifications", []), "verifications", errors)
    for vid, v in verifications.items():
        claim_id = v.get("claim_id")
        pid = v.get("participant_id")
        if claim_id not in claims:
            errors.append(f"verification {vid}: unknown claim")
        if pid not in participants or participants[pid].get("role") != "evidence_verifier":
            errors.append(f"verification {vid}: verifier role required")
        if v.get("verdict") not in VERDICTS:
            errors.append(f"verification {vid}: invalid verdict")
        ids_valid(v.get("evidence_ids"), evidence, f"verification {vid}.evidence_ids", errors, allow_empty=v.get("verdict") == "unresolved")
        if not nonblank(v.get("notes")):
            errors.append(f"verification {vid}: missing notes")
        if pid in participants:
            for eid in v.get("evidence_ids", []) if isinstance(v.get("evidence_ids"), list) else []:
                if eid in evidence and evidence[eid].get("participant_id") != pid:
                    errors.append(f"verification {vid}: evidence {eid} not independently attributed to verifier")

    for cid, claim in claims.items():
        status = claim.get("status")
        impact = claim.get("impact")
        if status not in STATES or impact not in IMPACTS or not is_bool(claim.get("material")):
            errors.append(f"claim {cid}: invalid state, impact, or material flag")
        if not nonblank(claim.get("statement")):
            errors.append(f"claim {cid}: empty statement")
        ids_valid(claim.get("evidence_ids"), evidence, f"claim {cid}.evidence_ids", errors, allow_empty=status == "UNRESOLVED")
        investigator = claim.get("investigator_id")
        if investigator not in participants or participants[investigator].get("role") not in ("path_explorer", "contract_explorer"):
            errors.append(f"claim {cid}: investigator role required")
        if status in ("INFERRED", "UNRESOLVED", "CONTRADICTED") and not nonblank(claim.get("uncertainty")):
            errors.append(f"claim {cid}: non-observed claim requires uncertainty")
        vid = claim.get("verification_id")
        needs_independent = outcome == "complete" and (claim.get("material") or impact in ("high", "critical"))
        if needs_independent and vid not in verifications:
            errors.append(f"complete material claim {cid}: independent verification required")
        if vid is not None:
            v = verifications.get(vid)
            if v is None or v.get("claim_id") != cid:
                errors.append(f"claim {cid}: invalid verification mapping")
            elif v.get("participant_id") == investigator or (investigator in participants and v.get("participant_id") in participants and participants[v["participant_id"]].get("context_id") == participants[investigator].get("context_id")):
                errors.append(f"claim {cid}: verifier must have separate context")
            elif outcome == "complete" and needs_independent and v.get("verdict") != "confirmed":
                errors.append(f"complete claim {cid}: material premise not confirmed")

    edges = unique_index(record.get("edges", []), "edges", errors)
    for edge_id, edge in edges.items():
        if edge.get("kind") not in EDGE_KINDS or edge.get("status") not in STATES:
            errors.append(f"edge {edge_id}: invalid kind or status")
        for side in ("from", "to"):
            node = edge.get(side)
            if not isinstance(node, dict) or node.get("repository_id") not in repos or not nonblank(node.get("symbol")):
                errors.append(f"edge {edge_id}.{side}: invalid node")
        ids_valid(edge.get("evidence_ids"), evidence, f"edge {edge_id}.evidence_ids", errors, allow_empty=edge.get("status") == "UNRESOLVED")
        if edge.get("status") != "OBSERVED" and not nonblank(edge.get("uncertainty")):
            errors.append(f"edge {edge_id}: non-observed edge needs uncertainty")

    coverage = unique_index(record.get("coverage", []), "coverage", errors)
    if outcome == "complete" and not coverage:
        errors.append("complete record requires coverage")
    for k, c in coverage.items():
        if not nonblank(c.get("obligation")) or c.get("status") not in COVERAGE:
            errors.append(f"coverage {k}: invalid obligation/status")
        ids_valid(c.get("claim_ids"), claims, f"coverage {k}.claim_ids", errors, allow_empty=True)
        ids_valid(c.get("evidence_ids"), evidence, f"coverage {k}.evidence_ids", errors, allow_empty=c.get("status") != "covered")
        if c.get("status") != "covered" and not nonblank(c.get("reason")):
            errors.append(f"coverage {k}: unclosed coverage requires reason")
        if outcome == "complete" and c.get("priority") == "material" and c.get("status") in ("partial", "blocked"):
            errors.append(f"complete record has material gap {k}")

    plans = unique_index(record.get("plan", []), "plan", errors)
    for pid, item in plans.items():
        if item.get("kind") not in PLAN_KINDS or not nonblank(item.get("action")):
            errors.append(f"plan {pid}: invalid kind/action")
        ids_valid(item.get("claim_ids"), claims, f"plan {pid}.claim_ids", errors, allow_empty=item.get("kind") == "OPTIONAL")
        ids_valid(item.get("depends_on"), plans, f"plan {pid}.depends_on", errors, allow_empty=True)
        if not nonblank(item.get("validation")):
            errors.append(f"plan {pid}: missing proposed validation")
        if not is_bool(item.get("retirement")):
            errors.append(f"plan {pid}: retirement must be boolean")
        if item.get("retirement") and (item.get("kind") == "REQUIRED" or not isinstance(item.get("retirement_conditions"), list) or len(item.get("retirement_conditions")) < 2):
            errors.append(f"plan {pid}: retirement is conditional, requires multiple proof conditions")
        for cid in item.get("claim_ids", []) if isinstance(item.get("claim_ids"), list) else []:
            c = claims.get(cid)
            if c and item.get("kind") == "REQUIRED" and c.get("status") != "OBSERVED":
                errors.append(f"plan {pid}: REQUIRED action rests on non-observed claim {cid}")

    # Detect circular prerequisite graph: serial implementation order cannot be cyclic.
    visited, active = set(), set()
    def visit(node):
        if node in active:
            errors.append(f"plan dependency cycle at {node}")
            return
        if node in visited or node not in plans:
            return
        active.add(node)
        deps = plans[node].get("depends_on", [])
        for d in deps if isinstance(deps, list) else []:
            visit(d)
        active.remove(node)
        visited.add(node)
    for pid in plans:
        visit(pid)

    review = record.get("review", {})
    if not isinstance(review, dict):
        errors.append("review must be an object")
        review = {}
    if outcome == "complete":
        if not claims and not edges:
            errors.append("complete record cannot be empty of code observations")
        if mode in ("standard", "deep"):
            critic = participants.get(review.get("critic_participant_id"))
            if not critic or critic.get("role") != "coverage_critic":
                errors.append("complete standard/deep requires independent coverage critic")
        verifier = participants.get(review.get("verifier_participant_id"))
        if not verifier or verifier.get("role") != "evidence_verifier":
            errors.append("complete requires independent evidence verifier")
        if review.get("final_ledger_review") is not True:
            errors.append("complete requires signed final evidence review (self-asserted)")
        if not nonblank(review.get("notes")):
            errors.append("complete requires final review notes")
        if not any(p.get("role") in ("path_explorer", "contract_explorer") for p in participants.values()):
            errors.append("complete requires an actual investigator")
        role_ids = [review.get("critic_participant_id"), review.get("verifier_participant_id")]
        if role_ids[0] and role_ids[0] == role_ids[1]:
            errors.append("critic and verifier must be different participant contexts")
        if len(tasks) == 0:
            errors.append("complete requires actual delegated tasks")
        task_owners = {t.get("participant_id") for t in tasks.values() if t.get("status") == "completed"}
        for pid in (review.get("critic_participant_id") if mode in ("standard", "deep") else None, review.get("verifier_participant_id")):
            if pid and pid not in task_owners:
                errors.append(f"complete requires completed task by review participant {pid}")

    return errors


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("record", help="JSON impact ledger")
    args = p.parse_args(argv)
    try:
        with open(args.record, encoding="utf-8") as f:
            record = json.load(f)
    except (OSError, ValueError) as e:
        print(f"INVALID RECORD: {e}", file=sys.stderr)
        return 2
    errors = validate(record)
    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        print(f"FAILED ({len(errors)} issue(s)). This tool does not verify source truth.", file=sys.stderr)
        return 1
    print("PASS: ledger structurally consistent. Source facts, runtime behavior and genuine context isolation remain unverified by this script.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
