"""SOVIA v0.7: opt-in offline SQLite metadata-only history (stdlib).

The default sovia_audit.py report flow is stateless and unchanged.
This module stores hashed event identities/content and rule metadata, never raw
event labels, prompt bodies, source pointers, filenames or customer documents.
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

VERSION = 1
TABLES = frozenset(("reports", "events", "report_events", "findings"))
SCHEMA = (
    """CREATE TABLE reports (
       report_id TEXT PRIMARY KEY, content_sha256 TEXT NOT NULL,
       engine_version TEXT NOT NULL, imported_utc TEXT NOT NULL,
       event_count INTEGER NOT NULL, finding_count INTEGER NOT NULL)""",
    """CREATE TABLE events (
       identity_sha256 TEXT PRIMARY KEY, payload_sha256 TEXT NOT NULL,
       occurred_at_utc TEXT NOT NULL, agent_sha256 TEXT NOT NULL,
       run_sha256 TEXT NOT NULL, tool_sha256 TEXT NOT NULL,
       source_pointer_present INTEGER NOT NULL CHECK (source_pointer_present IN (0,1)))""",
    """CREATE TABLE report_events (
       report_id TEXT NOT NULL REFERENCES reports(report_id) ON DELETE CASCADE,
       identity_sha256 TEXT NOT NULL REFERENCES events(identity_sha256),
       PRIMARY KEY (report_id, identity_sha256))""",
    """CREATE TABLE findings (
       report_id TEXT NOT NULL, finding_sha256 TEXT NOT NULL,
       identity_sha256 TEXT NOT NULL, rule_id TEXT NOT NULL,
       severity TEXT NOT NULL, evidence_status TEXT NOT NULL,
       PRIMARY KEY (report_id, finding_sha256),
       FOREIGN KEY (report_id, identity_sha256)
         REFERENCES report_events(report_id, identity_sha256) ON DELETE CASCADE)""",
)

class HistoryError(ValueError):
    """An invalid, conflicting or unsafe history operation."""


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def _sibling(filename, module_name):
    source = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(module_name, source)
    if spec is None or spec.loader is None:
        raise HistoryError("Required SOVIA module not found: " + filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def audit_source(path, policy_path=None):
    """Load same canonical audit contract as the read-only CLI; never execute logs."""
    audit = _sibling("sovia_audit.py", "_sovia_history_audit")
    source = Path(path)
    if source.suffix.lower() == ".csv":
        if policy_path is None:
            raise HistoryError("CSV source requires --policy")
        policy_doc = audit.read_document(policy_path)
        keys = {"allowed_tools", "approved_destinations",
                "sensitive_targets", "max_tool_calls_per_minute"}
        if (type(policy_doc) is not dict or set(policy_doc) != {"schema_version", "policy"}
                or policy_doc["schema_version"] != audit.SCHEMA
                or type(policy_doc["policy"]) is not dict
                or set(policy_doc["policy"]) - keys):
            raise HistoryError("CSV policy must contain only supported schema_version and policy keys")
        importer = _sibling("sovia_csv_input.py", "_sovia_history_csv")
        try:
            events = importer.read_csv_events(source)
        except ValueError as exc:
            raise HistoryError(str(exc)) from exc
        document = {"schema_version": audit.SCHEMA, "policy": policy_doc["policy"],
                    "events": events}
    else:
        if policy_path is not None:
            raise HistoryError("--policy applies only to CSV source")
        document = audit.read_document(source)
    return audit.evaluate(document)


def _safe_destination(path):
    path = Path(path)
    if path.is_symlink():
        raise HistoryError("Symlink destination not supported")
    if not path.parent.is_dir():
        raise HistoryError("Destination directory must already exist")
    return path


def _require_file(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise HistoryError("History/backup file missing or symlink is unsupported")
    return path


def _connect(path, readonly=False):
    if readonly:
        source = _require_file(path)
        conn = sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True, timeout=5)
    else:
        conn = sqlite3.connect(path, timeout=5)
    try:
        if readonly:
            conn.execute("PRAGMA query_only=ON")
        else:
            conn.execute("PRAGMA foreign_keys=ON")
            conn.execute("PRAGMA secure_delete=ON")
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA synchronous=FULL")
    except Exception:
        conn.close()
        raise
    return conn


def _verify_schema(conn, create=False):
    version = conn.execute("PRAGMA user_version").fetchone()[0]
    found = {row[0] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
    if version == 0 and create and not found:
        with conn:
            for statement in SCHEMA:
                conn.execute(statement)
            conn.execute("PRAGMA user_version=1")
        version, found = 1, TABLES
    if version != VERSION or found != TABLES:
        raise HistoryError("Unsupported or unrecognized SQLite history schema; no migration applied")
    if conn.execute("PRAGMA quick_check").fetchone()[0] != "ok":
        raise HistoryError("SQLite integrity check failed")
    if conn.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise HistoryError("SQLite foreign-key integrity check failed")


def _new_stage(directory):
    fd, name = tempfile.mkstemp(prefix=".sovia-db-", suffix=".sqlite3", dir=directory)
    os.close(fd)
    return Path(name)


def _publish(stage, destination):
    # os.link is deliberately exclusive: never overwrite backups/restores/DBs.
    os.link(stage, destination)
    # Caller cleans the staging file in finally.


def _identity(event):
    return _digest([event["agent_id"], event["run_id"], event["event_id"]])


def _import_transaction(conn, report):
    rid = report["report_id"]
    digest = report["normalized_policy_sha256"]
    if rid != digest[:16] or len(digest) != 64:
        raise HistoryError("Inconsistent audit report identity")
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        old = conn.execute("SELECT content_sha256 FROM reports WHERE report_id=?",
                           (rid,)).fetchone()
        if old is not None:
            if old[0] != digest:
                raise HistoryError("Report identifier digest collision")
            return {"status": "already_present", "report_id": rid,
                    "events": report["event_count"], "findings": report["finding_count"]}
        event_ids = {}
        # Precheck conflicts first to avoid recording partial history.
        for event in report["events"]:
            ident = _identity(event)
            content = _digest(event)
            old_event = conn.execute(
                "SELECT payload_sha256 FROM events WHERE identity_sha256=?", (ident,)
            ).fetchone()
            if old_event is not None and old_event[0] != content:
                raise HistoryError("Event identity reused with conflicting metadata")
            event_ids[event["event_id"]] = ident
        imported = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        conn.execute("INSERT INTO reports VALUES (?,?,?,?,?,?)",
                     (rid, digest, report["engine_version"], imported,
                      report["event_count"], report["finding_count"]))
        for event in report["events"]:
            ident = event_ids[event["event_id"]]
            conn.execute("INSERT OR IGNORE INTO events VALUES (?,?,?,?,?,?,?)",
                         (ident, _digest(event), event["occurred_at_utc"],
                          _digest(event["agent_id"]), _digest(event["run_id"]),
                          _digest(event["tool_name"]), int(bool(event["source_pointer"]))))
            conn.execute("INSERT INTO report_events VALUES (?,?)", (rid, ident))
        for item in report["findings"]:
            eid = item["event_ids"][0]
            ident = event_ids[eid]
            finding_hash = _digest([rid, item["rule_id"], ident])
            conn.execute("INSERT INTO findings VALUES (?,?,?,?,?,?)",
                         (rid, finding_hash, ident, item["rule_id"], item["severity"],
                          item["evidence_status"]))
    return {"status": "imported", "report_id": rid,
            "events": report["event_count"], "findings": report["finding_count"]}


def import_report(db_path, source_path, policy_path=None):
    db = _safe_destination(db_path)
    inputs = [Path(source_path).resolve()]
    if policy_path is not None:
        inputs.append(Path(policy_path).resolve())
    if db.resolve() in inputs:
        raise HistoryError("Database destination must differ from original inputs")
    # Evaluate before touching a database, including invalid input cases.
    report = audit_source(source_path, policy_path)
    if db.exists():
        conn = _connect(db)
        try:
            _verify_schema(conn)
            return _import_transaction(conn, report)
        finally:
            conn.close()
    stage = _new_stage(db.parent)
    try:
        conn = _connect(stage)
        try:
            _verify_schema(conn, create=True)
            result = _import_transaction(conn, report)
        finally:
            conn.close()
        _publish(stage, db)
        return result
    finally:
        stage.unlink(missing_ok=True)


def _snapshot(source, destination):
    source = _require_file(source)
    target = _safe_destination(destination)
    if target.exists() or target.resolve() == source.resolve():
        raise HistoryError("Snapshot destination exists or aliases source")
    reader = _connect(source, readonly=True)
    try:
        _verify_schema(reader)
        stage = _new_stage(target.parent)
        try:
            writer = _connect(stage)
            try:
                reader.backup(writer)
                _verify_schema(writer)
            finally:
                writer.close()
            with stage.open("r+b") as handle:
                os.fsync(handle.fileno())
            _publish(stage, target)
        finally:
            stage.unlink(missing_ok=True)
    finally:
        reader.close()
    return {"status": "snapshot_created"}


def backup(db_path, output_path):
    return _snapshot(db_path, output_path)


def restore(backup_path, new_db_path):
    return _snapshot(backup_path, new_db_path)


def status(db_path):
    conn = _connect(db_path, readonly=True)
    try:
        _verify_schema(conn)
        return {"schema_version": VERSION,
                "reports": conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0],
                "events": conn.execute("SELECT COUNT(*) FROM events").fetchone()[0],
                "findings": conn.execute("SELECT COUNT(*) FROM findings").fetchone()[0],
                "report_events": conn.execute("SELECT COUNT(*) FROM report_events").fetchone()[0]}
    finally:
        conn.close()


def purge(db_path, report_id=None, all_reports=False, confirmed=False):
    if not confirmed:
        raise HistoryError("Deletion requires --confirm-delete")
    if all_reports == (report_id is not None):
        raise HistoryError("Select exactly one of --report-id or --all")
    conn = _connect(_require_file(db_path))
    try:
        _verify_schema(conn)
        with conn:
            conn.execute("BEGIN IMMEDIATE")
            if all_reports:
                deleted = conn.execute("DELETE FROM reports").rowcount
            else:
                deleted = conn.execute("DELETE FROM reports WHERE report_id=?", (report_id,)).rowcount
                if deleted == 0:
                    raise HistoryError("Report not found; no rows deleted")
            conn.execute("""DELETE FROM events WHERE NOT EXISTS
                         (SELECT 1 FROM report_events
                          WHERE report_events.identity_sha256=events.identity_sha256)""")
        # SQLite secure_delete and VACUUM reduce remnant pages; backups/SSD snapshots
        # still require separate deletion, so this is NOT forensic secure erasure.
        conn.execute("VACUUM")
        return {"status": "purged", "deleted_reports": deleted, **status(db_path)}
    finally:
        conn.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA local metadata-only history")
    sub = parser.add_subparsers(dest="command", required=True)
    imp = sub.add_parser("import", help="Opt-in persist hashed event metadata")
    imp.add_argument("--db", required=True)
    imp.add_argument("--input", required=True)
    imp.add_argument("--policy")
    st = sub.add_parser("status", help="Show only anonymized counters")
    st.add_argument("--db", required=True)
    snap = sub.add_parser("backup", help="Snapshot to a NEW database path")
    snap.add_argument("--db", required=True)
    snap.add_argument("--output", required=True)
    rest = sub.add_parser("restore", help="Restore snapshot to a NEW database path")
    rest.add_argument("--input", required=True)
    rest.add_argument("--db", required=True)
    delete = sub.add_parser("purge", help="Explicitly delete history (never source logs)")
    delete.add_argument("--db", required=True)
    which = delete.add_mutually_exclusive_group(required=True)
    which.add_argument("--report-id")
    which.add_argument("--all", action="store_true")
    delete.add_argument("--confirm-delete", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "import":
            result = import_report(args.db, args.input, args.policy)
        elif args.command == "status":
            result = status(args.db)
        elif args.command == "backup":
            result = backup(args.db, args.output)
        elif args.command == "restore":
            result = restore(args.input, args.db)
        else:
            result = purge(args.db, args.report_id, args.all, args.confirm_delete)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except (HistoryError, ValueError, OSError, sqlite3.Error) as exc:
        print("SOVIA history error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
