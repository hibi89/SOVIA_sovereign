"""Standalone owner synthetic HTML/PDF static preflight; no real GUI/AV claims."""
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
import sovia_owner_artifact_preflight as pre
import sovia_audit as audit
import sovia_dashboard as board
import sovia_history as history


def auto(pdf="SKIPPED_REPORTLAB_MISSING"):
    return {
        "schema_version": "1.0", "version": "0.10.0-beta",
        "purpose": "SYNTHETIC_ONLY_NO_CUSTOMER_DATA",
        "status": "AUTOMATED_PASS_MANUAL_PENDING",
        "system": {"os": "Windows", "os_release": "synthetic",
                   "python": "3.13.0"},
        "checks": {
            "python": "PASS", "package_integrity": "PASS",
            "audit": "PASS", "sqlite": "PASS", "dashboard": "PASS",
            "recovery": "PASS", "optional_pdf": pdf,
        },
        "synthetic": {"events": 3, "findings": 5, "reports": 1},
        "manual_acceptance": {
            "audit_html_visual": "NOT_CHECKED",
            "dashboard_html_visual": "NOT_CHECKED",
            "korean_pdf_visual": "NOT_CHECKED",
            "antivirus_or_smartscreen": "NOT_CHECKED",
            "owner_device_commercial_approval": "NOT_CHECKED",
        },
        "error_code": None,
    }


class StaticArtifactPreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.global_tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.global_tmp.cleanup)
        base = Path(cls.global_tmp.name)
        sample = ROOT / "examples" / "demo_five_rules.json"
        cls.report = audit.evaluate(audit.read_document(sample))
        cls.audit_html = audit.render_html(cls.report)
        db = base / "history.sqlite"
        history.import_report(db, sample)
        cls.dashboard_html = board.render_html(board.read_snapshot(db))

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.install(auto())

    def install(self, selfcheck, pdf=None):
        (self.root / "SELF_CHECK_RESULT.json").write_text(
            json.dumps(selfcheck), encoding="utf-8")
        (self.root / "synthetic-audit.json").write_text(
            json.dumps(self.report, ensure_ascii=False), encoding="utf-8")
        (self.root / "synthetic-audit.html").write_text(
            self.audit_html, encoding="utf-8")
        (self.root / "synthetic-dashboard.html").write_text(
            self.dashboard_html, encoding="utf-8")
        if pdf is not None:
            (self.root / "synthetic-audit.pdf").write_bytes(pdf)

    def rewrite(self, name, transform):
        p = self.root / name
        p.write_text(transform(p.read_text(encoding="utf-8")), encoding="utf-8")

    def cli(self, folder=None):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_owner_artifact_preflight.py"),
             "--results-dir", str(self.root if folder is None else folder)],
            capture_output=True, text=True, timeout=20)

    def test_valid_offline_html_metadata_passes_with_all_manual_pending(self):
        r = pre.inspect(self.root)
        self.assertEqual("SYNTHETIC_ARTIFACT_STATIC_CHECKS_PASSED_MANUAL_PENDING", r["status"])
        self.assertEqual((3, 5), (r["synthetic_events"], r["synthetic_findings"]))
        self.assertEqual("PASS_HEURISTIC", r["offline_static_html_checks"])
        self.assertEqual("PDF_NOT_GENERATED_NOT_TESTED", r["pdf_static_check"])
        for key in ("browser_visual_verified", "korean_pdf_visual_verified",
                    "windows_defender_smartscreen_verified", "actual_owner_device_verified",
                    "source_or_owner_identity_authenticated", "commercial_approval",
                    "customer_data_processed", "writes_performed", "network_called"):
            with self.subTest(key=key):
                self.assertFalse(r[key])

    def test_cli_real_subprocess_succeeds_and_does_not_write(self):
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        r = self.cli()
        self.assertEqual(0, r.returncode, r.stderr)
        self.assertFalse(json.loads(r.stdout)["actual_owner_device_verified"])
        after = {p.name: p.read_bytes() for p in self.root.iterdir()}
        self.assertEqual(before, after)

    def test_no_network_ever(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(3, pre.inspect(self.root)["synthetic_events"])

    def test_pdf_only_header_footer_markers_never_visual_pass(self):
        self.install(auto("GENERATED_NEEDS_VISUAL_REVIEW"), b"%PDF-1.4\nhello\n%%EOF\n")
        result = pre.inspect(self.root)
        self.assertEqual("PDF_HEADER_TRAILER_PRESENT_VISUAL_PENDING", result["pdf_static_check"])
        self.assertFalse(result["korean_pdf_visual_verified"])

    def test_pdf_bogus_header_rejected(self):
        self.install(auto("GENERATED_NEEDS_VISUAL_REVIEW"), b"NOT PDF\n%%EOF\n")
        with self.assertRaisesRegex(pre.StaticPreflightError, "PDF_STATIC_MARKER_MISSING"):
            pre.inspect(self.root)

    def test_pdf_missing_trailer_rejected(self):
        self.install(auto("GENERATED_NEEDS_VISUAL_REVIEW"), b"%PDF-1.4\nINVALID\n")
        with self.assertRaisesRegex(pre.StaticPreflightError, "PDF_STATIC_MARKER_MISSING"):
            pre.inspect(self.root)

    def test_pdf_claim_generated_but_missing_file_rejected(self):
        self.install(auto("GENERATED_NEEDS_VISUAL_REVIEW"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ARTIFACT_MISSING_OR_SYMLINK"):
            pre.inspect(self.root)

    def test_pdf_skipped_must_have_no_file(self):
        self.install(auto("SKIPPED_KOREAN_TTF_MISSING"), b"%PDF-1.4\n%%EOF\n")
        with self.assertRaisesRegex(pre.StaticPreflightError, "UNEXPECTED_PDF_ARTIFACT"):
            pre.inspect(self.root)

    def test_pdf_autocheck_failed_blocks_even_if_other_artifacts_ok(self):
        self.install(auto("FAILED_OPTIONAL_PDF"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "OPTIONAL_PDF_AUTOCHECK_FAILED"):
            pre.inspect(self.root)

    def test_pdf_symlink_rejected(self):
        other = self.root / "external.pdf"
        other.write_bytes(b"%PDF-1.4\n%%EOF\n")
        link = self.root / "synthetic-audit.pdf"
        try:
            link.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unsupported")
        self.install(auto("GENERATED_NEEDS_VISUAL_REVIEW"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ARTIFACT_MISSING_OR_SYMLINK"):
            pre.inspect(self.root)

    def test_pdf_oversized_rejected_before_read_all(self):
        large = self.root / "synthetic-audit.pdf"
        large.write_bytes(b"%PDF-1.4" + b"x" * (pre.MAX_PDF + 1))
        self.install(auto("GENERATED_NEEDS_VISUAL_REVIEW"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ARTIFACT_SIZE_LIMIT"):
            pre.inspect(self.root)

    def test_unauthorized_script_tag_rejected_in_both_pages(self):
        for page in ("synthetic-audit.html", "synthetic-dashboard.html"):
            with self.subTest(page=page):
                self.install(auto())
                self.rewrite(page, lambda s: s.replace("</body>", "<script>bad()</script></body>"))
                with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_OR_UNEXPECTED_HTML"):
                    pre.inspect(self.root)

    def test_external_image_resource_rejected(self):
        self.rewrite("synthetic-dashboard.html", lambda s: s.replace(
            "</body>", '<img src="https://example.invalid/surveillance.png"></body>'))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_OR_UNEXPECTED_HTML"):
            pre.inspect(self.root)

    def test_embedded_frame_rejected(self):
        self.rewrite("synthetic-audit.html", lambda s: s.replace(
            "</body>", '<iframe src="about:blank"></iframe></body>'))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_OR_UNEXPECTED_HTML"):
            pre.inspect(self.root)

    def test_inline_event_handler_rejected(self):
        self.rewrite("synthetic-dashboard.html", lambda s: s.replace(
            "<body>", '<body onload="fetch(\'https://example.invalid\')">'))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_OR_UNEXPECTED_HTML"):
            pre.inspect(self.root)

    def test_unexpected_href_rejected(self):
        self.rewrite("synthetic-audit.html", lambda s: s.replace(
            "<body>", '<body href="file:///unsafe">'))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_OR_UNEXPECTED_HTML"):
            pre.inspect(self.root)

    def test_active_meta_refresh_rejected(self):
        self.rewrite("synthetic-dashboard.html", lambda s: s.replace(
            "</head>", '<meta http-equiv="refresh" content="0;url=https://example.invalid"></head>'))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_OR_UNEXPECTED_HTML"):
            pre.inspect(self.root)

    def test_css_remote_url_rejected(self):
        self.rewrite("synthetic-dashboard.html", lambda s: s.replace(
            "</style>", "body{background:url(https://example.invalid/)}" + "</style>"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_EXTERNAL_CSS_REJECTED"):
            pre.inspect(self.root)

    def test_css_import_rejected(self):
        self.rewrite("synthetic-audit.html", lambda s: s.replace(
            "</style>", "@import 'https://example.invalid/css';</style>"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "ACTIVE_EXTERNAL_CSS_REJECTED"):
            pre.inspect(self.root)

    def test_audit_html_missing_report_id_rejected(self):
        rid = self.report["report_id"]
        self.rewrite("synthetic-audit.html", lambda s: s.replace(rid, "0000000000000000"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "AUDIT_HTML_SEMANTIC_MISMATCH"):
            pre.inspect(self.root)

    def test_audit_count_mismatch_rejected(self):
        self.rewrite("synthetic-audit.html",
                     lambda s: s.replace("검토 이벤트 3건 · 위험 소견 5건", "검토 이벤트 3건 · 위험 소견 0건"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "AUDIT_HTML_SEMANTIC_MISMATCH"):
            pre.inspect(self.root)

    def test_dashboard_csp_missing_rejected(self):
        self.rewrite("synthetic-dashboard.html", lambda s: s.replace("script-src 'none'", "script-src 'self'"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "DASHBOARD_HTML_SEMANTIC_OR_CSP_MISMATCH"):
            pre.inspect(self.root)

    def test_dashboard_metric_tampering_rejected(self):
        self.rewrite("synthetic-dashboard.html", lambda s: s.replace(
            "metric-number'>5</div>", "metric-number'>0</div>"))
        with self.assertRaisesRegex(pre.StaticPreflightError, "DASHBOARD_HTML_SEMANTIC_OR_CSP_MISMATCH"):
            pre.inspect(self.root)

    def test_missing_html_rejected(self):
        (self.root / "synthetic-dashboard.html").unlink()
        with self.assertRaisesRegex(pre.StaticPreflightError, "ARTIFACT_MISSING_OR_SYMLINK"):
            pre.inspect(self.root)

    def test_invalid_utf8_rejected(self):
        (self.root / "synthetic-audit.html").write_bytes(b"<!doctype html>\xff")
        with self.assertRaisesRegex(pre.StaticPreflightError, "INVALID_UTF8_HTML"):
            pre.inspect(self.root)

    def test_missing_selfcheck_rejected(self):
        (self.root / "SELF_CHECK_RESULT.json").unlink()
        with self.assertRaisesRegex(pre.StaticPreflightError, "ARTIFACT_MISSING_OR_SYMLINK"):
            pre.inspect(self.root)

    def test_symlinked_report_refused(self):
        target = self.root / "new-report.json"
        target.write_bytes((self.root / "synthetic-audit.json").read_bytes())
        (self.root / "synthetic-audit.json").unlink()
        try:
            (self.root / "synthetic-audit.json").symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unsupported")
        with self.assertRaisesRegex(pre.StaticPreflightError, "ARTIFACT_MISSING_OR_SYMLINK"):
            pre.inspect(self.root)

    def test_results_directory_symlink_refused(self):
        target = self.root.parent / ("linked-owner" + self.root.name)
        try:
            target.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unsupported")
        with self.assertRaisesRegex(pre.StaticPreflightError, "INVALID_RESULT_DIRECTORY"):
            pre.inspect(target)

    def test_json_counts_wrong_rejected(self):
        p = self.root / "synthetic-audit.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["finding_count"] = 0
        p.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(pre.StaticPreflightError, "SYNTHETIC_REPORT_COUNTS_OR_RULES"):
            pre.inspect(self.root)

    def test_json_report_wrong_rule_rejected(self):
        p = self.root / "synthetic-audit.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["findings"][0]["rule_id"] = "MADE_UP"
        p.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(pre.StaticPreflightError, "SYNTHETIC_REPORT_COUNTS_OR_RULES"):
            pre.inspect(self.root)

    def test_bad_selfcheck_status_fails(self):
        p = self.root / "SELF_CHECK_RESULT.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["status"] = "AUTOMATED_FAILED"
        p.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(pre.StaticPreflightError, "SELF_CHECK_OR_REPORT_REJECTED"):
            pre.inspect(self.root)

    def test_selfcheck_manual_pass_tampering_fails(self):
        p = self.root / "SELF_CHECK_RESULT.json"
        doc = json.loads(p.read_text(encoding="utf-8"))
        doc["manual_acceptance"]["audit_html_visual"] = "PASS"
        p.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(pre.StaticPreflightError, "SELF_CHECK_OR_REPORT_REJECTED"):
            pre.inspect(self.root)

    def test_cli_error_does_not_echo_sensitive_paths(self):
        p = self.root / "synthetic-audit.html"
        p.write_text('<!doctype html><script>mock-private-value</script>', encoding="utf-8")
        proc = self.cli()
        self.assertEqual(2, proc.returncode)
        self.assertIn("REJECTED", proc.stderr)
        self.assertNotIn("mock-private-value", proc.stderr + proc.stdout)
        self.assertNotIn(str(self.root), proc.stderr + proc.stdout)

    def test_reject_empty_dir(self):
        path = self.root / "empty"
        path.mkdir()
        proc = self.cli(path)
        self.assertEqual(2, proc.returncode)
        self.assertNotIn(str(path), proc.stderr)

    def test_no_raw_customer_input_or_n8n_network_used(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            result = pre.inspect(self.root)
        self.assertFalse(result["customer_data_processed"])


if __name__ == "__main__":
    unittest.main()
