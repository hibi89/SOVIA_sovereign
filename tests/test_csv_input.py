"""Synthetic-only source CSV import validation and CLI contract tests."""
import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sovia_csv_input import read_csv_events, CSVInputError, MAX_CSV_BYTES, MAX_CSV_EVENTS
from sovia_audit import read_document, evaluate, AuditInputError

HEAD=["event_id","occurred_at_utc","agent_id","run_id","tool_name","permission_asserted"]
VALID=["e1","2026-10-26T00:00:00Z","agent","run","safe","false"]

class CSVSourceParserTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"source.csv"
    def rows(self,header=HEAD,rows=(VALID,)):
        with self.path.open("w",encoding="utf-8",newline="") as stream:
            w=csv.writer(stream);w.writerow(header);w.writerows(rows)
        return self.path
    def test_false_is_not_true(self):
        self.assertIs(read_csv_events(self.rows())[0]["permission_asserted"],False)
    def test_true(self):
        self.assertIs(read_csv_events(self.rows(rows=[VALID[:-1]+["true"]]))[0]["permission_asserted"],True)
    def test_blank_permission_unknown(self):
        self.assertNotIn("permission_asserted",read_csv_events(self.rows(rows=[VALID[:-1]+[""]]))[0])
    def test_bad_boolean(self):
        self.rows(rows=[VALID[:-1]+["TRUE"]])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_raw_prompt_column_rejected(self):
        self.rows(HEAD+["raw_prompt"],[VALID+["SECRET"]])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_duplicate_header_rejected(self):
        self.rows(HEAD+["event_id"],[VALID+["e2"]])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_missing_required_header(self):
        self.rows(HEAD[:-2],[VALID[:-2]])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_short_row(self):
        self.rows(rows=[VALID[:-1]])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_extra_cell(self):
        self.rows(rows=[VALID+["extra"]])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_utf8_bom(self):
        self.rows(rows=[VALID[:-2]+["한국어 도구","true"]])
        self.path.write_bytes(b"\xef\xbb\xbf"+self.path.read_bytes())
        self.assertEqual("한국어 도구",read_csv_events(self.path)[0]["tool_name"])
    def test_bad_utf8(self):
        self.path.write_bytes(b"\xff")
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_nul(self):
        self.path.write_bytes(b"x\x00")
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_byte_cap(self):
        self.path.write_bytes(b"a"*(MAX_CSV_BYTES+1))
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_row_cap(self):
        self.rows(rows=[["e"+str(i)]+VALID[1:] for i in range(MAX_CSV_EVENTS+1)])
        self.assertRaises(CSVInputError,read_csv_events,self.path)
    def test_quote_comma_roundtrip(self):
        self.rows(rows=[VALID[:-2]+["safe,with comma","true"]])
        self.assertEqual("safe,with comma",read_csv_events(self.path)[0]["tool_name"])
    def test_formula_is_inert(self):
        self.rows(rows=[VALID[:-2]+['=HYPERLINK("x")',"false"]])
        self.assertEqual('=HYPERLINK("x")',read_csv_events(self.path)[0]["tool_name"])
    def test_unterminated_quote(self):
        self.path.write_text(",".join(HEAD)+'\n"unterminated,bad,line',encoding="utf8")
        self.assertRaises(CSVInputError,read_csv_events,self.path)

class CSVSourceCLITests(unittest.TestCase):
    def _run(self,root,source=None,policy=None,isolated=False,extra=None):
        src=source or ROOT/"examples/demo_source.csv"
        cmd=[sys.executable]
        if isolated:cmd.extend(["-I","-B"])
        cmd.extend([str(root/"sovia_audit.py") if isolated else str(ROOT/"sovia_audit.py"),
                    "--input",str(src),"--output",str(root/"result.html"),
                    "--json-output",str(root/"result.json")])
        if policy is not False:
            cmd.extend(["--policy",str(policy or ROOT/"examples/demo_policy.json")])
        if extra:cmd.extend(extra)
        return subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    def test_oracle_equivalent_to_json(self):
        policy=read_document(ROOT/"examples/demo_policy.json")
        doc={"schema_version":"1.0","policy":policy["policy"],
             "events":read_csv_events(ROOT/"examples/demo_source.csv")}
        self.assertEqual(evaluate(read_document(ROOT/"examples/demo_five_rules.json")),evaluate(doc))
    def test_cli_html_json_five_rules(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run=self._run(root)
            self.assertEqual(0,run.returncode,run.stderr)
            self.assertEqual(5,json.loads((root/"result.json").read_text(encoding="utf-8"))["finding_count"])
            self.assertIn("이벤트 타임라인",(root/"result.html").read_text(encoding="utf-8"))
    def test_policy_required(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);run=self._run(root,policy=False)
            self.assertEqual(2,run.returncode)
            self.assertFalse((root/"result.html").exists())
    def test_bad_policy_no_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            bad=root/"policy.json";bad.write_text('{"schema_version":"1.0","policy":{},"events":[]}',encoding="utf-8")
            run=self._run(root,policy=bad)
            self.assertEqual(2,run.returncode)
            self.assertFalse((root/"result.json").exists())
    def test_source_rejected_without_partial_reports(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);src=root/"bad.csv"
            src.write_text("event_id,raw_prompt\n1,secret\n",encoding="utf-8")
            run=self._run(root,source=src)
            self.assertEqual(2,run.returncode)
            self.assertFalse((root/"result.html").exists())
    def test_cannot_overwrite_policy_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);p=root/"policy.json"
            original=(ROOT/"examples/demo_policy.json").read_text(encoding="utf-8")
            p.write_text(original,encoding="utf-8")
            result=self._run(root,policy=p,extra=["--events-csv",str(p)])
            self.assertEqual(2,result.returncode)
            self.assertEqual(original,p.read_text(encoding="utf-8"))
            self.assertFalse((root/"result.html").exists())
    def test_isolated_python_csv_package(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for name in ("sovia_audit.py","sovia_csv_input.py"):
                shutil.copy(ROOT/name,root/name)
            run=self._run(root,isolated=True)
            self.assertEqual(0,run.returncode,run.stderr)
            self.assertEqual(5,json.loads((root/"result.json").read_text(encoding="utf-8"))["finding_count"])
    def test_no_external_network_required(self):
        import socket
        from unittest.mock import patch
        with patch.object(socket,"socket",side_effect=AssertionError("No network allowed")):
            policy=read_document(ROOT/"examples/demo_policy.json")
            report=evaluate({"schema_version":"1.0","policy":policy["policy"],
                             "events":read_csv_events(ROOT/"examples/demo_source.csv")})
            self.assertEqual(5,report["finding_count"])
