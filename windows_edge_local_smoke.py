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
from importlib.util import module_from_spec, spec_from_file_location


def _adjacent(filename, alias):
    # -I excludes the script directory from ordinary import lookup; only
    # load explicit trusted local files, as the packaged builder itself does.
    source = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(alias, source)
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_SMOKE_HELPER_MISSING")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_builder = _adjacent("build_portable_p2.py", "_sovia_edge_builder")
_verifier = _adjacent("verify_portable_p2.py", "_sovia_edge_verifier")
DEFAULT_NAME, build = _builder.DEFAULT_NAME, _builder.build
extract_verified, verify_directory = _verifier.extract_verified, _verifier.verify_directory


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



def _png_size(path):
    """Bounded screenshot PNG header check; NOT human visual validation."""
    import struct
    try:
        if not path.is_file() or not 1_000 <= path.stat().st_size <= 8_388_608:
            raise EdgeSmokeError("EDGE_SCREENSHOT_INVALID")
        with path.open("rb") as file:
            header = file.read(24)
        if (len(header) != 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or
                header[12:16] != b"IHDR"):
            raise EdgeSmokeError("EDGE_SCREENSHOT_INVALID")
        width, height = struct.unpack(">II", header[16:24])
        if not 1100 <= width <= 4000 or not 900 <= height <= 4000:
            raise EdgeSmokeError("EDGE_SCREENSHOT_INVALID")
        return [width, height]
    except OSError as exc:
        raise EdgeSmokeError("EDGE_SCREENSHOT_INVALID") from exc


