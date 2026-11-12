"""0.15 package demo: generate only fabricated local SOVIA and LA-like claims.

This intentionally does NOT execute or authenticate first-party Lightning
Azent. The PRIVATE P41 integration CI separately exercises real synthetic LA.
No network or customer files. No pre-existing output path is overwritten.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


def _local(filename, alias):
    source = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(alias, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_DEMO_COMPONENT_UNAVAILABLE")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_review = _local("sovia_la_owner_review.py", "_sovia_v015_demo_owner")
_check = _local("sovia_la_minimal_projection.py", "_sovia_v015_demo_minimal")


def make_demo(output_dir, *, acknowledge=False):
    if acknowledge is not True:
        raise _review.ReviewError("SYNTHETIC_ACK_REQUIRED")
    target = _review._safe_path(output_dir)
    if target.exists() or target.is_symlink() or not target.parent.is_dir():
        raise _review.ReviewError("OUTPUT_EXISTS_OR_PARENT_MISSING")
    root = Path(__file__).resolve().parent
    # Fresh owned folder; failed runs leave visible INCOMPLETE marker.
    target.mkdir(mode=0o700)
    marker = target / ".SOVIA_INCOMPLETE"
    marker.write_bytes(b"NOT_VERIFIED\n")
    folder = target / "synthetic-review"
    created = _review.create_bundle(
        root / "examples/demo_la_plan_review.json",
        root / "examples/demo_policy.json",
        root / "examples/demo_la_observations.json",
        folder)
    if created["status"] != "SYNTHETIC_REVIEW_BUNDLE_CREATED_NOT_AUTHENTICATED":
        raise _review.ReviewError("DEMO_REPORT_FAILED")
    review = json.loads((folder / "review.json").read_text("utf-8"))
    count = review["planned_steps"]
    # Fabricated values chosen to illustrate P40. They are NOT LA runtime output.
    fixture = {
        "schema_version": _check.SCHEMA,
        "source_kind": _check.SOURCE_KIND,
        "synthetic_only": True,
        "source_authenticated": False,
        "approval_authenticated": False,
        "stream_completeness_verified": False,
        "plan_fingerprint_sha256": review["plan_fingerprint_sha256"],
        "run_status": "completed",
        "steps": {"declared": count, "recorded": count,
                  "completed": count, "skipped": 0, "failed": 0, "running": 0},
        "audit": {"event_count": count + 2, "terminal_completion_claimed": True,
                  "write_approval_claims": 1},
    }
    projection = target / "fabricated-la-like-projection.json"
    with projection.open("x", encoding="utf-8") as f:
        f.write(json.dumps(fixture, sort_keys=True, separators=(",", ":")) + "\n")
    checked = _check.compare_minimal_projection(projection, folder, acknowledge=True)
    if (checked["status"] != "REVIEW_REQUIRED_NOT_AUTHENTICATED" or
            not checked["plan_fingerprint_claim_matches"] or
            checked["source_authenticated"] is not False or
            checked["real_la_integration_verified"] is not False):
        raise _review.ReviewError("DEMO_UNTRUSTED_BOUNDARY_FAILED")
    _review.verify_bundle(folder)
    marker.unlink()
    return {
        "status": "SOVIA_V015_FABRICATED_LA_LIKE_DEMO_PASS_NOT_AUTHENTICATED",
        "report_status": checked["status"],
        "risk_findings_preserved": checked["review_risk_count"] > 0,
        "projection_sha256": hashlib.sha256(projection.read_bytes()).hexdigest(),
        "source_authenticated": False,
        "real_la_integration_verified": False,
        "owner_consent_authenticated": False,
        "commercial_release_approved": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA fabricated-only minimal LA projection demo")
    p.add_argument("--output-dir", required=True)
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args(argv)
    try:
        answer = make_demo(args.output_dir, acknowledge=args.synthetic_only)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError) as exc:
        code = str(exc) if isinstance(exc, _review.ReviewError) else "MINIMAL_DEMO_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    print(json.dumps(answer, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
