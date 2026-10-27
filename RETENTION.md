## P2 Windows reparse-point safety — proposed, 2026-10-27 KST

The read-only inventory already ignores Unix and Windows symlinks represented by `S_ISLNK`, but Windows NTFS junctions and directory mount points may appear as directories with `st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT`. Scanning such an entry risks including metadata from outside the selected folder. The source-only helper `sovia_retention.py` now rejects a reparse-point root and skips any reparse-point file/directory before descending or counting files. The existing `symlinks_skipped` count includes skipped junction/reparse entries for backward-compatible summary output.

Options evaluated: (A) resolve every visited path against root repeatedly (extra filesystem traversals and race windows); (B) examine no-follow `stat` reparse attributes, fail closed without traversal or content reads (chosen, minimal dependency-free Windows Python 3.11+ change). The Windows bit is checked via `getattr(st, "st_file_attributes", 0)`, preserving POSIX compatibility. Existing single-pass category checks, dry-run/no-delete and output contracts remain unchanged.

Synthetic mocks in `tests/test_retention_reparse.py` test simulated Windows reparse root, directory and regular-file flags plus ordinary file compatibility in Windows/Ubuntu Python CI. **Limit:** a concurrent directory replacement may occur after stat and before os.scandir; this is best-effort hygiene, **NOT** a hardened sandbox, race-free directory confinement, guarantee of actual Windows junction behavior, customer privacy certification or approval to delete. Actual owner Windows filesystem test remains outstanding. No real user files/credentials accessed. Existing v0.10 and v0.11.2 fixed portable payloads do not include the retention source helper, so immutable ZIP checksums must not change. Do not market this as completed commercial hardening.

---

## P2 follow-up — category policy dry-run (2026-10-27)

An independent source-only `sovia_retention_review.py` applies strict synthetic **per-category review thresholds** and operator-asserted legal-hold/backup states to the existing metadata-only `sovia_retention.inventory` counts. See [RETENTION_REVIEW.md](RETENTION_REVIEW.md). It **never** grants deletion authority or invokes the history purge, never uses customer file contents and never ships in the existing portable v0.10 beta ZIP. Five scans share a fixed clock, but are **not an atomic filesystem snapshot**. All outputs remain human-review candidates, not lawful expiry dates. Full CI regression is required before develop integration.

---

# SOVIA P2 local data lifecycle: read-only inventory (development-only)

Status: **safe diagnostic prototype**, NOT a retention/deletion implementation or commercial privacy clearance.

## Decision: two options

| Approach | Benefits | Cost/risk | Current choice |
|---|---|---|---|
| Auto-expire and delete customer artifacts | Low ongoing maintenance once correctly configured | Dangerous when consent period, legal hold, backup lineage, output ownership, or system snapshots are unknown; original data loss | Deferred; requires detailed approval |
| Read-only local artifact inventory | No mutation, zero new dependencies, useful before creating a data register | Extension/mtime classification can be wrong; operator must review each folder separately | **Implemented in separate P2 feature branch** |

## What this tool can do

`python sovia_retention.py --root PRIVATE_LOCAL_OUTPUT_FOLDER --older-than-days 30`

The user must specify the local root. The script traverses to depth 8, at most 10,000 entries, does not follow symlinks or scan common `.git`/venv directories, reads filesystem metadata *only*, makes no network calls and creates no files. It prints grouped file counts and size of age candidates, **never filenames or paths**. If the tree is too deep or inaccessible it fails closed. Report, source, SQLite, WAL and backup candidates are all only *candidates* for human review: extension and filesystem modification time cannot prove classification, ownership or lawful erasure date.

**No automated retention cutoff, data purge, backup deletion, source removal or secure erasure** is provided. Existing `sovia_history.py purge` remains separate and explicitly confirmed, and cannot delete customer originals, backups or HTML/CSV/PDF exports. The new tool is not in the v0.10 portable allowlist/ZIP, so shipping/support claims must not imply it is installed on end-user machines.

## Before authorized real customer use

1. Identify data controller, processing purpose, explicit authorization and the customer-approved source fields; never upload originals to a public repo or external service.
2. Document data inventory across original JSON/CSV, normalized reports, SQLite files and WAL/SHM, HTML/PDF/CSV exports, ZIPs, local backups, Windows restore points/sync folders, and the SOVIA_DIAGNOSTICS sibling.
3. Record customer-approved retention by artifact class, legal hold exceptions, notice obligations, operator identity and evidence of approved disposal; do not infer days from this diagnostic's `--older-than-days` argument.
4. For deletion, implement explicit scoped review/confirmation, snapshots/recovery verification, no-clobber boundaries, policy exceptions, and negative tests first. Customer agreements and privacy review are still mandatory.
5. Validate with explicitly consented, sanitized n8n-like fixtures offline first. Do not claim an untested adapter or real customer compatibility.

Regression: `python -m unittest discover -s tests -p test_retention.py -v`. This standalone development helper has no third-party dependencies and does not change existing audit/history/portable behavior.
