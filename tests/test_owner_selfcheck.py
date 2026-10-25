"""Owner self-check: unpacked clean-app tests without personal data or services."""
from contextlib import redirect_stdout
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_portable
import verify_portable
import owner_selfcheck


class OwnerSelfCheckTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.temp = Path(t.name)
        self.zip = self.temp / build_portable.DEFAULT_NAME
        self.install = self.temp / "SOVIA-install"

    def installed(self):
        build_portable.build(self.zip)
        verify_portable.extract_verified(self.zip, self.install)
        return self.install

    def run_owner(self, extra=(), *, py_args=None):
        cmd = [sys.executable, "-I", "-B", str(self.install / "owner_selfcheck.py"),
               "--output-dir", str(self.temp / "results"), *extra]
        if py_args is not None:
            cmd = py_args
        return subprocess.run(cmd, capture_output=True, text=True,
                              timeout=70, check=False)

    def result_files(self):
        return list((self.temp / "results").glob("SOVIA_SELF_CHECK_*/SELF_CHECK_RESULT.json"))

    def test_synthetic_owner_pass_has_manual_pending_and_files(self):
        self.installed()
        result = self.run_owner()
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("AUTOMATED_PASS_MANUAL_PENDING", result.stdout)
        files = self.result_files()
        self.assertEqual(1, len(files))
        report = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual("SYNTHETIC_ONLY_NO_CUSTOMER_DATA", report["purpose"])
        self.assertEqual((3, 5, 1), (report["synthetic"]["events"],
                                    report["synthetic"]["findings"],
                                    report["synthetic"]["reports"]))
        for name in ("python", "package_integrity", "audit", "sqlite",
                     "dashboard", "recovery"):
            self.assertEqual("PASS", report["checks"][name])
        self.assertTrue(report["checks"]["optional_pdf"].startswith(
            ("SKIPPED_", "GENERATED_", "FAILED_OPTIONAL_")))
        self.assertEqual({"NOT_CHECKED"}, set(report["manual_acceptance"].values()))
        self.assertIsNone(report["error_code"])
        for name in ("synthetic-audit.html", "synthetic-audit.json",
                     "synthetic-history.sqlite", "synthetic-dashboard.html",
                     "synthetic-backup.sqlite", "synthetic-restored.sqlite"):
            self.assertTrue((files[0].parent / name).is_file(), name)
        verify_portable.verify_directory(self.install)

    def test_result_json_is_sanitized_not_a_host_path_dump(self):
        self.installed()
        self.assertEqual(0, self.run_owner().returncode)
        data = self.result_files()[0].read_text(encoding="utf-8")
        for forbidden in ("demo-agent", "unauthorized_export", "client_records",
                          "outside.example", "synthetic:1", str(self.temp)):
            self.assertNotIn(forbidden, data)

    def test_second_run_never_overwrites_previous(self):
        self.installed()
        self.assertEqual(0, self.run_owner().returncode)
        old = self.result_files()[0]
        digest = hashlib.sha256(old.read_bytes()).hexdigest()
        self.assertEqual(0, self.run_owner().returncode)
        self.assertEqual(2, len(self.result_files()))
        self.assertEqual(digest, hashlib.sha256(old.read_bytes()).hexdigest())

    def test_tampered_extracted_script_fails_closed(self):
        self.installed()
        target = self.install / "sovia_audit.py"
        target.write_bytes(target.read_bytes() + b"\n# TAMPER")
        result = self.run_owner()
        self.assertEqual(2, result.returncode)
        reports = self.result_files()
        self.assertEqual(1, len(reports))
        report = json.loads(reports[0].read_text(encoding="utf-8"))
        self.assertEqual("AUTOMATED_FAILED", report["status"])
        self.assertEqual({}, report["synthetic"])
        self.assertEqual({}, report["checks"])
        self.assertFalse((reports[0].parent / "synthetic-audit.html").exists())

    def test_missing_portable_manifest_fails_before_running_app(self):
        self.installed()
        (self.install / "MANIFEST.json").unlink()
        result = self.run_owner()
        self.assertEqual(2, result.returncode)
        record = json.loads(self.result_files()[0].read_text(encoding="utf-8"))
        self.assertEqual("AUTOMATED_FAILED", record["status"])
        self.assertNotIn("audit", record["checks"])

    def test_invalid_target_parent_cannot_create_nested_paths(self):
        self.installed()
        target = self.temp / "absent" / "nested" / "results"
        result = self.run_owner(extra=("--output-dir", str(target)))
        self.assertEqual(2, result.returncode)
        self.assertFalse((self.temp / "absent").exists())

    def test_output_symlink_not_followed(self):
        self.installed()
        private = self.temp / "private"
        private.mkdir()
        link = self.temp / "results"
        try:
            link.symlink_to(private, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink privilege unavailable")
        result = self.run_owner()
        self.assertEqual(2, result.returncode)
        self.assertEqual([], list(private.iterdir()))

    def test_optional_pdf_unavailable_is_explicitly_skipped(self):
        checks = {}
        with patch.object(owner_selfcheck, "find_spec", return_value=None):
            owner_selfcheck._optional_pdf(ROOT, ROOT / "examples/demo_five_rules.json",
                                          self.temp, checks)
        self.assertEqual("SKIPPED_REPORTLAB_MISSING", checks["optional_pdf"])
        self.assertFalse((self.temp / "synthetic-audit.pdf").exists())

    def test_optional_pdf_font_unavailable_is_explicitly_skipped(self):
        checks = {}
        with patch.object(owner_selfcheck, "find_spec", return_value=object()), patch.object(
            owner_selfcheck, "_local", return_value=type("Fake", (), {
                "_locate_korean_font": staticmethod(
                    lambda: (_ for _ in ()).throw(ValueError("missing font")))
            })()
        ):
            owner_selfcheck._optional_pdf(ROOT, ROOT / "examples/demo_five_rules.json",
                                          self.temp, checks)
        self.assertEqual("SKIPPED_KOREAN_TTF_MISSING", checks["optional_pdf"])

    def test_old_python_gate_explicit(self):
        self.installed()
        with patch.object(owner_selfcheck.sys, "version_info", (3, 10, 0)):
            # This imported code lives in the repo tree without MANIFEST.json.
            # A version error must occur before manifest access.
            report, folder = owner_selfcheck.check(self.temp / "owner-old-python")
        self.assertEqual("AUTOMATED_FAILED", report["status"])
        self.assertEqual("PYTHON_3_11_REQUIRED", report["error_code"])
        self.assertTrue((folder / "SELF_CHECK_RESULT.json").exists())

    def test_launcher_contains_no_hidden_network_or_install_commands(self):
        self.installed()
        cmd = (self.install / "RUN_SELF_CHECK.cmd").read_text(encoding="utf-8")
        self.assertIn("--output-dir", cmd)
        self.assertIn("owner_selfcheck.py", cmd)
        self.assertIn("SOVIA_NO_PAUSE", cmd)
        for forbidden in ("powershell -enc", "curl ", "wget ", "pip install",
                          "start http", "reg add", "set-executionpolicy"):
            self.assertNotIn(forbidden, cmd.lower())

    @unittest.skipUnless(os.name == "nt", "Windows .cmd cannot run on this OS")
    def test_real_windows_double_click_launcher_noninteractive_ci(self):
        self.installed()
        env = dict(os.environ)
        env["SOVIA_NO_PAUSE"] = "1"
        proc = subprocess.run(["cmd", "/d", "/c", str(self.install / "RUN_SELF_CHECK.cmd")],
                              cwd=self.temp, env=env, capture_output=True,
                              text=True, timeout=80, check=False)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        reports = list((self.temp / "SOVIA_DIAGNOSTICS").glob(
            "SOVIA_SELF_CHECK_*/SELF_CHECK_RESULT.json"))
        self.assertEqual(1, len(reports))
        self.assertEqual("AUTOMATED_PASS_MANUAL_PENDING",
                         json.loads(reports[0].read_text(encoding="utf-8"))["status"])


if __name__ == "__main__":
    unittest.main()
