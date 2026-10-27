"""Dry-run output budget gate over *fixed synthetic* SOVIA cases.

Does not publish reports, alter the existing audit CLI or set a customer quota.
Uses the real auditor's JSON parser, evaluator, HTML renderer and indented JSON
serialization. Its returned metadata never contains source events or findings.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import tempfile

SCHEMA = "sovia.synthetic_output_budget.v1"
BUDGETS = (1_048_576, 2_097_152, 4_194_304)
COUNTS = (10, 100, 500, 1000)
PROFILES = ("normal", "alert_dense")


class BudgetError(ValueError):
    """Emit only fixed error codes; never include raw events or filesystem paths."""


def _load_local(name, file_name):
    path = Path(__file__).resolve().with_name(file_name)
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise BudgetError("LOCAL_MODULE_UNAVAILABLE")
    mod = module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except (OSError, ImportError) as exc:
        raise BudgetError("LOCAL_MODULE_UNAVAILABLE") from exc
    return mod


def _options(count, profile, budget_bytes):
    if type(count) is not int or count not in COUNTS:
        raise BudgetError("UNSUPPORTED_SYNTHETIC_COUNT")
    if type(profile) is not str or profile not in PROFILES:
        raise BudgetError("UNSUPPORTED_SYNTHETIC_PROFILE")
    if type(budget_bytes) is not int or budget_bytes not in BUDGETS:
        raise BudgetError("UNSUPPORTED_SIMULATED_BUDGET")


def assess_report(report, budget_bytes, audit):
    """Measure exactly the HTML/JSON serializations the current CLI publishes.

    Fail closed for unsupported budgets. The result is metadata only, not files.
    This function does NOT guard the production CLI until separately integrated.
    """
    if type(budget_bytes) is not int or budget_bytes not in BUDGETS:
        raise BudgetError("UNSUPPORTED_SIMULATED_BUDGET")
    if type(report) is not dict or type(report.get("event_count")) is not int or (
            type(report.get("finding_count")) is not int):
        raise BudgetError("INVALID_REPORT")
    try:
        html_output = audit.render_html(report).encode("utf-8")
        json_output = json.dumps(report, ensure_ascii=False, indent=2,
                                 allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, KeyError, UnicodeError, OverflowError, RecursionError) as exc:
        raise BudgetError("REPORT_SERIALIZATION_REJECTED") from exc
    html_size, json_size = len(html_output), len(json_output)
    allowed = html_size <= budget_bytes and json_size <= budget_bytes
    return {
        "status": "SIMULATED_WITHIN_BUDGET" if allowed else "SIMULATED_EXPORT_BLOCKED",
        "html_bytes": html_size,
        "json_bytes": json_size,
        "budget_per_file_bytes": budget_bytes,
        "estimated_combined_bytes": html_size + json_size,
        "exceeded_formats": [kind for kind, amount in (("html", html_size), ("json", json_size))
                             if amount > budget_bytes],
        "events": report["event_count"],
        "findings": report["finding_count"],
    }


def synthetic_preflight(count, profile, budget_bytes):
    _options(count, profile, budget_bytes)
    capacity = _load_local("_sovia_budget_capacity", "sovia_capacity_benchmark.py")
    audit = capacity._audit()
    raw = capacity._input_bytes(capacity.make_synthetic(count, profile), audit)
    # The fixed synthetic input alone is staged in an auto-cleaned temp folder.
    # No report outputs are written, even when the budget is exceeded.
    with tempfile.TemporaryDirectory(prefix="sovia-budget-synthetic-") as folder:
        input_path = Path(folder) / "fixture.json"
        input_path.write_bytes(raw)
        report = audit.evaluate(audit.read_document(input_path))
    measured = assess_report(report, budget_bytes, audit)
    if report["event_count"] != count or (
            report["finding_count"] != capacity.expected_findings(count, profile)):
        raise BudgetError("SYNTHETIC_PIPELINE_MISMATCH")
    return {
        "schema": SCHEMA,
        "scope": "SYNTHETIC_PREFLIGHT_ONLY_NOT_INTEGRATED_IN_AUDIT_CLI",
        "profile": profile,
        "synthetic_input_bytes": len(raw),
        "real_source_or_customer_data_used": False,
        "customer_quota_or_sla_approved": False,
        "production_export_enforced": False,
        "pdf_csv_disk_free_space_and_multi_file_atomicity_verified": False,
        **measured,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline synthetic output-budget dry run (no report files)")
    parser.add_argument("--synthetic-only", action="store_true")
    parser.add_argument("--events", type=int, default=1000)
    parser.add_argument("--profile", default="alert_dense")
    parser.add_argument("--budget-bytes", type=int, default=1_048_576)
    args = parser.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ONLY_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        result = synthetic_preflight(args.events, args.profile, args.budget_bytes)
    except (BudgetError, OSError, TypeError, ValueError, RecursionError, OverflowError) as exc:
        code = str(exc) if isinstance(exc, BudgetError) else "SYNTHETIC_PREFLIGHT_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["status"] == "SIMULATED_WITHIN_BUDGET" else 3


if __name__ == "__main__":
    raise SystemExit(main())
