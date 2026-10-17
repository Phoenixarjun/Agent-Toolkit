"""Executable negative/positive consistency tests; not live agent behavioral evaluation."""
import copy
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = Path(__file__).resolve().parents[1] / "validate_code_exploration.py"
spec = importlib.util.spec_from_file_location("validator", MODULE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
BASE = json.loads((ROOT / "evals/code-explore/fixtures/example.json").read_text())


class RecordValidationTest(unittest.TestCase):
    def check_mutation(self, mutate, message):
        r = copy.deepcopy(BASE)
        mutate(r)
        errors = mod.validate(r)
        self.assertTrue(errors, message)
        return errors

    def test_good_synthetic_fixture(self):
        self.assertEqual(mod.validate(BASE), [])

    def test_limited_record_allows_missing_independent_contexts(self):
        r = copy.deepcopy(BASE)
        r["outcome"] = "limited"
        r["review"] = {}
        r["claims"][0]["verification_id"] = None
        self.assertFalse(mod.validate(r))

    def test_missing_goal(self):
        self.check_mutation(lambda r: r.update(goal=""), "missing goal")

    def test_duplicate_repo(self):
        self.check_mutation(lambda r: r["repositories"].append(r["repositories"][0]), "duplicate repo")

    def test_unpinned_complete(self):
        r = copy.deepcopy(BASE)
        r["repositories"][0]["revision"] = None
        r["evidence"][0]["revision"] = None
        self.assertTrue(mod.validate(r))

    def test_dirty_unknown_complete(self):
        self.check_mutation(lambda r: r["repositories"][0].update(dirty="unknown"), "dirty unknown")

    def test_out_of_scope_repo(self):
        self.check_mutation(lambda r: r["repositories"][0].update(authorized=False), "unauthorized")

    def test_duplicate_context_id(self):
        self.check_mutation(lambda r: r["participants"][3].update(context_id="runtime-session-002"), "self verification")

    def test_missing_context(self):
        self.check_mutation(lambda r: r["participants"][2].update(context_id=""), "missing context")

    def test_missing_actual_origin(self):
        self.check_mutation(lambda r: r["participants"][3].update(context_origin="claimed"), "invalid origin")

    def test_over_budget(self):
        self.check_mutation(lambda r: r["budget"].update(max_tasks=2), "budget exceeded")

    def test_dangling_task_repo(self):
        self.check_mutation(lambda r: r["tasks"][0].update(repository_ids=["service-z"]), "unknown repository")

    def test_path_traversal(self):
        self.check_mutation(lambda r: r["evidence"][0].update(path="../secrets"), "unsafe path")

    def test_absolute_path(self):
        self.check_mutation(lambda r: r["evidence"][0].update(path="/etc/passwd"), "absolute path")

    def test_windows_absolute_path(self):
        self.check_mutation(lambda r: r["evidence"][0].update(path=r"C:\\Users\\secrets"), "Windows absolute path")

    def test_bad_evidence_revision(self):
        self.check_mutation(lambda r: r["evidence"][0].update(revision="1234567"), "revision mismatch")

    def test_bad_line_span(self):
        self.check_mutation(lambda r: r["evidence"][0].update(line_start=30, line_end=5), "bad lines")

    def test_unverified_material_claim(self):
        self.check_mutation(lambda r: r["claims"][0].update(verification_id=None), "verification required")

    def test_same_investigator_as_verifier(self):
        self.check_mutation(lambda r: r["verifications"][0].update(participant_id="I2"), "false independence")

    def test_unverified_verdict_cannot_complete(self):
        self.check_mutation(lambda r: r["verifications"][0].update(verdict="unresolved"), "unconfirmed finding")

    def test_unattributed_verifier_evidence(self):
        self.check_mutation(lambda r: r["verifications"][0].update(evidence_ids=["E2"]), "verifier used investigator evidence")

    def test_dangling_claim_evidence(self):
        self.check_mutation(lambda r: r["claims"][0].update(evidence_ids=["unknown"]), "unknown evidence")

    def test_dangling_edge_evidence(self):
        self.check_mutation(lambda r: r["edges"][0].update(evidence_ids=["missing"]), "unknown edge evidence")

    def test_inferred_without_uncertainty(self):
        self.check_mutation(lambda r: r["claims"][0].update(status="INFERRED"), "missing uncertainty")

    def test_material_coverage_blocked_cannot_complete(self):
        self.check_mutation(lambda r: r["coverage"][0].update(status="blocked", reason="Source unavailable"), "blocked material")

    def test_missing_covered_evidence(self):
        self.check_mutation(lambda r: r["coverage"][0].update(evidence_ids=[]), "coverage without source")

    def test_critic_missing(self):
        self.check_mutation(lambda r: r["review"].update(critic_participant_id="I1"), "critic must be independent")

    def test_final_review_missing(self):
        self.check_mutation(lambda r: r["review"].update(final_ledger_review=False), "needs final review")

    def test_reviewer_no_completed_task(self):
        self.check_mutation(lambda r: r["tasks"][3].update(status="blocked"), "unexecuted review")

    def test_required_action_from_inferred_claim(self):
        r = copy.deepcopy(BASE)
        r["claims"][0].update(status="INFERRED", uncertainty="unproven")
        self.assertTrue(any("REQUIRED action" in e for e in mod.validate(r)))

    def test_retirement_cannot_be_required(self):
        self.check_mutation(lambda r: r["plan"][1].update(kind="REQUIRED"), "retirement gating")

    def test_retirement_requires_conditions(self):
        self.check_mutation(lambda r: r["plan"][1].update(retirement_conditions=[]), "retirement without proof")

    def test_plan_cycle(self):
        self.check_mutation(lambda r: r["plan"][0].update(depends_on=["P2"]), "circular plan")

    def test_empty_complete_claims(self):
        r = copy.deepcopy(BASE)
        r["claims"] = []
        self.assertTrue(mod.validate(r))

    def test_bad_id_type_does_not_crash(self):
        r = copy.deepcopy(BASE)
        r["coverage"][0]["claim_ids"] = [{"bad": "id"}]
        self.assertTrue(mod.validate(r))


if __name__ == "__main__":
    unittest.main()
