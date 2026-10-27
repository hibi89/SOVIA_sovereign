"""Fabricated PUBLIC execution key names only; no n8n payloads or network."""
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
import sovia_n8n_execution_reference as ref
import sovia_n8n_pinned_reference as workflow_ref
import sovia_n8n_compatibility as old_probe


def fixture(version="1x"):
    p = ROOT / "examples" / ("n8n_pinned_execution_" + version + "_keys.json")
    return json.loads(p.read_text(encoding="utf-8"))


class ExecutionPublicContractTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.file = self.root / "names.json"
        self.save(fixture())

    def save(self, doc):
        self.file.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")

    def cli(self, *opts):
        return subprocess.run(
            [sys.executable, "-I", "-B",
             str(ROOT / "sovia_n8n_execution_reference.py"), *opts],
            capture_output=True, text=True, timeout=20)

    def test_pinned_release_commit_ids_match_workflow_reference(self):
        for tag in ref.PROFILES:
            with self.subTest(tag=tag):
                self.assertEqual(workflow_ref.SCHEMAS[tag]["commit"],
                                 ref.PROFILES[tag]["release_commit"])

    def test_exact_official_1x_execution_schema_blob(self):
        self.assertEqual("e20e27a02402563f3904c8b0468d56d32a42196c",
                         ref.PROFILES["n8n@1.123.88"]["source_blob_sha"])
        self.assertEqual("f8b60da7a25c09cdad6d31d4f7b22f4a430a2d58",
                         ref.PROFILES["n8n@1.123.88"]["operation_blob_sha"])

    def test_exact_official_2x_generated_operation_blob(self):
        self.assertEqual("329097122a6bfda7410314ff4ca73878c34b6918",
                         ref.PROFILES["n8n@2.44.7"]["source_blob_sha"])
        self.assertEqual(ref.PROFILES["n8n@2.44.7"]["source_blob_sha"],
                         ref.PROFILES["n8n@2.44.7"]["operation_blob_sha"])

    def test_property_delta_counts(self):
        delta = ref.public_delta()
        self.assertEqual(12, delta["older_property_count"])
        self.assertEqual(23, delta["newer_property_count"])
        self.assertEqual(11, len(delta["added_response_property_names"]))
        self.assertEqual([], delta["removed_response_property_names"])

    def test_declared_id_type_drift(self):
        self.assertEqual(["id", "retryOf", "retrySuccessId", "workflowId"],
                         ref.public_delta()["four_id_fields_with_changed_declared_types"])
        for key in ("id", "retryOf", "retrySuccessId", "workflowId"):
            self.assertEqual("number", ref.PROFILES["n8n@1.123.88"]["types"][key])
            self.assertEqual("string", ref.PROFILES["n8n@2.44.7"]["types"][key])

    def test_required_count_2x_is_19_1x_unstated(self):
        self.assertEqual(0, len(ref.PROFILES["n8n@1.123.88"]["required"]))
        self.assertEqual(19, len(ref.PROFILES["n8n@2.44.7"]["required"]))

    def test_declared_public_get_query_privacy_flags_without_api_support(self):
        delta = ref.public_delta()
        self.assertTrue(delta["older_includeData_query_declared"])
        self.assertTrue(delta["newer_includeData_default_false_declared"])
        self.assertTrue(delta["newer_redactExecutionData_query_declared"])
        self.assertTrue(delta["newer_ignoreDataSizeLimit_query_declared"])
        self.assertFalse(delta["raw_n8n_import_supported"])

    def test_fabricated_both_versions_recognized_but_blocked(self):
        for version in ("1x", "2x"):
            with self.subTest(version=version):
                r = ref.compare(fixture(version))
                self.assertEqual("PUBLIC_EXECUTION_KEYSET_ONLY_IMPORT_BLOCKED", r["status"])
                for field in ("raw_n8n_import_supported", "request_performed",
                              "conversion_performed", "n8n_instance_version_verified",
                              "customer_authorization_verified", "pii_redaction_verified"):
                    self.assertFalse(r[field])

    def test_future_optional_2x_field_refused_on_1x(self):
        d = fixture("2x")
        d["pinned_release_tag"] = "n8n@1.123.88"
        with self.assertRaisesRegex(ref.ExecutionReferenceError, "UNKNOWN_PUBLIC_EXECUTION_FIELD"):
            ref.compare(d)

    def test_all_content_bearing_keys_rejected(self):
        for tag, version in (("n8n@1.123.88", "1x"), ("n8n@2.44.7", "2x")):
            for key in ("data", "customData", "workflowData"):
                d = fixture(version)
                d["field_keys"].append(key)
                with self.subTest(tag=tag, key=key), self.assertRaisesRegex(
                    ref.ExecutionReferenceError, "EXECUTION_PAYLOAD_FIELD_BLOCKED"
                ):
                    ref.compare(d)

    def test_empty_field_list_is_not_usable(self):
        d = fixture()
        d["field_keys"] = []
        self.assertEqual("PUBLIC_EXECUTION_KEYSET_ONLY_IMPORT_BLOCKED",
                         ref.compare(d)["status"])

    def test_invalid_outer_manifest_rejected(self):
        for d in ({}, {"id": "42", "data": {}}, [], None, {"status": "success"}):
            with self.subTest(d=d), self.assertRaisesRegex(
                ref.ExecutionReferenceError, "INVALID_EXECUTION_REFERENCE_ENVELOPE"
            ):
                ref.compare(d)

    def test_extra_payload_field_in_manifest_rejected(self):
        d = fixture()
        d["items"] = [{"secret": "do-not-report"}]
        with self.assertRaisesRegex(ref.ExecutionReferenceError, "INVALID_EXECUTION_REFERENCE_ENVELOPE"):
            ref.compare(d)

    def test_false_synthetic_assertions_rejected(self):
        for v in (False, "true", 1, None):
            d = fixture()
            d["synthetic_only"] = v
            with self.subTest(v=v), self.assertRaisesRegex(
                ref.ExecutionReferenceError, "INVALID_EXECUTION_REFERENCE_ENVELOPE"
            ):
                ref.compare(d)

    def test_unpinned_version_tags_rejected(self):
        for tag in ("n8n@2.44.8", "n8n@1.123.89", "n8n@2", "latest", "", 2, None):
            d = fixture()
            d["pinned_release_tag"] = tag
            with self.subTest(tag=tag), self.assertRaisesRegex(
                ref.ExecutionReferenceError, "UNPINNED_EXECUTION_RELEASE"
            ):
                ref.compare(d)

    def test_duplicate_or_invalid_key_rejected(self):
        for fields in (["id", "id"], ["x@y"], ["abc.def"], [""], [1], [None],
                       ["x"*41], [f"k{i}" for i in range(31)]):
            d = fixture()
            d["field_keys"] = fields
            with self.subTest(fields=fields[:2]), self.assertRaisesRegex(
                ref.ExecutionReferenceError, "INVALID_EXECUTION_KEY_NAMES"
            ):
                ref.compare(d)

    def test_unknown_innocent_looking_name_rejected(self):
        d = fixture()
        d["field_keys"] = ["id", "hypotheticalNewStatus"]
        with self.assertRaisesRegex(ref.ExecutionReferenceError, "UNKNOWN_PUBLIC_EXECUTION_FIELD"):
            ref.compare(d)

    def test_wrong_source_family_rejected(self):
        d = fixture()
        d["source_kind"] = "raw_public_api_execution_response"
        with self.assertRaisesRegex(ref.ExecutionReferenceError, "INVALID_EXECUTION_REFERENCE_ENVELOPE"):
            ref.compare(d)

    def test_cli_known_keyset_exit3_no_import(self):
        p = self.cli("--input", str(self.file), "--synthetic-only")
        self.assertEqual(3, p.returncode, p.stderr)
        r = json.loads(p.stdout)
        self.assertFalse(r["request_performed"])
        self.assertFalse(r["conversion_performed"])
        self.assertNotIn(str(self.root), p.stdout + p.stderr)

    def test_cli_requires_synthetic_only_flag(self):
        p = self.cli("--input", str(self.file))
        self.assertEqual(2, p.returncode)
        self.assertIn("SYNTHETIC_MANIFEST_REQUIRED", p.stderr)

    def test_cli_no_input_no_work(self):
        p = self.cli("--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)

    def test_cli_delta_only_no_execution(self):
        p = self.cli("--show-public-delta")
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertEqual(11, len(json.loads(p.stdout)["added_response_property_names"]))

    def test_cli_delta_refuses_input_or_synthetic_toggle(self):
        for args in (("--show-public-delta", "--synthetic-only"),
                     ("--show-public-delta", "--input", str(self.file))):
            p = self.cli(*args)
            self.assertEqual(2, p.returncode)

    def test_cli_duplicate_json_keys_no_traceback(self):
        self.file.write_text('{"schema_version":"a","schema_version":"b"}', encoding="utf-8")
        p = self.cli("--input", str(self.file), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)

    def test_cli_oversized_manifest_rejected_no_leak(self):
        self.file.write_bytes(b"x" * 1_048_577)
        p = self.cli("--input", str(self.file), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn(str(self.root), p.stderr)

    def test_injected_socket_connect_is_unused(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual("PUBLIC_EXECUTION_KEYSET_ONLY_IMPORT_BLOCKED",
                             ref.compare_file(self.file)["status"])

    def test_existing_raw_profile_still_blocked(self):
        p = ROOT / "examples" / "synthetic_n8n_probe_mock_2x.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        self.assertEqual("UNVERIFIED_RAW_PROFILE_BLOCKED", old_probe.probe(d)["status"])


if __name__ == "__main__":
    unittest.main()
