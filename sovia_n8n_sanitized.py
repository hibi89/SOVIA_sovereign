"""Strict offline SOVIA adapter for pre-sanitized, n8n-like synthetic metadata.

NOT an n8n API client or a parser for raw n8n execution exports.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import hmac
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import stat
import sys

FORMAT = "sovia.n8n_sanitized.v1"
CODE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
MAX_STEPS = 1000
FIELDS = frozenset({
    "step_id", "occurred_at_utc", "tool_code", "target_code",
    "destination_domain", "permission_asserted", "outcome_code", "evidence_ref",
})
POLICY_KEYS = frozenset({
    "allowed_tools", "approved_destinations", "sensitive_targets",
    "max_tool_calls_per_minute",
})


class ContractError(ValueError):
    """No raw untrusted value/path in user-facing errors."""


def _audit():
    # Python -I omits the script directory from sys.path. Load ONLY sibling code.
    path = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_contract_audit", path)
    if spec is None or spec.loader is None:
        raise ContractError("AUDIT_MODULE_UNAVAILABLE")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _code(value, field):
    if type(value) is not str or CODE.fullmatch(value) is None:
        raise ContractError("INVALID_" + field.upper())
    return value


def _optional_code(value, field):
    return None if value is None else _code(value, field)


def convert(document, policy_document):
    """Fail closed on unsupported fields; never copy raw node params/items."""
    if type(document) is not dict or set(document) != {
        "format", "workflow_id", "execution_id", "steps",
    } or document["format"] != FORMAT:
        raise ContractError("UNSUPPORTED_SANITIZED_ENVELOPE")
    if type(policy_document) is not dict or set(policy_document) != {
        "schema_version", "policy",
    } or policy_document["schema_version"] != "1.0":
        raise ContractError("INVALID_POLICY_ENVELOPE")
    policy = policy_document["policy"]
    if type(policy) is not dict or set(policy) - POLICY_KEYS:
        raise ContractError("INVALID_POLICY_KEYS")
    workflow = _code(document["workflow_id"], "workflow_id")
    execution = _code(document["execution_id"], "execution_id")
    steps = document["steps"]
    if type(steps) is not list or len(steps) > MAX_STEPS:
        raise ContractError("INVALID_STEPS")
    events = []
    seen = set()
    for step in steps:
        if type(step) is not dict or set(step) - FIELDS or not {
            "step_id", "occurred_at_utc", "tool_code",
        }.issubset(step):
            raise ContractError("UNSUPPORTED_STEP_FIELDS")
        sid = _code(step["step_id"], "step_id")
        if sid in seen:
            raise ContractError("DUPLICATE_STEP_ID")
        seen.add(sid)
        tool = _code(step["tool_code"], "tool_code")
        target = _optional_code(step.get("target_code"), "target_code")
        evidence = _optional_code(step.get("evidence_ref"), "evidence_ref")
        outcome = step.get("outcome_code")
        if outcome is not None and outcome not in ("success", "error", "unknown"):
            raise ContractError("INVALID_OUTCOME_CODE")
        permission = step.get("permission_asserted")
        if permission is not None and type(permission) is not bool:
            raise ContractError("INVALID_PERMISSION_ASSERTION")
        domain = step.get("destination_domain")
        if domain is not None and (type(domain) is not str or len(domain) > 200):
            raise ContractError("INVALID_DOMAIN")
        events.append({
            "event_id": sid,
            "occurred_at_utc": step["occurred_at_utc"],
            "agent_id": workflow,
            "run_id": execution,
            "tool_name": tool,
            "target": target,
            "destination_domain": domain,
            "permission_asserted": permission,
            "outcome": outcome,
            "source_pointer": evidence,
        })
    canonical = {"schema_version": "1.0", "policy": policy, "events": events}
    try:
        # Reuse the real canonical evaluator, including UTC/domain/policy checks.
        _audit().evaluate(canonical)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ContractError("CANONICAL_VALIDATION_FAILED") from exc
    return canonical


ATTESTATION_KEYS = frozenset({
    "schema_version", "scope", "source_sha256", "policy_sha256",
    "source_authorized", "fields_reviewed", "retention_plan_documented",
    "expires_utc",
})


def canonical_sha256(document):
    """Hash the exact already-parsed content used in the subsequent conversion."""
    try:
        data = json.dumps(
            document, sort_keys=True, ensure_ascii=False,
            separators=(",", ":"), allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, RecursionError, OverflowError) as exc:
        raise ContractError("UNHASHABLE_DOCUMENT") from exc
    return hashlib.sha256(data).hexdigest()


def verify_operator_attestation(attestation, source_document, policy_document, *, now=None):
    """Verify operator *claims* and document binding; not genuine legal authorization."""
    if type(attestation) is not dict or set(attestation) != ATTESTATION_KEYS:
        raise ContractError("INVALID_ATTESTATION_FIELDS")
    if (attestation["schema_version"] != "1.0" or
            attestation["scope"] != "locally_reviewed_metadata"):
        raise ContractError("INVALID_ATTESTATION_SCOPE")
    for field in ("source_authorized", "fields_reviewed", "retention_plan_documented"):
        if attestation[field] is not True:
            raise ContractError("MISSING_OPERATOR_ACKNOWLEDGEMENT")
    for field, document in (("source_sha256", source_document),
                            ("policy_sha256", policy_document)):
        digest = attestation[field]
        if (type(digest) is not str or
                re.fullmatch(r"[a-f0-9]{64}", digest) is None or
                not hmac.compare_digest(digest, canonical_sha256(document))):
            raise ContractError("ATTESTATION_DIGEST_MISMATCH")
    expires = attestation["expires_utc"]
    if (type(expires) is not str or
            re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", expires) is None):
        raise ContractError("INVALID_ATTESTATION_EXPIRY")
    try:
        until = datetime.fromisoformat(expires.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("INVALID_ATTESTATION_EXPIRY") from exc
    instant = datetime.now(timezone.utc) if now is None else now
    if not isinstance(instant, datetime) or instant.tzinfo is None:
        raise ContractError("INVALID_CLOCK")
    utc_now = instant.astimezone(timezone.utc)
    if until <= utc_now:
        raise ContractError("ATTESTATION_EXPIRED")
    if until - utc_now > timedelta(days=30):
        raise ContractError("ATTESTATION_TOO_LONG_LIVED")
    return "OPERATOR_CLAIMS_PRESENT_NOT_INDEPENDENTLY_VERIFIED"


def _guard_approved_local_path(path, *, output_parent=False):
    """Reject symlink/reparse ancestors without reading local source contents.

    Checks are best-effort metadata snapshots, NOT race-free confinement.
    Only the approved-local mode uses this conservative guard.
    """
    root = path.parent if output_parent else path
    reparse = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
    try:
        for component in (root, *root.parents):
            entry = component.stat(follow_symlinks=False)
            if (stat.S_ISLNK(entry.st_mode) or
                    bool(getattr(entry, "st_file_attributes", 0) & reparse)):
                raise ContractError("LINKED_LOCAL_PATH_REFUSED")
            if component == root:
                expected = stat.S_ISDIR if output_parent else stat.S_ISREG
                if not expected(entry.st_mode):
                    raise ContractError("INVALID_LOCAL_PATH_TYPE")
        if output_parent:
            try:
                # A leaf file must never be reused (even a dangling link).
                path.lstat()
            except FileNotFoundError:
                pass
            else:
                raise ContractError("OUTPUT_ALREADY_EXISTS")
    except OSError as exc:
        raise ContractError("LOCAL_PATH_UNAVAILABLE") from exc


def convert_paths(source, policy_path, output, *, mode="synthetic", attestation_path=None):
    """Read only explicitly supplied files; publish one NEW output atomically."""
    if mode not in ("synthetic", "approved-local"):
        raise ContractError("INVALID_MODE")
    if (mode == "approved-local") != (attestation_path is not None):
        raise ContractError("ATTESTATION_REQUIRED_ONLY_FOR_APPROVED_LOCAL")
    try:
        target = Path(os.path.abspath(output))
        if mode == "approved-local":
            # Do NOT resolve input before checking lexical ancestors. Resolve
            # would hide a junction/symlink which redirected a supposedly
            # reviewed source, policy or attestation to another location.
            src, pol = Path(os.path.abspath(source)), Path(os.path.abspath(policy_path))
            attest = Path(os.path.abspath(attestation_path))
            same = lambda a, b: os.path.normcase(os.fspath(a)) == os.path.normcase(os.fspath(b))
            if any(same(target, p) for p in (src, pol, attest)):
                raise ContractError("OUTPUT_ALIASES_INPUT")
            for item in (src, pol, attest):
                _guard_approved_local_path(item)
            _guard_approved_local_path(target, output_parent=True)
        else:
            src, pol = Path(source).resolve(), Path(policy_path).resolve()
            attest = None
            if target.resolve() in (src, pol):
                raise ContractError("OUTPUT_ALIASES_INPUT")
    except (OSError, TypeError, ValueError, RuntimeError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError("LOCAL_PATH_UNAVAILABLE") from exc
    if not target.parent.is_dir():
        raise ContractError("OUTPUT_DIRECTORY_MISSING")
    audit = _audit()
    try:
        doc = audit.read_document(src)
        policy_doc = audit.read_document(pol)
        canonical = convert(doc, policy_doc)
        if attest is not None:
            # Fail closed before publishing canonical metadata; synthetic mode
            # stays backwards-compatible with existing public demo fixtures.
            preflight_path = Path(__file__).resolve().with_name("sovia_pii_preflight.py")
            spec = spec_from_file_location("_sovia_local_pii_preflight", preflight_path)
            if spec is None or spec.loader is None:
                raise ContractError("PREFLIGHT_MODULE_UNAVAILABLE")
            checker = module_from_spec(spec)
            try:
                spec.loader.exec_module(checker)
                checker.assert_no_high_risk_patterns(doc, policy_doc)
            except (OSError, ImportError) as exc:
                raise ContractError("PREFLIGHT_MODULE_UNAVAILABLE") from exc
            except ValueError as exc:
                raise ContractError("PREFLIGHT_REJECTED") from exc
            manifest = audit.read_document(attest)
            verify_operator_attestation(manifest, doc, policy_doc)
        payload = json.dumps(canonical, ensure_ascii=False, indent=2)
        audit.write_reports_atomically([(target, payload)])
    except (ValueError, OSError, TypeError, OverflowError, RecursionError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError("INPUT_OR_OUTPUT_REJECTED") from exc
    return len(canonical["events"])


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline pre-sanitized n8n-like metadata to SOVIA canonical JSON")
    p.add_argument("--input", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--output", required=True, help="NEW unused local JSON file")
    p.add_argument("--mode", choices=("synthetic", "approved-local"), default="synthetic",
                   help="Default synthetic only; approved-local requires operator attestation")
    p.add_argument("--attestation", help="Local operator-claim manifest (approved-local only)")
    args = p.parse_args(argv)
    try:
        count = convert_paths(args.input, args.policy, args.output,
                              mode=args.mode, attestation_path=args.attestation)
    except ContractError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({
        "status": ("CONVERTED_SYNTHETIC_CONTRACT_ONLY" if args.mode == "synthetic"
                   else "CONVERTED_WITH_UNVERIFIED_OPERATOR_CLAIMS"),
        "events": count, "independent_evidence_verified": False,
        "authorization_independently_verified": False,
        "pii_pattern_scan_executed": args.mode == "approved-local",
        "pii_absence_proven": False,
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
