"""Synthetic-only SQLite history tests: idempotency, conflicts, delete, backup, restore."""
import copy
from contextlib import closing
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
import sovia_history as h
from sovia_audit import evaluate, read_document


class SQLiteHistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.db = self.root / "audit.sqlite"
        self.example = ROOT / "examples/demo_five_rules.json"
        self.report = evaluate(read_document(self.example))

    def insert(self):
        return h.import_report(self.db, self.example)

    def run_cli(self, *args, isolated=False, executable=None):
        argv = [sys.executable]
        if isolated:
            argv.extend(["-I", "-B"])
        argv += [str(executable or ROOT / "sovia_history.py"), *map(str, args)]
        return subprocess.run(argv, capture_output=True, text=True, timeout=20)

    def test_first_import_has_five_findings_and_three_events(self):
        self.assertEqual("imported", self.insert()["status"])
        self.assertEqual({"schema_version": 1, "reports": 1, "events": 3,
                          "findings": 5, "report_events": 3}, h.status(self.db))

    def test_repeat_identical_is_noop(self):
        self.insert()
        initial = h.status(self.db)
        self.assertEqual("already_present", self.insert()["status"])
        self.assertEqual(initial, h.status(self.db))

    def test_csv_and_json_synthetic_contract_idempotent(self):
        self.insert()
        result = h.import_report(self.db, ROOT / "examples/demo_source.csv",
                                 ROOT / "examples/demo_policy.json")
        self.assertEqual("already_present", result["status"])
        self.assertEqual(1, h.status(self.db)["reports"])

    def test_same_identity_changed_payload_rolls_back(self):
        self.insert()
        doc = read_document(self.example)
        doc["events"][0]["tool_name"] = "DIFFERENT_TOOL"
        changed = self.root / "changed.json"
        changed.write_text(json.dumps(doc), encoding="utf-8")
        with self.assertRaisesRegex(h.HistoryError, "conflicting metadata"):
            h.import_report(self.db, changed)
        self.assertEqual((1, 3, 5), (h.status(self.db)["reports"],
                                   h.status(self.db)["events"],
                                   h.status(self.db)["findings"]))

    def test_policy_change_new_report_reuses_events(self):
        self.insert()
        doc = read_document(self.example)
        doc["policy"]["allowed_tools"] = ["approved_lookup", "unauthorized_export"]
        changed = self.root / "policychange.json"
        changed.write_text(json.dumps(doc), encoding="utf-8")
        self.assertEqual("imported", h.import_report(self.db, changed)["status"])
        self.assertEqual(2, h.status(self.db)["reports"])
        self.assertEqual(3, h.status(self.db)["events"])
        self.assertEqual(6, h.status(self.db)["report_events"])

    def test_database_contains_only_hash_metadata(self):
        self.insert()
        raw = self.db.read_bytes()
        for private in (b"evt-001", b"client_records", b"unauthorized_export",
                        b"demo-agent", b"synthetic:1", b"outside.example"):
            self.assertNotIn(private, raw)
        with closing(sqlite3.connect(self.db)) as c:
            self.assertEqual(["agent_sha256", "content_sha256", "engine_version",
                              "event_count", "evidence_status", "finding_count",
                              "finding_sha256", "identity_sha256", "imported_utc",
                              "occurred_at_utc", "payload_sha256", "report_id",
                              "rule_id", "run_sha256", "severity",
                              "source_pointer_present", "tool_sha256"],
                             sorted({x[1] for name in h.TABLES
                                     for x in c.execute("PRAGMA table_info(" + name + ")")}))

    def test_raw_prompt_is_dropped_even_if_source_contains_it(self):
        doc = read_document(self.example)
        doc["events"][0]["raw_prompt"] = "PRIVATE_MARKER_12345"
        src = self.root / "prompt.json"
        src.write_text(json.dumps(doc), encoding="utf-8")
        h.import_report(self.db, src)
        self.assertNotIn(b"PRIVATE_MARKER_12345", self.db.read_bytes())

    def test_missing_invalid_input_does_not_create_db(self):
        bad = self.root / "invalid.json"
        bad.write_text("{invalid}", encoding="utf-8")
        with self.assertRaises(ValueError):
            h.import_report(self.db, bad)
        self.assertFalse(self.db.exists())

    def test_csv_without_policy_does_not_create_db(self):
        with self.assertRaises(h.HistoryError):
            h.import_report(self.db, ROOT / "examples/demo_source.csv")
        self.assertFalse(self.db.exists())

    def test_conflicting_db_source_path_rejected(self):
        self.example = self.db
        with self.assertRaises(h.HistoryError):
            self.insert()
        self.assertFalse(self.db.exists())

    def test_status_nonexistent_does_not_create_db(self):
        with self.assertRaises(h.HistoryError):
            h.status(self.db)
        self.assertFalse(self.db.exists())

    def test_preexisting_unrecognized_db_not_overwritten(self):
        self.db.write_bytes(b"ORIGINAL-NOT-SQLITE")
        orig = self.db.read_bytes()
        with self.assertRaises((h.HistoryError, sqlite3.DatabaseError)):
            self.insert()
        self.assertEqual(orig, self.db.read_bytes())

    def test_unknown_future_version_blocked(self):
        self.insert()
        with closing(sqlite3.connect(self.db)) as c:
            c.execute("PRAGMA user_version=99")
        with self.assertRaises(h.HistoryError):
            h.status(self.db)

    def test_known_v1_schema_and_integrity(self):
        self.insert()
        with closing(sqlite3.connect(self.db)) as c:
            self.assertEqual(1, c.execute("PRAGMA user_version").fetchone()[0])
            self.assertEqual("ok", c.execute("PRAGMA integrity_check").fetchone()[0])
            self.assertEqual([], list(c.execute("PRAGMA foreign_key_check")))

    def test_report_id_hash_collision_guard(self):
        self.insert()
        fake = copy.deepcopy(self.report)
        fake["normalized_policy_sha256"] = fake["report_id"] + "0" * 48
        with closing(sqlite3.connect(self.db)) as c:
            with self.assertRaises(h.HistoryError):
                h._import_transaction(c, fake)
        self.assertEqual(1, h.status(self.db)["reports"])

    def test_backup_and_restore_roundtrip_without_change(self):
        self.insert()
        backup = self.root / "snapshot.sqlite"
        new_db = self.root / "restored.sqlite"
        self.assertEqual("snapshot_created", h.backup(self.db, backup)["status"])
        self.assertEqual(h.status(self.db), h.status(backup))
        self.assertEqual("snapshot_created", h.restore(backup, new_db)["status"])
        self.assertEqual(h.status(self.db), h.status(new_db))
        self.assertEqual("already_present", h.import_report(new_db, self.example)["status"])

    def test_backup_destination_never_clobbered(self):
        self.insert()
        backup = self.root / "keep.sqlite"
        backup.write_bytes(b"KEEP")
        with self.assertRaises(h.HistoryError):
            h.backup(self.db, backup)
        self.assertEqual(b"KEEP", backup.read_bytes())

    def test_restore_destination_never_clobbered(self):
        self.insert()
        backup = self.root / "backup.sqlite"
        h.backup(self.db, backup)
        existing = self.root / "keep.sqlite"
        existing.write_bytes(b"KEEP")
        with self.assertRaises(h.HistoryError):
            h.restore(backup, existing)
        self.assertEqual(b"KEEP", existing.read_bytes())

    def test_corrupt_restore_does_not_create_target(self):
        backup = self.root / "corrupt.sqlite"
        backup.write_bytes(b"NOT-SQLITE")
        out = self.root / "fresh.sqlite"
        with self.assertRaises((h.HistoryError, sqlite3.DatabaseError)):
            h.restore(backup, out)
        self.assertFalse(out.exists())

    def test_backup_alias_same_path_refused(self):
        self.insert()
        with self.assertRaises(h.HistoryError):
            h.backup(self.db, self.db)
        self.assertEqual(1, h.status(self.db)["reports"])

    def test_delete_requires_explicit_confirmation(self):
        self.insert()
        with self.assertRaises(h.HistoryError):
            h.purge(self.db, all_reports=True)
        self.assertEqual(1, h.status(self.db)["reports"])

    def test_targeted_purge_removes_orphans(self):
        self.insert()
        result = h.purge(self.db, report_id=self.report["report_id"], confirmed=True)
        self.assertEqual(1, result["deleted_reports"])
        self.assertEqual((0, 0, 0), (h.status(self.db)["reports"],
                                   h.status(self.db)["events"],
                                   h.status(self.db)["findings"]))

    def test_targeted_purge_keeps_shared_events(self):
        self.test_policy_change_new_report_reuses_events()
        result = h.purge(self.db, report_id=self.report["report_id"], confirmed=True)
        self.assertEqual(1, result["deleted_reports"])
        self.assertEqual((1, 3, 3), (h.status(self.db)["reports"],
                                   h.status(self.db)["events"],
                                   h.status(self.db)["report_events"]))

    def test_delete_nonexistent_rolls_back(self):
        self.insert()
        with self.assertRaises(h.HistoryError):
            h.purge(self.db, report_id="not_found", confirmed=True)
        self.assertEqual(1, h.status(self.db)["reports"])

    def test_delete_all_requires_correct_selector(self):
        self.insert()
        with self.assertRaises(h.HistoryError):
            h.purge(self.db, report_id=self.report["report_id"], all_reports=True,
                    confirmed=True)
        self.assertEqual(1, h.status(self.db)["reports"])

    def test_purge_all_and_backup_remains_independent(self):
        self.insert()
        snap = self.root / "snap.sqlite"
        h.backup(self.db, snap)
        self.assertEqual(1, h.purge(self.db, all_reports=True, confirmed=True)["deleted_reports"])
        self.assertEqual(0, h.status(self.db)["reports"])
        self.assertEqual(1, h.status(snap)["reports"])

    def test_reimport_after_delete_is_valid(self):
        self.insert()
        h.purge(self.db, all_reports=True, confirmed=True)
        self.assertEqual("imported", self.insert()["status"])

    def test_cli_all_crud_actions(self):
        first = self.run_cli("import", "--db", self.db, "--input", self.example)
        self.assertEqual(0, first.returncode, first.stderr)
        self.assertEqual("imported", json.loads(first.stdout)["status"])
        status = self.run_cli("status", "--db", self.db)
        self.assertEqual(1, json.loads(status.stdout)["reports"])
        snap = self.root / "snap.sqlite"
        self.assertEqual(0, self.run_cli("backup", "--db", self.db,
                                         "--output", snap).returncode)
        self.assertEqual(0, self.run_cli("purge", "--db", self.db, "--all",
                                         "--confirm-delete").returncode)
        restored = self.root / "restore.sqlite"
        self.assertEqual(0, self.run_cli("restore", "--input", snap,
                                         "--db", restored).returncode)
        self.assertEqual(1, h.status(restored)["reports"])

    def test_cli_csv_input_and_policy(self):
        result = self.run_cli("import", "--db", self.db, "--input",
                              ROOT / "examples/demo_source.csv",
                              "--policy", ROOT / "examples/demo_policy.json")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(5, h.status(self.db)["findings"])

    def test_cli_invalid_exits_two_no_files(self):
        bad = self.root / "bad.json"
        bad.write_text("[]", encoding="utf-8")
        result = self.run_cli("import", "--db", self.db, "--input", bad)
        self.assertEqual(2, result.returncode)
        self.assertFalse(self.db.exists())

    def test_isolated_python_clean_package(self):
        dest = self.root / "pkg"
        dest.mkdir()
        for name in ("sovia_history.py", "sovia_audit.py", "sovia_csv_input.py"):
            shutil.copyfile(ROOT / name, dest / name)
        pkgdb = dest / "h.sqlite"
        result = self.run_cli("import", "--db", pkgdb, "--input", self.example,
                              isolated=True, executable=dest / "sovia_history.py")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(5, h.status(pkgdb)["findings"])

    def test_no_network_access_during_import(self):
        with patch.object(socket, "socket", side_effect=AssertionError("Network used")):
            self.assertEqual("imported", self.insert()["status"])

    def test_symlink_destination_rejected(self):
        if not hasattr(self.db, "symlink_to"):
            self.skipTest("Symlink not available")
        target = self.root / "outside.sqlite"
        try:
            self.db.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("OS disallows symlink creation")
        with self.assertRaises(h.HistoryError):
            self.insert()
        self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
