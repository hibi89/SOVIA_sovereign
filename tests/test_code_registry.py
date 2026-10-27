"""Synthetic-only code-registry and policy-finding preservation regression tests."""
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
import sovia_code_registry as registry
from sovia_audit import evaluate, read_document


def fixtures():
    return (json.loads((ROOT / "examples/demo_n8n_sanitized.json").read_text(encoding="utf-8")),
            json.loads((ROOT / "examples/demo_policy.json").read_text(encoding="utf-8")),
            json.loads((ROOT / "examples/demo_code_registry.json").read_text(encoding="utf-8")))


class CodeRegistryTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.source = self.root / "source.json"
        self.policy = self.root / "policy.json"
        self.registry = self.root / "registry.json"
        self.output = self.root / "canonical.json"
        self.data = fixtures()
        self.save()

    def save(self):
        for path, obj in zip((self.source, self.policy, self.registry), self.data):
            path.write_text(json.dumps(obj, ensure_ascii=False), encoding="utf-8")

    def run_it(self):
        return registry.standardize_files(self.source, self.policy, self.registry, self.output)

    def test_synthetic_five_findings_preserved(self):
        doc, policy, mapping = self.data
        from sovia_n8n_sanitized import convert
        before = evaluate(convert(doc, policy))
        after = evaluate(registry.standardize(doc, policy, mapping))
        self.assertEqual((3, 5), (after["event_count"], after["finding_count"]))
        def signature(r):
            return sorted((x["rule_id"], tuple(x["event_ids"]), x["severity"])
                          for x in r["findings"])
        self.assertEqual(signature(before), signature(after))
        self.assertEqual(before["coverage_limits"], after["coverage_limits"])

    def test_tool_and_target_and_policy_remapped_consistently(self):
        out = registry.standardize(*self.data)
        self.assertEqual(["tool.lookup"], out["policy"]["allowed_tools"])
        self.assertEqual(["scope.sensitive"], out["policy"]["sensitive_targets"])
        self.assertEqual(["tool.lookup", "tool.lookup", "tool.export"],
                         [x["tool_name"] for x in out["events"]])
        self.assertEqual(["scope.public", "scope.public", "scope.sensitive"],
                         [x["target"] for x in out["events"]])
        self.assertEqual(["internal.example"], out["policy"]["approved_destinations"])

    def test_permission_evidence_timestamps_unchanged(self):
        out = registry.standardize(*self.data)
        originals = self.data[0]["steps"]
        for first, mapped in zip(originals, out["events"]):
            self.assertEqual(first["permission_asserted"], mapped["permission_asserted"])
            self.assertEqual(first["occurred_at_utc"].replace("+09:00", "+09:00"),
                             first["occurred_at_utc"])
            self.assertEqual(first.get("evidence_ref"), mapped["source_pointer"])

    def test_missing_evidence_remains_missing(self):
        out = registry.standardize(*self.data)
        self.assertIsNone(out["events"][-1]["source_pointer"])
        self.assertIn("MISSING_EVIDENCE", {f["rule_id"] for f in evaluate(out)["findings"]})

    def test_unregistered_event_tool_fails_closed(self):
        self.data[2]["tool_codes"].pop("unauthorized_export")
        with self.assertRaisesRegex(registry.RegistryError, "UNREGISTERED_METADATA_CODE"):
            registry.standardize(*self.data)
        self.save()
        with self.assertRaises(registry.RegistryError):
            self.run_it()
        self.assertFalse(self.output.exists())

    def test_unregistered_target_fails_closed(self):
        self.data[2]["target_codes"].pop("client_records")
        with self.assertRaisesRegex(registry.RegistryError, "UNREGISTERED_METADATA_CODE"):
            registry.standardize(*self.data)

    def test_unused_policy_tool_must_still_be_mapped(self):
        self.data[1]["policy"]["allowed_tools"].append("another_allowed")
        with self.assertRaisesRegex(registry.RegistryError, "UNREGISTERED_METADATA_CODE"):
            registry.standardize(*self.data)

    def test_unused_sensitive_target_policy_must_still_be_mapped(self):
        self.data[1]["policy"]["sensitive_targets"].append("scope_extra")
        with self.assertRaisesRegex(registry.RegistryError, "UNREGISTERED_METADATA_CODE"):
            registry.standardize(*self.data)

    def test_duplicate_tool_map_destination_refused(self):
        self.data[2]["tool_codes"]["unauthorized_export"] = "tool.lookup"
        with self.assertRaisesRegex(registry.RegistryError, "NON_INJECTIVE_REGISTRY_MAP"):
            registry.standardize(*self.data)

    def test_duplicate_target_map_destination_refused(self):
        self.data[2]["target_codes"]["client_records"] = "scope.public"
        with self.assertRaisesRegex(registry.RegistryError, "NON_INJECTIVE_REGISTRY_MAP"):
            registry.standardize(*self.data)

    def test_refuse_uppercase_and_malformed_aliases(self):
        for bad in ("Tool.Lookup", "user@example.com", "some phrase", "123start", "a"*81):
            with self.subTest(bad=bad):
                data = copy.deepcopy(self.data)
                data[2]["tool_codes"]["approved_lookup"] = bad
                with self.assertRaisesRegex(registry.RegistryError, "INVALID_REGISTRY_CODE"):
                    registry.standardize(*data)

    def test_refuse_raw_pii_before_code_mapping(self):
        self.data[0]["workflow_id"] = "phone_01012345678"
        with self.assertRaisesRegex(registry.RegistryError, "REGISTRY_PRIVACY_PREFLIGHT_REJECTED"):
            registry.standardize(*self.data)

    def test_refuse_secret_token_inside_registry(self):
        self.data[2]["tool_codes"]["approved_lookup"] = "sk-" + "x"*25
        with self.assertRaises(registry.RegistryError):
            registry.standardize(*self.data)

    def test_refuse_ipv4_literal_in_original_domain(self):
        self.data[0]["steps"][0]["destination_domain"] = "10.0.0.5"
        with self.assertRaisesRegex(registry.RegistryError, "REGISTRY_PRIVACY_PREFLIGHT_REJECTED"):
            registry.standardize(*self.data)

    def test_unknown_registry_keys_rejected(self):
        self.data[2]["original_values"] = {"email": "private"}
        with self.assertRaisesRegex(registry.RegistryError, "INVALID_REGISTRY_ENVELOPE"):
            registry.standardize(*self.data)

    def test_unknown_registry_kind_rejected(self):
        self.data[2]["kind"] = "n8n.raw-export"
        with self.assertRaisesRegex(registry.RegistryError, "INVALID_REGISTRY_ENVELOPE"):
            registry.standardize(*self.data)

    def test_raw_n8n_execution_export_rejected(self):
        self.data[0] = {"id": "execution", "data": {"resultData": {}}}
        with self.assertRaises(registry.RegistryError):
            registry.standardize(*self.data)

    def test_malformed_policy_rejected(self):
        self.data[1]["policy"]["unreviewed"] = "yes"
        with self.assertRaises(registry.RegistryError):
            registry.standardize(*self.data)

    def test_missing_policy_preserves_unknown(self):
        self.data[1]["policy"].pop("allowed_tools")
        self.data[1]["policy"].pop("sensitive_targets")
        output = registry.standardize(*self.data)
        self.assertNotIn("allowed_tools", output["policy"])
        self.assertNotIn("sensitive_targets", output["policy"])
        self.assertTrue(any("정책이 없어" in x for x in evaluate(output)["coverage_limits"]))

    def test_empty_target_registry_allowed_if_no_targets(self):
        self.data[2]["target_codes"] = {}
        self.data[1]["policy"]["sensitive_targets"] = []
        for step in self.data[0]["steps"]:
            step.pop("target_code", None)
        output = registry.standardize(*self.data)
        self.assertTrue(all(x["target"] is None for x in output["events"]))

    def test_empty_tool_registry_rejected(self):
        self.data[2]["tool_codes"] = {}
        with self.assertRaisesRegex(registry.RegistryError, "EMPTY_TOOL_REGISTRY"):
            registry.standardize(*self.data)

    def test_mapping_entry_limit(self):
        self.data[2]["tool_codes"] = {f"t{i}": f"z{i}" for i in range(1001)}
        with self.assertRaisesRegex(registry.RegistryError, "INVALID_REGISTRY_MAP"):
            registry.standardize(*self.data)

    def test_originals_and_registry_unchanged_on_success(self):
        originals = [p.read_bytes() for p in (self.source, self.policy, self.registry)]
        result = self.run_it()
        self.assertEqual(3, result["events"])
        self.assertTrue(result["audit_findings_preserved"])
        self.assertFalse(result["privacy_absence_proven"])
        self.assertFalse(result["customer_authorization_verified"])
        self.assertEqual(originals, [p.read_bytes() for p in
                                     (self.source, self.policy, self.registry)])
        self.assertEqual(5, evaluate(read_document(self.output))["finding_count"])

    def test_no_overwrite_existing_output(self):
        self.output.write_bytes(b"do-not-overwrite")
        with self.assertRaises(registry.RegistryError):
            self.run_it()
        self.assertEqual(b"do-not-overwrite", self.output.read_bytes())

    def test_output_alias_any_input_or_registry(self):
        for target in (self.source, self.policy, self.registry):
            before = target.read_bytes()
            with self.assertRaisesRegex(registry.RegistryError, "OUTPUT_ALIASES_INPUT"):
                registry.standardize_files(self.source, self.policy, self.registry, target)
            self.assertEqual(before, target.read_bytes())

    def test_large_registry_file_fails_closed(self):
        self.registry.write_bytes(b"x"*(1_048_576+1))
        with self.assertRaises(registry.RegistryError):
            self.run_it()
        self.assertFalse(self.output.exists())

    def test_unregistered_case_variant_refused_no_lowercase_guess(self):
        self.data[0]["steps"][0]["tool_code"] = "Approved_Lookup"
        with self.assertRaisesRegex(registry.RegistryError, "UNREGISTERED_METADATA_CODE"):
            registry.standardize(*self.data)

    def test_isolated_cli_requires_synthetic_acknowledgement(self):
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_code_registry.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--registry", str(self.registry), "--output", str(self.output)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.output.exists())
        self.assertIn("SYNTHETIC_ONLY_ACK_REQUIRED", result.stderr)
        passed = subprocess.run(cmd+["--synthetic-only"], capture_output=True,
                                text=True, timeout=20)
        self.assertEqual(0, passed.returncode, passed.stderr)
        self.assertEqual("SYNTHETIC_CODE_MAPPING_ONLY", json.loads(passed.stdout)["status"])
        self.assertNotIn(str(self.root), passed.stdout)

    def test_isolated_cli_rejects_unregistered_without_paths(self):
        self.data[2]["tool_codes"].pop("unauthorized_export")
        self.save()
        cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_code_registry.py"),
               "--input", str(self.source), "--policy", str(self.policy),
               "--registry", str(self.registry), "--output", str(self.output),
               "--synthetic-only"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.output.exists())
        self.assertNotIn(str(self.root), result.stderr)
        self.assertIn("UNREGISTERED_METADATA_CODE", result.stderr)

    def test_no_network_for_mapping(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(3, self.run_it()["events"])

    def test_mapping_does_not_change_reporting_coverage(self):
        initial = evaluate(__import__("sovia_n8n_sanitized").convert(self.data[0], self.data[1]))
        final = evaluate(registry.standardize(*self.data))
        self.assertEqual(initial["coverage_limits"], final["coverage_limits"])


if __name__ == "__main__":
    unittest.main()
