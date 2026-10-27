"""Isolated v0.12 history v2 has distinct report identity and rejects legacy v1."""
from __future__ import annotations
from contextlib import closing
import copy
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import sovia_history_v012 as h
import sovia_history as old
import sovia_audit

SAMPLE = ROOT/"examples"/"demo_temporal_boundary.json"
DEMO = ROOT/"examples"/"demo_five_rules.json"


class HistoryV012Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root/"new.sqlite3"

    def test_versioned_uid_distinct_from_original_id(self):
        result = h.import_synthetic(self.db,SAMPLE)
        source = sovia_audit.read_document(SAMPLE)
        old_id = sovia_audit.evaluate(source)["report_id"]
        self.assertNotEqual(old_id,result["report_uid"])
        self.assertEqual(64,len(result["report_uid"]))
        self.assertEqual({"schema_version":2,"engine_version":"0.12.0-preview",
                          "reports":1,"event_count_total":3,
                          "finding_count_total":0,"v1_compatible":False},h.status(self.db))

    def test_idempotent_same_input_does_not_duplicate(self):
        a=h.import_synthetic(self.db,SAMPLE)
        b=h.import_synthetic(self.db,SAMPLE)
        self.assertEqual(a["report_uid"],b["report_uid"])
        self.assertEqual("already_present",b["status"])
        self.assertEqual(1,h.status(self.db)["reports"])

    def test_two_inputs_are_distinct_versioned_reports(self):
        h.import_synthetic(self.db,SAMPLE)
        h.import_synthetic(self.db,DEMO)
        self.assertEqual(2,h.status(self.db)["reports"])
        self.assertEqual(5,h.status(self.db)["finding_count_total"])

    def test_storage_contains_no_raw_metadata(self):
        h.import_synthetic(self.db,SAMPLE)
        raw=self.db.read_bytes()
        for value in (b"synthetic-agent",b"public_docs",b"internal.example",
                      b"synthetic:1",b"client_records"):
            self.assertNotIn(value,raw)
        with closing(sqlite3.connect(self.db)) as db:
            self.assertEqual(2,db.execute("PRAGMA user_version").fetchone()[0])
            self.assertEqual("0.12.0-preview",
                             db.execute("SELECT engine_version FROM reports").fetchone()[0])

    def test_original_v1_refused_without_database_mutation(self):
        original=self.root/"legacy.sqlite3"
        old.import_report(original,DEMO)
        before=original.read_bytes()
        with self.assertRaisesRegex(h.HistoryV012Error,"INCOMPATIBLE_HISTORY_SCHEMA"):
            h.import_synthetic(original,SAMPLE)
        self.assertEqual(before,original.read_bytes())
        with self.assertRaisesRegex(h.HistoryV012Error,"INCOMPATIBLE_HISTORY_SCHEMA"):
            h.status(original)
        self.assertEqual(before,original.read_bytes())

    def test_v2_refused_by_legacy_without_changes(self):
        h.import_synthetic(self.db,SAMPLE)
        before=self.db.read_bytes()
        with self.assertRaises(old.HistoryError):
            old.status(self.db)
        self.assertEqual(before,self.db.read_bytes())

    def test_backup_restore_retains_versioned_rows_and_idempotency(self):
        h.import_synthetic(self.db,SAMPLE)
        backup=self.root/"backup.sqlite3"
        clone=self.root/"restored.sqlite3"
        self.assertEqual("snapshot_created",h.backup(self.db,backup)["status"])
        self.assertEqual("snapshot_created",h.restore(backup,clone)["status"])
        self.assertEqual(h.status(self.db),h.status(clone))
        self.assertEqual("already_present",h.import_synthetic(clone,SAMPLE)["status"])

    def test_backup_and_restore_never_overwrite(self):
        h.import_synthetic(self.db,SAMPLE)
        existing=self.root/"keep.sqlite3"
        existing.write_bytes(b"DO_NOT_OVERWRITE")
        with self.assertRaises(h.HistoryV012Error):
            h.backup(self.db,existing)
        self.assertEqual(b"DO_NOT_OVERWRITE",existing.read_bytes())

    def test_old_db_cannot_be_used_as_backup_source(self):
        legacy=self.root/"old.sqlite3"
        old.import_report(legacy,DEMO)
        destination=self.root/"forbidden.sqlite3"
        with self.assertRaisesRegex(h.HistoryV012Error,"INCOMPATIBLE_HISTORY_SCHEMA"):
            h.restore(legacy,destination)
        self.assertFalse(destination.exists())

    def test_reject_invalid_source_without_creating_db(self):
        malformed=self.root/"bad.json"
        malformed.write_text("{bad",encoding="utf-8")
        with self.assertRaises(ValueError):
            h.import_synthetic(self.db,malformed)
        self.assertFalse(self.db.exists())

    def test_reject_source_with_credential_without_creating_db(self):
        doc=sovia_audit.read_document(SAMPLE)
        doc["events"][0]["agent_id"]="user@example.com"
        input_path=self.root/"secret.json"
        input_path.write_text(json.dumps(doc),encoding="utf-8")
        with self.assertRaises(ValueError):
            h.import_synthetic(self.db,input_path)
        self.assertFalse(self.db.exists())

    def test_alias_source_database_is_rejected(self):
        self.db.write_bytes(SAMPLE.read_bytes())
        with self.assertRaisesRegex(h.HistoryV012Error,"INVALID_SOURCE_OR_ALIAS"):
            h.import_synthetic(self.db,self.db)
        self.assertEqual(SAMPLE.read_bytes(),self.db.read_bytes())

    def test_isolated_cli_ack_and_no_pii_in_error(self):
        new=self.root/"fresh.sqlite3"
        cmd=[sys.executable,"-I","-B",str(ROOT/"sovia_history_v012.py"),
             "import","--db",str(new),"--input",str(SAMPLE)]
        denied=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
        self.assertEqual(2,denied.returncode)
        self.assertEqual("SYNTHETIC_ACK_REQUIRED",json.loads(denied.stderr)["error_code"])
        self.assertFalse(new.exists())
        cmd.append("--synthetic-only")
        allowed=subprocess.run(cmd,capture_output=True,text=True,timeout=25)
        self.assertEqual(0,allowed.returncode,allowed.stderr)
        self.assertEqual(1,h.status(new)["reports"])
        self.assertNotIn(str(SAMPLE),allowed.stdout)

    def test_conflict_same_uid_different_findings_is_rejected(self):
        h.import_synthetic(self.db,SAMPLE)
        with closing(sqlite3.connect(self.db)) as db:
            db.execute("UPDATE reports SET findings_digest=?",("f"*64,))
            db.commit()  # closing() does not implicitly commit
        with self.assertRaisesRegex(h.HistoryV012Error,"VERSIONED_RESULT_CONFLICT"):
            h.import_synthetic(self.db,SAMPLE)
        self.assertEqual(1,h.status(self.db)["reports"])


if __name__=="__main__":
    unittest.main()
