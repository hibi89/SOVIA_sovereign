"""SOVIA P2 read-only static dashboard: synthetic and adversarial regression."""
from contextlib import closing
from html.parser import HTMLParser
import json
from pathlib import Path
import shutil
import socket
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_history as history
import sovia_dashboard as board

class CountingHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = 0
        self.trows = 0
        self.sections = 0
        self.scripts = 0
    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.tables += 1
        if tag == "tr":
            self.trows += 1
        if tag == "section":
            self.sections += 1
        if tag == "script":
            self.scripts += 1

class DashboardTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root / "history.sqlite"
        self.out = self.root / "dashboard.html"
        self.sample = ROOT / "examples/demo_five_rules.json"

    def _import(self):
        return history.import_report(self.db, self.sample)

    def _cli(self, db=None, out=None, isolated=False, exe=None):
        cmd = [sys.executable]
        if isolated:
            cmd.extend(("-I", "-B"))
        cmd.extend((str(exe or ROOT / "sovia_dashboard.py"),
                    "--db", str(self.db if db is None else db),
                    "--output", str(self.out if out is None else out)))
        return subprocess.run(cmd, capture_output=True, text=True, timeout=20)

    def test_synthetic_counts_risk_tables_and_timeline(self):
        self._import()
        s = board.read_snapshot(self.db)
        self.assertEqual({"reports": 1, "events": 3, "findings": 5,
                          "report_events": 3, "missing_pointers": 1}, s["totals"])
        self.assertEqual(5, len(s["rules"]))
        self.assertEqual(3, len(s["events"]))
        html = board.render_html(s)
        for expected in ("감사 보고서", "위험 소견", "위험 등급별 분포",
                         "규칙별 감지 건수", "최근 감사 보고서",
                         "최근 위험 소견", "최근 이벤트 타임라인",
                         "미제공", "제공(미검증)", "5"):
            self.assertIn(expected, html)
        parsed = CountingHTMLParser()
        parsed.feed(html)
        self.assertEqual((5, 5, 0), (parsed.tables, parsed.sections, parsed.scripts))

    def test_successful_cli_snapshot_counts_and_file(self):
        self._import()
        proc = self._cli()
        self.assertEqual(0, proc.returncode, proc.stderr)
        status = json.loads(proc.stdout)
        self.assertEqual({"status": "dashboard_created", "reports": 1,
                          "events": 3, "findings": 5}, status)
        html = self.out.read_text(encoding="utf-8")
        self.assertTrue(html.startswith("<!doctype html>"))
        self.assertIn("SOVIA SOVEREIGN", html)

    def test_empty_database_honest_empty_state(self):
        self._import()
        history.purge(self.db, all_reports=True, confirmed=True)
        data = board.read_snapshot(self.db)
        self.assertEqual((0, 0, 0), (data["totals"]["reports"],
                                   data["totals"]["events"], data["totals"]["findings"]))
        rendered = board.render_html(data)
        self.assertEqual(5, rendered.count("기록 없음 (안전성 보증 아님)"))

    def test_html_escaping_for_untrusted_rule_and_timestamp(self):
        self._import()
        bad = "<img src=x onerror=alert('pwn')> & \"q\""
        with closing(sqlite3.connect(self.db)) as db:
            with db:
                db.execute("UPDATE findings SET rule_id=?", (bad,))
                db.execute("UPDATE events SET occurred_at_utc=?", ("<script>evil</script>",))
                db.execute("UPDATE reports SET imported_utc=?", (bad,))
        html = board.render_html(board.read_snapshot(self.db))
        self.assertNotIn("<img", html)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;img", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&quot;q&quot;", html)
        self.assertIn("&amp;", html)

    def test_no_dynamic_script_network_external_asset_or_form(self):
        self._import()
        page = board.render_html(board.read_snapshot(self.db))
        for forbidden in ("<script", "<iframe", "<form", "<link", "<img", "<base",
                          "https://", "http://", "fetch(", "XMLHttpRequest", "window."):
            self.assertNotIn(forbidden, page)
        for required in ("default-src 'none'", "script-src 'none'", "connect-src 'none'",
                         "style-src 'unsafe-inline'", "<meta charset='utf-8'>"):
            self.assertIn(required, page)

    def test_raw_labels_and_prompts_are_never_exported(self):
        self._import()
        html = board.render_html(board.read_snapshot(self.db))
        for secret in ("demo-agent", "demo-001", "evt-001",
                       "unauthorized_export", "client_records", "outside.example",
                       "synthetic:1", "raw_prompt"):
            self.assertNotIn(secret, html)
        self.assertIn("해시", html)
        self.assertIn("재식별", html)

    def test_history_database_unchanged_after_export(self):
        self._import()
        before = self.db.read_bytes()
        board.export_dashboard(self.db, self.out)
        self.assertEqual(before, self.db.read_bytes())
        self.assertEqual(1, history.status(self.db)["reports"])

    def test_export_twice_identical_snapshot_deterministic_when_new_names(self):
        self._import()
        board.export_dashboard(self.db, self.out)
        first = self.out.read_bytes()
        second = self.root / "second.html"
        board.export_dashboard(self.db, second)
        self.assertEqual(first, second.read_bytes())

    def test_never_overwrites_existing_html(self):
        self._import()
        self.out.write_text("KEEP-ORIGINAL", encoding="utf-8")
        result = self._cli()
        self.assertEqual(2, result.returncode)
        self.assertEqual("KEEP-ORIGINAL", self.out.read_text(encoding="utf-8"))
        self.assertEqual([], list(self.root.glob(".sovia-staging-*")))

    def test_no_file_when_database_missing(self):
        result = self._cli()
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.db.exists())
        self.assertFalse(self.out.exists())

    def test_output_cannot_alias_source_database(self):
        self._import()
        before = self.db.read_bytes()
        result = self._cli(out=self.db)
        self.assertEqual(2, result.returncode)
        self.assertIn("differ", result.stderr)
        self.assertEqual(before, self.db.read_bytes())

    def test_missing_output_directory_fails_without_writing(self):
        self._import()
        result = self._cli(out=self.root / "missing-dir" / "dashboard.html")
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.root / "missing-dir").exists())

    def test_wrong_schema_or_garbage_do_not_create_output(self):
        self._import()
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("PRAGMA user_version=99")
        result = self._cli()
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.out.exists())

    def test_corrupted_database_does_not_create_output(self):
        self.db.write_bytes(b"BAD SQLITE")
        result = self._cli()
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.out.exists())

    def test_selected_overview_is_bounded_to_100_rows(self):
        self._import()
        with closing(sqlite3.connect(self.db)) as db:
            with db:
                for n in range(121):
                    db.execute("INSERT INTO reports VALUES (?,?,?,?,?,?)",
                               (f"mock{n:06d}", "a" * 64, "test", f"2026-10-26T00:{n:03d}:00Z",
                                0, 0))
        data = board.read_snapshot(self.db)
        self.assertEqual(122, data["totals"]["reports"])
        self.assertEqual(100, len(data["reports"]))
        self.assertEqual(100, board.MAX_ROWS)
        self.assertIn("최신 100건까지만 표시", board.render_html(data))

    def test_groups_bounded_without_misrepresenting_total(self):
        self._import()
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("PRAGMA foreign_keys=ON")
            report_id, event_id = db.execute(
                "SELECT report_id, identity_sha256 FROM report_events LIMIT 1"
            ).fetchone()
            with db:
                for n in range(25):
                    fid = f"mock{n:04d}"
                    db.execute("INSERT INTO findings VALUES (?,?,?,?,?,?)",
                               (report_id, fid, event_id,
                                f"RULE_{n}", "MEDIUM", "POINTER_MISSING"))
        # Direct SQL simulates unusual rule variety while FK integrity remains valid.
        self.assertLessEqual(len(board.read_snapshot(self.db)["rules"]), 20)

    def test_html_is_bounded_even_with_long_metadata(self):
        snapshot = {"totals": {"reports": 0, "events": 0, "findings": 0,
                               "report_events": 0, "missing_pointers": 0},
                    "severities": [("X" * 5_000, 1)], "rules": [],
                    "reports": [], "findings": [], "events": []}
        page = board.render_html(snapshot)
        self.assertNotIn("X" * 161, page)

    def test_purged_report_disappears_from_new_snapshot(self):
        self._import()
        before = board.read_snapshot(self.db)
        self.assertEqual(1, before["totals"]["reports"])
        history.purge(self.db, all_reports=True, confirmed=True)
        page = board.render_html(board.read_snapshot(self.db))
        self.assertIn("기록 없음 (안전성 보증 아님)", page)
        self.assertNotIn(before["reports"][0][0], page)

    def test_bad_symlink_output_rejected(self):
        self._import()
        missing = self.root / "not-existing.html"
        try:
            self.out.symlink_to(missing)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable on runner")
        result = self._cli()
        self.assertEqual(2, result.returncode)
        self.assertTrue(self.out.is_symlink())
        self.assertFalse(missing.exists())

    def test_symlink_source_db_not_accepted(self):
        self._import()
        link = self.root / "link.sqlite"
        try:
            link.symlink_to(self.db)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable on runner")
        result = self._cli(db=link)
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.out.exists())

    def test_isolated_python_extracted_copy_works(self):
        dest = self.root / "clean"
        dest.mkdir()
        for name in ("sovia_dashboard.py", "sovia_history.py", "sovia_audit.py"):
            shutil.copyfile(ROOT / name, dest / name)
        self._import()
        report = dest / "report.html"
        result = self._cli(out=report, isolated=True, exe=dest / "sovia_dashboard.py")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("최근 이벤트 타임라인", report.read_text(encoding="utf-8"))

    def test_no_network_needed_for_snapshot_or_html(self):
        self._import()
        with patch.object(socket, "socket", side_effect=AssertionError("unexpected network")):
            self.assertIn("에이전트 감사 이력", board.render_html(board.read_snapshot(self.db)))

    def test_no_file_if_sqlite_verification_fails(self):
        self._import()
        with patch.object(board, "read_snapshot", side_effect=board.DashboardError("unverified")):
            with self.assertRaises(board.DashboardError):
                board.export_dashboard(self.db, self.out)
        self.assertFalse(self.out.exists())


if __name__ == "__main__":
    unittest.main()
