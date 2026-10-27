"""Offline read-only retention *review planning*, never data disposal.

Uses the existing metadata-only inventory. Thresholds are review prompts,
not legal expiration, and operator hold/backup declarations are unverified.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys
import time

POLICY_SCHEMA = "sovia.retention_review.v1"
CATEGORIES = frozenset({
    "source_or_export", "rendered_report", "history_or_backup",
    "history_sidecar", "package_or_checksum",
})
LEGAL_HOLD = frozenset({"unknown", "present_claimed", "none_claimed"})
BACKUP = frozenset({"unknown", "reviewed_claimed"})
MAX_REVIEW_DAYS = 36500


class ReviewError(ValueError):
    """Only predeclared non-disclosing refusal codes."""


def _module(filename, name):
    src = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(name, src)
    if spec is None or spec.loader is None:
        raise ReviewError("REVIEW_DEPENDENCY_MISSING")
    mod = module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except (ImportError, OSError) as exc:
        raise ReviewError("REVIEW_DEPENDENCY_MISSING") from exc
    return mod


def validate_policy(document):
    """Only review metadata permitted: no customer fields, filenames, paths."""
    if (type(document) is not dict or set(document) !=
            {"schema_version", "dry_run_only", "categories"} or
            document["schema_version"] != POLICY_SCHEMA or
            document["dry_run_only"] is not True):
        raise ReviewError("INVALID_REVIEW_POLICY_ENVELOPE")
    configured = document["categories"]
    if type(configured) is not dict or set(configured) != CATEGORIES:
        raise ReviewError("INVALID_REVIEW_POLICY_CATEGORIES")
    result = {}
    for category in sorted(CATEGORIES):
        rules = configured[category]
        if (type(rules) is not dict or set(rules) !=
                {"review_after_days", "legal_hold", "backup_lineage"}):
            raise ReviewError("INVALID_REVIEW_POLICY_FIELDS")
        days = rules["review_after_days"]
        hold = rules["legal_hold"]
        backup = rules["backup_lineage"]
        if type(days) is not int or not 1 <= days <= MAX_REVIEW_DAYS:
            raise ReviewError("INVALID_REVIEW_THRESHOLD")
        if (type(hold) is not str or hold not in LEGAL_HOLD or
                type(backup) is not str or backup not in BACKUP):
            raise ReviewError("INVALID_REVIEW_POLICY_STATE")
        result[category] = (days, hold, backup)
    return result


def dry_run(root, policy, *, now=None, inventory_module=None):
    """Group candidate metadata only; never return a deletion plan.

    Normal review traverses metadata ONCE with strict per-category cutoffs.
    Injected legacy test inventories retain the old five-call behavior.
    This is NOT a transactionally consistent filesystem snapshot. Metadata
    changes during scanning can still go undetected.
    """
    rules = validate_policy(policy)
    scan = _module("sovia_retention.py", "_sovia_review_inventory") if inventory_module is None else inventory_module
    fixed_now = time.time() if now is None else now
    grouped = {}
    baseline = None
    # Ordinary review: one bounded metadata traversal with category-specific
    # thresholds. Preserve the injected legacy inventory hook for existing
    # fault-injection tests; neither mode is a transactional filesystem snapshot.
    if inventory_module is None:
        try:
            single_summary = scan.inventory(
                root, now=fixed_now,
                category_thresholds={category: entry[0]
                                     for category, entry in rules.items()})
        except (OSError, TypeError, ValueError, OverflowError) as exc:
            raise ReviewError("REVIEW_INVENTORY_FAILED") from exc
    else:
        single_summary = None
    for category, (days, hold, backup) in rules.items():
        if single_summary is not None:
            summary = single_summary
        else:
            try:
                summary = scan.inventory(root, older_than_days=days, now=fixed_now)
            except (OSError, TypeError, ValueError, OverflowError) as exc:
                raise ReviewError("REVIEW_INVENTORY_FAILED") from exc
        shared = (
            summary.get("entries_scanned"),
            summary.get("symlinks_skipped"),
            summary.get("unrecognized_or_skipped"),
            summary.get("files_by_category"),
        )
        if baseline is None:
            baseline = shared
        elif shared != baseline:
            raise ReviewError("REVIEW_METADATA_CHANGED_DURING_SCAN")
        count = summary["age_candidates_by_category"].get(category, 0)
        size = summary["age_candidate_bytes_by_category"].get(category, 0)
        if hold == "present_claimed":
            disposition = "HOLD_CLAIMED_REVIEW_REQUIRED"
        elif hold == "unknown":
            disposition = "VERIFY_LEGAL_HOLD"
        elif backup == "unknown":
            disposition = "VERIFY_BACKUP_LINEAGE"
        else:
            disposition = "HUMAN_REVIEW_ONLY"
        grouped[category] = {
            "review_after_days": days,
            "files_seen": summary["files_by_category"].get(category, 0),
            "age_review_candidates": count,
            "candidate_bytes": size,
            "review_queue_status": disposition,
        }
    return {
        "status": "READ_ONLY_REVIEW_CANDIDATES_NOT_DISPOSAL_APPROVAL",
        "category_review": grouped,
        "entries_scanned": baseline[0],
        "symlinks_skipped": baseline[1],
        "deletion_authorized": False,
        "deletion_attempted": False,
        "customer_data_read": False,
        "legal_hold_independently_verified": False,
        "backup_lineage_independently_verified": False,
        "snapshot_transactional": False,
        "limitations": [
            "FILE_MTIME_IS_NOT_THE_LEGAL_RETENTION_START_DATE",
            "FILE_EXTENSION_DOES_NOT_PROVE_CONTENT_OR_ORIGIN",
            "REVIEW_THRESHOLD_IS_NOT_A_DELETION_DEADLINE",
            "OPERATOR_POLICY_ASSERTIONS_ARE_NOT_AUTHENTICATED",
            "FILESYSTEM_CAN_CHANGE_DURING_METADATA_SCAN",
            "NO_FILES_READ_OR_MODIFIED_OR_DELETED",
        ],
    }


def plan_files(root, policy_path, *, now=None):
    source = Path(policy_path)
    if source.is_symlink() or not source.is_file():
        raise ReviewError("REVIEW_POLICY_FILE_UNAVAILABLE")
    reader = _module("sovia_audit.py", "_sovia_review_audit")
    try:
        document = reader.read_document(source)
    except (ValueError, OSError, TypeError, RecursionError, OverflowError) as exc:
        raise ReviewError("REVIEW_POLICY_INVALID_JSON") from exc
    return dry_run(root, document, now=now)


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA local read-only retention review dry-run")
    p.add_argument("--root", required=True, help="Explicit local artifacts directory")
    p.add_argument("--policy", required=True, help="Strict local review-only policy JSON")
    p.add_argument("--dry-run", action="store_true", help="Required. Never deletes.")
    args = p.parse_args(argv)
    if not args.dry_run:
        print(json.dumps({"status": "REJECTED", "error_code": "DRY_RUN_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        result = plan_files(args.root, args.policy)
    except ReviewError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
