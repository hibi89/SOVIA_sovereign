"""Windows Edge local-file browser smoke for the *actual extracted* v0.11.2 ZIP.

CI-only synthetic DOM acceptance. No customer data, network fetch, remote URL,
browser visual certification, SmartScreen/Defender claim, or production server.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from build_portable_p2 import DEFAULT_NAME, build
from verify_portable_p2 import extract_verified, verify_directory


class EdgeSmokeError(RuntimeError):
    """Known, non-path-bearing rejection code for synthetic browser smoke."""


def locate_edge():
    if os.name != "nt":
        raise EdgeSmokeError("WINDOWS_REQUIRED")
    folders = (
        os.environ.get("PROGRAMFILES(X86)", ""),
        os.environ.get("PROGRAMFILES", ""),
        os.environ.get("LOCALAPPDATA", ""),
    )
    choices = [Path(folder) / "Microsoft" / "Edge" / "Application" / "msedge.exe"
               for folder in folders if folder]
    found = shutil.which("msedge") or shutil.which("msedge.exe")
    if found:
        choices.append(Path(found))
    for choice in choices:
        if choice.is_file():
            return choice
    raise EdgeSmokeError("EDGE_UNAVAILABLE")


def _run_cli(script, *args):
    try:
        proc = subprocess.run(
            [sys.executable, "-I", "-B", str(script), *map(str, args)],
            text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=25, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise EdgeSmokeError("LOCAL_CLI_TIMEOUT") from exc
    if proc.returncode:
        raise EdgeSmokeError("LOCAL_SYNTHETIC_CLI_REJECTED")


def assert_dom(markup, expected):
    """Check parsed browser DOM text with strict marker presence, no PII."""
    if not isinstance(markup, str) or not markup.lower().lstrip().startswith("<!doctype html"):
        raise EdgeSmokeError("BROWSER_DOM_INVALID")
    if "<html" not in markup.lower() or "<body" not in markup.lower():
        raise EdgeSmokeError("BROWSER_DOM_INVALID")
    if any(marker not in markup for marker in expected):
        raise EdgeSmokeError("BROWSER_DOM_MISSING_SYNTHETIC_MARKER")


def open_local_dom(edge, file, profile):
    # The generated HTML has no remote assets and dashboard has offline CSP.
    # These switches suppress background networking; this is NOT packet-capture
    # proof that the browser never makes any network requests of its own.
    arguments = [
        str(edge), "--headless=new", "--disable-gpu",
        "--disable-background-networking", "--disable-component-update",
        "--disable-extensions", "--disable-default-apps",
        "--no-first-run", "--no-default-browser-check", "--disable-sync",
        "--no-proxy-server", "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost",
        "--disable-features=MediaRouter,OptimizationHints",
        "--user-data-dir=" + str(profile), "--dump-dom", file.as_uri(),
    ]
    try:
        proc = subprocess.run(
            arguments, text=True, encoding="utf-8", errors="replace",
            capture_output=True, timeout=45, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise EdgeSmokeError("EDGE_LOCAL_DOM_TIMEOUT") from exc
    if proc.returncode:
        raise EdgeSmokeError("EDGE_LOCAL_DOM_NONZERO_EXIT")
    return proc.stdout


def smoke():
    edge = locate_edge()
    with tempfile.TemporaryDirectory(prefix="sovia-browser-qa-") as folder:
        root = Path(folder)
        zip_file = root / DEFAULT_NAME
        result = build(zip_file)
        extracted = root / "fresh-install"
        extract_verified(zip_file, extracted,
                         zip_file.with_name(zip_file.name + ".sha256"))
        verify_directory(extracted)
        source = extracted / "examples" / "demo_five_rules.json"
        audit = root / "synthetic-audit.html"
        db = root / "synthetic-history.sqlite"
        dashboard = root / "synthetic-dashboard.html"
        _run_cli(extracted / "sovia_audit.py", "--input", source,
                 "--output", audit, "--json-output", root / "synthetic-audit.json")
        _run_cli(extracted / "sovia_history.py", "import", "--input", source,
                 "--db", db)
        _run_cli(extracted / "sovia_dashboard.py", "--db", db, "--output", dashboard)

        audit_dom = open_local_dom(edge, audit, root / "edge-audit-profile")
        assert_dom(audit_dom, ("SOVIA Audit Lite", "위험 소견 5건",
                               "이벤트 타임라인", "evt-003"))
        dashboard_dom = open_local_dom(edge, dashboard, root / "edge-dashboard-profile")
        assert_dom(dashboard_dom, ("에이전트 감사 이력", "최근 이벤트 타임라인",
                                   "감사 보고서", "위험 소견", "script-src 'none'"))
        verify_directory(extracted)
        return {
            "status": "SYNTHETIC_EDGE_LOCAL_FILE_DOM_PASS",
            "browser": "Microsoft Edge (GitHub-hosted Windows runner)",
            "html_pages_opened": 2,
            "portable_archive_sha256": result["sha256"],
            "offline_html_asset_urls": False,
            "network_absence_independently_verified": False,
            "pixel_visual_review_completed": False,
            "owner_device_verified": False,
            "windows_defender_or_smartscreen_verified": False,
            "native_n8n_or_customer_source_verified": False,
            "commercial_release_authorized": False,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline synthetic Edge DOM from extracted P2 ZIP")
    parser.parse_args(argv)
    try:
        from json import dumps
        print(dumps(smoke(), ensure_ascii=False, sort_keys=True))
        return 0
    except (EdgeSmokeError, OSError, RuntimeError, ValueError) as exc:
        # Fixed non-disclosing codes, no source/Edge paths or stderr backtrace.
        code = str(exc) if isinstance(exc, EdgeSmokeError) else "LOCAL_EDGE_SMOKE_FAILED"
        print("SOVIA browser synthetic acceptance: " + code, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
