"""Read-only retention review planner: synthetic file metadata only."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_retention_review as review


def policy():
    return json.loads((ROOT / "examples/demo_retention_review_policy.json")
                      .read_text(encoding="utf-8"))


class ReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = self.root / "artifacts"
        self.data.mkdir()
        self.config = self.root / "policy.json"
        self.config.write_text(json.dumps(policy()), encoding="utf-8")
        self.now = 2_000_000_000

    def create(self, name, days=40, payload=b"synthetic-private-data"):
        path = self.data / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(payload)
        timestamp = self.now - days * 86400
        os.utime(path, (timestamp, timestamp))
        return path

    def test_review_counts_and_category_specific_thresholds(self):
        self.create("old.json", days=40)
        self.create("young.csv", days=2)
        self.create("report.html", days=20)
        self.create("db.sqlite", days=120)
        self.create("db.sqlite-wal", days=10)
        self.create("portable.zip", days=200)
        self.create("portable.sha256", days=1)
        result = review.dry_run(self.data, policy(), now=self.now)
        self.assertEqual("READ_ONLY_REVIEW_CANDIDATES_NOT_DISPOSAL_APPROVAL", result["status"])
        self.assertEqual({"source_or_export": 1, "rendered_report": 1,
                          "history_or_backup": 1, "history_sidecar": 1,
                          "package_or_checksum": 1},
                         {k:v["age_review_candidates"] for k,v in result["category_review"].items()})
        self.assertEqual(2, result["category_review"]["source_or_export"]["files_seen"])
        self.assertEqual(2, result["category_review"]["package_or_checksum"]["files_seen"])

    def test_category_review_dispositions_are_non_destructive(self):
        result = review.dry_run(self.data, policy(), now=self.now)
        statuses = {k:v["review_queue_status"] for k,v in result["category_review"].items()}
        self.assertEqual("VERIFY_LEGAL_HOLD", statuses["source_or_export"])
        self.assertEqual("VERIFY_BACKUP_LINEAGE", statuses["rendered_report"])
        self.assertEqual("HOLD_CLAIMED_REVIEW_REQUIRED", statuses["history_or_backup"])
        self.assertEqual("HUMAN_REVIEW_ONLY", statuses["history_sidecar"])
        self.assertEqual("HUMAN_REVIEW_ONLY", statuses["package_or_checksum"])
        self.assertFalse(result["deletion_attempted"])
        self.assertFalse(result["deletion_authorized"])
        self.assertFalse(result["backup_lineage_independently_verified"])

    def test_no_original_file_modified_or_contents_accessed(self):
        f = self.create("client_sample.json", payload=b"do-not-publish-client")
        before = (f.read_bytes(), f.stat().st_mtime_ns)
        result = review.dry_run(self.data, policy(), now=self.now)
        self.assertEqual(before, (f.read_bytes(), f.stat().st_mtime_ns))
        self.assertFalse(result["customer_data_read"])
        self.assertNotIn("do-not-publish-client", json.dumps(result))

    def test_does_not_echo_filenames_paths_or_policy_file_location(self):
        self.create("client_abcdef.json")
        output = json.dumps(review.plan_files(self.data, self.config, now=self.now))
        for secret in ("client_abcdef", str(self.root), "artifacts"):
            self.assertNotIn(secret, output)

    def test_unrecognized_extensions_not_candidates(self):
        self.create("README.txt")
        result = review.dry_run(self.data, policy(), now=self.now)
        self.assertTrue(all(v["age_review_candidates"] == 0
                            for v in result["category_review"].values()))
        self.assertEqual(1, result["entries_scanned"])

    def test_symlink_files_skipped(self):
        outside = self.root / "private.json"
        outside.write_text("private", encoding="utf-8")
        link = self.data / "outside.json"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable")
        result = review.dry_run(self.data, policy(), now=self.now)
        self.assertEqual(1, result["symlinks_skipped"])
        self.assertEqual(0, result["category_review"]["source_or_export"]["age_review_candidates"])

    def test_root_symlink_rejected(self):
        link = self.root / "linked"
        try:
            link.symlink_to(self.data, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable")
        with self.assertRaisesRegex(review.ReviewError, "REVIEW_INVENTORY_FAILED"):
            review.dry_run(link, policy(), now=self.now)

    def test_policy_symlink_rejected(self):
        link = self.root / "shortcut.json"
        try:
            link.symlink_to(self.config)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink unavailable")
        with self.assertRaisesRegex(review.ReviewError, "REVIEW_POLICY_FILE_UNAVAILABLE"):
            review.plan_files(self.data, link)

    def test_policy_missing_rejected(self):
        with self.assertRaisesRegex(review.ReviewError, "REVIEW_POLICY_FILE_UNAVAILABLE"):
            review.plan_files(self.data, self.root / "missing.json")

    def test_unknown_policy_category_refused(self):
        d = policy()
        d["categories"]["everything"] = {"review_after_days":1,"legal_hold":"none_claimed","backup_lineage":"reviewed_claimed"}
        with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_POLICY_CATEGORIES"):
            review.validate_policy(d)

    def test_missing_category_refused(self):
        d = policy()
        del d["categories"]["history_sidecar"]
        with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_POLICY_CATEGORIES"):
            review.validate_policy(d)

    def test_unknown_policy_field_refused(self):
        d = policy()
        d["customer_email"] = "private"
        with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_POLICY_ENVELOPE"):
            review.validate_policy(d)

    def test_unknown_category_field_refused(self):
        d = policy()
        d["categories"]["rendered_report"]["person_name"] = "fake"
        with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_POLICY_FIELDS"):
            review.validate_policy(d)

    def test_bad_review_threshold_refused(self):
        for value in (0, -3, True, "30", 36501, None, 1.0):
            with self.subTest(value=value):
                d = policy()
                d["categories"]["source_or_export"]["review_after_days"] = value
                with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_THRESHOLD"):
                    review.validate_policy(d)

    def test_bad_hold_or_backup_states_refused(self):
        for field,value in (("legal_hold","not_required"),
                            ("legal_hold", False),
                            ("backup_lineage", "deleted"),
                            ("backup_lineage", None)):
            with self.subTest(field=field,value=value):
                d = policy()
                d["categories"]["source_or_export"][field] = value
                with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_POLICY_STATE"):
                    review.validate_policy(d)

    def test_missing_dry_run_claim_rejected(self):
        for value in (False, "true", 1, None):
            with self.subTest(value=value):
                d = policy()
                d["dry_run_only"] = value
                with self.assertRaisesRegex(review.ReviewError, "INVALID_REVIEW_POLICY_ENVELOPE"):
                    review.validate_policy(d)

    def test_duplicate_json_keys_refused_no_traceback(self):
        self.config.write_text('{"dry_run_only":true,"dry_run_only":false}', encoding="utf-8")
        result = self.cli("--dry-run")
        self.assertEqual(2, result.returncode)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn(str(self.root), result.stderr)

    def test_oversized_policy_file_refused(self):
        self.config.write_bytes(b" " * 1_048_577)
        result = self.cli("--dry-run")
        self.assertEqual(2, result.returncode)
        self.assertFalse(result.stdout)

    def test_explicit_dry_run_ack_required(self):
        result = self.cli()
        self.assertEqual(2, result.returncode)
        self.assertIn("DRY_RUN_ACK_REQUIRED", result.stderr)

    def test_isolated_python_cli_returns_only_safe_aggregates(self):
        self.create("old.pdf", days=40)
        old = self.data / "old.pdf"
        then = time.time() - 45 * 86400
        os.utime(old, (then, then))
        run = self.cli("--dry-run")
        self.assertEqual(0, run.returncode, run.stderr)
        value = json.loads(run.stdout)
        self.assertEqual(1, value["category_review"]["rendered_report"]["age_review_candidates"])
        self.assertIs(False, value["deletion_authorized"])
        self.assertNotIn(str(self.root), run.stdout)
        self.assertNotIn("old.pdf", run.stdout)

    def cli(self, *flags):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_retention_review.py"),
             "--root", str(self.data), "--policy", str(self.config), *flags],
            capture_output=True, text=True, timeout=20
        )

    def test_invalid_clock_fails_closed(self):
        with self.assertRaisesRegex(review.ReviewError, "REVIEW_INVENTORY_FAILED"):
            review.dry_run(self.data, policy(), now=-1)

    def test_directory_depth_guard_propagates_as_safe_error(self):
        self.create("/".join(["x"] * 10) + "/file.json")
        with self.assertRaisesRegex(review.ReviewError, "REVIEW_INVENTORY_FAILED"):
            review.dry_run(self.data, policy(), now=self.now)

    def test_unstable_snapshot_is_rejected(self):
        class Changes:
            hits = 0
            @classmethod
            def inventory(cls, *args, **kwargs):
                cls.hits += 1
                return {"entries_scanned": cls.hits, "symlinks_skipped": 0,
                        "unrecognized_or_skipped": 0, "files_by_category": {},
                        "age_candidates_by_category": {}, "age_candidate_bytes_by_category": {}}
        with self.assertRaisesRegex(review.ReviewError, "REVIEW_METADATA_CHANGED_DURING_SCAN"):
            review.dry_run(self.data, policy(), now=self.now, inventory_module=Changes)

    def test_snapshot_clock_pinned_across_categories(self):
        class Clock:
            calls = []
            @classmethod
            def inventory(cls, *args, **kwargs):
                cls.calls.append(kwargs["now"])
                return {"entries_scanned":0,"symlinks_skipped":0,
                        "unrecognized_or_skipped":0,"files_by_category":{},
                        "age_candidates_by_category":{},"age_candidate_bytes_by_category":{}}
        review.dry_run(self.data, policy(), now=self.now, inventory_module=Clock)
        self.assertEqual(5, len(Clock.calls))
        self.assertEqual({self.now}, set(Clock.calls))

    def test_no_network_ever(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertFalse(review.dry_run(self.data, policy(), now=self.now)["deletion_attempted"])


if __name__ == "__main__":
    unittest.main()
