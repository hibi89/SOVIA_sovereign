"""Offline, read-only retention inventory. Never deletes or reads file contents."""
from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import stat
import sys
import time

MAX_ENTRIES = 10_000
MAX_DEPTH = 8
SKIP_DIRECTORIES = frozenset({".git", ".venv", "venv", "__pycache__", "node_modules"})
CATEGORIES = frozenset({"source_or_export", "rendered_report", "history_or_backup",
                        "history_sidecar", "package_or_checksum"})


class InventoryError(ValueError):
    """Safe, non-path-bearing inventory failure."""


# Python's Windows stat_result exposes FILE_ATTRIBUTE_REPARSE_POINT. Junctions
# and directory mount points are not consistently represented by S_ISLNK.
# Treat them like symlinks: their contents are outside a trusted scan boundary.
_REPARSE_POINT = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)


def _is_reparse_point(metadata):
    return bool(getattr(metadata, "st_file_attributes", 0) & _REPARSE_POINT)


def _category(filename: str) -> str | None:
    name = filename.lower()
    if name.endswith((".sqlite-wal", ".sqlite-shm", ".sqlite-journal", ".db-wal", ".db-shm", ".db-journal")):
        return "history_sidecar"
    if name.endswith((".sqlite", ".sqlite3", ".db")):
        return "history_or_backup"
    if name.endswith((".json", ".csv")):
        return "source_or_export"
    if name.endswith((".html", ".htm", ".pdf")):
        return "rendered_report"
    if name.endswith((".zip", ".sha256")):
        return "package_or_checksum"
    return None


def inventory(root, *, older_than_days=30, now=None, max_entries=MAX_ENTRIES,
              category_thresholds=None):
    """Summarize *candidates* by extension and mtime, without reading or modifying data.

    No filenames, paths, or file content are included in the returned summary.
    Fail closed on traversal errors/limits; symlinks and reported Windows
    reparse points (junctions/mounts) are skipped, including ancestor
    components of the requested root. Concurrent path replacement
    remains a filesystem TOCTOU caveat: this is no sandbox boundary.
    Optional strict per-category thresholds are evaluated in the SAME scan;
    this is not a transactional filesystem snapshot or disposal authorization.
    """
    if type(older_than_days) is not int or not 1 <= older_than_days <= 36500:
        raise InventoryError("INVALID_AGE")
    if type(max_entries) is not int or not 1 <= max_entries <= MAX_ENTRIES:
        raise InventoryError("INVALID_LIMIT")
    if category_thresholds is not None:
        if (type(category_thresholds) is not dict or
                set(category_thresholds) != CATEGORIES or
                any(type(v) is not int or not 1 <= v <= 36500
                    for v in category_thresholds.values())):
            raise InventoryError("INVALID_CATEGORY_THRESHOLDS")
    try:
        # os.path.abspath normalizes relative paths WITHOUT resolving junctions.
        # Checking only the terminal directory misses `junction/child` roots:
        # a reparse point in an ancestor can redirect a whole requested tree.
        target = Path(os.path.abspath(root))
        root_metadata = None
        for component in (target, *target.parents):
            metadata = component.stat(follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode) or _is_reparse_point(metadata):
                raise InventoryError("INVALID_ROOT")
            if component == target:
                root_metadata = metadata
        if not stat.S_ISDIR(root_metadata.st_mode):
            raise InventoryError("INVALID_ROOT")
    except (OSError, ValueError) as exc:
        raise InventoryError("ROOT_ACCESS_FAILED") from exc
    when = time.time() if now is None else now
    if not isinstance(when, (int, float)) or not (0 < when < float("inf")):
        raise InventoryError("INVALID_CLOCK")
    cutoff = when - older_than_days * 86400
    cutoffs = (None if category_thresholds is None else
               {key: when - days * 86400
                for key, days in category_thresholds.items()})
    scanned = 0
    skipped_links = 0
    ignored = 0
    categories = Counter()
    candidates = Counter()
    candidate_bytes = Counter()
    stack = [(target, 0)]
    try:
        while stack:
            folder, depth = stack.pop()
            with os.scandir(folder) as scan:
                for entry in scan:
                    # Stream entries rather than materializing an unbounded directory.
                    scanned += 1
                    if scanned > max_entries:
                        raise InventoryError("ENTRY_LIMIT_EXCEEDED")
                    mode = entry.stat(follow_symlinks=False)
                    if stat.S_ISLNK(mode.st_mode) or _is_reparse_point(mode):
                        skipped_links += 1
                        continue
                    if stat.S_ISDIR(mode.st_mode):
                        if entry.name in SKIP_DIRECTORIES:
                            ignored += 1
                            continue
                        if depth >= MAX_DEPTH:
                            raise InventoryError("DEPTH_LIMIT_EXCEEDED")
                        stack.append((Path(entry.path), depth + 1))
                        continue
                    if not stat.S_ISREG(mode.st_mode):
                        ignored += 1
                        continue
                    category = _category(entry.name)
                    if category is None:
                        ignored += 1
                        continue
                    categories[category] += 1
                    if mode.st_mtime <= (cutoff if cutoffs is None else cutoffs[category]):
                        candidates[category] += 1
                        candidate_bytes[category] += mode.st_size
    except InventoryError:
        raise
    except OSError as exc:
        raise InventoryError("TRAVERSAL_FAILED") from exc
    return {
        "status": "READ_ONLY_CANDIDATES_NOT_DELETION_AUTHORIZATION",
        "older_than_days": older_than_days if cutoffs is None else None,
        "entries_scanned": scanned,
        "symlinks_skipped": skipped_links,
        "unrecognized_or_skipped": ignored,
        "files_by_category": dict(sorted(categories.items())),
        "age_candidates_by_category": dict(sorted(candidates.items())),
        "age_candidate_bytes_by_category": dict(sorted(candidate_bytes.items())),
        "limitations": [
            "MTIME_IS_NOT_CREATION_OR_LEGAL_RETENTION_DATE",
            "EXTENSION_IS_NOT_VERIFIED_CONTENT_TYPE",
            "FILES_MAY_BE_REQUIRED_OR_BACKED_UP_ELSEWHERE",
            "NO_FILES_READ_MODIFIED_OR_DELETED",
        ],
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="SOVIA private local read-only retention inventory")
    p.add_argument("--root", required=True, help="Explicit local directory; nothing is transmitted")
    p.add_argument("--older-than-days", type=int, default=30)
    args = p.parse_args(argv)
    try:
        summary = inventory(args.root, older_than_days=args.older_than_days)
    except InventoryError as exc:
        print(json.dumps({"status": "INVENTORY_FAILED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
