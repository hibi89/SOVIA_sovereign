"""Read-only synthetic evidence binding and metadata privacy preflight.

THIS IS NOT an origin authenticator, n8n API importer, real PII certification,
signed manifest, or customer authorization. Hashes verify only self-consistency.
No writes, network, secrets, raw execution payload or auto-redaction.
"""
from __future__ import annotations

import argparse
import hmac
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

FORMAT = "sovia.synthetic_evidence.v1"
CLAIM = "fabricated_offline_fixture"
MANIFEST_KEYS = frozenset({
    "schema_version", "synthetic_only", "origin_claim",
    "pinned_release_tag", "source_sha256", "policy_sha256",
    "expected_canonical_sha256",
})
DIGEST = re.compile(r"^[0-9a-f]{64}$")
RELEASES = frozenset(("n8n@1.123.88", "n8n@2.44.7"))


class EvidenceError(ValueError):
    """Stable safe error codes only; original values never echoed."""


def _load(filename, name):
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise EvidenceError("EVIDENCE_DEPENDENCY_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise EvidenceError("EVIDENCE_DEPENDENCY_UNAVAILABLE") from exc
    return module


def _check_manifest(manifest):
    if (type(manifest) is not dict or set(manifest) != MANIFEST_KEYS or
            manifest["schema_version"] != FORMAT or
            manifest["synthetic_only"] is not True or
            manifest["origin_claim"] != CLAIM):
        raise EvidenceError("INVALID_SYNTHETIC_EVIDENCE_MANIFEST")
    tag = manifest["pinned_release_tag"]
    if type(tag) is not str or tag not in RELEASES:
        raise EvidenceError("UNPINNED_EVIDENCE_RELEASE")
    for field in ("source_sha256", "policy_sha256", "expected_canonical_sha256"):
        digest = manifest[field]
        if type(digest) is not str or DIGEST.fullmatch(digest) is None:
            raise EvidenceError("INVALID_EVIDENCE_SHA256")
    return tag


def verify(source, policy, manifest):
    """Verify fabricated-document digests and heuristic patterns, read-only.

    Re-hashing after tampering can forge the entire unsiged manifest. We never
    represent a successful comparison as genuine origin, operator ID or consent.
    """
    tag = _check_manifest(manifest)
    if (type(source) is not dict or source.get("synthetic_only") is not True or
            source.get("pinned_release_tag") != tag):
        raise EvidenceError("SOURCE_RELEASE_OR_CLAIM_MISMATCH")
    checker = _load("sovia_pii_preflight.py", "_sovia_evidence_pii_preflight")
    try:
        # Before conversion, so source/policy suspect strings are not published.
        checker.assert_no_high_risk_patterns(source, policy)
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise EvidenceError("EVIDENCE_PRIVACY_PREFLIGHT_REJECTED") from exc
    adapter = _load("sovia_n8n_sanitized.py", "_sovia_evidence_sanitized")
    try:
        source_digest = adapter.canonical_sha256(source)
        policy_digest = adapter.canonical_sha256(policy)
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise EvidenceError("EVIDENCE_HASH_UNAVAILABLE") from exc
    if (not hmac.compare_digest(source_digest, manifest["source_sha256"]) or
            not hmac.compare_digest(policy_digest, manifest["policy_sha256"])):
        raise EvidenceError("SOURCE_OR_POLICY_DIGEST_MISMATCH")
    bridge = _load("sovia_n8n_execution_bridge.py", "_sovia_evidence_bridge")
    try:
        canonical = bridge.convert_synthetic(source, policy)
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise EvidenceError("EVIDENCE_CONVERSION_REJECTED") from exc
    try:
        checker.assert_no_high_risk_patterns(canonical)
        canonical_digest = adapter.canonical_sha256(canonical)
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise EvidenceError("CANONICAL_EVIDENCE_PRIVACY_OR_HASH_REJECTED") from exc
    if not hmac.compare_digest(canonical_digest, manifest["expected_canonical_sha256"]):
        raise EvidenceError("CANONICAL_DIGEST_MISMATCH")
    return {
        "status": "SYNTHETIC_DIGESTS_AND_PATTERN_CHECKS_CONSISTENT_UNVERIFIED",
        "pinned_release_tag": tag,
        "event_count": len(canonical["events"]),
        "source_digest_matches": True,
        "policy_digest_matches": True,
        "canonical_digest_matches": True,
        "known_pattern_preflight_executed": True,
        "manifest_signature_verified": False,
        "provenance_independently_authenticated": False,
        "synthetic_origin_independently_verified": False,
        "customer_authorization_verified": False,
        "pii_absence_proven": False,
        "n8n_instance_or_version_verified": False,
        "n8n_api_called": False,
        "file_write_performed": False,
    }


def verify_files(source_path, policy_path, manifest_path):
    audit = _load("sovia_audit.py", "_sovia_evidence_reader")
    for raw in (source_path, policy_path, manifest_path):
        if Path(raw).is_symlink():
            raise EvidenceError("SYMLINK_INPUT_NOT_ALLOWED")
    try:
        source = audit.read_document(source_path)
        policy = audit.read_document(policy_path)
        manifest = audit.read_document(manifest_path)
    except (ValueError, TypeError, OSError, RecursionError, OverflowError) as exc:
        raise EvidenceError("EVIDENCE_INPUT_REJECTED") from exc
    return verify(source, policy, manifest)


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only, synthetic-only SHA256 and metadata pattern check")
    p.add_argument("--input", required=True, help="fabricated execution summary and sanitized steps only")
    p.add_argument("--policy", required=True)
    p.add_argument("--manifest", required=True, help="self-claimed unsigned synthetic evidence manifest")
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ACK_REQUIRED"}), file=sys.stderr)
        return 2
    try:
        result = verify_files(args.input, args.policy, args.manifest)
    except EvidenceError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
