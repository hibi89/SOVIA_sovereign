"""SOVIA synthetic n8n field/version CLAIM probes; no raw exports accepted."""
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
import sovia_n8n_compatibility as compat
import sovia_n8n_sanitized as adapter


def manifest(name="sanitized"):
    filename = {
        "sanitized": "synthetic_n8n_probe_sanitized_v1.json",
        "1x": "synthetic_n8n_probe_mock_1x.json",
        "2x": "synthetic_n8n_probe_mock_2x.json",
    }[name]
    return json.loads((ROOT / "examples" / filename).read_text(encoding="utf-8"))


class CompatibilityProbeTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.file = self.root / "manifest.json"
        self.save(manifest())

    def save(self, value):
        self.file.write_text(json.dumps(value), encoding="utf-8")

    def cli(self, *flags):
        return subprocess.run([sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_compatibility.py"),
                               "--input", str(self.file), *flags],
                              text=True, capture_output=True, timeout=20)

    def test_sanitized_keyset_match_does_not_prove_n8n(self):
        out = compat.probe(manifest())
        self.assertEqual("SYNTHETIC_SANITIZED_KEYSET_MATCH_ONLY", out["status"])
        self.assertEqual(0, out["missing_expected_key_count"])
        self.assertFalse(out["native_n8n_schema_compatibility_verified"])
        self.assertFalse(out["source_authorization_verified"])
        self.assertFalse(out["conversion_performed"])

    def test_mock_1x_workflow_is_blocked_even_with_keys(self):
        out = compat.probe(manifest("1x"))
        self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", out["status"])
        self.assertEqual("mock_1_x", out["version_claim_bucket"])
        self.assertFalse(out["raw_n8n_import_supported"])

    def test_mock_2x_execution_is_blocked_even_with_keys(self):
        out = compat.probe(manifest("2x"))
        self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", out["status"])
        self.assertEqual("mock_2_x", out["version_claim_bucket"])
        self.assertFalse(out["n8n_version_independently_verified"])

    def test_future_version_claim_never_becomes_supported(self):
        data = manifest("2x")
        data["claimed_n8n_version"] = "3.99.9"
        self.assertEqual("UNRECOGNIZED_VERSION_BLOCKED", compat.probe(data)["status"])

    def test_patch_version_does_not_change_raw_block(self):
        for vers in ("1.2.3", "2.99.0"):
            with self.subTest(vers=vers):
                data = manifest("1x")
                data["claimed_n8n_version"] = vers
                self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", compat.probe(data)["status"])

    def test_invalid_version_format_rejected(self):
        for vers in ("1", "v1.0.0", "1.x", "0.0.1", "2.0.0-alpha", "1.02.0", 2, None):
            with self.subTest(vers=vers):
                data = manifest("2x")
                data["claimed_n8n_version"] = vers
                with self.assertRaisesRegex(compat.ProbeError, "INVALID_N8N_VERSION_CLAIM"):
                    compat.probe(data)

    def test_sanitized_profile_must_not_advertise_n8n_version(self):
        data = manifest()
        data["claimed_n8n_version"] = "2.6.4"
        with self.assertRaisesRegex(compat.ProbeError, "SANITIZED_PROFILE_REQUIRES_NO_N8N_VERSION"):
            compat.probe(data)

    def test_missing_sanitized_key_returns_blocked_not_success(self):
        data = manifest()
        data["field_keys"].remove("steps")
        output = compat.probe(data)
        self.assertEqual("INCOMPLETE_SANITIZED_KEYSET_BLOCKED", output["status"])
        self.assertEqual(1, output["missing_expected_key_count"])

    def test_missing_raw_key_remains_unverified_and_blocked(self):
        data = manifest("2x")
        data["field_keys"].remove("status")
        output = compat.probe(data)
        self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", output["status"])
        self.assertEqual(1, output["missing_expected_key_count"])

    def test_raw_payload_keys_always_rejected(self):
        for field in ("data", "credentials", "parameters", "runData", "pinData",
                      "binary", "items", "prompt", "json", "token", "resultData"):
            with self.subTest(field=field):
                data = manifest("1x")
                data["field_keys"].append(field)
                with self.assertRaisesRegex(compat.ProbeError, "RAW_PAYLOAD_FIELD_BLOCKED"):
                    compat.probe(data)

    def test_raw_like_payload_in_sanitized_profile_rejected(self):
        data = manifest()
        data["field_keys"].append("credentials")
        with self.assertRaisesRegex(compat.ProbeError, "RAW_PAYLOAD_FIELD_BLOCKED"):
            compat.probe(data)

    def test_unknown_sanitized_field_rejected(self):
        data = manifest()
        data["field_keys"].append("allowUnsafe")
        with self.assertRaisesRegex(compat.ProbeError, "UNKNOWN_SANITIZED_FIELD_BLOCKED"):
            compat.probe(data)

    def test_unknown_raw_profile_field_rejected(self):
        data = manifest("1x")
        data["field_keys"].append("debugFlags")
        with self.assertRaisesRegex(compat.ProbeError, "UNKNOWN_RAW_PROFILE_FIELD_BLOCKED"):
            compat.probe(data)

    def test_raw_n8n_export_cannot_be_used_as_manifest(self):
        for raw in (
            {"name": "example", "nodes": [], "connections": {}},
            {"id": "run_1", "workflowId": "workflow_1", "data": {}},
        ):
            with self.subTest(raw=list(raw)):
                with self.assertRaisesRegex(compat.ProbeError, "INVALID_PROBE_ENVELOPE"):
                    compat.probe(raw)

    def test_unknown_profile_rejected(self):
        data = manifest()
        data["source_profile"] = "real_n8n"
        with self.assertRaisesRegex(compat.ProbeError, "UNRECOGNIZED_SOURCE_PROFILE"):
            compat.probe(data)

    def test_only_exact_boolean_true_allows_synthetic_probe(self):
        for value in (False, 1, "true", None):
            with self.subTest(value=value):
                data = manifest()
                data["synthetic_only"] = value
                with self.assertRaisesRegex(compat.ProbeError, "INVALID_PROBE_ENVELOPE"):
                    compat.probe(data)

    def test_nonallowlisted_top_field_rejected(self):
        data = manifest()
        data["customer_email"] = "private"
        with self.assertRaisesRegex(compat.ProbeError, "INVALID_PROBE_ENVELOPE"):
            compat.probe(data)

    def test_malformed_field_keys_rejected(self):
        for field in ("customer@example.com", "name.value", "local/path", "A"*41, "", 8, None):
            with self.subTest(field=field):
                data = manifest()
                data["field_keys"][0] = field
                with self.assertRaisesRegex(compat.ProbeError, "INVALID_FIELD_KEY_MANIFEST"):
                    compat.probe(data)

    def test_duplicate_field_keys_rejected(self):
        data = manifest()
        data["field_keys"].append(data["field_keys"][0])
        with self.assertRaisesRegex(compat.ProbeError, "INVALID_FIELD_KEY_MANIFEST"):
            compat.probe(data)

    def test_too_many_keys_rejected(self):
        data = manifest()
        data["field_keys"] = [f"fake{i}" for i in range(compat.MAX_KEYS+1)]
        with self.assertRaisesRegex(compat.ProbeError, "INVALID_FIELD_KEY_MANIFEST"):
            compat.probe(data)

    def test_cli_requires_acknowledgement(self):
        p = self.cli()
        self.assertEqual(2, p.returncode)
        self.assertIn("SYNTHETIC_ONLY_ACK_REQUIRED", p.stderr)

    def test_cli_synthetic_success_in_isolated_python(self):
        p = self.cli("--synthetic-only")
        self.assertEqual(0, p.returncode, p.stderr)
        data = json.loads(p.stdout)
        self.assertFalse(data["raw_n8n_import_supported"])
        self.assertNotIn(str(self.root), p.stdout + p.stderr)

    def test_cli_mock_version_returns_block_code_three(self):
        self.save(manifest("2x"))
        p = self.cli("--synthetic-only")
        self.assertEqual(3, p.returncode, p.stderr)
        self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", json.loads(p.stdout)["status"])

    def test_cli_missing_sanitized_key_returns_three(self):
        d = manifest()
        d["field_keys"].remove("steps")
        self.save(d)
        self.assertEqual(3, self.cli("--synthetic-only").returncode)

    def test_cli_raw_export_returns_fixed_code_without_paths(self):
        self.save({"name":"fake","nodes":[],"connections":{}})
        p = self.cli("--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn(str(self.root), p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("INVALID_PROBE_ENVELOPE", p.stderr)

    def test_duplicate_json_keys_refused(self):
        self.file.write_text('{"schema_version":"x","schema_version":"y"}', encoding="utf-8")
        p = self.cli("--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)

    def test_oversized_input_refused(self):
        self.file.write_bytes(b" " * 1_048_577)
        self.assertEqual(2, self.cli("--synthetic-only").returncode)

    def test_no_network_connection(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("no network")):
            self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED",
                             compat.probe_file(ROOT / "examples/synthetic_n8n_probe_mock_2x.json")["status"])

    def test_existing_adapter_still_rejects_raw_export(self):
        from sovia_audit import read_document
        policy = read_document(ROOT / "examples/demo_policy.json")
        with self.assertRaises(adapter.ContractError):
            adapter.convert({"nodes":[],"connections":{}}, policy)

    def test_existing_adapter_synthetic_still_produces_five_findings(self):
        from sovia_audit import evaluate, read_document
        source = read_document(ROOT / "examples/demo_n8n_sanitized.json")
        policy = read_document(ROOT / "examples/demo_policy.json")
        self.assertEqual(5, evaluate(adapter.convert(source, policy))["finding_count"])


if __name__ == "__main__":
    unittest.main()
