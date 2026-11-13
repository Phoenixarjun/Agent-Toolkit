"""
scripts/tests/test_run_eval.py — Unit tests for scripts/run_eval.py behavioral evaluation runner.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest

import scripts.run_eval as runner


class RunEvalUnitTests(unittest.TestCase):
    def setUp(self):
        self.root = runner.ROOT
        self.evals_dir = runner.EVALS_DIR

    def test_discover_suites(self):
        suites = runner.discover_suites(self.evals_dir)
        self.assertGreater(len(suites), 10)
        suite_names = {s.name for s in suites}
        self.assertIn("app-check", suite_names)
        self.assertIn("product-reality", suite_names)
        self.assertIn("security-audit", suite_names)
        self.assertIn("code", suite_names)

    def test_load_suite_by_name(self):
        suite = runner.load_suite("product-reality", self.evals_dir)
        self.assertEqual(suite.name, "product-reality")
        self.assertGreater(len(suite.cases), 0)
        first_case = suite.cases[0]
        self.assertTrue(bool(first_case.case_id))
        self.assertTrue(bool(first_case.input))
        self.assertGreater(len(first_case.expect), 0)

    def test_load_suite_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            runner.load_suite("non-existent-suite-xyz", self.evals_dir)

    def test_normalize_various_schemas(self):
        # 1. Product-reality style (name, input, expect, reject)
        c1 = runner.normalize_case(
            "test-suite",
            {
                "name": "case_one",
                "input": "Prompt text",
                "expect": ["must include foo", "must include bar"],
                "reject": ["must not include baz"],
            },
            0,
        )
        self.assertEqual(c1.case_id, "case_one")
        self.assertEqual(c1.input, "Prompt text")
        self.assertEqual(len(c1.expect), 2)
        self.assertEqual(len(c1.reject), 1)

        # 2. App-check style (id, setup, expect, forbid)
        c2 = runner.normalize_case(
            "test-suite",
            {
                "id": "AC-01",
                "setup": "Application setup description",
                "expect": "Check state",
                "forbid": "Overengineering",
            },
            1,
        )
        self.assertEqual(c2.case_id, "AC-01")
        self.assertEqual(c2.input, "Application setup description")
        self.assertEqual(c2.expect, ["Check state"])
        self.assertEqual(c2.reject, ["Overengineering"])

        # 3. Code style (id, stimulus, required_behavior)
        c3 = runner.normalize_case(
            "test-suite",
            {
                "id": "C-01",
                "name": "Title",
                "stimulus": "Stimulus info",
                "required_behavior": ["Preserve behavior"],
            },
            2,
        )
        self.assertEqual(c3.case_id, "C-01")
        self.assertEqual(c3.name, "Title")
        self.assertEqual(c3.input, "Stimulus info")
        self.assertEqual(c3.expect, ["Preserve behavior"])

        # 4. Grill-me style with context and expected dict
        c4 = runner.normalize_case(
            "test-suite",
            {
                "id": "GM-01",
                "context": {"stage": "discovery", "answered": 3},
                "expected": {
                    "status": "READY",
                    "behaviors": ["Stop interview", "Return summary"],
                },
            },
            3,
        )
        self.assertEqual(c4.case_id, "GM-01")
        self.assertIn("discovery", c4.input)
        self.assertIn("Stop interview", c4.expect)
        self.assertIn("Return summary", c4.expect)

        # 5. Visualize style with given / when
        c5 = runner.normalize_case(
            "test-suite",
            {
                "id": "VIS-01",
                "given": "A monolith with internal services",
                "when": "Visualize the app",
                "expect": ["Logical top-level components"],
            },
            4,
        )
        self.assertEqual(c5.case_id, "VIS-01")
        self.assertIn("Given: A monolith", c5.input)
        self.assertIn("When: Visualize the app", c5.input)
        self.assertEqual(c5.expect, ["Logical top-level components"])

    def test_verify_case_definition(self):
        valid_case = runner.EvalCase(
            suite="test",
            case_id="T01",
            name="Valid",
            input="Valid stimulus",
            expect=["Expect something"],
        )
        self.assertEqual(runner.verify_case_definition(valid_case), [])

        invalid_case = runner.EvalCase(
            suite="test",
            case_id="",
            name="No ID",
            input="",
            expect=[],
        )
        issues = runner.verify_case_definition(invalid_case)
        self.assertGreater(len(issues), 0)

    def test_verify_all_suites_in_repository(self):
        suites = runner.discover_suites(self.evals_dir)
        total_errors = []
        for s in suites:
            valid, errs, msgs = runner.verify_suite_definitions(s)
            self.assertEqual(errs, 0, f"Suite {s.name} had definition errors: {msgs}")
            self.assertGreater(valid, 0)

    def test_evaluate_case_pass(self):
        case = runner.EvalCase(
            suite="test",
            case_id="E01",
            name="Pass Case",
            input="Review this feature",
            expect=["inspect test behavior", "mark distributed scaling NOT_APPLICABLE"],
            reject=["recommend database replicas or sharding"],
        )
        response = (
            "We inspect test behavior and determine that distributed scaling concerns are "
            "NOT_APPLICABLE for this single-process app. No infrastructure changes needed."
        )
        result = runner.evaluate_case(case, response)
        self.assertTrue(result.passed)
        self.assertEqual(result.status, "PASS")
        self.assertEqual(len(result.violations), 0)

    def test_evaluate_case_fail_rejection_violation(self):
        case = runner.EvalCase(
            suite="test",
            case_id="E02",
            name="Reject Violation Case",
            input="Review this feature",
            expect=["inspect state"],
            reject=["recommend database replicas"],
        )
        response = "We inspect state and recommend database replicas for scaling."
        result = runner.evaluate_case(case, response)
        self.assertFalse(result.passed)
        self.assertEqual(result.status, "FAIL")
        self.assertGreater(len(result.violations), 0)

    def test_evaluate_case_fail_missing_expectation(self):
        case = runner.EvalCase(
            suite="test",
            case_id="E03",
            name="Missing Expectation Case",
            input="Review this feature",
            expect=["require differential test evidence", "enforce cryptographic signature verification"],
            reject=[],
        )
        response = "Looks good to me, no issues found."
        result = runner.evaluate_case(case, response)
        self.assertFalse(result.passed)
        self.assertEqual(result.status, "FAIL")
        self.assertIn("Unmatched", result.details)
        self.assertEqual(len(result.unmatched_expectations), 2)

    def test_evaluate_case_structured_json(self):
        case = runner.EvalCase(
            suite="test",
            case_id="E04",
            name="Structured Report",
            input="Assess app health",
            expect=["APPLICABLE", "NOT_APPLICABLE"],
            expected_status="PASS",
        )
        response_dict = {
            "status": "PASS",
            "applicability": [
                {"area": "correctness", "status": "APPLICABLE"},
                {"area": "distributed-recovery", "status": "NOT_APPLICABLE"}
            ]
        }
        result = runner.evaluate_case(case, response_dict)
        self.assertTrue(result.passed)
        self.assertEqual(result.status, "PASS")

    def test_format_summary_report(self):
        results = [
            runner.CaseResult(
                suite="suite-a",
                case_id="C01",
                name="Pass Case",
                passed=True,
                status="PASS",
                details="All expectations satisfied",
            ),
            runner.CaseResult(
                suite="suite-a",
                case_id="C02",
                name="Fail Case",
                passed=False,
                status="FAIL",
                details="Missing required expectation",
                unmatched_expectations=["expected auth token check"],
            ),
        ]
        text, structured = runner.format_summary_report(results)
        self.assertIn("suite-a", text)
        self.assertEqual(structured["verdict"], "FAIL")
        self.assertEqual(structured["total"], 2)
        self.assertEqual(structured["passed"], 1)
        self.assertEqual(structured["failed"], 1)

    def test_load_responses_from_file(self):
        with tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False) as tf:
            json.dump({
                "C01": "Sample response text for C01",
                "C02": {"status": "PASS", "data": "value"}
            }, tf)
            tf_path = Path(tf.name)

        try:
            mapping = runner.load_responses(tf_path)
            self.assertIn("C01", mapping)
            self.assertIn("C02", mapping)
        finally:
            tf_path.unlink(missing_ok=True)

    def test_main_cli_verify_definitions(self):
        code = runner.main(["--eval", "product-reality", "--verify-definitions"])
        self.assertEqual(code, 0)

    def test_main_cli_all_verify(self):
        code = runner.main(["--all", "--verify-definitions"])
        self.assertEqual(code, 0)

    def test_main_cli_output_file(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            out_path = Path(tf.name)

        try:
            code = runner.main([
                "--eval", "intent-capture",
                "--verify-definitions",
                "--output", str(out_path),
            ])
            self.assertEqual(code, 0)
            self.assertTrue(out_path.is_file())
            data = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(data["verdict"], "PASS")
            self.assertEqual(data["total"], 6)
        finally:
            out_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
