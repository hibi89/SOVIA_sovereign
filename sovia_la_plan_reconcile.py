"""Read-only cross-check of synthetic planned LA facts against SOVIA observations.

This is an internal *prototype of the correlation contract*, not an actual
Lightning Azent runtime/receipt adapter, complete telemetry, or live approval.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


class ReconcileError(ValueError):
    """Opaque rejection; raw local input is never logged by this command."""


def _local(filename, alias):
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise ReconcileError("COMPONENT_MISSING")
    mod = module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except (ImportError, OSError) as exc:
        raise ReconcileError("COMPONENT_MISSING") from exc
    return mod


def reconcile(plan_doc, policy_doc, observed_doc):
    """Correlate sanitized IDs in memory; do not assume missing=not executed."""
    plan_engine = _local("sovia_la_plan_preflight.py", "_sovia_la_planning")
    audit_core = _local("sovia_audit.py", "_sovia_la_event_schema")
    audit_engine = _local("sovia_audit_v012.py", "_sovia_la_post_audit")
    preflight = _local("sovia_pii_preflight.py", "_sovia_la_observed_privacy")
    planned = plan_engine.assess(plan_doc, policy_doc)

    # A canonical evaluator alone would accept unknown top-level/step keys.
    # Reject those BEFORE evaluation to avoid silently dropping raw payloads.
    if (type(observed_doc) is not dict or
            set(observed_doc) != {"schema_version", "policy", "events"} or
            observed_doc["schema_version"] != "1.0" or
            type(observed_doc["policy"]) is not dict or
            type(observed_doc["events"]) is not list or
            len(observed_doc["events"]) > 1000 or
            set(observed_doc["policy"]) - plan_engine.POLICY_KEYS):
        raise ReconcileError("UNSUPPORTED_OBSERVATION_ENVELOPE")
    if observed_doc["policy"] != policy_doc["policy"]:
        raise ReconcileError("OBSERVATION_POLICY_MISMATCH")
    for event in observed_doc["events"]:
        if type(event) is not dict or set(event) - set(audit_core.EVENT_KEYS):
            raise ReconcileError("RAW_OR_UNKNOWN_EVENT_FIELDS_REFUSED")
    try:
        preflight.assert_no_high_risk_patterns(observed_doc)
        audited = audit_engine.evaluate(observed_doc, legacy_audit=audit_core)
    except (ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        raise ReconcileError("OBSERVATION_REJECTED") from exc

    step_by_id = {step["step_id"]: step for step in plan_doc["steps"]}
    observed_by_id = {event["event_id"]: event for event in audited["events"]}
    findings = []

    def flag(identifier, rule_id, severity="HIGH"):
        # These fields are from the already validated allowlisted event/step ID
        # contract, not private payload/actual source references.
        findings.append({
            "step_or_event_id": identifier,
            "rule_id": rule_id,
            "severity": severity,
            "evidence_not_authenticated": True,
        })

    for step_id, step in step_by_id.items():
        event = observed_by_id.get(step_id)
        if event is None:
            flag(step_id, "PLANNED_STEP_NOT_OBSERVED", "UNKNOWN")
            continue
        if step["tool_code"].lower() != event["tool_name"].lower():
            flag(step_id, "OBSERVED_TOOL_DIFFERS_FROM_PLAN")
        plan_dest = plan_engine._domain(step.get("destination_domain"))
        if plan_dest != event["destination_domain"]:
            flag(step_id, "OBSERVED_DESTINATION_DIFFERS_FROM_PLAN")
        if step.get("target_code") != event["target"]:
            flag(step_id, "OBSERVED_TARGET_DIFFERS_FROM_PLAN")
        if step.get("permission_asserted") != event["permission_asserted"]:
            flag(step_id, "OBSERVED_PERMISSION_CLAIM_DIFFERS_FROM_PLAN")
        if not event["source_pointer"]:
            flag(step_id, "OBSERVATION_EVIDENCE_POINTER_MISSING", "UNKNOWN")
    for event_id in observed_by_id.keys() - step_by_id.keys():
        flag(event_id, "OBSERVED_EVENT_NOT_IN_PLAN")
    # These summary counts do not authenticate logs, distinguish skipped from
    # unobserved, or prove absence of other external side effects.
    return {
        "schema_version": "sovia.plan_observation_reconcile.v1",
        "status": ("SYNTHETIC_REVIEW_REQUIRED" if findings else
                   "SYNTHETIC_MATCH_NOT_AUTHENTICATED"),
        "plan_fingerprint_sha256": planned["plan_fingerprint_sha256"],
        "planned_steps": planned["step_count"],
        "observed_events": audited["event_count"],
        "matched_step_ids": len(step_by_id.keys() & observed_by_id.keys()),
        "plan_risk_finding_count": planned["finding_count"],
        "post_audit_finding_count": audited["finding_count"],
        "reconciliation_finding_count": len(findings),
        "reconciliation_findings": sorted(
            findings, key=lambda f: (f["step_or_event_id"], f["rule_id"])
        ),
        "coverage_limits": [
            "OBSERVED_RECORDS_NOT_AUTHENTICATED_OR_COMPLETE",
            "MISSING_STEP_NOT_PROVEN_FAILED_OR_NOT_EXECUTED",
            "EVENT_ID_EQUALS_STEP_ID_ONLY_BY_SYNTHETIC_CONTRACT",
            "NO_REAL_LA_RUNTIME_OR_APPROVAL_INTEGRATION",
        ],
        "execution_authorized": False,
        "real_la_integration_verified": False,
        "observation_completeness_verified": False,
        "approval_identity_verified": False,
        "source_payload_persisted_by_this_command": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Synthetic offline LA plan/observation risk comparison")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--policy", required=True)
    parser.add_argument("--observations", required=True)
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        core = _local("sovia_audit.py", "_sovia_la_reconcile_reader")
        result = reconcile(core.read_document(args.plan),
                           core.read_document(args.policy),
                           core.read_document(args.observations))
    except (ValueError, TypeError, OSError, KeyError, OverflowError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, ReconcileError) else "RECONCILIATION_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
