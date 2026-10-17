import copy
import importlib.util
import json
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location("validate_code_implementation", BASE / "scripts" / "validate_code_implementation.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
FIXTURE = json.loads((BASE / "evals/code/fixtures/verified-illustrative.json").read_text())


class ImplementationLedgerTests(unittest.TestCase):
    def setUp(self):
        self.doc = copy.deepcopy(FIXTURE)

    def assert_invalid(self, expected):
        errors = mod.validate(self.doc)
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_valid_illustrative_fixture(self):
        self.assertEqual(mod.validate(self.doc), [])

    def test_missing_acceptance(self):
        self.doc["requirements"].pop(0)
        self.assert_invalid("explicit evidence entries")

    def test_verifier_not_independent(self):
        self.doc["verification"]["context"] = "example-builder-context"
        self.assert_invalid("distinct real context")

    def test_stale_check_candidate(self):
        self.doc["checks"][0]["candidate_id"] = "old"
        self.assert_invalid("stale candidate evidence")

    def test_stale_verifier_candidate(self):
        self.doc["verification"]["candidate_id"] = "old"
        self.assert_invalid("stale candidate")

    def test_unscoped_change(self):
        self.doc["tasks"][0]["changed_paths"] = ["src/private.py"]
        self.assert_invalid("outside write scope")

    def test_parent_traversal(self):
        self.doc["tasks"][0]["allowed_paths"] = ["src/../"]
        self.assert_invalid("unsafe allowed path")

    def test_empty_approval_for_dirty_changes(self):
        self.doc["baseline"]["repositories"][0]["dirty_paths"] = ["src/feature.py"]
        self.assert_invalid("pre-existing dirty path")

    def test_valid_dirty_path_approval(self):
        self.doc["baseline"]["repositories"][0]["dirty_paths"] = ["src/feature.py"]
        self.doc["dirty_path_approvals"] = [{"repository": "app", "path": "src/feature.py", "approval_ref": "user-ok"}]
        self.assertEqual(mod.validate(self.doc), [])

    def test_tdd_started_too_early(self):
        self.doc["events"] = [
            {"seq": 1, "type": "TDD_ASSIST_STARTED"}, {"seq": 2, "type": "BUILD_COMPLETED"},
            {"seq": 3, "type": "FINAL_CANDIDATE_SELECTED"}, {"seq": 4, "type": "INDEPENDENT_VERIFICATION_COMPLETED"}]
        self.assert_invalid("cannot start before implementation")

    def test_used_tdd_requires_real_behavior_test(self):
        for check in self.doc["checks"]:
            check["kind"] = "diff"
        self.assert_invalid("requires independent successful behavior/runtime check")

    def test_tdd_not_used_does_not_need_event(self):
        self.doc["post_build_testing"] = {"decision": "NOT_APPLICABLE", "reason": "Only text formatting changed"}
        self.doc["events"] = [e for e in self.doc["events"] if e["type"] != "TDD_ASSIST_STARTED"]
        self.assertEqual(mod.validate(self.doc), [])

    def test_wrong_tdd_label(self):
        self.doc["post_build_testing"]["mode"] = "retroactive-red-green"
        self.assert_invalid("post_implementation")

    def test_duplicate_writer_same_file(self):
        task = copy.deepcopy(self.doc["tasks"][0]); task["id"] = "CODE-002"; task["builder_context"] = "other-builder"
        self.doc["tasks"].append(task)
        self.assert_invalid("overlapping writers")

    def test_dependency_cycle(self):
        self.doc["tasks"][0]["depends_on"] = ["CODE-002"]
        task = copy.deepcopy(self.doc["tasks"][0]); task["id"] = "CODE-002"; task["depends_on"] = ["CODE-001"]
        task["changed_paths"] = []
        self.doc["tasks"].append(task)
        self.assert_invalid("dependency cycle")

    def test_extra_candidate_file(self):
        self.doc["candidate"]["paths"].append({"repository": "app", "path": "src/other.py"})
        self.assert_invalid("exactly match")

    def test_failed_check_blocks_verified(self):
        self.doc["checks"][0]["status"] = "FAIL"
        self.assert_invalid("conflicts with failing check")

    def test_blocked_assist_blocks_verified(self):
        self.doc["post_build_testing"] = {"decision": "BLOCKED", "reason": "No safe integration environment"}
        self.doc["events"] = [e for e in self.doc["events"] if e["type"] != "TDD_ASSIST_STARTED"]
        self.assert_invalid("cannot have blocked")

    def test_missing_review_evidence(self):
        self.doc["review"]["evidence"] = ""
        self.assert_invalid("needs observed evidence")

    def test_fabricated_independent_requirement_evidence(self):
        self.doc["checks"][0]["runner_context"] = "example-builder-context"
        self.assert_invalid("independent verifier's passing check")

    def test_review_failure_blocks_verified(self):
        self.doc["review"]["status"] = "FAIL"
        self.assert_invalid("requires passing verification and review")

    def test_unsafe_action_blocks_verified(self):
        self.doc["unsafe_actions"] = ["unapproved rewrite"]
        self.assert_invalid("unsafe or unapproved")

    def test_missing_event(self):
        self.doc["events"] = [e for e in self.doc["events"] if e["type"] != "INDEPENDENT_VERIFICATION_COMPLETED"]
        self.assert_invalid("requires independent verification event")

    def test_invalid_check_state(self):
        self.doc["checks"][0]["status"] = "DONE"
        self.assert_invalid("invalid status")

    def test_unknown_acceptance_id(self):
        self.doc["tasks"][0]["acceptance_ids"] = ["AC-999"]
        self.assert_invalid("unknown acceptance ID")


if __name__ == "__main__":
    unittest.main()
