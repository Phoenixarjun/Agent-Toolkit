#!/usr/bin/env python3
"""Structural validator for Agent Toolkit Security Audit v2 evidence records.

Usage: python scripts/validate_security_audit.py path/to/audit.json
This checks internal consistency, NOT whether an assessment or agent run occurred.
"""
import json
import sys
from pathlib import Path

TIERS = {"LOW", "MODERATE", "HIGH", "CRITICAL"}
DEPTHS = {"SANITY", "STANDARD", "DEEP"}
APPLICABILITY = {"REQUIRED", "RECOMMENDED", "NOT_APPLICABLE", "UNDETERMINED"}
IMPLEMENTATION = {"COMPLETE", "PARTIAL", "ABSENT", "UNKNOWN"}
VERIFICATION = {"VERIFIED", "FAILED", "PARTIAL", "NOT_VERIFIED", "INCONCLUSIVE", "BLOCKED", "NOT_APPLICABLE"}
COVERAGE = {"planned", "covered", "candidate", "blocked", "deferred", "not_applicable", "out_of_scope"}
VERDICTS = {"confirmed", "needs_validation", "rejected"}
SEVERITIES = {"CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"}
OP_STATES = {"VERIFIED", "FAILED", "NOT_VERIFIED", "INCONCLUSIVE", "BLOCKED"}
OUTCOMES = {"ACCEPTABLE_WITHIN_ASSESSED_SCOPE", "REMEDIATION_REQUIRED", "INSUFFICIENT_EVIDENCE", "SCOPE_UNRESOLVED"}
ROLES = {"authority", "trust_path", "coverage_critic", "finding_verifier"}


def _nonempty(obj, field):
    return isinstance(obj.get(field), str) and bool(obj[field].strip())


