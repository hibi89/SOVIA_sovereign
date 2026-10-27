"""Strict offline SOVIA adapter for pre-sanitized, n8n-like synthetic metadata.

NOT an n8n API client or a parser for raw n8n execution exports.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
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


def convert_paths(source, policy_path, output):
    """Read only explicitly supplied files; publish one NEW output atomically."""
    audit = _audit()
    src, pol = Path(source).resolve(), Path(policy_path).resolve()
    target = Path(os.path.abspath(output))
    if target.resolve() in (src, pol):
        raise ContractError("OUTPUT_ALIASES_INPUT")
    if not target.parent.is_dir():
        raise ContractError("OUTPUT_DIRECTORY_MISSING")
    try:
        doc = audit.read_document(src)
        policy_doc = audit.read_document(pol)
        canonical = convert(doc, policy_doc)
        payload = json.dumps(canonical, ensure_ascii=False, indent=2)
        audit.write_reports_atomically([(target, payload)])
    except (ValueError, OSError, TypeError, OverflowError) as exc:
        if isinstance(exc, ContractError):
            raise
        raise ContractError("INPUT_OR_OUTPUT_REJECTED") from exc
    return len(canonical["events"])


def main(argv=None):
    p = argparse.ArgumentParser(description="Offline pre-sanitized n8n-like metadata to SOVIA canonical JSON")
    p.add_argument("--input", required=True)
    p.add_argument("--policy", required=True)
    p.add_argument("--output", required=True, help="NEW unused local JSON file")
    args = p.parse_args(argv)
    try:
        count = convert_paths(args.input, args.policy, args.output)
    except ContractError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps({"status": "CONVERTED_SYNTHETIC_CONTRACT_ONLY",
                      "events": count, "independent_evidence_verified": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
