"""P42: v0.15 synthetic minimal portability, preserving v0.14 byte identity."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build_portable_la_minimal as builder
import verify_portable_la_minimal as verifier
from portable_smoke_la_minimal import smoke


class LaMinimalPortableTests(unittest.TestCase):
    def test_reproducibility_and_legacy_v014_unchanged(self):
        self.assertEqual("0.15.0-la-minimal-beta", verifier.VERSION)
        self.assertEqual(23, len(verifier.FILES))
        self.assertIn("sovia_la_minimal_projection.py", verifier.FILES)
        self.assertIn("RUN_LA_MINIMAL.cmd", verifier.FILES)
        self.assertEqual(builder.package_bytes(), builder.package_bytes())
        import build_portable_la_delta as older
        import verify_portable_la_delta as old_verify
        self.assertEqual("0.14.0-la-delta-beta", old_verify.VERSION)
        self.assertEqual(18, len(old_verify.FILES))
        self.assertEqual(older.package_bytes(), older.package_bytes())
        self.assertNotEqual(verifier.PREFIX, old_verify.PREFIX)

    def test_clean_extract_isolated_real_cli_tamper_and_repeat(self):
        result = smoke()
        self.assertEqual("SOVIA_V015_MINIMAL_PORTABLE_CLEAN_EXTRACT_PASS", result["status"])
        self.assertTrue(result["no_overwrite"])
        self.assertTrue(result["tamper_rejected"])
        self.assertFalse(result["real_la_execution_in_this_package"])

    def test_archive_strict_verifier_and_destination_no_overwrite(self):
        with TemporaryDirectory() as tmp:
            home = Path(tmp)
            archive = home / builder.DEFAULT_NAME
            receipt = builder.build(archive)
            self.assertEqual(23, receipt["files"])
            detached = home / (archive.name + ".sha256")
            self.assertEqual("verified", verifier.verify_archive(archive, detached)["status"])
            with self.assertRaises((builder.BuildError, verifier.PackageError)):
                builder.build(archive)
            extracted = home / "installed"
            verifier.extract_verified(archive, extracted, detached)
            self.assertEqual("verified_directory", verifier.verify_directory(extracted)["status"])
            with self.assertRaises(verifier.PackageError):
                verifier.extract_verified(archive, extracted, detached)

    @unittest.skipUnless(os.name == "nt", "actual Windows CMD required")
    def test_real_windows_cmd_synthetic_p40_and_no_overwrite(self):
        with TemporaryDirectory(prefix="sovia-minimal-win-") as tmp:
            home = Path(tmp)
            archive = home / builder.DEFAULT_NAME
            builder.build(archive)
            install = home / "installed"
            verifier.extract_verified(archive, install,
                                      home / (archive.name + ".sha256"))
            cmd = ["cmd.exe", "/d", "/c", str(install / "RUN_LA_MINIMAL.cmd"), "--ci"]
            first = subprocess.run(cmd, cwd=home, capture_output=True, text=True,
                                   errors="replace", timeout=85)
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            self.assertIn("SOVIA MINIMAL SYNTHETIC DEMO COMPLETE", first.stdout)
            demo = home / "SOVIA-LA-MINIMAL-DEMO"
            self.assertTrue((demo / "fabricated-la-like-projection.json").is_file())
            self.assertTrue((demo / "synthetic-review" / "review.html").is_file())
            again = subprocess.run(cmd, cwd=home, capture_output=True, text=True,
                                   errors="replace", timeout=85)
            self.assertEqual(2, again.returncode, again.stdout + again.stderr)
            verifier.verify_directory(install)


if __name__ == "__main__":
    unittest.main()
