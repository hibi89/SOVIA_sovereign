"""P2 synthetic-only CSV output contract, no-clobber and formula-guard tests."""
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_audit import (evaluate, read_document, render_csv, _spreadsheet_safe,
                         write_reports_atomically, AuditInputError)


class CSVExportTests(unittest.TestCase):
    def setUp(self):
        self.demo = json.loads((ROOT / 'examples/demo_five_rules.json').read_text(encoding='utf-8'))
        self.report = evaluate(self.demo)

    def _parse(self, kind):
        text = render_csv(self.report, kind)
        self.assertTrue(text.startswith('\ufeff'))
        return list(csv.DictReader(io.StringIO(text.lstrip('\ufeff'), newline='')))

    def _run(self, directory, **paths):
        cmd = [sys.executable, str(ROOT / 'sovia_audit.py'), '--input',
               str(ROOT / 'examples/demo_five_rules.json'), '--output', str(directory / 'report.html')]
        for name, value in paths.items():
            cmd.extend(['--' + name.replace('_', '-'), str(value)])
        return subprocess.run(cmd, capture_output=True, text=True, timeout=15)

    def test_five_findings_export_and_evidence_metadata(self):
        rows = self._parse('findings')
        self.assertEqual(5, len(rows))
        self.assertEqual(5, len({row['rule_id'] for row in rows}))
        self.assertTrue(all(row['event_id'] == 'evt-003' for row in rows))
        self.assertTrue(all(row['report_id'] == self.report['report_id'] for row in rows))
        self.assertTrue(all(row['evidence_status'] == 'POINTER_MISSING' for row in rows))

    def test_timeline_export_sorted_and_stable(self):
        self.demo['events'].reverse()
        self.report = evaluate(self.demo)
        rows = self._parse('events')
        self.assertEqual(['evt-001', 'evt-002', 'evt-003'], [x['event_id'] for x in rows])
        self.assertEqual('2026-10-25T15:01:00Z', rows[0]['occurred_at_utc'])
        self.assertEqual(render_csv(self.report,'events'), render_csv(self.report,'events'))

    def test_csv_utf8_bom_and_korean_text_crlf(self):
        text = render_csv(self.report,'findings')
        self.assertTrue(text.encode('utf-8').startswith(b'\xef\xbb\xbf'))
        self.assertIn('허용 도구', text)
        self.assertIn('\r\n', text)
        self.assertNotIn('\r\r\n', text)

    def test_formula_values_guarded(self):
        for text in ['=2+3','+SUM(1,2)','-1+2','@NOW()', '   =HYPERLINK("x")',
                     '\ufeff=1', '\u200b=1', '\u00a0=3', ' \t=3']:
            with self.subTest(text=text):
                self.assertTrue(_spreadsheet_safe(text).startswith("'"))
        self.assertEqual('safe text',_spreadsheet_safe('safe text'))
        self.assertEqual('',_spreadsheet_safe(None))

    def test_attack_values_in_findings_and_timeline(self):
        self.demo['events'][2]['tool_name'] = '=HYPERLINK("http://example.invalid", "open")'
        self.demo['events'][2]['source_pointer'] = '+SUM(1,1)'
        self.demo['events'][2]['agent_id'] = '  @CMD'
        self.report = evaluate(self.demo)
        finds = self._parse('findings')
        events = self._parse('events')
        self.assertTrue(any(r['source_pointer'].startswith("'+SUM") for r in finds))
        self.assertTrue(events[-1]['tool_name'].startswith("'=HYPERLINK"))
        self.assertTrue(events[-1]['agent_id'].startswith("'  @CMD"))

    def test_csv_quotes_comma_and_newline_format(self):
        self.demo['events'][0]['target'] = 'a, "special" text'
        self.report = evaluate(self.demo)
        text = render_csv(self.report,'events')
        self.assertIn('"a, ""special"" text"', text)
        self.assertEqual('a, "special" text',self._parse('events')[0]['target'])

    def test_raw_prompt_never_in_csv(self):
        self.demo['events'][0]['raw_prompt'] = 'DO-NOT-EXPORT-SECRETS'
        self.report=evaluate(self.demo)
        self.assertNotIn('DO-NOT-EXPORT-SECRETS', render_csv(self.report, 'events'))
        self.assertNotIn('DO-NOT-EXPORT-SECRETS', render_csv(self.report, 'findings'))

    def test_safe_fixture_empty_findings_keeps_header(self):
        safe = json.loads((ROOT/'examples/demo.json').read_text(encoding='utf-8'))
        safe['events']=safe['events'][:1]
        self.report=evaluate(safe)
        text=render_csv(self.report,'findings')
        self.assertEqual(1, len(list(csv.reader(io.StringIO(text[1:])))))

    def test_unrecognized_kind_rejected(self):
        with self.assertRaises(ValueError):
            render_csv(self.report,'raw_events')

    def test_cli_all_four_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            proc=self._run(root,json_output=root/'report.json',findings_csv=root/'findings.csv',events_csv=root/'events.csv')
            self.assertEqual(0,proc.returncode,proc.stderr)
            self.assertIn('이벤트 타임라인', (root/'report.html').read_text(encoding='utf-8'))
            self.assertEqual(5,json.loads((root/'report.json').read_text(encoding='utf-8'))['finding_count'])
            with (root/'findings.csv').open(encoding='utf-8-sig',newline='') as f:
                self.assertEqual(5,len(list(csv.DictReader(f))))
            with (root/'events.csv').open(encoding='utf-8-sig',newline='') as f:
                self.assertEqual(3,len(list(csv.DictReader(f))))

    def test_existing_csv_preserved_and_other_reports_not_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            exists=root/'findings.csv'
            exists.write_text('KEEP ORIGINAL',encoding='utf-8')
            proc=self._run(root,findings_csv=exists,events_csv=root/'events.csv')
            self.assertEqual(2,proc.returncode)
            self.assertEqual('KEEP ORIGINAL', exists.read_text(encoding='utf-8'))
            self.assertFalse((root/'report.html').exists())
            self.assertFalse((root/'events.csv').exists())
            self.assertEqual([],list(root.glob('.sovia-staging-*')))

    def test_duplicate_output_paths_fail_before_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            path=root/'same.csv'
            proc=self._run(root,findings_csv=path,events_csv=path)
            self.assertEqual(2,proc.returncode)
            self.assertFalse(path.exists())
            self.assertFalse((root/'report.html').exists())

    def test_publish_error_in_fourth_item_cleans_previously_published(self):
        import sovia_audit
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            names=[root/n for n in ('a.html','b.json','c.csv','d.csv')]
            original=sovia_audit.os.link
            calls=0
            def fail_fourth(a,b):
                nonlocal calls
                calls+=1
                if calls==4:
                    raise OSError('simulated disk error')
                return original(a,b)
            with patch.object(sovia_audit.os,'link',side_effect=fail_fourth):
                with self.assertRaises(OSError):
                    write_reports_atomically([(p,'x') for p in names])
            self.assertTrue(all(not p.exists() for p in names))
            self.assertFalse(list(root.glob('.sovia-staging-*')))

    def test_no_csv_generated_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            proc=self._run(root)
            self.assertEqual(0,proc.returncode)
            self.assertFalse(list(root.glob('*.csv')))
