"""Build a separate deterministic synthetic LA-owner review candidate ZIP.

No historical v0.12 artifacts or source are modified. Development-only
builder reuses the existing verified ZIP writer in its own module namespace.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_NAME = "SOVIA-LA-Review-0.13.0-beta.zip"


def _local(filename, alias):
    spec = spec_from_file_location(alias, ROOT / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_BUNDLE_COMPONENT_MISSING")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


verify = _local("verify_portable_la_review.py", "_sovia_la_candidate_verify")
_writer = _local("build_portable_v012.py", "_sovia_la_candidate_writer")
# Both imports are private module objects. This cannot mutate the original
# v0.12 module or its historical ZIP content/digests.
_writer.verify = verify
_writer.DEFAULT_NAME = DEFAULT_NAME

BuildError = _writer.BuildError
make_payload = _writer.make_payload
package_bytes = _writer.package_bytes
build = _writer.build


def main(argv=None):
    p = argparse.ArgumentParser(description="Build separate unsigned SOVIA LA review ZIP")
    p.add_argument("--output", required=True)
    args = p.parse_args(argv)
    try:
        print(json.dumps(build(args.output), ensure_ascii=False, sort_keys=True))
        return 0
    except (BuildError, verify.PackageError, OSError, ValueError) as exc:
        print(json.dumps({"status": "REJECTED", "error_code": "PORTABLE_BUILD_REJECTED"}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
