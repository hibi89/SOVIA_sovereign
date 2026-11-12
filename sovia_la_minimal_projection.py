"""P40: read-only minimised LA-like synthetic receipt claims vs verified SOVIA.

The *input is a public abstract PROJECTION*, never raw LA/private HAE output.
No import of private code, live runtime, customer files, network or execution.
A self-reported checksum/receipt is NOT authentication or human authorization.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys


def _local_review():
    # Python -I excludes local paths, so load only this public adjacent file.
    source = Path(__file__).resolve().with_name("sovia_la_owner_review.py")
    spec = spec_from_file_location("_sovia_projection_public_review", source)
    if spec is None or spec.loader is None:
        raise RuntimeError("PUBLIC_REVIEW_COMPONENT_MISSING")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_review = _local_review()
ReviewError = _review.ReviewError
_safe_path = _review._safe_path
_parse_json = _review._parse_json
_require_review_structure = _review._require_review_structure
verify_bundle = _review.verify_bundle

SCHEMA = "sovia.la_minimal_projection.synthetic.v1"
SOURCE_KIND = "DECLARED_LA_LIKE_SYNTHETIC"
MAX_BYTES = 16_384
MAX_STEPS = 1000
MAX_AUDIT = 4096
HEX = re.compile(r"^[0-9a-f]{64}$")
SUMMARY_FIELDS = ("declared", "recorded", "completed", "skipped", "failed", "running")
REPORT_STATUS = "REVIEW_REQUIRED_NOT_AUTHENTICATED"


def _validate_projection(value):
    if (type(value) is not dict or set(value) != {
        "schema_version", "source_kind", "synthetic_only",
        "source_authenticated", "approval_authenticated",
        "stream_completeness_verified", "plan_fingerprint_sha256",
        "run_status", "steps", "audit",
    } or value["schema_version"] != SCHEMA
            or value["source_kind"] != SOURCE_KIND
            or value["synthetic_only"] is not True
            or value["source_authenticated"] is not False
            or value["approval_authenticated"] is not False
            or value["stream_completeness_verified"] is not False
            or type(value["plan_fingerprint_sha256"]) is not str
            or HEX.fullmatch(value["plan_fingerprint_sha256"]) is None
            or value["run_status"] not in ("completed", "running", "failed", "unknown")
            or type(value["steps"]) is not dict
            or set(value["steps"]) != set(SUMMARY_FIELDS)
            or type(value["audit"]) is not dict
            or set(value["audit"]) != {"event_count", "terminal_completion_claimed", "write_approval_claims"}
            or type(value["audit"]["terminal_completion_claimed"]) is not bool):
        raise ReviewError("PROJECTION_SCHEMA_REFUSED")
    for key in SUMMARY_FIELDS:
        v = value["steps"][key]
        if type(v) is not int or not 0 <= v <= MAX_STEPS:
            raise ReviewError("PROJECTION_COUNT_REFUSED")
    for key in ("event_count", "write_approval_claims"):
        v = value["audit"][key]
        if type(v) is not int or not 0 <= v <= MAX_AUDIT:
            raise ReviewError("PROJECTION_COUNT_REFUSED")
    return value


def _checked_projection(path):
    target = _safe_path(path, expect_file=True)
    if target.stat().st_size > MAX_BYTES:
        raise ReviewError("PROJECTION_OVERSIZED")
    with target.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ReviewError("PROJECTION_OVERSIZED")
    parsed = _validate_projection(_parse_json(raw))
    # Discourage simple concurrent source-file replacement, no race-free claim.
    if _safe_path(target, expect_file=True).read_bytes() != raw:
        raise ReviewError("PROJECTION_CHANGED")
    return parsed, raw


def compare_minimal_projection(projection, review_dir, *, acknowledge=False):
    """Correlate bounded **synthetic claims** only; nothing is authenticated."""
    if acknowledge is not True:
        raise ReviewError("SYNTHETIC_PROJECTION_ACK_REQUIRED")
    proj, original = _checked_projection(projection)
    root = _safe_path(review_dir)
    verify_bundle(root)
    review_file = _safe_path(root / "review.json", expect_file=True)
    review_raw = review_file.read_bytes()
    if len(review_raw) > _review.MAX_FILE:
        raise ReviewError("REVIEW_OVERSIZED")
    review = _require_review_structure(_parse_json(review_raw))

    actual_fingerprint = review.get("plan_fingerprint_sha256")
    if type(actual_fingerprint) is not str or HEX.fullmatch(actual_fingerprint) is None:
        raise ReviewError("REVIEW_FINGERPRINT_MISSING")
    claims = proj["steps"]
    audit = proj["audit"]
    reasons = []
    if proj["plan_fingerprint_sha256"] != actual_fingerprint:
        reasons.append("PLAN_FINGERPRINT_MISMATCH")
    if claims["declared"] != review["planned_steps"]:
        reasons.append("PLANNED_STEP_COUNT_MISMATCH")
    if claims["recorded"] != sum(claims[k] for k in
                                ("completed", "skipped", "failed", "running")):
        reasons.append("STEP_OUTCOME_TOTAL_MISMATCH")
    if claims["declared"] != claims["recorded"]:
        reasons.append("STEP_LEDGER_INCOMPLETE_OR_EXTRA")
    if proj["run_status"] != "completed":
        reasons.append("COMPLETION_NOT_CLAIMED")
    if claims["failed"] or claims["running"]:
        reasons.append("INCOMPLETE_OR_FAILED_STEPS")
    if not audit["terminal_completion_claimed"]:
        reasons.append("TERMINAL_AUDIT_NOT_CLAIMED")
    if audit["event_count"] == 0:
        reasons.append("NO_AUDIT_EVENTS_DECLARED")
    if (review["plan_risk_finding_count"] or review["post_audit_finding_count"] or
            review["reconciliation_finding_count"]):
        reasons.append("SOVIA_RISK_FINDINGS_PRESENT")
    # Validate again before emitting result, still best-effort TOCTOU protection.
    verify_bundle(root)
    if _safe_path(review_file, expect_file=True).read_bytes() != review_raw:
        raise ReviewError("REVIEW_CHANGED")
    if _safe_path(projection, expect_file=True).read_bytes() != original:
        raise ReviewError("PROJECTION_CHANGED")
    return {
        "schema_version": "sovia.la_minimal_crosscheck.synthetic.v1",
        "status": REPORT_STATUS,
        "scope": "SYNTHETIC_READ_ONLY_AGGREGATES",
        "reasons": sorted(set(reasons)),
        "reason_count": len(set(reasons)),
        "review_plan_steps": review["planned_steps"],
        "projection_declared_steps": claims["declared"],
        "projection_recorded_steps": claims["recorded"],
        "audit_event_count_claimed": audit["event_count"],
        "write_approval_claims": audit["write_approval_claims"],
        "review_risk_count": (
            review["plan_risk_finding_count"] +
            review["post_audit_finding_count"] +
            review["reconciliation_finding_count"]
        ),
        "plan_fingerprint_claim_matches": proj["plan_fingerprint_sha256"] == actual_fingerprint,
        "public_projection_sha256": hashlib.sha256(original).hexdigest(),
        "source_authenticated": False,
        "owner_approval_authenticated": False,
        "real_la_integration_verified": False,
        "observation_completeness_verified": False,
        "cross_run_identity_verified": False,
        "execution_authorized": False,
        "commercial_release_approved": False,
        "coverage_limits": [
            "BOTH_INPUTS_ARE_SELF_ASSERTED_SYNTHETIC",
            "PROJECTION_DIGEST_IS_NOT_A_SIGNATURE",
            "EVEN_MATCHING_PLAN_DIGEST_IS_NOT_PROVEN_RUN_IDENTITY",
            "LA_STEP_COUNTS_ARE_NOT_SOVIA_EVENT_COUNTS",
            "MISSING_EVENTS_OR_REDUCED_RISK_DO_NOT_PROVE_SAFETY",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA synthetic-only LA-like projection cross-check")
    p.add_argument("--projection", required=True)
    p.add_argument("--review-dir", required=True)
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args(argv)
    try:
        report = compare_minimal_projection(
            args.projection, args.review_dir, acknowledge=args.synthetic_only)
    except (ReviewError, ValueError, OSError, TypeError, UnicodeError) as exc:
        code = str(exc) if isinstance(exc, ReviewError) else "PROJECTION_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}),
              file=sys.stderr)
        return 2
    print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
