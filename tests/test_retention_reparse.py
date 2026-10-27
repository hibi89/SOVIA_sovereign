"""Windows reparse-point boundary checks for source-only retention metadata walk.

Synthetic DirEntry.stat() mocks exercise junction/mount-point attributes on all
CI platforms. These are not proof against concurrent replacement or an actual
customer Windows installation.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from sovia_retention import InventoryError, _is_reparse_point, inventory

_REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


class _ReparseEntry:
    def __init__(self, folder, *, name, mode):
        self.path = str(folder / name)
        self.name = name
        self.mode = mode

    def stat(self, *, follow_symlinks=True):
        if follow_symlinks is not False:
            raise AssertionError("Refusing to follow reparse entry")
        return SimpleNamespace(
            st_mode=self.mode,
            st_file_attributes=_REPARSE,
            st_mtime=1_000_000_000,
            st_size=42,
        )


class _OneSyntheticDirectory:
    def __init__(self, entry):
        self.entry = entry

    def __enter__(self):
        return iter((self.entry,))

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class ReparseBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.now = 2_000_000_000

    def test_reparse_directory_is_skipped_before_descending(self):
        entry = _ReparseEntry(self.root, name="linked-subdir", mode=stat.S_IFDIR | 0o755)
        scanned = []

        def guarded_scandir(path):
            scanned.append(str(path))
            if str(path) != str(self.root):
                raise AssertionError("must not traverse synthetic reparse directory")
            return _OneSyntheticDirectory(entry)

        with patch("sovia_retention.os.scandir", side_effect=guarded_scandir):
            report = inventory(self.root, now=self.now)
        self.assertEqual([str(self.root)], scanned)
        self.assertEqual(1, report["symlinks_skipped"])
        self.assertEqual(1, report["entries_scanned"])
        self.assertEqual({}, report["files_by_category"])
        self.assertFalse(any(str(self.root) in x for x in report["limitations"]))

    def test_reparse_regular_file_not_counted(self):
        entry = _ReparseEntry(self.root, name="private.csv", mode=stat.S_IFREG | 0o644)
        with patch("sovia_retention.os.scandir", return_value=_OneSyntheticDirectory(entry)):
            report = inventory(self.root, now=self.now)
        self.assertEqual(1, report["symlinks_skipped"])
        self.assertEqual({}, report["files_by_category"])
        self.assertNotIn("private.csv", json.dumps(report))

    def test_reparse_root_fails_closed_before_scandir(self):
        original = Path.stat

        def fake_root_stat(path, *args, **kwargs):
            if path == self.root:
                return SimpleNamespace(st_mode=stat.S_IFDIR | 0o755,
                                       st_file_attributes=_REPARSE)
            return original(path, *args, **kwargs)

        with patch.object(Path, "stat", fake_root_stat), patch(
                "sovia_retention.os.scandir", side_effect=AssertionError("walked root")):
            with self.assertRaisesRegex(InventoryError, "INVALID_ROOT"):
                inventory(self.root, now=self.now)

    def test_missing_file_attributes_or_plain_file_remain_compatible(self):
        self.assertFalse(_is_reparse_point(SimpleNamespace(st_mode=stat.S_IFDIR)))
        self.assertTrue(_is_reparse_point(SimpleNamespace(st_file_attributes=_REPARSE)))
        f = self.root / "safe.json"
        f.write_text('{"synthetic":true}', encoding="utf-8")
        before = (f.read_bytes(), f.stat().st_mtime_ns)
        report = inventory(self.root, now=self.now)
        self.assertEqual({"source_or_export": 1}, report["files_by_category"])
        self.assertEqual(before, (f.read_bytes(), f.stat().st_mtime_ns))


if __name__ == "__main__":
    unittest.main()
