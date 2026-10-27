"""Actual in-memory and isolated subprocess synthetic plan/observation tests."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_audit import read_document
import sovia_la_plan_reconcile as subject

PLAN = read_document(ROOT / "examples" / "demo_la_plan_review.json")
POLICY = read_document(ROOT / "examples" / "demo_policy.json")
OBSERVED = read_document(ROOT / "examples" / "demo_la_observations.json")


class ReconcileTests(unittest.TestCase):
    def test_matching_steps_still_not_authenticated(self):
        result = subject.reconcile(PLAN, POLICY, OBSERVED)
        self.assertEqual((2, 2, 2), (result["planned_steps"], result["observed_events"],
                                    result["matched_step_ids"]))
        self.assertEqual(0, result["reconciliation_finding_count"])
        self.assertEqual("SYNTHETIC_MATCH_NOT_AUTHENTICATED", result["status"])
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["observation_completeness_verified"])
        self.assertFalse(result["real_la_integration_verified"])
        self.assertGreater(result["plan_risk_finding_count"], 0)
        self.assertGreater(result["post_audit_finding_count"], 0)

    def test_missing_step_is_unknown_not_failed(self):
        obs = copy.deepcopy(OBSERVED)
        obs["events"] = obs["events"][:1]
        result = subject.reconcile(PLAN, POLICY, obs)
        self.assertEqual("PLANNED_STEP_NOT_OBSERVED",
                         result["reconciliation_findings"][0]["rule_id"])
        self.assertEqual("UNKNOWN", result["reconciliation_findings"][0]["severity"])
        self.assertIn("MISSING_STEP_NOT_PROVEN_FAILED_OR_NOT_EXECUTED",
                      result["coverage_limits"])

    def test_unplanned_observation_and_changed_action_risk(self):
        obs = copy.deepcopy(OBSERVED)
        obs["events"][0]["tool_name"] = "unauthorized_export"
        obs["events"][0]["target"] = "client_records"
        obs["events"][0]["destination_domain"] = "outside.example"
        obs["events"][0]["permission_asserted"] = False
        extra = copy.deepcopy(obs["events"][0])
        extra["event_id"] = "unplanned_action"
        obs["events"].append(extra)
        rules = {f["rule_id"] for f in subject.reconcile(PLAN, POLICY, obs)["reconciliation_findings"]}
        self.assertEqual({
            "OBSERVED_TOOL_DIFFERS_FROM_PLAN",
            "OBSERVED_TARGET_DIFFERS_FROM_PLAN",
            "OBSERVED_DESTINATION_DIFFERS_FROM_PLAN",
            "OBSERVED_PERMISSION_CLAIM_DIFFERS_FROM_PLAN",
            "OBSERVED_EVENT_NOT_IN_PLAN",
        }, rules)

    def test_missing_evidence_not_claimed_verified(self):
        obs = copy.deepcopy(OBSERVED)
        obs["events"][0]["source_pointer"] = None
        rules = {f["rule_id"] for f in subject.reconcile(PLAN, POLICY, obs)["reconciliation_findings"]}
        self.assertIn("OBSERVATION_EVIDENCE_POINTER_MISSING", rules)

    def test_raw_event_payload_fail_closed(self):
        for extra in ("credentials", "prompt", "raw", "arguments", "runData"):
            obs = copy.deepcopy(OBSERVED)
            obs["events"][0][extra] = {"private": "do-not-show"}
            with self.subTest(field=extra):
                with self.assertRaisesRegex(subject.ReconcileError, "^RAW_OR_UNKNOWN_EVENT_FIELDS_REFUSED$"):
                    subject.reconcile(PLAN, POLICY, obs)

    def test_reject_missing_or_mismatched_policy_and_container(self):
        obs = copy.deepcopy(OBSERVED)
        obs["policy"]["allowed_tools"] = ["other_tool"]
        with self.assertRaisesRegex(subject.ReconcileError, "OBSERVATION_POLICY_MISMATCH"):
            subject.reconcile(PLAN, POLICY, obs)
        obs = copy.deepcopy(OBSERVED)
        obs["extra"] = "unexpected"
        with self.assertRaisesRegex(subject.ReconcileError, "UNSUPPORTED_OBSERVATION_ENVELOPE"):
            subject.reconcile(PLAN, POLICY, obs)

    def test_reject_private_metadata(self):
        obs = copy.deepcopy(OBSERVED)
        obs["events"][0]["source_pointer"] = "sk-" + "x" * 25
        with self.assertRaisesRegex(subject.ReconcileError, "OBSERVATION_REJECTED"):
            subject.reconcile(PLAN, POLICY, obs)

    def test_duplicate_correlation_events_rejected(self):
        obs = copy.deepcopy(OBSERVED)
        obs["events"].append(dict(obs["events"][0]))
        with self.assertRaisesRegex(subject.ReconcileError, "OBSERVATION_REJECTED"):
            subject.reconcile(PLAN, POLICY, obs)

    def test_isolated_cli_no_output_files_and_no_input_echo(self):
        with tempfile.TemporaryDirectory(prefix="sovia-la-reconcile-") as tmp:
            cmd = [
                sys.executable, "-I", "-B", str(ROOT / "sovia_la_plan_reconcile.py"),
                "--plan", str(ROOT / "examples" / "demo_la_plan_review.json"),
                "--policy", str(ROOT / "examples" / "demo_policy.json"),
                "--observations", str(ROOT / "examples" / "demo_la_observations.json"),
                "--synthetic-only",
            ]
            result = subprocess.run(cmd, cwd=tmp, capture_output=True, text=True, timeout=25)
            self.assertEqual(0, result.returncode, result.stderr)
            parsed = json.loads(result.stdout)
            self.assertEqual(0, parsed["reconciliation_finding_count"])
            self.assertEqual([], list(Path(tmp).iterdir()))
            denied = subprocess.run(cmd[:-1], cwd=tmp, capture_output=True, text=True, timeout=25)
            self.assertEqual(2, denied.returncode)
            self.assertEqual("SYNTHETIC_ACK_REQUIRED", json.loads(denied.stderr)["error_code"])
            self.assertNotIn(str(ROOT), denied.stderr)
            self.assertFalse(denied.stdout)


if __name__ == "__main__":
    unittest.main()
