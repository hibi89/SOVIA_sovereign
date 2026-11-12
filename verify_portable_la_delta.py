"""Separate deterministic 0.14 synthetic LA review+delta beta verifier.

Preserves 0.13 and earlier modules under distinct private module instances.
A checksum checks transport consistency, never source authenticity or permission.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

VERSION = "0.14.0-la-delta-beta"
FORMAT = "SOVIA_PORTABLE_LA_DELTA_V1"
PREFIX = "SOVIA-LA-DELTA/"
MANIFEST = "MANIFEST.json"
EXTRA_FILES = (
    "sovia_la_review_delta.py",
    "verify_portable_la_delta.py",
    "RUN_LA_DELTA.cmd",
    "LA_DELTA_PORTABLE_README.md",
    "examples/demo_la_observations_gap.json",
)

_source = Path(__file__).resolve().with_name("verify_portable_la_review.py")
_spec = spec_from_file_location("_sovia_delta_isolated_v013_verifier", _source)
if _spec is None or _spec.loader is None:
    raise RuntimeError("LOCAL_V013_VERIFIER_UNAVAILABLE")
_prior = module_from_spec(_spec)
_spec.loader.exec_module(_prior)

FILES = _prior.FILES + EXTRA_FILES
_backend = _prior._backend
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
    parser = argparse.ArgumentParser(description="Unsigned synthetic SOVIA LA delta package verifier")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--archive")
    group.add_argument("--directory")
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
        print(json.dumps({"status":"REJECTED","error_code":"DELTA_PACKAGE_REFUSED"}),
              file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
