"""Read-only, offline consistency checks for owner Windows synthetic beta evidence.

A self-check JSON or manual checklist can be forged. Even a consistent result
does NOT authenticate the owner, prove device execution, or approve a release.
No customer files and no sensitive paths/details in standard output.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

EXPECTED_INNER_ZIP_SHA256 = "894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b"
MAX_ZIP_BYTES = 32 * 1024 * 1024
REVIEW_SCHEMA = "sovia.owner_windows_review.v1"
REQUIRED_AUTOCHECKS = (
    "python", "package_integrity", "audit", "sqlite", "dashboard", "recovery"
)
REQUIRED_MANUAL_CHECKS = (
    "audit_html_visual", "dashboard_html_visual", "antivirus_or_smartscreen"
)
OPTIONAL_PDF_OUTCOMES = frozenset({
    "GENERATED_NEEDS_VISUAL_REVIEW", "SKIPPED_REPORTLAB_MISSING",
    "SKIPPED_KOREAN_TTF_MISSING", "FAILED_OPTIONAL_PDF",
})
ALLOWED_REVIEW_STATES = frozenset({"PASS", "FAIL", "NOT_CHECKED"})
MANUAL_KEYS = frozenset((*REQUIRED_MANUAL_CHECKS, "korean_pdf_visual"))


class EvidenceError(ValueError):
    """Only constant status codes, never raw paths / machine information."""


def _audit():
    local = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_owner_evidence_audit", local)
    if spec is None or spec.loader is None:
        raise EvidenceError("EVIDENCE_READER_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise EvidenceError("EVIDENCE_READER_UNAVAILABLE") from exc
    return module


def hash_expected_portable(path):
    target = Path(path)
    if target.is_symlink() or not target.is_file():
        raise EvidenceError("PORTABLE_FILE_UNAVAILABLE")
    try:
        if target.stat().st_size > MAX_ZIP_BYTES:
            raise EvidenceError("PORTABLE_SIZE_EXCEEDED")
        digest = hashlib.sha256()
        with target.open("rb") as f:
            while True:
                chunk = f.read(65536)
                if not chunk:
                    break
                digest.update(chunk)
        if digest.hexdigest() != EXPECTED_INNER_ZIP_SHA256:
            raise EvidenceError("PORTABLE_HASH_MISMATCH")
    except OSError as exc:
        raise EvidenceError("PORTABLE_FILE_UNAVAILABLE") from exc
    return True


def _validate_selfcheck(doc):
    if (type(doc) is not dict or set(doc) != {
        "schema_version", "version", "purpose", "status", "system",
        "checks", "synthetic", "manual_acceptance", "error_code",
    } or doc["schema_version"] != "1.0" or
        doc["version"] != "0.10.0-beta" or
        doc["purpose"] != "SYNTHETIC_ONLY_NO_CUSTOMER_DATA" or
        doc["status"] != "AUTOMATED_PASS_MANUAL_PENDING" or
        doc["error_code"] is not None):
        raise EvidenceError("SELFCHECK_INVALID_ENVELOPE")
    machine = doc["system"]
    if (type(machine) is not dict or set(machine) !=
        {"os", "os_release", "python"} or machine["os"] != "Windows" or
        type(machine["python"]) is not str or
        re.fullmatch(r"\d+\.\d+\.\d+", machine["python"]) is None):
        raise EvidenceError("SELFCHECK_NOT_WINDOWS")
    try:
        version = tuple(int(x) for x in machine["python"].split("."))
    except ValueError as exc:
        raise EvidenceError("SELFCHECK_NOT_WINDOWS") from exc
    if version < (3, 11):
        raise EvidenceError("SELFCHECK_UNSUPPORTED_PYTHON")
    checks = doc["checks"]
    if (type(checks) is not dict or set(checks) !=
        set(REQUIRED_AUTOCHECKS) | {"optional_pdf"} or
        any(checks[k] != "PASS" for k in REQUIRED_AUTOCHECKS) or
        checks["optional_pdf"] not in OPTIONAL_PDF_OUTCOMES):
        raise EvidenceError("SELFCHECK_AUTOMATION_INCOMPLETE")
    if (type(doc["synthetic"]) is not dict or doc["synthetic"] !=
        {"events": 3, "findings": 5, "reports": 1}):
        raise EvidenceError("SELFCHECK_SYNTHETIC_COUNTS_MISMATCH")
    legacy = doc["manual_acceptance"]
    if (type(legacy) is not dict or set(legacy) != {
        "audit_html_visual", "dashboard_html_visual", "korean_pdf_visual",
        "antivirus_or_smartscreen", "owner_device_commercial_approval"
    } or any(value != "NOT_CHECKED" for value in legacy.values())):
        raise EvidenceError("SELFCHECK_MANUAL_FIELDS_TAMPERED")
    return checks["optional_pdf"]


def _validate_review(doc, pdf_status):
    if (type(doc) is not dict or set(doc) != {"schema_version", "manual_checks"} or
        doc["schema_version"] != REVIEW_SCHEMA):
        raise EvidenceError("REVIEW_INVALID_ENVELOPE")
    checks = doc["manual_checks"]
    if type(checks) is not dict or set(checks) != MANUAL_KEYS:
        raise EvidenceError("REVIEW_INVALID_FIELDS")
    if any(type(value) is not str or value not in
           ALLOWED_REVIEW_STATES | {"NOT_TESTED"} for value in checks.values()):
        raise EvidenceError("REVIEW_INVALID_STATE")
    if any(checks[k] == "NOT_TESTED" for k in REQUIRED_MANUAL_CHECKS):
        raise EvidenceError("REVIEW_INVALID_STATE")
    pdf = checks["korean_pdf_visual"]
    if pdf == "PASS" and pdf_status != "GENERATED_NEEDS_VISUAL_REVIEW":
        raise EvidenceError("PDF_CLAIM_CONTRADICTS_AUTOCHECK")
    if pdf_status == "FAILED_OPTIONAL_PDF" and pdf == "PASS":
        raise EvidenceError("PDF_CLAIM_CONTRADICTS_AUTOCHECK")
    return checks


def assess(automated, manual):
    pdf = _validate_selfcheck(automated)
    review = _validate_review(manual, pdf)
    if (any(review[k] == "FAIL" for k in REQUIRED_MANUAL_CHECKS) or
            review["korean_pdf_visual"] == "FAIL" or
            pdf == "FAILED_OPTIONAL_PDF"):
        state = "MANUAL_REVIEW_BLOCKED"
    elif any(review[k] == "NOT_CHECKED" for k in REQUIRED_MANUAL_CHECKS):
        state = "MANUAL_REVIEW_PENDING"
    else:
        state = "OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED"
    # The optional PDF may be omitted while base audit remains in review.
    pdf_claim = (
        "DECLARED_PASS_UNVERIFIED" if review["korean_pdf_visual"] == "PASS" else
        "DECLARED_FAIL" if review["korean_pdf_visual"] == "FAIL" else
        "NOT_TESTED" if review["korean_pdf_visual"] == "NOT_TESTED" else
        "NOT_CHECKED"
    )
    return {
        "status": state,
        "automated_report_claims_consistent": True,
        "inner_portable_hash_verified": True,
        "pdf_claim": pdf_claim,
        "owner_identity_verified": False,
        "owner_device_execution_independently_verified": False,
        "manual_observations_independently_verified": False,
        "commercial_release_approved": False,
    }


def assess_files(portable_zip, selfcheck_json, review_json):
    hash_expected_portable(portable_zip)
    audit = _audit()
    try:
        automated = audit.read_document(selfcheck_json)
        review = audit.read_document(review_json)
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise EvidenceError("EVIDENCE_INPUT_REJECTED") from exc
    return assess(automated, review)


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA local Windows evidence consistency (claims not verified)")
    p.add_argument("--portable-zip", required=True, help="actual v0.10 inner portable ZIP")
    p.add_argument("--selfcheck", required=True, help="read-only SELF_CHECK_RESULT.json")
    p.add_argument("--manual-review", required=True, help="local operator-declared review JSON")
    args = p.parse_args(argv)
    try:
        result = assess_files(args.portable_zip, args.selfcheck, args.manual_review)
    except EvidenceError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 3 if result["status"] != "OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
