"""Synthetic-only privacy pattern triage. Emits aggregate confusion counts only.

This test harness is NOT a de-identification tool, suppression list,
statistical quality estimate for live users, or authorization workflow.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

SCHEMA = "sovia.privacy_triage.v1"
MAX_CASES = 100
MAX_SPECIMEN_CHARS = 256
CASE_ID = re.compile(r"^[a-z][a-z0-9_-]{0,39}$")


class TriageError(ValueError):
    """Fixed non-disclosing diagnostic errors."""


def _sibling(module):
    path = Path(__file__).resolve().with_name(module + ".py")
    spec = spec_from_file_location("_sovia_triage_" + module, path)
    if spec is None or spec.loader is None:
        raise TriageError("TRIAGE_DEPENDENCY_UNAVAILABLE")
    target = module_from_spec(spec)
    try:
        spec.loader.exec_module(target)
    except (ImportError, OSError) as exc:
        raise TriageError("TRIAGE_DEPENDENCY_UNAVAILABLE") from exc
    return target


def score_suite(document, *, checker=None):
    """Return only counts, never specimens, IDs or inferred private properties."""
    if (type(document) is not dict or set(document) !=
            {"schema_version", "synthetic_only", "cases"} or
            document["schema_version"] != SCHEMA or
            document["synthetic_only"] is not True):
        raise TriageError("TRIAGE_INVALID_ENVELOPE")
    rows = document["cases"]
    if type(rows) is not list or not 1 <= len(rows) <= MAX_CASES:
        raise TriageError("TRIAGE_INVALID_CASES")
    preflight = _sibling("sovia_pii_preflight") if checker is None else checker
    tp = tn = fp = fn = 0
    seen = set()
    for case in rows:
        if type(case) is not dict or set(case) != {"case_id", "specimen", "expected_reject"}:
            raise TriageError("TRIAGE_INVALID_CASE_FIELDS")
        label, specimen, expected = case["case_id"], case["specimen"], case["expected_reject"]
        if (type(label) is not str or CASE_ID.fullmatch(label) is None or
                label in seen):
            raise TriageError("TRIAGE_INVALID_CASE_ID")
        seen.add(label)
        if (type(specimen) is not str or not 1 <= len(specimen) <= MAX_SPECIMEN_CHARS or
                type(expected) is not bool):
            raise TriageError("TRIAGE_INVALID_CASE_VALUE")
        try:
            preflight.assert_no_high_risk_patterns({"specimen": specimen})
        except preflight.PreflightError as exc:
            if str(exc) != "PREFLIGHT_SUSPECT_METADATA":
                raise TriageError("TRIAGE_CHECKER_REFUSED_INPUT") from exc
            actual = True
        else:
            actual = False
        if actual and expected:
            tp += 1
        elif not actual and not expected:
            tn += 1
        elif actual:
            fp += 1
        else:
            fn += 1
    return {
        "status": "REVIEW_REQUIRED" if fp or fn else "SYNTHETIC_SUITE_MATCHED",
        "total_cases": len(rows),
        "true_positives": tp,
        "true_negatives": tn,
        "false_positives": fp,
        "false_negatives": fn,
        "suppression_applied": False,
        "privacy_absence_proven": False,
        "representative_population_validated": False,
    }


def score_file(path):
    # Reuse the existing bounded JSON reader (duplicate-key and size guards).
    audit = _sibling("sovia_n8n_sanitized")._audit()
    try:
        document = audit.read_document(path)
        return score_suite(document)
    except TriageError:
        raise
    except (ValueError, OSError, TypeError, OverflowError, RecursionError) as exc:
        raise TriageError("TRIAGE_INPUT_REJECTED") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Offline synthetic-only aggregate privacy triage; no user data"
    )
    parser.add_argument("--input", required=True, help="Bounded synthetic test JSON")
    parser.add_argument("--synthetic-only", action="store_true", required=False)
    args = parser.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED",
                          "error_code": "TRIAGE_SYNTHETIC_ONLY_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        result = score_file(args.input)
    except TriageError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 3 if result["status"] == "REVIEW_REQUIRED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
