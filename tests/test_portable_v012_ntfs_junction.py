"""SOVIA v0.12 portable verifier: cross-platform reparse and real NTFS junction gates.

All input and files are synthetic and remain confined to TemporaryDirectory.
Windows junction tests run on GitHub-hosted Windows, not the owner's own PC.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_portable_v012 as build
import verify_portable_v012 as verify

REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class SyntheticReparseAttributeTests(unittest.TestCase):
    def test_windows_junction_attribute_refused_without_following_target(self):
        fake = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755,
                               st_file_attributes=REPARSE)
        with patch.object(Path, "lstat", return_value=fake):
            self.assertTrue(verify._linked_or_reparse(Path("synthetic-only")))

    def test_ordinary_directory_without_windows_attributes_allowed(self):
        fake = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755)
        with patch.object(Path, "lstat", return_value=fake):
            self.assertFalse(verify._linked_or_reparse(Path("synthetic-only")))

    def test_missing_root_keeps_package_refusal(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(verify.PackageError):
                verify.verify_directory(Path(tmp) / "missing")


@unittest.skipUnless(os.name == "nt", "Requires a real Windows NTFS junction")
class WindowsJunctionPortableTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="sovia-v012-junction-")
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.archive = self.base / build.DEFAULT_NAME
        self.install = self.base / "verified-install"
        build.build(self.archive)
        verify.extract_verified(
            self.archive, self.install,
            self.archive.with_name(self.archive.name + ".sha256"),
        )

    def junction(self, link, target):
        proc = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, proc.returncode, "Unable to create NTFS test junction")
        self.assertNotEqual(
            0, link.stat(follow_symlinks=False).st_file_attributes & REPARSE,
            "Expected an actual Windows reparse point",
        )
        # Remove junction only; never remove its outside target via the link.
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)

    def test_linked_install_root_refused_even_with_correct_member_bytes(self):
        linked = self.base / "root-junction"
        self.junction(linked, self.install)
        self.assertEqual(len(verify.FILES), verify.verify_directory(self.install)["files"])
        with self.assertRaisesRegex(verify.PackageError, "absent or linked"):
            verify.verify_directory(linked)

    def test_allowed_examples_directory_redirected_outside_is_refused(self):
        external = self.base / "external-examples"
        (self.install / "examples").rename(external)
        before = {
            file.name: file.read_bytes() for file in external.iterdir()
            if file.is_file()
        }
        self.junction(self.install / "examples", external)
        with self.assertRaisesRegex(verify.PackageError, "Linked or reparse"):
            verify.verify_directory(self.install)
        self.assertEqual(
            before,
            {file.name: file.read_bytes() for file in external.iterdir()
             if file.is_file()},
        )


if __name__ == "__main__":
    unittest.main()
