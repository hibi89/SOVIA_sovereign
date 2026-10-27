"""Synthetic-only tests of stateless, aggregate no-report-file diagnostic."""
import contextlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import sovia_ephemeral_diagnostic as diag
from sovia_capacity_benchmark import make_synthetic

ROOT = Path(__file__).resolve().parents[1]


class EphemeralDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sovia-ephemeral-")
        self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name)
        self.input = self.folder / "synthetic.json"
        self.input.write_bytes((ROOT / "examples/demo_five_rules.json").read_bytes())

    def test_actual_five_rule_fixture_aggregates(self):
        result = diag.diagnose(self.input)
        self.assertEqual(result["events"], 3)
        self.assertEqual(result["findings"], 5)
        self.assertEqual(len(result["rules"]), 5)
        self.assertEqual(result["rules"]["BURST_TOOLS"], 1)
        self.assertEqual(result["rules"]["UNAUTHORIZED_TOOL"], 1)
        self.assertTrue(result["risk_findings_observed"])

    def test_healthy_synthetic_is_not_certified_safe(self):
        self.input.write_text(json.dumps(make_synthetic(10, "normal")), encoding="utf-8")
        result = diag.diagnose(self.input)
        self.assertEqual(result["events"], 10)
        self.assertEqual(result["findings"], 0)
        self.assertFalse(result["risk_findings_observed"])
        self.assertTrue(result["coverage_not_certified"])

    def test_missing_policy_is_unknown_not_safe(self):
        doc = make_synthetic(10, "normal")
        doc["policy"] = {}
        self.input.write_text(json.dumps(doc), encoding="utf-8")
        result = diag.diagnose(self.input)
        self.assertGreaterEqual(result["coverage_limit_count"], 5)
        self.assertTrue(result["coverage_not_certified"])

    def test_diagnose_does_not_create_local_files(self):
        before = sorted(p.name for p in self.folder.iterdir())
        diag.diagnose(self.input)
        self.assertEqual(before, sorted(p.name for p in self.folder.iterdir()))

    def test_result_never_contains_source_details_or_report_id(self):
        result = diag.diagnose(self.input)
        data = json.dumps(result)
        for forbidden in ("evt-003", "agent_id", "source_pointer", "report_id",
                          "normalized_policy_sha256", "events\": [", "findings\": ["):
            self.assertNotIn(forbidden, data)
        self.assertFalse(result["source_authorization_independently_verified"])
        self.assertFalse(result["persistent_os_or_shell_logs_ruled_out"])

    def test_sensitive_tool_label_not_printed(self):
        doc = make_synthetic(10, "normal")
        doc["events"][0]["tool_name"] = "PRIVATE_CUSTOMER_TOOL"
        self.input.write_text(json.dumps(doc), encoding="utf-8")
        summary = json.dumps(diag.diagnose(self.input))
        self.assertNotIn("PRIVATE_CUSTOMER_TOOL", summary)
        self.assertIn("UNAUTHORIZED_TOOL", summary)

    def test_unknown_rule_label_fail_closed(self):
        report = {"events": [{}], "event_count": 1, "findings": [
            {"rule_id": "CUSTOMER_SECRET", "severity": "HIGH"}],
            "finding_count": 1, "coverage_limits": []}
        with self.assertRaisesRegex(diag.DiagnosticError, "^UNSUPPORTED_FINDING_LABEL$"):
            diag.summarize(report)

    def test_unknown_severity_fail_closed(self):
        report = {"events": [], "event_count": 0, "findings": [
            {"rule_id": "MISSING_EVIDENCE", "severity": "SECRET"}],
            "finding_count": 1, "coverage_limits": []}
        with self.assertRaisesRegex(diag.DiagnosticError, "^UNSUPPORTED_FINDING_LABEL$"):
            diag.summarize(report)

    def test_bad_report_shape_fail_closed(self):
        for report in ([], None, {}, {"events": [], "event_count": True,
                      "findings": [], "finding_count": 0, "coverage_limits": []}):
            with self.subTest(report=report), self.assertRaises(diag.DiagnosticError):
                diag.summarize(report)

    def test_invalid_json_rejects_without_echo(self):
        self.input.write_text("PRIVATE_DATA_POSSIBLY_SECRET", encoding="utf-8")
        with self.assertRaisesRegex(diag.DiagnosticError, "^INVALID_AUDIT_INPUT$"):
            diag.diagnose(self.input)

    def test_too_large_source_fails_closed(self):
        self.input.write_bytes(b" " * (1024 * 1024 + 1))
        with self.assertRaisesRegex(diag.DiagnosticError, "^INVALID_AUDIT_INPUT$"):
            diag.diagnose(self.input)

    def test_non_json_extension_fails(self):
        other = self.folder / "synthetic.txt"
        other.write_bytes(self.input.read_bytes())
        with self.assertRaisesRegex(diag.DiagnosticError, "^INVALID_LOCAL_JSON_SOURCE$"):
            diag.diagnose(other)

    def test_source_symlink_fails(self):
        link = self.folder / "shortcut.json"
        try:
            link.symlink_to(self.input)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        with self.assertRaisesRegex(diag.DiagnosticError, "^INVALID_LOCAL_JSON_SOURCE$"):
            diag.diagnose(link)

    def test_no_ack_does_not_read_source(self):
        self.input.write_text("INVALID_SECRET_INPUT", encoding="utf-8")
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(diag.main(["--input", str(self.input)]), 2)
        self.assertEqual(json.loads(err.getvalue())["error_code"], "SOURCE_ACK_REQUIRED")

    def test_cli_json_aggregate_only_and_no_outputs(self):
        args = [sys.executable, "-I", "-B", str(ROOT / "sovia_ephemeral_diagnostic.py"),
                "--input", str(self.input), "--ack-sanitized-source"]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["findings"], 5)
        self.assertEqual(sorted(p.name for p in self.folder.iterdir()), [self.input.name])
        self.assertNotIn(str(self.folder), proc.stdout)

    def test_cli_bad_data_not_echoed(self):
        self.input.write_text("PRIVATE_EXCEPTION_CONTENT", encoding="utf-8")
        args = [sys.executable, "-I", "-B", str(ROOT / "sovia_ephemeral_diagnostic.py"),
                "--input", str(self.input), "--ack-sanitized-source"]
        proc = subprocess.run(args, capture_output=True, text=True, timeout=20)
        self.assertEqual(proc.returncode, 2)
        self.assertEqual(json.loads(proc.stderr)["error_code"], "INVALID_AUDIT_INPUT")
        self.assertNotIn(str(self.folder), proc.stderr)
        self.assertNotIn("PRIVATE_EXCEPTION_CONTENT", proc.stderr)


if __name__ == "__main__":
    unittest.main()
