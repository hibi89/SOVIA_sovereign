"""Separate source-only deterministic 0.14 delta review ZIP.

No mutation of the historical v0.13 package, frozen versions or defaults.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_NAME = "SOVIA-LA-Delta-0.14.0-beta.zip"


def _local(filename, alias):
    spec = spec_from_file_location(alias, ROOT / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_DELTA_COMPONENT_MISSING")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verify = _local("verify_portable_la_delta.py", "_sovia_delta_candidate_verify")
_writer = _local("build_portable_v012.py", "_sovia_delta_candidate_writer")
_writer.verify = verify
_writer.DEFAULT_NAME = DEFAULT_NAME

BuildError = _writer.BuildError
make_payload = _writer.make_payload
package_bytes = _writer.package_bytes
build = _writer.build


def main(argv=None):
    p = argparse.ArgumentParser(description="Build separate unsigned 0.14 LA delta review candidate")
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    try:
        print(json.dumps(build(args.output), sort_keys=True, ensure_ascii=False))
        return 0
    except (BuildError, verify.PackageError, OSError, ValueError):
        print(json.dumps({"status":"REJECTED","error_code":"DELTA_BUILD_REFUSED"}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
