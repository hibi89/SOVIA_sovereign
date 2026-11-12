"""SOVIA P38: compare two verified *synthetic* LA owner review bundles.

A strictly aggregate read-only diff. Historical ordering is operator supplied;
manifest hashes are not signatures and neither input proves real LA events.
No source rows, rule identifiers, targets or event/step identifiers are emitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

from importlib.util import module_from_spec, spec_from_file_location


def _load_local_review():
    # python -I intentionally omits the script directory from sys.path.
    # Use the established SOVIA explicit local file loader, not sys.path hacks.
    source = Path(__file__).resolve().with_name("sovia_la_owner_review.py")
    spec = spec_from_file_location("_sovia_delta_review", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("SOVIA_REVIEW_COMPONENT_MISSING")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_review = _load_local_review()
FILES, MAX_FILE, ReviewError = _review.FILES, _review.MAX_FILE, _review.ReviewError
_parse_json = _review._parse_json
_require_review_structure = _review._require_review_structure
_safe_path, verify_bundle = _review._safe_path, _review.verify_bundle

SCHEMA = "sovia.la_review_delta.v1"
SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN")
GROUPS = ("plan_risk_findings", "post_audit_findings", "reconciliation_findings")


def _load_checked(path: str | Path):
    root = _safe_path(path)
    verify_bundle(root)
    sources = {}
    for name in FILES:
        file = _safe_path(root / name, expect_file=True)
        with file.open("rb") as reader:
            raw = reader.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            raise ReviewError("REPORT_TOO_LARGE")
        sources[name] = raw
    review = _require_review_structure(_parse_json(sources["review.json"]))
    if any(row["severity"] not in SEVERITIES
           for group in GROUPS for row in review[group]):
        raise ReviewError("UNSUPPORTED_SEVERITY")
    verify_bundle(root)
    # Re-read exact bytes to identify a simple concurrent replacement.
    for name in FILES:
        if _safe_path(root / name, expect_file=True).read_bytes() != sources[name]:
            raise ReviewError("INPUT_CHANGED_DURING_COMPARE")
    return review, hashlib.sha256(sources["review.json"]).hexdigest()


def compare_review_bundles(previous: str | Path, current: str | Path) -> dict:
    """No output file, network access, authentication assertion or execution."""
    before_path = _safe_path(previous)
    after_path = _safe_path(current)
    if before_path == after_path:
        raise ReviewError("SAME_REVIEW_DIRECTORY")
    before, bsha = _load_checked(before_path)
    after, asha = _load_checked(after_path)

    groups = {}
    increases = 0
    for group in GROUPS:
        baseline = Counter(item["severity"] for item in before[group])
        observed = Counter(item["severity"] for item in after[group])
        changes = {}
        for severity in SEVERITIES:
            old, new = baseline[severity], observed[severity]
            changes[severity] = {"previous": old, "current": new,
                                 "change": new - old}
            increases += max(0, new - old)
        groups[group.removesuffix("_findings")] = changes
    result = {
        "schema_version": SCHEMA,
        "status": "REVIEW_REQUIRED_UNAUTHENTICATED",
        "ordering": "CALLER_ASSERTED_PREVIOUS_TO_CURRENT",
        "previous_review_sha256": bsha,
        "current_review_sha256": asha,
        "same_report": bsha == asha,
        "plan_steps_change": after["planned_steps"] - before["planned_steps"],
        "observation_count_change": after["observed_events"] - before["observed_events"],
        "severity_counts": groups,
        "severity_increases": increases,
        "risk_clearance_verified": False,
        "real_la_integration_verified": False,
        "source_authenticity_verified": False,
        "execution_authorized": False,
        "policy": "SYNTHETIC_ONLY;READ_ONLY;NO_RAW_IDS;NO_REMOTE;NO_SAFETY_CLEARANCE",
        "coverage_limits": [
            "BOTH_REPORTS_UNSIGNED_AND_SOURCE_UNAUTHENTICATED",
            "CALLER_ORDER_NOT_PROVEN_CHRONOLOGICAL",
            "COUNT_DECREASE_IS_NOT_PROOF_OF_SAFETY_OR_MISSING_EVENTS",
            "DIFFERENT_DATA_SCOPE_OR_POLICY_CAN_CHANGE_COUNTS",
        ],
    }
    # Compare exact input bytes again before publishing summary.
    for folder, fingerprint in ((before_path, bsha), (after_path, asha)):
        check, checksha = _load_checked(folder)
        if checksha != fingerprint:
            raise ReviewError("INPUT_CHANGED_DURING_COMPARE")
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA signed-by-nobody synthetic review delta")
    p.add_argument("--previous", required=True)
    p.add_argument("--current", required=True)
    p.add_argument("--synthetic-only", action="store_true",
                   help="acknowledge both inputs are synthetic review bundles")
    args = p.parse_args(argv)
    try:
        if not args.synthetic_only:
            raise ReviewError("SYNTHETIC_ACK_REQUIRED")
        result = compare_review_bundles(args.previous, args.current)
    except (ReviewError, OSError, UnicodeError, ValueError, TypeError) as exc:
        code = str(exc) if isinstance(exc, ReviewError) else "DELTA_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
