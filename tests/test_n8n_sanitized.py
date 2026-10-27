"""Synthetic-only fail-closed contract and existing-audit integration checks."""
import copy
import json
import os
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
from sovia_audit import evaluate, read_document


def fixture():
    return {
        "format": adapter.FORMAT, "workflow_id": "synthetic_wf",
        "execution_id": "synthetic_run", "steps": [
            {"step_id": "node-1", "occurred_at_utc": "2026-10-26T00:01:00+09:00",
             "tool_code": "approved_lookup", "target_code": "public_docs",
             "destination_domain": "internal.example", "permission_asserted": True,
             "outcome_code": "success", "evidence_ref": "synthetic:1"},
            {"step_id": "node-2", "occurred_at_utc": "2026-10-26T00:01:15+09:00",
             "tool_code": "approved_lookup", "target_code": "public_docs",
             "destination_domain": "internal.example", "permission_asserted": True,
             "outcome_code": "success", "evidence_ref": "synthetic:2"},
            {"step_id": "node-3", "occurred_at_utc": "2026-10-26T00:01:30+09:00",
             "tool_code": "unauthorized_export", "target_code": "client_records",
             "destination_domain": "outside.example", "permission_asserted": False,
             "outcome_code": "unknown"},
        ],
    }


def policy():
    return {"schema_version": "1.0", "policy": {
        "allowed_tools": ["approved_lookup"],
        "approved_destinations": ["internal.example"],
        "sensitive_targets": ["client_records"],
        "max_tool_calls_per_minute": 2,
    }}


