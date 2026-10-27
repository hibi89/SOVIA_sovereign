"""Bounded offline synthetic workload capacity measurements; NOT customer SLA data.

Uses the *actual* SOVIA JSON parser, five-rule evaluator and HTML/JSON renderer.
The source is generated internally and exists only in an auto-cleaned temp folder.
Measures wall-clock core pipeline and tracemalloc Python allocations (NOT RSS).
No real user input, database, PDF, promises, external calls or persistent output.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import gc
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import platform
import statistics
import sys
import tempfile
import time
import tracemalloc

COUNTS = (10, 100, 500, 1000)
PROFILES = ("normal", "alert_dense")
MAX_ROUNDS = 3
SCHEMA = "sovia.synthetic_capacity.v1"
START = datetime(2026, 10, 26, tzinfo=timezone.utc)


class CapacityError(ValueError):
    """Safe constant codes only, not raw data or local filesystem paths."""


def _audit():
    script = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_capacity_audit", script)
    if spec is None or spec.loader is None:
        raise CapacityError("LOCAL_AUDIT_UNAVAILABLE")
    mod = module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except (OSError, ImportError) as exc:
        raise CapacityError("LOCAL_AUDIT_UNAVAILABLE") from exc
    return mod


def _parse_csv_option(text, allowed, code):
    if type(text) is not str:
        raise CapacityError(code)
    parts = text.split(",")
    valid_tokens = tuple(str(item) for item in allowed)
    if (not parts or len(set(parts)) != len(parts) or
            any(part not in valid_tokens for part in parts)):
        raise CapacityError(code)
    return tuple(int(part) if type(allowed[0]) is int else part for part in parts)


def make_synthetic(count, profile):
    """Deterministic bounded invented IDs, times, .example domains and pointers."""
    if type(count) is not int or count not in COUNTS:
        raise CapacityError("UNSUPPORTED_SYNTHETIC_COUNT")
    if type(profile) is not str or profile not in PROFILES:
        raise CapacityError("UNSUPPORTED_SYNTHETIC_PROFILE")
    dense = profile == "alert_dense"
    events = []
    for i in range(count):
        events.append({
            "event_id": f"sim-{i + 1:04d}",
            "occurred_at_utc": (START + timedelta(seconds=i)).isoformat().replace("+00:00", "Z"),
            "agent_id": "synthetic-capacity-agent",
            "run_id": "synthetic-capacity-run",
            "tool_name": "unapproved_export" if dense else "approved_lookup",
            "target": "sensitive_demo_data" if dense else "public_demo_docs",
            "destination_domain": "unapproved.example" if dense else "approved.example",
            "permission_asserted": False if dense else True,
            "outcome": "ok",
            "source_pointer": None if dense else f"synthetic:{i + 1:04d}",
        })
    doc = {
        "schema_version": "1.0",
        "policy": {
            "allowed_tools": ["approved_lookup"],
            "approved_destinations": ["approved.example"],
            "sensitive_targets": ["sensitive_demo_data"],
            "max_tool_calls_per_minute": 2 if dense else 1000,
        },
        "events": events,
    }
    return doc


def expected_findings(count, profile):
    if type(count) is not int or count not in COUNTS or profile not in PROFILES:
        raise CapacityError("UNSUPPORTED_SYNTHETIC_CASE")
    # Four rule findings per dense event; burst from event 3 onward at 1 Hz.
    return 0 if profile == "normal" else 4 * count + max(0, count - 2)


def _input_bytes(document, audit):
    data = json.dumps(document, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(document["events"]) > audit.MAX_EVENTS or len(data) > audit.MAX_BYTES:
        raise CapacityError("SYNTHETIC_CASE_EXCEEDS_AUDIT_INPUT_CONTRACT")
    return data


def run_case(count, profile, rounds=1):
    if type(rounds) is not int or not 1 <= rounds <= MAX_ROUNDS:
        raise CapacityError("UNSUPPORTED_SYNTHETIC_ROUNDS")
    doc = make_synthetic(count, profile)
    audit = _audit()
    raw = _input_bytes(doc, audit)
    times_ms = []
    memory_kib = []
    output_html_bytes = None
    output_json_bytes = None
    with tempfile.TemporaryDirectory(prefix="sovia-synthetic-capacity-") as temporary:
        path = Path(temporary) / "fixture.json"
        path.write_bytes(raw)
        for _ in range(rounds):
            gc.collect()
            tracemalloc.start()
            try:
                start = time.perf_counter_ns()
                parsed = audit.read_document(path)
                report = audit.evaluate(parsed)
                html = audit.render_html(report).encode("utf-8")
                report_json = json.dumps(report, ensure_ascii=False, sort_keys=True,
                                         allow_nan=False).encode("utf-8")
                elapsed_ms = (time.perf_counter_ns() - start) / 1_000_000
                _, peak_bytes = tracemalloc.get_traced_memory()
            finally:
                tracemalloc.stop()
            if (report["event_count"] != count or
                    report["finding_count"] != expected_findings(count, profile) or
                    not html.startswith(b"<!doctype html>") or
                    not report_json.startswith(b"{")):
                raise CapacityError("SYNTHETIC_PIPELINE_RESULT_MISMATCH")
            times_ms.append(round(elapsed_ms, 3))
            memory_kib.append(round(peak_bytes / 1024, 1))
            output_html_bytes = len(html)
            output_json_bytes = len(report_json)
    return {
        "events": count,
        "profile": profile,
        "rounds": rounds,
        "synthetic_input_bytes": len(raw),
        "findings": expected_findings(count, profile),
        "html_bytes": output_html_bytes,
        "json_report_bytes": output_json_bytes,
        "median_pipeline_ms": round(statistics.median(times_ms), 3),
        "min_pipeline_ms": min(times_ms),
        "max_pipeline_ms": max(times_ms),
        "median_python_tracemalloc_peak_kib": round(statistics.median(memory_kib), 1),
        "max_python_tracemalloc_peak_kib": max(memory_kib),
    }


def run_suite(counts=COUNTS, profiles=PROFILES, rounds=1):
    if (type(counts) not in (tuple, list) or not counts or
            type(profiles) not in (tuple, list) or not profiles):
        raise CapacityError("INVALID_SYNTHETIC_CASE_SELECTION")
    if type(rounds) is not int or not 1 <= rounds <= MAX_ROUNDS:
        raise CapacityError("UNSUPPORTED_SYNTHETIC_ROUNDS")
    if len(set(counts)) != len(counts) or len(set(profiles)) != len(profiles):
        raise CapacityError("DUPLICATE_SYNTHETIC_CASE_SELECTION")
    if any(type(c) is not int or c not in COUNTS for c in counts):
        raise CapacityError("UNSUPPORTED_SYNTHETIC_COUNT")
    if any(type(p) is not str or p not in PROFILES for p in profiles):
        raise CapacityError("UNSUPPORTED_SYNTHETIC_PROFILE")
    results = [run_case(count, profile, rounds)
               for profile in profiles for count in counts]
    audit = _audit()
    return {
        "schema": SCHEMA,
        "status": "SYNTHETIC_MEASUREMENTS_ONLY_NOT_CUSTOMER_SLA",
        "platform": platform.system(),
        "python": platform.python_version(),
        "auditor_max_input_bytes": audit.MAX_BYTES,
        "auditor_max_events": audit.MAX_EVENTS,
        "coverage": "json_read_evaluate_html_render_json_serialize",
        "excludes": ["input_generation", "output_file_write", "PDF", "SQLite",
                     "n8n_api", "upstream_sanitization", "browser", "customer_data"],
        "memory": "Python tracemalloc peak allocations, NOT process RSS or system peak",
        "sample_is_representative_of_customers": False,
        "independent_owner_machine_verified": False,
        "performance_sla_or_commercial_quota_approved": False,
        "actual_customer_data_used": False,
        "persisted_benchmark_input_or_report": False,
        "results": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA synthetic-only bounded capacity measurement (non-SLA)")
    parser.add_argument("--synthetic-only", action="store_true", help="mandatory acknowledgment")
    parser.add_argument("--counts", default="10,100,500,1000",
                        help="comma-separated subset of 10,100,500,1000")
    parser.add_argument("--profiles", default="normal,alert_dense",
                        help="comma-separated normal,alert_dense")
    parser.add_argument("--rounds", type=int, default=1, help="measurement rounds, 1..3")
    args = parser.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ONLY_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        counts = _parse_csv_option(args.counts, COUNTS,
                                   "UNSUPPORTED_SYNTHETIC_COUNT")
        profiles = _parse_csv_option(args.profiles, PROFILES,
                                     "UNSUPPORTED_SYNTHETIC_PROFILE")
        outcome = run_suite(counts, profiles, args.rounds)
    except (CapacityError, ValueError, TypeError, OSError, OverflowError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, CapacityError) else "SYNTHETIC_CAPACITY_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    print(json.dumps(outcome, sort_keys=True, separators=(",", ":"), allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
