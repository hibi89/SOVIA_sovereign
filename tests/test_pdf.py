"""PDF is optional: core CLI must remain usable without third-party dependencies."""
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_audit import evaluate, read_document, write_reports_atomically
from sovia_pdf import _locate_korean_font, render_pdf
try:
    import reportlab
    HAVE_REPORTLAB=True
except ImportError:
    HAVE_REPORTLAB=False


class PDFOptionalTests(unittest.TestCase):
    def command(self, out, other=None, font=None, synthetic=None):
        cmd=[sys.executable,str(ROOT/'sovia_audit.py'), '--input',
             str(synthetic or ROOT/'examples/demo_five_rules.json'), '--output',str(out)]
        if other: cmd.extend(['--pdf-output',str(other)])
        if font: cmd.extend(['--pdf-font',str(font)])
        return subprocess.run(cmd,capture_output=True,text=True,timeout=30)

    def test_default_cli_does_not_need_reportlab(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/'report.html'
            with patch.dict(sys.modules,{'reportlab':None}):
                # PDF isn't requested here, and no imported module should require reportlab.
                from sovia_audit import render_html
                report=evaluate(read_document(ROOT/'examples/demo.json'))
                self.assertIn('SOVIA', render_html(report))
            proc=self.command(out)
            self.assertEqual(0,proc.returncode,proc.stderr)
            self.assertTrue(out.exists())

    def test_wrong_font_path_fails_without_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            proc=self.command(folder/'report.html',folder/'report.pdf',folder/'missing.ttf')
            self.assertEqual(2,proc.returncode)
            self.assertIn('PDF generation unavailable',proc.stderr)
            self.assertEqual([],list(folder.iterdir()))

    def test_pdf_output_can_not_be_input_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            source=ROOT/'examples/demo.json'
            proc=self.command(folder/'report.html',source)
            self.assertEqual(2,proc.returncode)
            self.assertFalse((folder/'report.html').exists())

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_cjk_font_resolved_on_test_machine(self):
        self.assertTrue(_locate_korean_font().is_file())

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_header_and_full_five_rules(self):
        report=evaluate(read_document(ROOT/'examples/demo_five_rules.json'))
        payload=render_pdf(report)
        self.assertTrue(payload.startswith(b'%PDF-'))
        self.assertIn(b'%%EOF',payload[-128:])
        self.assertGreater(len(payload),10000)

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_is_bitwise_deterministic_for_same_input(self):
        report=evaluate(read_document(ROOT/'examples/demo_five_rules.json'))
        self.assertEqual(render_pdf(report),render_pdf(report))

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_default_run_writes_both_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            pdf=folder/'result.pdf'
            proc=self.command(folder/'report.html',pdf)
            self.assertEqual(0,proc.returncode,proc.stderr)
            self.assertTrue(pdf.read_bytes().startswith(b'%PDF-'))
            self.assertIn('이벤트 타임라인',(folder/'report.html').read_text(encoding='utf-8'))

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_no_clobber_existing_pdf(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            pdf=folder/'report.pdf'
            pdf.write_bytes(b'KEEP_ORIGINAL_BYTES')
            proc=self.command(folder/'new.html',pdf)
            self.assertEqual(2,proc.returncode)
            self.assertEqual(b'KEEP_ORIGINAL_BYTES',pdf.read_bytes())
            self.assertFalse((folder/'new.html').exists())

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_failure_rollback_when_hardlink_blocked(self):
        import sovia_audit
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            html=folder/'first.html';pdf=folder/'second.pdf'
            calls=0
            real=sovia_audit.os.link
            def fail_second(src,target):
                nonlocal calls
                calls+=1
                if calls==2:
                    raise OSError('blocked hardlinks on PDF destination')
                return real(src,target)
            with patch.object(sovia_audit.os,'link',side_effect=fail_second):
                with self.assertRaises(OSError):
                    write_reports_atomically([(html,'valid HTML'),(pdf,render_pdf(evaluate(read_document(ROOT/'examples/demo.json'))))])
            self.assertFalse(html.exists())
            self.assertFalse(pdf.exists())
            self.assertEqual([],list(folder.glob('.sovia-staging-*')))

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_does_not_carry_unknown_prompt(self):
        document=json.loads((ROOT/'examples/demo.json').read_text(encoding='utf-8'))
        document['events'][0]['raw_prompt']='NON-PUBLIC-MESSAGE'
        report=evaluate(document)
        self.assertNotIn(b'NON-PUBLIC-MESSAGE',render_pdf(report))

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_safe_zero_findings_pdf_still_generated(self):
        document=json.loads((ROOT/'examples/demo.json').read_text(encoding='utf-8'))
        document['events']=document['events'][:1]
        report=evaluate(document)
        self.assertEqual(0,report['finding_count'])
        self.assertTrue(render_pdf(report).startswith(b'%PDF-'))

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_works_with_html_json_csv_all_flags(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            cmd=[sys.executable,str(ROOT/'sovia_audit.py'), '--input',str(ROOT/'examples/demo_five_rules.json'),
                 '--output',str(folder/'report.html'), '--json-output',str(folder/'report.json'),
                 '--findings-csv',str(folder/'findings.csv'), '--events-csv',str(folder/'events.csv'),
                 '--pdf-output',str(folder/'report.pdf')]
            p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
            self.assertEqual(0,p.returncode,p.stderr)
            self.assertEqual(5,len(list(folder.iterdir())))
            self.assertEqual(5,json.loads((folder/'report.json').read_text('utf-8'))['finding_count'])
            self.assertTrue((folder/'report.pdf').read_bytes().startswith(b'%PDF-'))

    @unittest.skipUnless(HAVE_REPORTLAB,'Optional reportlab dependency not installed')
    def test_pdf_runs_in_isolated_python_mode(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)
            cmd=[sys.executable,'-I','-B',str(ROOT/'sovia_audit.py'),
                 '--input',str(ROOT/'examples/demo_five_rules.json'),
                 '--output',str(folder/'report.html'),
                 '--pdf-output',str(folder/'report.pdf')]
            proc=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
            self.assertEqual(0,proc.returncode,proc.stderr)
            self.assertTrue((folder/'report.pdf').read_bytes().startswith(b'%PDF-'))
