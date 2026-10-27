"""Source-only 0.12 experimental UTC temporal auditor. Not a commercial release.

Original sovia_audit.py and historical portable archives remain immutable.
Reuses strict legacy parsing and four rules; recomputes only BURST_TOOLS.
"""
from __future__ import annotations
import argparse
from collections import defaultdict, deque
from datetime import datetime, timedelta
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sys

VERSION = "0.12.0-preview"
MAX_OUTPUT_BYTES = 4_194_304  # local synthetic test budget, not customer quota

class CandidateError(ValueError):
    """Constant non-disclosing error codes."""

def _sibling(filename, alias):
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise CandidateError("DEPENDENCY_UNAVAILABLE")
    mod = module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except (OSError, ImportError) as exc:
        raise CandidateError("DEPENDENCY_UNAVAILABLE") from exc
    return mod

def _when(event):
    # Strict original evaluator has normalized all source timestamps to UTC.
    return datetime.fromisoformat(event["occurred_at_utc"].replace("Z", "+00:00"))

def evaluate(document, *, legacy_audit=None):
    """Correct 60s finding semantics without modifying any original objects.

    Same report_id for same normalized source: legacy SQLite history MUST NOT
    accept mixed versions until a separately designed identity migration.
    """
    core = legacy_audit if legacy_audit is not None else _sibling(
        "sovia_audit.py", "_sovia_v012_legacy"
    )
    original = core.evaluate(document)
    findings = [f for f in original["findings"] if f["rule_id"] != "BURST_TOOLS"]
    threshold = document["policy"].get("max_tool_calls_per_minute")
    if threshold is not None:
        windows = defaultdict(deque)
        for event in sorted(original["events"], key=lambda e: (_when(e), e["event_id"])):
            instant = _when(event)
            window = windows[(event["agent_id"], event["run_id"])]
            while window and instant - window[0] >= timedelta(seconds=60):
                window.popleft()
            window.append(instant)
            if len(window) > threshold:
                ident = event["event_id"]
                findings.append({
                    "finding_id": "BURST_TOOLS:" + ident,
                    "rule_id": "BURST_TOOLS",
                    "rule_version": "1.1",
                    "severity": "MEDIUM",
                    "event_ids": [ident],
                    "source_pointer": event["source_pointer"],
                    "evidence_status": (
                        "POINTER_PROVIDED_UNVERIFIED" if event["source_pointer"]
                        else "POINTER_MISSING"
                    ),
                    "rationale": (
                        f"같은 실행에서 60초 이내 호출 {len(window)}건 "
                        f"(설정 한도 {threshold}건 초과)"
                    ),
                    "recommended_action": "호출량 급증 원인과 승인된 자동화를 확인하세요.",
                })
    report = dict(original)
    report["findings"] = findings
    report["finding_count"] = len(findings)
    report["engine_version"] = VERSION
    return report


