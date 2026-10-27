"""Offline metadata-only v0.12 history v2, synthetic ONLY.

No automatic v1 migration. Separate namespace for (engine version, source
digest) prevents silent 'same report ID, different findings' collisions.
Only hashes, timestamps of import and aggregate counts are stored.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile

SCHEMA_VERSION = 2
ENGINE_VERSION = "0.12.0-preview"
COLUMNS = ("report_uid", "source_report_id", "engine_version",
           "source_digest", "findings_digest", "event_count",
           "finding_count", "imported_utc")
# The local beta owns a single fixed table DDL. Column names alone do not
# establish PRIMARY KEY / UNIQUE constraints or exclude hidden SQL triggers.
# Only databases created by this exact schema are supported, no auto-migration.
REPORTS_DDL = """CREATE TABLE reports (
                report_uid TEXT PRIMARY KEY,
                source_report_id TEXT NOT NULL,
                engine_version TEXT NOT NULL,
                source_digest TEXT NOT NULL,
                findings_digest TEXT NOT NULL,
                event_count INTEGER NOT NULL,
                finding_count INTEGER NOT NULL,
                imported_utc TEXT NOT NULL,
                UNIQUE(engine_version, source_digest))"""


class HistoryV012Error(ValueError):
    """Non-disclosing refusal code."""


def _sibling(filename, alias):
    target = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(alias, target)
    if spec is None or spec.loader is None:
        raise HistoryV012Error("DEPENDENCY_MISSING")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise HistoryV012Error("DEPENDENCY_MISSING") from exc
    return module


def _destination(path):
    dest = Path(os.path.abspath(path))
    if dest.is_symlink() or not dest.parent.is_dir():
        raise HistoryV012Error("INVALID_DESTINATION")
    return dest


def _existing(path):
    src = Path(os.path.abspath(path))
    if src.is_symlink() or not src.is_file():
        raise HistoryV012Error("DATABASE_UNAVAILABLE")
    return src


def _connect(path, readonly=False):
    # mode=rw NEVER creates a missing file; ordinary connect() could.
    uri = path.resolve().as_uri() + ("?mode=ro" if readonly else "?mode=rw")
    db = sqlite3.connect(uri, uri=True, timeout=5)
    try:
        db.execute("PRAGMA foreign_keys=ON")
        if readonly:
            db.execute("PRAGMA query_only=ON")
        else:
            db.execute("PRAGMA secure_delete=ON")
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA busy_timeout=5000")
    except Exception:
        db.close()
        raise
    return db


def _schema(db, create=False):
    version = db.execute("PRAGMA user_version").fetchone()[0]
    found = {row[0] for row in db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    if version == 0 and not found and create:
        with db:
            db.execute(REPORTS_DDL)
            db.execute("PRAGMA user_version=2")
        version, found = 2, {"reports"}
    if version != SCHEMA_VERSION or found != {"reports"}:
        raise HistoryV012Error("INCOMPATIBLE_HISTORY_SCHEMA")
    # SQLite quick_check detects low-level corruption, not altered constraints
    # or extra triggers/views/indexes. Refuse lookalike v2 tables and any user
    # defined schema object outside the one exact, supported reports table.
    objects = list(db.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%'"
    ))
    if objects != [("table", "reports", "reports", REPORTS_DDL)]:
        raise HistoryV012Error("INVALID_HISTORY_SCHEMA_OR_INTEGRITY")
    columns = tuple(row[1] for row in db.execute("PRAGMA table_info(reports)"))
    if columns != COLUMNS or db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
        raise HistoryV012Error("INVALID_HISTORY_SCHEMA_OR_INTEGRITY")


def _new_stage(parent):
    fd, name = tempfile.mkstemp(prefix=".sovia-v012-", suffix=".sqlite3", dir=parent)
    os.close(fd)
    return Path(name)


def _publish(stage, target):
    if target.exists() or target.is_symlink():
        raise HistoryV012Error("DESTINATION_ALREADY_EXISTS")
    # Exclusive publication: never overwrite an original DB or snapshot.
    os.link(stage, target)


def _signature(report):
    if report["engine_version"] != ENGINE_VERSION:
        raise HistoryV012Error("UNSUPPORTED_ENGINE_VERSION")
    source_digest = report["normalized_policy_sha256"]
    if report["report_id"] != source_digest[:16]:
        raise HistoryV012Error("INCONSISTENT_REPORT_DIGEST")
    findings_bytes = json.dumps(
        report["findings"], ensure_ascii=False, sort_keys=True,
        separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    findings_digest = hashlib.sha256(findings_bytes).hexdigest()
    identity = hashlib.sha256(
        (ENGINE_VERSION + "\0" + source_digest).encode("ascii")
    ).hexdigest()
    return identity, source_digest, findings_digest


def _insert(db, report):
    uid, source_digest, finding_digest = _signature(report)
    with db:
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            "SELECT source_report_id, engine_version, source_digest, "
            "findings_digest, event_count, finding_count "
            "FROM reports WHERE report_uid=?", (uid,)
        ).fetchone()
        if row is not None:
            # A matching findings hash alone cannot prove that persisted
            # event/finding counts and identity metadata were not changed.
            expected = (
                report["report_id"], ENGINE_VERSION, source_digest,
                finding_digest, report["event_count"], report["finding_count"],
            )
            if row != expected:
                raise HistoryV012Error("VERSIONED_RESULT_CONFLICT")
            return {"status": "already_present", "report_uid": uid, "reports_added": 0}
        db.execute("""INSERT INTO reports VALUES (?,?,?,?,?,?,?,?)""", (
            uid, report["report_id"], ENGINE_VERSION, source_digest, finding_digest,
            report["event_count"], report["finding_count"],
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        ))
    return {"status": "imported", "report_uid": uid, "reports_added": 1}


def import_synthetic(db_path, input_path):
    """Never accept live data, v1 DBs, or implicit conversion."""
    target = _destination(db_path)
    source = Path(os.path.abspath(input_path))
    if source.is_symlink() or not source.is_file() or target.resolve() == source.resolve():
        raise HistoryV012Error("INVALID_SOURCE_OR_ALIAS")
    core = _sibling("sovia_audit.py", "_sovia_h012_reader")
    document = core.read_document(source)
    _sibling("sovia_pii_preflight.py", "_sovia_h012_pii").assert_no_high_risk_patterns(document)
    report = _sibling("sovia_audit_v012.py", "_sovia_h012_engine").evaluate(
        document, legacy_audit=core
    )
    if target.exists():
        db = _connect(_existing(target))
        try:
            _schema(db)
            return _insert(db, report)
        finally:
            db.close()
    stage = _new_stage(target.parent)
    try:
        db = _connect(stage)
        try:
            _schema(db, create=True)
            result = _insert(db, report)
        finally:
            db.close()
        with stage.open("r+b") as fd:
            os.fsync(fd.fileno())
        _publish(stage, target)
        return result
    finally:
        stage.unlink(missing_ok=True)


def status(path):
    db = _connect(_existing(path), readonly=True)
    try:
        _schema(db)
        row = db.execute(
            "SELECT COUNT(*),COALESCE(SUM(event_count),0),"
            "COALESCE(SUM(finding_count),0) FROM reports"
        ).fetchone()
        return {"schema_version": SCHEMA_VERSION, "engine_version": ENGINE_VERSION,
                "reports": row[0], "event_count_total": row[1],
                "finding_count_total": row[2], "v1_compatible": False}
    finally:
        db.close()


def _snapshot(source_path, destination_path):
    source = _existing(source_path)
    target = _destination(destination_path)
    if target.exists() or target.resolve() == source.resolve():
        raise HistoryV012Error("SNAPSHOT_DESTINATION_EXISTS_OR_ALIASES")
    reader = _connect(source, readonly=True)
    try:
        _schema(reader)
        stage = _new_stage(target.parent)
        try:
            writer = _connect(stage)
            try:
                reader.backup(writer)
                _schema(writer)
            finally:
                writer.close()
            with stage.open("r+b") as fd:
                os.fsync(fd.fileno())
            _publish(stage, target)
        finally:
            stage.unlink(missing_ok=True)
    finally:
        reader.close()
    return {"status": "snapshot_created", "schema_version": SCHEMA_VERSION}


def backup(db_path, new_path):
    return _snapshot(db_path, new_path)


def restore(backup_path, new_path):
    return _snapshot(backup_path, new_path)


def main(argv=None):
    parser = argparse.ArgumentParser(description="v0.12 offline synthetic-only metadata history v2")
    subs = parser.add_subparsers(dest="cmd", required=True)
    imp = subs.add_parser("import")
    imp.add_argument("--db", required=True)
    imp.add_argument("--input", required=True)
    imp.add_argument("--synthetic-only", action="store_true")
    st = subs.add_parser("status")
    st.add_argument("--db", required=True)
    cp = subs.add_parser("backup")
    cp.add_argument("--db", required=True)
    cp.add_argument("--output", required=True)
    rest = subs.add_parser("restore")
    rest.add_argument("--input", required=True)
    rest.add_argument("--db", required=True)
    args = parser.parse_args(argv)
    if args.cmd == "import" and not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ACK_REQUIRED"}),
              file=sys.stderr)
        return 2
    try:
        if args.cmd == "import":
            result = import_synthetic(args.db, args.input)
        elif args.cmd == "status":
            result = status(args.db)
        elif args.cmd == "backup":
            result = backup(args.db, args.output)
        else:
            result = restore(args.input, args.db)
    except (ValueError, TypeError, OSError, OverflowError, RecursionError,
            sqlite3.Error) as exc:
        code = str(exc) if isinstance(exc, HistoryV012Error) else "HISTORY_V012_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
