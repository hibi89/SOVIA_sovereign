"""Owner evidence consistency tests are synthetic, not real device acceptance."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_portable
import sovia_owner_evidence as evidence


def auto(pdf="SKIPPED_REPORTLAB_MISSING"):
    return {
        "schema_version": "1.0", "version": "0.10.0-beta",
        "purpose": "SYNTHETIC_ONLY_NO_CUSTOMER_DATA",
        "status": "AUTOMATED_PASS_MANUAL_PENDING",
        "system": {"os": "Windows", "os_release": "synthetic", "python": "3.13.0"},
        "checks": {
            "python": "PASS", "package_integrity": "PASS", "audit": "PASS",
            "sqlite": "PASS", "dashboard": "PASS", "recovery": "PASS",
            "optional_pdf": pdf,
        },
        "synthetic": {"events": 3, "findings": 5, "reports": 1},
        "manual_acceptance": {
            "audit_html_visual": "NOT_CHECKED",
            "dashboard_html_visual": "NOT_CHECKED",
            "korean_pdf_visual": "NOT_CHECKED",
            "antivirus_or_smartscreen": "NOT_CHECKED",
            "owner_device_commercial_approval": "NOT_CHECKED",
        },
        "error_code": None,
    }


def review(audit="NOT_CHECKED", dashboard="NOT_CHECKED",
           defender="NOT_CHECKED", pdf="NOT_TESTED"):
    return {"schema_version": evidence.REVIEW_SCHEMA, "manual_checks": {
        "audit_html_visual": audit, "dashboard_html_visual": dashboard,
        "antivirus_or_smartscreen": defender, "korean_pdf_visual": pdf,
    }}


class OwnerEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.portable = Path(cls.temp.name) / build_portable.DEFAULT_NAME
        build_portable.build(cls.portable)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.temp_each = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_each.cleanup)
        self.root = Path(self.temp_each.name)
        self.auto = self.root / "SELF_CHECK_RESULT.json"
        self.manual = self.root / "manual.json"
        self.save()

    def save(self, automated=None, manual=None):
        self.auto.write_text(json.dumps(auto() if automated is None else automated),
                             encoding="utf-8")
        self.manual.write_text(json.dumps(review() if manual is None else manual),
                               encoding="utf-8")

    def run_cli(self, zip_path=None):
        return subprocess.run([
            sys.executable, "-I", "-B", str(ROOT / "sovia_owner_evidence.py"),
            "--portable-zip", str(self.portable if zip_path is None else zip_path),
            "--selfcheck", str(self.auto), "--manual-review", str(self.manual),
        ], capture_output=True, text=True, timeout=30)

    def test_known_v010_zip_digest_is_verified_from_bytes(self):
        self.assertTrue(evidence.hash_expected_portable(self.portable))
        digest = hashlib.sha256(self.portable.read_bytes()).hexdigest()
        self.assertEqual(evidence.EXPECTED_INNER_ZIP_SHA256, digest)

    def test_default_manual_not_checked_remains_pending(self):
        result = evidence.assess_files(self.portable, self.auto, self.manual)
        self.assertEqual("MANUAL_REVIEW_PENDING", result["status"])
        self.assertFalse(result["owner_identity_verified"])
        self.assertFalse(result["commercial_release_approved"])

    def test_fully_declared_checks_are_only_unverified_claims(self):
        self.save(manual=review("PASS", "PASS", "PASS", "NOT_TESTED"))
        result = evidence.assess_files(self.portable, self.auto, self.manual)
        self.assertEqual("OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED", result["status"])
        for key in ("owner_identity_verified",
                    "owner_device_execution_independently_verified",
                    "manual_observations_independently_verified",
                    "commercial_release_approved"):
            self.assertIs(False, result[key])

    def test_manual_block_is_not_silently_passed(self):
        self.save(manual=review("PASS", "FAIL", "PASS"))
        result = evidence.assess_files(self.portable, self.auto, self.manual)
        self.assertEqual("MANUAL_REVIEW_BLOCKED", result["status"])

    def test_bare_not_checked_antivirus_cannot_pass(self):
        self.save(manual=review("PASS", "PASS", "NOT_CHECKED"))
        self.assertEqual("MANUAL_REVIEW_PENDING",
                         evidence.assess_files(self.portable, self.auto, self.manual)["status"])

    def test_pdf_claim_cannot_pass_when_not_generated(self):
        self.save(manual=review("PASS", "PASS", "PASS", "PASS"))
        with self.assertRaisesRegex(evidence.EvidenceError, "PDF_CLAIM_CONTRADICTS_AUTOCHECK"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_generated_pdf_declared_pass_is_still_not_verified(self):
        self.save(automated=auto("GENERATED_NEEDS_VISUAL_REVIEW"),
                  manual=review("PASS", "PASS", "PASS", "PASS"))
        result = evidence.assess_files(self.portable, self.auto, self.manual)
        self.assertEqual("DECLARED_PASS_UNVERIFIED", result["pdf_claim"])
        self.assertIs(False, result["manual_observations_independently_verified"])

    def test_optional_pdf_failure_prevents_claims_consistent(self):
        self.save(automated=auto("FAILED_OPTIONAL_PDF"),
                  manual=review("PASS", "PASS", "PASS", "NOT_TESTED"))
        result = evidence.assess_files(self.portable, self.auto, self.manual)
        self.assertEqual("MANUAL_REVIEW_BLOCKED", result["status"])

    def test_human_pdf_fail_prevents_claims_consistent(self):
        self.save(automated=auto("GENERATED_NEEDS_VISUAL_REVIEW"),
                  manual=review("PASS", "PASS", "PASS", "FAIL"))
        result = evidence.assess_files(self.portable, self.auto, self.manual)
        self.assertEqual("MANUAL_REVIEW_BLOCKED", result["status"])

    def test_unsupported_pdf_status_is_refused(self):
        record = auto()
        record["checks"]["optional_pdf"] = "PASS"
        self.save(automated=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_AUTOMATION_INCOMPLETE"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_version_mismatch_rejected(self):
        record = auto()
        record["version"] = "0.9.0-beta"
        self.save(automated=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_INVALID_ENVELOPE"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_macos_linux_claims_rejected(self):
        for platform_name in ("Linux", "Darwin"):
            with self.subTest(name=platform_name):
                record = auto()
                record["system"]["os"] = platform_name
                self.save(automated=record)
                with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_NOT_WINDOWS"):
                    evidence.assess_files(self.portable, self.auto, self.manual)

    def test_python_older_than_3_11_rejected(self):
        record = auto()
        record["system"]["python"] = "3.10.15"
        self.save(automated=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_UNSUPPORTED_PYTHON"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_invalid_python_string_rejected(self):
        for value in ("3.13", "python 3.13.0", "", None):
            with self.subTest(value=value):
                record = auto()
                record["system"]["python"] = value
                self.save(automated=record)
                with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_NOT_WINDOWS"):
                    evidence.assess_files(self.portable, self.auto, self.manual)

    def test_cannot_claim_pass_on_failed_automation(self):
        record = auto()
        record["checks"]["sqlite"] = "FAIL"
        self.save(automated=record, manual=review("PASS", "PASS", "PASS"))
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_AUTOMATION_INCOMPLETE"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_cannot_claim_pass_on_failed_overall_status(self):
        record = auto()
        record["status"] = "AUTOMATED_FAILED"
        self.save(automated=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_INVALID_ENVELOPE"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_cannot_claim_success_on_wrong_counts(self):
        record = auto()
        record["synthetic"]["findings"] = 0
        self.save(automated=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_SYNTHETIC_COUNTS_MISMATCH"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_legacy_manual_fields_must_remain_not_checked(self):
        record = auto()
        record["manual_acceptance"]["audit_html_visual"] = "PASS"
        self.save(automated=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "SELFCHECK_MANUAL_FIELDS_TAMPERED"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_invalid_review_extraneous_personal_field(self):
        record = review()
        record["full_name"] = "not-allowed"
        self.save(manual=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "REVIEW_INVALID_ENVELOPE"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_unknown_manual_checks_fail(self):
        record = review()
        record["manual_checks"]["customer_phone"] = "PASS"
        self.save(manual=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "REVIEW_INVALID_FIELDS"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_illegal_review_state_does_not_count(self):
        for value in ("APPROVED", 1, "SKIP", None):
            with self.subTest(value=value):
                record = review()
                record["manual_checks"]["audit_html_visual"] = value
                self.save(manual=record)
                with self.assertRaisesRegex(evidence.EvidenceError, "REVIEW_INVALID_STATE"):
                    evidence.assess_files(self.portable, self.auto, self.manual)

    def test_required_manual_fields_cannot_be_not_tested(self):
        record = review()
        record["manual_checks"]["antivirus_or_smartscreen"] = "NOT_TESTED"
        self.save(manual=record)
        with self.assertRaisesRegex(evidence.EvidenceError, "REVIEW_INVALID_STATE"):
            evidence.assess_files(self.portable, self.auto, self.manual)

    def test_wrong_portable_hash_rejected_without_reading_manual(self):
        tampered = self.root / "modified.zip"
        tampered.write_bytes(self.portable.read_bytes() + b"extra")
        with self.assertRaisesRegex(evidence.EvidenceError, "PORTABLE_HASH_MISMATCH"):
            evidence.assess_files(tampered, self.auto, self.manual)

    def test_missing_zip_fails_closed(self):
        with self.assertRaisesRegex(evidence.EvidenceError, "PORTABLE_FILE_UNAVAILABLE"):
            evidence.assess_files(self.root / "unknown.zip", self.auto, self.manual)

    def test_zip_symlink_is_rejected(self):
        link = self.root / "linked.zip"
        try:
            link.symlink_to(self.portable)
        except (OSError, NotImplementedError):
            self.skipTest("symlink privilege unavailable")
        with self.assertRaisesRegex(evidence.EvidenceError, "PORTABLE_FILE_UNAVAILABLE"):
            evidence.assess_files(link, self.auto, self.manual)

    def test_duplicate_json_fields_fail_without_traceback(self):
        self.manual.write_text('{"schema_version":"x","schema_version":"y"}', encoding="utf-8")
        process = self.run_cli()
        self.assertEqual(2, process.returncode)
        self.assertNotIn("Traceback", process.stderr)
        self.assertNotIn(str(self.root), process.stderr)

    def test_oversized_manual_report_rejected(self):
        self.manual.write_bytes(b" " * (1_048_576 + 1))
        self.assertEqual(2, self.run_cli().returncode)

    def test_isolated_cli_pending_return_code_three(self):
        result = self.run_cli()
        self.assertEqual(3, result.returncode, result.stderr)
        self.assertEqual("MANUAL_REVIEW_PENDING", json.loads(result.stdout)["status"])
        self.assertNotIn(str(self.root), result.stdout + result.stderr)

    def test_isolated_cli_declared_complete_still_unverified(self):
        self.save(manual=review("PASS", "PASS", "PASS"))
        result = self.run_cli()
        self.assertEqual(0, result.returncode, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual("OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED", data["status"])
        self.assertFalse(data["owner_device_execution_independently_verified"])

    def test_does_not_access_network(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual("MANUAL_REVIEW_PENDING",
                             evidence.assess_files(self.portable, self.auto, self.manual)["status"])


if __name__ == "__main__":
    unittest.main()
