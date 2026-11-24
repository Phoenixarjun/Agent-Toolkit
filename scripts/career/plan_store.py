from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import re
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path


class PlanError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise PlanError(message)


def ident(value, label):
    require(isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value), f"Invalid {label}")
    return value


def text(value, label):
    require(isinstance(value, str) and bool(value.strip()), f"Missing {label}")
    return value


def number(value, label, minimum=0):
    require(type(value) in (int, float) and math.isfinite(value) and value >= minimum, f"Invalid {label}")
    return value


def day(value, label):
    require(isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value), f"Invalid {label}")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise PlanError(f"Invalid {label}") from exc


def timestamp(value, label):
    text(value, label)
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        require(result.tzinfo is not None and result.utcoffset() is not None, f"Timezone required in {label}")
        return result
    except ValueError as exc:
        raise PlanError(f"Invalid {label}") from exc


def records(plan, key, allow_empty=False):
    items = plan.get(key)
    require(isinstance(items, list) and (allow_empty or bool(items)), f"Missing {key}")
    result = {}
    for item in items:
        require(isinstance(item, dict), f"Invalid record in {key}")
        item_id = ident(item.get("id"), f"{key} id")
        require(item_id not in result, f"Duplicate {key} id: {item_id}")
        result[item_id] = item
    return result


def references(value, allowed, label, nonempty=False):
    require(isinstance(value, list) and (not nonempty or bool(value)), f"Invalid {label}")
    for item in value:
        require(isinstance(item, str) and item in allowed, f"Unknown reference in {label}: {item}")
    require(len(value) == len(set(value)), f"Duplicate reference in {label}")
    return value


def string_list(value, label):
    require(isinstance(value, list), f"Invalid {label}")
    for item in value:
        text(item, label)


