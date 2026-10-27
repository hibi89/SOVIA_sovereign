"""Read-only synthetic retention inventory regression checks."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_retention import inventory, InventoryError, main


class RetentionInventoryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.now = 2_000_000_000

    def create(self, name, content=b"secret", age=40):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        t = self.now - age * 86400
        os.utime(path, (t, t))
        return path

    def test_counts_categories_and_old_candidates(self):
        self.create("input.json")
        self.create("output.html", age=1)
        self.create("snap.sqlite")
        self.create("snap.sqlite-wal")
        self.create("README.txt")
        result = inventory(self.root, now=self.now, older_than_days=30)
        self.assertEqual({"history_or_backup": 1, "history_sidecar": 1,
                          "rendered_report": 1, "source_or_export": 1}, result["files_by_category"])
        self.assertEqual({"history_or_backup": 1, "history_sidecar": 1,
                          "source_or_export": 1}, result["age_candidates_by_category"])
        self.assertEqual(6, result["age_candidate_bytes_by_category"]["source_or_export"])

    def test_does_not_change_file_contents_or_mtime(self):
        f = self.create("private.csv", b"do not change")
        before = (f.read_bytes(), f.stat().st_mtime_ns)
        inventory(self.root, now=self.now)
        self.assertEqual(before, (f.read_bytes(), f.stat().st_mtime_ns))

    def test_returns_no_private_paths_or_filenames(self):
        self.create("secret_client_abc.json")
        out = json.dumps(inventory(self.root, now=self.now))
        self.assertNotIn("secret_client", out)
        self.assertNotIn(str(self.root), out)

    def test_skips_symlink_without_following(self):
        outer = tempfile.TemporaryDirectory()
        self.addCleanup(outer.cleanup)
        other = Path(outer.name) / "private.json"
        other.write_text("private")
        try:
            (self.root / "link.json").symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        result = inventory(self.root, now=self.now)
        self.assertEqual(1, result["symlinks_skipped"])
        self.assertFalse(result["files_by_category"])

    def test_root_symlink_refused(self):
        link = self.root.parent / (self.root.name + "-link")
        try:
            link.symlink_to(self.root, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("symlink unavailable")
        self.addCleanup(lambda: link.unlink(missing_ok=True))
        with self.assertRaisesRegex(InventoryError, "INVALID_ROOT"):
            inventory(link)

    def test_entry_limit_is_fail_closed(self):
        self.create("a.json")
        self.create("b.json")
        with self.assertRaisesRegex(InventoryError, "ENTRY_LIMIT_EXCEEDED"):
            inventory(self.root, max_entries=1)

    def test_depth_limit_is_fail_closed(self):
        self.create("/".join(["nest"] * 10) + "/deep.json")
        with self.assertRaisesRegex(InventoryError, "DEPTH_LIMIT_EXCEEDED"):
            inventory(self.root)

    def test_bad_ages_rejected(self):
        for age in (0, -1, 36501, True, 3.5):
            with self.subTest(age=age), self.assertRaisesRegex(InventoryError, "INVALID_AGE"):
                inventory(self.root, older_than_days=age)

    def test_skip_dotgit(self):
        self.create(".git/private.json")
        self.assertFalse(inventory(self.root, now=self.now)["files_by_category"])

    def test_cli_stderr_redacted_on_missing_root(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(2, main(["--root", str(self.root / "NOT-FOUND")]))
        self.assertIn("INVENTORY_FAILED", err.getvalue())
        self.assertNotIn(str(self.root), err.getvalue())

    def test_offline_isolated_python_cli(self):
        old = self.create("old.pdf")
        actual_old = time.time() - 40 * 86400
        os.utime(old, (actual_old, actual_old))
        result = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "sovia_retention.py"),
                                 "--root", str(self.root), "--older-than-days", "30"],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(1, json.loads(result.stdout)["age_candidates_by_category"]["rendered_report"])


if __name__ == "__main__":
    unittest.main()
