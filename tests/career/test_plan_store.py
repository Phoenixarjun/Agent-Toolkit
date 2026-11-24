import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[2] / "scripts/career/plan_store.py"
SPEC = importlib.util.spec_from_file_location("career_plan_store", MODULE)
store = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(store)


def plan(pid="v1", parent=None):
    return {
        "schema_version": 1, "plan_id": pid, "parent_plan_id": parent,
        "created_at": "2026-01-01T09:00:00+00:00", "target": "Example role",
        "start_date": "2026-01-01", "deadline": "2026-01-28", "weekly_hours": 10,
        "buffer_fraction": 0.2, "review_interval_days": 14,
        "pillars": [{"id": "p1", "outcome": "Durable evidence", "rationale": "Target need"}],
        "capabilities": [{"id": "c1", "outcome": "Demonstrate capability", "pillar_ids": ["p1"]}],
        "milestones": [{"id": "m1", "title": "Practice", "capability_ids": ["c1"], "start_date": "2026-01-01", "due_date": "2026-01-14", "estimated_hours": 10, "depends_on": [], "acceptance": "Observed artifact", "workflow_id": "career-projects", "activation": "ACTIVE", "trigger": ""}],
        "assumptions": [], "evidence_refs": [], "review_rationale": "Initial example"
    }


def approval(p):
    return {"plan_id": p["plan_id"], "plan_sha256": store.digest(p), "decision": "APPROVE", "approved_at": "2026-01-02T09:00:00Z", "approval_reference": "Synthetic test decision"}


class PlanStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def test_capacity(self):
        r = store.validate_plan(plan())
        self.assertEqual(r["capacity_hours"], 32)
        self.assertEqual(r["estimated_hours"], 10)

    def test_total_overload(self):
        p = plan()
        p["milestones"][0]["estimated_hours"] = 40
        with self.assertRaisesRegex(store.PlanError, "exceeds capacity"):
            store.validate_plan(p)

    def test_period_overload(self):
        p = plan()
        p["milestones"][0]["due_date"] = "2026-01-07"
        with self.assertRaisesRegex(store.PlanError, "exceeds .* in period"):
            store.validate_plan(p)

    def test_cycle(self):
        p = plan()
        p["milestones"][0]["depends_on"] = ["m1"]
        with self.assertRaisesRegex(store.PlanError, "cycle"):
            store.validate_plan(p)

    def test_missing_pillar(self):
        p = plan()
        p["capabilities"][0]["pillar_ids"] = ["missing"]
        with self.assertRaises(store.PlanError):
            store.validate_plan(p)

    def test_conditional_trigger(self):
        p = plan()
        p["milestones"][0]["activation"] = "CONDITIONAL"
        with self.assertRaisesRegex(store.PlanError, "trigger"):
            store.validate_plan(p)

    def test_dependency_order(self):
        p = plan()
        m = copy.deepcopy(p["milestones"][0]); m.update(id="m2", depends_on=["m1"], estimated_hours=1)
        p["milestones"].append(m)
        with self.assertRaisesRegex(store.PlanError, "timing conflict"):
            store.validate_plan(p)

    def test_stage_does_not_activate(self):
        p = plan(); store.stage(self.root, p)
        self.assertIsNone(store.pointer(self.root))
        self.assertEqual(store.stage(self.root, p)["state"], "STAGED")

    def test_activation(self):
        p = plan(); store.stage(self.root, p)
        active = store.activate(self.root, "v1", approval(p))
        self.assertEqual(active, store.pointer(self.root))
        self.assertEqual(active, store.activate(self.root, "v1", approval(p)))

    def test_unapproved(self):
        p = plan(); store.stage(self.root, p)
        a = approval(p); a["decision"] = "DEFER"
        with self.assertRaises(store.PlanError):
            store.activate(self.root, "v1", a)
        self.assertIsNone(store.pointer(self.root))

    def test_wrong_hash(self):
        p = plan(); store.stage(self.root, p)
        a = approval(p); a["plan_sha256"] = "bad"
        with self.assertRaises(store.PlanError):
            store.activate(self.root, "v1", a)

    def test_immutable_and_stale(self):
        p = plan(); store.stage(self.root, p); store.activate(self.root, "v1", approval(p))
        first = (self.root / "strategy/plans/v1.json").read_bytes()
        b, c = plan("v2", "v1"), plan("v3", "v1")
        store.stage(self.root, b); store.stage(self.root, c)
        store.activate(self.root, "v2", approval(b))
        with self.assertRaisesRegex(store.PlanError, "Stale proposal"):
            store.activate(self.root, "v3", approval(c))
        p["target"] = "Mutated"
        with self.assertRaisesRegex(store.PlanError, "different contents"):
            store.stage(self.root, p)
        self.assertEqual(first, (self.root / "strategy/plans/v1.json").read_bytes())
        self.assertEqual(store.pointer(self.root)["plan_id"], "v2")

    def test_path_traversal(self):
        with self.assertRaises(store.PlanError):
            store.stage(self.root, plan("../escape"))

    def test_symlink(self):
        with tempfile.TemporaryDirectory() as outside:
            try:
                (self.root / "strategy").symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Symlinks unavailable")
            with self.assertRaises(store.PlanError):
                store.stage(self.root, plan())
            self.assertEqual(list(Path(outside).iterdir()), [])

    def test_repo_rejected(self):
        (self.root / ".git").mkdir()
        with self.assertRaises(store.PlanError):
            store.stage(self.root, plan())

    def test_locked(self):
        with store.lock(self.root):
            with self.assertRaisesRegex(store.PlanError, "locked"):
                store.stage(self.root, plan())

    def test_tampered_pointer(self):
        p = plan(); store.stage(self.root, p); store.activate(self.root, "v1", approval(p))
        file = self.root / "strategy/plans/v1.json"
        p["target"] = "Tampered"; file.write_bytes(store.canonical(p))
        with self.assertRaisesRegex(store.PlanError, "integrity mismatch"):
            store.pointer(self.root)

    def test_duplicate_json(self):
        f = self.root / "bad.json"; f.write_text('{"x":1,"x":2}')
        with self.assertRaisesRegex(store.PlanError, "Duplicate JSON key"):
            store.read_json(f)

    def test_approval_before_creation(self):
        p = plan(); store.stage(self.root, p)
        a = approval(p); a["approved_at"] = "2025-12-31T09:00:00Z"
        with self.assertRaisesRegex(store.PlanError, "predates"):
            store.activate(self.root, "v1", a)

    def test_ambiguous_dates_rejected(self):
        p = plan(); p["deadline"] = "20260128"
        with self.assertRaises(store.PlanError):
            store.validate_plan(p)


if __name__ == "__main__":
    unittest.main()
