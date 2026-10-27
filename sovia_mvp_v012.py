"""SOVIA v0.12 one-command minimum working unit, offline synthetic-only.

Input: one canonical, locally supplied JSON fixture.
Output: new directory with report.html, report.json, history.sqlite3.
No genuine n8n API, customer integration, hosting or privacy certification.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sys
import tempfile


OUTPUTS = ("report.html", "report.json", "history.sqlite3")
INCOMPLETE_MARKER = ".SOVIA_INCOMPLETE"


class MVPError(ValueError):
    """Non-disclosing rejection codes."""


def _module(filename, alias):
    path = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise MVPError("COMPONENT_UNAVAILABLE")
    module = module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except (OSError, ImportError) as exc:
        raise MVPError("COMPONENT_UNAVAILABLE") from exc
    return module


def run(input_path, output_dir, *, synthetic_only=False,
        source_format="canonical", policy_path=None):
    """Preflight/run wholly in a staging directory, then publish fresh files.

    Directory and output files are individually exclusive, not a transaction
    for concurrent readers. A fail-closed marker distinguishes incomplete
    publication after interruption; ordinary failures roll back our own
    inode-matched files. Power loss still has no durability guarantee.
    """
    if synthetic_only is not True:
        raise MVPError("SYNTHETIC_ACK_REQUIRED")
    if source_format not in ("canonical", "n8n-sanitized"):
        raise MVPError("SOURCE_FORMAT_UNSUPPORTED")
    if (source_format == "n8n-sanitized") != (policy_path is not None):
        raise MVPError("POLICY_REQUIRED_ONLY_FOR_N8N")
    source = Path(os.path.abspath(input_path))
    target = Path(os.path.abspath(output_dir))
    if (not source.is_file() or source.is_symlink() or
            source.suffix.lower() != ".json"):
        raise MVPError("INVALID_SOURCE")
    if not target.parent.is_dir():
        raise MVPError("OUTPUT_PARENT_MISSING")
    if target.exists() or target.is_symlink():
        raise MVPError("OUTPUT_EXISTS")
    if source.resolve() == target.resolve():
        raise MVPError("PATH_COLLISION")
    policy = None
    if policy_path is not None:
        policy = Path(os.path.abspath(policy_path))
        if (policy.is_symlink() or not policy.is_file() or
                policy.suffix.lower() != ".json"):
            raise MVPError("INVALID_POLICY_SOURCE")
        if policy.resolve() == source.resolve():
            raise MVPError("SOURCE_POLICY_COLLISION")
    created = False
    published = []
    marker = target / INCOMPLETE_MARKER
    marker_identity = None
    try:
        with tempfile.TemporaryDirectory(
            prefix=".sovia-mvp-stage-", dir=target.parent
        ) as temp:
            stage = Path(temp)
            engine = _module("sovia_audit_v012.py", "_sovia_mvp_engine")
            history = _module("sovia_history_v012.py", "_sovia_mvp_history")
            if source_format == "n8n-sanitized":
                # Only pre-sanitized fabricated n8n-like metadata. No raw
                # execution import, network/API access or proof of consent.
                core = _module("sovia_audit.py", "_sovia_mvp_n8n_reader")
                pii = _module("sovia_pii_preflight.py", "_sovia_mvp_n8n_pii")
                adapter = _module("sovia_n8n_sanitized.py", "_sovia_mvp_n8n_adapter")
                source_document = core.read_document(source)
                policy_document = core.read_document(policy)
                pii.assert_no_high_risk_patterns(source_document, policy_document)
                canonical = adapter.convert(source_document, policy_document)
                # Pass the validated canonical object directly to the audit
                # and history. Never serialize an intermediate canonical JSON
                # file, including in the temporary staging directory.
                report = engine.write_synthetic_document(
                    canonical, stage / OUTPUTS[0], stage / OUTPUTS[1],
                    legacy_audit=core
                )
                entry = history.import_synthetic_document(
                    stage / OUTPUTS[2], canonical, legacy_audit=core
                )
            else:
                report = engine.run_synthetic(
                    source, stage / OUTPUTS[0], stage / OUTPUTS[1]
                )
                entry = history.import_synthetic(stage / OUTPUTS[2], source)
            if entry["status"] != "imported":
                raise MVPError("HISTORY_IMPORT_INCOMPLETE")
            if any(not (stage / name).is_file() for name in OUTPUTS):
                raise MVPError("OUTPUT_INCOMPLETE")
            # os.mkdir and os.link both refuse to overwrite existing targets.
            target.mkdir(mode=0o700)
            created = True
            # Leave an explicit incomplete marker before publishing any
            # report file. Its contents contain no input or private data.
            descriptor = os.open(
                marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
            )
            marker_stat = os.fstat(descriptor)
            marker_identity = (marker_stat.st_dev, marker_stat.st_ino)
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(b"SOVIA_SYNTHETIC_OUTPUT_INCOMPLETE\n")
                stream.flush()
                os.fsync(stream.fileno())
            for name in OUTPUTS:
                original = stage / name
                state = original.stat()
                destination = target / name
                os.link(original, destination)
                published.append((destination, state.st_dev, state.st_ino))
            marker_stat = marker.stat()
            if (marker_stat.st_dev, marker_stat.st_ino) != marker_identity:
                raise MVPError("OUTPUT_MARKER_CHANGED")
            marker.unlink()
            return {
                "status": "SYNTHETIC_V012_MVP_COMPLETE",
                "engine_version": report["engine_version"],
                "events": report["events"],
                "findings": report["findings"],
                "history_schema_version": history.SCHEMA_VERSION,
                "files": list(OUTPUTS),
                "source_format": source_format,
                "real_n8n_verified": False,
                "customer_release_approved": False,
            }
    except Exception as exc:
        if created:
            for path, device, inode in reversed(published):
                try:
                    current = path.stat()
                    if (current.st_dev, current.st_ino) == (device, inode):
                        path.unlink()
                except OSError:
                    pass
            if marker_identity is not None:
                try:
                    current = marker.stat()
                    if (current.st_dev, current.st_ino) == marker_identity:
                        marker.unlink()
                except OSError:
                    pass
            try:
                target.rmdir()
            except OSError:
                pass
        if isinstance(exc, MVPError):
            raise
        raise MVPError("MVP_INPUT_OR_OUTPUT_REJECTED") from exc


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="SOVIA v0.12 offline synthetic-only one-command MVP"
    )
    parser.add_argument("--input", required=True, help="synthetic canonical or pre-sanitized n8n-like JSON")
    parser.add_argument("--source-format", choices=("canonical", "n8n-sanitized"),
                        default="canonical")
    parser.add_argument("--policy", help="required for n8n-sanitized, forbidden for canonical")
    parser.add_argument("--output-dir", required=True, help="brand NEW directory")
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run(args.input, args.output_dir, synthetic_only=args.synthetic_only,
                     source_format=args.source_format, policy_path=args.policy)
    except (MVPError, OSError, ValueError, TypeError, RecursionError) as exc:
        code = str(exc) if isinstance(exc, MVPError) else "MVP_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
