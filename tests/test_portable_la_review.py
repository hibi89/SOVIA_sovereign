"""Independent isolated LA beta distribution regression (synthetic only)."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))

import build_portable_la_review as builder
import verify_portable_la_review as verifier
from portable_smoke_la_review import smoke


class ReviewPortableTests(unittest.TestCase):
    def test_reproducible_separate_manifest_and_old_version_independent(self):
        a = builder.package_bytes()
        b = builder.package_bytes()
        self.assertEqual(a, b)
        self.assertEqual("0.13.0-la-review-beta", verifier.VERSION)
        self.assertEqual("SOVIA-LA-REVIEW/", verifier.PREFIX)
        self.assertIn(b"SOVIA_PORTABLE_LA_REVIEW_V1", a)
        import verify_portable_v012 as old
        self.assertEqual("0.12.0-beta", old.VERSION)
        self.assertNotEqual(tuple(verifier.FILES), tuple(old.FILES))

    def test_extracted_isolated_end_to_end(self):
        result = smoke()
        self.assertEqual("SYNTHETIC_LA_REVIEW_PORTABLE_CLEAN_INSTALL_PASS",
                         result["status"])
        self.assertTrue(result["no_raw_source_export"])
        self.assertTrue(result["tamper_rejected"])
        self.assertFalse(result["real_la_integration_verified"])

    def test_zip_payload_tamper_and_no_overwrite_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive = root / builder.DEFAULT_NAME
            builder.build(archive)
            checksum = archive.with_name(archive.name + ".sha256")
            verifier.verify_archive(archive, checksum)
            with self.assertRaises((verifier.PackageError, builder.BuildError)):
                builder.build(archive)
            bad = root / "bad.zip"
            bad.write_bytes(archive.read_bytes() + b"spoofed")
            with self.assertRaises(verifier.PackageError):
                verifier.verify_archive(bad, checksum)
            install = root / "installed"
            verifier.extract_verified(archive, install, checksum)
            with self.assertRaises(verifier.PackageError):
                verifier.extract_verified(archive, install, checksum)

    @unittest.skipUnless(os.name == "nt", "Windows cmd.exe owner path")
    def test_packaged_windows_runner_no_overwrite_and_tamper_refusal(self):
        with tempfile.TemporaryDirectory(prefix="sovia-la-review-windows-") as tmp:
            root = Path(tmp)
            archive = root / builder.DEFAULT_NAME
            builder.build(archive)
            extract = root / "sovia-la-demo"
            verifier.extract_verified(
                archive, extract, archive.with_name(archive.name + ".sha256"))
            runner = extract / "RUN_LA_REVIEW.cmd"
            first = subprocess.run(["cmd.exe", "/d", "/c", str(runner), "--ci"],
                                   cwd=root, capture_output=True, text=True, timeout=50)
            self.assertEqual(0, first.returncode, first.stdout + first.stderr)
            out = root / "SOVIA-LA-synthetic-review"
            self.assertEqual("SYNTHETIC_BUNDLE_CONSISTENT_NOT_AUTHENTICATED",
                             __import__("sovia_la_owner_review").verify_bundle(out)["status"])
            repeat = subprocess.run(["cmd.exe", "/d", "/c", str(runner), "--ci"],
                                    cwd=root, capture_output=True, text=True, timeout=50)
            self.assertEqual(2, repeat.returncode)
            second = root / "sovia-la-damaged"
            verifier.extract_verified(archive, second, archive.with_name(archive.name + ".sha256"))
            (second / "sovia_la_plan_reconcile.py").write_text("bad", encoding="utf-8")
            rejected = subprocess.run(["cmd.exe", "/d", "/c",
                                       str(second / "RUN_LA_REVIEW.cmd"), "--ci"],
                                      cwd=root, capture_output=True, text=True, timeout=50)
            self.assertEqual(2, rejected.returncode)
            self.assertFalse((root / "SOVIA-LA-synthetic-review-new").exists())


if __name__ == "__main__":
    unittest.main()
