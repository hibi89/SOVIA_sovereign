"""P42: end-to-end clean extraction of independent SOVIA v0.15 synthetic package."""
from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


def _local(filename, alias):
    spec = spec_from_file_location(alias, Path(__file__).resolve().with_name(filename))
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_MINIMAL_SMOKE_COMPONENT_MISSING")
    m = module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


build = _local("build_portable_la_minimal.py", "_sovia_minimal_smoke_builder")
verify = _local("verify_portable_la_minimal.py", "_sovia_minimal_smoke_verifier")


def _cli(path, *args, expect=0):
    p = subprocess.run([sys.executable, "-I", "-B", str(path), *[str(a) for a in args]],
                       capture_output=True, text=True, timeout=55)
    if p.returncode != expect:
        raise RuntimeError("MINIMAL_CANDIDATE_ISOLATED_CLI_STATUS_MISMATCH")
    return json.loads(p.stderr if expect else p.stdout)


def smoke():
    with TemporaryDirectory(prefix="sovia-p42-v015-") as tmp:
        home = Path(tmp)
        archive = home / build.DEFAULT_NAME
        made = build.build(archive)
        root = home / "clean"
        verify.extract_verified(archive, root, home / (archive.name + ".sha256"))
        verify.verify_directory(root)
        demo = root / "sovia_la_minimal_demo.py"
        folder = home / "output"
        first = _cli(demo, "--output-dir", folder, "--synthetic-only")
        if (first["status"] != "SOVIA_V015_FABRICATED_LA_LIKE_DEMO_PASS_NOT_AUTHENTICATED" or
                first["source_authenticated"] is not False or
                not first["risk_findings_preserved"]):
            raise RuntimeError("MINIMAL_DEMO_FALSE_CLEAR")
        source = folder / "fabricated-la-like-projection.json"
        review = folder / "synthetic-review"
        original = source.read_bytes()
        compare = root / "sovia_la_minimal_projection.py"
        actual = _cli(compare, "--projection", source, "--review-dir", review, "--synthetic-only")
        if actual["status"] != "REVIEW_REQUIRED_NOT_AUTHENTICATED":
            raise RuntimeError("MINIMAL_PROJECTION_FALSE_CLEAR")
        denied = _cli(demo, "--output-dir", folder, "--synthetic-only", expect=2)
        if denied["error_code"] != "OUTPUT_EXISTS_OR_PARENT_MISSING" or source.read_bytes() != original:
            raise RuntimeError("DEMO_REEXECUTION_OVERWROTE_OUTPUT")
        (review / "review.html").write_text("tampered", encoding="utf-8")
        bad = _cli(compare, "--projection", source, "--review-dir", review, "--synthetic-only",
                   expect=2)
        if bad["error_code"] != "INTEGRITY_MISMATCH":
            raise RuntimeError("MINIMAL_REPORT_TAMPER_NOT_REJECTED")
        verify.verify_directory(root)
        return {
            "status": "SOVIA_V015_MINIMAL_PORTABLE_CLEAN_EXTRACT_PASS",
            "files": made["files"], "zip_sha256": made["sha256"],
            "source_only": True, "tamper_rejected": True, "no_overwrite": True,
            "risk_review_retained": True, "real_la_execution_in_this_package": False,
            "retail_approved": False,
        }


if __name__ == "__main__":
    print(json.dumps(smoke(), sort_keys=True))