def validate_plan(plan):
    require(isinstance(plan, dict) and type(plan.get("schema_version")) is int and plan["schema_version"] == 1, "Unsupported schema version")
    pid = ident(plan.get("plan_id"), "plan ID")
    require("parent_plan_id" in plan, "Missing parent_plan_id")
    parent = plan["parent_plan_id"]
    if parent is not None:
        ident(parent, "parent plan ID")
        require(parent != pid, "Plan cannot parent itself")
    timestamp(plan.get("created_at"), "created_at")
    text(plan.get("target"), "target")
    start, deadline = day(plan.get("start_date"), "start_date"), day(plan.get("deadline"), "deadline")
    require(start <= deadline, "Deadline precedes start")
    duration = (deadline - start).days + 1
    require(duration <= 3660, "Plan horizon exceeds supported 10-year bound; use a rolling plan")
    hours = number(plan.get("weekly_hours"), "weekly_hours", 0.01)
    require(hours <= 168, "Weekly hours exceed elapsed time")
    buffer = number(plan.get("buffer_fraction"), "buffer_fraction")
    require(buffer < 1, "Reserve must be less than 100%")
    interval = plan.get("review_interval_days")
    require(type(interval) is int and 1 <= interval <= 366, "Review interval must be 1–366 days")
    string_list(plan.get("assumptions"), "assumptions")
    string_list(plan.get("evidence_refs"), "evidence_refs")
    text(plan.get("review_rationale"), "review_rationale")
    pillars = records(plan, "pillars")
    capabilities = records(plan, "capabilities")
    milestones = records(plan, "milestones", allow_empty=True)
    for p in pillars.values():
        text(p.get("outcome"), "pillar outcome")
        text(p.get("rationale"), "pillar rationale")
    for c in capabilities.values():
        text(c.get("outcome"), "capability outcome")
        references(c.get("pillar_ids"), pillars, "pillar_ids", True)
    ranges, loads = {}, {}
    graph = {}
    for mid, m in milestones.items():
        text(m.get("title"), "milestone title")
        references(m.get("capability_ids"), capabilities, "capability_ids", True)
        s, d = day(m.get("start_date"), "milestone start"), day(m.get("due_date"), "milestone due")
        require(start <= s <= d <= deadline, f"Milestone outside horizon: {mid}")
        ranges[mid] = (s, d)
        loads[mid] = number(m.get("estimated_hours"), "estimated_hours")
        graph[mid] = references(m.get("depends_on"), milestones, "depends_on")
        text(m.get("acceptance"), "milestone acceptance")
        require("workflow_id" in m, "Missing workflow_id")
        if m["workflow_id"] is not None:
            ident(m["workflow_id"], "workflow_id")
        activation = m.get("activation")
        require(activation in ("ACTIVE", "SCHEDULED", "CONDITIONAL"), f"Invalid activation: {mid}")
        if activation == "CONDITIONAL":
            text(m.get("trigger"), "conditional trigger")
    seen, visiting = set(), set()

    def visit(mid):
        require(mid not in visiting, f"Dependency cycle: {mid}")
        if mid in seen:
            return
        visiting.add(mid)
        for dep in graph[mid]:
            visit(dep)
        visiting.remove(mid)
        seen.add(mid)

    for mid in milestones:
        visit(mid)
    for mid, deps in graph.items():
        for dep in deps:
            require(ranges[dep][1] <= ranges[mid][0], f"Dependency timing conflict: {dep} -> {mid}")
            require(not (milestones[dep]["activation"] == "CONDITIONAL" and milestones[mid]["activation"] != "CONDITIONAL"), f"Unconditional milestone depends on conditional work: {mid}")
    daily = hours * (1 - buffer) / 7
    capacity = daily * duration
    total = sum(loads.values())
    require(total <= capacity + 1e-8, f"Estimated total {total:.2f}h exceeds capacity {capacity:.2f}h")
    weeks = []
    for offset in range(0, duration, 7):
        lo, hi = start + timedelta(days=offset), start + timedelta(days=min(offset + 6, duration - 1))
        scheduled = 0.0
        for mid, (s, d) in ranges.items():
            overlap = max(0, (min(d, hi) - max(s, lo)).days + 1)
            scheduled += loads[mid] * overlap / ((d - s).days + 1)
        limit = daily * ((hi - lo).days + 1)
        require(scheduled <= limit + 1e-8, f"Estimated load {scheduled:.2f}h exceeds {limit:.2f}h in period {lo}")
        weeks.append({"start": lo.isoformat(), "estimated_hours": round(scheduled, 4), "capacity_hours": round(limit, 4)})
    return {"plan_id": pid, "estimated_hours": round(total, 4), "capacity_hours": round(capacity, 4), "periods": weeks, "assumption": "Uniform effort across calendar days; all conditional work reserves capacity. This is a structural check, not a feasibility or authorization guarantee."}


