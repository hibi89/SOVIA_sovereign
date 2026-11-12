"""P39 independent synthetic v0.14 delivery; existing 0.13 candidate intact."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_portable_la_delta as builder
import verify_portable_la_delta as verifier
from portable_smoke_la_delta import smoke


class LaDeltaPortableTests(unittest.TestCase):
    def test_versioned_reproducible_and_old_candidate_unchanged(self):
        self.assertEqual("0.14.0-la-delta-beta", verifier.VERSION)
        self.assertIn("sovia_la_review_delta.py", verifier.FILES)
        self.assertIn("RUN_LA_DELTA.cmd", verifier.FILES)
        self.assertEqual(18, len(verifier.FILES))
        self.assertEqual(builder.package_bytes(), builder.package_bytes())
        import build_portable_la_review as previous
        import verify_portable_la_review as old
        self.assertEqual("0.13.0-la-review-beta", old.VERSION)
        self.assertEqual(13, len(old.FILES))
        self.assertEqual(previous.package_bytes(), previous.package_bytes())
        self.assertNotEqual(verifier.PREFIX, old.PREFIX)

    def test_clean_extraction_actual_isolated_delta(self):
        result = smoke()
        self.assertEqual("SYNTHETIC_LA_DELTA_V014_CLEAN_INSTALL_PASS", result["status"])
        self.assertTrue(result["risk_increase_detected"])
        self.assertTrue(result["no_raw_source_export"])
        self.assertTrue(result["tamper_refusal"])
        self.assertFalse(result["real_la_integration_verified"])

    def test_transport_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / builder.DEFAULT_NAME
            first = builder.build(archive)
            self.assertEqual(18, first["files"])
            checksum = root / (archive.name + ".sha256")
            self.assertEqual("verified", verifier.verify_archive(archive, checksum)["status"])
            with self.assertRaises((builder.BuildError, verifier.PackageError)):
                builder.build(archive)
            candidate = root / "extra.zip"
            candidate.write_bytes(archive.read_bytes() + b"trailer")
            with self.assertRaises(verifier.PackageError):
                verifier.verify_archive(candidate, checksum)
            destination = root / "fresh"
            verifier.extract_verified(archive, destination, checksum)
            self.assertEqual("verified_directory",
                             verifier.verify_directory(destination)["status"])
            with self.assertRaises(verifier.PackageError):
                verifier.extract_verified(archive, destination, checksum)

    @unittest.skipUnless(os.name == "nt", "genuine Windows CMD required")
    def test_real_windows_cmd_synthetic_then_relaunch_refused(self):
        with tempfile.TemporaryDirectory(prefix="sovia-win-delta-") as tmp:
            root = Path(tmp)
            archive = root / builder.DEFAULT_NAME
            builder.build(archive)
            install = root / "installed"
            verifier.extract_verified(archive, install,
                                       root / (archive.name + ".sha256"))
            runner = install / "RUN_LA_DELTA.cmd"
            cmd = ["cmd.exe", "/d", "/c", str(runner), "--ci"]
            first = subprocess.run(cmd, cwd=root, capture_output=True,
                                   text=True, errors="replace", timeout=80)
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertIn("SOVIA DELTA SYNTHETIC COMPLETE", first.stdout)
            before = root / "SOVIA-LA-DELTA-before"
            after = root / "SOVIA-LA-DELTA-after"
            self.assertTrue((before / "review.html").is_file())
            self.assertTrue((after / "review.json").is_file())
            retry = subprocess.run(cmd, cwd=root, capture_output=True,
                                   text=True, errors="replace", timeout=80)
            self.assertEqual(2, retry.returncode, retry.stdout + retry.stderr)
            verifier.verify_directory(install)


if __name__ == "__main__":
    unittest.main()
