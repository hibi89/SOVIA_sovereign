"""Real Windows NTFS junction acceptance: synthetic local folders only.

This suite intentionally runs inside GitHub Actions Windows hosts. It cannot
establish that an owner's Windows/Defender environment has been inspected.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_retention import InventoryError, inventory
from sovia_retention_review import dry_run

WIN = os.name == "nt"
REPARSE = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


@unittest.skipUnless(WIN, "Requires real Windows NTFS junctions")
class WindowsJunctionIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="sovia-ntfs-junction-")
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.selected = self.home / "selected"
        self.outside = self.home / "outside"
        self.selected.mkdir()
        self.outside.mkdir()
        self.now = 2_000_000_000

    def create_junction(self, junction, destination):
        self.assertFalse(junction.exists())
        # Junctions do not require symbolic-link developer-mode privileges.
        result = subprocess.run(
            ["cmd.exe", "/d", "/c", "mklink", "/J", str(junction), str(destination)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(0, result.returncode, "Windows mklink /J unavailable: " + result.stderr[:120])
        attributes = junction.stat(follow_symlinks=False).st_file_attributes
        self.assertNotEqual(0, attributes & REPARSE, "Actual NTFS junction expected")

    def test_child_ntfs_junction_skipped_and_external_file_unread(self):
        safe = self.selected / "safe.json"
        secret = self.outside / "external-private.json"
        safe.write_bytes(b"SAFE_SYNTHETIC")
        secret.write_bytes(b"NOT_A_CUSTOMER_RECORD")
        self.create_junction(self.selected / "junction", self.outside)
        before = (safe.read_bytes(), secret.read_bytes(),
                  safe.stat().st_mtime_ns, secret.stat().st_mtime_ns)
        got = inventory(self.selected, now=self.now)
        self.assertEqual(2, got["entries_scanned"])
        self.assertEqual(1, got["symlinks_skipped"])
        self.assertEqual({"source_or_export": 1}, got["files_by_category"])
        self.assertNotIn("external-private", json.dumps(got))
        self.assertEqual(before, (safe.read_bytes(), secret.read_bytes(),
                                 safe.stat().st_mtime_ns, secret.stat().st_mtime_ns))

    def test_ntfs_junction_root_refused(self):
        self.create_junction(self.home / "external-root", self.outside)
        with self.assertRaisesRegex(InventoryError, "INVALID_ROOT"):
            inventory(self.home / "external-root", now=self.now)

    def test_ancestor_junction_root_refused_even_when_terminal_dir_is_plain(self):
        child = self.outside / "child"
        child.mkdir()
        (child / "private.pdf").write_bytes(b"SYNTHETIC_ONLY")
        self.create_junction(self.selected / "link", self.outside)
        # A terminal \`child\` directory is ordinary. Its ancestor link is not.
        self.assertFalse(child.is_symlink())
        with self.assertRaisesRegex(InventoryError, "INVALID_ROOT"):
            inventory(self.selected / "link" / "child", now=self.now)

    def test_review_uses_one_scan_and_does_not_include_junction_targets(self):
        (self.selected / "synthetic.html").write_bytes(b"SAFE")
        (self.outside / "private.html").write_bytes(b"OUTSIDE")
        self.create_junction(self.selected / "junction", self.outside)
        policy = json.loads(
            (ROOT / "examples" / "demo_retention_review_policy.json").read_text("utf-8")
        )
        summary = dry_run(self.selected, policy, now=self.now)
        self.assertEqual(1, summary["symlinks_skipped"])
        self.assertEqual(2, summary["entries_scanned"])
        self.assertEqual(1, summary["category_review"]["rendered_report"]["files_seen"])
        self.assertFalse(summary["deletion_authorized"])
        self.assertFalse(summary["customer_data_read"])
        self.assertNotIn("private.html", json.dumps(summary))


if __name__ == "__main__":
    unittest.main()
