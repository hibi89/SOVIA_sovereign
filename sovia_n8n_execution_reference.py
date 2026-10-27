"""Frozen public n8n getExecution API SCHEMA FIELD NAMES; not an API client.

The references identify two Git-tagged upstream OpenAPI sources. Only
fabricated lists of property NAMES may be compared. No execution values,
HTTP requests, credentials, payload parsing or conversion are supported.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

FORMAT = "sovia.n8n_pinned_execution_keys.v1"
SOURCE_KIND = "public_api_get_execution_response_keyset_only"
KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,39}$")
BLOCKED_KEYS = frozenset(("data", "customData", "workflowData"))
BASE = frozenset((
    "id", "data", "finished", "mode", "retryOf", "retrySuccessId",
    "startedAt", "stoppedAt", "workflowId", "waitTill", "customData",
    "status",
))
V2_ADDITIONS = frozenset((
    "createdAt", "deletedAt", "storedAt", "tracingContext",
    "deduplicationKey", "jsonSizeBytes", "binaryDataSizeBytes",
    "workflowVersionId", "usedPrivateCredentials",
    "workflowData", "dataTooLargeToDisplay",
))
# SOURCE: upstream n8n-io/n8n, exact Git tags and blobs (not instance evidence).
PROFILES = {
    "n8n@1.123.88": {
        "release_commit": "6b88ad7f6be54df9f26efe17e0c249e345b40375",
        "source_path": "packages/cli/src/public-api/v1/handlers/executions/spec/schemas/execution.yml",
        "source_blob_sha": "e20e27a02402563f3904c8b0468d56d32a42196c",
        "operation_path": "packages/cli/src/public-api/v1/handlers/executions/spec/paths/executions.id.yml",
        "operation_blob_sha": "f8b60da7a25c09cdad6d31d4f7b22f4a430a2d58",
        "properties": BASE,
        "required": frozenset(),
        "types": {"id": "number", "workflowId": "number", "retryOf": "number",
                  "retrySuccessId": "number"},
    },
    "n8n@2.44.7": {
        "release_commit": "cbe3950c51759577f9e611d28f8f5cd01828eaef",
        "source_path": "packages/cli/src/public-api/v1/handlers/executions/spec/paths/getExecution.generated.yml",
        "source_blob_sha": "329097122a6bfda7410314ff4ca73878c34b6918",
        "operation_path": "packages/cli/src/public-api/v1/handlers/executions/spec/paths/getExecution.generated.yml",
        "operation_blob_sha": "329097122a6bfda7410314ff4ca73878c34b6918",
        "properties": BASE | V2_ADDITIONS,
        "required": frozenset((
            "id", "finished", "mode", "retryOf", "retrySuccessId", "status",
            "createdAt", "startedAt", "stoppedAt", "deletedAt", "workflowId",
            "waitTill", "storedAt", "tracingContext", "deduplicationKey",
            "jsonSizeBytes", "binaryDataSizeBytes", "workflowVersionId",
            "usedPrivateCredentials",
        )),
        "types": {"id": "string", "workflowId": "string", "retryOf": "string",
                  "retrySuccessId": "string"},
    },
}


class ExecutionReferenceError(ValueError):
    """Only fixed, redacted error codes are raised."""


def public_delta():
    old, new = PROFILES["n8n@1.123.88"], PROFILES["n8n@2.44.7"]
    return {
        "source_family": SOURCE_KIND,
        "older_tag": "n8n@1.123.88",
        "newer_tag": "n8n@2.44.7",
        "older_property_count": len(old["properties"]),
        "newer_property_count": len(new["properties"]),
        "added_response_property_names": sorted(new["properties"] - old["properties"]),
        "removed_response_property_names": sorted(old["properties"] - new["properties"]),
        "four_id_fields_with_changed_declared_types": sorted(
            name for name in old["types"]
            if old["types"][name] != new["types"][name]
        ),
        "older_required_not_specified": True,
        "newer_required_count": len(new["required"]),
        "older_includeData_query_declared": True,
        "newer_includeData_default_false_declared": True,
        "newer_redactExecutionData_query_declared": True,
        "newer_ignoreDataSizeLimit_query_declared": True,
        "raw_n8n_import_supported": False,
        "n8n_instance_compatibility_verified": False,
    }


def compare(manifest):
    if (type(manifest) is not dict or set(manifest) != {
        "schema_version", "synthetic_only", "source_kind",
        "pinned_release_tag", "field_keys"
    } or manifest["schema_version"] != FORMAT or
            manifest["synthetic_only"] is not True or
            manifest["source_kind"] != SOURCE_KIND):
        raise ExecutionReferenceError("INVALID_EXECUTION_REFERENCE_ENVELOPE")
    tag = manifest["pinned_release_tag"]
    if type(tag) is not str or tag not in PROFILES:
        raise ExecutionReferenceError("UNPINNED_EXECUTION_RELEASE")
    names = manifest["field_keys"]
    if (type(names) is not list or len(names) > 30 or
            any(type(name) is not str or KEY_RE.fullmatch(name) is None
                for name in names) or len(set(names)) != len(names)):
        raise ExecutionReferenceError("INVALID_EXECUTION_KEY_NAMES")
    present = set(names)
    if present & BLOCKED_KEYS:
        raise ExecutionReferenceError("EXECUTION_PAYLOAD_FIELD_BLOCKED")
    spec = PROFILES[tag]
    if present - spec["properties"]:
        raise ExecutionReferenceError("UNKNOWN_PUBLIC_EXECUTION_FIELD")
    return {
        "status": "PUBLIC_EXECUTION_KEYSET_ONLY_IMPORT_BLOCKED",
        "pinned_release_tag": tag,
        "reference_release_commit": spec["release_commit"],
        "reference_source_blob_sha": spec["source_blob_sha"],
        "reference_property_count": len(spec["properties"]),
        "reference_declared_required_count": len(spec["required"]),
        "provided_known_key_count": len(present),
        "data_bearing_fields_never_inspected": True,
        "raw_n8n_import_supported": False,
        "request_performed": False,
        "conversion_performed": False,
        "n8n_instance_version_verified": False,
        "customer_authorization_verified": False,
        "pii_redaction_verified": False,
    }


def compare_file(path):
    source = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_public_execution_reader", source)
    if spec is None or spec.loader is None:
        raise ExecutionReferenceError("REFERENCE_READER_UNAVAILABLE")
    reader = module_from_spec(spec)
    try:
        spec.loader.exec_module(reader)
        doc = reader.read_document(path)
    except (OSError, ImportError, ValueError, TypeError, RecursionError,
            OverflowError) as exc:
        raise ExecutionReferenceError("REFERENCE_INPUT_REJECTED") from exc
    return compare(doc)


def main(argv=None):
    p = argparse.ArgumentParser(description="PUBLIC n8n execution schema key reference; import disabled")
    p.add_argument("--show-public-delta", action="store_true")
    p.add_argument("--input", help="synthetic-only key-name manifest, NEVER a real API response")
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args(argv)
    if args.show_public_delta:
        if args.input is not None or args.synthetic_only:
            print(json.dumps({"status": "REJECTED", "error_code": "DELTA_TAKES_NO_INPUT"}), file=sys.stderr)
            return 2
        print(json.dumps(public_delta(), sort_keys=True))
        return 0
    if args.input is None or not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_MANIFEST_REQUIRED"}), file=sys.stderr)
        return 2
    try:
        report = compare_file(args.input)
    except ExecutionReferenceError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    # Recognizing names is never permission to load execution objects.
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
