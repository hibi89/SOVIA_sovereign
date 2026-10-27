"""Synthetic observation reconciliation regression tests."""
import copy
import unittest
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sovia_la_observation_reconcile import reconcile
from sovia_la_plan_preflight import PlanReviewError
from sovia_audit import read_document

ROOT = Path(__file__).resolve().parents[1]
PLAN = read_document(ROOT / "examples/demo_la_plan_review.json")
POLICY = read_document(ROOT / "examples/demo_policy.json")

def observed():
    return {"schema_version": "sovia.observation.v1",
            "plan_ref": PLAN["plan_ref"],
            "observations": [{"step_id": "lookup", "tool_code": "approved_lookup",
                              "side_effect": "none", "target_code": "public_docs",
                              "destination_domain": "internal.example",
                              "state": "observed", "evidence_ref": "synthetic_evidence"}]}

class ReconcileTests(unittest.TestCase):
    def test_missing_step_is_unknown_not_safe(self):
        result = reconcile(PLAN, POLICY, observed())
        self.assertIn("PLANNED_STEP_NOT_OBSERVED", {f["rule_id"] for f in result["findings"]})
        self.assertFalse(result["execution_authorized"])
        self.assertFalse(result["evidence_authenticated"])

    def test_mismatch_and_missing_evidence(self):
        doc = observed()
        doc["observations"][0].update(tool_code="unexpected_tool", side_effect="payment",
                                       target_code="different_target", destination_domain=None,
                                       evidence_ref=None)
        rules = {f["rule_id"] for f in reconcile(PLAN, POLICY, doc)["findings"]}
        self.assertTrue({"TOOL_MISMATCH", "SIDE_EFFECT_MISMATCH", "TARGET_MISMATCH",
                         "DESTINATION_MISMATCH", "OBSERVED_EVIDENCE_MISSING"} <= rules)

    def test_unplanned_and_unknown(self):
        doc = observed()
        doc["observations"].append({"step_id": "extra", "tool_code": "other",
                                    "side_effect": "unknown", "state": "unknown"})
        rules = {f["rule_id"] for f in reconcile(PLAN, POLICY, doc)["findings"]}
        self.assertIn("UNPLANNED_OBSERVED_STEP", rules)
        self.assertIn("OBSERVATION_STATE_UNKNOWN", rules)

    def test_duplicate_and_wrong_plan_ref_rejected(self):
        doc = observed()
        doc["observations"].append(copy.deepcopy(doc["observations"][0]))
        with self.assertRaisesRegex(PlanReviewError, "DUPLICATE_OBSERVATION_STEP"):
            reconcile(PLAN, POLICY, doc)
        doc = observed()
        doc["plan_ref"] = "wrong"
        with self.assertRaisesRegex(PlanReviewError, "INVALID_OBSERVATION_ENVELOPE"):
            reconcile(PLAN, POLICY, doc)

    def test_repeatable(self):
        self.assertEqual(reconcile(PLAN, POLICY, observed()), reconcile(PLAN, POLICY, observed()))

if __name__ == "__main__":
    unittest.main()
