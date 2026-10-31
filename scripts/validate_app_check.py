import argparse
import json
import sys
from pathlib import Path

STATUSES = {"SUFFICIENT", "LIMITED", "BLOCKED"}
VERIFICATION = {"INDEPENDENT", "SELF_CHECKED", "NOT_VERIFIED"}
FINDING_STATUSES = {"CONFIRMED_DEFECT", "SUPPORTED_RISK", "HYPOTHESIS", "OPPORTUNITY"}
PRIORITIES = {"P0", "P1", "P2", "P3", "UNRATED"}
DECISIONS = {"NOW", "NEXT", "DEFER", "NO_CHANGE"}
ACTION_KINDS = {"FIX", "DIAGNOSE", "MONITOR", "NONE"}
EVIDENCE_KINDS = {"OBSERVED_SOURCE", "EXECUTED_CHECK", "RUNTIME_MEASUREMENT", "USER_REPORTED", "INFERENCE"}
MEASUREMENT_STATUSES = {"MEASURED", "FORECAST_WITH_BASIS", "HYPOTHETICAL", "UNKNOWN"}
APPLICABILITY = {"APPLICABLE", "CONDITIONAL", "NOT_APPLICABLE"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate(document):
    errors = []

    def reject(path, reason):
        errors.append(f"{path}: {reason}")

    if not isinstance(document, dict):
        return ["root: expected a JSON object"]
    if document.get("schema") != "app-check-report-v1":
        reject("schema", "expected app-check-report-v1")

    assessment = document.get("assessment")
    if not isinstance(assessment, dict):
        return errors + ["assessment: expected an object"]
    if assessment.get("status") not in STATUSES:
        reject("assessment.status", "invalid assessment status")
    if assessment.get("verification") not in VERIFICATION:
        reject("assessment.verification", "invalid verification status")
    if not nonempty(assessment.get("scope")):
        reject("assessment.scope", "nonempty assessed scope required")
    if assessment.get("no_code_changes") is not True:
        reject("assessment.no_code_changes", "assessment must be read-only")
    inspected = assessment.get("inspected_sources", [])
    if not isinstance(inspected, list) or not all(nonempty(x) for x in inspected):
        reject("assessment.inspected_sources", "must be a list of source identifiers")
        inspected = []
    if assessment.get("status") == "SUFFICIENT" and not inspected:
        reject("assessment.status", "SUFFICIENT requires an inspected source")
    if assessment.get("verification") == "INDEPENDENT":
        agents = assessment.get("independent_context_ids", [])
        if not isinstance(agents, list) or not agents or not all(nonempty(x) for x in agents):
            reject("assessment.independent_context_ids", "independent review requires context identifiers")

    applicability = document.get("applicability", [])
    if not isinstance(applicability, list):
        reject("applicability", "expected a list")
        applicability = []
    seen_areas = set()
    for i, entry in enumerate(applicability):
        path = f"applicability[{i}]"
        if not isinstance(entry, dict):
            reject(path, "expected object")
            continue
        if not nonempty(entry.get("area")):
            reject(path + ".area", "area required")
        elif entry["area"] in seen_areas:
            reject(path + ".area", "duplicate area")
        else:
            seen_areas.add(entry["area"])
        if entry.get("status") not in APPLICABILITY:
            reject(path + ".status", "invalid applicability")
        if not nonempty(entry.get("reason")):
            reject(path + ".reason", "relevance decision requires explanation")

    questions = document.get("questions", [])
    if not isinstance(questions, list):
        reject("questions", "expected a list")
        questions = []
    if len(questions) > 8:
        reject("questions", "more than eight questions")
    for i, question in enumerate(questions):
        path = f"questions[{i}]"
        if not isinstance(question, dict) or not nonempty(question.get("text")) or not nonempty(question.get("decision_affected")):
            reject(path, "question and affected decision are required")

    measurements = document.get("measurements", [])
    if not isinstance(measurements, list):
        reject("measurements", "expected a list")
        measurements = []
    for i, item in enumerate(measurements):
        path = f"measurements[{i}]"
        if not isinstance(item, dict):
            reject(path, "expected object")
            continue
        status = item.get("status")
        if status not in MEASUREMENT_STATUSES:
            reject(path + ".status", "invalid measurement status")
        if not nonempty(item.get("name")):
            reject(path + ".name", "metric name required")
        if status in {"MEASURED", "FORECAST_WITH_BASIS"} and not nonempty(item.get("provenance")):
            reject(path + ".provenance", "measured or forecast numbers require provenance")
        if status == "MEASURED" and not nonempty(item.get("environment")):
            reject(path + ".environment", "measurement environment required")
        if status == "MEASURED" and not nonempty(item.get("window")):
            reject(path + ".window", "measurement window required")
        if status == "UNKNOWN" and item.get("value") not in (None, "NOT_MEASURED"):
            reject(path + ".value", "unknown metrics cannot declare a value")

    findings = document.get("findings", [])
    if not isinstance(findings, list):
        reject("findings", "expected a list")
        findings = []
    ids = set()
    for i, finding in enumerate(findings):
        path = f"findings[{i}]"
        if not isinstance(finding, dict):
            reject(path, "expected object")
            continue
        identifier = finding.get("id")
        if not nonempty(identifier) or identifier in ids:
            reject(path + ".id", "unique nonempty finding ID required")
        else:
            ids.add(identifier)
        if finding.get("status") not in FINDING_STATUSES:
            reject(path + ".status", "invalid finding status")
        if finding.get("priority") not in PRIORITIES:
            reject(path + ".priority", "invalid priority")
        if not nonempty(finding.get("affected_behavior")):
            reject(path + ".affected_behavior", "specific affected behavior required")
        if not nonempty(finding.get("applicability_reason")):
            reject(path + ".applicability_reason", "application relevance required")
        evidence = finding.get("evidence", [])
        if not isinstance(evidence, list) or not evidence:
            reject(path + ".evidence", "at least one evidence record required")
            evidence = []
        kinds = set()
        for j, item in enumerate(evidence):
            epath = f"{path}.evidence[{j}]"
            if not isinstance(item, dict):
                reject(epath, "expected object")
                continue
            kind = item.get("kind")
            if kind not in EVIDENCE_KINDS:
                reject(epath + ".kind", "invalid evidence kind")
            kinds.add(kind)
            if not nonempty(item.get("locator")):
                reject(epath + ".locator", "exact source or artifact location required")
            if not nonempty(item.get("provenance")):
                reject(epath + ".provenance", "origin and context required")
        if finding.get("priority") == "P0":
            if finding.get("status") != "CONFIRMED_DEFECT":
                reject(path + ".priority", "P0 requires a confirmed defect")
            if not kinds.intersection({"OBSERVED_SOURCE", "EXECUTED_CHECK", "RUNTIME_MEASUREMENT"}):
                reject(path + ".priority", "P0 requires direct evidence")
        if finding.get("topic") == "memory_leak" and finding.get("status") == "CONFIRMED_DEFECT":
            if not kinds.intersection({"EXECUTED_CHECK", "RUNTIME_MEASUREMENT"}):
                reject(path + ".topic", "confirmed memory leak requires diagnostic evidence")
        recommendation = finding.get("recommendation")
        if not isinstance(recommendation, dict):
            reject(path + ".recommendation", "expected recommendation object")
            continue
        if recommendation.get("decision") not in DECISIONS:
            reject(path + ".recommendation.decision", "invalid decision")
        if recommendation.get("action_kind") not in ACTION_KINDS:
            reject(path + ".recommendation.action_kind", "invalid action kind")
        if not nonempty(recommendation.get("rationale")):
            reject(path + ".recommendation.rationale", "decision rationale required")
        if recommendation.get("decision") == "NO_CHANGE" and recommendation.get("action_kind") != "NONE":
            reject(path + ".recommendation", "NO_CHANGE requires NONE action")
        if finding.get("status") in {"HYPOTHESIS", "OPPORTUNITY"} and recommendation.get("decision") == "NOW" and recommendation.get("action_kind") == "FIX":
            reject(path + ".recommendation", "hypothesis/opportunity cannot mandate an immediate fix")
        if recommendation.get("action_kind") in {"FIX", "DIAGNOSE", "MONITOR"} and not nonempty(recommendation.get("verification")):
            reject(path + ".recommendation.verification", "action requires success or diagnostic evidence")

    decisions = document.get("top_actions", [])
    if not isinstance(decisions, list):
        reject("top_actions", "expected list")
        decisions = []
    if len(decisions) > 5:
        reject("top_actions", "more than five top actions; place additional findings in details")
    for i, entry in enumerate(decisions):
        path = f"top_actions[{i}]"
        if not isinstance(entry, dict) or entry.get("finding_id") not in ids:
            reject(path, "top action must reference a recorded finding")
        elif entry.get("decision") not in DECISIONS:
            reject(path + ".decision", "invalid decision")
        else:
            finding = next((x for x in findings if isinstance(x, dict) and x.get("id") == entry["finding_id"]), {})
            if entry.get("decision") != finding.get("recommendation", {}).get("decision"):
                reject(path + ".decision", "top action contradicts finding recommendation")
    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate the structure of a read-only app-check evidence record")
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        data = json.loads(args.report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid input: {exc}", file=sys.stderr)
        return 2
    errors = validate(data)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("STRUCTURE_VALID: evidence assertions require independent source verification")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
