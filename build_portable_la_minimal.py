"""New, unmerged 0.15 synthetic SOVIA portable. Old packages unchanged."""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
DEFAULT_NAME = "SOVIA-LA-Minimal-0.15.0-beta.zip"


def _local(filename, alias):
    spec = spec_from_file_location(alias, ROOT / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_MINIMAL_COMPONENT_UNAVAILABLE")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


verify = _local("verify_portable_la_minimal.py", "_sovia_minimal_builder_verify")
_writer = _local("build_portable_v012.py", "_sovia_minimal_builder_core")
_writer.verify = verify
_writer.DEFAULT_NAME = DEFAULT_NAME

BuildError = _writer.BuildError
make_payload = _writer.make_payload
package_bytes = _writer.package_bytes
build = _writer.build


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build unsigned synthetic SOVIA v0.15 ZIP")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.output), sort_keys=True, ensure_ascii=False))
        return 0
    except (BuildError, verify.PackageError, OSError, ValueError):
        print(json.dumps({"status": "REJECTED", "error_code": "MINIMAL_BUILD_REFUSED"}),
              file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
