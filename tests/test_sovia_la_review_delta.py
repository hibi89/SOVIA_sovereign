"""P38: differential synthetic retrospective risk readout, no raw row disclosure."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sovia_audit import read_document
from sovia_la_owner_review import create_bundle, ReviewError
from sovia_la_review_delta import compare_review_bundles

PLAN = ROOT / "examples/demo_la_plan_review.json"
POLICY = ROOT / "examples/demo_policy.json"
OBS = ROOT / "examples/demo_la_observations.json"


class LaReviewDeltaTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory(prefix="sovia-delta-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.old = self.root / "old"
        self.new = self.root / "new"
        create_bundle(PLAN, POLICY, OBS, self.old)
        observed = read_document(OBS)
        observed["events"] = observed["events"][:1]
        altered = self.root / "other_observations.json"
        altered.write_text(json.dumps(observed), encoding="utf-8")
        create_bundle(PLAN, POLICY, altered, self.new)

    def test_verified_aggregate_delta_detects_missing_observation(self):
        report = compare_review_bundles(self.old, self.new)
        self.assertEqual("REVIEW_REQUIRED_UNAUTHENTICATED", report["status"])
        self.assertEqual(-1, report["observation_count_change"])
        self.assertEqual(0, report["plan_steps_change"])
        self.assertGreaterEqual(report["severity_increases"], 1)
        self.assertGreater(
            report["severity_counts"]["reconciliation"]["UNKNOWN"]["change"], 0)
        for field in ("risk_clearance_verified", "real_la_integration_verified",
                      "source_authenticity_verified", "execution_authorized"):
            self.assertIs(report[field], False)

    def test_output_omits_raw_event_identifiers_and_source_rows(self):
        report = json.dumps(compare_review_bundles(self.old, self.new))
        for hidden in ('"events":', '"steps":', '"policy": {', "synthetic:lookup",
                       "demo_la_plan", "step_or_event_id", "event_id", "source_pointer"):
            self.assertNotIn(hidden, report)
        self.assertIn("CALLER_ORDER_NOT_PROVEN_CHRONOLOGICAL", report)

    def test_identical_content_separate_folders_not_safe_clearance(self):
        duplicate = self.root / "duplicate"
        create_bundle(PLAN, POLICY, OBS, duplicate)
        report = compare_review_bundles(self.old, duplicate)
        self.assertTrue(report["same_report"])
        self.assertEqual(0, report["severity_increases"])
        self.assertEqual("REVIEW_REQUIRED_UNAUTHENTICATED", report["status"])
        self.assertIs(report["risk_clearance_verified"], False)

    def test_same_path_not_permitted(self):
        with self.assertRaisesRegex(ReviewError, "SAME_REVIEW_DIRECTORY"):
            compare_review_bundles(self.old, self.old)

    def test_tampered_report_rejected_even_with_valid_original(self):
        (self.new / "review.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(ReviewError):
            compare_review_bundles(self.old, self.new)

    def test_symlinked_report_file_rejected(self):
        item = self.new / "review.html"
        item.unlink()
        try:
            item.symlink_to(self.old / "review.html")
        except (OSError, NotImplementedError):
            self.skipTest("host symlink unavailable")
        with self.assertRaisesRegex(ReviewError, "LINKED_PATH_REFUSED"):
            compare_review_bundles(self.old, self.new)

    def test_cli_ack_required_with_no_source_mutation(self):
        args = [sys.executable, "-I", "-B", str(ROOT / "sovia_la_review_delta.py"),
                "--previous", str(self.old), "--current", str(self.new)]
        previous = (self.old / "review.json").read_bytes()
        denied = subprocess.run(args, capture_output=True, text=True, timeout=30)
        self.assertEqual(2, denied.returncode)
        self.assertIn("SYNTHETIC_ACK_REQUIRED", denied.stderr)
        ok = subprocess.run(args + ["--synthetic-only"], capture_output=True,
                            text=True, timeout=30)
        self.assertEqual(0, ok.returncode, ok.stderr)
        self.assertEqual("REVIEW_REQUIRED_UNAUTHENTICATED",
                         json.loads(ok.stdout)["status"])
        self.assertEqual(previous, (self.old / "review.json").read_bytes())


if __name__ == "__main__":
    unittest.main()