def capture_local_png(edge, file, profile, output):
    """Render a full viewport of synthetic file:// HTML with preinstalled Edge."""
    command = [
        str(edge), "--headless=new", "--disable-gpu",
        "--disable-background-networking", "--disable-component-update",
        "--disable-extensions", "--disable-default-apps",
        "--no-first-run", "--no-default-browser-check", "--disable-sync",
        "--no-proxy-server", "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost",
        "--disable-features=MediaRouter,OptimizationHints",
        "--force-device-scale-factor=1", "--window-size=1440,1600",
        "--hide-scrollbars", "--user-data-dir=" + str(profile),
        "--screenshot=" + str(output), file.as_uri(),
    ]
    try:
        finished = subprocess.run(
            command, capture_output=True, timeout=45, check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise EdgeSmokeError("EDGE_SCREENSHOT_TIMEOUT") from exc
    if finished.returncode:
        raise EdgeSmokeError("EDGE_SCREENSHOT_FAILED")
    return _png_size(output)


def validate_printed_pdf(path):
    """Check bounded PDF transport structure only, not rendered readability."""
    try:
        if not path.is_file() or not 2048 <= path.stat().st_size <= 8_388_608:
            raise EdgeSmokeError("EDGE_PRINT_PDF_INVALID")
        with path.open("rb") as stream:
            if not stream.read(8).startswith(b"%PDF-"):
                raise EdgeSmokeError("EDGE_PRINT_PDF_INVALID")
            stream.seek(max(0, path.stat().st_size - 2048))
            if b"%%EOF" not in stream.read():
                raise EdgeSmokeError("EDGE_PRINT_PDF_INVALID")
        return True
    except OSError as exc:
        raise EdgeSmokeError("EDGE_PRINT_PDF_INVALID") from exc


def print_local_a4(edge, html, profile, output):
    """Actual Windows Edge print-to-PDF. A4 page geometry comes from CSS @page."""
    cmd = [
        str(edge), "--headless=new", "--disable-gpu",
        "--disable-background-networking", "--disable-component-update",
        "--disable-extensions", "--disable-default-apps",
        "--no-first-run", "--no-default-browser-check", "--disable-sync",
        "--no-proxy-server", "--host-resolver-rules=MAP * ~NOTFOUND, EXCLUDE localhost",
        "--disable-features=MediaRouter,OptimizationHints",
        "--no-pdf-header-footer", "--user-data-dir=" + str(profile),
        "--print-to-pdf=" + str(output), html.as_uri(),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=45, check=False)
    except subprocess.TimeoutExpired as exc:
        raise EdgeSmokeError("EDGE_PRINT_TIMEOUT") from exc
    if proc.returncode:
        raise EdgeSmokeError("EDGE_PRINT_NONZERO_EXIT")
    validate_printed_pdf(output)
    return output.stat().st_size


def smoke(screenshot_dir=None, *, next_print_preview=False, print_a4_pdf=False):
    edge = locate_edge()
    destination = None
    if print_a4_pdf and (not next_print_preview or screenshot_dir is None):
        raise EdgeSmokeError("A4_PREVIEW_OUTPUT_REQUIRED")
    if screenshot_dir is not None:
        destination = Path(screenshot_dir).absolute()
        if (destination.exists() or destination.is_symlink() or
                not destination.parent.is_dir() or destination.parent.is_symlink()):
            raise EdgeSmokeError("SCREENSHOT_DEST_INVALID")
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
        preview = None
        if next_print_preview:
            # Run the additive next-version source ONLY. It is deliberately
            # NOT copied into or executed from the immutable 18-file ZIP.
            preview = root / "synthetic-print-preview.html"
            _run_cli(Path(__file__).resolve().with_name("sovia_report_print_preview.py"),
                     "--input", source, "--output", preview, "--synthetic-only")
            preview_dom = open_local_dom(edge, preview, root / "edge-next-print-preview")
            assert_dom(preview_dom, ("SOVIA Audit Lite", "차기 출력 미리보기",
                                     "위험 소견 5건", "data-label=", "이벤트 타임라인"))
        pdf_bytes = None
        if print_a4_pdf:
            pdf_source = root / "synthetic-next-preview-a4.pdf"
            pdf_bytes = print_local_a4(
                edge, preview, root / "edge-print-profile", pdf_source)
        dimensions = {}
        if destination is not None:
            images = {
                "synthetic-audit-edge.png": audit,
                "synthetic-dashboard-edge.png": dashboard,
            }
            if preview is not None:
                images["synthetic-next-print-preview-edge.png"] = preview
            for name, document in images.items():
                local = root / name
                dimensions[name] = capture_local_png(
                    edge, document, root / ("profile-" + name), local)
            # Publish only fabricated HTML screenshots, never source/client files.
            destination.mkdir()
            for name in images:
                with (root / name).open("rb") as source_file, (
                        destination / name).open("xb") as target:
                    shutil.copyfileobj(source_file, target)
            if pdf_bytes is not None:
                with pdf_source.open("rb") as source_file, (
                        destination / pdf_source.name).open("xb") as target:
                    shutil.copyfileobj(source_file, target)
        verify_directory(extracted)
        return {
            "status": "SYNTHETIC_EDGE_LOCAL_FILE_DOM_PASS",
            "browser": "Microsoft Edge (GitHub-hosted Windows runner)",
            "html_pages_opened": 3 if next_print_preview else 2,
            "experimental_source_only_print_preview_dom_verified": next_print_preview,
            "synthetic_edge_screenshot_count": len(dimensions),
            "synthetic_edge_screenshot_dimensions": dimensions,
            "screenshot_human_visual_review": False,
            "synthetic_edge_print_pdf_generated": pdf_bytes is not None,
            "synthetic_edge_print_pdf_bytes": pdf_bytes,
            "pdf_a4_pages_and_readability_verified": False,
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
    parser.add_argument("--screenshot-dir",
                        help="New empty folder for synthetic Edge screenshot PNGs")
    parser.add_argument("--next-print-preview", action="store_true",
                        help="Include opt-in source-only future print layout for synthetic QA")
    parser.add_argument("--print-a4-pdf", action="store_true",
                        help="Actual Edge A4 PDF output of the synthetic next-version preview")
    args = parser.parse_args(argv)
    try:
        from json import dumps
        print(dumps(smoke(args.screenshot_dir, next_print_preview=args.next_print_preview,
                          print_a4_pdf=args.print_a4_pdf),
                    ensure_ascii=False, sort_keys=True))
        return 0
    except (EdgeSmokeError, OSError, RuntimeError, ValueError) as exc:
        # Fixed non-disclosing codes, no source/Edge paths or stderr backtrace.
        code = str(exc) if isinstance(exc, EdgeSmokeError) else "LOCAL_EDGE_SMOKE_FAILED"
        print("SOVIA browser synthetic acceptance: " + code, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
