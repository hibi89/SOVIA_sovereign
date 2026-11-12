"""SOVIA 0.15 synthetic minimal LA-claim candidate: fixed independent verifier.

Reuses the older *isolated module instance*, never changes historic v0.14.
Checks source-inventory bytes only, not authenticity, owner consent or signing.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

VERSION = "0.15.0-la-minimal-beta"
FORMAT = "SOVIA_PORTABLE_LA_MINIMAL_V1"
PREFIX = "SOVIA-LA-MINIMAL/"
MANIFEST = "MANIFEST.json"
ADDED = (
    "sovia_la_minimal_projection.py",
    "sovia_la_minimal_demo.py",
    "verify_portable_la_minimal.py",
    "RUN_LA_MINIMAL.cmd",
    "LA_MINIMAL_PORTABLE_README.md",
)
_spec = spec_from_file_location("_sovia_minimal_isolated_v014_verifier",
                                Path(__file__).resolve().with_name("verify_portable_la_delta.py"))
if _spec is None or _spec.loader is None:
    raise RuntimeError("LOCAL_MINIMAL_VERIFIER_UNAVAILABLE")
_previous = module_from_spec(_spec)
_spec.loader.exec_module(_previous)
FILES = _previous.FILES + ADDED
_backend = _previous._backend
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
    p = argparse.ArgumentParser(description="Verify unsigned, synthetic-only SOVIA v0.15 ZIP")
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--archive")
    mode.add_argument("--directory")
    p.add_argument("--sha256-file")
    p.add_argument("--extract-to")
    args = p.parse_args(argv)
    try:
        if args.directory:
            if args.sha256_file or args.extract_to:
                raise PackageError("INVALID_DIRECTORY_VERIFY_MODE")
            answer = verify_directory(args.directory)
        elif args.extract_to:
            answer = extract_verified(args.archive, args.extract_to, args.sha256_file)
        else:
            answer = verify_archive(args.archive, args.sha256_file)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "REJECTED", "error_code": "MINIMAL_PACKAGE_REFUSED"}),
              file=sys.stderr)
        return 2
    print(json.dumps(answer, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
