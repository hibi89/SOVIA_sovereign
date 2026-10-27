"""Version-isolated P2 portable acceptance; no real customer inputs or releases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

import build_portable as legacy
import build_portable_p2 as build
import verify_portable as old_verify
import verify_portable_p2 as verify

ROOT = Path(__file__).resolve().parents[1]


class P2VersionedPortableTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="sovia-p2-bundle-test-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.zip = self.root / build.DEFAULT_NAME
        self.checksum = self.root / (build.DEFAULT_NAME + ".sha256")
        self.extracted = self.root / "new-install"

    def test_distinct_version_fixed_allowlist(self):
        self.assertEqual(build.DEFAULT_NAME, "SOVIA-Audit-Lite-0.11.2-beta.zip")
        self.assertEqual(verify.VERSION, "0.11.2-beta")
        self.assertEqual(verify.FORMAT, "SOVIA_PORTABLE_P2_V1")
        self.assertEqual(len(verify.FILES), 18)
        self.assertNotIn("owner_selfcheck.py", verify.FILES)
        self.assertIn("owner_p2_selfcheck.py", verify.FILES)
        self.assertIn("sovia_n8n_direct_audit.py", verify.FILES)
        self.assertIn("sovia_guarded_export.py", verify.FILES)
        self.assertIn("sovia_ephemeral_diagnostic.py", verify.FILES)
        self.assertNotEqual(set(verify.FILES), set(old_verify.FILES))

    def test_old_package_bytes_identical_to_independent_known_baseline(self):
        self.assertEqual(hashlib.sha256(legacy.package_bytes()).hexdigest(),
                         "68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9")

    def test_build_deterministic_and_strict_manifest(self):
        a, b = build.package_bytes(), build.package_bytes()
        self.assertEqual(a, b)
        self.assertEqual(build.build(self.zip)["sha256"], hashlib.sha256(a).hexdigest())
        self.assertEqual(verify.verify_archive(self.zip, self.checksum)["files"], 18)
        with zipfile.ZipFile(self.zip) as bundle:
            self.assertEqual(set(bundle.namelist()),
                             {verify.PREFIX + p for p in verify.FILES} |
                             {verify.PREFIX + verify.MANIFEST})
            self.assertNotIn("client_logs", "".join(bundle.namelist()).lower())
            self.assertNotIn("private/", "".join(bundle.namelist()).lower())
            manifest = json.loads(bundle.read(verify.PREFIX + verify.MANIFEST))
            self.assertEqual(manifest["version"], "0.11.2-beta")

    def test_rejects_v010_verifier_and_old_archive_name(self):
        self.assertNotEqual(build.DEFAULT_NAME, legacy.DEFAULT_NAME)
        with self.assertRaises(build.BuildError):
            build.build(self.root / legacy.DEFAULT_NAME)
        self.assertFalse(self.zip.exists())

    def test_existing_artifacts_no_clobber(self):
        self.zip.write_bytes(b"ORIGINAL_DO_NOT_OVERWRITE")
        with self.assertRaises(build.BuildError):
            build.build(self.zip)
        self.assertEqual(self.zip.read_bytes(), b"ORIGINAL_DO_NOT_OVERWRITE")
        self.assertFalse(self.checksum.exists())

    def test_verify_tamper_detects_before_extract(self):
        build.build(self.zip)
        self.zip.write_bytes(self.zip.read_bytes() + b"CHANGED")
        with self.assertRaises(verify.PackageError):
            verify.extract_verified(self.zip, self.extracted, self.checksum)
        self.assertFalse(self.extracted.exists())

    def test_verify_strict_fresh_install_and_no_overwrite(self):
        build.build(self.zip)
        result = verify.extract_verified(self.zip, self.extracted, self.checksum)
        self.assertEqual(result["files"], 18)
        self.assertEqual(verify.verify_directory(self.extracted)["files"], 18)
        with self.assertRaises(verify.PackageError):
            verify.extract_verified(self.zip, self.extracted, self.checksum)

    def test_extracted_direct_and_aggregate_clis_isolated(self):
        build.build(self.zip)
        verify.extract_verified(self.zip, self.extracted, self.checksum)
        direct = subprocess.run([
            sys.executable, "-I", "-B", str(self.extracted / "sovia_n8n_direct_audit.py"),
            "--input", str(self.extracted / "examples" / "demo_n8n_sanitized.json"),
            "--policy", str(self.extracted / "examples" / "demo_policy.json"),
            "--html-output", str(self.root / "report.html"),
            "--json-output", str(self.root / "report.json"),
            "--synthetic-only", "--local-test-budget-bytes", "1048576",
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(direct.returncode, 0, direct.stderr)
        self.assertEqual((json.loads((self.root / "report.json").read_text(encoding="utf-8"))["event_count"],
                          json.loads(direct.stdout)["findings"]), (3, 5))
        aggregate = subprocess.run([
            sys.executable, "-I", "-B", str(self.extracted / "sovia_ephemeral_diagnostic.py"),
            "--input", str(self.extracted / "examples" / "demo_five_rules.json"),
            "--ack-sanitized-source"
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(aggregate.returncode, 0, aggregate.stderr)
        self.assertEqual(json.loads(aggregate.stdout)["findings"], 5)
        self.assertFalse(json.loads(aggregate.stdout)["application_output_files_created"])
        self.assertEqual(verify.verify_directory(self.extracted)["status"], "verified_directory")

    def test_real_p2_selfcheck_manual_gates_still_pending(self):
        build.build(self.zip)
        verify.extract_verified(self.zip, self.extracted, self.checksum)
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            cmd = subprocess.run([
                sys.executable, "-I", "-B", str(self.extracted / "owner_p2_selfcheck.py"),
                "--output-dir", str(self.root / "results"),
            ], capture_output=True, text=True, timeout=90)
        self.assertEqual(cmd.returncode, 0, cmd.stderr)
        files = list((self.root / "results").glob("SOVIA_SELF_CHECK_*/SELF_CHECK_RESULT.json"))
        self.assertEqual(len(files), 1)
        report = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(report["status"], "AUTOMATED_PASS_MANUAL_PENDING")
        self.assertEqual(report["checks"]["direct_sanitized"], "PASS")
        self.assertEqual(report["checks"]["direct_metadata_pattern_scan"], "PASS")
        self.assertEqual(report["checks"]["aggregate_no_report"], "PASS")
        self.assertTrue(all(value == "NOT_CHECKED"
                            for value in report["manual_acceptance"].values()))
        self.assertEqual(verify.verify_directory(self.extracted)["files"], 18)

    def test_isolated_full_p2_zip_smoke(self):
        from portable_smoke_p2 import smoke
        result = smoke()
        self.assertEqual(result["status"], "p2_portable_clean_install_pass")
        self.assertEqual(result["release_files"], 18)
        self.assertTrue(result["database_restored"])


    def test_replaced_zip_after_validation_never_extracted(self):
        # Previously the extractor verified one on-disk archive, then opened it
        # afresh. Replacing its bytes in between could bypass prior validation.
        build.build(self.zip)
        real_verify = verify.verify_archive
        def replace_after_check(archive_path, checksum_path=None):
            checked = real_verify(archive_path, checksum_path)
            self.zip.write_bytes(self.zip.read_bytes() + b"REPLACED_POST_CHECK")
            return checked
        with patch.object(verify, "verify_archive", side_effect=replace_after_check):
            with self.assertRaisesRegex(verify.PackageError, "Archive changed after verification"):
                verify.extract_verified(self.zip, self.extracted, self.checksum)
        self.assertFalse(self.extracted.exists())

    def test_tampered_install_selfcheck_creates_no_diagnostics(self):
        build.build(self.zip)
        verify.extract_verified(self.zip, self.extracted, self.checksum)
        altered = self.extracted / "P2_PORTABLE_README.md"
        altered.write_bytes(altered.read_bytes() + b"\nTAMPERED")
        diagnostics = self.root / "no-diagnostics"
        check = subprocess.run([
            sys.executable, "-I", "-B", str(self.extracted / "owner_p2_selfcheck.py"),
            "--output-dir", str(diagnostics)
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(check.returncode, 2)
        self.assertFalse(diagnostics.exists())
        self.assertNotIn(str(self.extracted), check.stderr)

    def test_selfcheck_rejects_results_in_install_before_mutation(self):
        build.build(self.zip)
        verify.extract_verified(self.zip, self.extracted, self.checksum)
        check = subprocess.run([
            sys.executable, "-I", "-B", str(self.extracted / "owner_p2_selfcheck.py"),
            "--output-dir", str(self.extracted / "BAD_OUTPUTS")
        ], capture_output=True, text=True, timeout=30)
        self.assertEqual(check.returncode, 2)
        self.assertIn("RESULTS_INSIDE_VERIFIED_INSTALL", check.stderr)
        self.assertFalse((self.extracted / "BAD_OUTPUTS").exists())
        self.assertEqual(verify.verify_directory(self.extracted)["files"], 18)

    def test_existing_outer_results_parent_keeps_install_pristine(self):
        build.build(self.zip)
        verify.extract_verified(self.zip, self.extracted, self.checksum)
        output_parent = self.root / "reports"
        check = subprocess.run([
            sys.executable, "-I", "-B", str(self.extracted / "owner_p2_selfcheck.py"),
            "--output-dir", str(output_parent)
        ], capture_output=True, text=True, timeout=60)
        self.assertEqual(check.returncode, 0, check.stderr)
        self.assertEqual(len(list(output_parent.glob("SOVIA_SELF_CHECK_*/SELF_CHECK_RESULT.json"))), 1)
        self.assertEqual(verify.verify_directory(self.extracted)["status"], "verified_directory")


if __name__ == "__main__":
    unittest.main()
