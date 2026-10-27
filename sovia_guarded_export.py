"""Opt-in offline guarded HTML+JSON export using the existing SOVIA core.

No default CLI behavior change, no public release and no customer SLA. This
source-only helper is deliberately excluded from the v0.10 portable beta ZIP.
The user supplies a local structured JSON source and explicitly selects a
per-file local test budget. It never opens sockets or publishes telemetry.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import shutil
import sys

LOCAL_TEST_BUDGETS = (1_048_576, 2_097_152, 4_194_304)
FREE_SPACE_RESERVE_PER_FILE = 65_536
SCHEMA = "sovia.guarded_local_export.v1"


class GuardedExportError(ValueError):
    """Contains only fixed error codes, never input paths or event values."""


def _core():
    path = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_guarded_core", path)
    if spec is None or spec.loader is None:
        raise GuardedExportError("LOCAL_AUDIT_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise GuardedExportError("LOCAL_AUDIT_UNAVAILABLE") from exc
    return module


def _paths(source_path, html_path, json_path):
    source = Path(os.path.abspath(source_path))
    if source.is_symlink() or source.suffix.lower() != ".json" or not source.is_file():
        raise GuardedExportError("INVALID_LOCAL_JSON_SOURCE")
    targets = (Path(os.path.abspath(html_path)), Path(os.path.abspath(json_path)))
    canonical_source = source.resolve()
    canonical_targets = tuple(path.resolve() for path in targets)
    if len(set(canonical_targets)) != 2 or canonical_source in canonical_targets:
        raise GuardedExportError("OUTPUT_PATH_COLLISION")
    for target in targets:
        if target.exists() or target.is_symlink():
            raise GuardedExportError("OUTPUT_ALREADY_EXISTS")
        if not target.parent.is_dir():
            raise GuardedExportError("OUTPUT_PARENT_NOT_DIRECTORY")
    return source, targets


def _check_storage(items):
    """Best-effort preflight, not proof of later writes under concurrency.

    Group by real device, so two outputs sharing a filesystem are added rather
    than independently compared with the same available free bytes.
    """
    per_device = {}
    for target, data in items:
        device = os.stat(target.parent).st_dev
        size = len(data) + FREE_SPACE_RESERVE_PER_FILE
        if device in per_device:
            old_parent, old_bytes = per_device[device]
            per_device[device] = (old_parent, old_bytes + size)
        else:
            per_device[device] = (target.parent, size)
    for parent, required in per_device.values():
        if shutil.disk_usage(parent).free < required:
            raise GuardedExportError("INSUFFICIENT_FREE_SPACE_PREFLIGHT")


def export_guarded(source_path, html_path, json_path, local_test_budget_bytes):
    """Measure both finished formats, reject over-budget, then no-clobber write.

    Existing core writer stages both complete files, publishes by exclusive
    hard link, and attempts rollback on errors; readers across both filenames
    do NOT get a filesystem transaction or concurrency guarantee.
    """
    if type(local_test_budget_bytes) is not int or local_test_budget_bytes not in LOCAL_TEST_BUDGETS:
        raise GuardedExportError("INVALID_LOCAL_TEST_BUDGET")
    source, targets = _paths(source_path, html_path, json_path)
    audit = _core()
    try:
        report = audit.evaluate(audit.read_document(source))
    except (audit.AuditInputError, OSError, ValueError, TypeError, RecursionError) as exc:
        raise GuardedExportError("INVALID_AUDIT_INPUT") from exc
    try:
        html_bytes = audit.render_html(report).encode("utf-8")
        json_bytes = json.dumps(report, ensure_ascii=False, indent=2,
                                allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, KeyError, UnicodeError, OverflowError, RecursionError) as exc:
        raise GuardedExportError("REPORT_SERIALIZATION_REJECTED") from exc
    items = list(zip(targets, (html_bytes, json_bytes)))
    if any(len(data) > local_test_budget_bytes for _, data in items):
        raise GuardedExportError("OUTPUT_EXCEEDS_SELECTED_LOCAL_TEST_BUDGET")
    # Repeat collision checks immediately before staging. The original writer
    # itself also refuses occupied paths and os.link won't overwrite races.
    _paths(source_path, html_path, json_path)
    try:
        _check_storage(items)
        audit.write_reports_atomically(items)
    except GuardedExportError:
        raise
    except (audit.AuditInputError, OSError) as exc:
        raise GuardedExportError("OUTPUT_WRITE_FAILED") from exc
    return {
        "schema": SCHEMA,
        "status": "LOCAL_GUARDED_EXPORT_CREATED",
        "events": report["event_count"],
        "findings": report["finding_count"],
        "html_bytes": len(html_bytes),
        "json_bytes": len(json_bytes),
        "local_test_budget_per_file_bytes": local_test_budget_bytes,
        "commercial_quota_or_sla_approved": False,
        "full_multi_file_transaction_guaranteed": False,
        "disk_space_checked_at_write_time_guaranteed": False,
        "portable_beta_includes_this_tool": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Opt-in offline guarded SOVIA JSON to HTML+JSON export")
    parser.add_argument("--input", required=True, help="local authorized and sanitized schema-1.0 JSON only")
    parser.add_argument("--html-output", required=True, help="new report HTML filename, never overwritten")
    parser.add_argument("--json-output", required=True, help="new report JSON filename, never overwritten")
    parser.add_argument("--local-test-budget-bytes", required=True, type=int,
                        help="per-file test ceiling: 1048576, 2097152, 4194304; NOT a customer quota")
    args = parser.parse_args(argv)
    try:
        outcome = export_guarded(args.input, args.html_output, args.json_output,
                                 args.local_test_budget_bytes)
    except GuardedExportError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, OverflowError, RecursionError):
        # User input/path/OS exception descriptions could expose sensitive data.
        print(json.dumps({"status": "REJECTED", "error_code": "LOCAL_EXPORT_REJECTED"}),
              file=sys.stderr)
        return 2
    print(json.dumps(outcome, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
