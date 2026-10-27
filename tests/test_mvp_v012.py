"""Single-command v0.12 MVP regression: real offline engine/report/ledger path."""
from __future__ import annotations
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_mvp_v012 as mvp
import sovia_history_v012 as history
import sovia_audit_v012 as engine
import sovia_audit as core_audit

GOLDEN = ROOT / "examples" / "demo_five_rules.json"
BOUNDARY = ROOT / "examples" / "demo_temporal_boundary.json"
N8N = ROOT / "examples" / "demo_n8n_sanitized.json"
POLICY = ROOT / "examples" / "demo_policy.json"


class MVPV012Tests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="sovia-mvp-test-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.target = self.root / "fresh-output"

    def test_one_command_outputs_reports_and_metadata_ledger(self):
        pristine_source = GOLDEN.read_bytes()
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
        self.assertEqual(pristine_source, GOLDEN.read_bytes())

    def test_result_is_marked_incomplete_until_all_outputs_publish(self):
        original_link = os.link
        observed = []

        def inspecting_link(src, dst, *args, **kwargs):
            # The audit renderer uses os.link inside its staging folder too.
            # Only inspect the MVP's final publish destination.
            if Path(dst).parent == self.target:
                self.assertTrue((self.target / mvp.INCOMPLETE_MARKER).is_file())
                observed.append(Path(dst).name)
            return original_link(src, dst, *args, **kwargs)

        with patch("sovia_mvp_v012.os.link", side_effect=inspecting_link):
            result = mvp.run(GOLDEN, self.target, synthetic_only=True)
        self.assertEqual("SYNTHETIC_V012_MVP_COMPLETE", result["status"])
        self.assertEqual(list(mvp.OUTPUTS), observed)
        self.assertFalse((self.target / mvp.INCOMPLETE_MARKER).exists())
        self.assertEqual(set(mvp.OUTPUTS), {p.name for p in self.target.iterdir()})

    def test_publication_fault_rolls_back_outputs_and_marker(self):
        original_link = os.link

        def failing_second_link(src, dst, *args, **kwargs):
            if Path(dst).parent == self.target and Path(dst).name == "report.json":
                self.assertTrue((self.target / mvp.INCOMPLETE_MARKER).exists())
                self.assertTrue((self.target / "report.html").exists())
                raise OSError("synthetic fault after first link")
            return original_link(src, dst, *args, **kwargs)

        with patch("sovia_mvp_v012.os.link", side_effect=failing_second_link):
            with self.assertRaisesRegex(
                mvp.MVPError, "MVP_INPUT_OR_OUTPUT_REJECTED"
            ):
                mvp.run(GOLDEN, self.target, synthetic_only=True)
        self.assertFalse(self.target.exists())

    def test_nonstandard_interruption_leaves_explicit_incomplete_marker(self):
        original_link = os.link

        def interrupted_link(src, dst, *args, **kwargs):
            if Path(dst).parent == self.target and Path(dst).name == "report.json":
                raise KeyboardInterrupt()
            return original_link(src, dst, *args, **kwargs)

        with patch("sovia_mvp_v012.os.link", side_effect=interrupted_link):
            with self.assertRaises(KeyboardInterrupt):
                mvp.run(GOLDEN, self.target, synthetic_only=True)
        self.assertTrue((self.target / mvp.INCOMPLETE_MARKER).is_file())
        self.assertTrue((self.target / "report.html").is_file())
        self.assertFalse((self.target / "report.json").exists())
        self.assertFalse((self.target / "history.sqlite3").exists())

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

    def test_n8n_synthetic_one_command_outputs_no_canonical_export(self):
        previous = (N8N.read_bytes(), POLICY.read_bytes())
        result = mvp.run(N8N, self.target, synthetic_only=True,
                         source_format="n8n-sanitized", policy_path=POLICY)
        self.assertEqual("n8n-sanitized", result["source_format"])
        self.assertEqual("SYNTHETIC_V012_MVP_COMPLETE", result["status"])
        self.assertEqual((3, 5), (result["events"], result["findings"]))
        self.assertEqual(set(mvp.OUTPUTS), {p.name for p in self.target.iterdir()})
        self.assertEqual(previous, (N8N.read_bytes(), POLICY.read_bytes()))
        report = json.loads((self.target / "report.json").read_text("utf-8"))
        self.assertEqual("0.12.0-preview", report["engine_version"])
        self.assertEqual(5, report["finding_count"])
        status = history.status(self.target / "history.sqlite3")
        self.assertEqual((1, 5), (status["reports"], status["finding_count_total"]))
        self.assertFalse(result["real_n8n_verified"])
        self.assertFalse(result["customer_release_approved"])

    def test_n8n_never_writes_intermediate_canonical_even_in_staging(self):
        # Old implementation published _temporary_canonical.json under a
        # temporary folder. Track every hardlink destination, not just final
        # output files, to prove the new pipeline never materializes it.
        destinations = []
        original_link = os.link

        def recorded_link(source, destination, *args, **kwargs):
            destinations.append(Path(destination).name)
            return original_link(source, destination, *args, **kwargs)

        with patch("sovia_mvp_v012.os.link", side_effect=recorded_link):
            result = mvp.run(
                N8N, self.target, synthetic_only=True,
                source_format="n8n-sanitized", policy_path=POLICY
            )
        self.assertEqual((3, 5), (result["events"], result["findings"]))
        self.assertEqual(set(mvp.OUTPUTS), set(destinations))
        self.assertNotIn("_temporary_canonical.json", destinations)

    def test_in_memory_evaluation_matches_file_based_engine_findings(self):
        document = core_audit.read_document(GOLDEN)
        memory_root = self.root / "memory"
        memory_root.mkdir()
        file_root = self.root / "file"
        file_root.mkdir()
        in_memory = engine.write_synthetic_document(
            document, memory_root / "report.html", memory_root / "report.json",
            legacy_audit=core_audit
        )
        via_file = engine.run_synthetic(
            GOLDEN, file_root / "report.html", file_root / "report.json"
        )
        self.assertEqual(in_memory["events"], via_file["events"])
        self.assertEqual(in_memory["findings"], via_file["findings"])
        memory_report = json.loads((memory_root / "report.json").read_text("utf-8"))
        file_report = json.loads((file_root / "report.json").read_text("utf-8"))
        self.assertEqual(memory_report, file_report)
        self.assertEqual(3, memory_report["event_count"])
        self.assertEqual(5, memory_report["finding_count"])
        self.assertEqual(
            (memory_root / "report.html").read_bytes(),
            (file_root / "report.html").read_bytes()
        )
        self.assertFalse((memory_root / "_temporary_canonical.json").exists())

    def test_in_memory_history_matches_path_based_result_and_no_raw_content(self):
        document = core_audit.read_document(GOLDEN)
        memory_db = self.root / "memory.sqlite3"
        result = history.import_synthetic_document(
            memory_db, document, legacy_audit=core_audit
        )
        self.assertEqual("imported", result["status"])
        self.assertEqual(
            "already_present",
            history.import_synthetic(memory_db, GOLDEN)["status"]
        )
        self.assertEqual((1, 3, 5), (
            history.status(memory_db)["reports"],
            history.status(memory_db)["event_count_total"],
            history.status(memory_db)["finding_count_total"],
        ))
        self.assertNotIn(b"client_records", memory_db.read_bytes())

    def test_in_memory_history_refuses_recognizable_private_metadata(self):
        document = core_audit.read_document(GOLDEN)
        document["events"][0]["agent_id"] = "user@example.com"
        db = self.root / "denied.sqlite3"
        with self.assertRaises(ValueError):
            history.import_synthetic_document(db, document)
        self.assertFalse(db.exists())

    def test_n8n_rejects_missing_policy_without_publishing(self):
        with self.assertRaisesRegex(mvp.MVPError, "POLICY_REQUIRED_ONLY_FOR_N8N"):
            mvp.run(N8N, self.target, synthetic_only=True,
                    source_format="n8n-sanitized")
        self.assertFalse(self.target.exists())

    def test_canonical_rejects_unexpected_policy_without_publishing(self):
        with self.assertRaisesRegex(mvp.MVPError, "POLICY_REQUIRED_ONLY_FOR_N8N"):
            mvp.run(GOLDEN, self.target, synthetic_only=True, policy_path=POLICY)
        self.assertFalse(self.target.exists())

    def test_n8n_rejects_raw_node_parameters_without_publishing(self):
        document = json.loads(N8N.read_text("utf-8"))
        document["steps"][0]["parameters"] = {"secret": "SHOULD_NOT_ACCEPT"}
        bad = self.root / "raw-node.json"
        bad.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(mvp.MVPError, "MVP_INPUT_OR_OUTPUT_REJECTED"):
            mvp.run(bad, self.target, synthetic_only=True,
                    source_format="n8n-sanitized", policy_path=POLICY)
        self.assertFalse(self.target.exists())

    def test_n8n_rejects_pii_before_materializing_report(self):
        document = json.loads(N8N.read_text("utf-8"))
        document["steps"][0]["evidence_ref"] = "person@example.com"
        bad = self.root / "pii-node.json"
        bad.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(mvp.MVPError, "MVP_INPUT_OR_OUTPUT_REJECTED"):
            mvp.run(bad, self.target, synthetic_only=True,
                    source_format="n8n-sanitized", policy_path=POLICY)
        self.assertFalse(self.target.exists())

    def test_n8n_source_policy_same_file_and_existing_output_refused(self):
        with self.assertRaisesRegex(mvp.MVPError, "SOURCE_POLICY_COLLISION"):
            mvp.run(N8N, self.target, synthetic_only=True,
                    source_format="n8n-sanitized", policy_path=N8N)
        self.assertFalse(self.target.exists())
        self.target.mkdir()
        (self.target / "sentinel").write_bytes(b"PRESERVE")
        with self.assertRaisesRegex(mvp.MVPError, "OUTPUT_EXISTS"):
            mvp.run(N8N, self.target, synthetic_only=True,
                    source_format="n8n-sanitized", policy_path=POLICY)
        self.assertEqual(b"PRESERVE", (self.target / "sentinel").read_bytes())

    def test_n8n_isolated_python_cli(self):
        proc = subprocess.run([
            sys.executable, "-I", "-B", str(ROOT / "sovia_mvp_v012.py"),
            "--source-format", "n8n-sanitized",
            "--input", str(N8N), "--policy", str(POLICY),
            "--output-dir", str(self.target), "--synthetic-only",
        ], capture_output=True, text=True, cwd=self.root, timeout=45)
        self.assertEqual(0, proc.returncode, proc.stderr)
        summary = json.loads(proc.stdout)
        self.assertEqual("n8n-sanitized", summary["source_format"])
        self.assertEqual((3, 5), (summary["events"], summary["findings"]))
        self.assertEqual(set(mvp.OUTPUTS), {p.name for p in self.target.iterdir()})
        self.assertNotIn(str(N8N), proc.stdout)

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
