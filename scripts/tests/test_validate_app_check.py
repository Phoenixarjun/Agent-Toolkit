import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("app_check_validator", ROOT / "scripts" / "validate_app_check.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
SAMPLE = json.loads((ROOT / "evals" / "app-check" / "fixtures" / "valid-bounded-sample.json").read_text())


class AppCheckValidationTests(unittest.TestCase):
    def check_invalid(self, modify, expected):
        data = copy.deepcopy(SAMPLE)
        modify(data)
        errors = MODULE.validate(data)
        self.assertTrue(any(expected in issue for issue in errors), errors)

    def test_valid_example(self):
        self.assertEqual(MODULE.validate(copy.deepcopy(SAMPLE)), [])

    def test_reject_wrong_schema(self):
        self.check_invalid(lambda d: d.update(schema="invalid"), "schema")

    def test_reject_non_object(self):
        self.assertTrue(MODULE.validate([]))

    def test_reject_missing_scope(self):
        self.check_invalid(lambda d: d["assessment"].update(scope=""), "scope")

    def test_reject_write_claim(self):
        self.check_invalid(lambda d: d["assessment"].update(no_code_changes=False), "no_code_changes")

    def test_reject_sufficient_without_inspection(self):
        self.check_invalid(lambda d: d["assessment"].update(status="SUFFICIENT", inspected_sources=[]), "SUFFICIENT")

    def test_reject_fake_independence(self):
        self.check_invalid(lambda d: d["assessment"].update(verification="INDEPENDENT"), "independent_context_ids")

    def test_accept_independent_context(self):
        data = copy.deepcopy(SAMPLE)
        data["assessment"].update(verification="INDEPENDENT", independent_context_ids=["ctx-27"])
        self.assertEqual(MODULE.validate(data), [])

    def test_reject_irrelevant_without_reason(self):
        self.check_invalid(lambda d: d["applicability"][1].update(reason=""), "reason")

    def test_reject_duplicate_area(self):
        self.check_invalid(lambda d: d["applicability"].append(dict(d["applicability"][0])), "duplicate area")

    def test_reject_ninth_question(self):
        self.check_invalid(lambda d: d.update(questions=[{"text": "Why?", "decision_affected": "Architecture choice"}] * 9), "more than eight")

    def test_reject_question_without_decision(self):
        self.check_invalid(lambda d: d.update(questions=[{"text": "How many users?", "decision_affected": ""}]), "questions[0]")

    def test_accept_zero_questions(self):
        self.assertEqual(MODULE.validate(copy.deepcopy(SAMPLE)), [])

    def test_reject_measured_without_provenance(self):
        self.check_invalid(lambda d: d["measurements"][0].update(status="MEASURED", value=500), "provenance")

    def test_reject_measured_without_environment(self):
        self.check_invalid(lambda d: d["measurements"][0].update(status="MEASURED", value=500, provenance="run-1", window="5m"), "environment")

    def test_reject_measured_without_window(self):
        self.check_invalid(lambda d: d["measurements"][0].update(status="MEASURED", value=500, provenance="run-1", environment="local"), "window")

    def test_reject_forecast_without_basis(self):
        self.check_invalid(lambda d: d["measurements"][0].update(status="FORECAST_WITH_BASIS", value=500), "provenance")

    def test_reject_unknown_metric_with_number(self):
        self.check_invalid(lambda d: d["measurements"][0].update(value=1200), "unknown metrics")

    def test_reject_p0_risk(self):
        self.check_invalid(lambda d: d["findings"][0].update(priority="P0"), "P0 requires a confirmed")

    def test_reject_p0_without_direct_evidence(self):
        self.check_invalid(lambda d: (d["findings"][0].update(status="CONFIRMED_DEFECT", priority="P0"), d["findings"][0]["evidence"][0].update(kind="INFERENCE")), "P0 requires direct evidence")

    def test_accept_p0_with_direct_evidence(self):
        data = copy.deepcopy(SAMPLE)
        data["findings"][0].update(status="CONFIRMED_DEFECT", priority="P0")
        self.assertEqual(MODULE.validate(data), [])

    def test_reject_confirmed_memory_leak_without_diagnostic(self):
        self.check_invalid(lambda d: d["findings"][0].update(topic="memory_leak", status="CONFIRMED_DEFECT"), "requires diagnostic evidence")

    def test_accept_memory_leak_with_diagnostic(self):
        data = copy.deepcopy(SAMPLE)
        data["findings"][0].update(topic="memory_leak", status="CONFIRMED_DEFECT")
        data["findings"][0]["evidence"][0]["kind"] = "RUNTIME_MEASUREMENT"
        self.assertEqual(MODULE.validate(data), [])

    def test_reject_missing_evidence(self):
        self.check_invalid(lambda d: d["findings"][0].update(evidence=[]), "at least one evidence")

    def test_reject_evidence_missing_provenance(self):
        self.check_invalid(lambda d: d["findings"][0]["evidence"][0].update(provenance=""), "origin and context")

    def test_reject_duplicate_finding_id(self):
        self.check_invalid(lambda d: d["findings"].append(copy.deepcopy(d["findings"][0])), "unique nonempty")

    def test_reject_nonsense_now_fix(self):
        self.check_invalid(lambda d: d["findings"][0].update(status="HYPOTHESIS", recommendation={"decision": "NOW", "action_kind": "FIX", "rationale": "unverified", "verification": "test"}), "cannot mandate")

    def test_allow_hypothesis_now_diagnose(self):
        data = copy.deepcopy(SAMPLE)
        data["findings"][0].update(status="HYPOTHESIS", recommendation={"decision": "NOW", "action_kind": "DIAGNOSE", "rationale": "cheap critical probe", "verification": "observe target behavior"})
        data["top_actions"][0]["decision"] = "NOW"
        self.assertEqual(MODULE.validate(data), [])

    def test_reject_no_change_with_fix(self):
        self.check_invalid(lambda d: d["findings"][0].update(recommendation={"decision": "NO_CHANGE", "action_kind": "FIX", "rationale": "not needed", "verification": "check"}), "NO_CHANGE requires NONE")

    def test_reject_action_without_test(self):
        self.check_invalid(lambda d: d["findings"][0]["recommendation"].update(verification=""), "action requires")

    def test_reject_top_action_without_finding(self):
        self.check_invalid(lambda d: d["top_actions"][0].update(finding_id="missing"), "must reference")

    def test_reject_top_action_disagreement(self):
        self.check_invalid(lambda d: d["top_actions"][0].update(decision="NOW"), "contradicts")

    def test_reject_more_than_five_top_actions(self):
        self.check_invalid(lambda d: d.update(top_actions=d["top_actions"] * 6), "more than five")

    def test_accept_no_material_findings(self):
        data = copy.deepcopy(SAMPLE)
        data["findings"] = []
        data["top_actions"] = []
        self.assertEqual(MODULE.validate(data), [])

    def test_allow_potential_risk_without_runtime(self):
        self.assertEqual(MODULE.validate(copy.deepcopy(SAMPLE)), [])


if __name__ == "__main__":
    unittest.main()
