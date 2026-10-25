"""SOVIA offline owner-PC synthetic-only diagnostic (v0.10 beta).

The script never uses customer data, network, or external APIs. It first verifies
the pristine extracted portable app, then runs subprocesses with Python -I -B
and writes only synthetic demonstration outputs into a NEW local directory.
Optional Korean PDF and owner browser visual checks are NOT automatically passed.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location, find_spec
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile

VERSION = "0.10.0-beta"
MIN_PYTHON = (3, 11)
JSON_SCHEMA = "1.0"


class SelfCheckError(ValueError):
    """A local self-check prerequisite or synthetic check failed."""


def _local(filename, name):
    source = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(name, source)
    if spec is None or spec.loader is None:
        raise SelfCheckError("LOCAL_MODULE_MISSING")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _cmd(*args):
    task = subprocess.run([sys.executable, "-I", "-B", *map(str, args)],
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          timeout=30, text=True, encoding="utf-8", errors="replace",
                          check=False)
    if task.returncode:
        raise SelfCheckError("SYNTHETIC_COMMAND_EXIT_NONZERO")
    return task.stdout.strip()


def _optional_pdf(root, sample, output_dir, checks):
    """An absent dependency/font means skipped, NEVER an installation attempt."""
    pdf = _local("sovia_pdf.py", "_sovia_selfcheck_pdf")
    if find_spec("reportlab") is None:
        checks["optional_pdf"] = "SKIPPED_REPORTLAB_MISSING"
        return
    try:
        pdf._locate_korean_font()
    except ValueError:
        checks["optional_pdf"] = "SKIPPED_KOREAN_TTF_MISSING"
        return
    pdf_path = output_dir / "synthetic-audit.pdf"
    try:
        _cmd(root / "sovia_audit.py", "--input", sample,
             "--output", output_dir / "synthetic-pdf-audit.html",
             "--pdf-output", pdf_path)
        if not pdf_path.is_file() or not pdf_path.read_bytes().startswith(b"%PDF-"):
            raise SelfCheckError("INVALID_PDF_HEADER")
        checks["optional_pdf"] = "GENERATED_NEEDS_VISUAL_REVIEW"
    except (OSError, ValueError, subprocess.SubprocessError, SelfCheckError):
        checks["optional_pdf"] = "FAILED_OPTIONAL_PDF"
        # Do not leak local font filenames or tracebacks to the diagnostic report.


def _new_results_parent(parent):
    candidate = Path(parent).absolute()
    if candidate.is_symlink():
        raise SelfCheckError("OUTPUT_DIRECTORY_SYMLINK")
    if candidate.exists():
        if not candidate.is_dir():
            raise SelfCheckError("OUTPUT_DIRECTORY_INVALID")
    else:
        if not candidate.parent.is_dir():
            raise SelfCheckError("OUTPUT_PARENT_MISSING")
        candidate.mkdir()
    if candidate.is_symlink():
        raise SelfCheckError("OUTPUT_DIRECTORY_SYMLINK")
    # Create a new uniquely named results folder: never overwrite past audits.
    return Path(tempfile.mkdtemp(prefix="SOVIA_SELF_CHECK_", dir=candidate))


def check(owner_results):
    root = Path(__file__).resolve().parent
    result_dir = _new_results_parent(owner_results)
    report = {
        "schema_version": JSON_SCHEMA,
        "version": VERSION,
        "purpose": "SYNTHETIC_ONLY_NO_CUSTOMER_DATA",
        "status": "AUTOMATED_FAILED",
        "system": {"os": platform.system(), "os_release": platform.release(),
                   "python": platform.python_version()},
        "checks": {},
        "synthetic": {},
        "manual_acceptance": {
            "audit_html_visual": "NOT_CHECKED",
            "dashboard_html_visual": "NOT_CHECKED",
            "korean_pdf_visual": "NOT_CHECKED",
            "antivirus_or_smartscreen": "NOT_CHECKED",
            "owner_device_commercial_approval": "NOT_CHECKED",
        },
        "error_code": None,
    }
    failed = None
    try:
        if sys.version_info[:2] < MIN_PYTHON:
            raise SelfCheckError("PYTHON_3_11_REQUIRED")
        report["checks"]["python"] = "PASS"
        verify = _local("verify_portable.py", "_sovia_selfcheck_verifier")
        # Fail closed before invoking any bundled app module; package must be
        # pristine, including this script and Windows launcher.
        verify.verify_directory(root)
        report["checks"]["package_integrity"] = "PASS"
        sample = root / "examples" / "demo_five_rules.json"
        out = result_dir
        _cmd(root / "sovia_audit.py", "--input", sample,
             "--output", out / "synthetic-audit.html",
             "--json-output", out / "synthetic-audit.json")
        audit = json.loads((out / "synthetic-audit.json").read_text(encoding="utf-8"))
        if (audit.get("event_count"), audit.get("finding_count")) != (3, 5):
            raise SelfCheckError("SYNTHETIC_AUDIT_COUNTS")
        if "SOVIA Audit Lite" not in (out / "synthetic-audit.html").read_text(encoding="utf-8"):
            raise SelfCheckError("AUDIT_HTML_MISSING")
        report["checks"]["audit"] = "PASS"
        source = out / "synthetic-history.sqlite"
        first = json.loads(_cmd(root / "sovia_history.py", "import", "--input",
                                sample, "--db", source))
        duplicate = json.loads(_cmd(root / "sovia_history.py", "import", "--input",
                                    sample, "--db", source))
        state = json.loads(_cmd(root / "sovia_history.py", "status", "--db", source))
        if (first.get("status") != "imported" or
            duplicate.get("status") != "already_present" or
            (state.get("reports"), state.get("events"), state.get("findings")) != (1, 3, 5)):
            raise SelfCheckError("SQLITE_COUNTS_OR_DEDUP")
        report["checks"]["sqlite"] = "PASS"
        dash = json.loads(_cmd(root / "sovia_dashboard.py", "--db", source,
                               "--output", out / "synthetic-dashboard.html"))
        html = (out / "synthetic-dashboard.html").read_text(encoding="utf-8")
        if (dash.get("reports"), dash.get("events"), dash.get("findings")) != (1, 3, 5):
            raise SelfCheckError("DASHBOARD_COUNTS")
        if "최근 이벤트 타임라인" not in html or "script-src 'none'" not in html:
            raise SelfCheckError("DASHBOARD_SECURITY_OR_CONTENT")
        report["checks"]["dashboard"] = "PASS"
        _cmd(root / "sovia_history.py", "backup", "--db", source,
             "--output", out / "synthetic-backup.sqlite")
        _cmd(root / "sovia_history.py", "restore", "--input",
             out / "synthetic-backup.sqlite", "--db", out / "synthetic-restored.sqlite")
        restored = json.loads(_cmd(root / "sovia_history.py", "status", "--db",
                                   out / "synthetic-restored.sqlite"))
        if restored != state:
            raise SelfCheckError("SQLITE_RESTORE_MISMATCH")
        report["checks"]["recovery"] = "PASS"
        report["synthetic"] = {"events": 3, "findings": 5, "reports": 1}
        _optional_pdf(root, sample, out, report["checks"])
        # Optional font/dependency absence is not a failure of the stdlib flow.
        report["status"] = "AUTOMATED_PASS_MANUAL_PENDING"
    except (SelfCheckError, ValueError, OSError, subprocess.SubprocessError,
            json.JSONDecodeError) as exc:
        failed = exc
        code = str(exc) if isinstance(exc, SelfCheckError) else type(exc).__name__.upper()
        # No raw paths, user names, input contents or exception detail in report.
        report["error_code"] = code if len(code) <= 64 else "CHECK_ERROR"
    # Even in a failure case, persist only the structured synthetic summary.
    destination = result_dir / "SELF_CHECK_RESULT.json"
    with destination.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    return report, result_dir


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA local synthetic-only owner self-check")
    parser.add_argument("--output-dir", required=True,
                        help="A local folder for NEW per-run synthetic diagnostic folders")
    args = parser.parse_args(argv)
    try:
        report, folder = check(args.output_dir)
        print("SOVIA self-check: " + report["status"])
        print("Local results folder: " + str(folder))
        print("Structured result: " + str(folder / "SELF_CHECK_RESULT.json"))
        print("Manual HTML/browser and optional Korean PDF visual checks remain NOT_CHECKED.")
        return 0 if report["status"] == "AUTOMATED_PASS_MANUAL_PENDING" else 2
    except (SelfCheckError, OSError, ValueError, subprocess.SubprocessError) as exc:
        print("SOVIA self-check could not start: " +
              (str(exc) if isinstance(exc, SelfCheckError) else type(exc).__name__),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
