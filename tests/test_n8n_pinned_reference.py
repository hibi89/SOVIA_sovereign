"""Synthetic pinned-public-schema key comparisons, not raw n8n interoperability."""
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
import sovia_n8n_pinned_reference as pinned
import sovia_n8n_compatibility as old_probe
import sovia_n8n_sanitized as sanitized


def fixture(name="1x"):
    file = "n8n_pinned_public_1x_keys.json" if name == "1x" else "n8n_pinned_public_2x_keys.json"
    return json.loads((ROOT / "examples" / file).read_text(encoding="utf-8"))


class PinnedOfficialReferenceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.input = self.root / "only_keys.json"
        self.save(fixture())

    def save(self, obj):
        self.input.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def cli(self, *flags):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_pinned_reference.py"), *flags],
            capture_output=True, text=True, timeout=20)

    def test_pinned_1x_release_commit_and_source_blob(self):
        ref = pinned.SCHEMAS["n8n@1.123.88"]
        self.assertEqual("6b88ad7f6be54df9f26efe17e0c249e345b40375", ref["commit"])
        self.assertEqual("7f36ea82d077db612b6cea4807ccaa7ee1e1227e", ref["schema_blob_sha"])
        self.assertEqual(12, len(ref["properties"]))

    def test_pinned_2x_release_commit_and_source_blob(self):
        ref = pinned.SCHEMAS["n8n@2.44.7"]
        self.assertEqual("cbe3950c51759577f9e611d28f8f5cd01828eaef", ref["commit"])
        self.assertEqual("0eb571b216406d9d2d4b6e072195a1296124e6fc", ref["schema_blob_sha"])
        self.assertEqual(21, len(ref["properties"]))

    def test_four_required_names_are_shared(self):
        self.assertEqual({"name","nodes","connections","settings"}, pinned.REQUIRED)
        for profile in pinned.SCHEMAS.values():
            self.assertTrue(pinned.REQUIRED.issubset(profile["properties"]))

    def test_referenced_public_difference_is_nine_added_zero_removed(self):
        delta = pinned.public_reference_delta()
        self.assertEqual([
            "activeVersionId", "description", "isArchived", "meta",
            "nodeGroups", "parentFolderId", "pinData", "triggerCount", "versionId"
        ], delta["added_public_property_names"])
        self.assertEqual([], delta["removed_public_property_names"])
        self.assertFalse(delta["native_api_integration_verified"])

    def test_both_examples_are_keyset_only_not_imported(self):
        for name in ("1x", "2x"):
            with self.subTest(name=name):
                result = pinned.compare_key_names(fixture(name))
                self.assertEqual("PINNED_PUBLIC_API_KEYSET_RECOGNIZED_IMPORT_BLOCKED", result["status"])
                self.assertFalse(result["raw_workflow_or_execution_import_supported"])
                self.assertFalse(result["native_api_integration_verified"])
                self.assertFalse(result["source_authorization_verified"])
                self.assertFalse(result["n8n_runtime_version_verified"])
                self.assertFalse(result["customer_payload_inspected"])
                self.assertFalse(result["conversion_performed"])

    def test_2x_keys_are_not_wrongly_accepted_as_1x(self):
        manifest = fixture("2x")
        manifest["pinned_release_tag"] = "n8n@1.123.88"
        with self.assertRaisesRegex(pinned.ReferenceError, "KEY_ABSENT_FROM_PINNED_API_SCHEMA"):
            pinned.compare_key_names(manifest)

    def test_required_key_missing_remains_blocked(self):
        for key in sorted(pinned.REQUIRED):
            with self.subTest(key=key):
                manifest = fixture()
                manifest["field_keys"].remove(key)
                result = pinned.compare_key_names(manifest)
                self.assertEqual("REQUIRED_PUBLIC_API_KEYS_MISSING_BLOCKED", result["status"])
                self.assertEqual(1, result["missing_required_key_count"])

    def test_missing_two_required_gives_exact_count(self):
        manifest = fixture()
        manifest["field_keys"] = ["id", "name", "settings"]
        result = pinned.compare_key_names(manifest)
        self.assertEqual(2, result["missing_required_key_count"])

    def test_empty_key_list_never_passes(self):
        manifest = fixture()
        manifest["field_keys"] = []
        self.assertEqual(4, pinned.compare_key_names(manifest)["missing_required_key_count"])

    def test_optional_static_data_key_explicitly_refused(self):
        for tag in ("n8n@1.123.88", "n8n@2.44.7"):
            with self.subTest(tag=tag):
                manifest = fixture()
                manifest["pinned_release_tag"] = tag
                manifest["field_keys"].append("staticData")
                with self.assertRaisesRegex(pinned.ReferenceError, "DATA_BEARING_OPTIONAL_FIELD_BLOCKED"):
                    pinned.compare_key_names(manifest)

    def test_optional_pinned_data_key_explicitly_refused(self):
        manifest = fixture("2x")
        manifest["field_keys"].append("pinData")
        with self.assertRaisesRegex(pinned.ReferenceError, "DATA_BEARING_OPTIONAL_FIELD_BLOCKED"):
            pinned.compare_key_names(manifest)

    def test_schema_doc_does_not_imply_field_values_are_safe(self):
        manifest = fixture()
        manifest["node_parameters"] = {"token": "do-not-process"}
        with self.assertRaisesRegex(pinned.ReferenceError, "INVALID_REFERENCE_ENVELOPE"):
            pinned.compare_key_names(manifest)

    def test_literal_raw_workflow_is_not_a_manifest(self):
        for raw in (
            {"name": "mock", "nodes": [], "connections": {}, "settings": {}},
            {"id": "mock", "data": {"runData": []}},
        ):
            with self.subTest(fields=list(raw)):
                with self.assertRaisesRegex(pinned.ReferenceError, "INVALID_REFERENCE_ENVELOPE"):
                    pinned.compare_key_names(raw)

    def test_unpinned_versions_rejected_even_plausible_semver(self):
        for version in ("n8n@1.123.89", "n8n@2.44.8", "n8n@2.45.0", "2.44.7", "latest", "", None):
            with self.subTest(version=version):
                manifest = fixture()
                manifest["pinned_release_tag"] = version
                with self.assertRaisesRegex(pinned.ReferenceError, "UNPINNED_RELEASE_BLOCKED"):
                    pinned.compare_key_names(manifest)

    def test_malformed_key_names_rejected(self):
        for key in ("user@example.com", "nodes.child", "http/path", "x"*41, "", 0, None):
            with self.subTest(key=key):
                manifest = fixture()
                manifest["field_keys"] = ["name", key]
                with self.assertRaisesRegex(pinned.ReferenceError, "INVALID_KEYSET_MANIFEST"):
                    pinned.compare_key_names(manifest)

    def test_duplicate_and_too_many_names_rejected(self):
        m = fixture()
        m["field_keys"] = ["name", "name"]
        with self.assertRaisesRegex(pinned.ReferenceError, "INVALID_KEYSET_MANIFEST"):
            pinned.compare_key_names(m)
        m["field_keys"] = [f"test{i}" for i in range(31)]
        with self.assertRaisesRegex(pinned.ReferenceError, "INVALID_KEYSET_MANIFEST"):
            pinned.compare_key_names(m)

    def test_extra_unknown_key_rejected_even_if_looks_harmless(self):
        m = fixture("2x")
        m["field_keys"].append("testFlags")
        with self.assertRaisesRegex(pinned.ReferenceError, "KEY_ABSENT_FROM_PINNED_API_SCHEMA"):
            pinned.compare_key_names(m)

    def test_wrong_source_kind_rejected(self):
        m = fixture()
        m["source_kind"] = "actual_execution_api"
        with self.assertRaisesRegex(pinned.ReferenceError, "INVALID_REFERENCE_ENVELOPE"):
            pinned.compare_key_names(m)

    def test_only_exact_true_synthetic_claim_allowed(self):
        for value in (False, None, 1, "true"):
            m = fixture()
            m["synthetic_only"] = value
            with self.subTest(value=value), self.assertRaisesRegex(pinned.ReferenceError, "INVALID_REFERENCE_ENVELOPE"):
                pinned.compare_key_names(m)

    def test_isolated_python_cli_always_blocks_import_even_known_keys(self):
        p = self.cli("--input", str(self.input), "--synthetic-only")
        self.assertEqual(3, p.returncode, p.stderr)
        d = json.loads(p.stdout)
        self.assertEqual("PINNED_PUBLIC_API_KEYSET_RECOGNIZED_IMPORT_BLOCKED", d["status"])
        self.assertFalse(d["conversion_performed"])
        self.assertNotIn(str(self.root), p.stdout + p.stderr)

    def test_cli_requires_synthetic_ack(self):
        p = self.cli("--input", str(self.input))
        self.assertEqual(2, p.returncode)
        self.assertIn("SYNTHETIC_MANIFEST_REQUIRED", p.stderr)

    def test_cli_public_delta_has_only_public_key_names(self):
        p = self.cli("--show-public-delta")
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertEqual(9, len(json.loads(p.stdout)["added_public_property_names"]))
        self.assertNotIn(str(self.root), p.stdout + p.stderr)

    def test_cli_cannot_mix_delta_with_input(self):
        p = self.cli("--show-public-delta", "--input", str(self.input))
        self.assertEqual(2, p.returncode)
        self.assertIn("DELTA_TAKES_NO_INPUT", p.stderr)

    def test_duplicate_keys_in_json_refused_without_traceback(self):
        self.input.write_text('{"schema_version":"x","schema_version":"y"}', encoding="utf-8")
        p = self.cli("--input", str(self.input), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)

    def test_oversized_manifest_refused_without_echo(self):
        self.input.write_bytes(b" " * 1_048_577)
        p = self.cli("--input", str(self.input), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn(str(self.root), p.stderr)

    def test_version_probe_existing_block_is_preserved(self):
        manifest = json.loads((ROOT / "examples/synthetic_n8n_probe_mock_2x.json").read_text(encoding="utf-8"))
        self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", old_probe.probe(manifest)["status"])

    def test_sanitized_converter_existing_five_findings_preserved(self):
        from sovia_audit import evaluate, read_document
        doc = read_document(ROOT / "examples/demo_n8n_sanitized.json")
        policy = read_document(ROOT / "examples/demo_policy.json")
        self.assertEqual(5, evaluate(sanitized.convert(doc, policy))["finding_count"])

    def test_no_socket_network(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual("PINNED_PUBLIC_API_KEYSET_RECOGNIZED_IMPORT_BLOCKED",
                             pinned.compare_file(self.input)["status"])


if __name__ == "__main__":
    unittest.main()
