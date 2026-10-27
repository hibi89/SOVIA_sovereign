"""Fast end-to-end tests of independent synthetic SOVIA plan risk review."""
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
import sovia_la_plan_preflight as risk
from sovia_audit import read_document

PLAN = read_document(ROOT / "examples/demo_la_plan_review.json")
POLICY = read_document(ROOT / "examples/demo_policy.json")


class PlanReviewTests(unittest.TestCase):
    def test_findings_on_write_without_trusting_permission_claim(self):
        report = risk.assess(PLAN, POLICY)
        self.assertEqual((2, 3), (report["step_count"], report["finding_count"]))
        self.assertEqual({
            "UNAUTHORIZED_PLANNED_TOOL", "SENSITIVE_PLANNED_TARGET_REVIEW",
            "SIDE_EFFECT_REQUIRES_INDEPENDENT_APPROVAL",
        }, {f["rule_id"] for f in report["findings"]})
        for field in ("execution_authorized", "approval_identity_verified",
                      "real_la_integration_verified", "runtime_policy_enforced"):
            self.assertFalse(report[field])

    def test_clean_plan_never_grants_execution_permission(self):
        doc = copy.deepcopy(PLAN)
        doc["steps"] = doc["steps"][:1]
        output = risk.assess(doc, POLICY)
        self.assertEqual("NO_FINDINGS_STILL_UNVERIFIED", output["status"])
        self.assertFalse(output["execution_authorized"])
        self.assertIn("RUNTIME_POLICY_NOT_ENFORCED", output["coverage_limits"])

    def test_missing_policy_is_unknown_not_safe(self):
        output = risk.assess(PLAN, {"schema_version":"1.0", "policy":{}})
        self.assertIn("TOOL_POLICY_NOT_PROVIDED", output["coverage_limits"])

    def test_provided_approval_reference_not_a_real_signature(self):
        doc = copy.deepcopy(PLAN)
        doc["steps"][1].update(approval_ref="operator_claim", permission_asserted=True)
        result = risk.assess(doc, POLICY)
        self.assertIn("SIDE_EFFECT_REQUIRES_INDEPENDENT_APPROVAL",
                      {item["rule_id"] for item in result["findings"]})
        self.assertFalse(result["approval_identity_verified"])

    def test_unknown_payment_destructive_external_are_reviewed(self):
        for effect, name in (
            ("unknown", "UNCLASSIFIED_SIDE_EFFECT"),
            ("payment", "SIDE_EFFECT_REQUIRES_INDEPENDENT_APPROVAL"),
            ("destructive", "SIDE_EFFECT_REQUIRES_INDEPENDENT_APPROVAL"),
            ("external_send", "EXTERNAL_DESTINATION_NOT_DISCLOSED"),
        ):
            doc = copy.deepcopy(PLAN)
            doc["steps"][0]["side_effect"] = effect
            doc["steps"][0]["destination_domain"] = None
            with self.subTest(effect=effect):
                output = risk.assess(doc, POLICY)
                self.assertIn(name, {i["rule_id"] for i in output["findings"]})

    def test_raw_fields_fail_closed(self):
        for field in ("arguments", "sql", "credentials", "prompt", "payload"):
            doc = copy.deepcopy(PLAN)
            doc["steps"][0][field] = "secret"
            with self.subTest(field=field):
                with self.assertRaisesRegex(risk.PlanReviewError, "UNSUPPORTED_STEP_FIELDS"):
                    risk.assess(doc, POLICY)

    def test_duplicate_and_invalid_types_fail_closed(self):
        mutations = (
            (lambda d: d["steps"].append(dict(d["steps"][0])), "DUPLICATE_STEP_ID"),
            (lambda d: d["steps"][0].update(side_effect="shell"), "INVALID_SIDE_EFFECT"),
            (lambda d: d["steps"][0].update(permission_asserted="yes"), "INVALID_PERMISSION_ASSERTION"),
            (lambda d: d["steps"][0].update(destination_domain="https://x.io"), "INVALID_DESTINATION"),
            (lambda d: d.update(steps=[]), "INVALID_PLAN_STEPS"),
        )
        for change, error in mutations:
            doc = copy.deepcopy(PLAN)
            change(doc)
            with self.subTest(error=error):
                with self.assertRaisesRegex(risk.PlanReviewError, "^" + error + "$"):
                    risk.assess(doc, POLICY)

    def test_private_pattern_rejected_without_echo(self):
        doc = copy.deepcopy(PLAN)
        doc["steps"][0]["step_id"] = "01012345678"
        with self.assertRaisesRegex(risk.PlanReviewError, "^PLAN_METADATA_PREFLIGHT_REJECTED$"):
            risk.assess(doc, POLICY)

    def test_repeatable_report_hash(self):
        self.assertEqual(risk.assess(PLAN, POLICY), risk.assess(PLAN, POLICY))

    def test_isolated_cli_real_execution_no_extra_files(self):
        with tempfile.TemporaryDirectory(prefix="sovia-plan-check-") as temp:
            command = [
                sys.executable, "-I", "-B", str(ROOT / "sovia_la_plan_preflight.py"),
                "--input", str(ROOT / "examples/demo_la_plan_review.json"),
                "--policy", str(ROOT / "examples/demo_policy.json"),
                "--synthetic-only",
            ]
            with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
                proc = subprocess.run(command, cwd=temp, capture_output=True,
                                      text=True, timeout=20)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertEqual(3, json.loads(proc.stdout)["finding_count"])
            self.assertEqual([], list(Path(temp).iterdir()))
            bad = subprocess.run(command[:-1], cwd=temp, capture_output=True,
                                 text=True, timeout=20)
            self.assertEqual(2, bad.returncode)
            self.assertEqual("SYNTHETIC_ACK_REQUIRED", json.loads(bad.stderr)["error_code"])


if __name__ == "__main__":
    unittest.main()
