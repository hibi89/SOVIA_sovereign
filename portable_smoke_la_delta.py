"""P39: real isolated synthetic 0.14 ZIP extract and P38 delta end-to-end."""
from __future__ import annotations

import json
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import subprocess
import sys
import tempfile


def _local(filename, alias):
    spec = spec_from_file_location(alias, Path(__file__).resolve().with_name(filename))
    if spec is None or spec.loader is None:
        raise RuntimeError("LOCAL_DELTA_SMOKE_COMPONENT_MISSING")
    mod = module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_builder = _local("build_portable_la_delta.py", "_sovia_delta_smoke_builder")
_verifier = _local("verify_portable_la_delta.py", "_sovia_delta_smoke_verify")


def _cli(script, *args, expected=0):
    proc = subprocess.run([sys.executable, "-I", "-B", str(script),
                           *[str(x) for x in args]],
                          capture_output=True, text=True, timeout=40)
    if proc.returncode != expected:
        raise RuntimeError("ISOLATED_DELTA_CLI_STATUS_MISMATCH")
    return json.loads(proc.stderr if expected else proc.stdout)


def smoke():
    with tempfile.TemporaryDirectory(prefix="sovia-la-delta-") as tmp:
        root = Path(tmp)
        archive = root / _builder.DEFAULT_NAME
        receipt = _builder.build(archive)
        installation = root / "clean"
        _verifier.extract_verified(archive, installation,
                                    archive.with_name(archive.name + ".sha256"))
        _verifier.verify_directory(installation)
        review = installation / "sovia_la_owner_review.py"
        before, after = root / "before", root / "after"
        args = ("--plan", installation / "examples/demo_la_plan_review.json",
                "--policy", installation / "examples/demo_policy.json")
        first = _cli(review, *args,
                     "--observations", installation / "examples/demo_la_observations.json",
                     "--output-dir", before, "--synthetic-only")
        second = _cli(review, *args,
                      "--observations", installation / "examples/demo_la_observations_gap.json",
                      "--output-dir", after, "--synthetic-only")
        if (first["review_status"] != "SYNTHETIC_REVIEW_REQUIRED" or
                second["review_status"] != "SYNTHETIC_REVIEW_REQUIRED"):
            raise RuntimeError("DELTA_RISK_FALSE_CLEAR")
        delta_script = installation / "sovia_la_review_delta.py"
        compared = _cli(delta_script, "--previous", before, "--current", after,
                        "--synthetic-only")
        if (compared["status"] != "REVIEW_REQUIRED_UNAUTHENTICATED" or
                compared["observation_count_change"] != -1 or
                compared["severity_increases"] < 1 or
                compared["risk_clearance_verified"] is not False):
            raise RuntimeError("DELTA_REPORT_INVALID")
        payload = json.dumps(compared)
        if any(value in payload for value in ("synthetic:lookup", "synthetic:write",
                                              "source_pointer", "event_id", "target_code")):
            raise RuntimeError("SENSITIVE_DELTA_DATA_EXPOSED")
        again = _cli(review, *args,
                     "--observations", installation / "examples/demo_la_observations.json",
                     "--output-dir", before, "--synthetic-only", expected=2)
        if again["error_code"] != "OUTPUT_EXISTS":
            raise RuntimeError("DELTA_SOURCE_OVERWRITE_ALLOWED")
        (after / "review.html").write_text("tampered", encoding="utf-8")
        bad = _cli(delta_script, "--previous", before, "--current", after,
                   "--synthetic-only", expected=2)
        if bad["error_code"] != "INTEGRITY_MISMATCH":
            raise RuntimeError("DELTA_TAMPER_NOT_DETECTED")
        _verifier.verify_directory(installation)
        return {
            "status": "SYNTHETIC_LA_DELTA_V014_CLEAN_INSTALL_PASS",
            "files": receipt["files"], "zip_sha256": receipt["sha256"],
            "isolated_cli": True, "risk_increase_detected": True,
            "no_raw_source_export": True, "no_overwrite": True,
            "tamper_refusal": True, "real_la_integration_verified": False,
            "commercial_release_approved": False,
        }


if __name__ == "__main__":
    print(json.dumps(smoke(), sort_keys=True))
