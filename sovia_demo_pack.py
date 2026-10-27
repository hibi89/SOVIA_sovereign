"""Offline customer-facing SAMPLE pack made only from one fixed fabricated fixture.

Creates a NEW local folder with a visibly watermarked real-engine HTML report,
machine-readable synthetic sample, explanation and unsigned integrity manifest.
No real customer input, screenshots, live site publishing or release approval.
"""
from __future__ import annotations

import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sys

FILES = ("SOVIA_SAMPLE_REPORT.html", "SOVIA_SAMPLE_REPORT.json",
         "SOVIA_SAMPLE_SCOPE.md", "SOVIA_SAMPLE_MANIFEST.json")
LABEL = "SAMPLE — SYNTHETIC DEMONSTRATION / 합성 예시 · 실제 고객 감사 아님"
FIXTURE = "demo_five_rules.json"

# Exact fabricated fixture values; any extra field, changed identifier,
# purported private content or replacement customer sample is rejected.
EXPECTED = {
    "schema_version": "1.0",
    "policy": {
        "allowed_tools": ["approved_lookup"],
        "approved_destinations": ["internal.example"],
        "sensitive_targets": ["client_records"],
        "max_tool_calls_per_minute": 2,
    },
    "events": [
        {"event_id": "evt-001", "occurred_at_utc": "2026-10-26T00:01:00+09:00",
         "agent_id": "demo-agent", "run_id": "demo-001",
         "tool_name": "approved_lookup", "target": "public_docs",
         "destination_domain": "internal.example", "permission_asserted": True,
         "outcome": "ok", "source_pointer": "synthetic:1"},
        {"event_id": "evt-002", "occurred_at_utc": "2026-10-26T00:01:15+09:00",
         "agent_id": "demo-agent", "run_id": "demo-001",
         "tool_name": "approved_lookup", "target": "public_docs",
         "destination_domain": "internal.example", "permission_asserted": True,
         "outcome": "ok", "source_pointer": "synthetic:2"},
        {"event_id": "evt-003", "occurred_at_utc": "2026-10-26T00:01:30+09:00",
         "agent_id": "demo-agent", "run_id": "demo-001",
         "tool_name": "unauthorized_export", "target": "client_records",
         "destination_domain": "outside.example", "permission_asserted": False,
         "outcome": "ok", "source_pointer": None},
    ],
}
EXPECTED_RULES = {
    "UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION", "SENSITIVE_ACCESS",
    "MISSING_EVIDENCE", "BURST_TOOLS",
}
CSP = ("default-src 'none'; script-src 'none'; connect-src 'none'; "
       "img-src 'none'; style-src 'unsafe-inline'; object-src 'none'; "
       "form-action 'none'; base-uri 'none'")


class SamplePackError(ValueError):
    """Fixed codes; no input content, local paths or identifiers are echoed."""


