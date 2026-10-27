"""Offline advisory comparison of synthetic LA plan and sanitized observations.

No LA runtime integration, consent verification or execution authorization.
"""
from __future__ import annotations
from collections import Counter
from sovia_la_plan_preflight import FORMAT, PlanReviewError, _code, _optional, _domain, assess

OBS_FORMAT = "sovia.observation.v1"
STATES = {"observed", "failed", "unknown"}
FIELDS = {"step_id", "tool_code", "side_effect", "target_code", "destination_domain", "state", "evidence_ref"}

def reconcile(plan, policy, observations):
    prior = assess(plan, policy)
    if (type(observations) is not dict or set(observations) != {"schema_version", "plan_ref", "observations"}
            or observations["schema_version"] != OBS_FORMAT
            or observations["plan_ref"] != plan["plan_ref"]):
        raise PlanReviewError("INVALID_OBSERVATION_ENVELOPE")
    rows = observations["observations"]
    if type(rows) is not list or len(rows) > 256:
        raise PlanReviewError("INVALID_OBSERVATIONS")
    from sovia_pii_preflight import assert_no_high_risk_patterns
    try:
        assert_no_high_risk_patterns(observations)
    except ValueError as exc:
        raise PlanReviewError("OBSERVATION_METADATA_PREFLIGHT_REJECTED") from exc
    planned = {s["step_id"]: s for s in plan["steps"]}
    seen, findings = set(), []
    def flag(step, rule):
        findings.append({"step_id": step, "rule_id": rule, "evidence_verified": False})
    for row in rows:
        if type(row) is not dict or not {"step_id", "tool_code", "side_effect", "state"}.issubset(row) or set(row) - FIELDS:
            raise PlanReviewError("INVALID_OBSERVATION_FIELDS")
        sid = _code(row["step_id"])
        if sid in seen:
            raise PlanReviewError("DUPLICATE_OBSERVATION_STEP")
        seen.add(sid)
        tool = _code(row["tool_code"])
        effect = row["side_effect"]
        if type(effect) is not str or effect not in {"none", "local_write", "external_send", "destructive", "payment", "unknown"}:
            raise PlanReviewError("INVALID_OBSERVATION_EFFECT")
        state = row["state"]
        if type(state) is not str or state not in STATES:
            raise PlanReviewError("INVALID_OBSERVATION_STATE")
        target = _optional(row.get("target_code"))
        destination = _optional(row.get("destination_domain"), domain=True)
        evidence = _optional(row.get("evidence_ref"))
        if sid not in planned:
            flag(sid, "UNPLANNED_OBSERVED_STEP")
        else:
            expected = planned[sid]
            if tool != expected["tool_code"]:
                flag(sid, "TOOL_MISMATCH")
            if effect != expected["side_effect"]:
                flag(sid, "SIDE_EFFECT_MISMATCH")
            if target != expected.get("target_code"):
                flag(sid, "TARGET_MISMATCH")
            if destination != _optional(expected.get("destination_domain"), domain=True):
                flag(sid, "DESTINATION_MISMATCH")
        if state == "unknown":
            flag(sid, "OBSERVATION_STATE_UNKNOWN")
        if state == "observed" and evidence is None:
            flag(sid, "OBSERVED_EVIDENCE_MISSING")
    for sid in planned:
        if sid not in seen:
            flag(sid, "PLANNED_STEP_NOT_OBSERVED")
    return {
        "schema_version": "sovia.plan_observation_review.v1",
        "plan_fingerprint_sha256": prior["plan_fingerprint_sha256"],
        "planned_count": len(planned), "observation_count": len(rows),
        "finding_count": len(findings), "findings": findings,
        "preflight_finding_count": prior["finding_count"],
        "execution_authorized": False, "evidence_authenticated": False,
        "real_la_integration_verified": False,
        "coverage_limits": ["OBSERVATIONS_ARE_UNAUTHENTICATED_ASSERTIONS", "ABSENCE_DOES_NOT_PROVE_NON_EXECUTION"],
    }
