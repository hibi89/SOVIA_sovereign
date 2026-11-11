"""Separate offline synthetic LA-review ZIP verifier, reusing proven v0.12 gates.

The historical v0.12 module is loaded under a NEW isolated module object and
its constants are specialized only in that object. Its original source,
historical package hashes and public entrypoints remain unchanged.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

VERSION = "0.13.0-la-review-beta"
FORMAT = "SOVIA_PORTABLE_LA_REVIEW_V1"
PREFIX = "SOVIA-LA-REVIEW/"
MANIFEST = "MANIFEST.json"
FILES = (
    "sovia_audit.py",
    "sovia_audit_v012.py",
    "sovia_pii_preflight.py",
    "sovia_la_plan_preflight.py",
    "sovia_la_plan_reconcile.py",
    "sovia_la_owner_review.py",
    "verify_portable_v012.py",
    "verify_portable_la_review.py",
    "RUN_LA_REVIEW.cmd",
    "LA_REVIEW_PORTABLE_README.md",
    "examples/demo_la_plan_review.json",
    "examples/demo_la_observations.json",
    "examples/demo_policy.json",
)

_source = Path(__file__).resolve().with_name("verify_portable_v012.py")
_spec = spec_from_file_location("_sovia_la_independent_portable_verifier", _source)
if _spec is None or _spec.loader is None:
    raise RuntimeError("LOCAL_V012_VERIFIER_UNAVAILABLE")
_backend = module_from_spec(_spec)
_spec.loader.exec_module(_backend)
_backend.VERSION = VERSION
_backend.FORMAT = FORMAT
_backend.PREFIX = PREFIX
_backend.FILES = FILES

MAX_FILE_BYTES = _backend.MAX_FILE_BYTES
MAX_TOTAL_BYTES = _backend.MAX_TOTAL_BYTES
MAX_MANIFEST_BYTES = _backend.MAX_MANIFEST_BYTES
MAX_ARCHIVE_BYTES = _backend.MAX_ARCHIVE_BYTES
PackageError = _backend.PackageError
verify_archive = _backend.verify_archive
verify_directory = _backend.verify_directory
extract_verified = _backend.extract_verified


def main(argv=None):
    parser = argparse.ArgumentParser(description="Separate SOVIA synthetic LA reviewer package verifier")
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--archive")
    modes.add_argument("--directory")
    parser.add_argument("--sha256-file")
    parser.add_argument("--extract-to")
    args = parser.parse_args(argv)
    try:
        if args.directory:
            if args.sha256_file or args.extract_to:
                raise PackageError("INVALID_DIRECTORY_VERIFY_MODE")
            result = verify_directory(args.directory)
        elif args.extract_to:
            result = extract_verified(args.archive, args.extract_to, args.sha256_file)
        else:
            result = verify_archive(args.archive, args.sha256_file)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "REJECTED", "error_code": "PORTABLE_VERIFY_REJECTED"}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