def canonical(data):
    return (json.dumps(data, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def digest(data):
    return hashlib.sha256(canonical(data)).hexdigest()


def read_json(path):
    def unique(pairs):
        out = {}
        for k, v in pairs:
            require(k not in out, f"Duplicate JSON key: {k}")
            out[k] = v
        return out

    def reject_constant(value):
        raise PlanError(f"Nonfinite JSON value: {value}")

    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=unique, parse_constant=reject_constant)


def workspace(path):
    p = Path(os.path.abspath(Path(path).expanduser()))
    require(p.is_dir(), "Choose an existing private workspace directory explicitly")
    for node in (p, *p.parents):
        require(not node.is_symlink(), f"Symlink workspace boundary: {node}")
        require(not (node / ".git").exists(), "Workspace must be outside Git repositories")
        require(not ((node / "skills").is_dir() and (node / "catalog").is_dir() and (node / "agents").is_dir()), "Workspace must be outside Agent Toolkit")
    return p


def safe(root, *parts):
    p = root
    for part in parts:
        require(part not in ("", ".", "..") and Path(part).name == part, "Unsafe path component")
        p = p / part
        require(not p.is_symlink(), f"Symlink rejected: {p}")
    require(p.resolve().is_relative_to(root.resolve()), "Path escapes workspace")
    return p


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    fd, temp = tempfile.mkstemp(prefix=".career-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(canonical(data))
            out.flush()
            os.fsync(out.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


@contextlib.contextmanager
def lock(root):
    path = safe(root, "strategy", ".plan.lock")
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise PlanError("Plan store locked; resolve concurrent or interrupted writer manually") from exc
    try:
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


def pointer(root):
    p = safe(root, "strategy", "active-plan.json")
    if not p.exists():
        return None
    active = read_json(p)
    pid = ident(active.get("plan_id"), "active plan ID")
    candidate = read_json(safe(root, "strategy", "plans", pid + ".json"))
    validate_plan(candidate)
    require(candidate["plan_id"] == pid and active.get("plan_sha256") == digest(candidate), "Active plan integrity mismatch")
    approved = read_json(safe(root, "strategy", "decisions", pid + ".json"))
    validate_approval(approved, candidate)
    require(active.get("approval_sha256") == digest(approved), "Active approval integrity mismatch")
    return active


def stage(root, plan):
    validate_plan(plan)
    root = workspace(root)
    pid = plan["plan_id"]
    with lock(root):
        target = safe(root, "strategy", "plans", pid + ".json")
        if target.exists():
            require(digest(read_json(target)) == digest(plan), "Plan ID already exists with different contents")
        else:
            active = pointer(root)
            require(plan["parent_plan_id"] == (active["plan_id"] if active else None), "Proposal parent is not current active plan")
            atomic_write(target, plan)
    return {"plan_id": pid, "sha256": digest(plan), "state": "STAGED"}


def validate_approval(approval, plan):
    require(isinstance(approval, dict) and approval.get("decision") == "APPROVE", "Explicit APPROVE record required")
    require(approval.get("plan_id") == plan["plan_id"] and approval.get("plan_sha256") == digest(plan), "Approval does not match exact plan")
    require(timestamp(approval.get("approved_at"), "approved_at") >= timestamp(plan["created_at"], "created_at"), "Approval predates plan")
    text(approval.get("approval_reference"), "approval_reference")


def activate(root, pid, approval):
    root = workspace(root)
    ident(pid, "plan ID")
    with lock(root):
        plan = read_json(safe(root, "strategy", "plans", pid + ".json"))
        validate_plan(plan)
        require(plan["plan_id"] == pid, "Staged plan ID mismatch")
        validate_approval(approval, plan)
        active = pointer(root)
        if active and active["plan_id"] == pid:
            require(active["approval_sha256"] == digest(approval), "Already activated with different approval")
            return active
        require(plan["parent_plan_id"] == (active["plan_id"] if active else None), "Stale proposal; rebase and obtain new approval")
        decision = safe(root, "strategy", "decisions", pid + ".json")
        if decision.exists():
            require(digest(read_json(decision)) == digest(approval), "Conflicting approval record")
        else:
            atomic_write(decision, approval)
        new_pointer = {"plan_id": pid, "plan_sha256": digest(plan), "approval_sha256": digest(approval)}
        atomic_write(safe(root, "strategy", "active-plan.json"), new_pointer)
        return new_pointer


def main():
    parser = argparse.ArgumentParser(description="Optional career plan structural checks and immutable local version activation")
    commands = parser.add_subparsers(dest="command", required=True)
    validate = commands.add_parser("validate")
    validate.add_argument("plan", type=Path)
    staging = commands.add_parser("stage")
    staging.add_argument("workspace", type=Path)
    staging.add_argument("plan", type=Path)
    activation = commands.add_parser("activate")
    activation.add_argument("workspace", type=Path)
    activation.add_argument("plan_id")
    activation.add_argument("approval", type=Path)
    status = commands.add_parser("status")
    status.add_argument("workspace", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "validate":
            plan = read_json(args.plan)
            result = validate_plan(plan) | {"sha256": digest(plan)}
        elif args.command == "stage":
            result = stage(args.workspace, read_json(args.plan))
        elif args.command == "activate":
            result = activate(args.workspace, args.plan_id, read_json(args.approval))
        else:
            result = {"active": pointer(workspace(args.workspace))}
        print(json.dumps(result, indent=2))
    except (OSError, ValueError, TypeError, KeyError, AttributeError, RecursionError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
