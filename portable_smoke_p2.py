"""Clean-folder isolated-Python P2 v0.11 candidate end-to-end acceptance.

Runs all executable actions from a verified extracted ZIP, not repository source.
Only fabricated example data; no pip, browser, network, live records or service.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from build_portable_p2 import DEFAULT_NAME, build
from verify_portable_p2 import extract_verified, verify_directory

ROOT = Path(__file__).resolve().parent


def _run(*args):
    task = subprocess.run([sys.executable, "-I", "-B", *map(str, args)],
                          text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=30, check=False)
    if task.returncode != 0:
        raise RuntimeError("Portable smoke CLI failed: " + task.stderr[-1000:])
    return task.stdout.strip()


def smoke():
    with tempfile.TemporaryDirectory(prefix="sovia-clean-install-") as tmp:
        root = Path(tmp)
        zipfile = root / DEFAULT_NAME
        result = build(zipfile)
        extracted = root / "fresh-install"
        extract_verified(zipfile, extracted, zipfile.with_name(zipfile.name + ".sha256"))
        verify_directory(extracted)
        source = extracted / "examples" / "demo_five_rules.json"
        # The audit tool prints a compact text summary; validate its real JSON file.
        # Each output is created in the temp root, outside the pristine app install.
        _run(extracted / "sovia_audit.py", "--input", source,
             "--output", root / "audit.html", "--json-output", root / "audit.json")
        report = json.loads((root / "audit.json").read_text(encoding="utf-8"))
        if (report.get("event_count"), report.get("finding_count")) != (3, 5):
            raise RuntimeError("Unexpected portable synthetic audit counts")
        html = (root / "audit.html").read_text(encoding="utf-8")
        if "SOVIA Audit Lite" not in html:
            raise RuntimeError("Missing audit HTML")
        history = json.loads(_run(extracted / "sovia_history.py", "import", "--input", source,
                                  "--db", root / "history.sqlite"))
        if (history["events"], history["findings"]) != (3, 5):
            raise RuntimeError("Wrong SQLite imported counts")
        repeat = json.loads(_run(extracted / "sovia_history.py", "import", "--input", source,
                                 "--db", root / "history.sqlite"))
        if repeat["status"] != "already_present":
            raise RuntimeError("History repeated import should be idempotent")
        db_status = json.loads(_run(extracted / "sovia_history.py", "status", "--db",
                                    root / "history.sqlite"))
        if (db_status["reports"], db_status["events"], db_status["findings"]) != (1, 3, 5):
            raise RuntimeError("Invalid SQLite status")
        dash = json.loads(_run(extracted / "sovia_dashboard.py", "--db", root / "history.sqlite",
                               "--output", root / "dashboard.html"))
        if (dash["reports"], dash["events"], dash["findings"]) != (1, 3, 5):
            raise RuntimeError("Incorrect portable dashboard summary")
        page = (root / "dashboard.html").read_text(encoding="utf-8")
        if "최근 이벤트 타임라인" not in page or "script-src 'none'" not in page:
            raise RuntimeError("Missing expected offline dashboard security/view")
        snap = json.loads(_run(extracted / "sovia_history.py", "backup", "--db",
                               root / "history.sqlite", "--output", root / "backup.sqlite"))
        restored = json.loads(_run(extracted / "sovia_history.py", "restore", "--input",
                                   root / "backup.sqlite", "--db", root / "restored.sqlite"))
        if snap["status"] != "snapshot_created" or restored["status"] != "snapshot_created":
            raise RuntimeError("SQLite backup/restore failed")
        restored_status = json.loads(_run(extracted / "sovia_history.py", "status", "--db",
                                          root / "restored.sqlite"))
        if restored_status != db_status:
            raise RuntimeError("Restored SQLite database differs in counts")
        verify_directory(extracted)
        # Owner-mode diagnostic, executed FROM THE EXTRACTED ZIP with Python -I -B.
        # All generated synthetic results live outside the pristine app folder.
        owner_out = root / "owner-results"
        owner_stdout = _run(extracted / "owner_p2_selfcheck.py", "--output-dir", owner_out)
        reports = list(owner_out.glob("SOVIA_SELF_CHECK_*/SELF_CHECK_RESULT.json"))
        if len(reports) != 1 or "AUTOMATED_PASS_MANUAL_PENDING" not in owner_stdout:
            raise RuntimeError("No successful owner self-check result")
        owner = json.loads(reports[0].read_text(encoding="utf-8"))
        if owner["status"] != "AUTOMATED_PASS_MANUAL_PENDING" or any(
            owner["checks"].get(key) != "PASS" for key in
            ("python", "package_integrity", "audit", "direct_sanitized", "aggregate_no_report", "sqlite", "dashboard", "recovery")
        ):
            raise RuntimeError("Owner synthetic self-check did not pass all mandatory checks")
        if any(value != "NOT_CHECKED" for value in owner["manual_acceptance"].values()):
            raise RuntimeError("Owner-only manual acceptance was incorrectly passed")
        verify_directory(extracted)
        return {"status": "p2_portable_clean_install_pass",
                "archive_sha256": result["sha256"], "release_files": result["files"],
                "events": 3, "findings": 5, "database_restored": True,
                "isolated_python": True, "owner_selfcheck": "AUTOMATED_PASS_MANUAL_PENDING"}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synthetic clean-install portable ZIP smoke")
    parser.parse_args(argv)
    try:
        print(json.dumps(smoke(), sort_keys=True))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print("Portable acceptance failed: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
