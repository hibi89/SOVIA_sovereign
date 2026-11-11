"""SOVIA synthetic LA owner review bundle: offline source and corruption tests."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_audit import read_document
from sovia_la_owner_review import (ReviewError, create_bundle, render_html,
                                   verify_bundle)

PLAN = ROOT / "examples" / "demo_la_plan_review.json"
POLICY = ROOT / "examples" / "demo_policy.json"
OBS = ROOT / "examples" / "demo_la_observations.json"


class OwnerReviewTests(unittest.TestCase):
    def _create(self, root):
        output = root / "review"
        result = create_bundle(PLAN, POLICY, OBS, output)
        self.assertEqual("SYNTHETIC_REVIEW_REQUIRED", result["review_status"])
        return output

    def test_source_engine_to_static_report_and_independent_verifier(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = self._create(root)
            self.assertEqual({"review.json", "review.html", "manifest.json"},
                             {p.name for p in output.iterdir()})
            verified = verify_bundle(output)
            self.assertEqual("SYNTHETIC_BUNDLE_CONSISTENT_NOT_AUTHENTICATED",
                             verified["status"])
            review = json.loads((output / "review.json").read_text("utf-8"))
            self.assertEqual((2, 2, 0),
                             (review["planned_steps"], review["observed_events"],
                              review["reconciliation_finding_count"]))
            self.assertGreater(review["plan_risk_finding_count"], 0)
            self.assertGreater(review["post_audit_finding_count"], 0)
            self.assertFalse(review["real_la_integration_verified"])
            page = (output / "review.html").read_text("utf-8")
            self.assertIn("default-src 'none'", page)
            self.assertIn("Lightning Azent", page)
            self.assertNotIn("<script", page)
            self.assertNotIn("2026-10-28T01:00:00Z", page)
            self.assertNotIn('"events":', page)

    def test_severity_of_missing_observation_is_review_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            observed = read_document(OBS)
            observed["events"] = observed["events"][:1]
            modified = root / "observed.json"
            modified.write_text(json.dumps(observed), encoding="utf-8")
            out = root / "bundle"
            create_bundle(PLAN, POLICY, modified, out)
            result = json.loads((out / "review.json").read_text("utf-8"))
            self.assertIn("PLANNED_STEP_NOT_OBSERVED",
                          {x["rule_id"] for x in result["reconciliation_findings"]})
            self.assertEqual("SYNTHETIC_REVIEW_REQUIRED", result["status"])
            self.assertEqual("SYNTHETIC_BUNDLE_CONSISTENT_NOT_AUTHENTICATED",
                             verify_bundle(out)["status"])

    def test_tampered_missing_and_extra_outputs_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self._create(root)
            (out / "review.html").write_text("tampered", encoding="utf-8")
            with self.assertRaisesRegex(ReviewError, "INTEGRITY_MISMATCH"):
                verify_bundle(out)
            out2 = root / "second"
            create_bundle(PLAN, POLICY, OBS, out2)
            (out2 / "unknown.bin").write_bytes(b"unexpected")
            with self.assertRaisesRegex(ReviewError, "INCOMPLETE_OR_EXTRA_OUTPUT"):
                verify_bundle(out2)
            (out2 / "unknown.bin").unlink()
            (out2 / "manifest.json").unlink()
            with self.assertRaisesRegex(ReviewError, "INCOMPLETE_OR_EXTRA_OUTPUT"):
                verify_bundle(out2)

    def test_empty_output_no_overwrite_and_sources_untouched(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out = self._create(root)
            originals = [(p, p.read_bytes()) for p in (PLAN, POLICY, OBS)]
            with self.assertRaisesRegex(ReviewError, "OUTPUT_EXISTS"):
                create_bundle(PLAN, POLICY, OBS, out)
            self.assertTrue(all(p.read_bytes() == raw for p, raw in originals))
            self.assertEqual("SYNTHETIC_BUNDLE_CONSISTENT_NOT_AUTHENTICATED",
                             verify_bundle(out)["status"])

    def test_bad_raw_event_and_private_token_rejected_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            observed = read_document(OBS)
            observed["events"][0]["credentials"] = "do-not-copy"
            bad = root / "bad.json"
            bad.write_text(json.dumps(observed), encoding="utf-8")
            with self.assertRaisesRegex(ReviewError, "SYNTHETIC_REVIEW_REJECTED"):
                create_bundle(PLAN, POLICY, bad, root / "reject")
            self.assertFalse((root / "reject").exists())
            observed = read_document(OBS)
            observed["events"][0]["source_pointer"] = "sk-" + "x" * 30
            bad.write_text(json.dumps(observed), encoding="utf-8")
            with self.assertRaisesRegex(ReviewError, "SYNTHETIC_REVIEW_REJECTED"):
                create_bundle(PLAN, POLICY, bad, root / "reject2")
            self.assertFalse((root / "reject2").exists())

    def test_html_escapes_even_unexpected_display_values(self):
        report = {
            "status": "<img src=x>", "planned_steps": 1, "observed_events": 1,
            "plan_risk_finding_count": 1, "post_audit_finding_count": 1,
            "reconciliation_finding_count": 1,
            "reconciliation_findings": [
                {"step_or_event_id": "<script>x</script>", "rule_id": "RULE",
                 "severity": "HIGH"}],
            "coverage_limits": ["<unsafe>"],
        }
        rendered = render_html(report)
        self.assertNotIn("<script>x</script>", rendered)
        self.assertIn("&lt;script&gt;x&lt;/script&gt;", rendered)
        self.assertIn("&lt;unsafe&gt;", rendered)

    def test_symlink_input_or_bundle_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            alias = root / "alias.json"
            try:
                alias.symlink_to(OBS)
            except (OSError, NotImplementedError):
                self.skipTest("No symlink privilege")
            with self.assertRaisesRegex(ReviewError, "LINKED_PATH_REFUSED"):
                create_bundle(PLAN, POLICY, alias, root / "reject")
            out = self._create(root)
            (out / "review.html").unlink()
            (out / "review.html").symlink_to(PLAN)
            with self.assertRaisesRegex(ReviewError, "LINKED_PATH_REFUSED"):
                verify_bundle(out)

    def test_isolated_cli_review_verify_and_acknowledgement(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            cli = [sys.executable, "-I", "-B",
                   str(ROOT / "sovia_la_owner_review.py")]
            args = ["--plan", str(PLAN), "--policy", str(POLICY),
                    "--observations", str(OBS), "--output-dir", str(root / "result")]
            denied = subprocess.run(cli + args, cwd=tmp,
                                    capture_output=True, text=True, timeout=25)
            self.assertEqual(2, denied.returncode)
            self.assertIn("SYNTHETIC_ACK_AND_INPUTS_REQUIRED", denied.stderr)
            self.assertFalse((root / "result").exists())
            approved = subprocess.run(cli + args + ["--synthetic-only"],
                                      cwd=tmp, capture_output=True, text=True, timeout=25)
            self.assertEqual(0, approved.returncode, approved.stderr)
            verified = subprocess.run(
                cli + ["--verify-output-dir", str(root / "result")],
                cwd=tmp, capture_output=True, text=True, timeout=25)
            self.assertEqual(0, verified.returncode, verified.stderr)
            self.assertIn("CONSISTENT_NOT_AUTHENTICATED", verified.stdout)
            self.assertFalse((root / "result" / ".SOVIA_INCOMPLETE").exists())


if __name__ == "__main__":
    unittest.main()
