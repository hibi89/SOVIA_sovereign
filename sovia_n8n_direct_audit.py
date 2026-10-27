"""Direct offline pre-sanitized n8n-like metadata -> SOVIA HTML/JSON reports.

Never reads raw n8n executions or calls the n8n API. No intermediate
canonical JSON file is created. Synthetic and operator-claim modes are
explicitly separated. Operator statements are NOT independent consent proof.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sys


class DirectAuditError(ValueError):
    """Constant safe codes, without source values or local file paths."""


def _module(name, filename):
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise DirectAuditError("LOCAL_MODULE_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise DirectAuditError("LOCAL_MODULE_UNAVAILABLE") from exc
    return module


def _paths(source, policy, html_output, json_output, attestation):
    sources = [Path(os.path.abspath(source)), Path(os.path.abspath(policy))]
    if attestation is not None:
        sources.append(Path(os.path.abspath(attestation)))
    targets = [Path(os.path.abspath(html_output)), Path(os.path.abspath(json_output))]
    if any(p.is_symlink() or not p.is_file() for p in sources):
        raise DirectAuditError("LOCAL_SOURCE_MISSING_OR_SYMLINK")
    canonical_sources = [p.resolve() for p in sources]
    canonical_targets = [p.resolve() for p in targets]
    if (len(set(canonical_sources)) != len(canonical_sources) or
            len(set(canonical_targets)) != len(canonical_targets) or
            set(canonical_targets) & set(canonical_sources)):
        raise DirectAuditError("INPUT_OUTPUT_PATH_COLLISION")
    for p in targets:
        if p.is_symlink() or p.exists():
            raise DirectAuditError("OUTPUT_ALREADY_EXISTS")
        if not p.parent.is_dir():
            raise DirectAuditError("OUTPUT_DIRECTORY_MISSING")
    return sources, targets


def direct_audit(source, policy, html_output, json_output, *,
                 mode="synthetic", synthetic_only=False, attestation=None):
    """Read, validate, classify, render, and publish; no canonical temp file."""
    if mode not in ("synthetic", "approved-local"):
        raise DirectAuditError("INVALID_MODE")
    if mode == "synthetic":
        if synthetic_only is not True or attestation is not None:
            raise DirectAuditError("SYNTHETIC_ACK_REQUIRED")
    elif synthetic_only is not False or attestation is None:
        raise DirectAuditError("OPERATOR_ATTESTATION_REQUIRED")

    sources, targets = _paths(source, policy, html_output, json_output, attestation)
    audit = _module("_sovia_direct_audit_core", "sovia_audit.py")
    adapter = _module("_sovia_direct_n8n_contract", "sovia_n8n_sanitized.py")
    try:
        document = audit.read_document(sources[0])
        policy_doc = audit.read_document(sources[1])
        canonical = adapter.convert(document, policy_doc)
        if mode == "approved-local":
            pii = _module("_sovia_direct_pii", "sovia_pii_preflight.py")
            pii.assert_no_high_risk_patterns(document, policy_doc)
            review = audit.read_document(sources[2])
            adapter.verify_operator_attestation(review, document, policy_doc)
        report = audit.evaluate(canonical)
        html = audit.render_html(report).encode("utf-8")
        machine = json.dumps(report, sort_keys=True, ensure_ascii=False,
                             indent=2, allow_nan=False).encode("utf-8")
    except (ValueError, TypeError, KeyError, OSError, UnicodeError,
            RecursionError, OverflowError) as exc:
        raise DirectAuditError("CONTRACT_OR_REVIEW_REJECTED") from exc
    # Reject aliases again immediately before publication; the original writer
    # also uses exclusive hardlinks and never intentionally overwrites a file.
    _paths(source, policy, html_output, json_output, attestation)
    try:
        audit.write_reports_atomically(list(zip(targets, (html, machine))))
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        raise DirectAuditError("REPORT_PUBLISH_FAILED") from exc
    return {
        "status": ("SYNTHETIC_REPORTS_CREATED" if mode == "synthetic"
                   else "REPORTS_CREATED_WITH_UNVERIFIED_OPERATOR_CLAIMS"),
        "events": report["event_count"],
        "findings": report["finding_count"],
        "html_bytes": len(html),
        "json_bytes": len(machine),
        "intermediate_canonical_file_created": False,
        "pii_pattern_scan_executed": mode == "approved-local",
        "pii_absence_proven": False,
        "source_authorization_independently_verified": False,
        "n8n_native_api_compatibility_verified": False,
        "customer_delivery_approved": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Direct offline pre-sanitized n8n-like metadata -> Korean audit HTML + JSON")
    p.add_argument("--input", required=True, help="local pre-sanitized SOVIA n8n-like JSON")
    p.add_argument("--policy", required=True, help="local SOVIA policy JSON")
    p.add_argument("--html-output", required=True, help="new unused HTML report path")
    p.add_argument("--json-output", required=True, help="new unused JSON report path")
    p.add_argument("--mode", choices=("synthetic", "approved-local"), default="synthetic")
    p.add_argument("--synthetic-only", action="store_true",
                   help="required for synthetic mode; asserts fixed fabricated source")
    p.add_argument("--attestation",
                   help="operator review-claim file; required for approved-local only")
    args = p.parse_args(argv)
    try:
        result = direct_audit(
            args.input, args.policy, args.html_output, args.json_output,
            mode=args.mode, synthetic_only=args.synthetic_only,
            attestation=args.attestation)
    except DirectAuditError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}),
              file=sys.stderr)
        return 2
    except (OSError, ValueError, TypeError, RecursionError, OverflowError):
        print(json.dumps({"status": "REJECTED", "error_code": "DIRECT_AUDIT_REJECTED"}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
