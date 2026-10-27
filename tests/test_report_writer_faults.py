"""Fault-injection regression for existing SOVIA report publisher.

All scenarios use temporary synthetic strings. No customer files/network.
"""
from __future__ import annotations

import errno
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import sovia_audit


class ReportWriterFaultTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="sovia-publish-fixture-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.first = self.root / "first.html"
        self.second = self.root / "second.json"

    def _no_stages(self):
        self.assertEqual([], list(self.root.glob(".sovia-staging-*")))

    def test_temporary_ci_checksum_diagnostic(self):
        import hashlib
        import build_portable
        # Diagnostic removed after pinning the actual newly built package.
        print("SOVIA_CURRENT_INNER_SHA256=" +
              hashlib.sha256(build_portable.package_bytes()).hexdigest(),
              flush=True)

    def test_no_post_link_staging_stat_can_orphan_new_destination(self):
        """A late metadata read must not happen after the final link exists."""
        actual_stat = os.stat
        def forbid_late_stat(path, *args, **kwargs):
            if Path(path).name.startswith(".sovia-staging-") and self.first.exists():
                raise OSError(errno.EIO, "injected post-link metadata failure")
            return actual_stat(path, *args, **kwargs)
        with patch.object(sovia_audit.os, "stat", side_effect=forbid_late_stat):
            sovia_audit.write_reports_atomically([(self.first, "synthetic")])
        self.assertEqual(b"synthetic", self.first.read_bytes())
        self._no_stages()

    def test_stat_failure_before_publication_never_leaves_output(self):
        actual_stat = os.stat
        def fail_staged_stat(path, *args, **kwargs):
            if Path(path).name.startswith(".sovia-staging-"):
                raise OSError(errno.EIO, "injected staged stat failure")
            return actual_stat(path, *args, **kwargs)
        with patch.object(sovia_audit.os, "stat", side_effect=fail_staged_stat):
            with self.assertRaises(OSError):
                sovia_audit.write_reports_atomically([(self.first, "synthetic")])
        self.assertFalse(self.first.exists())
        self._no_stages()

    def test_fsync_enospc_during_first_stage_cleans_all(self):
        with patch.object(sovia_audit.os, "fsync",
                          side_effect=OSError(errno.ENOSPC, "injected disk full")):
            with self.assertRaises(OSError):
                sovia_audit.write_reports_atomically([(self.first, "a"), (self.second, "b")])
        self.assertFalse(self.first.exists())
        self.assertFalse(self.second.exists())
        self._no_stages()

    def test_fsync_enospc_during_second_stage_never_publishes_first(self):
        real_fsync = os.fsync
        calls = 0
        def fail_second(fd):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError(errno.ENOSPC, "injected disk full second file")
            return real_fsync(fd)
        with patch.object(sovia_audit.os, "fsync", side_effect=fail_second):
            with self.assertRaises(OSError):
                sovia_audit.write_reports_atomically([(self.first, "a"), (self.second, "b")])
        self.assertEqual(calls, 2)
        self.assertFalse(self.first.exists())
        self.assertFalse(self.second.exists())
        self._no_stages()

    def test_racer_created_second_target_is_not_overwritten_or_rolled_back(self):
        real_link = os.link
        def concurrent_writer(src, dst, *args, **kwargs):
            if Path(dst) == self.second:
                self.second.write_bytes(b"EXTERNAL_OWNER_FILE")
                raise FileExistsError(errno.EEXIST, "simulated collision")
            return real_link(src, dst, *args, **kwargs)
        with patch.object(sovia_audit.os, "link", side_effect=concurrent_writer):
            with self.assertRaises(FileExistsError):
                sovia_audit.write_reports_atomically([(self.first, "ours"), (self.second, "ours")])
        self.assertFalse(self.first.exists())
        self.assertEqual(self.second.read_bytes(), b"EXTERNAL_OWNER_FILE")
        self._no_stages()

    def test_unsupported_payload_does_not_allocate_staging_descriptor(self):
        with patch.object(sovia_audit.tempfile, "mkstemp",
                          side_effect=AssertionError("must not stage invalid payload")):
            with self.assertRaises(sovia_audit.AuditInputError):
                sovia_audit.write_reports_atomically([(self.first, object())])
        self.assertFalse(self.first.exists())
        self._no_stages()

    def test_unavailable_hardlinks_fail_closed_without_fallback_overwrite(self):
        with patch.object(sovia_audit.os, "link",
                          side_effect=OSError(errno.EPERM, "hardlinks unsupported")):
            with self.assertRaises(OSError):
                sovia_audit.write_reports_atomically([(self.first, "file")])
        self.assertFalse(self.first.exists())
        self._no_stages()

    def test_second_link_eio_rolls_back_first_and_cleans_stages(self):
        real_link = os.link
        calls = 0
        def fail_second(src, dst, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError(errno.EIO, "second publish failed")
            return real_link(src, dst, *args, **kwargs)
        with patch.object(sovia_audit.os, "link", side_effect=fail_second):
            with self.assertRaises(OSError):
                sovia_audit.write_reports_atomically([(self.first, "first"), (self.second, "second")])
        self.assertEqual(calls, 2)
        self.assertFalse(self.first.exists())
        self.assertFalse(self.second.exists())
        self._no_stages()

    def test_existing_source_output_is_untouched(self):
        self.first.write_bytes(b"KEEP ORIGINAL")
        with self.assertRaises(sovia_audit.AuditInputError):
            sovia_audit.write_reports_atomically([(self.first, b"new"), (self.second, "new")])
        self.assertEqual(b"KEEP ORIGINAL", self.first.read_bytes())
        self.assertFalse(self.second.exists())
        self._no_stages()

    def test_successful_batch_keeps_bytes_and_no_staging_files(self):
        sovia_audit.write_reports_atomically([(self.first, "<h1>테스트</h1>"),
                                               (self.second, b'{"synthetic":true}')])
        self.assertEqual(self.first.read_bytes(), "<h1>테스트</h1>".encode("utf-8"))
        self.assertEqual(self.second.read_bytes(), b'{"synthetic":true}')
        self._no_stages()


if __name__ == "__main__":
    unittest.main()
