"""Next printable HTML report: product UX evidence without touching P2 ZIP."""
from __future__ import annotations

import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_audit
from sovia_report_print_preview import (
    EVENT_COLUMNS, FINDING_COLUMNS, PreviewError, preview_files, render,
)

EXAMPLE = ROOT / "examples" / "demo_five_rules.json"


class ReportCells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.headers = []
        self.cell_values = []
        self._in_cell = False

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.labels.append(dict(attrs).get("data-label"))
            self._in_cell = True
        elif tag == "th":
            self.headers.append(dict(attrs).get("scope"))

    def handle_data(self, data):
        if self._in_cell:
            self.cell_values.append(data)

    def handle_endtag(self, tag):
        if tag == "td":
            self._in_cell = False


class PrintablePreviewTests(unittest.TestCase):
    def setUp(self):
        self.document = sovia_audit.read_document(EXAMPLE)
        self.report = sovia_audit.evaluate(self.document)

    def test_unchanged_evaluation_and_columns(self):
        before = json.dumps(self.report, ensure_ascii=False, sort_keys=True)
        page = render(self.report)
        after = json.dumps(self.report, ensure_ascii=False, sort_keys=True)
        self.assertEqual(before, after)
        self.assertEqual((3, 5), (self.report["event_count"], self.report["finding_count"]))
        self.assertIn("위험 소견 5건", page)
        self.assertIn("출력 버전 0.12.0-preview", page)
        parser = ReportCells()
        parser.feed(page)
        self.assertEqual(5 * 6 + 3 * 9, len(parser.labels))
        self.assertEqual(
            [label for label, _ in FINDING_COLUMNS] * 5 +
            [label for label, _ in EVENT_COLUMNS] * 3,
            parser.labels
        )
        self.assertEqual(["col"] * 15, parser.headers)

    def test_print_only_cards_and_screen_scroll(self):
        page = render(self.report)
        self.assertIn("@media print{", page)
        self.assertIn("@page{size:A4 portrait", page)
        self.assertIn("content:attr(data-label)", page)
        self.assertIn(".table-scroll{width:100%;overflow-x:auto}", page)
        self.assertEqual(2, page.count("class='table-scroll'"))
        self.assertIn("script-src &#39;none&#39;", page)
        self.assertNotIn("<script", page)
        self.assertNotIn("http://", page)
        self.assertNotIn("https://", page)

    def test_fractional_seconds_timeline_is_chronological(self):
        report = dict(self.report)
        report["events"] = [dict(event) for event in self.report["events"]]
        report["events"][0]["occurred_at_utc"] = "2026-10-25T15:01:00Z"
        report["events"][1]["occurred_at_utc"] = "2026-10-25T15:01:00.500000Z"
        report["events"][2]["occurred_at_utc"] = "2026-10-25T15:01:01Z"
        before = json.dumps(report, sort_keys=True)
        page = render(report)
        first = page.index('<td data-label="일시 (UTC)">2026-10-25T15:01:00Z</td>')
        second = page.index('<td data-label="일시 (UTC)">2026-10-25T15:01:00.500000Z</td>')
        third = page.index('<td data-label="일시 (UTC)">2026-10-25T15:01:01Z</td>')
        self.assertLess(first, second)
        self.assertLess(second, third)
        self.assertEqual(before, json.dumps(report, sort_keys=True))

    def test_equal_timestamp_timeline_uses_event_id_order(self):
        report = dict(self.report)
        report["events"] = [dict(event) for event in reversed(self.report["events"])]
        for event in report["events"]:
            event["occurred_at_utc"] = "2026-10-25T15:01:00Z"
        page = render(report)
        timeline = page.split("이벤트 타임라인 (UTC)</h2>", 1)[1]
        self.assertLess(timeline.index('>evt-001</td>'), timeline.index('>evt-002</td>'))
        self.assertLess(timeline.index('>evt-002</td>'), timeline.index('>evt-003</td>'))

    def test_malicious_metadata_escaped(self):
        report = dict(self.report)
        report["events"] = [dict(event) for event in self.report["events"]]
        report["findings"] = [dict(f) for f in self.report["findings"]]
        report["events"][0]["agent_id"] = '<img src=x onerror="alert(1)">'
        report["findings"][0]["rationale"] = '<script>alert("danger")</script>'
        page = render(report)
        self.assertNotIn("<img src=x", page)
        self.assertNotIn("<script>", page)
        self.assertIn("&lt;img src=x onerror=&quot;alert(1)&quot;&gt;", page)
        self.assertIn("&lt;script&gt;alert(&quot;danger&quot;)&lt;/script&gt;", page)

    def test_empty_fallback(self):
        report = dict(self.report)
        report["findings"] = []
        report["events"] = []
        report["finding_count"] = 0
        report["event_count"] = 0
        page = render(report)
        self.assertIn("탐지된 규칙 위반 없음", page)
        self.assertIn("입력된 이벤트 없음", page)
        self.assertNotIn("위험 소견 5건", page)

    def test_privacy_gate_rejects_sensitive_event_values_before_output(self):
        for field, value in (
            ("agent_id", "person@example.com"),
            ("source_pointer", "sk-" + "Q" * 28),
        ):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                source = Path(tmp) / "synthetic.json"
                destination = Path(tmp) / "preview.html"
                document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
                document["events"][0][field] = value
                source.write_text(json.dumps(document), encoding="utf-8")
                with self.assertRaisesRegex(
                        PreviewError, "^PREVIEW_INPUT_OR_OUTPUT_REJECTED$"):
                    preview_files(source, destination)
                self.assertFalse(destination.exists())
                self.assertIn(value, source.read_text(encoding="utf-8"))

    def test_privacy_gate_isolated_cli_hides_token_and_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "synthetic.json"
            destination = Path(tmp) / "preview.html"
            secret = "sk-" + "R" * 28
            document = json.loads(EXAMPLE.read_text(encoding="utf-8"))
            document["events"][0]["source_pointer"] = secret
            source.write_text(json.dumps(document), encoding="utf-8")
            cmd = [sys.executable, "-I", "-B",
                   str(ROOT / "sovia_report_print_preview.py"),
                   "--input", str(source), "--output", str(destination),
                   "--synthetic-only"]
            outcome = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            self.assertEqual(2, outcome.returncode)
            self.assertEqual(
                "PREVIEW_INPUT_OR_OUTPUT_REJECTED",
                json.loads(outcome.stderr)["error_code"])
            self.assertNotIn(secret, outcome.stderr)
            self.assertNotIn(str(source), outcome.stderr)
            self.assertNotIn(str(destination), outcome.stderr)
            self.assertFalse(destination.exists())

    def test_real_synthetic_cli_isolated_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "preview.html"
            argv = [sys.executable, "-I", "-B", str(ROOT / "sovia_report_print_preview.py"),
                    "--input", str(EXAMPLE), "--output", str(dest), "--synthetic-only"]
            first = subprocess.run(argv, capture_output=True, text=True, timeout=20)
            self.assertEqual(0, first.returncode, first.stderr)
            obj = json.loads(first.stdout)
            self.assertEqual((3, 5), (obj["events"], obj["findings"]))
            self.assertFalse(obj["commercial_release_authorized"])
            before = dest.read_bytes()
            self.assertTrue(before.startswith(b"<!doctype html>"))
            second = subprocess.run(argv, capture_output=True, text=True, timeout=20)
            self.assertEqual(2, second.returncode)
            self.assertEqual(before, dest.read_bytes())
            self.assertNotIn(str(EXAMPLE), second.stderr)
            self.assertNotIn(str(dest), second.stderr)

    def test_no_unacknowledged_or_input_alias(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "new.html"
            cmd = [sys.executable, "-I", "-B", str(ROOT / "sovia_report_print_preview.py"),
                   "--input", str(EXAMPLE), "--output", str(output)]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            self.assertEqual(2, proc.returncode)
            self.assertFalse(output.exists())
            with self.assertRaisesRegex(PreviewError, "PREVIEW_OUTPUT_ALIASES_INPUT"):
                preview_files(EXAMPLE, EXAMPLE)
            self.assertFalse(output.exists())

    def test_preexisting_destination_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "original.html"
            dest.write_bytes(b"DO_NOT_TOUCH")
            with self.assertRaisesRegex(PreviewError, "PREVIEW_OUTPUT_EXISTS"):
                preview_files(EXAMPLE, dest)
            self.assertEqual(b"DO_NOT_TOUCH", dest.read_bytes())


if __name__ == "__main__":
    unittest.main()