def validate(data):
    errors = []

    def err(location, message):
        errors.append(f"{location}: {message}")

    if not isinstance(data, dict):
        return ["root: expected object"]
    if data.get("schema_version") != "2":
        err("schema_version", "expected '2'; v1 records require explicit migration/reassessment")

    target = data.get("target")
    if not isinstance(target, dict):
        err("target", "expected object")
        target = {}
    for field in ("repository", "revision", "scope", "impact_tier", "depth"):
        if not _nonempty(target, field):
            err("target", f"missing {field}")
    if target.get("impact_tier") not in TIERS:
        err("target.impact_tier", "invalid value")
    if target.get("depth") not in DEPTHS:
        err("target.depth", "invalid value")

    orchestration = data.get("orchestration")
    if not isinstance(orchestration, dict):
        err("orchestration", "expected object")
        orchestration = {}
    mode = orchestration.get("mode")
    if mode not in {"multi_agent", "unavailable"}:
        err("orchestration.mode", "must be multi_agent or unavailable")
    coordinator = orchestration.get("coordinator_context")
    if not isinstance(coordinator, str) or not coordinator.strip():
        err("orchestration.coordinator_context", "required")
    participants = orchestration.get("participants")
    if not isinstance(participants, list):
        err("orchestration.participants", "expected array")
        participants = []
    contexts = set()
    by_role = {}
    for i, p in enumerate(participants):
        loc = f"orchestration.participants[{i}]"
        if not isinstance(p, dict):
            err(loc, "expected object")
            continue
        role, context_id = p.get("role"), p.get("context_id")
        if role not in ROLES:
            err(loc, "invalid role")
        if not isinstance(context_id, str) or not context_id.strip():
            err(loc, "context_id required")
            continue
        if context_id in contexts or context_id == coordinator:
            err(loc, "agent contexts must be unique and distinct from coordinator")
        contexts.add(context_id)
        if p.get("revision") != target.get("revision"):
            err(loc, "participant revision must equal target revision")
        by_role.setdefault(role, []).append(context_id)
    if mode == "multi_agent" and not ROLES.issubset(set(by_role)):
        err("orchestration", "completed multi-agent audit needs authority, trust_path, coverage_critic and finding_verifier contexts")
    if mode == "unavailable" and participants:
        err("orchestration", "unavailable mode cannot claim agent participants")

    collections = {}
    indexes = {}
    for key in ("invariants", "operations", "coverage", "controls", "evidence", "findings"):
        items = data.get(key)
        if not isinstance(items, list):
            err(key, "expected array")
            items = []
        ids = set()
        for i, item in enumerate(items):
            loc = f"{key}[{i}]"
            if not isinstance(item, dict) or not _nonempty(item, "id"):
                err(loc, "expected object with nonempty id")
                continue
            if item["id"] in ids:
                err(loc, "duplicate ID")
            ids.add(item["id"])
        collections[key], indexes[key] = items, ids

    def references(item, key, destination, loc, required=False):
        values = item.get(key)
        if not isinstance(values, list) or (required and not values):
            err(loc, f"{key} requires {'nonempty ' if required else ''}array")
            return []
        for ref in values:
            if not isinstance(ref, str) or ref not in indexes[destination]:
                err(loc, f"unknown {destination} reference from {key}: {ref}")
        return values

    evid_by_id = {e["id"]: e for e in collections["evidence"] if isinstance(e, dict) and _nonempty(e, "id")}
    inv_by_id = {i["id"]: i for i in collections["invariants"] if isinstance(i, dict) and _nonempty(i, "id")}
    coverage_by_id = {c["id"]: c for c in collections["coverage"] if isinstance(c, dict) and _nonempty(c, "id")}

    for i, e in enumerate(collections["evidence"]):
        if not isinstance(e, dict):
            continue
        loc = f"evidence[{i}]"
        for key in ("method", "source", "observation", "revision", "context_id"):
            if not _nonempty(e, key):
                err(loc, f"{key} required")
        if e.get("revision") != target.get("revision"):
            err(loc, "evidence revision mismatch")
        if e.get("context_id") not in contexts and e.get("context_id") != coordinator:
            err(loc, "evidence refers to unregistered context")
        if e.get("kind") not in {"static", "dynamic", "configuration", "scanner", "inference"}:
            err(loc, "invalid evidence kind")
        if e.get("kind") == "dynamic" and not _nonempty(e, "runtime_identity"):
            err(loc, "dynamic evidence requires runtime_identity/build provenance")

    # Completed runs must contain actual independent review evidence,
    # including when no vulnerabilities were reported.
    if mode == "multi_agent":
        for key, role in (("coverage_critique_evidence_refs", "coverage_critic"),
                          ("record_review_evidence_refs", "finding_verifier")):
            items = orchestration.get(key)
            if not isinstance(items, list) or not items:
                err("orchestration", f"{key} requires nonempty evidence refs")
                continue
            if not any(evid_by_id.get(ref, {}).get("context_id") in by_role.get(role, []) for ref in items):
                err("orchestration", f"{key} must originate from independent {role} context")
            for ref in items:
                if ref not in indexes["evidence"]:
                    err("orchestration", f"{key} unknown evidence ref: {ref}")

    for i, invariant in enumerate(collections["invariants"]):
        if not isinstance(invariant, dict):
            continue
        loc = f"invariants[{i}]"
        for field in ("property", "boundary", "oracle"):
            if not _nonempty(invariant, field):
                err(loc, f"{field} required")
        references(invariant, "coverage_ids", "coverage", loc, required=True)

    for i, c in enumerate(collections["coverage"]):
        if not isinstance(c, dict):
            continue
        loc = f"coverage[{i}]"
        for field in ("surface", "boundary", "class"):
            if not _nonempty(c, field):
                err(loc, f"{field} required")
        status = c.get("status")
        if status not in COVERAGE:
            err(loc, "invalid coverage status")
        evidence_refs = references(c, "evidence_refs", "evidence", loc, required=status in {"covered", "candidate"})
        if status in {"blocked", "deferred", "not_applicable", "out_of_scope"} and not _nonempty(c, "reason"):
            err(loc, "state requires reason")
        if status == "covered":
            agents = c.get("investigated_by")
            if not isinstance(agents, list) or not agents:
                err(loc, "covered requires investigated_by context IDs")
            elif not any(a in by_role.get("authority", []) + by_role.get("trust_path", []) for a in agents):
                err(loc, "coverage not linked to a real investigator")
            elif any(a not in contexts for a in agents):
                err(loc, "unregistered investigated_by context")
        if status == "candidate" and not evidence_refs:
            err(loc, "candidate needs evidence")

    for i, op in enumerate(collections["operations"]):
        if not isinstance(op, dict):
            continue
        loc = f"operations[{i}]"
        for key in ("surface", "principal", "action", "resource", "context", "invariant_id"):
            if not _nonempty(op, key):
                err(loc, f"{key} required")
        if op.get("invariant_id") not in indexes["invariants"]:
            err(loc, "unknown invariant_id")
        expected, observed, status = op.get("expected"), op.get("observed"), op.get("status")
        if expected not in {"ALLOW", "DENY", "UNDETERMINED"} or observed not in {"ALLOW", "DENY", "UNKNOWN"} or status not in OP_STATES:
            err(loc, "invalid expected/observed/status")
        refs = references(op, "evidence_refs", "evidence", loc, required=status in {"VERIFIED", "FAILED"})
        cov_refs = references(op, "coverage_ids", "coverage", loc, required=True)
        if status in {"VERIFIED", "FAILED"} and refs and not any(
                evid_by_id.get(ref, {}).get("context_id") in
                by_role.get("authority", []) + by_role.get("trust_path", []) for ref in refs):
            err(loc, "verified/failed operation requires investigator-origin evidence")
        if status == "VERIFIED":
            if expected == "UNDETERMINED" or observed != expected:
                err(loc, "VERIFIED requires observed to match independently known ALLOW/DENY expectation")
            if not any(coverage_by_id.get(r, {}).get("status") == "covered" for r in cov_refs):
                err(loc, "VERIFIED requires covered coverage unit")
            if refs and all(evid_by_id.get(ref, {}).get("kind") == "inference" for ref in refs):
                err(loc, "VERIFIED cannot rely exclusively on inference")
        if status == "FAILED" and (expected == "UNDETERMINED" or observed not in {"ALLOW", "DENY"} or expected == observed):
            err(loc, "FAILED requires contradictory observed result")
        if status in {"NOT_VERIFIED", "INCONCLUSIVE", "BLOCKED"} and observed != "UNKNOWN":
            err(loc, "unverified operation must use observed UNKNOWN")
        if status == "BLOCKED" and not _nonempty(op, "reason"):
            err(loc, "blocked operation requires reason")

    for i, c in enumerate(collections["controls"]):
        if not isinstance(c, dict):
            continue
        loc = f"controls[{i}]"
        if not _nonempty(c, "property") or not _nonempty(c, "basis"):
            err(loc, "control property and applicability basis required")
        if c.get("applicability") not in APPLICABILITY or c.get("implementation") not in IMPLEMENTATION or c.get("verification") not in VERIFICATION:
            err(loc, "invalid control dimensions")
        cov_refs = references(c, "coverage_ids", "coverage", loc)
        references(c, "invariant_refs", "invariants", loc)
        ev_refs = references(c, "evidence_refs", "evidence", loc, required=c.get("verification") in {"VERIFIED", "FAILED", "PARTIAL"})
        if c.get("verification") == "VERIFIED":
            if c.get("applicability") in {"NOT_APPLICABLE", "UNDETERMINED"}:
                err(loc, "cannot verify a control with missing/inapplicable authority")
            if c.get("implementation") not in {"COMPLETE", "PARTIAL"}:
                err(loc, "VERIFIED requires observed implementation")
            if not any(coverage_by_id.get(ref, {}).get("status") == "covered" for ref in cov_refs):
                err(loc, "VERIFIED requires covered surface")
            if ev_refs and all(evid_by_id.get(ref, {}).get("kind") == "inference" for ref in ev_refs):
                err(loc, "VERIFIED cannot rely exclusively on inference")
        if c.get("applicability") == "NOT_APPLICABLE" and c.get("verification") != "NOT_APPLICABLE":
            err(loc, "inapplicable control must have NOT_APPLICABLE verification")
        if c.get("applicability") != "NOT_APPLICABLE" and c.get("verification") == "NOT_APPLICABLE":
            err(loc, "applicable control cannot have NOT_APPLICABLE verification")
        if c.get("verification") == "FAILED" and c.get("applicability") == "NOT_APPLICABLE":
            err(loc, "inapplicable control cannot fail")

    for i, finding in enumerate(collections["findings"]):
        if not isinstance(finding, dict):
            continue
        loc = f"findings[{i}]"
        if not _nonempty(finding, "title"):
            err(loc, "title required")
        verdict = finding.get("verdict")
        if verdict not in VERDICTS:
            err(loc, "invalid verdict")
        references(finding, "coverage_ids", "coverage", loc, required=True)
        references(finding, "evidence_refs", "evidence", loc, required=True)
        independent_refs = references(finding, "independent_evidence_refs", "evidence", loc, required=True)
        hunter, reviewer = finding.get("discovered_by"), finding.get("reviewed_by")
        if hunter not in by_role.get("authority", []) + by_role.get("trust_path", []):
            err(loc, "discovered_by must be real investigator context")
        if reviewer not in by_role.get("finding_verifier", []):
            err(loc, "reviewed_by must be independent verifier context")
        if hunter == reviewer:
            err(loc, "hunter cannot verify own finding")
        if independent_refs and not any(evid_by_id.get(ref, {}).get("context_id") == reviewer for ref in independent_refs):
            err(loc, "independent evidence must originate in reviewer context")
        if verdict == "confirmed":
            if finding.get("severity") not in SEVERITIES or not _nonempty(finding, "observed_effect") or not _nonempty(finding, "boundary"):
                err(loc, "confirmed requires severity, observed_effect and boundary")
        if verdict == "needs_validation":
            if "severity" in finding or not _nonempty(finding, "blocker") or not _nonempty(finding, "validation_plan"):
                err(loc, "needs_validation forbids severity and requires blocker/validation_plan")
        if verdict == "rejected":
            if "severity" in finding or not _nonempty(finding, "reason"):
                err(loc, "rejected forbids severity and requires reason")

    status, outcome = data.get("run_status"), data.get("report_outcome")
    if status not in {"complete", "incomplete"}:
        err("run_status", "must be complete or incomplete")
    if outcome not in OUTCOMES:
        err("report_outcome", "invalid outcome")
    if status == "incomplete" and not _nonempty(data, "incomplete_reason"):
        err("incomplete_reason", "required for incomplete assessment")
    if mode == "unavailable" and (status != "incomplete" or outcome not in {"INSUFFICIENT_EVIDENCE", "SCOPE_UNRESOLVED"}):
        err("orchestration", "unavailable agents cannot yield a complete audit or positive outcome")
    if status == "complete" and mode != "multi_agent":
        err("run_status", "completed audit requires actual multi-agent topology")
    if outcome == "ACCEPTABLE_WITHIN_ASSESSED_SCOPE":
        if status != "complete":
            err("report_outcome", "positive assurance requires complete audit")
        if not collections["controls"] or not collections["coverage"] or not collections["invariants"]:
            err("report_outcome", "positive assurance requires nonempty assessed controls, coverage, invariants")
        if any(c.get("applicability") == "REQUIRED" and c.get("verification") != "VERIFIED" for c in collections["controls"] if isinstance(c, dict)):
            err("report_outcome", "positive assurance impossible with unverified REQUIRED controls")
        if any(c.get("status") in {"planned", "candidate", "blocked", "deferred"} for c in collections["coverage"] if isinstance(c, dict)):
            err("report_outcome", "positive assurance impossible with open material coverage")
        if any(f.get("verdict") in {"confirmed", "needs_validation"} for f in collections["findings"] if isinstance(f, dict)):
            err("report_outcome", "positive assurance impossible with unresolved finding")
        if any(op.get("status") in {"FAILED", "NOT_VERIFIED", "BLOCKED", "INCONCLUSIVE"} for op in collections["operations"] if isinstance(op, dict)):
            err("report_outcome", "positive assurance impossible with unverified operation")
    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate_security_audit.py audit.json", file=sys.stderr)
        return 2
    path = Path(sys.argv[1])
    if not path.is_file() or path.stat().st_size > 5_000_000:
        print("ERROR: audit record missing or too large", file=sys.stderr)
        return 2
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (UnicodeError, ValueError) as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2
    problems = validate(obj)
    for item in problems[:100]:
        print("FAIL:", item)
    print(f"{'FAIL' if problems else 'PASS'}: {len(problems)} structural issue(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
