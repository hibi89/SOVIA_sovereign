"""Synthetic-only end-to-end validation for direct sanitized adapter audit."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import sovia_n8n_direct_audit as direct
import sovia_n8n_sanitized as adapter
import sovia_audit as core

ROOT = Path(__file__).resolve().parents[1]


class DirectSanitizedAuditTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="sovia-direct-sanitized-")
        self.addCleanup(t.cleanup)
        root = Path(t.name)
        self.source = root / "source.json"
        self.policy = root / "policy.json"
        self.review = root / "review.json"
        self.html = root / "findings.html"
        self.report = root / "findings.json"
        self.source.write_bytes((ROOT / "examples/demo_n8n_sanitized.json").read_bytes())
        self.policy.write_bytes((ROOT / "examples/demo_policy.json").read_bytes())

    def execute(self):
        return direct.direct_audit(
            self.source, self.policy, self.html, self.report, synthetic_only=True)

    def attest(self):
        doc = json.loads(self.source.read_text(encoding="utf-8"))
        pol = json.loads(self.policy.read_text(encoding="utf-8"))
        review = {
            "schema_version": "1.0",
            "scope": "locally_reviewed_metadata",
            "source_sha256": adapter.canonical_sha256(doc),
            "policy_sha256": adapter.canonical_sha256(pol),
            "source_authorized": True,
            "fields_reviewed": True,
            "retention_plan_documented": True,
            "expires_utc": (datetime.now(timezone.utc) + timedelta(days=7)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"),
        }
        self.review.write_text(json.dumps(review), encoding="utf-8")

    def approved(self):
        return direct.direct_audit(
            self.source, self.policy, self.html, self.report,
            mode="approved-local", attestation=self.review)

    def test_real_engine_three_events_five_rules(self):
        result = self.execute()
        self.assertEqual((result["events"], result["findings"]), (3, 5))
        self.assertTrue(self.html.read_bytes().startswith(b"<!doctype html>"))
        parsed = json.loads(self.report.read_text(encoding="utf-8"))
        self.assertEqual((parsed["event_count"], parsed["finding_count"]), (3, 5))
        self.assertEqual(len({f["rule_id"] for f in parsed["findings"]}), 5)
        self.assertFalse(result["intermediate_canonical_file_created"])

    def test_matches_two_command_conversion_and_audit(self):
        self.execute()
        legacy = core.evaluate(adapter.convert(
            core.read_document(self.source), core.read_document(self.policy)))
        self.assertEqual(json.loads(self.report.read_text(encoding="utf-8")), legacy)
        self.assertEqual(self.html.read_bytes(), core.render_html(legacy).encode("utf-8"))

    def test_no_intermediate_canonical_file(self):
        self.execute()
        self.assertEqual(sorted(p.name for p in self.html.parent.iterdir()),
                         ["findings.html", "findings.json", "policy.json", "source.json"])

    def test_missing_synthetic_ack_rejected(self):
        with self.assertRaisesRegex(direct.DirectAuditError, "^SYNTHETIC_ACK_REQUIRED$"):
            direct.direct_audit(self.source, self.policy, self.html, self.report)
        self.assertFalse(self.html.exists())

    def test_invalid_mode_rejected(self):
        with self.assertRaisesRegex(direct.DirectAuditError, "^INVALID_MODE$"):
            direct.direct_audit(self.source, self.policy, self.html, self.report,
                                mode="native", synthetic_only=True)

    def test_synthetic_mode_rejects_attestation(self):
        self.attest()
        with self.assertRaisesRegex(direct.DirectAuditError, "^SYNTHETIC_ACK_REQUIRED$"):
            direct.direct_audit(self.source, self.policy, self.html, self.report,
                                attestation=self.review, synthetic_only=True)

    def test_approved_requires_claim(self):
        with self.assertRaisesRegex(direct.DirectAuditError, "^OPERATOR_ATTESTATION_REQUIRED$"):
            direct.direct_audit(self.source, self.policy, self.html, self.report,
                                mode="approved-local")
        self.assertFalse(self.html.exists())

    def test_approved_rejects_synthetic_switch(self):
        self.attest()
        with self.assertRaisesRegex(direct.DirectAuditError, "^OPERATOR_ATTESTATION_REQUIRED$"):
            direct.direct_audit(self.source, self.policy, self.html, self.report,
                                mode="approved-local", attestation=self.review,
                                synthetic_only=True)

    def test_operator_claim_not_independent_consent(self):
        self.attest()
        result = self.approved()
        self.assertTrue(result["pii_pattern_scan_executed"])
        self.assertFalse(result["pii_absence_proven"])
        self.assertFalse(result["source_authorization_independently_verified"])
        self.assertFalse(result["n8n_native_api_compatibility_verified"])
        self.assertEqual(result["status"], "REPORTS_CREATED_WITH_UNVERIFIED_OPERATOR_CLAIMS")

    def test_changed_source_after_claim_rejected(self):
        self.attest()
        doc = json.loads(self.source.read_text(encoding="utf-8"))
        doc["steps"][0]["tool_code"] = "other_lookup"
        self.source.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(direct.DirectAuditError, "^CONTRACT_OR_REVIEW_REJECTED$"):
            self.approved()
        self.assertFalse(self.html.exists())

    def test_raw_n8n_execution_rejected(self):
        self.source.write_text(
            json.dumps({"id": "nativeExecution", "data": {"resultData": "secret"}}),
            encoding="utf-8")
        with self.assertRaisesRegex(direct.DirectAuditError, "^CONTRACT_OR_REVIEW_REJECTED$"):
            self.execute()
        self.assertFalse(self.html.exists())

    def test_duplicate_json_keys_rejected(self):
        self.source.write_text('{"format":"sovia.n8n_sanitized.v1","format":"duplicate"}',
                               encoding="utf-8")
        with self.assertRaises(direct.DirectAuditError):
            self.execute()
        self.assertFalse(self.report.exists())

    def test_raw_payload_fields_rejected(self):
        doc = json.loads(self.source.read_text(encoding="utf-8"))
        doc["steps"][0]["credentials"] = {"secret": "TOKEN_DO_NOT_PRINT"}
        self.source.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(direct.DirectAuditError, "^CONTRACT_OR_REVIEW_REJECTED$"):
            self.execute()
        self.assertFalse(self.html.exists())

    def test_approved_pii_pattern_rejected_before_export(self):
        self.attest()
        doc = json.loads(self.source.read_text(encoding="utf-8"))
        doc["steps"][0]["evidence_ref"] = "4111111111111111"
        self.source.write_text(json.dumps(doc), encoding="utf-8")
        # Bound an altered source to a matching (unverified) claim so the PII
        # scan, rather than the content digest, must be the reason for denial.
        self.attest()
        with self.assertRaisesRegex(direct.DirectAuditError, "^CONTRACT_OR_REVIEW_REJECTED$"):
            self.approved()
        self.assertFalse(self.report.exists())

    def test_existing_html_untouched(self):
        self.html.write_text("ORIGINAL", encoding="utf-8")
        with self.assertRaisesRegex(direct.DirectAuditError, "^OUTPUT_ALREADY_EXISTS$"):
            self.execute()
        self.assertEqual(self.html.read_text(encoding="utf-8"), "ORIGINAL")
        self.assertFalse(self.report.exists())

    def test_existing_json_untouched(self):
        self.report.write_text("ORIGINAL", encoding="utf-8")
        with self.assertRaisesRegex(direct.DirectAuditError, "^OUTPUT_ALREADY_EXISTS$"):
            self.execute()
        self.assertEqual(self.report.read_text(encoding="utf-8"), "ORIGINAL")
        self.assertFalse(self.html.exists())

    def test_same_output_path_denied(self):
        with self.assertRaisesRegex(direct.DirectAuditError, "^INPUT_OUTPUT_PATH_COLLISION$"):
            direct.direct_audit(self.source, self.policy, self.html, self.html,
                                synthetic_only=True)

    def test_output_alias_source_denied(self):
        old = self.source.read_bytes()
        with self.assertRaisesRegex(direct.DirectAuditError, "^INPUT_OUTPUT_PATH_COLLISION$"):
            direct.direct_audit(self.source, self.policy, self.source, self.report,
                                synthetic_only=True)
        self.assertEqual(self.source.read_bytes(), old)

    def test_output_alias_claim_denied(self):
        self.attest()
        with self.assertRaisesRegex(direct.DirectAuditError, "^INPUT_OUTPUT_PATH_COLLISION$"):
            direct.direct_audit(self.source, self.policy, self.review, self.report,
                                mode="approved-local", attestation=self.review)

    def test_source_symlink_denied(self):
        link = self.html.parent / "link.json"
        try:
            link.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks not available")
        with self.assertRaisesRegex(direct.DirectAuditError, "^LOCAL_SOURCE_MISSING_OR_SYMLINK$"):
            direct.direct_audit(link, self.policy, self.html, self.report,
                                synthetic_only=True)

    def test_missing_output_folder_denied(self):
        with self.assertRaisesRegex(direct.DirectAuditError, "^OUTPUT_DIRECTORY_MISSING$"):
            direct.direct_audit(self.source, self.policy,
                                self.html.parent / "notcreated" / "report.html",
                                self.report, synthetic_only=True)

    def test_network_not_used(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network called")):
            self.execute()

    def test_publish_failure_does_not_leave_first_report(self):
        with patch.object(core.os, "link", side_effect=OSError("simulated disk full")):
            with self.assertRaisesRegex(direct.DirectAuditError, "^REPORT_PUBLISH_FAILED$"):
                self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.report.exists())

    def test_cli_isolated_python(self):
        proc = subprocess.run([
            sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_direct_audit.py"),
            "--input", str(self.source), "--policy", str(self.policy),
            "--html-output", str(self.html), "--json-output", str(self.report),
            "--synthetic-only",
        ], capture_output=True, text=True, timeout=25)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["findings"], 5)
        self.assertNotIn(str(self.html.parent), proc.stdout)

    def test_cli_error_does_not_disclose_input(self):
        self.source.write_text("PRIVATE_SECRET", encoding="utf-8")
        proc = subprocess.run([
            sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_direct_audit.py"),
            "--input", str(self.source), "--policy", str(self.policy),
            "--html-output", str(self.html), "--json-output", str(self.report),
            "--synthetic-only",
        ], capture_output=True, text=True, timeout=25)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stderr)["error_code"], "CONTRACT_OR_REVIEW_REJECTED")
        self.assertNotIn("PRIVATE_SECRET", proc.stderr)
        self.assertNotIn(str(self.source), proc.stderr)
        self.assertFalse(self.report.exists())


if __name__ == "__main__":
    unittest.main()
