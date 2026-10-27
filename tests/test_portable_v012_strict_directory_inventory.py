"""Fail-closed v0.12 extracted-directory inventory regression tests (synthetic only)."""
from __future__ import annotations

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_portable_v012 as build
import verify_portable_v012 as verify


class V012DirectoryInventoryTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.archive = self.base / build.DEFAULT_NAME
        self.install = self.base / "install"
        build.build(self.archive)
        verify.extract_verified(
            self.archive,
            self.install,
            self.archive.with_name(self.archive.name + ".sha256"),
        )

    def test_pristine_allowed_directory_succeeds(self):
        self.assertEqual(9, verify.verify_directory(self.install)["files"])

    def test_unlisted_empty_root_directory_is_rejected(self):
        (self.install / "unlisted-empty-directory").mkdir()
        with self.assertRaisesRegex(verify.PackageError, "Unexpected extracted directory"):
            verify.verify_directory(self.install)

    def test_unlisted_empty_nested_directory_is_rejected(self):
        (self.install / "examples" / "unlisted-empty-directory").mkdir()
        with self.assertRaisesRegex(verify.PackageError, "Unexpected extracted directory"):
            verify.verify_directory(self.install)


if __name__ == "__main__":
    unittest.main()