def _audit():
    local = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_demo_audit", local)
    if spec is None or spec.loader is None:
        raise SamplePackError("AUDIT_ENGINE_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise SamplePackError("AUDIT_ENGINE_UNAVAILABLE") from exc
    return module


def render_package():
    """Generate bytes only; no input path, network or filesystem writes."""
    auditor = _audit()
    sample = Path(__file__).resolve().parent / "examples" / FIXTURE
    try:
        doc = auditor.read_document(sample)
    except (OSError, ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise SamplePackError("FIXTURE_UNAVAILABLE_OR_INVALID") from exc
    if doc != EXPECTED:
        raise SamplePackError("FIXTURE_NOT_EXACT_FABRICATED_SAMPLE")
    try:
        report = auditor.evaluate(doc)
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise SamplePackError("SAMPLE_AUDIT_REJECTED") from exc
    if (report["event_count"] != 3 or report["finding_count"] != 5 or
            len(report["events"]) != 3 or len(report["findings"]) != 5 or
            {f["rule_id"] for f in report["findings"]} != EXPECTED_RULES):
        raise SamplePackError("SAMPLE_AUDIT_EXPECTATIONS_CHANGED")
    html = auditor.render_html(report)
    if (html.count("<head>") != 1 or html.count("<body>") != 1 or
            html.count("</style>") != 1):
        raise SamplePackError("UNEXPECTED_REPORT_HTML_STRUCTURE")
    html = html.replace(
        "<head>",
        '<head><meta http-equiv="Content-Security-Policy" content="' + CSP + '">',
        1)
    html = html.replace(
        "</style>",
        ".sovia-sample-banner{border:4px solid #7a2020;background:#fff1e8;"
        "color:#7a2020;font-weight:800;padding:18px;letter-spacing:.04em;"
        "font-size:1.1rem;text-align:center;margin-bottom:20px}"
        "@media print{.sovia-sample-banner{display:block!important;"
        "break-inside:avoid}}"
        "</style>", 1)
    html = html.replace("<body>", "<body><aside class='sovia-sample-banner' "
                        "role='note'>" + LABEL + "</aside>", 1)
    if html.count(LABEL) != 1:
        raise SamplePackError("SAMPLE_WATERMARK_MISSING")

    wrapped_json = {
        "format": "sovia.synthetic_sales_sample.v1",
        "watermark": "SAMPLE_SYNTHETIC_NOT_CUSTOMER_EVIDENCE",
        "sample_dataset": "fixed_fabricated_three_events_five_findings",
        "customer_records_processed": False,
        "real_n8n_integration_verified": False,
        "owner_device_or_security_certified": False,
        "commercial_release_approved": False,
        "report": report,
    }
    readme = (
        "# SOVIA Audit Lite — SAMPLE ONLY / 합성 예시\n\n"
        "**이 파일 묶음은 100% 사전에 고정된 가상 기록으로 실제 SOVIA 감사 엔진을 "
        "실행해 생성한 예시이며, 고객 감사 결과나 판매 승인 자료가 아닙니다.**\n\n"
        "**SAMPLE / SYNTHETIC DATA — NOT A CUSTOMER AUDIT.** "
        "Screenshots, independent owner Windows/browser/Defender/Korean PDF "
        "acceptance, customer permissions and supported live n8n integration "
        "have NOT been verified.\n\n"
        "- HTML: five explainable rule findings from three fabricated events; "
        "prominent on-screen AND print sample banner; offline restrictive CSP.\n"
        "- JSON: same SOVIA engine output wrapped in an explicit sample envelope; "
        "not legal evidence or independent proof of source authenticity.\n"
        "- Manifest: local SHA-256 bytes and lengths for inspection; **unsigned**, "
        "not authenticated provenance or a release signature.\n"
        "- Synthetic identifiers such as demo-agent, synthetic:1, internal.example, "
        "outside.example and client_records are fabricated placeholders only.\n"
        "- Actual screen captures for a public listing must be taken from the "
        "real app after review. Do not use this sample as a verified customer case.\n"
        "- Never substitute original n8n exports, customer records, secrets, "
        "private documents or customer screenshots for this fixed sample.\n"
        "- This tool creates an unused local folder only. It does not upload, "
        "publish, deploy, invoice, release or access network services.\n"
    )
    items = {
        FILES[0]: html.encode("utf-8"),
        FILES[1]: (json.dumps(wrapped_json, indent=2, sort_keys=True,
                            ensure_ascii=False) + "\n").encode("utf-8"),
        FILES[2]: readme.encode("utf-8"),
    }
    manifest = {
        "format": "sovia.unsigned_synthetic_demo_manifest.v1",
        "status": "UNSIGNED_SAMPLE_ONLY_NOT_A_RELEASE",
        "synthetic_only": True,
        "independent_origin_authenticated": False,
        "commercial_release_approved": False,
        "files": {
            name: {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
            for name, data in sorted(items.items())
        },
    }
    items[FILES[3]] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return items


def write_package(output_dir):
    """Creates an unused folder; uses existing auditor's atomic no-overwrite writer."""
    target = Path(os.path.abspath(output_dir))
    parent = target.parent
    if not parent.is_dir() or parent.is_symlink() or target.exists() or target.is_symlink():
        raise SamplePackError("NEW_OUTPUT_DIRECTORY_REQUIRED")
    payloads = render_package()  # Prepare/validate before changing filesystem.
    try:
        target.mkdir(exist_ok=False)
    except (FileExistsError, OSError) as exc:
        raise SamplePackError("OUTPUT_DIRECTORY_CREATE_REJECTED") from exc
    auditor = _audit()
    try:
        auditor.write_reports_atomically([(target / name, data)
                                         for name, data in payloads.items()])
    except (OSError, ValueError, TypeError) as exc:
        # Writer undoes only links it created; remove only our EMPTY folder.
        try:
            target.rmdir()
        except OSError:
            pass
        raise SamplePackError("SAMPLE_OUTPUT_REJECTED") from exc
    return {
        "status": "SYNTHETIC_SAMPLE_FILES_CREATED_NOT_PUBLISHED",
        "file_count": len(payloads),
        "synthetic_events": 3,
        "synthetic_findings": 5,
        "visible_and_print_sample_notice": True,
        "source_is_fixed_fabricated_fixture": True,
        "manifest_is_signed": False,
        "customer_evidence_or_authorization_verified": False,
        "real_n8n_compatibility_verified": False,
        "real_owner_windows_or_browser_verified": False,
        "commercial_release_approved": False,
        "network_called": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Create NEW local sample pack from fixed synthetic fixture only")
    p.add_argument("--output-dir", required=True, help="unused local directory for SAMPLE materials")
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ONLY_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        status = write_package(args.output_dir)
    except SamplePackError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(status, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
