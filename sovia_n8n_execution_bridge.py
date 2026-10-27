"""SOVIA synthetic-only n8n execution summary -> pre-sanitized step bridge.

NO raw n8n execution import, API connectivity, credentials or real-data claim.
Version-pinned public summary field TYPES are references, not runtime validation.
Only already-sanitized fabricated steps are passed to the established converter.
"""
from __future__ import annotations

import argparse
from datetime import datetime
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import sys

FORMAT = "sovia.n8n_execution_bridge.synthetic.v1"
SOURCE_KIND = "synthetic_public_execution_summary_plus_sanitized_steps"
SUMMARY_KEYS = frozenset(("id", "workflowId", "status", "startedAt"))
TOP_KEYS = frozenset((
    "format", "synthetic_only", "source_kind", "pinned_release_tag",
    "execution_summary", "sanitized_steps",
))
STATUSES = frozenset((
    "canceled", "crashed", "error", "new", "running", "success",
    "unknown", "waiting",
))
# Narrow intentionally: this tool accepts a fabricated numeric-ID fixture
# subset, not a real export. Leading zeros, emails, nonnumeric IDs rejected.
SYNTHETIC_V2_ID = re.compile(r"^[1-9][0-9]{0,12}$")
UTC_SECONDS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
MAX_SYNTHETIC_ID = 999_999_999_999


class BridgeError(ValueError):
    """Fixed error codes; no echo of customer/user-supplied values."""


def _sibling(name, module_name):
    path = Path(__file__).resolve().with_name(name)
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise BridgeError("DEPENDENCY_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise BridgeError("DEPENDENCY_UNAVAILABLE") from exc
    return module


def _synthetic_identifier(value, tag):
    if tag == "n8n@1.123.88":
        if type(value) is not int or not 1 <= value <= MAX_SYNTHETIC_ID:
            raise BridgeError("SYNTHETIC_ID_TYPE_MISMATCH")
        return str(value)
    if tag == "n8n@2.44.7":
        if type(value) is not str or SYNTHETIC_V2_ID.fullmatch(value) is None:
            raise BridgeError("SYNTHETIC_ID_TYPE_MISMATCH")
        if int(value) > MAX_SYNTHETIC_ID:
            raise BridgeError("SYNTHETIC_ID_TYPE_MISMATCH")
        return value
    raise BridgeError("UNPINNED_RELEASE_BLOCKED")


def _validate_utc(value):
    if type(value) is not str or UTC_SECONDS.fullmatch(value) is None:
        raise BridgeError("INVALID_SYNTHETIC_STARTED_AT")
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise BridgeError("INVALID_SYNTHETIC_STARTED_AT") from exc


def convert_synthetic(document, policy_document):
    """Return canonical SOVIA document with ONLY explicitly given tool steps.

    Execution status/start time are checked but never invented as tool events
    or used to infer individual step outcomes, destinations or permissions.
    """
    if (type(document) is not dict or set(document) != TOP_KEYS or
            document["format"] != FORMAT or document["synthetic_only"] is not True or
            document["source_kind"] != SOURCE_KIND):
        raise BridgeError("INVALID_SYNTHETIC_BRIDGE_ENVELOPE")
    tag = document["pinned_release_tag"]
    if type(tag) is not str or tag not in ("n8n@1.123.88", "n8n@2.44.7"):
        raise BridgeError("UNPINNED_RELEASE_BLOCKED")
    ref = _sibling("sovia_n8n_execution_reference.py", "_sovia_bridge_public_reference")
    if tag not in ref.PROFILES:
        raise BridgeError("UNPINNED_RELEASE_BLOCKED")
    summary = document["execution_summary"]
    if type(summary) is not dict or set(summary) != SUMMARY_KEYS:
        raise BridgeError("INVALID_EXECUTION_SUMMARY_FIELDS")
    workflow = _synthetic_identifier(summary["workflowId"], tag)
    execution = _synthetic_identifier(summary["id"], tag)
    if type(summary["status"]) is not str or summary["status"] not in STATUSES:
        raise BridgeError("INVALID_SYNTHETIC_EXECUTION_STATUS")
    _validate_utc(summary["startedAt"])
    steps = document["sanitized_steps"]
    if type(steps) is not list or not 1 <= len(steps) <= 1000:
        raise BridgeError("SYNTHETIC_STEPS_REQUIRED")
    contract = {
        "format": "sovia.n8n_sanitized.v1",
        "workflow_id": "wf_" + workflow,
        "execution_id": "exec_" + execution,
        "steps": steps,
    }
    converter = _sibling("sovia_n8n_sanitized.py", "_sovia_bridge_existing_converter")
    try:
        canonical = converter.convert(contract, policy_document)
    except (ValueError, TypeError, OverflowError, RecursionError) as exc:
        raise BridgeError("PRE_SANITIZED_STEPS_OR_POLICY_REJECTED") from exc
    return canonical


def convert_files(input_path, policy_path, output_path):
    """Read bounded synthetic JSON and publish a single NEW canonical file."""
    audit = _sibling("sovia_audit.py", "_sovia_bridge_file_audit")
    src, pol = Path(input_path).resolve(), Path(policy_path).resolve()
    target = Path(os.path.abspath(output_path))
    if target.resolve() in (src, pol):
        raise BridgeError("OUTPUT_ALIASES_INPUT")
    if not target.parent.is_dir():
        raise BridgeError("OUTPUT_DIRECTORY_MISSING")
    try:
        document = audit.read_document(src)
        policy = audit.read_document(pol)
        canonical = convert_synthetic(document, policy)
        # Full evaluator above guarantees this is the existing canonical schema.
        output = json.dumps(canonical, ensure_ascii=False, sort_keys=True, indent=2)
        audit.write_reports_atomically([(target, output)])
    except (ValueError, TypeError, OSError, OverflowError, RecursionError) as exc:
        if isinstance(exc, BridgeError):
            raise
        raise BridgeError("BRIDGE_INPUT_OR_OUTPUT_REJECTED") from exc
    return len(canonical["events"])


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA fabricated n8n summary + pre-sanitized steps ONLY")
    p.add_argument("--input", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--output", required=True, help="NEW local canonical JSON path")
    p.add_argument("--synthetic-only", action="store_true", help="required; no real execution support")
    args = p.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ACK_REQUIRED"}), file=sys.stderr)
        return 2
    try:
        count = convert_files(args.input, args.policy, args.output)
    except BridgeError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "CONVERTED_SYNTHETIC_STEPS_ONLY",
        "event_count": count,
        "n8n_api_called": False,
        "real_n8n_execution_import_supported": False,
        "version_independently_verified": False,
        "authorization_independently_verified": False,
        "pii_absence_proven": False,
        "summary_status_used_as_tool_evidence": False,
        "synthetic_claim_independently_verified": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
