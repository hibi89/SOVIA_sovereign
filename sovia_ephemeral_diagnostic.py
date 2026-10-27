"""SOVIA offline read-only aggregate diagnosis without publishing report files.

This is an opt-in, source-only canonical JSON CLI, not the old portable ZIP.
It does not create application reports, databases, temporary files or sockets.
Shell redirection, OS logging, page files and the user's environment are outside
this utility's control: never promise forensic non-retention.
"""
from __future__ import annotations

import argparse
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

SCHEMA = "sovia.ephemeral_diagnostic.v1"
RULE_IDS = frozenset({
    "UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION", "SENSITIVE_ACCESS",
    "BURST_TOOLS", "MISSING_EVIDENCE",
})
SEVERITIES = frozenset({"HIGH", "MEDIUM", "LOW"})


class DiagnosticError(ValueError):
    """Fixed diagnostic error codes only: never include input data or paths."""


def _audit():
    source = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_ephemeral_audit", source)
    if spec is None or spec.loader is None:
        raise DiagnosticError("LOCAL_AUDIT_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise DiagnosticError("LOCAL_AUDIT_UNAVAILABLE") from exc
    return module


def summarize(report):
    """Aggregate only allowlisted rule labels and severities, never event text."""
    if type(report) is not dict:
        raise DiagnosticError("INVALID_REPORT")
    try:
        events = report["events"]
        findings = report["findings"]
        limits = report["coverage_limits"]
        if (type(events) is not list or type(findings) is not list or
                type(limits) is not list or type(report["event_count"]) is not int or
                type(report["finding_count"]) is not int or
                report["event_count"] != len(events) or
                report["finding_count"] != len(findings)):
            raise DiagnosticError("INVALID_REPORT")
        counts = Counter()
        grades = Counter()
        for item in findings:
            if type(item) is not dict:
                raise DiagnosticError("INVALID_REPORT")
            rule = item["rule_id"]
            grade = item["severity"]
            if type(rule) is not str or rule not in RULE_IDS or (
                    type(grade) is not str or grade not in SEVERITIES):
                raise DiagnosticError("UNSUPPORTED_FINDING_LABEL")
            counts[rule] += 1
            grades[grade] += 1
        if any(type(item) is not str for item in limits):
            raise DiagnosticError("INVALID_REPORT")
    except (KeyError, TypeError, ValueError) as exc:
        if isinstance(exc, DiagnosticError):
            raise
        raise DiagnosticError("INVALID_REPORT") from exc
    return {
        "schema": SCHEMA,
        "status": "AGGREGATE_LOCAL_DIAGNOSIS_ONLY",
        "events": report["event_count"],
        "findings": report["finding_count"],
        "rules": {key: counts[key] for key in sorted(RULE_IDS) if counts[key]},
        "severities": {key: grades[key] for key in sorted(SEVERITIES) if grades[key]},
        "risk_findings_observed": bool(findings),
        "coverage_limit_count": len(limits),
        "coverage_not_certified": True,
        "event_details_exported": False,
        "application_output_files_created": False,
        "source_authorization_independently_verified": False,
        "persistent_os_or_shell_logs_ruled_out": False,
    }


def diagnose(path):
    try:
        source = Path(path)
        if source.is_symlink() or source.suffix.lower() != ".json" or not source.is_file():
            raise DiagnosticError("INVALID_LOCAL_JSON_SOURCE")
    except (OSError, ValueError, TypeError) as exc:
        if isinstance(exc, DiagnosticError):
            raise
        raise DiagnosticError("INVALID_LOCAL_JSON_SOURCE") from exc
    audit = _audit()
    try:
        report = audit.evaluate(audit.read_document(source))
    except (audit.AuditInputError, OSError, ValueError, TypeError,
            OverflowError, RecursionError) as exc:
        raise DiagnosticError("INVALID_AUDIT_INPUT") from exc
    return summarize(report)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Read-only aggregate risk diagnosis; prints counts, not event data")
    parser.add_argument("--input", required=True, help="local authorized sanitized JSON source")
    parser.add_argument("--ack-sanitized-source", action="store_true",
                        help="explicitly acknowledge that input is sanitized and authorized")
    args = parser.parse_args(argv)
    if not args.ack_sanitized_source:
        print(json.dumps({"status": "REJECTED", "error_code": "SOURCE_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        result = diagnose(args.input)
    except DiagnosticError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        print(json.dumps({"status": "REJECTED", "error_code": "DIAGNOSIS_REJECTED"}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
