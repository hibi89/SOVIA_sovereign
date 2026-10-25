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
