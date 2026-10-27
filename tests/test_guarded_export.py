"""Synthetic-only regression of guarded local file publishing."""
from __future__ import annotations

import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import sovia_guarded_export as guard
from sovia_capacity_benchmark import make_synthetic

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples" / "demo_five_rules.json"


class GuardedExportTests(unittest.TestCase):
    def setUp(self):
        self._temporary = tempfile.TemporaryDirectory(prefix="sovia-guarded-export-test-")
        self.addCleanup(self._temporary.cleanup)
        self.folder = Path(self._temporary.name)
        self.source = self.folder / "synthetic.json"
        self.source.write_bytes(FIXTURE.read_bytes())
        self.html = self.folder / "report.html"
        self.json = self.folder / "report.json"

    def execute(self, budget=1_048_576):
        return guard.export_guarded(self.source, self.html, self.json, budget)

    def test_creates_both_real_core_reports(self):
        result = self.execute()
        self.assertEqual(result["events"], 3)
        self.assertEqual(result["findings"], 5)
        self.assertEqual(result["status"], "LOCAL_GUARDED_EXPORT_CREATED")
        self.assertTrue(self.html.read_bytes().startswith(b"<!doctype html>"))
        report = json.loads(self.json.read_text(encoding="utf-8"))
        self.assertEqual(report["event_count"], 3)
        self.assertEqual(report["finding_count"], 5)
        self.assertEqual(self.html.stat().st_size, result["html_bytes"])
        self.assertEqual(self.json.stat().st_size, result["json_bytes"])
        self.assertFalse(result["commercial_quota_or_sla_approved"])
        self.assertFalse(result["portable_beta_includes_this_tool"])

    def test_existing_html_untouched_and_json_absent(self):
        self.html.write_text("ORIGINAL", encoding="utf-8")
        with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_ALREADY_EXISTS$"):
            self.execute()
        self.assertEqual(self.html.read_text(encoding="utf-8"), "ORIGINAL")
        self.assertFalse(self.json.exists())

    def test_existing_json_untouched_and_html_absent(self):
        self.json.write_text("ORIGINAL", encoding="utf-8")
        with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_ALREADY_EXISTS$"):
            self.execute()
        self.assertEqual(self.json.read_text(encoding="utf-8"), "ORIGINAL")
        self.assertFalse(self.html.exists())

    def test_reject_input_as_output(self):
        with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_PATH_COLLISION$"):
            guard.export_guarded(self.source, self.source, self.json, 1_048_576)
        self.assertFalse(self.json.exists())

    def test_reject_same_two_outputs(self):
        with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_PATH_COLLISION$"):
            guard.export_guarded(self.source, self.html, self.html, 1_048_576)

    def test_nonexistent_parent_rejected(self):
        with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_PARENT_NOT_DIRECTORY$"):
            guard.export_guarded(self.source, self.folder / "missing" / "report.html",
                                  self.json, 1_048_576)

    def test_invalid_budget_fail_closed(self):
        for size in (True, None, 0, -1, 1, 1_048_575, 3_000_000, 1.0, "1048576"):
            with self.subTest(size=size), self.assertRaisesRegex(
                    guard.GuardedExportError, "^INVALID_LOCAL_TEST_BUDGET$"):
                self.execute(size)
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())

    def test_invalid_document_no_partial_outputs(self):
        self.source.write_text("{ malformed", encoding="utf-8")
        with self.assertRaisesRegex(guard.GuardedExportError, "^INVALID_AUDIT_INPUT$"):
            self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())

    def test_unsupported_schema_no_partial_outputs(self):
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
        document["schema_version"] = "99"
        self.source.write_text(json.dumps(document), encoding="utf-8")
        with self.assertRaisesRegex(guard.GuardedExportError, "^INVALID_AUDIT_INPUT$"):
            self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())

    def test_budget_deny_dense_outputs_before_write(self):
        self.source.write_text(json.dumps(make_synthetic(1000, "alert_dense"),
                                         ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(
                guard.GuardedExportError, "^OUTPUT_EXCEEDS_SELECTED_LOCAL_TEST_BUDGET$"):
            self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())
        self.assertEqual(list(self.folder.glob(".sovia-staging-*")), [])

    def test_dense_under_four_mib_is_not_customer_quota(self):
        self.source.write_text(json.dumps(make_synthetic(1000, "alert_dense"),
                                         ensure_ascii=False), encoding="utf-8")
        result = self.execute(4_194_304)
        self.assertGreater(result["json_bytes"], 2_000_000)
        self.assertFalse(result["commercial_quota_or_sla_approved"])

    def test_insufficient_free_space_rejected_without_staging(self):
        with mock.patch.object(guard.shutil, "disk_usage", return_value=(1000, 1000, 0)):
            with self.assertRaisesRegex(
                    guard.GuardedExportError, "^INSUFFICIENT_FREE_SPACE_PREFLIGHT$"):
                self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())
        self.assertEqual(list(self.folder.glob(".sovia-staging-*")), [])

    def test_disk_stat_error_is_constant_code(self):
        with mock.patch.object(guard.shutil, "disk_usage", side_effect=OSError("PRIVATE_PATH")):
            with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_WRITE_FAILED$"):
                self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())

    def test_second_hardlink_failure_rolls_back_both_targets(self):
        core = guard._core()
        real_link = core.os.link
        calls = []
        def link_with_failure(source, target, *args, **kwargs):
            calls.append(str(target))
            if len(calls) == 2:
                raise OSError("simulated ENOSPC")
            return real_link(source, target, *args, **kwargs)
        # _core loads a new module, but imports the shared os module; patch it for the call.
        with mock.patch.object(os, "link", side_effect=link_with_failure):
            with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_WRITE_FAILED$"):
                self.execute()
        self.assertEqual(len(calls), 2)
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())
        self.assertEqual(list(self.folder.glob(".sovia-staging-*")), [])

    def test_first_hardlink_failure_no_target_or_staging(self):
        with mock.patch.object(os, "link", side_effect=OSError("simulated ENOSPC")):
            with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_WRITE_FAILED$"):
                self.execute()
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())
        self.assertEqual(list(self.folder.glob(".sovia-staging-*")), [])

    def test_symlinked_source_blocked(self):
        alias = self.folder / "alias.json"
        try:
            alias.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        with self.assertRaisesRegex(guard.GuardedExportError, "^INVALID_LOCAL_JSON_SOURCE$"):
            guard.export_guarded(alias, self.html, self.json, 1_048_576)

    def test_symlinked_output_blocked(self):
        alias = self.folder / "alias.html"
        try:
            alias.symlink_to(self.source)
        except (OSError, NotImplementedError):
            self.skipTest("Symlink creation unavailable")
        with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_PATH_COLLISION$"):
            guard.export_guarded(self.source, alias, self.json, 1_048_576)

    def test_unexpected_extension_rejected(self):
        renamed = self.folder / "source.txt"
        renamed.write_bytes(self.source.read_bytes())
        with self.assertRaisesRegex(guard.GuardedExportError, "^INVALID_LOCAL_JSON_SOURCE$"):
            guard.export_guarded(renamed, self.html, self.json, 1_048_576)

    def test_cli_success_and_no_sensitive_paths_in_stdout(self):
        proc = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "sovia_guarded_export.py"),
                               "--input", str(self.source), "--html-output", str(self.html),
                               "--json-output", str(self.json), "--local-test-budget-bytes",
                               "1048576"], capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        result = json.loads(proc.stdout)
        self.assertEqual(result["findings"], 5)
        self.assertNotIn(str(self.folder), proc.stdout)
        self.assertEqual(proc.stderr, "")

    def test_cli_error_hides_input_path_and_contents(self):
        self.source.write_text("PRIVATE_INPUT_SHOULD_NOT_PRINT", encoding="utf-8")
        proc = subprocess.run([sys.executable, "-I", "-B", str(ROOT / "sovia_guarded_export.py"),
                               "--input", str(self.source), "--html-output", str(self.html),
                               "--json-output", str(self.json), "--local-test-budget-bytes",
                               "1048576"], capture_output=True, text=True, timeout=30)
        self.assertEqual(proc.returncode, 2)
        outcome = json.loads(proc.stderr)
        self.assertEqual(outcome["error_code"], "INVALID_AUDIT_INPUT")
        self.assertNotIn(str(self.folder), proc.stderr)
        self.assertNotIn("PRIVATE_INPUT_SHOULD_NOT_PRINT", proc.stderr)
        self.assertFalse(self.html.exists())
        self.assertFalse(self.json.exists())

    def test_no_staging_or_partial_if_preflight_denies_budget(self):
        self.source.write_text(json.dumps(make_synthetic(1000, "alert_dense")),
                               encoding="utf-8")
        with mock.patch.object(guard, "_check_storage",
                               side_effect=AssertionError("must not preflight disk")):
            with self.assertRaisesRegex(guard.GuardedExportError, "^OUTPUT_EXCEEDS_SELECTED_LOCAL_TEST_BUDGET$"):
                self.execute()
        self.assertEqual(list(self.folder.iterdir()), [self.source])

    def test_free_space_groups_two_files_on_same_volume(self):
        parent = self.folder
        small = [(parent / "a.html", b"x" * 30), (parent / "b.json", b"y" * 40)]
        with mock.patch.object(guard.shutil, "disk_usage",
                               return_value=(1000000, 900000, 2 * guard.FREE_SPACE_RESERVE_PER_FILE + 69)) as storage:
            with self.assertRaisesRegex(guard.GuardedExportError, "^INSUFFICIENT_FREE_SPACE_PREFLIGHT$"):
                guard._check_storage(small)
            self.assertEqual(storage.call_count, 1)

    def test_real_core_output_matches_legacy_serializer(self):
        core = guard._core()
        report = core.evaluate(core.read_document(self.source))
        self.execute()
        self.assertEqual(self.html.read_bytes(), core.render_html(report).encode("utf-8"))
        self.assertEqual(self.json.read_bytes(),
                         json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
