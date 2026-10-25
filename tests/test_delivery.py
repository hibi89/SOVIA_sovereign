import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

class DeliverySafetyTests(unittest.TestCase):
    """Protect user files; verify reproducible offline execution."""

    def _cli(self, src, out, extra=None):
        command = [sys.executable, str(ROOT / 'sovia_audit.py'), '--input', str(src), '--output', str(out)]
        if extra:
            command.extend(['--json-output', str(extra)])
        return subprocess.run(command, capture_output=True, text=True, timeout=15)

    def test_existing_html_not_overwritten(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / 'already.html'
            output.write_text('KEEP_ME', encoding='utf-8')
            proc = self._cli(ROOT / 'examples/demo.json', output)
            self.assertEqual(2, proc.returncode)
            self.assertEqual('KEEP_ME', output.read_text(encoding='utf-8'))
            self.assertFalse(list(Path(temp).glob('.sovia-staging-*')))

    def test_existing_json_cannot_leave_partial_html(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'fresh.html'
            existing = root / 'keep.json'
            existing.write_text('PRESERVED', encoding='utf-8')
            proc = self._cli(ROOT / 'examples/demo.json', output, existing)
            self.assertEqual(2, proc.returncode)
            self.assertFalse(output.exists())
            self.assertEqual('PRESERVED', existing.read_text(encoding='utf-8'))
            self.assertFalse(list(root.glob('.sovia-staging-*')))

    def test_atomic_publish_second_file_failure_rolls_back(self):
        from unittest.mock import patch
        import sovia_audit
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            one, two = root / 'one.html', root / 'two.json'
            original_link = sovia_audit.os.link
            calls = 0
            def fail_second(src, dest):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError('simulated second report filesystem failure')
                return original_link(src, dest)
            with patch.object(sovia_audit.os, 'link', side_effect=fail_second):
                with self.assertRaises(OSError):
                    sovia_audit.write_reports_atomically([(one, 'hello'), (two, 'world')])
            self.assertFalse(one.exists())
            self.assertFalse(two.exists())
            self.assertEqual([], list(root.glob('.sovia-staging-*')))

    def test_created_reports_private_and_complete(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            html_file, json_file = root / 'result.html', root / 'result.json'
            proc = self._cli(ROOT / 'examples/demo_five_rules.json', html_file, json_file)
            self.assertEqual(0, proc.returncode, proc.stderr)
            report = json.loads(json_file.read_text(encoding='utf-8'))
            self.assertEqual(5, report['finding_count'])
            self.assertIn('이벤트 타임라인', html_file.read_text(encoding='utf-8'))
            self.assertEqual([], list(root.glob('.sovia-staging-*')))

    def test_rerun_reports_are_not_clobbered(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'output.html'
            first = self._cli(ROOT / 'examples/demo.json', target)
            self.assertEqual(0, first.returncode)
            old = target.read_bytes()
            second = self._cli(ROOT / 'examples/demo_five_rules.json', target)
            self.assertEqual(2, second.returncode)
            self.assertEqual(old, target.read_bytes())

    def test_dangling_symlink_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / 'report.html'
            try:
                target.symlink_to(Path(temp) / 'missing.html')
            except (OSError, NotImplementedError):
                self.skipTest('Symlinks unavailable in this environment')
            proc = self._cli(ROOT / 'examples/demo.json', target)
            self.assertEqual(2, proc.returncode)
            self.assertTrue(target.is_symlink())

    def test_isolated_stdlib_clean_directory(self):
        import shutil
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'fixtures').mkdir()
            shutil.copyfile(ROOT / 'sovia_audit.py', root / 'sovia_audit.py')
            shutil.copyfile(ROOT / 'examples/demo_five_rules.json', root / 'fixtures/demo.json')
            html_file, json_file = root / 'demo.html', root / 'demo.json'
            proc = subprocess.run([sys.executable, '-I', '-B', str(root / 'sovia_audit.py'),
                                   '--input', str(root / 'fixtures/demo.json'),
                                   '--output', str(html_file), '--json-output', str(json_file)],
                                  cwd=root, capture_output=True, text=True, timeout=15)
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertEqual(5, json.loads(json_file.read_text(encoding='utf-8'))['finding_count'])

    def test_report_no_raw_prompt_in_export(self):
        from sovia_audit import evaluate, render_html
        data = json.loads((ROOT / 'examples/demo.json').read_text(encoding='utf-8'))
        data['events'][0]['raw_prompt'] = 'UNTRUSTED_PRIVATE_PAYLOAD'
        report = evaluate(data)
        self.assertNotIn('UNTRUSTED_PRIVATE_PAYLOAD', json.dumps(report))
        self.assertNotIn('UNTRUSTED_PRIVATE_PAYLOAD', render_html(report))

    def test_existing_files_not_modified_on_missing_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'not_here' / 'report.html'
            proc = self._cli(ROOT / 'examples/demo.json', path)
            self.assertEqual(2, proc.returncode)
            self.assertFalse(path.exists())

class OfflineReportContractTests(unittest.TestCase):
    def test_engine_works_with_socket_access_disabled(self):
        from unittest.mock import patch
        import socket
        from sovia_audit import read_document, evaluate, render_html
        with patch.object(socket, 'socket', side_effect=AssertionError('unexpected outbound socket')):
            report = evaluate(read_document(ROOT / 'examples/demo_five_rules.json'))
            self.assertEqual(5, report['finding_count'])
            self.assertIn('SOVIA Audit Lite', render_html(report))

    def test_html_has_both_expected_table_sections(self):
        from html.parser import HTMLParser
        from sovia_audit import evaluate, read_document, render_html
        class Counter(HTMLParser):
            def __init__(self):
                super().__init__()
                self.tables = 0
                self.rows = 0
            def handle_starttag(self, tag, attrs):
                if tag == 'table': self.tables += 1
                if tag == 'tr': self.rows += 1
        counter = Counter()
        counter.feed(render_html(evaluate(read_document(ROOT / 'examples/demo_five_rules.json'))))
        self.assertEqual(2, counter.tables)
        self.assertEqual(10, counter.rows)  # 2 headers + 5 findings + 3 events
