#!/usr/bin/env python3
"""
scripts/run_eval.py — Behavioral Evaluation Runner for Agent Toolkit.

Loads, validates, and executes behavioral evaluation scenarios defined in
evals/*/cases.yaml against agent responses, mock outputs, or test fixtures.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import sys
from typing import Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
EVALS_DIR = ROOT / "evals"

# Stopwords to exclude when extracting semantic keywords from expectation text
COMMON_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "at",
    "by", "for", "with", "about", "against", "between", "into", "through",
    "during", "before", "after", "above", "below", "to", "from", "up", "down",
    "in", "out", "on", "off", "over", "under", "again", "further", "then",
    "once", "here", "there", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "nor", "not", "only", "own",
    "same", "so", "than", "too", "very", "s", "t", "can", "will", "just",
    "don", "should", "now", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "having", "do", "does", "did", "doing", "would",
    "could", "might", "must", "shall"
}


@dataclass
class EvalCase:
    suite: str
    case_id: str
    name: str
    input: str
    expect: list[str] = field(default_factory=list)
    reject: list[str] = field(default_factory=list)
    expected_status: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite": self.suite,
            "case_id": self.case_id,
            "name": self.name,
            "input": self.input,
            "expect": self.expect,
            "reject": self.reject,
            "expected_status": self.expected_status,
            "metadata": self.metadata,
        }


@dataclass
class EvalSuite:
    name: str
    path: Path
    version: str | None = None
    status: str | None = None
    criteria: list[str] = field(default_factory=list)
    cases: list[EvalCase] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class CaseResult:
    suite: str
    case_id: str
    name: str
    passed: bool
    status: str  # "PASS", "FAIL", "SKIPPED", "VERIFIED_DEFINITION"
    matched_expectations: list[str] = field(default_factory=list)
    unmatched_expectations: list[str] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    details: str = ""
    response_preview: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite": self.suite,
            "case_id": self.case_id,
            "name": self.name,
            "passed": self.passed,
            "status": self.status,
            "matched_expectations": self.matched_expectations,
            "unmatched_expectations": self.unmatched_expectations,
            "violations": self.violations,
            "details": self.details,
            "response_preview": self.response_preview[:300] if self.response_preview else "",
        }


def extract_string_list(value: Any) -> list[str]:
    """Normalizes a string, list, or dict of items into a list of non-empty strings."""
    if value is None:
        return []
    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item.strip())
            elif isinstance(item, dict):
                if "behaviors" in item and isinstance(item["behaviors"], list):
                    result.extend(extract_string_list(item["behaviors"]))
                else:
                    result.append(json.dumps(item))
            elif item is not None:
                result.append(str(item).strip())
        return result
    if isinstance(value, dict):
        result = []
        if "behaviors" in value and isinstance(value["behaviors"], list):
            result.extend(extract_string_list(value["behaviors"]))
        for k, v in value.items():
            if k != "behaviors" and isinstance(v, (str, int, float, bool)):
                result.append(f"{k}: {v}")
        return result
    return [str(value).strip()]


def extract_input_text(raw_case: dict[str, Any]) -> str:
    """Extracts scenario/input text across various schema conventions."""
    for key in ("input", "scenario", "stimulus", "setup", "request", "conversation", "context"):
        val = raw_case.get(key)
        if val is not None:
            if isinstance(val, str):
                return val.strip()
            if isinstance(val, (list, dict)):
                return json.dumps(val)
            return str(val).strip()
    return ""


def normalize_case(suite_name: str, raw_case: dict[str, Any], index: int) -> EvalCase:
    """Normalizes a raw dictionary case into a standardized EvalCase."""
    case_id = (
        raw_case.get("id")
        or raw_case.get("name")
        or f"{suite_name}-{index + 1:03d}"
    )
    if not isinstance(case_id, str):
        case_id = str(case_id)

    name = (
        raw_case.get("name")
        or raw_case.get("title")
        or raw_case.get("id")
        or f"Case {index + 1}"
    )
    if not isinstance(name, str):
        name = str(name)

    input_text = extract_input_text(raw_case)

    # Expectations
    expect_list: list[str] = []
    for key in ("expect", "expected", "must_include", "required_behavior"):
        if key in raw_case:
            expect_list.extend(extract_string_list(raw_case[key]))

    # Rejections / Forbids
    reject_list: list[str] = []
    for key in ("reject", "forbid", "must_not_include"):
        if key in raw_case:
            reject_list.extend(extract_string_list(raw_case[key]))

    expected_status = raw_case.get("expected_status")
    if expected_status is not None:
        expected_status = str(expected_status).strip()

    # Retain non-standard fields as metadata
    standard_keys = {
        "id", "name", "title", "input", "scenario", "stimulus", "setup",
        "request", "conversation", "expect", "expected", "must_include",
        "required_behavior", "reject", "forbid", "must_not_include",
        "expected_status"
    }
    metadata = {k: v for k, v in raw_case.items() if k not in standard_keys}

    return EvalCase(
        suite=suite_name,
        case_id=case_id,
        name=name,
        input=input_text,
        expect=expect_list,
        reject=reject_list,
        expected_status=expected_status,
        metadata=metadata,
        raw=raw_case,
    )


def load_suite(path_or_name: str | Path, evals_dir: Path = EVALS_DIR) -> EvalSuite:
    """Loads an EvalSuite from a directory name or path to cases.yaml."""
    target_path = Path(path_or_name)
    if not target_path.is_file():
        # Treat as suite name under evals_dir
        candidate = evals_dir / path_or_name / "cases.yaml"
        if candidate.is_file():
            target_path = candidate
        else:
            raise FileNotFoundError(f"Evaluation suite not found: {path_or_name} (checked {candidate})")

    suite_name = target_path.parent.name
    with target_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise ValueError(f"{target_path}: expected YAML mapping at root")

    version = data.get("version") or data.get("schema_version")
    if version is not None:
        version = str(version)

    status = data.get("status") or data.get("evaluation_status")
    if status is not None:
        status = str(status)

    criteria = extract_string_list(data.get("criteria", []))

    raw_cases = data.get("cases", [])
    if not isinstance(raw_cases, list):
        raise ValueError(f"{target_path}: 'cases' must be a list")

    cases = [normalize_case(suite_name, c, idx) for idx, c in enumerate(raw_cases) if isinstance(c, dict)]

    return EvalSuite(
        name=suite_name,
        path=target_path,
        version=version,
        status=status,
        criteria=criteria,
        cases=cases,
        raw=data,
    )


def discover_suites(evals_dir: Path = EVALS_DIR) -> list[EvalSuite]:
    """Discovers all evaluation suites with a cases.yaml in evals_dir."""
    suites = []
    if not evals_dir.is_dir():
        return suites

    for yaml_path in sorted(evals_dir.glob("*/cases.yaml")):
        try:
            suites.append(load_suite(yaml_path, evals_dir))
        except Exception as exc:
            print(f"Warning: Failed to load {yaml_path}: {exc}", file=sys.stderr)
    return suites


def verify_case_definition(case: EvalCase) -> list[str]:
    """Verifies that an EvalCase has non-empty id, input, and expectations."""
    issues = []
    if not case.case_id:
        issues.append("missing or empty 'id'/'name'")
    if not case.input:
        issues.append(f"case {case.case_id}: missing or empty input/stimulus/setup")
    if not case.expect and not case.expected_status:
        issues.append(f"case {case.case_id}: has neither expectation criteria nor expected_status")
    return issues


def verify_suite_definitions(suite: EvalSuite) -> tuple[int, int, list[str]]:
    """
    Validates structural validity of all cases in a suite.
    Returns: (valid_cases_count, error_cases_count, list_of_error_messages)
    """
    if not suite.cases:
        return 0, 1, [f"Suite {suite.name}: contains no cases"]

    errors = []
    valid_count = 0
    error_count = 0

    for case in suite.cases:
        case_errors = verify_case_definition(case)
        if case_errors:
            error_count += 1
            errors.extend([f"[{suite.name}:{case.case_id}] {err}" for err in case_errors])
        else:
            valid_count += 1

    return valid_count, error_count, errors


def extract_keywords(text: str) -> set[str]:
    """Extracts informative keywords from an expectation string for semantic matching."""
    tokens = re.findall(r"\b[a-zA-Z0-9_\-]+\b", text.lower())
    return {tok for tok in tokens if tok not in COMMON_STOPWORDS and len(tok) > 2}


def evaluate_case(case: EvalCase, response: str | dict[str, Any], keyword_threshold: float = 0.4) -> CaseResult:
    """
    Evaluates a candidate response against an EvalCase's expectations and rejections.

    - If response is a dict, it is searched as both structured keys/values and serialized JSON.
    - Matches expectations via keyword overlap and direct phrase occurrences.
    - Detects violations if reject criteria patterns or key phrases appear asserting forbidden behavior.
    """
    if isinstance(response, dict):
        response_str = json.dumps(response, indent=2)
        response_lower = response_str.lower()
    else:
        response_str = str(response)
        response_lower = response_str.lower()

    matched_expectations: list[str] = []
    unmatched_expectations: list[str] = []
    violations: list[str] = []

    # Check status if expected_status is declared (e.g. PASS, FIX, etc.)
    if case.expected_status and isinstance(response, dict):
        actual_status = response.get("status") or response.get("expected_status") or response.get("decision")
        if actual_status and str(actual_status).upper() != case.expected_status.upper():
            unmatched_expectations.append(f"expected status '{case.expected_status}', got '{actual_status}'")

    # Evaluate expectations
    for exp in case.expect:
        exp_lower = exp.lower().strip()
        # Direct phrase match or pattern match
        if exp_lower in response_lower:
            matched_expectations.append(exp)
            continue

        # Keyword token overlap
        exp_keywords = extract_keywords(exp)
        if not exp_keywords:
            matched_expectations.append(exp)
            continue

        resp_tokens = extract_keywords(response_lower)
        overlap = exp_keywords.intersection(resp_tokens)
        overlap_ratio = len(overlap) / len(exp_keywords)

        if overlap_ratio >= keyword_threshold or len(overlap) >= 3:
            matched_expectations.append(exp)
        else:
            unmatched_expectations.append(exp)

    # Evaluate rejections (forbid / reject)
    for rej in case.reject:
        rej_lower = rej.lower().strip()
        rej_keywords = extract_keywords(rej)
        if not rej_keywords:
            continue

        # If direct phrase is found in response
        if rej_lower in response_lower:
            violations.append(f"Contains forbidden phrase: '{rej}'")
            continue

        # Check for strong keyword cluster presence (>= 75% overlap of forbidden phrase)
        resp_tokens = extract_keywords(response_lower)
        overlap = rej_keywords.intersection(resp_tokens)
        if len(rej_keywords) >= 3 and (len(overlap) / len(rej_keywords)) >= 0.75:
            violations.append(f"Violates rejection criterion: '{rej}' (detected overlap: {', '.join(sorted(overlap))})")

    passed = (len(violations) == 0) and (len(unmatched_expectations) == 0)
    status = "PASS" if passed else "FAIL"

    details_parts = []
    if unmatched_expectations:
        details_parts.append(f"Unmatched expectations: {len(unmatched_expectations)}/{len(case.expect)}")
    if violations:
        details_parts.append(f"Violations: {len(violations)}")
    if passed:
        details_parts.append(f"All {len(case.expect)} expectations satisfied")

    details = "; ".join(details_parts)

    return CaseResult(
        suite=case.suite,
        case_id=case.case_id,
        name=case.name,
        passed=passed,
        status=status,
        matched_expectations=matched_expectations,
        unmatched_expectations=unmatched_expectations,
        violations=violations,
        details=details,
        response_preview=response_str,
    )


def load_responses(path: Path) -> dict[str, Any]:
    """Loads response mapping from a JSON or YAML file."""
    if not path.is_file():
        raise FileNotFoundError(f"Responses file not found: {path}")

    with path.open("r", encoding="utf-8") as handle:
        if path.suffix in (".yaml", ".yml"):
            data = yaml.safe_load(handle)
        else:
            data = json.load(handle)

    if isinstance(data, list):
        # Format: [{"id": "...", "response": "..."}, ...]
        mapping = {}
        for entry in data:
            if isinstance(entry, dict):
                cid = entry.get("id") or entry.get("name") or entry.get("case_id")
                resp = entry.get("response") or entry.get("output") or entry
                if cid:
                    mapping[str(cid)] = resp
        return mapping

    if isinstance(data, dict):
        # Format: {"case_id": "response", ...}
        # Or nested under "cases" / "responses"
        if "cases" in data and isinstance(data["cases"], list):
            mapping = {}
            for entry in data["cases"]:
                if isinstance(entry, dict):
                    cid = entry.get("id") or entry.get("name") or entry.get("case_id")
                    resp = entry.get("response") or entry.get("output") or entry
                    if cid:
                        mapping[str(cid)] = resp
            return mapping
        return data

    raise ValueError(f"Invalid format in responses file: {path}")


def run_suite(
    suite: EvalSuite,
    case_filter: str | None = None,
    responses: dict[str, Any] | None = None,
    verify_only: bool = False,
    verbose: bool = False,
) -> list[CaseResult]:
    """Runs verification or execution for a single suite."""
    results: list[CaseResult] = []

    for case in suite.cases:
        if case_filter and case_filter not in (case.case_id, case.name):
            continue

        if verify_only or responses is None:
            # Definition verification mode
            errors = verify_case_definition(case)
            passed = len(errors) == 0
            res = CaseResult(
                suite=suite.name,
                case_id=case.case_id,
                name=case.name,
                passed=passed,
                status="PASS" if passed else "FAIL",
                details="Definition valid" if passed else "; ".join(errors),
                unmatched_expectations=errors,
            )
        else:
            # Response evaluation mode
            resp = responses.get(case.case_id) or responses.get(case.name)
            if resp is None:
                res = CaseResult(
                    suite=suite.name,
                    case_id=case.case_id,
                    name=case.name,
                    passed=False,
                    status="SKIPPED",
                    details=f"No response provided for case {case.case_id}",
                )
            else:
                res = evaluate_case(case, resp)

        results.append(res)

    return results


def format_summary_report(results: list[CaseResult]) -> tuple[str, dict[str, Any]]:
    """Formats human-readable summary and structured dict."""
    total = len(results)
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    skipped = sum(1 for r in results if r.status == "SKIPPED")

    overall_status = "PASS" if (failed == 0 and total > 0) else "FAIL"

    lines = [
        "=" * 68,
        "Behavioral Evaluation Summary",
        "=" * 68,
    ]

    # Group by suite
    by_suite: dict[str, list[CaseResult]] = {}
    for r in results:
        by_suite.setdefault(r.suite, []).append(r)

    for suite_name, suite_results in by_suite.items():
        s_total = len(suite_results)
        s_pass = sum(1 for r in suite_results if r.status == "PASS")
        s_fail = sum(1 for r in suite_results if r.status == "FAIL")
        s_skip = sum(1 for r in suite_results if r.status == "SKIPPED")
        lines.append(f"Suite: {suite_name:<24} | Total: {s_total:<3} | Pass: {s_pass:<3} | Fail: {s_fail:<3} | Skip: {s_skip}")

        for r in suite_results:
            if r.status == "FAIL":
                lines.append(f"  [FAIL] {r.case_id}: {r.details}")
                if r.violations:
                    for v in r.violations:
                        lines.append(f"         ! {v}")
                if r.unmatched_expectations:
                    for u in r.unmatched_expectations:
                        lines.append(f"         - Missing: {u}")
            elif r.status == "SKIPPED":
                lines.append(f"  [SKIP] {r.case_id}: {r.details}")

    lines.append("-" * 68)
    lines.append(f"Overall: {total} cases | {passed} passed | {failed} failed | {skipped} skipped")
    lines.append(f"Verdict: {overall_status}")
    lines.append("=" * 68)

    structured = {
        "verdict": overall_status,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "results": [r.to_dict() for r in results],
    }

    return "\n".join(lines), structured


def parse_arguments(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Behavioral Evaluation Runner for Agent Toolkit"
    )
    parser.add_argument(
        "--eval",
        dest="eval_target",
        help="Name of the eval suite to run (e.g. app-check, product-reality, security-audit)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run across all evaluation suites in evals/",
    )
    parser.add_argument(
        "--case",
        dest="case_filter",
        help="Filter to a specific case ID or name",
    )
    parser.add_argument(
        "--verify-definitions",
        action="store_true",
        help="Verify structural validity of scenario definitions (no responses required)",
    )
    parser.add_argument(
        "--responses",
        type=Path,
        help="Path to JSON/YAML file containing candidate responses to evaluate",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Path to write the structured evaluation ledger (JSON)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON result directly to stdout",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose details of evaluation",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_arguments(argv)

    # 1. Determine targets
    if args.all:
        suites = discover_suites(EVALS_DIR)
        if not suites:
            print("No evaluation suites discovered in evals/", file=sys.stderr)
            return 1
    elif args.eval_target:
        try:
            suites = [load_suite(args.eval_target, EVALS_DIR)]
        except Exception as exc:
            print(f"Error loading eval suite '{args.eval_target}': {exc}", file=sys.stderr)
            return 1
    else:
        # Default behavior: if no target specified, verify all definitions
        suites = discover_suites(EVALS_DIR)
        args.verify_definitions = True

    # 2. Load responses if provided
    responses = None
    if args.responses:
        try:
            responses = load_responses(args.responses)
        except Exception as exc:
            print(f"Error loading responses from {args.responses}: {exc}", file=sys.stderr)
            return 1

    # 3. Execute
    all_results: list[CaseResult] = []
    verify_only = args.verify_definitions or (responses is None)

    for suite in suites:
        suite_results = run_suite(
            suite=suite,
            case_filter=args.case_filter,
            responses=responses,
            verify_only=verify_only,
            verbose=args.verbose,
        )
        all_results.extend(suite_results)

    # 4. Reporting
    report_text, structured_data = format_summary_report(all_results)

    if args.json:
        print(json.dumps(structured_data, indent=2))
    else:
        print(report_text)

    if args.output:
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(structured_data, indent=2), encoding="utf-8")
            if not args.json:
                print(f"Evaluation report written to {args.output}")
        except Exception as exc:
            print(f"Error writing output to {args.output}: {exc}", file=sys.stderr)
            return 1

    return 0 if structured_data["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
