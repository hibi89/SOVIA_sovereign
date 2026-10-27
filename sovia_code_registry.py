"""Offline, synthetic-only explicit code registry; never accepts raw n8n exports.

Maps pre-sanitized tool and target *codes*, including corresponding policy
entries. No automatic anonymization, exemptions, consent or PII certification.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import re
import sys

FORMAT = "sovia.safe_code_registry.v1"
SAFE_CODE = re.compile(r"^[a-z][a-z0-9_.:-]{0,79}$")
MAX_ALIASES = 1000


class RegistryError(ValueError):
    """Machine-readable fixed error codes; never echo source values or paths."""


def _sibling(module_name):
    path = Path(__file__).resolve().with_name(module_name + ".py")
    spec = spec_from_file_location("_sovia_registry_" + module_name, path)
    if spec is None or spec.loader is None:
        raise RegistryError("REGISTRY_DEPENDENCY_MISSING")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (ImportError, OSError) as exc:
        raise RegistryError("REGISTRY_DEPENDENCY_MISSING") from exc
    return module


def _checked_mapping(mapping):
    if type(mapping) is not dict or len(mapping) > MAX_ALIASES:
        raise RegistryError("INVALID_REGISTRY_MAP")
    used = set()
    result = {}
    for alias, standard in mapping.items():
        if (type(alias) is not str or type(standard) is not str or
                SAFE_CODE.fullmatch(alias) is None or
                SAFE_CODE.fullmatch(standard) is None):
            raise RegistryError("INVALID_REGISTRY_CODE")
        if standard in used:
            raise RegistryError("NON_INJECTIVE_REGISTRY_MAP")
        used.add(standard)
        result[alias] = standard
    return result


def _map(mapping, code):
    if type(code) is not str or code not in mapping:
        raise RegistryError("UNREGISTERED_METADATA_CODE")
    return mapping[code]


def standardize(source, policy, registry):
    """Return canonical audit JSON only when policy findings are preserved.

    The caller must provide exclusively synthetic, pre-sanitized metadata.
    A registry never overrides the preflight or creates authorization.
    """
    adapter = _sibling("sovia_n8n_sanitized")
    checker = _sibling("sovia_pii_preflight")
    if (type(registry) is not dict or
            set(registry) != {"schema_version", "kind", "tool_codes", "target_codes"} or
            registry["schema_version"] != "1.0" or registry["kind"] != FORMAT):
        raise RegistryError("INVALID_REGISTRY_ENVELOPE")
    tools = _checked_mapping(registry["tool_codes"])
    targets = _checked_mapping(registry["target_codes"])
    if not tools:
        raise RegistryError("EMPTY_TOOL_REGISTRY")
    try:
        checker.assert_no_high_risk_patterns(source, policy, registry)
    except ValueError as exc:
        raise RegistryError("REGISTRY_PRIVACY_PREFLIGHT_REJECTED") from exc
    try:
        original = adapter.convert(source, policy)
    except (ValueError, TypeError, RecursionError) as exc:
        raise RegistryError("REGISTRY_INPUT_REJECTED") from exc

    # Work on a fresh allowlisted projection only: no raw document copying.
    mapped_policy = dict(policy["policy"])
    for key, table in (("allowed_tools", tools), ("sensitive_targets", targets)):
        if key in mapped_policy and mapped_policy[key] is not None:
            if type(mapped_policy[key]) is not list:
                raise RegistryError("REGISTRY_POLICY_REJECTED")
            mapped_policy[key] = [_map(table, code) for code in mapped_policy[key]]
    mapped_events = []
    for event in original["events"]:
        mapped = dict(event)
        mapped["tool_name"] = _map(tools, event["tool_name"])
        if event["target"] is not None:
            mapped["target"] = _map(targets, event["target"])
        mapped_events.append(mapped)
    # The adapter validates source rules. The audit engine also validates the
    # transformed canonical report and independently recomputes risk findings.
    canonical = {"schema_version": "1.0", "policy": mapped_policy,
                 "events": mapped_events}
    # Validate transformed metadata too; a registry never bypasses preflight.
    try:
        checker.assert_no_high_risk_patterns(canonical)
    except ValueError as exc:
        raise RegistryError("REGISTRY_PRIVACY_PREFLIGHT_REJECTED") from exc
    audit = adapter._audit()
    try:
        initial_report = audit.evaluate(original)
        final_report = audit.evaluate(canonical)
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise RegistryError("REGISTRY_AUDIT_REJECTED") from exc
    def findings(report):
        return sorted((f["rule_id"], tuple(f["event_ids"]), f["severity"])
                      for f in report["findings"])
    if (findings(initial_report) != findings(final_report) or
            initial_report["coverage_limits"] != final_report["coverage_limits"]):
        raise RegistryError("AUDIT_FINDING_DRIFT")
    return canonical


def standardize_files(source, policy, registry, output):
    """Publish a single NEW canonical JSON. Originals and registry are read-only."""
    src, pol, reg = (Path(p).resolve() for p in (source, policy, registry))
    target = Path(os.path.abspath(output))
    if target.resolve() in (src, pol, reg):
        raise RegistryError("OUTPUT_ALIASES_INPUT")
    if not target.parent.is_dir():
        raise RegistryError("OUTPUT_DIRECTORY_MISSING")
    adapter = _sibling("sovia_n8n_sanitized")
    audit = adapter._audit()
    try:
        source_data = audit.read_document(src)
        policy_data = audit.read_document(pol)
        registry_data = audit.read_document(reg)
        canonical = standardize(source_data, policy_data, registry_data)
        payload = json.dumps(canonical, ensure_ascii=False, indent=2, allow_nan=False)
        audit.write_reports_atomically([(target, payload)])
    except RegistryError:
        raise
    except (ValueError, TypeError, OSError, RecursionError, OverflowError) as exc:
        raise RegistryError("REGISTRY_INPUT_OUTPUT_REJECTED") from exc
    return {"events": len(canonical["events"]),
            "status": "SYNTHETIC_CODE_MAPPING_ONLY",
            "audit_findings_preserved": True,
            "privacy_absence_proven": False,
            "customer_authorization_verified": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA synthetic code registry transform")
    parser.add_argument("--input", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--registry", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--synthetic-only", action="store_true",
                        help="Required: no real customer data or permission assertion")
    args = parser.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ONLY_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        result = standardize_files(args.input, args.policy, args.registry, args.output)
    except RegistryError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
