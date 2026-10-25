"""Strict, bounded, offline source-CSV importer for SOVIA canonical events.

Only the metadata allowlist is ingested; raw prompts or unknown headers are rejected.
The caller owns policy loading, canonical validation and findings evaluation.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path

MAX_CSV_BYTES = 1_048_576
MAX_CSV_EVENTS = 1_000
CSV_FIELDS = (
    "event_id", "occurred_at_utc", "agent_id", "run_id", "tool_name",
    "target", "destination_domain", "permission_asserted", "outcome", "source_pointer",
)
REQUIRED_FIELDS = frozenset(("event_id", "occurred_at_utc", "agent_id", "run_id", "tool_name"))


class CSVInputError(ValueError):
    """Untrusted source CSV is invalid, never partially accepted."""


def read_csv_events(path):
    """Return allowed event metadata, keeping all tool/prompt strings as inert data.

    File size, record count, header uniqueness, column count, UTF-8, and strict CSV
    quoting are validated before any report generation. Permission uses exact
    lower-case true/false; blank means not asserted/unknown, never true.
    """
    source = Path(path)
    if not source.is_file():
        raise CSVInputError("CSV source file not found")
    with source.open("rb") as stream:
        data = stream.read(MAX_CSV_BYTES + 1)
    if len(data) > MAX_CSV_BYTES:
        raise CSVInputError("CSV source too large (max 1 MiB)")
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise CSVInputError("CSV source must be UTF-8") from exc
    if "\x00" in text:
        raise CSVInputError("CSV source contains a NUL byte")
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), restkey="__EXTRA__", strict=True)
        headers = reader.fieldnames
        if not headers or len(headers) != len(set(headers)):
            raise CSVInputError("CSV requires one header row with unique columns")
        if not REQUIRED_FIELDS.issubset(headers) or any(key not in CSV_FIELDS for key in headers):
            raise CSVInputError("CSV header contains unknown columns or lacks required event fields")
        events = []
        for row in reader:
            if len(events) >= MAX_CSV_EVENTS:
                raise CSVInputError("CSV event limit exceeded (max 1000)")
            if "__EXTRA__" in row or any(row[name] is None for name in headers):
                raise CSVInputError("CSV row has missing or extra columns")
            event = {}
            for name in headers:
                value = row[name]
                if name == "permission_asserted":
                    if value == "":
                        continue
                    if value not in ("true", "false"):
                        raise CSVInputError("permission_asserted must be true, false or empty")
                    event[name] = value == "true"
                elif value != "":
                    event[name] = value
            events.append(event)
        return events
    except csv.Error as exc:
        raise CSVInputError("Malformed CSV quoting or row data") from exc
