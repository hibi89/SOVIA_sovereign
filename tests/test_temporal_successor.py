"""Issue 52 regression: real 60-second timestamps, source-only 0.12 candidate."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import socket

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_audit
import sovia_audit_v012 as newer
from sovia_report_print_preview import preview_files

DEMO = ROOT / "examples" / "demo_five_rules.json"

def make(times, *, threshold=2, agents=None, runs=None):
    return {"schema_version": "1.0", "policy": {
        "allowed_tools": ["approved_lookup"],
        "approved_destinations": ["internal.example"],
        "sensitive_targets": ["client_records"],
        "max_tool_calls_per_minute": threshold,
    }, "events": [{
        "event_id": f"e{i+1}", "occurred_at_utc": t,
        "agent_id": "agent" if agents is None else agents[i],
        "run_id": "run" if runs is None else runs[i],
        "tool_name": "approved_lookup", "target": "public_docs",
        "destination_domain": "internal.example",
        "permission_asserted": True, "outcome": "ok",
        "source_pointer": f"synthetic:{i+1}",
    } for i,t in enumerate(times)]}

def bursts(report):
    return [f for f in report["findings"] if f["rule_id"] == "BURST_TOOLS"]

class TemporalRuleTests(unittest.TestCase):
    def setUp(self):
        self.fixture = make([
            "2026-10-25T15:01:00Z",
            "2026-10-25T15:01:00.500000Z",
            "2026-10-25T15:02:00.300000Z"])

    def test_false_positive_proved_in_original_but_absent_in_successor(self):
        source = copy.deepcopy(self.fixture)
        self.assertEqual(["e3"], [f["event_ids"][0] for f in bursts(sovia_audit.evaluate(source))])
        self.assertEqual([], bursts(newer.evaluate(source)))
        self.assertEqual(source, self.fixture)

    def test_preserves_original_digest_events_limits_and_other_rules(self):
        old, new = sovia_audit.evaluate(self.fixture), newer.evaluate(self.fixture)
        for field in ("normalized_policy_sha256", "report_id", "events", "coverage_limits"):
            self.assertEqual(old[field], new[field])
        self.assertEqual(0, new["finding_count"])
        self.assertEqual("0.12.0-preview", new["engine_version"])

    def test_valid_burst_strictly_inside_sixty_seconds(self):
        doc = make(["2026-10-25T15:01:00Z",
                    "2026-10-25T15:01:00.500000Z",
                    "2026-10-25T15:01:59.999999Z"])
        findings = bursts(newer.evaluate(doc))
        self.assertEqual(["e3"], [f["event_ids"][0] for f in findings])
        self.assertEqual("1.1", findings[0]["rule_version"])
        self.assertEqual("POINTER_PROVIDED_UNVERIFIED", findings[0]["evidence_status"])

    def test_exact_sixty_second_boundary_evicts_event(self):
        doc = make(["2026-10-25T15:01:00Z",
                    "2026-10-25T15:01:00.500000Z",
                    "2026-10-25T15:02:00Z"])
        self.assertEqual([], bursts(newer.evaluate(doc)))

    def test_reverse_input_order_same_burst_identity(self):
        doc = make(["2026-10-25T15:01:00Z",
                    "2026-10-25T15:01:00.500000Z",
                    "2026-10-25T15:01:59.999999Z"])
        rev = copy.deepcopy(doc)
        rev["events"].reverse()
        self.assertEqual(bursts(newer.evaluate(doc)), bursts(newer.evaluate(rev)))

    def test_equal_timestamp_deterministic_event_id(self):
        doc = make(["2026-10-25T15:01:00Z"]*3)
        doc["events"].reverse()
        self.assertEqual(["e3"], [f["event_ids"][0] for f in bursts(newer.evaluate(doc))])

    def test_agent_and_run_isolation(self):
        doc = make(["2026-10-25T15:01:00Z"]*3,
                   agents=["alice","bob","alice"], runs=["a","a","b"])
        self.assertEqual([], bursts(newer.evaluate(doc)))

    def test_golden_demo_preserves_four_rules_and_five_findings(self):
        doc = sovia_audit.read_document(DEMO)
        old, new = sovia_audit.evaluate(doc), newer.evaluate(doc)
        self.assertEqual(5, new["finding_count"])
        self.assertEqual([f for f in old["findings"] if f["rule_id"]!="BURST_TOOLS"],
                         [f for f in new["findings"] if f["rule_id"]!="BURST_TOOLS"])
        self.assertEqual("1.1", bursts(new)[0]["rule_version"])

    def test_missing_burst_threshold_keeps_unknown(self):
        doc = copy.deepcopy(self.fixture)
        doc["policy"].pop("max_tool_calls_per_minute")
        new = newer.evaluate(doc)
        self.assertEqual([], bursts(new))
        self.assertTrue(any("임계치 정책" in x for x in new["coverage_limits"]))

    def test_invalid_input_refuses_via_original_validation(self):
        doc = copy.deepcopy(self.fixture)
        doc["events"][0]["occurred_at_utc"] = "bogus"
        with self.assertRaises(sovia_audit.AuditInputError):
            newer.evaluate(doc, legacy_audit=sovia_audit)

    def test_real_isolated_python_cli_writes_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/"input.json"
            html, data = Path(tmp)/"out.html", Path(tmp)/"out.json"
            source.write_text(json.dumps(self.fixture), encoding="utf-8")
            cmd = [sys.executable, "-I", "-B", str(ROOT/"sovia_audit_v012.py"),
                   "--input", str(source), "--html-output", str(html),
                   "--json-output", str(data), "--synthetic-only"]
            orig = source.read_bytes()
            first = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.assertEqual(0, first.returncode, first.stderr)
            self.assertEqual(0, json.loads(data.read_text(encoding="utf-8"))["finding_count"])
            self.assertIn("SOVIA Audit Lite", html.read_text(encoding="utf-8"))
            self.assertEqual(orig, source.read_bytes())
            saved = (html.read_bytes(), data.read_bytes())
            second = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.assertEqual(2, second.returncode)
            self.assertEqual(saved, (html.read_bytes(), data.read_bytes()))
            self.assertNotIn(str(source), second.stderr)

    def test_missing_synthetic_ack_makes_no_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp)/"a.html", Path(tmp)/"b.json"
            cmd = [sys.executable, "-I", "-B", str(ROOT/"sovia_audit_v012.py"),
                   "--input", str(DEMO), "--html-output", str(a), "--json-output", str(b)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.assertEqual(2, result.returncode)
            self.assertEqual("SYNTHETIC_ACK_REQUIRED", json.loads(result.stderr)["error_code"])
            self.assertFalse(a.exists())

    def test_synthetic_ack_does_not_bypass_pii_scan(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/"src.json"
            doc = copy.deepcopy(self.fixture)
            doc["events"][0]["agent_id"] = "user@example.com"
            source.write_text(json.dumps(doc), encoding="utf-8")
            a, b = Path(tmp)/"a.html", Path(tmp)/"b.json"
            cmd = [sys.executable, "-I", "-B", str(ROOT/"sovia_audit_v012.py"),
                   "--input", str(source), "--html-output", str(a),
                   "--json-output", str(b), "--synthetic-only"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            self.assertEqual(2, result.returncode)
            self.assertNotIn("user@example.com", result.stderr)
            self.assertNotIn(str(source), result.stderr)
            self.assertFalse(a.exists())
            self.assertFalse(b.exists())

    def test_never_aliases_input_or_two_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/"source.json"
            source.write_text(json.dumps(self.fixture), encoding="utf-8")
            with self.assertRaisesRegex(newer.CandidateError, "PATH_COLLISION"):
                newer.run_synthetic(source, source, Path(tmp)/"other.json")
            with self.assertRaisesRegex(newer.CandidateError, "PATH_COLLISION"):
                newer.run_synthetic(source, Path(tmp)/"same.json", Path(tmp)/"same.json")

    def test_print_preview_uses_successor_risk_engine(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, page = Path(tmp)/"synthetic.json", Path(tmp)/"next.html"
            source.write_text(json.dumps(self.fixture), encoding="utf-8")
            self.assertEqual((3,0), preview_files(source, page))
            self.assertIn("위험 소견 0건", page.read_text(encoding="utf-8"))

    def test_no_network_required_for_candidate_evaluation(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(0, newer.evaluate(self.fixture)["finding_count"])

if __name__ == "__main__":
    unittest.main()
