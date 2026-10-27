## P2 improvement — single-pass metadata scan (2026-10-27, feature proposal)

Existing reviewed category thresholds formerly made **five full directory traversals** with the same pinned clock. This raises I/O linearly with category count and permits changes between traversals to cause spurious metadata disagreement. Two choices were compared: **(A)** keep five scans and compare coarse counters (zero development effort, five directory passes and inconsistent sample windows); **(B)** accept strict per-category thresholds in the existing offline inventory and evaluate all candidates in **one** bounded directory pass (small additive source-only change, fewer I/O operations, shared sample window). Option B selected for review; it does **not** make a transactional/atomic filesystem snapshot. The original single-age inventory CLI and injected fault-test inventory compatibility path are preserved.

New regression `tests/test_retention_single_pass.py` checks that 5 independently computed legacy category thresholds produce exactly the same counts/bytes as a *single* scan, verifies one `os.scandir` for a flat fixture (two for a nested directory), no file/content changes, strict thresholds and no local path/filename leakage. `sovia_retention.py` and `sovia_retention_review.py` are source-only helpers outside old v0.10 and v0.11.2 18-file portable archives. Existing immutable release provenance must stay identical. This remains a review queue, not legal retention period, secure erase, permission to delete or sale readiness. **CI and integration pending** at feature creation.

---

# SOVIA P2 — read-only artifact retention governance dry-run

**Development-stage review tool, NOT automatic retention enforcement or deletion approval.** No real customer artifacts were used to build or test this feature.

## Trade-off and chosen design

| Design | Initial implementation cost | Risk and maintenance | Decision |
|---|---|---|---|
| Implement scheduled purge by category and age | Complex lineage, legal hold, SQLite WAL/backups, distributed copies; actual destruction can be irreversible | Cannot prove legal period from mtime; high-risk customer loss | **Not implemented** |
| Add a strict review-only category policy on top of the existing offline read-only retention inventory | Python stdlib, no external calls, metadata-only scan | Explicit policy claims remain unverified, requires human review, repeat-scans are not transactional | **Implemented** |

## Scope and exact policy

The new `sovia_retention_review.py` uses `sovia_retention.inventory` without editing it. A policy file must contain exactly these five supported categories and fields; extra fields (especially potential filenames, owner names or customer data) fail closed:

```json
{
  "schema_version": "sovia.retention_review.v1",
  "dry_run_only": true,
  "categories": {
    "source_or_export": {"review_after_days": 30, "legal_hold": "unknown", "backup_lineage": "unknown"},
    "rendered_report": {"review_after_days": 14, "legal_hold": "none_claimed", "backup_lineage": "unknown"},
    "history_or_backup": {"review_after_days": 90, "legal_hold": "present_claimed", "backup_lineage": "unknown"},
    "history_sidecar": {"review_after_days": 7, "legal_hold": "none_claimed", "backup_lineage": "reviewed_claimed"},
    "package_or_checksum": {"review_after_days": 180, "legal_hold": "none_claimed", "backup_lineage": "reviewed_claimed"}
  }
}
```

These are **fabricated demonstration review thresholds**, NOT recommended lawful retention durations. The claim `none_claimed` is **not** verified absence of a legal hold; `reviewed_claimed` is **not** verified backup history. All policy assertions can be fabricated. A candidate remains **human-review-only**, never safe-to-delete.

Results are aggregate by extension category with file counts, older-than-threshold review counts, bytes, and one of:
- `HOLD_CLAIMED_REVIEW_REQUIRED` — operator claims a hold; do not dispose
- `VERIFY_LEGAL_HOLD` — legal hold status is unknown; do not dispose
- `VERIFY_BACKUP_LINEAGE` — claimed no hold but backup status unknown; do not dispose
- `HUMAN_REVIEW_ONLY` — operator claims no hold and reviewed backup; still **not** approved for disposal

Strict outcomes always include `deletion_authorized:false`, `deletion_attempted:false`, `legal_hold_independently_verified:false`, `backup_lineage_independently_verified:false` and `snapshot_transactional:false`. No filenames, local paths or file contents are returned.

## Synthetic offline usage

```powershell
py -3 -I -B sovia_retention_review.py --root "SYNTHETIC_ARTIFACT_DIRECTORY" --policy examples/demo_retention_review_policy.json --dry-run
py -3 -m unittest discover -s tests -p test_retention_review.py -v
```

The scanner reads filesystem metadata only under the explicit root and reads the **operator-supplied JSON policy**; no customer file contents, filenames or file locations are printed and no source file is written, renamed, touched or deleted. The five configured thresholds cause up to five repeat scans of the same directory with one pinned timestamp. It enforces existing limits (10,000 scanned entries, max depth 8, skipped symlinks/venv/.git, strict errors); if summary counts change between scans it rejects the result. **This is still not an atomic snapshot**: changes with coincidentally identical counts may escape detection. For genuine customer use, an authenticated inventory/ownership model, consistent snapshot capability, legal hold and processor/controller agreements, retention start-date evidence, backup lineage/restore tests, and destructive-action approval gates remain unimplemented.

The existing `sovia_history.py purge` API remains separate and unchanged. Do not interpret this new tool as authorization to invoke it or delete ZIPs/WAL/shadow copies. The source-only P2 tool is **not in the old v0.10 portable ZIP**. `main`, Production, Cloud and paid listing remain unchanged.

See [RETENTION.md](RETENTION.md) for existing inventory limitations, and [GAP_MATRIX.md](GAP_MATRIX.md) for outstanding commercial/privacy requirements.
