"""P2 fabricated n8n summary and already-sanitized steps, never raw APIs."""
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
import sovia_n8n_execution_bridge as bridge
import sovia_n8n_sanitized as original
from sovia_audit import evaluate, read_document


def sample(version="2x"):
    return json.loads((ROOT / "examples" / ("synthetic_n8n_bridge_" + version + ".json")).read_text(encoding="utf-8"))


def policy():
    return read_document(ROOT / "examples" / "demo_policy.json")


class SyntheticExecutionBridgeTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.src = self.root / "fabricated.json"
        self.pol = self.root / "policy.json"
        self.out = self.root / "canonical.json"
        self.save()

    def save(self, doc=None, pol=None):
        self.src.write_text(json.dumps(sample() if doc is None else doc), encoding="utf-8")
        self.pol.write_text(json.dumps(policy() if pol is None else pol), encoding="utf-8")

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_n8n_execution_bridge.py"), *args],
            capture_output=True, text=True, timeout=20)

    def test_both_pinned_synthetic_versions_produce_3_events_five_findings(self):
        for version in ("1x", "2x"):
            with self.subTest(version=version):
                canonical = bridge.convert_synthetic(sample(version), policy())
                report = evaluate(canonical)
                self.assertEqual((3, 5), (report["event_count"], report["finding_count"]))

    def test_canonical_report_matches_existing_sanitized_converter(self):
        doc = sample()
        expected = original.convert({
            "format": original.FORMAT, "workflow_id": "wf_201",
            "execution_id": "exec_101", "steps": doc["sanitized_steps"],
        }, policy())
        self.assertEqual(expected, bridge.convert_synthetic(doc, policy()))

    def test_unknown_observation_stays_unknown_and_not_fabricated(self):
        doc = sample()
        doc["execution_summary"]["status"] = "success"
        canon = bridge.convert_synthetic(doc, policy())
        self.assertEqual(3, len(canon["events"]))
        self.assertEqual("unknown", canon["events"][-1]["outcome"])
        self.assertIsNone(canon["events"][-1]["source_pointer"])
        self.assertFalse(canon["events"][-1]["permission_asserted"])
        self.assertEqual("unauthorized_export", canon["events"][-1]["tool_name"])

    def test_execution_summary_status_never_becomes_tool_outcome(self):
        d = sample()
        for status in sorted(bridge.STATUSES):
            d["execution_summary"]["status"] = status
            with self.subTest(status=status):
                canon = bridge.convert_synthetic(d, policy())
                self.assertEqual(["success", "success", "unknown"],
                                 [e["outcome"] for e in canon["events"]])

    def test_summary_start_time_does_not_replace_step_times(self):
        d = sample()
        d["execution_summary"]["startedAt"] = "2025-01-02T03:04:05Z"
        c = bridge.convert_synthetic(d, policy())
        self.assertEqual("2026-10-26T00:01:00+09:00", c["events"][0]["occurred_at_utc"])
        self.assertEqual("2026-10-25T15:01:00Z", evaluate(c)["events"][0]["occurred_at_utc"])

    def test_v1_numeric_id_types_enforced(self):
        for val in ("101", True, 0, -1, 1.3, None, [], {}, 10**13):
            d = sample("1x")
            d["execution_summary"]["id"] = val
            with self.subTest(val=val), self.assertRaisesRegex(bridge.BridgeError, "SYNTHETIC_ID_TYPE_MISMATCH"):
                bridge.convert_synthetic(d, policy())

    def test_v2_string_id_types_enforced(self):
        for val in (101, True, None, 0, -1, "0", "001", "-1", "a123",
                    "person@example.com", "1"*14, "", "1.0"):
            d = sample("2x")
            d["execution_summary"]["workflowId"] = val
            with self.subTest(val=val), self.assertRaisesRegex(bridge.BridgeError, "SYNTHETIC_ID_TYPE_MISMATCH"):
                bridge.convert_synthetic(d, policy())

    def test_v2_accepts_canonical_positive_numeric_strings(self):
        d = sample("2x")
        d["execution_summary"]["id"] = "999999999999"
        canon = bridge.convert_synthetic(d, policy())
        self.assertEqual("exec_999999999999", canon["events"][0]["run_id"])

    def test_unpinned_release_tags_rejected(self):
        for value in ("n8n@2.44.8", "n8n@1.123.89", "latest", "", None, 1):
            d = sample()
            d["pinned_release_tag"] = value
            with self.subTest(value=value), self.assertRaisesRegex(bridge.BridgeError, "UNPINNED_RELEASE_BLOCKED"):
                bridge.convert_synthetic(d, policy())

    def test_raw_n8n_execution_object_rejected(self):
        with self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_BRIDGE_ENVELOPE"):
            bridge.convert_synthetic({"id": "101", "data": {"runData": []}}, policy())

    def test_raw_keys_blocked_at_top_level(self):
        for key in ("data", "credentials", "items", "workflowData", "customData", "prompt", "apiKey"):
            d = sample()
            d[key] = {"secret": "never-echo"}
            with self.subTest(key=key), self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_BRIDGE_ENVELOPE"):
                bridge.convert_synthetic(d, policy())

    def test_raw_keys_blocked_in_execution_summary(self):
        for key in ("data", "customData", "workflowData", "tracingContext",
                    "storedAt", "jsonSizeBytes", "retryOf"):
            d = sample()
            d["execution_summary"][key] = "secret"
            with self.subTest(key=key), self.assertRaisesRegex(bridge.BridgeError, "INVALID_EXECUTION_SUMMARY_FIELDS"):
                bridge.convert_synthetic(d, policy())

    def test_missing_summary_keys_fail_closed(self):
        for key in bridge.SUMMARY_KEYS:
            d = sample()
            del d["execution_summary"][key]
            with self.subTest(key=key), self.assertRaisesRegex(bridge.BridgeError, "INVALID_EXECUTION_SUMMARY_FIELDS"):
                bridge.convert_synthetic(d, policy())

    def test_missing_top_envelope_fields_fail_closed(self):
        for key in bridge.TOP_KEYS:
            d = sample()
            del d[key]
            with self.subTest(key=key), self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_BRIDGE_ENVELOPE"):
                bridge.convert_synthetic(d, policy())

    def test_not_real_or_unasserted_synthetic(self):
        for claim in (False, "true", 1, None):
            d = sample()
            d["synthetic_only"] = claim
            with self.subTest(claim=claim), self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_BRIDGE_ENVELOPE"):
                bridge.convert_synthetic(d, policy())

    def test_source_kind_never_raw_api(self):
        d = sample()
        d["source_kind"] = "n8n_actual_getExecution_api"
        with self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_BRIDGE_ENVELOPE"):
            bridge.convert_synthetic(d, policy())

    def test_invalid_execution_status_rejected(self):
        for val in ("completed", "unknown raw", None, 1, "SUCCESS"):
            d = sample()
            d["execution_summary"]["status"] = val
            with self.subTest(val=val), self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_EXECUTION_STATUS"):
                bridge.convert_synthetic(d, policy())

    def test_invalid_utc_timestamp_rejected(self):
        for val in (None, 1, "", "2026-10-25", "2026-10-25T15:01:00+00:00",
                    "2026-10-25T15:01:00+09:00", "2026-13-25T15:01:00Z",
                    "2026-10-25T99:01:00Z"):
            d = sample()
            d["execution_summary"]["startedAt"] = val
            with self.subTest(val=val), self.assertRaisesRegex(bridge.BridgeError, "INVALID_SYNTHETIC_STARTED_AT"):
                bridge.convert_synthetic(d, policy())

    def test_empty_steps_rejected_so_summary_is_not_a_fake_tool_event(self):
        d = sample()
        d["sanitized_steps"] = []
        with self.assertRaisesRegex(bridge.BridgeError, "SYNTHETIC_STEPS_REQUIRED"):
            bridge.convert_synthetic(d, policy())

    def test_large_or_nonlist_step_collection_rejected(self):
        for val in (None, {}, "step", [None]*1001):
            d = sample()
            d["sanitized_steps"] = val
            with self.subTest(type=type(val)), self.assertRaisesRegex(bridge.BridgeError, "SYNTHETIC_STEPS_REQUIRED"):
                bridge.convert_synthetic(d, policy())

    def test_steps_containing_raw_fields_rejected(self):
        for key in ("data", "items", "binary", "parameters", "credentials", "json", "prompt"):
            d = sample()
            d["sanitized_steps"][0][key] = "raw-data"
            with self.subTest(key=key), self.assertRaisesRegex(bridge.BridgeError, "PRE_SANITIZED_STEPS_OR_POLICY_REJECTED"):
                bridge.convert_synthetic(d, policy())

    def test_no_permission_or_destination_invention(self):
        d = sample()
        d["sanitized_steps"][0].pop("permission_asserted")
        d["sanitized_steps"][0].pop("destination_domain")
        canonical = bridge.convert_synthetic(d, policy())
        self.assertIsNone(canonical["events"][0]["permission_asserted"])
        self.assertIsNone(canonical["events"][0]["destination_domain"])

    def test_duplicate_or_bad_step_rejected_by_established_converter(self):
        d = sample()
        d["sanitized_steps"][1]["step_id"] = d["sanitized_steps"][0]["step_id"]
        with self.assertRaisesRegex(bridge.BridgeError, "PRE_SANITIZED_STEPS_OR_POLICY_REJECTED"):
            bridge.convert_synthetic(d, policy())

    def test_invalid_policy_does_not_create_output(self):
        d = sample()
        pol = policy()
        pol["policy"]["secret"] = "private"
        with self.assertRaisesRegex(bridge.BridgeError, "PRE_SANITIZED_STEPS_OR_POLICY_REJECTED"):
            bridge.convert_synthetic(d, pol)

    def test_bridge_rejects_pii_like_sanitized_codes(self):
        # All specimens are fabricated but conform to the CODE allowlist,
        # which previously let the bridge publish them into canonical JSON.
        for kind, value in (
            ("phone", "01012345678"),
            ("ipv4", "10.0.0.9"),
            ("api-token", "sk-" + "x" * 26),
        ):
            doc = sample()
            doc["sanitized_steps"][0]["evidence_ref"] = value
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(bridge.BridgeError, "^PREFLIGHT_REJECTED$"):
                    bridge.convert_synthetic(doc, policy())

    def test_bridge_rejects_suspect_policy_metadata(self):
        config = policy()
        config["policy"]["allowed_tools"].append("sk-" + "z" * 27)
        with self.assertRaisesRegex(bridge.BridgeError, "^PREFLIGHT_REJECTED$"):
            bridge.convert_synthetic(sample(), config)

    def test_bridge_cli_rejects_suspect_metadata_without_output_or_echo(self):
        doc = sample()
        doc["sanitized_steps"][0]["evidence_ref"] = "01012345678"
        self.save(doc=doc)
        response = self.cli("--input", str(self.src), "--policy", str(self.pol),
                            "--output", str(self.out), "--synthetic-only")
        self.assertEqual(2, response.returncode)
        self.assertEqual(
            "PREFLIGHT_REJECTED", json.loads(response.stderr)["error_code"]
        )
        self.assertFalse(self.out.exists())
        self.assertNotIn("01012345678", response.stdout + response.stderr)
        self.assertNotIn(str(self.root), response.stdout + response.stderr)

    def test_cli_requires_synthetic_ack_and_makes_no_output(self):
        proc = self.cli("--input", str(self.src), "--policy", str(self.pol), "--output", str(self.out))
        self.assertEqual(2, proc.returncode)
        self.assertFalse(self.out.exists())

    def test_cli_clean_end_to_end_to_real_auditor(self):
        proc = self.cli("--input", str(self.src), "--policy", str(self.pol),
                        "--output", str(self.out), "--synthetic-only")
        self.assertEqual(0, proc.returncode, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual("CONVERTED_SYNTHETIC_STEPS_ONLY", result["status"])
        self.assertEqual(3, result["event_count"])
        for flag in ("n8n_api_called", "real_n8n_execution_import_supported",
                     "version_independently_verified", "authorization_independently_verified",
                     "pii_absence_proven", "synthetic_claim_independently_verified",
                     "summary_status_used_as_tool_evidence"):
            self.assertFalse(result[flag])
        report = evaluate(read_document(self.out))
        self.assertEqual(5, report["finding_count"])

    def test_cli_output_no_overwrite(self):
        self.out.write_text("protected", encoding="utf-8")
        proc = self.cli("--input", str(self.src), "--policy", str(self.pol),
                        "--output", str(self.out), "--synthetic-only")
        self.assertEqual(2, proc.returncode)
        self.assertEqual("protected", self.out.read_text(encoding="utf-8"))

    def test_cli_output_input_alias_rejected(self):
        proc = self.cli("--input", str(self.src), "--policy", str(self.pol),
                        "--output", str(self.src), "--synthetic-only")
        self.assertEqual(2, proc.returncode)
        self.assertIn("OUTPUT_ALIASES_INPUT", proc.stderr)

    def test_cli_oversize_and_duplicate_json_fail_with_fixed_error(self):
        self.src.write_bytes(b" " * 1_048_577)
        p = self.cli("--input", str(self.src), "--policy", str(self.pol),
                     "--output", str(self.out), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertFalse(self.out.exists())
        self.src.write_text('{"format":"x","format":"y"}', encoding="utf-8")
        p = self.cli("--input", str(self.src), "--policy", str(self.pol),
                     "--output", str(self.out), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn("Traceback", p.stderr)

    def test_no_path_or_secret_echo_on_failed_input(self):
        d = sample()
        d["data"] = {"secret": "DO_NOT_ECHO_382"}
        self.save(doc=d)
        p = self.cli("--input", str(self.src), "--policy", str(self.pol),
                     "--output", str(self.out), "--synthetic-only")
        self.assertEqual(2, p.returncode)
        self.assertNotIn("DO_NOT_ECHO_382", p.stderr + p.stdout)
        self.assertNotIn(str(self.root), p.stderr + p.stdout)
        self.assertFalse(self.out.exists())

    def test_synthetic_steps_preserve_old_rules_without_network(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("unexpected network")):
            report = evaluate(bridge.convert_synthetic(sample(), policy()))
        self.assertEqual({"UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION",
                          "SENSITIVE_ACCESS", "MISSING_EVIDENCE", "BURST_TOOLS"},
                         {f["rule_id"] for f in report["findings"]})


if __name__ == "__main__":
    unittest.main()
