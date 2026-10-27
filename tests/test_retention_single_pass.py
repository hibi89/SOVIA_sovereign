"""Retention inventory and review must count each category with one safe traversal."""
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sovia_retention import CATEGORIES, InventoryError, inventory
from sovia_retention_review import dry_run, validate_policy

ROOT = Path(__file__).resolve().parents[1]


class SinglePassRetentionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.now = 2_000_000_000
        self.policy = json.loads((ROOT / "examples" / "demo_retention_review_policy.json")
                                 .read_text(encoding="utf-8"))

    def put(self, name, age):
        p = self.root / name
        p.write_bytes(b"SYNTHETIC_REVIEW_ONLY")
        when = self.now - age * 86400
        os.utime(p, (when, when))
        return p

    def test_single_scan_matches_five_legacy_threshold_results(self):
        files = [
            self.put("old.json", 31), self.put("recent.csv", 5),
            self.put("old.html", 15), self.put("recent.pdf", 2),
            self.put("old.sqlite", 91), self.put("recent.db", 30),
            self.put("old.sqlite-wal", 8), self.put("recent.db-shm", 3),
            self.put("old.zip", 181), self.put("recent.sha256", 50),
        ]
        baseline = [(p, p.read_bytes(), p.stat().st_mtime_ns) for p in files]
        rules = validate_policy(self.policy)
        expected = {}
        for category, (days, _, _) in rules.items():
            result = inventory(self.root, older_than_days=days, now=self.now)
            expected[category] = (result["files_by_category"].get(category, 0),
                                  result["age_candidates_by_category"].get(category, 0),
                                  result["age_candidate_bytes_by_category"].get(category, 0))
        original = os.scandir
        with patch.object(os, "scandir", wraps=original) as scan:
            result = dry_run(self.root, self.policy, now=self.now)
            self.assertEqual(1, scan.call_count)
        for cat in CATEGORIES:
            row = result["category_review"][cat]
            self.assertEqual(expected[cat],
                             (row["files_seen"], row["age_review_candidates"],
                              row["candidate_bytes"]))
        self.assertFalse(result["deletion_authorized"])
        self.assertFalse(result["deletion_attempted"])
        self.assertFalse(result["customer_data_read"])
        self.assertFalse(result["snapshot_transactional"])
        self.assertEqual(baseline, [(p, p.read_bytes(), p.stat().st_mtime_ns) for p in files])
        self.assertNotIn(str(self.root), json.dumps(result))
        self.assertNotIn("old.sqlite", json.dumps(result))

    def test_thresholds_strict_and_old_inventory_behavior_unchanged(self):
        for invalid in ({}, {"source_or_export": 30}, None):
            if invalid is None:
                self.assertEqual(30, inventory(self.root, now=self.now)["older_than_days"])
            else:
                with self.assertRaisesRegex(InventoryError, "INVALID_CATEGORY_THRESHOLDS"):
                    inventory(self.root, now=self.now, category_thresholds=invalid)
        good = {cat: 14 for cat in CATEGORIES}
        for bad in (True, 0, -1, 36501, "14", None, 4.5):
            wrong = dict(good, source_or_export=bad)
            with self.subTest(bad=bad), self.assertRaisesRegex(
                    InventoryError, "INVALID_CATEGORY_THRESHOLDS"):
                inventory(self.root, now=self.now, category_thresholds=wrong)
        self.assertIsNone(inventory(self.root, now=self.now,
                                    category_thresholds=good)["older_than_days"])

    def test_nested_directories_scanned_once_each(self):
        (self.root / "sub").mkdir()
        f = self.root / "sub" / "report.html"
        f.write_text("synthetic", encoding="utf-8")
        original = os.scandir
        with patch.object(os, "scandir", wraps=original) as scan:
            result = dry_run(self.root, self.policy, now=self.now)
            self.assertEqual(2, scan.call_count)
        self.assertEqual(2, result["entries_scanned"])
        self.assertEqual(1, result["category_review"]["rendered_report"]["files_seen"])


if __name__ == "__main__":
    unittest.main()