class N8nSanitizedContractTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.input = self.root / "events.json"
        self.policy = self.root / "policy.json"
        self.output = self.root / "canonical.json"
        self.store()

    def store(self, doc=None, policy_doc=None):
        self.input.write_text(json.dumps(fixture() if doc is None else doc), encoding="utf-8")
        self.policy.write_text(json.dumps(policy() if policy_doc is None else policy_doc), encoding="utf-8")

    def test_three_events_five_findings_through_existing_engine(self):
        converted = adapter.convert(fixture(), policy())
        report = evaluate(converted)
        self.assertEqual((3, 5), (report["event_count"], report["finding_count"]))
        self.assertEqual({"UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION",
                          "SENSITIVE_ACCESS", "MISSING_EVIDENCE", "BURST_TOOLS"},
                         {f["rule_id"] for f in report["findings"]})

    def test_never_infer_permission_or_evidence(self):
        canonical = adapter.convert(fixture(), policy())
        self.assertIsNone(canonical["events"][-1]["source_pointer"])
        self.assertIs(False, canonical["events"][-1]["permission_asserted"])
        doc = fixture()
        doc["steps"][0].pop("permission_asserted")
        self.assertIsNone(adapter.convert(doc, policy())["events"][0]["permission_asserted"])

    def test_no_raw_params_result_data_or_credentials_in_output(self):
        self.assertFalse({"parameters", "data", "credentials", "items"} &
                         set(adapter.convert(fixture(), policy())["events"][0]))

    def test_reject_raw_n8n_execution_export(self):
        with self.assertRaisesRegex(adapter.ContractError, "UNSUPPORTED_SANITIZED_ENVELOPE"):
            adapter.convert({"id": "a", "data": {"resultData": {}}}, policy())

    def test_reject_extraneous_top_level_payload(self):
        bad = fixture()
        bad["apiToken"] = "secret"
        with self.assertRaisesRegex(adapter.ContractError, "UNSUPPORTED_SANITIZED_ENVELOPE"):
            adapter.convert(bad, policy())

    def test_reject_unallowlisted_step_fields(self):
        for field in ("data", "json", "binary", "parameters", "credentials", "prompt", "email"):
            with self.subTest(field=field):
                bad = fixture()
                bad["steps"][0][field] = "private"
                with self.assertRaisesRegex(adapter.ContractError, "UNSUPPORTED_STEP_FIELDS"):
                    adapter.convert(bad, policy())

    def test_reject_duplicate_step_id(self):
        bad = fixture()
        bad["steps"][1]["step_id"] = "node-1"
        with self.assertRaisesRegex(adapter.ContractError, "DUPLICATE_STEP_ID"):
            adapter.convert(bad, policy())

    def test_reject_missing_required_fields(self):
        for field in ("step_id", "tool_code", "occurred_at_utc"):
            with self.subTest(field=field):
                bad = fixture()
                del bad["steps"][0][field]
                with self.assertRaisesRegex(adapter.ContractError, "UNSUPPORTED_STEP_FIELDS"):
                    adapter.convert(bad, policy())

    def test_reject_bad_permission_flag(self):
        for value in ("true", 1, [], {}):
            with self.subTest(value=value):
                bad = fixture()
                bad["steps"][0]["permission_asserted"] = value
                with self.assertRaisesRegex(adapter.ContractError, "INVALID_PERMISSION_ASSERTION"):
                    adapter.convert(bad, policy())

    def test_reject_raw_identifiers_and_outcome(self):
        for field, value in (("step_id", "person@example.com"),
                             ("tool_code", "HTTP Request <script>"),
                             ("target_code", "user email@example.com"),
                             ("evidence_ref", "https://private.example/path")):
            with self.subTest(field=field):
                bad = fixture()
                bad["steps"][0][field] = value
                with self.assertRaises(adapter.ContractError):
                    adapter.convert(bad, policy())
        bad = fixture()
        bad["steps"][0]["outcome_code"] = "secret"
        with self.assertRaisesRegex(adapter.ContractError, "INVALID_OUTCOME_CODE"):
            adapter.convert(bad, policy())

    def test_reject_invalid_domain_and_timestamp(self):
        bad = fixture()
        bad["steps"][0]["destination_domain"] = "https://internal.example"
        with self.assertRaisesRegex(adapter.ContractError, "CANONICAL_VALIDATION_FAILED"):
            adapter.convert(bad, policy())
        bad = fixture()
        bad["steps"][0]["occurred_at_utc"] = "2026-01-01T00:00:00"
        with self.assertRaisesRegex(adapter.ContractError, "CANONICAL_VALIDATION_FAILED"):
            adapter.convert(bad, policy())

    def test_reject_policy_metadata_extension(self):
        p = policy()
        p["policy"]["private_api_key"] = "secret"
        with self.assertRaisesRegex(adapter.ContractError, "INVALID_POLICY_KEYS"):
            adapter.convert(fixture(), p)

    def test_reject_over_limit_without_truncation(self):
        bad = fixture()
        bad["steps"] = [dict(bad["steps"][0], step_id=f"node-{i}")
                        for i in range(adapter.MAX_STEPS + 1)]
        with self.assertRaisesRegex(adapter.ContractError, "INVALID_STEPS"):
            adapter.convert(bad, policy())

    def test_input_output_no_clobber(self):
        self.output.write_text("untouched", encoding="utf-8")
        with self.assertRaises(adapter.ContractError):
            adapter.convert_paths(self.input, self.policy, self.output)
        self.assertEqual("untouched", self.output.read_text(encoding="utf-8"))

    def test_reject_output_alias_original_or_policy(self):
        for path in (self.input, self.policy):
            before = path.read_bytes()
            with self.assertRaisesRegex(adapter.ContractError, "OUTPUT_ALIASES_INPUT"):
                adapter.convert_paths(self.input, self.policy, path)
            self.assertEqual(before, path.read_bytes())

    def test_existing_originals_unchanged_on_conversion(self):
        before = (self.input.read_bytes(), self.policy.read_bytes())
        self.assertEqual(3, adapter.convert_paths(self.input, self.policy, self.output))
        self.assertEqual(before, (self.input.read_bytes(), self.policy.read_bytes()))
        self.assertEqual(5, evaluate(read_document(self.output))["finding_count"])

    def test_offline_no_network(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(3, adapter.convert_paths(self.input, self.policy, self.output))

    def test_duplicate_json_keys_fail_closed_without_output(self):
        self.input.write_text('{"format":"sovia.n8n_sanitized.v1","format":"unexpected"}', encoding="utf-8")
        with self.assertRaises(adapter.ContractError):
            adapter.convert_paths(self.input, self.policy, self.output)
        self.assertFalse(self.output.exists())

    def test_oversized_input_no_output(self):
        self.input.write_bytes(b"x" * (1_048_576 + 1))
        with self.assertRaises(adapter.ContractError):
            adapter.convert_paths(self.input, self.policy, self.output)
        self.assertFalse(self.output.exists())

    def test_cli_isolated_python_and_redacted_messages(self):
        exe = ROOT / "sovia_n8n_sanitized.py"
        cmd = [sys.executable, "-I", "-B", str(exe), "--input", str(self.input),
               "--policy", str(self.policy), "--output", str(self.output)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(3, json.loads(result.stdout)["events"])
        self.assertNotIn(str(self.root), result.stdout)
        denied = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(2, denied.returncode)
        self.assertNotIn(str(self.root), denied.stderr)


if __name__ == "__main__":
    unittest.main()
