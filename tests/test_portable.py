"""Portable beta: deterministic allowlist, integrity, no-clobber and clean-install tests."""
from contextlib import redirect_stdout
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_portable as build
import verify_portable as verify


class PortableTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.archive = self.root / build.DEFAULT_NAME
        self.check = self.root / (build.DEFAULT_NAME + ".sha256")
        self.install = self.root / "unpacked"

    def create(self):
        return build.build(self.archive)

    def fake_archive(self, updates, *, duplicates=()):
        contents = build.make_payload()
        contents[verify.MANIFEST] = json.dumps({
            "format": verify.FORMAT, "version": verify.VERSION,
            "files": {name: {"bytes": len(contents[name]),
                             "sha256": hashlib.sha256(contents[name]).hexdigest()}
                      for name in sorted(contents)}
        }, sort_keys=True).encode()
        contents.update(updates)
        with zipfile.ZipFile(self.archive, "w", compression=zipfile.ZIP_STORED) as z:
            for name, data in contents.items():
                z.writestr(verify.PREFIX + name, data)
            for name in duplicates:
                z.writestr(verify.PREFIX + name, contents[name])

    def test_package_has_fixed_files_and_no_secrets(self):
        self.create()
        with zipfile.ZipFile(self.archive) as z:
            self.assertEqual({verify.PREFIX + n for n in verify.FILES} |
                             {verify.PREFIX + verify.MANIFEST}, set(z.namelist()))
            self.assertNotIn("private/", "".join(z.namelist()))
            for name in z.namelist():
                self.assertTrue(name.startswith(verify.PREFIX))
        self.assertEqual(len(verify.FILES), verify.verify_archive(self.archive)["files"])

    def test_build_identical_bytes_twice_with_different_filename_path(self):
        first = build.package_bytes()
        second = build.package_bytes()
        self.assertEqual(first, second)
        self.assertEqual(hashlib.sha256(first).digest(), hashlib.sha256(second).digest())

    def test_build_normalizes_crlf_for_cross_os_source_checkout(self):
        copy = self.root / "copy"
        for name in verify.FILES:
            target = copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            original = ROOT / name
            data = original.read_bytes()
            if name.endswith((".py", ".json", ".csv", ".md")):
                data = data.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
            target.write_bytes(data)
        self.assertEqual(build.package_bytes(ROOT), build.package_bytes(copy))

    def test_extra_private_source_files_never_packaged(self):
        copy = self.root / "sources"
        for name in verify.FILES:
            target = copy / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        (copy / ".env").write_text("PRIVATE_KEY=NEVER", encoding="utf-8")
        (copy / "client_records.sqlite").write_bytes(b"CLIENT_PERSON")
        self.assertEqual(build.package_bytes(ROOT), build.package_bytes(copy))
        self.assertNotIn(b"CLIENT_PERSON", build.package_bytes(copy))
        self.assertNotIn(b"PRIVATE_KEY=NEVER", build.package_bytes(copy))

    def test_digest_line_matches_real_zip(self):
        result = self.create()
        self.assertEqual(hashlib.sha256(self.archive.read_bytes()).hexdigest(), result["sha256"])
        self.assertEqual(result["sha256"] + "  " + self.archive.name + "\n",
                         self.check.read_text(encoding="ascii"))
        self.assertEqual("verified", verify.verify_archive(self.archive, self.check)["status"])

    def test_archives_have_fixed_metadata_and_no_compression(self):
        self.create()
        with zipfile.ZipFile(self.archive) as z:
            for info in z.infolist():
                self.assertEqual((1980, 1, 1, 0, 0, 0), info.date_time)
                self.assertEqual(zipfile.ZIP_STORED, info.compress_type)
                self.assertEqual(3, info.create_system)
                self.assertEqual(0o100000, (info.external_attr >> 16) & 0o170000)

    def test_build_does_not_overwrite_existing_zip(self):
        self.archive.write_bytes(b"EXISTING")
        with self.assertRaises(build.BuildError):
            self.create()
        self.assertEqual(b"EXISTING", self.archive.read_bytes())
        self.assertFalse(self.check.exists())

    def test_build_does_not_overwrite_existing_checksum(self):
        self.check.write_text("STAY", encoding="ascii")
        with self.assertRaises(build.BuildError):
            self.create()
        self.assertEqual("STAY", self.check.read_text(encoding="ascii"))
        self.assertFalse(self.archive.exists())

    def test_build_missing_source_fails_before_publish(self):
        source = self.root / "missing"
        source.mkdir()
        with self.assertRaises(build.BuildError):
            build.build(self.archive, root=source)
        self.assertFalse(self.archive.exists())

    def test_build_wrong_filename_rejected(self):
        with self.assertRaises(build.BuildError):
            build.build(self.root / "other.zip")
        self.assertFalse((self.root / "other.zip").exists())

    def test_missing_output_folder_does_not_create_artifact(self):
        with self.assertRaises(build.BuildError):
            build.build(self.root / "absent" / build.DEFAULT_NAME)
        self.assertFalse((self.root / "absent").exists())

    def test_verify_archive_rejects_checksum_tampering(self):
        self.create()
        original = self.archive.read_bytes()
        self.archive.write_bytes(original + b"tampered")
        with self.assertRaisesRegex(verify.PackageError, "Detached SHA-256 mismatch"):
            verify.verify_archive(self.archive, self.check)

    def test_verify_archive_rejects_wrong_member_even_without_external_checksum(self):
        self.fake_archive({"sovia_audit.py": b"changed"})
        with self.assertRaisesRegex(verify.PackageError, "Member checksum mismatch"):
            verify.verify_archive(self.archive)

    def test_verify_rejects_wrong_manifest_version(self):
        payload = build.make_payload()
        info = {"format": verify.FORMAT, "version": "HACK",
                "files": {name: {"bytes": len(value),
                                 "sha256": hashlib.sha256(value).hexdigest()}
                          for name, value in payload.items()}}
        self.fake_archive({verify.MANIFEST: json.dumps(info).encode("utf-8")})
        with self.assertRaisesRegex(verify.PackageError, "Manifest format"):
            verify.verify_archive(self.archive)

    def test_rejects_duplicate_zip_members(self):
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            self.fake_archive({}, duplicates=("sovia_audit.py",))
        with self.assertRaisesRegex(verify.PackageError, "duplicate or unsafe"):
            verify.verify_archive(self.archive)

    def test_rejects_zip_path_traversal(self):
        self.fake_archive({"../outside.py": b"MALICIOUS"})
        with self.assertRaisesRegex(verify.PackageError, "unsafe names"):
            verify.verify_archive(self.archive)
        with self.assertRaises(verify.PackageError):
            verify.extract_verified(self.archive, self.install)
        self.assertFalse(self.install.exists())
        self.assertFalse((self.root / "outside.py").exists())

    def test_rejects_missing_entry(self):
        original = build.make_payload()
        with zipfile.ZipFile(self.archive, "w", zipfile.ZIP_STORED) as z:
            z.writestr(verify.PREFIX + "sovia_audit.py", original["sovia_audit.py"])
        with self.assertRaises(verify.PackageError):
            verify.verify_archive(self.archive)

    def test_rejects_oversize_zip_without_extract(self):
        self.archive.write_bytes(b"A" * (verify.MAX_ARCHIVE_BYTES + 1))
        with self.assertRaisesRegex(verify.PackageError, "size limit"):
            verify.verify_archive(self.archive)
        self.assertFalse(self.install.exists())

    def test_strict_extract_then_directory_verification(self):
        self.create()
        result = verify.extract_verified(self.archive, self.install, self.check)
        self.assertEqual("extracted_verified", result["status"])
        self.assertEqual("verified_directory", verify.verify_directory(self.install)["status"])
        self.assertEqual(len(verify.FILES) + 1,
                         len([p for p in self.install.rglob("*") if p.is_file()]))

    def test_directory_modified_byte_detected(self):
        self.create()
        verify.extract_verified(self.archive, self.install, self.check)
        script = self.install / "sovia_audit.py"
        script.write_bytes(script.read_bytes() + b"\n# changed")
        with self.assertRaisesRegex(verify.PackageError, "checksum mismatch"):
            verify.verify_directory(self.install)

    def test_directory_unexpected_file_rejected(self):
        self.create()
        verify.extract_verified(self.archive, self.install, self.check)
        (self.install / "CUSTOMER.txt").write_text("secret", encoding="utf-8")
        with self.assertRaisesRegex(verify.PackageError, "Unexpected extracted file"):
            verify.verify_directory(self.install)

    def test_extract_must_not_clobber_occupied_directory(self):
        self.create()
        self.install.mkdir()
        (self.install / "keep.txt").write_text("KEEP", encoding="utf-8")
        with self.assertRaisesRegex(verify.PackageError, "must be new"):
            verify.extract_verified(self.archive, self.install)
        self.assertEqual("KEEP", (self.install / "keep.txt").read_text(encoding="utf-8"))

    def test_extract_bad_checksum_creates_no_destination(self):
        self.create()
        self.check.write_text("a"*64+"  "+self.archive.name+"\n", encoding="ascii")
        with self.assertRaises(verify.PackageError):
            verify.extract_verified(self.archive, self.install, self.check)
        self.assertFalse(self.install.exists())

    def test_directory_symlink_rejected_where_supported(self):
        self.create()
        verify.extract_verified(self.archive, self.install)
        filename = self.install / "sovia_audit.py"
        filename.unlink()
        try:
            filename.symlink_to(ROOT / "sovia_audit.py")
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks disallowed by Windows runner")
        with self.assertRaisesRegex(verify.PackageError, "Symlink"):
            verify.verify_directory(self.install)

    def test_verify_cli_exit_code_and_json(self):
        self.create()
        result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "verify_portable.py"),
                                 "--archive", str(self.archive),
                                 "--sha256-file", str(self.check)],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("verified", json.loads(result.stdout)["status"])

    def test_verify_cli_invalid_archive_fails(self):
        res = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "verify_portable.py"),
                              "--archive", str(self.archive), "--extract-to",
                              str(self.install)], capture_output=True, text=True, timeout=20)
        self.assertEqual(2, res.returncode)
        self.assertFalse(self.install.exists())

    def test_verify_directory_does_not_mutate_source(self):
        self.create()
        verify.extract_verified(self.archive, self.install)
        before = {(p.relative_to(self.install).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
                  for p in self.install.rglob("*") if p.is_file()}
        verify.verify_directory(self.install)
        after = {(p.relative_to(self.install).as_posix(), hashlib.sha256(p.read_bytes()).hexdigest())
                 for p in self.install.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_no_network_during_build_verify_extract(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network call")):
            self.create()
            verify.extract_verified(self.archive, self.install, self.check)
            verify.verify_directory(self.install)

    def test_portable_full_synthetic_e2e(self):
        from portable_smoke import smoke
        result = smoke()
        self.assertEqual("portable_clean_install_pass", result["status"])
        self.assertTrue(result["database_restored"])

if __name__ == "__main__":
    unittest.main()
