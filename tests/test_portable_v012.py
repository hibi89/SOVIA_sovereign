"""Strictly distinct synthetic v0.12 portable archive checks."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import build_portable_v012 as build
import verify_portable_v012 as verify
import build_portable_p2 as old_build
import verify_portable_p2 as old_verify

class V012PortableTests(unittest.TestCase):
    def setUp(self):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root=Path(tmp.name)
        self.zip=self.root/build.DEFAULT_NAME
        self.sha=self.root/(build.DEFAULT_NAME+".sha256")
        self.install=self.root/"install"

    def create(self):
        return build.build(self.zip)

    def test_fourteen_files_manifest_prefix_and_deterministic_bytes(self):
        a=build.package_bytes()
        self.assertEqual(a,build.package_bytes())
        self.assertEqual(14,len(verify.FILES))
        self.assertEqual("0.12.0-beta",verify.VERSION)
        self.assertEqual("SOVIA-V012/",verify.PREFIX)
        with zipfile.ZipFile(self._bytesio(a)) as z:
            names={verify.PREFIX+name for name in verify.FILES}|{verify.PREFIX+verify.MANIFEST}
            self.assertEqual(names,set(z.namelist()))
            meta=json.loads(z.read(verify.PREFIX+verify.MANIFEST))
            self.assertEqual("SOVIA_PORTABLE_V012_V1",meta["format"])
            self.assertEqual("0.12.0-beta",meta["version"])
            self.assertIn("sovia_history_v012.py",meta["files"])
            self.assertNotIn("sovia_history.py",meta["files"])

    @staticmethod
    def _bytesio(value):
        import io
        return io.BytesIO(value)

    def test_fixed_zip_sha_and_exact_fresh_install(self):
        result=self.create()
        self.assertEqual(result["sha256"],hashlib.sha256(self.zip.read_bytes()).hexdigest())
        self.assertEqual(14,verify.verify_archive(self.zip,self.sha)["files"])
        verify.extract_verified(self.zip,self.install,self.sha)
        self.assertEqual(14,verify.verify_directory(self.install)["files"])

    def test_old_v011_verifier_does_not_accept_new_candidate(self):
        self.create()
        with self.assertRaises(old_verify.PackageError):
            old_verify.verify_archive(self.zip,self.sha)

    def test_new_verifier_does_not_accept_old_v011(self):
        legacy=self.root/old_build.DEFAULT_NAME
        old_build.build(legacy)
        with self.assertRaises(verify.PackageError):
            verify.verify_archive(legacy,legacy.with_name(legacy.name+".sha256"))

    def test_checksum_mismatch_prevents_new_extraction(self):
        self.create()
        self.zip.write_bytes(self.zip.read_bytes()+b"tamper")
        with self.assertRaises(verify.PackageError):
            verify.extract_verified(self.zip,self.install,self.sha)
        self.assertFalse(self.install.exists())

    def test_existing_zip_never_overwritten(self):
        self.zip.write_bytes(b"PRESERVE")
        with self.assertRaises(build.BuildError):
            self.create()
        self.assertEqual(b"PRESERVE",self.zip.read_bytes())
        self.assertFalse(self.sha.exists())

    def test_existing_install_never_overwritten(self):
        self.create()
        self.install.mkdir()
        (self.install/"sentinel").write_bytes(b"PRESERVE")
        with self.assertRaises(verify.PackageError):
            verify.extract_verified(self.zip,self.install,self.sha)
        self.assertEqual(b"PRESERVE",(self.install/"sentinel").read_bytes())

    def test_extracted_verifier_works_with_isolated_python(self):
        self.create()
        verify.extract_verified(self.zip,self.install,self.sha)
        proc=subprocess.run([sys.executable,"-I","-B",
                             str(self.install/"verify_portable_v012.py"),
                             "--directory",str(self.install)],
                            capture_output=True,text=True,timeout=30)
        self.assertEqual(0,proc.returncode,proc.stderr)
        self.assertEqual(14,json.loads(proc.stdout)["files"])

    def test_extracted_full_synthetic_smoke(self):
        from portable_smoke_v012 import smoke
        result=smoke()
        self.assertEqual("v012_portable_clean_install_pass",result["status"])
        self.assertEqual((3,0),(result["boundary_events"],result["boundary_findings"]))
        self.assertTrue(result["history_backup_restored"])

if __name__=="__main__":
    unittest.main()