def write_synthetic_document(document, html_output, json_output, *, legacy_audit=None):
    """Render already-parsed synthetic metadata without a canonical JSON input file.

    Preserves the same heuristic PII screen, four existing rules plus corrected
    BURST_TOOLS, per-output budget and exclusive report writer as run_synthetic.
    Used by the offline n8n-like adapter; no upstream source authority implied.
    """
    targets = (Path(os.path.abspath(html_output)),
               Path(os.path.abspath(json_output)))
    if len({path.resolve() for path in targets}) != 2:
        raise CandidateError("PATH_COLLISION")
    if any(path.exists() or path.is_symlink() for path in targets):
        raise CandidateError("OUTPUT_EXISTS")
    if any(not path.parent.is_dir() for path in targets):
        raise CandidateError("OUTPUT_PARENT_MISSING")
    core = legacy_audit if legacy_audit is not None else _sibling(
        "sovia_audit.py", "_sovia_v012_memory_reader"
    )
    try:
        _sibling("sovia_pii_preflight.py", "_sovia_v012_memory_pii").assert_no_high_risk_patterns(
            document
        )
        result = evaluate(document, legacy_audit=core)
        data = (
            _sibling("sovia_report_print_preview.py", "_sovia_v012_memory_view")
            .render(result).encode("utf-8"),
            json.dumps(result, ensure_ascii=False, sort_keys=True,
                       indent=2, allow_nan=False).encode("utf-8"),
        )
        if any(len(payload) > MAX_OUTPUT_BYTES for payload in data):
            raise CandidateError("OUTPUT_LIMIT")
        if any(path.exists() or path.is_symlink() for path in targets):
            raise CandidateError("OUTPUT_EXISTS")
        if len({path.resolve() for path in targets}) != 2:
            raise CandidateError("PATH_COLLISION")
        core.write_reports_atomically(list(zip(targets, data)))
    except CandidateError:
        raise
    except (OSError, ValueError, TypeError, KeyError, UnicodeError,
            OverflowError, RecursionError) as exc:
        raise CandidateError("INPUT_OR_OUTPUT_REJECTED") from exc
    return {
        "status": "SYNTHETIC_V012_TEMPORAL_PREVIEW",
        "engine_version": VERSION,
        "events": result["event_count"],
        "findings": result["finding_count"],
        "historic_zip_modified": False,
        "legacy_history_compatible": False,
        "genuine_n8n_verified": False,
        "commercial_release_approved": False,
    }

def run_synthetic(input_path, html_output, json_output):
    source = Path(os.path.abspath(input_path))
    targets = (Path(os.path.abspath(html_output)), Path(os.path.abspath(json_output)))
    if source.is_symlink() or not source.is_file() or source.suffix.lower() != ".json":
        raise CandidateError("INVALID_SOURCE")
    if len({p.resolve() for p in targets}) != 2 or source.resolve() in {
            p.resolve() for p in targets}:
        raise CandidateError("PATH_COLLISION")
    if any(p.exists() or p.is_symlink() for p in targets):
        raise CandidateError("OUTPUT_EXISTS")
    if any(not p.parent.is_dir() for p in targets):
        raise CandidateError("OUTPUT_PARENT_MISSING")
    core = _sibling("sovia_audit.py", "_sovia_v012_reader")
    try:
        document = core.read_document(source)
        _sibling("sovia_pii_preflight.py", "_sovia_v012_pii").assert_no_high_risk_patterns(document)
        result = evaluate(document, legacy_audit=core)
        data = (_sibling("sovia_report_print_preview.py", "_sovia_v012_view").render(result).encode("utf-8"),
                json.dumps(result, ensure_ascii=False, sort_keys=True,
                           indent=2, allow_nan=False).encode("utf-8"))
        if any(len(payload) > MAX_OUTPUT_BYTES for payload in data):
            raise CandidateError("OUTPUT_LIMIT")
        if (any(p.exists() or p.is_symlink() for p in targets) or
                len({p.resolve() for p in targets}) != 2 or
                source.resolve() in {p.resolve() for p in targets}):
            raise CandidateError("PATH_COLLISION")
        core.write_reports_atomically(list(zip(targets, data)))
    except CandidateError:
        raise
    except (OSError, ValueError, TypeError, KeyError, UnicodeError,
            OverflowError, RecursionError) as exc:
        raise CandidateError("INPUT_OR_OUTPUT_REJECTED") from exc
    return {"status": "SYNTHETIC_V012_TEMPORAL_PREVIEW", "engine_version": VERSION,
            "events": result["event_count"], "findings": result["finding_count"],
            "historic_zip_modified": False, "legacy_history_compatible": False,
            "genuine_n8n_verified": False, "commercial_release_approved": False}

def main(argv=None):
    p = argparse.ArgumentParser(description="0.12 offline synthetic temporal engine candidate")
    p.add_argument("--input", required=True)
    p.add_argument("--html-output", required=True)
    p.add_argument("--json-output", required=True)
    p.add_argument("--synthetic-only", action="store_true")
    args = p.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED", "error_code": "SYNTHETIC_ACK_REQUIRED"}), file=sys.stderr)
        return 2
    try:
        summary = run_synthetic(args.input, args.html_output, args.json_output)
    except CandidateError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
