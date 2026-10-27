"""Single-command v0.12 MVP regression: real offline engine/report/ledger path."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_mvp_v012 as mvp
import sovia_history_v012 as history

GOLDEN = ROOT / "examples" / "demo_five_rules.json"
BOUNDARY = ROOT / "examples" / "demo_temporal_boundary.json"


class MVPV012Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="sovia-mvp-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "fresh-output"

    def test_one_command_outputs_reports_and_metadata_ledger(self):
        result = mvp.run(GOLDEN, self.target, synthetic_only=True)
        self.assertEqual("SYNTHETIC_V012_MVP_COMPLETE", result["status"])
        self.assertEqual((3, 5), (result["events"], result["findings"]))
        self.assertEqual(set(mvp.OUTPUTS), {p.name for p in self.target.iterdir()})
        report = json.loads((self.target / "report.json").read_text("utf-8"))
        self.assertEqual(5, report["finding_count"])
        self.assertEqual("0.12.0-preview", report["engine_version"])
        self.assertIn("<html", (self.target / "report.html").read_text("utf-8"))
        status = history.status(self.target / "history.sqlite3")
        self.assertEqual((2, 1, 5), (status["schema_version"],
                                    status["reports"], status["finding_count_total"]))
        self.assertEqual(GOLDEN.read_bytes(), GOLDEN.read_bytes())

    def test_boundary_uses_corrected_utc_engine(self):
        result = mvp.run(BOUNDARY, self.target, synthetic_only=True)
        self.assertEqual((3, 0), (result["events"], result["findings"]))
        self.assertEqual(0, history.status(self.target / "history.sqlite3")["finding_count_total"])

    def test_acknowledgement_required_without_creating_outputs(self):
        with self.assertRaisesRegex(mvp.MVPError, "SYNTHETIC_ACK_REQUIRED"):
            mvp.run(GOLDEN, self.target)
        self.assertFalse(self.target.exists())

    def test_existing_destination_preserved_and_not_reused(self):
        self.target.mkdir()
        (self.target / "owner-file").write_bytes(b"DO_NOT_REPLACE")
        with self.assertRaisesRegex(mvp.MVPError, "OUTPUT_EXISTS"):
            mvp.run(GOLDEN, self.target, synthetic_only=True)
        self.assertEqual(b"DO_NOT_REPLACE", (self.target / "owner-file").read_bytes())

    def test_recognizable_pii_rejected_with_no_published_folder(self):
        document = json.loads(GOLDEN.read_text("utf-8"))
        document["events"][0]["agent_id"] = "private@example.com"
        forbidden = self.root / "secret-fixture.json"
        forbidden.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(mvp.MVPError, "MVP_INPUT_OR_OUTPUT_REJECTED"):
            mvp.run(forbidden, self.target, synthetic_only=True)
        self.assertFalse(self.target.exists())

    def test_isolated_python_cli_no_cwd_import_dependencies(self):
        proc = subprocess.run([
            sys.executable, "-I", "-B", str(ROOT / "sovia_mvp_v012.py"),
            "--input", str(GOLDEN), "--output-dir", str(self.target),
            "--synthetic-only",
        ], capture_output=True, text=True, cwd=self.root, timeout=45)
        self.assertEqual(0, proc.returncode, proc.stderr)
        summary = json.loads(proc.stdout)
        self.assertEqual("SYNTHETIC_V012_MVP_COMPLETE", summary["status"])
        self.assertEqual(3, len(list(self.target.iterdir())))
        self.assertNotIn(str(GOLDEN), proc.stdout)


if __name__ == "__main__":
    unittest.main()
