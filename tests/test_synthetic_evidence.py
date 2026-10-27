"""Only simulated privacy negatives and self-claimed synthetic evidence, no customer data."""
from __future__ import annotations

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
import sovia_synthetic_evidence as gate
import sovia_n8n_execution_bridge as bridge
import sovia_n8n_sanitized as adapter
from sovia_audit import read_document, evaluate


def sample(version="2x"):
    return read_document(ROOT / "examples" / ("synthetic_n8n_bridge_" + version + ".json"))


def policy():
    return read_document(ROOT / "examples" / "demo_policy.json")


def manifest(source, pol):
    return {
        "schema_version": gate.FORMAT,
        "synthetic_only": True,
        "origin_claim": gate.CLAIM,
        "pinned_release_tag": source["pinned_release_tag"],
        "source_sha256": adapter.canonical_sha256(source),
        "policy_sha256": adapter.canonical_sha256(pol),
        "expected_canonical_sha256": adapter.canonical_sha256(
            bridge.convert_synthetic(source, pol)),
    }


class SyntheticEvidenceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.source_path = self.root / "source.json"
        self.policy_path = self.root / "policy.json"
        self.manifest_path = self.root / "manifest.json"
        self.source = sample()
        self.policy = policy()
        self.claim = manifest(self.source, self.policy)
        self.write_all()

    def write_all(self):
        for path, obj in ((self.source_path, self.source),
                          (self.policy_path, self.policy),
                          (self.manifest_path, self.claim)):
            path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_synthetic_evidence.py"),
             *args], capture_output=True, text=True, timeout=20)

    def args(self):
        return ("--input", str(self.source_path), "--policy", str(self.policy_path),
                "--manifest", str(self.manifest_path), "--synthetic-only")

    def test_both_release_synthetic_hashes_match(self):
        for version in ("1x", "2x"):
            with self.subTest(version=version):
                src = sample(version)
                result = gate.verify(src, policy(), manifest(src, policy()))
                self.assertEqual(3, result["event_count"])
                self.assertTrue(result["source_digest_matches"])
                self.assertTrue(result["policy_digest_matches"])
                self.assertTrue(result["canonical_digest_matches"])

    def test_all_success_limits_are_explicitly_unverified(self):
        result = gate.verify(self.source, self.policy, self.claim)
        self.assertEqual(
            "SYNTHETIC_DIGESTS_AND_PATTERN_CHECKS_CONSISTENT_UNVERIFIED",
            result["status"])
        for key in ("manifest_signature_verified", "provenance_independently_authenticated",
                    "synthetic_origin_independently_verified",
                    "customer_authorization_verified", "pii_absence_proven",
                    "n8n_instance_or_version_verified", "n8n_api_called", "file_write_performed"):
            with self.subTest(key=key):
                self.assertFalse(result[key])
        self.assertTrue(result["known_pattern_preflight_executed"])

    def test_original_source_and_policy_are_not_mutated(self):
        before_source, before_policy, before_claim = (
            copy.deepcopy(self.source), copy.deepcopy(self.policy), copy.deepcopy(self.claim))
        gate.verify(self.source, self.policy, self.claim)
        self.assertEqual(before_source, self.source)
        self.assertEqual(before_policy, self.policy)
        self.assertEqual(before_claim, self.claim)

    def test_summary_status_tampering_changes_source_hash_not_canonical(self):
        changed = copy.deepcopy(self.source)
        changed["execution_summary"]["status"] = "running"
        self.assertEqual(
            adapter.canonical_sha256(bridge.convert_synthetic(changed, self.policy)),
            self.claim["expected_canonical_sha256"])
        with self.assertRaisesRegex(gate.EvidenceError, "SOURCE_OR_POLICY_DIGEST_MISMATCH"):
            gate.verify(changed, self.policy, self.claim)

    def test_policy_change_fails_before_conversion(self):
        changed = copy.deepcopy(self.policy)
        changed["policy"]["max_tool_calls_per_minute"] = 3
        with self.assertRaisesRegex(gate.EvidenceError, "SOURCE_OR_POLICY_DIGEST_MISMATCH"):
            gate.verify(self.source, changed, self.claim)

    def test_manifest_source_digest_tamper_detected(self):
        c = dict(self.claim, source_sha256="0"*64)
        with self.assertRaisesRegex(gate.EvidenceError, "SOURCE_OR_POLICY_DIGEST_MISMATCH"):
            gate.verify(self.source, self.policy, c)

    def test_manifest_policy_digest_tamper_detected(self):
        c = dict(self.claim, policy_sha256="0"*64)
        with self.assertRaisesRegex(gate.EvidenceError, "SOURCE_OR_POLICY_DIGEST_MISMATCH"):
            gate.verify(self.source, self.policy, c)

    def test_expected_canonical_digest_tamper_detected(self):
        c = dict(self.claim, expected_canonical_sha256="0"*64)
        with self.assertRaisesRegex(gate.EvidenceError, "CANONICAL_DIGEST_MISMATCH"):
            gate.verify(self.source, self.policy, c)

    def test_recomputed_manifest_not_authenticated_even_after_tamper(self):
        changed = copy.deepcopy(self.source)
        changed["execution_summary"]["status"] = "crashed"
        new_claim = manifest(changed, self.policy)
        result = gate.verify(changed, self.policy, new_claim)
        self.assertTrue(result["source_digest_matches"])
        self.assertFalse(result["provenance_independently_authenticated"])
        self.assertFalse(result["manifest_signature_verified"])
        self.assertFalse(result["synthetic_origin_independently_verified"])

    def test_missing_or_extra_manifest_fields_block(self):
        for key in gate.MANIFEST_KEYS:
            c = dict(self.claim)
            del c[key]
            with self.subTest(key=key), self.assertRaisesRegex(
                gate.EvidenceError, "INVALID_SYNTHETIC_EVIDENCE_MANIFEST"):
                gate.verify(self.source, self.policy, c)
        c = dict(self.claim)
        c["operator_signature"] = "not-real"
        with self.assertRaisesRegex(gate.EvidenceError, "INVALID_SYNTHETIC_EVIDENCE_MANIFEST"):
            gate.verify(self.source, self.policy, c)

    def test_manifest_requires_exact_boolean_true(self):
        for value in (False, 1, None, "true"):
            c = dict(self.claim)
            c["synthetic_only"] = value
            with self.subTest(value=value), self.assertRaisesRegex(
                gate.EvidenceError, "INVALID_SYNTHETIC_EVIDENCE_MANIFEST"):
                gate.verify(self.source, self.policy, c)

    def test_reject_other_origin_claims_and_version(self):
        for value in ("customer_api_log", "real_export", None, "", {}):
            c = dict(self.claim)
            c["origin_claim"] = value
            with self.subTest(value=value), self.assertRaisesRegex(
                gate.EvidenceError, "INVALID_SYNTHETIC_EVIDENCE_MANIFEST"):
                gate.verify(self.source, self.policy, c)
        c = dict(self.claim)
        c["schema_version"] = "2.0"
        with self.assertRaisesRegex(gate.EvidenceError, "INVALID_SYNTHETIC_EVIDENCE_MANIFEST"):
            gate.verify(self.source, self.policy, c)

    def test_reject_unpinned_release_or_source_claim_mismatch(self):
        for tag in ("latest", "n8n@2.44.8", 123, None):
            c = dict(self.claim)
            c["pinned_release_tag"] = tag
            with self.subTest(tag=tag), self.assertRaisesRegex(
                gate.EvidenceError, "UNPINNED_EVIDENCE_RELEASE"):
                gate.verify(self.source, self.policy, c)
        c = dict(self.claim)
        c["pinned_release_tag"] = "n8n@1.123.88"
        with self.assertRaisesRegex(gate.EvidenceError, "SOURCE_RELEASE_OR_CLAIM_MISMATCH"):
            gate.verify(self.source, self.policy, c)

    def test_reject_noncanonical_or_invalid_hashes(self):
        for value in ("A"*64, "a"*63, "z"*64, "", 1, None, [], "a"*65):
            for field in ("source_sha256", "policy_sha256", "expected_canonical_sha256"):
                c = dict(self.claim)
                c[field] = value
                with self.subTest(field=field, value=repr(value)[:20]), self.assertRaisesRegex(
                    gate.EvidenceError, "INVALID_EVIDENCE_SHA256"):
                    gate.verify(self.source, self.policy, c)

    def test_only_self_declared_source_kind_not_real_api(self):
        d = copy.deepcopy(self.source)
        d["source_kind"] = "live_api_execution"
        c = dict(self.claim, source_sha256=adapter.canonical_sha256(d))
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_CONVERSION_REJECTED"):
            gate.verify(d, self.policy, c)

    def test_raw_execution_object_may_not_be_relabelled(self):
        d = {"id": "123", "data": {"runData": ["secret"]}, "synthetic_only": True,
             "pinned_release_tag": "n8n@2.44.7"}
        with self.assertRaises(gate.EvidenceError):
            gate.verify(d, self.policy, self.claim)

    def test_email_like_metadata_rejected_without_echo(self):
        # Full address is synthetically fabricated, never a user's email.
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["evidence_ref"] = "mock.user@example.com"
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(d, self.policy, self.claim)

    def test_simulated_access_key_in_tool_code_rejected(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["tool_code"] = "AKIA" + "A"*16
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(d, self.policy, self.claim)

    def test_synthetic_uuid_in_evidence_ref_rejected(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["evidence_ref"] = "550e8400-e29b-41d4-a716-446655440000"
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(d, self.policy, self.claim)

    def test_synthetic_korean_mobile_like_pattern_rejected(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["evidence_ref"] = "010-1234-5678"
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(d, self.policy, self.claim)

    def test_synthetic_ip_pattern_rejected(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["destination_domain"] = "198.51.100.25"
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(d, self.policy, self.claim)

    def test_synthetic_opaque_token_pattern_rejected(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["target_code"] = "z"*44
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(d, self.policy, self.claim)

    def test_sensitive_policy_patterns_rejected(self):
        p = copy.deepcopy(self.policy)
        p["policy"]["allowed_tools"][0] = "AKIA" + "B"*16
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_PRIVACY_PREFLIGHT_REJECTED"):
            gate.verify(self.source, p, self.claim)

    def test_extra_raw_execution_fields_refused_even_after_rehash(self):
        d = copy.deepcopy(self.source)
        d["execution_summary"]["data"] = {"not": "safe"}
        c = dict(self.claim, source_sha256=adapter.canonical_sha256(d))
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_CONVERSION_REJECTED"):
            gate.verify(d, self.policy, c)

    def test_unsafe_step_fields_refused_even_after_rehash(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["parameters"] = {"opaque": "fixture"}
        c = dict(self.claim, source_sha256=adapter.canonical_sha256(d))
        with self.assertRaisesRegex(gate.EvidenceError, "EVIDENCE_CONVERSION_REJECTED"):
            gate.verify(d, self.policy, c)

    def test_cli_readonly_success_and_no_files_created(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        p = self.cli(*self.args())
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertFalse(json.loads(p.stdout)["provenance_independently_authenticated"])
        after = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.assertEqual(before, after)

    def test_cli_requires_synthetic_only_flag(self):
        args = list(self.args())
        args.remove("--synthetic-only")
        p = self.cli(*args)
        self.assertEqual(2, p.returncode)
        self.assertIn("SYNTHETIC_ACK_REQUIRED", p.stderr)
        self.assertNotIn(str(self.root), p.stderr)

    def test_cli_rejects_duplicate_json_key_without_traceback(self):
        self.manifest_path.write_text('{"schema_version":"a","schema_version":"b"}', encoding="utf-8")
        p = self.cli(*self.args())
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)

    def test_cli_rejects_oversized_manifest_with_no_echo(self):
        self.manifest_path.write_bytes(b"x" * 1_048_577)
        p = self.cli(*self.args())
        self.assertEqual(2, p.returncode)
        self.assertNotIn(str(self.root), p.stderr + p.stdout)

    def test_cli_path_and_pattern_non_disclosure(self):
        self.source["sanitized_steps"][0]["evidence_ref"] = "mock.user@example.com"
        self.write_all()
        p = self.cli(*self.args())
        self.assertEqual(2, p.returncode)
        self.assertNotIn("mock.user@example.com", p.stdout + p.stderr)
        self.assertNotIn(str(self.root), p.stdout + p.stderr)

    def test_cli_missing_file_is_generic(self):
        self.manifest_path.unlink()
        p = self.cli(*self.args())
        self.assertEqual(2, p.returncode)
        self.assertIn("EVIDENCE_INPUT_REJECTED", p.stderr)
        self.assertNotIn(str(self.manifest_path), p.stderr)

    def test_no_network_ever(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(3, gate.verify(self.source, self.policy, self.claim)["event_count"])

    def test_scanner_is_heuristic_and_normal_code_is_not_blocked(self):
        d = copy.deepcopy(self.source)
        d["sanitized_steps"][0]["tool_code"] = "customer42"
        d["sanitized_steps"][0]["target_code"] = "generic"
        c = manifest(d, self.policy)
        result = gate.verify(d, self.policy, c)
        self.assertFalse(result["pii_absence_proven"])

    def test_cli_symlink_file_refused(self):
        link = self.root / "source-link.json"
        try:
            link.symlink_to(self.source_path)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable on this host")
        args = list(self.args())
        args[1] = str(link)
        p = self.cli(*args)
        self.assertEqual(2, p.returncode)
        self.assertIn("SYMLINK_INPUT_NOT_ALLOWED", p.stderr)

    def test_report_equivalence_not_consent(self):
        canonical = bridge.convert_synthetic(self.source, self.policy)
        self.assertEqual(5, evaluate(canonical)["finding_count"])
        self.assertFalse(gate.verify(self.source, self.policy, self.claim)["customer_authorization_verified"])


if __name__ == "__main__":
    unittest.main()
