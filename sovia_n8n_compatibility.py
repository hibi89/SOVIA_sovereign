"""Offline synthetic key-only n8n family/version *claim* capability probe.

Never parses exports, raw executions, node parameters, item data or secrets.
This probe cannot verify n8n releases, source provenance, or user permission.
"""
from __future__ import annotations

import argparse
import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import re
import sys

SCHEMA = "sovia.n8n_compatibility_probe.v1"
SANITIZED = "sovia_sanitized_metadata_v1"
WORKFLOW = "mock_n8n_workflow_export"
EXECUTION = "mock_n8n_execution_api"
PROFILES = frozenset({SANITIZED, WORKFLOW, EXECUTION})
SAFE_KEYS = frozenset({"format", "workflow_id", "execution_id", "steps"})
RAW_WORKFLOW_KEYS = frozenset({"name", "nodes", "connections", "settings", "active", "id"})
RAW_EXECUTION_KEYS = frozenset({"id", "workflowId", "status", "startedAt", "stoppedAt"})
DANGEROUS_KEYS = frozenset({
    "data", "parameters", "credentials", "items", "json", "binary",
    "runData", "executionData", "pinData", "resultData", "workflowData",
    "connectionData", "prompt", "response", "secrets", "token",
})
VERSION = re.compile(r"^(?:[1-9][0-9]{0,3})\.(?:0|[1-9][0-9]{0,3})\.(?:0|[1-9][0-9]{0,3})$")
KEY = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,39}$")
MAX_KEYS = 30


class ProbeError(ValueError):
    """Fixed codes only; no untrusted input or local paths."""


def _reader():
    target = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_n8n_probe_reader", target)
    if spec is None or spec.loader is None:
        raise ProbeError("PROBE_READER_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise ProbeError("PROBE_READER_UNAVAILABLE") from exc
    return module


def probe(manifest):
    if (type(manifest) is not dict or
        set(manifest) != {"schema_version", "synthetic_only", "source_profile",
                          "claimed_n8n_version", "field_keys"} or
        manifest["schema_version"] != SCHEMA or
        manifest["synthetic_only"] is not True):
        raise ProbeError("INVALID_PROBE_ENVELOPE")
    profile = manifest["source_profile"]
    if type(profile) is not str or profile not in PROFILES:
        raise ProbeError("UNRECOGNIZED_SOURCE_PROFILE")
    version = manifest["claimed_n8n_version"]
    if profile == SANITIZED:
        if version != "not_applicable":
            raise ProbeError("SANITIZED_PROFILE_REQUIRES_NO_N8N_VERSION")
    elif type(version) is not str or VERSION.fullmatch(version) is None:
        raise ProbeError("INVALID_N8N_VERSION_CLAIM")
    keys = manifest["field_keys"]
    if (type(keys) is not list or len(keys) > MAX_KEYS or
        any(type(k) is not str or KEY.fullmatch(k) is None for k in keys) or
        len(set(keys)) != len(keys)):
        raise ProbeError("INVALID_FIELD_KEY_MANIFEST")
    found = set(keys)
    if found & DANGEROUS_KEYS:
        raise ProbeError("RAW_PAYLOAD_FIELD_BLOCKED")
    if profile == SANITIZED:
        if found - SAFE_KEYS:
            raise ProbeError("UNKNOWN_SANITIZED_FIELD_BLOCKED")
        missing = len(SAFE_KEYS - found)
        state = ("SYNTHETIC_SANITIZED_KEYSET_MATCH_ONLY" if not missing
                 else "INCOMPLETE_SANITIZED_KEYSET_BLOCKED")
        bucket = "not_applicable"
    else:
        expected = RAW_WORKFLOW_KEYS if profile == WORKFLOW else RAW_EXECUTION_KEYS
        if found - expected:
            raise ProbeError("UNKNOWN_RAW_PROFILE_FIELD_BLOCKED")
        missing = len(expected - found)
        major = int(version.split(".", 1)[0])
        state = ("UNVERIFIED_RAW_PROFILE_BLOCKED" if major in (1, 2)
                 else "UNRECOGNIZED_VERSION_BLOCKED")
        bucket = ("mock_1_x" if major == 1 else
                  "mock_2_x" if major == 2 else "other_unrecognized")
    return {
        "status": state,
        "synthetic_only": True,
        "profile_kind": profile,
        "version_claim_bucket": bucket,
        "missing_expected_key_count": missing,
        "raw_n8n_import_supported": False,
        "n8n_version_independently_verified": False,
        "native_n8n_schema_compatibility_verified": False,
        "source_authorization_verified": False,
        "payload_inspected": False,
        "conversion_performed": False,
    }


def probe_file(path):
    audit = _reader()
    try:
        doc = audit.read_document(path)
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise ProbeError("PROBE_INPUT_REJECTED") from exc
    return probe(doc)


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline synthetic metadata key compatibility probe")
    p.add_argument("--input", required=True, help="Synthetic key-only manifest (NOT an n8n export)")
    p.add_argument("--synthetic-only", action="store_true")
    a = p.parse_args(argv)
    if not a.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ONLY_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        report = probe_file(a.input)
    except ProbeError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}),
              file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    return 0 if report["status"] == "SYNTHETIC_SANITIZED_KEYSET_MATCH_ONLY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
