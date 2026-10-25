import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_audit import AuditInputError, evaluate, read_document, render_html


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / "examples/demo.json").read_text(encoding="utf-8"))

    def test_demo_three_findings_and_ids(self):
        result = evaluate(self.document)
        self.assertEqual(2, result["event_count"])
        self.assertEqual(3, result["finding_count"])
        self.assertEqual({"UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION", "SENSITIVE_ACCESS"}, {f["rule_id"] for f in result["findings"]})
        self.assertTrue(all(f["event_ids"] == ["evt-002"] for f in result["findings"]))

    def test_known_safe(self):
        self.document["events"] = self.document["events"][:1]
        self.assertEqual([], evaluate(self.document)["findings"])

    def test_missing_policy_is_unknown(self):
        self.document["policy"] = {}
        r = evaluate(self.document)
        self.assertEqual(0, r["finding_count"])
        self.assertGreaterEqual(len(r["coverage_limits"]), 3)

    def test_bad_timestamp(self):
        self.document["events"][0]["occurred_at_utc"] = "yesterday"
        with self.assertRaises(AuditInputError):
            evaluate(self.document)

    def test_duplicate_event(self):
        self.document["events"][1]["event_id"] = "evt-001"
        with self.assertRaises(AuditInputError):
            evaluate(self.document)

    def test_bad_boolean(self):
        self.document["events"][1]["permission_asserted"] = "false"
        with self.assertRaises(AuditInputError):
            evaluate(self.document)

    def test_html_escaped(self):
        self.document["events"][1]["source_pointer"] = '<script>alert(1)</script>'
        html = render_html(evaluate(self.document))
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_prompt_not_carried(self):
        self.document["events"][1]["raw_prompt"] = "TOP SECRET PLEASE RUN"
        result = evaluate(self.document)
        self.assertNotIn("TOP SECRET", json.dumps(result))

    def test_file_too_large(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "huge.json"
            p.write_bytes(b"a" * 1048577)
            with self.assertRaises(AuditInputError):
                read_document(p)

    def test_duplicate_json_keys(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "bad.json"
            p.write_text('{"schema_version":"1.0","schema_version":"1.0"}', encoding="utf-8")
            with self.assertRaises(AuditInputError):
                read_document(p)

    def test_cli_full_pipeline(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "report.html"
            meta = Path(tmp) / "report.json"
            cmd = [sys.executable, str(ROOT / "sovia_audit.py"), "--input", str(ROOT / "examples/demo.json"), "--output", str(out), "--json-output", str(meta)]
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("위험 소견 3건", out.read_text(encoding="utf-8"))
            self.assertEqual(3, json.loads(meta.read_text(encoding="utf-8"))["finding_count"])

    def test_output_cannot_overwrite_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = Path(tmp) / "demo.json"
            inp.write_text(json.dumps(self.document), encoding="utf-8")
            cmd = [sys.executable, str(ROOT / "sovia_audit.py"), "--input", str(inp), "--output", str(inp)]
            completed = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(completed.returncode, 2)
            self.assertIn("must differ", completed.stderr)


if __name__ == "__main__":
    unittest.main()

class ExtendedAuditTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads((ROOT / 'examples/demo.json').read_text(encoding='utf-8'))

    def test_missing_pointer_detected_and_not_marked_observed(self):
        self.document['events'][1]['source_pointer'] = None
        result = evaluate(self.document)
        finding = [f for f in result['findings'] if f['rule_id'] == 'MISSING_EVIDENCE']
        self.assertEqual(1, len(finding))
        self.assertEqual('POINTER_MISSING', finding[0]['evidence_status'])

    def test_present_pointer_explicitly_unverified(self):
        result = evaluate(self.document)
        self.assertTrue(all(f['evidence_status'] == 'POINTER_PROVIDED_UNVERIFIED' for f in result['findings']))
        self.assertTrue(any('독립 검증되지' in x for x in result['coverage_limits']))

    def test_burst_rule_uses_utc_and_agent_run(self):
        self.document['policy']['max_tool_calls_per_minute'] = 2
        self.document['events'][1]['occurred_at_utc'] = '2026-10-25T15:01:30Z'
        third = dict(self.document['events'][0], event_id='evt-003', occurred_at_utc='2026-10-25T15:01:15Z')
        self.document['events'].insert(0, third)  # out of order does not affect result
        burst = [f for f in evaluate(self.document)['findings'] if f['rule_id'] == 'BURST_TOOLS']
        self.assertEqual(['evt-002'], [f['event_ids'][0] for f in burst])

    def test_burst_at_60_seconds_not_alerted(self):
        self.document['policy']['max_tool_calls_per_minute'] = 1
        self.document['events'][1]['occurred_at_utc'] = '2026-10-26T00:02:00+09:00'
        burst = [f for f in evaluate(self.document)['findings'] if f['rule_id'] == 'BURST_TOOLS']
        self.assertEqual([], burst)

    def test_burst_separated_by_run(self):
        self.document['policy']['max_tool_calls_per_minute'] = 1
        self.document['events'][1]['run_id'] = 'other-run'
        self.document['events'][1]['occurred_at_utc'] = '2026-10-26T00:01:15+09:00'
        self.assertFalse(any(f['rule_id'] == 'BURST_TOOLS' for f in evaluate(self.document)['findings']))

    def test_invalid_burst_policy(self):
        for bad in (True, 0, 1001, '3', -1):
            with self.subTest(bad=bad):
                self.document['policy']['max_tool_calls_per_minute'] = bad
                with self.assertRaises(AuditInputError):
                    evaluate(self.document)

    def test_timeline_escapes_untrusted_agent_name(self):
        self.document['events'][0]['agent_id'] = '<img src=x onerror=alert(1)>'
        result = render_html(evaluate(self.document))
        self.assertIn('이벤트 타임라인', result)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', result)
        self.assertNotIn('<img src=x', result)

    def test_timezone_to_utc(self):
        self.assertEqual('2026-10-25T15:01:00Z', evaluate(self.document)['events'][0]['occurred_at_utc'])

    def test_repeated_evaluation_is_deterministic(self):
        self.assertEqual(evaluate(self.document), evaluate(self.document))

    def test_invalid_domain_rejected(self):
        self.document['events'][0]['destination_domain'] = 'https://internal.example/path'
        with self.assertRaises(AuditInputError):
            evaluate(self.document)

    def test_deep_json_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'deep.json'
            p.write_text('[' * 18 + '1' + ']' * 18, encoding='utf-8')
            with self.assertRaises(AuditInputError):
                read_document(p)

    def test_non_utf8_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad.json'
            p.write_bytes(b'\xff\xfe')
            with self.assertRaises(AuditInputError):
                read_document(p)

    def test_invalid_input_does_not_touch_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            inp = Path(tmp) / 'invalid.json'
            out = Path(tmp) / 'result.html'
            inp.write_text('not json', encoding='utf-8')
            res = subprocess.run([sys.executable, str(ROOT / 'sovia_audit.py'), '--input', str(inp), '--output', str(out)], capture_output=True, text=True, timeout=10)
            self.assertEqual(2, res.returncode)
            self.assertFalse(out.exists())

    def test_no_untrusted_tool_execution(self):
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / 'would_be_executed.txt'
            self.document['events'][1]['tool_name'] = 'touch ' + str(marker)
            evaluate(self.document)
            self.assertFalse(marker.exists())

    def test_burst_missing_threshold_unknown(self):
        self.assertTrue(any('임계치 정책' in x for x in evaluate(self.document)['coverage_limits']))
