"""Privacy preflight tests use public synthetic placeholders, never customer logs."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import copy
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
import sovia_n8n_sanitized as adapter
import sovia_pii_preflight as preflight

ORIGINAL = {
    "format": adapter.FORMAT,
    "workflow_id": "synthetic_wf",
    "execution_id": "synthetic_run",
    "steps": [{
        "step_id": "node-1",
        "occurred_at_utc": "2026-10-26T00:01:00Z",
        "tool_code": "approved_lookup",
        "target_code": "public_docs",
        "destination_domain": "internal.example",
        "permission_asserted": True,
        "outcome_code": "success",
        "evidence_ref": "synthetic:1",
    }],
}
POLICY = {"schema_version": "1.0", "policy": {
    "allowed_tools": ["approved_lookup"],
    "approved_destinations": ["internal.example"],
    "sensitive_targets": ["client_records"],
    "max_tool_calls_per_minute": 2,
}}


def manifest(source=ORIGINAL, policy=POLICY):
    return {
        "schema_version": "1.0", "scope": "locally_reviewed_metadata",
        "source_sha256": adapter.canonical_sha256(source),
        "policy_sha256": adapter.canonical_sha256(policy),
        "source_authorized": True, "fields_reviewed": True,
        "retention_plan_documented": True,
        "expires_utc": (datetime.now(timezone.utc) + timedelta(days=7)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }


class PreflightTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.source = self.root / "private.json"
        self.policy = self.root / "policy.json"
        self.review = self.root / "review.json"
        self.output = self.root / "canonical.json"
        self.store()

    def store(self, source=None, policy=None):
        doc = copy.deepcopy(ORIGINAL if source is None else source)
        pol = copy.deepcopy(POLICY if policy is None else policy)
        self.source.write_text(json.dumps(doc), encoding="utf-8")
        self.policy.write_text(json.dumps(pol), encoding="utf-8")
        self.review.write_text(json.dumps(manifest(doc, pol)), encoding="utf-8")

    def approved(self):
        return adapter.convert_paths(self.source, self.policy, self.output,
                                     mode="approved-local", attestation_path=self.review)

    def test_clean_approved_metadata_conversion(self):
        original = (self.source.read_bytes(), self.policy.read_bytes(),
                    self.review.read_bytes())
        self.assertEqual(1, self.approved())
        self.assertEqual(original, (self.source.read_bytes(), self.policy.read_bytes(),
                                    self.review.read_bytes()))
        self.assertEqual(1, len(json.loads(self.output.read_text())["events"]))

    def test_clear_marker_explicitly_disclaims_complete_pii_scan(self):
        self.assertEqual("HEURISTIC_PATTERN_SCAN_CLEAR_NOT_PII_CERTIFIED",
                         preflight.assert_no_high_risk_patterns(ORIGINAL, POLICY))

    def test_approved_metadata_rejects_korean_mobile_number_in_code(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["workflow_id"] = "user_01012345678"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_approved_metadata_rejects_spaced_mobile_in_evidence(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["evidence_ref"] = "010-1234-5678"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_korean_id_like_numbers(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["execution_id"] = "000000-1000000"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_luhn_compatible_card_number(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["step_id"] = "evt_4111111111111111"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_luhn_invalid_number_is_not_automatically_flagged(self):
        self.assertEqual("HEURISTIC_PATTERN_SCAN_CLEAR_NOT_PII_CERTIFIED",
                         preflight.assert_no_high_risk_patterns({"code": "4111111111111112"}))

    def test_approved_metadata_rejects_ipv4_address_in_target(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["target_code"] = "10.0.0.4"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_ipv4_domain(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["destination_domain"] = "10.0.0.9"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_invalid_ipv4_like_string_not_flagged_by_pattern(self):
        self.assertEqual("HEURISTIC_PATTERN_SCAN_CLEAR_NOT_PII_CERTIFIED",
                         preflight.assert_no_high_risk_patterns({"text": "999.999.999.999"}))

    def test_approved_metadata_rejects_uuid_like_reference(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["execution_id"] = "123e4567-e89b-12d3-a456-426614174000"
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_access_key_like_reference(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["evidence_ref"] = "AKIA" + "A" * 16
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_api_token_like_reference(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["evidence_ref"] = "sk-" + "z" * 25
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_jwt_like_token(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["steps"][0]["evidence_ref"] = "eyJ" + "a" * 12 + "." + "b" * 12 + "." + "c" * 12
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_long_opaque_identifiers(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["workflow_id"] = "A" * 48
        self.store(source=doc)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()

    def test_approved_metadata_rejects_sensitive_policy_metadata(self):
        pol = copy.deepcopy(POLICY)
        pol["policy"]["allowed_tools"].append("sk-" + "x" * 30)
        self.store(policy=pol)
        with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_REJECTED"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_email_is_rejected_in_direct_preflight(self):
        with self.assertRaisesRegex(preflight.PreflightError, "PREFLIGHT_SUSPECT_METADATA"):
            preflight.assert_no_high_risk_patterns({"field": "user.name@example.com"})

    def test_approved_mode_never_echoes_pii_or_paths_in_cli_errors(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["workflow_id"] = "phone_01012345678"
        self.store(source=doc)
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_sanitized.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--attestation", str(self.review), "--mode", "approved-local",
               "--output", str(self.output)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(2, proc.returncode, proc.stderr)
        self.assertIn("PREFLIGHT_REJECTED", proc.stderr)
        self.assertNotIn("01012345678", proc.stderr)
        self.assertNotIn(str(self.root), proc.stderr)
        self.assertFalse(self.output.exists())

    def test_clean_cli_shows_heuristic_not_certification(self):
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_sanitized.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--attestation", str(self.review), "--mode", "approved-local",
               "--output", str(self.output)]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(0, proc.returncode, proc.stderr)
        obj = json.loads(proc.stdout)
        self.assertTrue(obj["pii_pattern_scan_executed"])
        self.assertFalse(obj["pii_absence_proven"])
        self.assertFalse(obj["authorization_independently_verified"])

    def test_synthetic_mode_retains_prior_contract_behavior(self):
        doc = copy.deepcopy(ORIGINAL)
        doc["workflow_id"] = "synthetic_01012345678"
        self.store(source=doc)
        self.assertEqual(1, adapter.convert_paths(self.source, self.policy, self.output))
        # The development-only synthetic path is deliberately NOT real-data authorization.
        self.assertEqual("synthetic_01012345678",
                         json.loads(self.output.read_text())["events"][0]["agent_id"])

    def test_clean_synthetic_cli_reports_not_scanned(self):
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_sanitized.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--output", str(self.output)]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertFalse(json.loads(p.stdout)["pii_pattern_scan_executed"])

    def test_preflight_blocks_nested_secret_values(self):
        with self.assertRaisesRegex(preflight.PreflightError, "PREFLIGHT_SUSPECT_METADATA"):
            preflight.assert_no_high_risk_patterns({"nested": [{"key": "sk-" + "v" * 30}]})

    def test_preflight_fails_closed_on_unbounded_depth(self):
        obj = "safe"
        for _ in range(18):
            obj = [obj]
        with self.assertRaisesRegex(preflight.PreflightError, "PREFLIGHT_LIMIT_EXCEEDED"):
            preflight.assert_no_high_risk_patterns(obj)

    def test_preflight_fails_closed_on_unbounded_nodes(self):
        with self.assertRaisesRegex(preflight.PreflightError, "PREFLIGHT_LIMIT_EXCEEDED"):
            preflight.assert_no_high_risk_patterns(["safe"] * (preflight.MAX_NODES + 1))

    def test_preflight_rejects_oversized_string(self):
        with self.assertRaisesRegex(preflight.PreflightError, "PREFLIGHT_STRING_TOO_LONG"):
            preflight.assert_no_high_risk_patterns("a" * (preflight.MAX_STRING_LENGTH + 1))

    def test_preflight_rejects_unsupported_types(self):
        with self.assertRaisesRegex(preflight.PreflightError, "PREFLIGHT_INVALID_METADATA"):
            preflight.assert_no_high_risk_patterns({"key": {42}})

    def test_preflight_errors_contain_no_sensitive_match(self):
        secret = "sk-" + "s" * 28
        try:
            preflight.assert_no_high_risk_patterns({"tool": secret})
        except preflight.PreflightError as exc:
            self.assertEqual("PREFLIGHT_SUSPECT_METADATA", str(exc))
            self.assertNotIn(secret, str(exc))
        else:
            self.fail("secret must be refused")

    def test_approved_path_cannot_publish_with_missing_checker(self):
        import sovia_audit
        with patch.object(adapter, "_audit", return_value=sovia_audit), \
             patch.object(adapter, "spec_from_file_location", return_value=None):
            with self.assertRaisesRegex(adapter.ContractError, "PREFLIGHT_MODULE_UNAVAILABLE"):
                self.approved()
        self.assertFalse(self.output.exists())

    def test_approved_path_offline_no_sockets(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(1, self.approved())


if __name__ == "__main__":
    unittest.main()
