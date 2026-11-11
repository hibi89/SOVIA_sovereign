"""Isolated new-version SOVIA LA review package smoke: no customer data/API."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile

from build_portable_la_review import DEFAULT_NAME, build
from verify_portable_la_review import extract_verified, verify_directory


def _cli(script, *args, expected=0):
    proc = subprocess.run(
        [sys.executable, "-I", "-B", str(script), *[str(v) for v in args]],
        capture_output=True, text=True, timeout=40,
    )
    if proc.returncode != expected:
        raise RuntimeError("ISOLATED_REVIEW_CLI_STATUS_MISMATCH")
    if expected:
        return json.loads(proc.stderr)
    return json.loads(proc.stdout)


def smoke():
    with tempfile.TemporaryDirectory(prefix="sovia-la-review-") as tmp:
        root = Path(tmp)
        archive = root / DEFAULT_NAME
        receipt = build(archive)
        extraction = root / "clean-extract"
        extract_verified(archive, extraction,
                         archive.with_name(archive.name + ".sha256"))
        verify_directory(extraction)
        script = extraction / "sovia_la_owner_review.py"
        output = root / "human-review"
        result = _cli(
            script, "--plan", extraction / "examples/demo_la_plan_review.json",
            "--policy", extraction / "examples/demo_policy.json",
            "--observations", extraction / "examples/demo_la_observations.json",
            "--output-dir", output, "--synthetic-only")
        if result["review_status"] != "SYNTHETIC_REVIEW_REQUIRED":
            raise RuntimeError("SYNTHETIC_RISK_FALSE_CLEAR")
        verified = _cli(script, "--verify-output-dir", output)
        if verified["status"] != "SYNTHETIC_BUNDLE_CONSISTENT_NOT_AUTHENTICATED":
            raise RuntimeError("REVIEW_BUNDLE_NOT_CONSISTENT")
        review = json.loads((output / "review.json").read_text("utf-8"))
        if not (review["planned_steps"] == review["observed_events"] == 2
                and review["plan_risk_finding_count"] > 0
                and review["post_audit_finding_count"] > 0
                and review["execution_authorized"] is False
                and review["real_la_integration_verified"] is False):
            raise RuntimeError("REVIEW_COVERAGE_OR_CLAIMS_INVALID")
        raw = (output / "review.json").read_text("utf-8")
        if "synthetic:lookup" in raw or "occurred_at_utc" in raw:
            raise RuntimeError("RAW_OBSERVATION_IN_REPORT")
        rerun = _cli(
            script, "--plan", extraction / "examples/demo_la_plan_review.json",
            "--policy", extraction / "examples/demo_policy.json",
            "--observations", extraction / "examples/demo_la_observations.json",
            "--output-dir", output, "--synthetic-only", expected=2)
        if rerun["error_code"] != "OUTPUT_EXISTS":
            raise RuntimeError("OUTPUT_OVERWRITE_NOT_BLOCKED")
        (output / "review.html").write_text("tampered", encoding="utf-8")
        invalid = _cli(script, "--verify-output-dir", output, expected=2)
        if invalid["error_code"] != "INTEGRITY_MISMATCH":
            raise RuntimeError("REPORT_TAMPER_NOT_DETECTED")
        verify_directory(extraction)
        return {"status": "SYNTHETIC_LA_REVIEW_PORTABLE_CLEAN_INSTALL_PASS",
                "files": receipt["files"], "zip_sha256": receipt["sha256"],
                "review_risks_preserved": True, "no_raw_source_export": True,
                "no_overwrite": True, "tamper_rejected": True,
                "real_la_integration_verified": False,
                "commercial_release_approved": False}


if __name__ == "__main__":
    print(json.dumps(smoke(), sort_keys=True))
