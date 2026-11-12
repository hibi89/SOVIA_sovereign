"""P40 public-safe synthetic LA-like projection and verified SOVIA review crosscheck."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sovia_la_owner_review import create_bundle
from sovia_la_minimal_projection import (
    SCHEMA, SOURCE_KIND, ReviewError, compare_minimal_projection,
)

PLAN = ROOT / "examples/demo_la_plan_review.json"
POLICY = ROOT / "examples/demo_policy.json"
OBS = ROOT / "examples/demo_la_observations.json"


class MinimalLAProjectionTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="sovia-p40-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.review = self.root / "review"
        create_bundle(PLAN, POLICY, OBS, self.review)
        doc = json.loads((self.review / "review.json").read_text("utf-8"))
        self.projection = self.root / "projection.json"
        self.payload = {
            "schema_version": SCHEMA,
            "source_kind": SOURCE_KIND,
            "synthetic_only": True,
            "source_authenticated": False,
            "approval_authenticated": False,
            "stream_completeness_verified": False,
            "plan_fingerprint_sha256": doc["plan_fingerprint_sha256"],
            "run_status": "completed",
            "steps": {
                "declared": 2, "recorded": 2, "completed": 2,
                "skipped": 0, "failed": 0, "running": 0,
            },
            "audit": {"event_count": 4, "terminal_completion_claimed": True,
                      "write_approval_claims": 1},
        }
        self.write()

    def write(self):
        self.projection.write_text(json.dumps(self.payload), encoding="utf-8")

    def compare(self):
        return compare_minimal_projection(self.projection, self.review, acknowledge=True)

    def test_happy_claimed_counts_still_untrusted_and_existing_risks_kept(self):
        report = self.compare()
        self.assertEqual("REVIEW_REQUIRED_NOT_AUTHENTICATED", report["status"])
        self.assertEqual(["SOVIA_RISK_FINDINGS_PRESENT"], report["reasons"])
        self.assertGreater(report["review_risk_count"], 0)
        self.assertTrue(report["plan_fingerprint_claim_matches"])
        for key in ("source_authenticated", "owner_approval_authenticated",
                    "real_la_integration_verified", "cross_run_identity_verified",
                    "execution_authorized", "commercial_release_approved"):
            self.assertIs(report[key], False)

    def test_missing_or_extra_steps_detected_not_approved(self):
        self.payload["steps"]["recorded"] = 1
        self.payload["steps"]["completed"] = 1
        self.write()
        report = self.compare()
        self.assertIn("STEP_LEDGER_INCOMPLETE_OR_EXTRA", report["reasons"])

    def test_invalid_outcome_sum_and_status_detected(self):
        self.payload["steps"]["completed"] = 1
        self.payload["run_status"] = "running"
        self.payload["audit"]["terminal_completion_claimed"] = False
        self.write()
        reasons = self.compare()["reasons"]
        for code in ("STEP_OUTCOME_TOTAL_MISMATCH", "COMPLETION_NOT_CLAIMED",
                     "TERMINAL_AUDIT_NOT_CLAIMED"):
            self.assertIn(code, reasons)

    def test_wrong_plan_digest_and_wrong_declared_count_are_visible_flags_not_identifiers(self):
        self.payload["plan_fingerprint_sha256"] = "0" * 64
        self.payload["steps"]["declared"] = 3
        self.write()
        report = self.compare()
        self.assertIn("PLAN_FINGERPRINT_MISMATCH", report["reasons"])
        self.assertIn("PLANNED_STEP_COUNT_MISMATCH", report["reasons"])
        self.assertNotIn("0" * 64, json.dumps(report))

    def test_unapproved_authenticated_claims_refused(self):
        self.payload["source_authenticated"] = True
        self.write()
        with self.assertRaisesRegex(ReviewError, "PROJECTION_SCHEMA_REFUSED"):
            self.compare()
        self.payload["source_authenticated"] = False
        self.payload["approval_authenticated"] = True
        self.write()
        with self.assertRaisesRegex(ReviewError, "PROJECTION_SCHEMA_REFUSED"):
            self.compare()

    def test_unknown_raw_fields_and_bools_as_counts_refused(self):
        self.payload["events"] = [{"token": "DO_NOT_EXPORT"}]
        self.write()
        with self.assertRaisesRegex(ReviewError, "PROJECTION_SCHEMA_REFUSED"):
            self.compare()
        del self.payload["events"]
        self.payload["steps"]["recorded"] = True
        self.write()
        with self.assertRaisesRegex(ReviewError, "PROJECTION_COUNT_REFUSED"):
            self.compare()

    def test_json_duplicate_keys_refused(self):
        raw = self.projection.read_text("utf-8")
        self.projection.write_text(raw.replace(
            '"synthetic_only": true', '"synthetic_only": true, "synthetic_only": true'),
            encoding="utf-8")
        with self.assertRaisesRegex(ReviewError, "DUPLICATE_JSON_KEY"):
            self.compare()

    def test_tampered_review_fails_without_writing(self):
        self.assertTrue(self.review.is_dir())
        (self.review / "review.html").write_text("tampered", encoding="utf-8")
        with self.assertRaisesRegex(ReviewError, "INTEGRITY_MISMATCH"):
            self.compare()

    def test_oversize_projection_fails_before_decoding(self):
        self.projection.write_bytes(b"x" * 17000)
        with self.assertRaisesRegex(ReviewError, "PROJECTION_OVERSIZED"):
            self.compare()

    def test_symlink_projection_forbidden(self):
        linked = self.root / "linked.json"
        try:
            linked.symlink_to(self.projection)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink not available")
        with self.assertRaisesRegex(ReviewError, "LINKED_PATH_REFUSED"):
            compare_minimal_projection(linked, self.review, acknowledge=True)

    def test_requires_ack_before_reading(self):
        with self.assertRaisesRegex(ReviewError, "SYNTHETIC_PROJECTION_ACK_REQUIRED"):
            compare_minimal_projection(self.root / "unknown.json", self.review)

    def test_isolated_cli_real_process_no_raw_fields_or_source_mutation(self):
        raw = self.projection.read_bytes()
        review = (self.review / "review.json").read_bytes()
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_la_minimal_projection.py"),
               "--projection", str(self.projection), "--review-dir", str(self.review)]
        denial = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        self.assertEqual(2, denial.returncode)
        self.assertIn("SYNTHETIC_PROJECTION_ACK_REQUIRED", denial.stderr)
        ok = subprocess.run(cmd + ["--synthetic-only"], capture_output=True,
                            text=True, timeout=30)
        self.assertEqual(0, ok.returncode, ok.stderr)
        text = ok.stdout
        result = json.loads(text)
        self.assertEqual("REVIEW_REQUIRED_NOT_AUTHENTICATED", result["status"])
        self.assertNotIn('"events"', text)
        self.assertNotIn('"run_id"', text)
        self.assertNotIn("synthetic:lookup", text)
        self.assertEqual(raw, self.projection.read_bytes())
        self.assertEqual(review, (self.review / "review.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
