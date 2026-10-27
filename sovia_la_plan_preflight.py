"""Independent SOVIA pre-execution review of *sanitized synthetic* LA-facing facts.

No raw LA IR, prompts, node arguments, credentials, execution, or runtime gate.
All findings are advisory; a clear plan never constitutes execution approval.
"""
from __future__ import annotations
import argparse
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

FORMAT = "sovia.plan_review.v1"
CODE = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
DOMAIN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$")
STEP_KEYS = {"step_id", "tool_code", "side_effect", "target_code",
             "destination_domain", "permission_asserted", "approval_ref"}
POLICY_KEYS = {"allowed_tools", "approved_destinations", "sensitive_targets",
               "max_tool_calls_per_minute"}
SIDE_EFFECTS = {"none", "local_write", "external_send", "destructive",
                "payment", "unknown"}


class PlanReviewError(ValueError):
    """Only opaque, non-disclosing refusal codes."""


def _module(name):
    path = Path(__file__).resolve().with_name(name)
    spec = spec_from_file_location("_sovia_plan_" + name.replace(".", "_"), path)
    if spec is None or spec.loader is None:
        raise PlanReviewError("DEPENDENCY_MISSING")
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _code(value):
    if type(value) is not str or CODE.fullmatch(value) is None:
        raise PlanReviewError("INVALID_PLAN_CODE")
    return value


def _domain(value):
    if value is None:
        return None
    if type(value) is not str or len(value) > 253:
        raise PlanReviewError("INVALID_DESTINATION")
    result = value.lower()
    if ".." in result or DOMAIN.fullmatch(result) is None:
        raise PlanReviewError("INVALID_DESTINATION")
    return result


def _optional(value, domain=False):
    if value is None:
        return None
    return _domain(value) if domain else _code(value)


def _policy_set(value, domain=False):
    if value is None:
        return None
    if type(value) is not list or len(value) > 1000:
        raise PlanReviewError("INVALID_PLAN_POLICY")
    items = [(_domain(v) if domain else _code(v).lower()) for v in value]
    if None in items or len(set(items)) != len(items):
        raise PlanReviewError("INVALID_PLAN_POLICY")
    return set(items)


def assess(plan, policy_doc):
    if (type(plan) is not dict or set(plan) !=
            {"schema_version", "plan_ref", "steps"} or
            plan["schema_version"] != FORMAT):
        raise PlanReviewError("INVALID_PLAN_ENVELOPE")
    reference = _code(plan["plan_ref"])
    steps = plan["steps"]
    if type(steps) is not list or not 1 <= len(steps) <= 256:
        raise PlanReviewError("INVALID_PLAN_STEPS")
    if (type(policy_doc) is not dict or
            set(policy_doc) != {"schema_version", "policy"} or
            policy_doc["schema_version"] != "1.0" or
            type(policy_doc["policy"]) is not dict or
            set(policy_doc["policy"]) - POLICY_KEYS):
        raise PlanReviewError("INVALID_PLAN_POLICY")
    policy = policy_doc["policy"]
    allowed = _policy_set(policy.get("allowed_tools"))
    domains = _policy_set(policy.get("approved_destinations"), domain=True)
    sensitive = _policy_set(policy.get("sensitive_targets"))
    quota = policy.get("max_tool_calls_per_minute")
    if quota is not None and (type(quota) is not int or not 1 <= quota <= 1000):
        raise PlanReviewError("INVALID_PLAN_POLICY")
    try:
        _module("sovia_pii_preflight.py").assert_no_high_risk_patterns(plan, policy_doc)
    except ValueError as exc:
        raise PlanReviewError("PLAN_METADATA_PREFLIGHT_REJECTED") from exc

    findings, normalized, seen = [], [], set()
    unknown = ["PROVENANCE_AND_APPROVAL_NOT_AUTHENTICATED",
               "RUNTIME_POLICY_NOT_ENFORCED",
               "BURST_LIMIT_NOT_EVALUABLE_PRE_EXECUTION"]
    if allowed is None:
        unknown.append("TOOL_POLICY_NOT_PROVIDED")
    if domains is None:
        unknown.append("DESTINATION_POLICY_NOT_PROVIDED")
    if sensitive is None:
        unknown.append("SENSITIVE_POLICY_NOT_PROVIDED")

    def add(sid, rule, severity="HIGH"):
        findings.append({"step_id": sid, "rule_id": rule,
                         "severity": severity, "evidence_verified": False})

    for step in steps:
        if (type(step) is not dict or
                not {"step_id", "tool_code", "side_effect"}.issubset(step) or
                set(step) - STEP_KEYS):
            raise PlanReviewError("UNSUPPORTED_STEP_FIELDS")
        sid, tool = _code(step["step_id"]), _code(step["tool_code"])
        if sid in seen:
            raise PlanReviewError("DUPLICATE_STEP_ID")
        seen.add(sid)
        effect = step["side_effect"]
        if type(effect) is not str or effect not in SIDE_EFFECTS:
            raise PlanReviewError("INVALID_SIDE_EFFECT")
        target = _optional(step.get("target_code"))
        destination = _optional(step.get("destination_domain"), domain=True)
        approval = _optional(step.get("approval_ref"))
        permission = step.get("permission_asserted")
        if permission is not None and type(permission) is not bool:
            raise PlanReviewError("INVALID_PERMISSION_ASSERTION")
        normalized.append({"step_id": sid, "tool_code": tool,
                           "side_effect": effect, "target_code": target,
                           "destination_domain": destination,
                           "approval_ref": approval,
                           "permission_asserted": permission})
        if allowed is not None and tool.lower() not in allowed:
            add(sid, "UNAUTHORIZED_PLANNED_TOOL")
        if destination is not None and domains is not None and destination not in domains:
            add(sid, "UNAPPROVED_PLANNED_DESTINATION")
        if (sensitive is not None and target is not None and
                target.lower() in sensitive and
                (permission is not True or approval is None)):
            add(sid, "SENSITIVE_PLANNED_TARGET_REVIEW")
        if effect in ("local_write", "external_send", "destructive", "payment"):
            add(sid, "SIDE_EFFECT_REQUIRES_INDEPENDENT_APPROVAL",
                "CRITICAL" if effect in ("destructive", "payment") else "HIGH")
        if effect == "unknown":
            add(sid, "UNCLASSIFIED_SIDE_EFFECT")
        if effect == "external_send" and destination is None:
            add(sid, "EXTERNAL_DESTINATION_NOT_DISCLOSED")
    digest = hashlib.sha256(json.dumps(
        {"plan_ref": reference, "steps": normalized, "policy": policy},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False).encode("utf-8")).hexdigest()
    return {
        "schema_version": FORMAT,
        "status": "FINDINGS_REVIEW_REQUIRED" if findings else "NO_FINDINGS_STILL_UNVERIFIED",
        "plan_fingerprint_sha256": digest, "step_count": len(steps),
        "finding_count": len(findings), "findings": findings,
        "coverage_limits": unknown, "execution_authorized": False,
        "approval_identity_verified": False, "real_la_integration_verified": False,
        "runtime_policy_enforced": False, "offline_only": True,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline sanitized LA plan review, synthetic only")
    parser.add_argument("--input", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        reader = _module("sovia_audit.py")
        result = assess(reader.read_document(args.input),
                        reader.read_document(args.policy))
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        error = str(exc) if isinstance(exc, PlanReviewError) else "PLAN_REVIEW_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": error}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
