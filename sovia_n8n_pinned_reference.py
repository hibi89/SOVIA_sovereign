"""Pinned PUBLIC n8n API workflow schema key reference; NEVER an importer.

Official schema property names were extracted from n8n's two release-tagged
GitHub files. There are no workflow instances, node bodies, credentials,
execution records, customer logs or network calls in this module.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

FORMAT = "sovia.n8n_pinned_workflow_keys.v1"
SOURCE_KIND = "public_api_workflow_keyset_only"
REQUIRED = frozenset(("name", "nodes", "connections", "settings"))
DATA_BEARING_OPTIONALS = frozenset(("pinData", "staticData"))
KEY_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,39}$")
SCHEMAS = {
    "n8n@1.123.88": {
        "commit": "6b88ad7f6be54df9f26efe17e0c249e345b40375",
        "schema_blob_sha": "7f36ea82d077db612b6cea4807ccaa7ee1e1227e",
        "properties": frozenset((
            "id", "name", "active", "createdAt", "updatedAt", "nodes",
            "connections", "settings", "staticData", "tags",
            "shared", "activeVersion",
        )),
    },
    "n8n@2.44.7": {
        "commit": "cbe3950c51759577f9e611d28f8f5cd01828eaef",
        "schema_blob_sha": "0eb571b216406d9d2d4b6e072195a1296124e6fc",
        "properties": frozenset((
            "id", "name", "description", "parentFolderId", "active",
            "activeVersionId", "createdAt", "updatedAt", "isArchived",
            "versionId", "triggerCount", "nodes", "connections",
            "nodeGroups", "settings", "staticData", "pinData",
            "meta", "tags", "shared", "activeVersion",
        )),
    },
}


class ReferenceError(ValueError):
    """Fixed, non-sensitive status codes only."""


def compare_key_names(manifest):
    """Compare only manually provided *synthetic key names*, never a raw export."""
    if (type(manifest) is not dict or set(manifest) != {
        "schema_version", "synthetic_only", "source_kind",
        "pinned_release_tag", "field_keys",
    } or manifest["schema_version"] != FORMAT or
            manifest["synthetic_only"] is not True or
            manifest["source_kind"] != SOURCE_KIND):
        raise ReferenceError("INVALID_REFERENCE_ENVELOPE")
    tag = manifest["pinned_release_tag"]
    if type(tag) is not str or tag not in SCHEMAS:
        raise ReferenceError("UNPINNED_RELEASE_BLOCKED")
    names = manifest["field_keys"]
    if (type(names) is not list or len(names) > 30 or
            any(type(name) is not str or KEY_RE.fullmatch(name) is None
                for name in names) or len(set(names)) != len(names)):
        raise ReferenceError("INVALID_KEYSET_MANIFEST")
    actual = set(names)
    known = SCHEMAS[tag]["properties"]
    if actual - known:
        raise ReferenceError("KEY_ABSENT_FROM_PINNED_API_SCHEMA")
    # Even these names alone are innocuous; block them to avoid future
    # accidental extension of the probe into customer-carrying values.
    if actual & DATA_BEARING_OPTIONALS:
        raise ReferenceError("DATA_BEARING_OPTIONAL_FIELD_BLOCKED")
    missing = len(REQUIRED - actual)
    return {
        "status": ("PINNED_PUBLIC_API_KEYSET_RECOGNIZED_IMPORT_BLOCKED"
                   if not missing else "REQUIRED_PUBLIC_API_KEYS_MISSING_BLOCKED"),
        "pinned_release_tag": tag,
        "reference_commit": SCHEMAS[tag]["commit"],
        "reference_schema_blob_sha": SCHEMAS[tag]["schema_blob_sha"],
        "reference_required_key_count": len(REQUIRED),
        "reference_property_count": len(known),
        "missing_required_key_count": missing,
        "provided_known_key_count": len(actual),
        "raw_workflow_or_execution_import_supported": False,
        "n8n_runtime_version_verified": False,
        "native_api_integration_verified": False,
        "source_authorization_verified": False,
        "customer_payload_inspected": False,
        "conversion_performed": False,
    }


def public_reference_delta():
    """Official public schema PROPERTY NAMES only, never workflow values."""
    older = SCHEMAS["n8n@1.123.88"]["properties"]
    newer = SCHEMAS["n8n@2.44.7"]["properties"]
    return {
        "older_tag": "n8n@1.123.88",
        "newer_tag": "n8n@2.44.7",
        "required_unchanged": True,
        "added_public_property_names": sorted(newer - older),
        "removed_public_property_names": sorted(older - newer),
        "native_api_integration_verified": False,
    }


def _reader():
    path = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_n8n_pinned_reader", path)
    if spec is None or spec.loader is None:
        raise ReferenceError("REFERENCE_READER_MISSING")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise ReferenceError("REFERENCE_READER_MISSING") from exc
    return module


def compare_file(path):
    reader = _reader()
    try:
        doc = reader.read_document(path)
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise ReferenceError("REFERENCE_INPUT_REJECTED") from exc
    return compare_key_names(doc)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Pinned public n8n schema key comparison; never import")
    parser.add_argument("--input", help="ONLY synthetic key-name manifest")
    parser.add_argument("--show-public-delta", action="store_true")
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args(argv)
    if args.show_public_delta:
        if args.input is not None:
            print(json.dumps({"status": "REJECTED", "error_code": "DELTA_TAKES_NO_INPUT"}), file=sys.stderr)
            return 2
        print(json.dumps(public_reference_delta(), sort_keys=True))
        return 0
    if args.input is None or not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_MANIFEST_REQUIRED"}), file=sys.stderr)
        return 2
    try:
        report = compare_file(args.input)
    except ReferenceError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True))
    # Always block import; 3 means key contract only, even if exact.
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
