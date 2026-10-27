"""Synthetic-only operator review manifest and content-integrity gate tests."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
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
import sovia_n8n_sanitized as gate

SOURCE = {
    "format": gate.FORMAT,
    "workflow_id": "synthetic_wf",
    "execution_id": "synthetic_run",
    "steps": [{
        "step_id": "synthetic_node",
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


def claim(source=None, policy=None):
    return {
        "schema_version": "1.0",
        "scope": "locally_reviewed_metadata",
        "source_sha256": gate.canonical_sha256(SOURCE if source is None else source),
        "policy_sha256": gate.canonical_sha256(POLICY if policy is None else policy),
        "source_authorized": True,
        "fields_reviewed": True,
        "retention_plan_documented": True,
        "expires_utc": (datetime.now(timezone.utc) + timedelta(days=7)).strftime(
            "%Y-%m-%dT%H:%M:%SZ"),
    }


class OperatorGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / "input.json"
        self.policy = self.root / "policy.json"
        self.claim = self.root / "review.json"
        self.output = self.root / "result.json"
        self.store()

    def store(self, source=None, policy=None, manifest=None):
        self.source.write_text(json.dumps(SOURCE if source is None else source), encoding="utf-8")
        self.policy.write_text(json.dumps(POLICY if policy is None else policy), encoding="utf-8")
        self.claim.write_text(json.dumps(claim() if manifest is None else manifest), encoding="utf-8")

    def approved(self):
        return gate.convert_paths(self.source, self.policy, self.output,
                                  mode="approved-local", attestation_path=self.claim)

    def test_approved_local_claim_and_existing_evaluator(self):
        self.assertEqual(1, self.approved())
        from sovia_audit import evaluate, read_document
        report = evaluate(read_document(self.output))
        self.assertEqual(1, report["event_count"])
        self.assertEqual(0, report["finding_count"])

    def test_synthetic_backwards_compatible_without_claim(self):
        self.assertEqual(1, gate.convert_paths(self.source, self.policy, self.output))

    def test_approved_mode_requires_manifest(self):
        with self.assertRaisesRegex(gate.ContractError, "ATTESTATION_REQUIRED_ONLY_FOR_APPROVED_LOCAL"):
            gate.convert_paths(self.source, self.policy, self.output, mode="approved-local")
        self.assertFalse(self.output.exists())

    def test_synthetic_mode_rejects_manifest(self):
        with self.assertRaisesRegex(gate.ContractError, "ATTESTATION_REQUIRED_ONLY_FOR_APPROVED_LOCAL"):
            gate.convert_paths(self.source, self.policy, self.output, attestation_path=self.claim)
        self.assertFalse(self.output.exists())

    def test_source_modified_after_claim_is_rejected(self):
        altered = json.loads(self.source.read_text())
        altered["steps"][0]["tool_code"] = "other_tool"
        self.source.write_text(json.dumps(altered), encoding="utf-8")
        with self.assertRaisesRegex(gate.ContractError, "ATTESTATION_DIGEST_MISMATCH"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_policy_modified_after_claim_is_rejected(self):
        altered = json.loads(self.policy.read_text())
        altered["policy"]["allowed_tools"].append("new_tool")
        self.policy.write_text(json.dumps(altered), encoding="utf-8")
        with self.assertRaisesRegex(gate.ContractError, "ATTESTATION_DIGEST_MISMATCH"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_false_claims_and_string_booleans_are_denied(self):
        for field in ("source_authorized", "fields_reviewed", "retention_plan_documented"):
            for value in (False, None, "true", 1):
                with self.subTest(field=field, value=value):
                    obj = claim()
                    obj[field] = value
                    self.claim.write_text(json.dumps(obj), encoding="utf-8")
                    with self.assertRaisesRegex(gate.ContractError, "MISSING_OPERATOR_ACKNOWLEDGEMENT"):
                        self.approved()
                    self.assertFalse(self.output.exists())

    def test_extra_and_missing_review_metadata(self):
        for field in ("source_sha256", "scope", "expires_utc"):
            obj = claim()
            del obj[field]
            self.claim.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaisesRegex(gate.ContractError, "INVALID_ATTESTATION_FIELDS"):
                self.approved()
        obj = claim()
        obj["customer_email"] = "never_commit"
        self.claim.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(gate.ContractError, "INVALID_ATTESTATION_FIELDS"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_expired_manifest_is_denied(self):
        obj = claim()
        obj["expires_utc"] = "2020-01-01T00:00:00Z"
        self.claim.write_text(json.dumps(obj), encoding="utf-8")
        with self.assertRaisesRegex(gate.ContractError, "ATTESTATION_EXPIRED"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_invalid_expiry_timezone_format_and_calendar(self):
        for stamp in ("2099-01-01T00:00:00+09:00", "2099-02-30T00:00:00Z",
                      "2099-01-01T00:00:00", 1234, "2099-01-01"):
            with self.subTest(stamp=stamp):
                obj = claim()
                obj["expires_utc"] = stamp
                self.claim.write_text(json.dumps(obj), encoding="utf-8")
                with self.assertRaisesRegex(gate.ContractError, "INVALID_ATTESTATION_EXPIRY"):
                    self.approved()
                self.assertFalse(self.output.exists())

    def test_mismatched_or_non_hex_digest_is_denied(self):
        for value in ("0"*64, "ABCDEF"*10+"FFFF", 42, "short"):
            with self.subTest(value=value):
                obj = claim()
                obj["source_sha256"] = value
                self.claim.write_text(json.dumps(obj), encoding="utf-8")
                with self.assertRaisesRegex(gate.ContractError, "ATTESTATION_DIGEST_MISMATCH"):
                    self.approved()

    def test_scope_and_schema_must_be_exact(self):
        for field, value in (("scope", "consent_proven"), ("schema_version", "2.0")):
            obj = claim()
            obj[field] = value
            self.claim.write_text(json.dumps(obj), encoding="utf-8")
            with self.assertRaisesRegex(gate.ContractError, "INVALID_ATTESTATION_SCOPE"):
                self.approved()

    def test_same_document_different_json_order_is_same_digest(self):
        reordered = dict(reversed(list(SOURCE.items())))
        self.assertEqual(gate.canonical_sha256(reordered), claim()["source_sha256"])

    def test_duplicate_review_json_keys_rejected(self):
        self.claim.write_text('{"scope":"ok","scope":"bad"}', encoding="utf-8")
        with self.assertRaises(gate.ContractError):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_oversized_review_manifest_rejected(self):
        self.claim.write_bytes(b"{" + b" " * (1_048_576 + 1))
        with self.assertRaises(gate.ContractError):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_output_cannot_alias_review_file(self):
        before = self.claim.read_bytes()
        with self.assertRaisesRegex(gate.ContractError, "OUTPUT_ALIASES_INPUT"):
            gate.convert_paths(self.source, self.policy, self.claim,
                               mode="approved-local", attestation_path=self.claim)
        self.assertEqual(before, self.claim.read_bytes())

    def test_no_overwrite_existing_report(self):
        self.output.write_bytes(b"original")
        with self.assertRaises(gate.ContractError):
            self.approved()
        self.assertEqual(b"original", self.output.read_bytes())

    def test_raw_execution_payload_rejected_even_with_claim(self):
        raw = dict(SOURCE, data={"runData": [{"secret": "not permitted"}]})
        self.store(source=raw, manifest=claim(raw))
        with self.assertRaisesRegex(gate.ContractError, "UNSUPPORTED_SANITIZED_ENVELOPE"):
            self.approved()
        self.assertFalse(self.output.exists())

    def test_offline_no_network(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(1, self.approved())

    def test_isolated_cli_reports_unverified_claims(self):
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_sanitized.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--output", str(self.output), "--mode", "approved-local",
               "--attestation", str(self.claim)]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(0, p.returncode, p.stderr)
        result = json.loads(p.stdout)
        self.assertEqual("CONVERTED_WITH_UNVERIFIED_OPERATOR_CLAIMS", result["status"])
        self.assertIs(False, result["authorization_independently_verified"])
        self.assertNotIn(str(self.root), p.stdout)

    def test_cli_rejects_bad_claim_with_redacted_error(self):
        obj = claim()
        obj["source_authorized"] = False
        self.claim.write_text(json.dumps(obj), encoding="utf-8")
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_sanitized.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--output", str(self.output), "--mode", "approved-local",
               "--attestation", str(self.claim)]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(2, p.returncode)
        self.assertFalse(self.output.exists())
        self.assertNotIn(str(self.root), p.stderr)
        self.assertIn("MISSING_OPERATOR_ACKNOWLEDGEMENT", p.stderr)

    def test_deep_json_input_fails_closed_without_traceback_or_output(self):
        self.source.write_text("[" * 1500 + "0" + "]" * 1500, encoding="utf-8")
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_sanitized.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--output", str(self.output), "--mode", "approved-local",
               "--attestation", str(self.claim)]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)
        self.assertFalse(self.output.exists())

    def test_invalid_library_mode(self):
        with self.assertRaisesRegex(gate.ContractError, "INVALID_MODE"):
            gate.convert_paths(self.source, self.policy, self.output, mode="any")

    def test_manifest_is_only_operator_claim_not_authorization_proof(self):
        result = gate.verify_operator_attestation(claim(), SOURCE, POLICY)
        self.assertEqual("OPERATOR_CLAIMS_PRESENT_NOT_INDEPENDENTLY_VERIFIED", result)


if __name__ == "__main__":
    unittest.main()
