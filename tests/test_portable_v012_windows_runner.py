"""Windows one-click v0.12 synthetic demo runner integration and package contracts.

Actual cmd.exe invocation is checked on GitHub-hosted Windows. No browser
launch in CI, owner device / Defender / SmartScreen acceptance not claimed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build_portable_v012 as build
import verify_portable_v012 as verify


class WindowsRunnerPackageContractTests(unittest.TestCase):
    def test_batch_entrypoint_is_allowlisted_crlf_and_offline(self):
        self.assertIn("RUN_V012_DEMO.cmd", verify.FILES)
        data = build.package_bytes()
        with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
            runner = archive.read(verify.PREFIX + "RUN_V012_DEMO.cmd")
        self.assertIn(b"\r\n", runner)
        self.assertNotIn(b"\n", runner.replace(b"\r\n", b""))
        self.assertIn(b"--synthetic-only", runner)
        self.assertIn(b"verify_portable_v012.py", runner)
        self.assertIn(b"--directory", runner)
        self.assertIn(b"--ci", runner)
        for dangerous in (b"curl ", b"wget ", b"Invoke-WebRequest",
                          b"powershell ", b"del /", b"rmdir /"):
            self.assertNotIn(dangerous, runner)


@unittest.skipUnless(os.name == "nt", "Actual cmd.exe needs Windows")
class WindowsRunnerActualTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="sovia-windows-demo-")
        self.addCleanup(temp.cleanup)
        self.parent = Path(temp.name)
        self.archive = self.parent / build.DEFAULT_NAME
        self.install = self.parent / "SOVIA demo & spaces"
        self.output = self.parent / "SOVIA-v012-synthetic-output"
        build.build(self.archive)
        verify.extract_verified(
            self.archive, self.install,
            self.archive.with_name(self.archive.name + ".sha256"),
        )
        self.assertEqual(len(verify.FILES), verify.verify_directory(self.install)["files"])

    def launch(self):
        # Execute the real packaged CRLF batch script from an unrelated CWD.
        # --ci suppresses opening Edge or pausing in GitHub Actions.
        return subprocess.run(
            ["cmd.exe", "/d", "/c",
             str(self.install / "RUN_V012_DEMO.cmd"), "--ci"],
            cwd=self.parent, capture_output=True, text=True, timeout=45,
        )

    def test_real_cmd_creates_report_and_metadata_then_refuses_overwrite(self):
        before = (self.install / "RUN_V012_DEMO.cmd").read_bytes()
        result = self.launch()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("SOVIA SYNTHETIC DEMO COMPLETE", result.stdout)
        self.assertEqual(
            {"report.html", "report.json", "history.sqlite3"},
            {item.name for item in self.output.iterdir()},
        )
        data = json.loads((self.output / "report.json").read_text("utf-8"))
        self.assertEqual((3, 5), (data["event_count"], data["finding_count"]))
        self.assertEqual(before, (self.install / "RUN_V012_DEMO.cmd").read_bytes())
        originals = {item.name: item.read_bytes() for item in self.output.iterdir()}
        duplicate = self.launch()
        self.assertEqual(2, duplicate.returncode, duplicate.stdout + duplicate.stderr)
        self.assertIn("No overwrite", duplicate.stdout)
        self.assertEqual(
            originals,
            {item.name: item.read_bytes() for item in self.output.iterdir()},
        )

    def test_tampered_synthetic_fixture_refuses_without_any_output(self):
        fixture = self.install / "examples" / "demo_five_rules.json"
        fixture.write_bytes(fixture.read_bytes() + b"\n")
        result = self.launch()
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("Package integrity verification failed", result.stdout)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
