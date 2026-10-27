"""Reproducible, no-clobber SOVIA v0.11.2-beta isolated ZIP from a fixed public allowlist.

Build only synthetic examples + core offline Python scripts. No tree walk,
external dependencies, customer records, repo settings or network calls.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile
import zipfile

from importlib.util import module_from_spec, spec_from_file_location

# Python -I intentionally omits the script directory from import lookup.
# Load only our adjacent explicit P2 verifier, even in isolated mode.
_spec = spec_from_file_location("_sovia_bundle_p2_verifier", Path(__file__).resolve().with_name("verify_portable_p2.py"))
if _spec is None or _spec.loader is None:
    raise RuntimeError("LOCAL_P2_VERIFIER_UNAVAILABLE")
verify = module_from_spec(_spec)
_spec.loader.exec_module(verify)

ROOT = Path(__file__).resolve().parent
DEFAULT_NAME = "SOVIA-Audit-Lite-0.11.2-beta.zip"
TEXT_SUFFIXES = (".py", ".json", ".csv", ".md")


class BuildError(ValueError):
    """Cannot build a safe deterministic portable artifact."""


def make_payload(root=ROOT):
    """Select exactly the predetermined files; normalize Windows CRLF to LF."""
    base = Path(root)
    values = {}
    for name in verify.FILES:
        source = base / name
        if source.is_symlink() or not source.is_file():
            raise BuildError("Allowlisted source missing/symlinked: " + name)
        if source.stat().st_size > verify.MAX_FILE_BYTES:
            raise BuildError("Allowlisted source too large: " + name)
        contents = source.read_bytes()
        if name.endswith(".cmd"):
            # Batch entrypoint must keep canonical CRLF on Windows/Ubuntu builds.
            contents = contents.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
        if name.endswith(TEXT_SUFFIXES):
            contents = contents.replace(b"\r\n", b"\n")
            try:
                contents.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise BuildError("Non UTF-8 payload: " + name) from exc
        if len(contents) > verify.MAX_FILE_BYTES:
            raise BuildError("Payload too large: " + name)
        values[name] = contents
    if sum(len(v) for v in values.values()) > verify.MAX_TOTAL_BYTES:
        raise BuildError("Total payload too large")
    return values


def package_bytes(root=ROOT):
    """Create stable ZIP member bytes, order, permissions and timestamps."""
    payload = make_payload(root)
    manifest = {
        "format": verify.FORMAT,
        "version": verify.VERSION,
        "files": {
            name: {"bytes": len(payload[name]), "sha256": hashlib.sha256(payload[name]).hexdigest()}
            for name in sorted(payload)
        },
    }
    payload[verify.MANIFEST] = (
        json.dumps(manifest, ensure_ascii=False, sort_keys=True,
                   separators=(",", ":")) + "\n"
    ).encode("utf-8")
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as z:
        for name in sorted(payload):
            info = zipfile.ZipInfo(verify.PREFIX + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o100644 << 16
            info.flag_bits = 0
            z.writestr(info, payload[name])
    data = out.getvalue()
    if len(data) > verify.MAX_ARCHIVE_BYTES:
        raise BuildError("Output ZIP exceeds maximum size")
    return data


def _atomic_publish(items):
    """Create only fresh paths, stage complete bytes and hardlink exclusively."""
    stages = []
    published = []
    try:
        for target, _ in items:
            if target.exists() or target.is_symlink():
                raise BuildError("Existing artifact must never be overwritten")
            if not target.parent.is_dir():
                raise BuildError("Output directory must exist")
        if len({path.resolve() for path, _ in items}) != len(items):
            raise BuildError("Artifact paths must differ")
        for target, data in items:
            # Reject unexpected payload before opening a stage descriptor.
            if type(data) is not bytes:
                raise BuildError("Portable payload must be bytes")
            fd, temp_name = tempfile.mkstemp(prefix=".sovia-portable-", suffix=".tmp",
                                             dir=target.parent)
            tmp = Path(temp_name)
            stages.append(tmp)
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
        for (target, _), stage in zip(items, stages):
            # Capture inode BEFORE publishing; a post-link metadata failure
            # would otherwise leave an untracked published output on rollback.
            st = os.stat(stage)
            os.link(stage, target)
            published.append((target, st.st_dev, st.st_ino))
    except Exception:
        for target, device, inode in published:
            try:
                state = os.stat(target)
                if (state.st_dev, state.st_ino) == (device, inode):
                    target.unlink()
            except OSError:
                pass
        raise
    finally:
        for stage in stages:
            stage.unlink(missing_ok=True)


def build(output_path, root=ROOT):
    archive = Path(output_path).absolute()
    if archive.name != DEFAULT_NAME:
        raise BuildError("Use the fixed public beta archive filename: " + DEFAULT_NAME)
    checksum = archive.with_name(archive.name + ".sha256")
    data = package_bytes(root)
    digest = hashlib.sha256(data).hexdigest()
    checksum_data = (digest + "  " + archive.name + "\n").encode("ascii")
    _atomic_publish([(archive, data), (checksum, checksum_data)])
    verify.verify_archive(archive, checksum)
    return {"status": "built_verified", "zip": str(archive), "sha256_file": str(checksum),
            "sha256": digest, "files": len(verify.FILES), "bytes": len(data)}


def main(argv=None):
    p = argparse.ArgumentParser(description="Build reproducible SOVIA Audit Lite offline beta ZIP")
    p.add_argument("--output", required=True, help="NEW SOVIA-Audit-Lite-0.11.2-beta.zip path")
    args = p.parse_args(argv)
    try:
        print(json.dumps(build(args.output), ensure_ascii=False, sort_keys=True))
        return 0
    except (BuildError, verify.PackageError, OSError, ValueError,
            zipfile.BadZipFile) as exc:
        print("SOVIA portable build error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
