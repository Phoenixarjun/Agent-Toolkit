"""Deterministic negative/positive contract checks; NOT security agent benchmark tests."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location("validate_security_audit", ROOT / "scripts/validate_security_audit.py")
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)
EXAMPLE = json.loads((ROOT / "evals/security-audit/fixtures/SECURITY-AUDIT-DATA.example.json").read_text(encoding="utf-8"))


class AuditContractTests(unittest.TestCase):
    def assert_invalid(self, update, expected):
        data = copy.deepcopy(EXAMPLE)
        update(data)
        issues = validator.validate(data)
        self.assertTrue(any(expected in issue for issue in issues), issues)

    def test_unscoped_case_may_report_scope_unresolved(self):
        data = copy.deepcopy(EXAMPLE)
        data["orchestration"]["mode"] = "unavailable"
        data["orchestration"]["participants"] = []
        data["orchestration"].pop("coverage_critique_evidence_refs")
        data["orchestration"].pop("record_review_evidence_refs")
        data["run_status"] = "incomplete"
        data["report_outcome"] = "SCOPE_UNRESOLVED"
        data["incomplete_reason"] = "No authorized target specified"
        for k in ("invariants", "operations", "controls", "coverage", "evidence", "findings"):
            data[k] = []
        self.assertEqual([], validator.validate(data))

    def test_valid_synthetic_example(self):
        self.assertEqual([], validator.validate(copy.deepcopy(EXAMPLE)))

    def test_schema_v1_not_accepted(self):
        self.assert_invalid(lambda d: d.update(schema_version="1"), "schema_version")

    def test_duplicate_agent_context_rejected(self):
        self.assert_invalid(lambda d: d["orchestration"]["participants"][1].update(context_id="example-authority-context"), "unique")

    def test_no_critic_rejected(self):
        self.assert_invalid(lambda d: d["orchestration"]["participants"].pop(2), "coverage_critic")

    def test_no_critique_evidence_rejected(self):
        self.assert_invalid(lambda d: d["orchestration"].update(coverage_critique_evidence_refs=[]), "coverage_critique_evidence_refs")

    def test_no_final_record_review_rejected(self):
        self.assert_invalid(lambda d: d["orchestration"].update(record_review_evidence_refs=[]), "record_review_evidence_refs")

    def test_dynamic_evidence_needs_runtime_identity(self):
        self.assert_invalid(lambda d: d["evidence"][0].pop("runtime_identity"), "runtime_identity")

    def test_missing_verifier_rejected(self):
        self.assert_invalid(lambda d: d["orchestration"]["participants"].pop(3), "finding_verifier")

    def test_single_agent_unavailable_cannot_pass(self):
        def change(d):
            d["orchestration"]["mode"] = "unavailable"
            d["orchestration"]["participants"] = []
        self.assert_invalid(change, "unavailable agents cannot")

    def test_verified_op_must_match_expectation(self):
        self.assert_invalid(lambda d: d["operations"][0].update(observed="ALLOW"), "VERIFIED requires observed")

    def test_failed_op_cannot_match_expectation(self):
        self.assert_invalid(lambda d: d["operations"][0].update(status="FAILED"), "FAILED requires contradictory")

    def test_verified_op_requires_evidence(self):
        self.assert_invalid(lambda d: d["operations"][0].update(evidence_refs=[]), "nonempty")

    def test_control_cannot_be_verified_on_undetermined_applicability(self):
        self.assert_invalid(lambda d: d["controls"][0].update(applicability="UNDETERMINED"), "cannot verify")

    def test_positive_outcome_blocked_by_required_gap(self):
        self.assert_invalid(lambda d: d["controls"][0].update(verification="BLOCKED"), "unverified REQUIRED")

    def test_positive_outcome_blocked_by_coverage_gap(self):
        self.assert_invalid(lambda d: d["coverage"][0].update(status="blocked", reason="runtime unavailable"), "open material coverage")

    def test_stale_evidence_rejected(self):
        self.assert_invalid(lambda d: d["evidence"][0].update(revision="OTHER_SHA"), "revision mismatch")

    def test_covered_requires_real_investigator(self):
        self.assert_invalid(lambda d: d["coverage"][0].update(investigated_by=["example-critic-context"]), "real investigator")

    def test_unverified_control_cannot_be_positive_assurance(self):
        self.assert_invalid(lambda d: d["controls"][0].update(verification="NOT_VERIFIED"), "unverified REQUIRED")

    def test_confirmed_finding_requires_verifier_evidence(self):
        def change(d):
            d["findings"] = [{"id": "F-001", "title": "Cross-user read", "verdict": "confirmed", "severity": "HIGH", "observed_effect": "Unauthorized read", "boundary": "user->private profile", "coverage_ids": ["C-001"], "evidence_refs": ["E-001"], "independent_evidence_refs": ["E-001"], "discovered_by": "example-authority-context", "reviewed_by": "example-verifier-context"}]
        self.assert_invalid(change, "originate in reviewer")

    def test_unverified_candidate_cannot_have_severity(self):
        def change(d):
            d["findings"] = [{"id": "F-001", "title": "Candidate", "verdict": "needs_validation", "severity": "HIGH", "blocker": "No permitted staging target", "validation_plan": "Test with synthetic profiles", "coverage_ids": ["C-001"], "evidence_refs": ["E-001"], "independent_evidence_refs": ["E-002"], "discovered_by": "example-authority-context", "reviewed_by": "example-verifier-context"}]
        self.assert_invalid(change, "forbids severity")

    def test_confirmed_vulnerability_precludes_positive_assurance(self):
        def change(d):
            d["findings"] = [{"id": "F-001", "title": "Confirmed", "verdict": "confirmed", "severity": "HIGH", "observed_effect": "Unauthorized read", "boundary": "user->private profile", "coverage_ids": ["C-001"], "evidence_refs": ["E-001"], "independent_evidence_refs": ["E-002"], "discovered_by": "example-authority-context", "reviewed_by": "example-verifier-context"}]
        self.assert_invalid(change, "unresolved finding")

    def test_confirmed_remediation_required_record_is_valid(self):
        data = copy.deepcopy(EXAMPLE)
        data["operations"][0]["observed"] = "ALLOW"
        data["operations"][0]["status"] = "FAILED"
        data["controls"][0]["verification"] = "FAILED"
        data["controls"][0]["implementation"] = "PARTIAL"
        data["report_outcome"] = "REMEDIATION_REQUIRED"
        data["evidence"][0]["observation"] = "SYNTHETIC demonstration: unauthorized cross-user read succeeds"
        data["evidence"][1]["observation"] = "SYNTHETIC verifier re-inspected source and corroborated boundary violation"
        data["findings"] = [{
            "id": "F-001", "title": "Cross-user read", "verdict": "confirmed", "severity": "HIGH",
            "observed_effect": "Private profile exposed", "boundary": "user->private profile",
            "coverage_ids": ["C-001"], "evidence_refs": ["E-001"],
            "independent_evidence_refs": ["E-002"],
            "discovered_by": "example-authority-context", "reviewed_by": "example-verifier-context"
        }]
        self.assertEqual([], validator.validate(data))

    def test_absent_contexts_can_only_be_incomplete(self):
        data = copy.deepcopy(EXAMPLE)
        data["orchestration"]["mode"] = "unavailable"
        data["orchestration"]["participants"] = []
        data["orchestration"].pop("coverage_critique_evidence_refs")
        data["orchestration"].pop("record_review_evidence_refs")
        data["run_status"] = "incomplete"
        data["report_outcome"] = "INSUFFICIENT_EVIDENCE"
        data["incomplete_reason"] = "Harness cannot launch isolated subagents"
        # Example's evidence still attributes real agent roles, so remove inferred observations.
        data["evidence"] = []
        data["invariants"] = []
        data["operations"] = []
        data["controls"] = []
        data["coverage"] = []
        self.assertEqual([], validator.validate(data))


if __name__ == "__main__":
    unittest.main()
