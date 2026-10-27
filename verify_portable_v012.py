"""Offline, strict allowlist verifier/extractor for SEPARATE SOVIA v0.12.0-beta candidate.

No network, package installer, customer data, permission changes or code execution.
A matching .sha256 beside an archive is a transport checksum, NOT a signature.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

VERSION = "0.12.0-beta"
FORMAT = "SOVIA_PORTABLE_V012_V1"
PREFIX = "SOVIA-V012/"
FILES = (
    "sovia_audit.py",
    "sovia_audit_v012.py",
    "sovia_pii_preflight.py",
    "sovia_report_print_preview.py",
    "sovia_history_v012.py",
    "verify_portable_v012.py",
    "V012_PORTABLE_README.md",
    "examples/demo_five_rules.json",
    "examples/demo_temporal_boundary.json",
)
MANIFEST = "MANIFEST.json"
MAX_FILE_BYTES = 2_097_152
MAX_TOTAL_BYTES = 8_388_608
MAX_MANIFEST_BYTES = 16_384
MAX_ARCHIVE_BYTES = 12_582_912
HEX = re.compile(r"^[0-9a-f]{64}$")
CHECKSUM = re.compile(r"^([0-9a-f]{64})  ([A-Za-z0-9_.-]+\.zip)\n$")


class PackageError(ValueError):
    """A portable package failed structural, content or destination validation."""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _check_manifest(raw):
    if len(raw) > MAX_MANIFEST_BYTES:
        raise PackageError("Manifest exceeds allowed size")
    try:
        doc = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PackageError("Invalid UTF-8 manifest JSON") from exc
    if (type(doc) is not dict or set(doc) != {"format", "version", "files"}
            or doc["format"] != FORMAT or doc["version"] != VERSION
            or type(doc["files"]) is not dict or set(doc["files"]) != set(FILES)):
        raise PackageError("Manifest format or explicit payload allowlist mismatch")
    total = 0
    for name in FILES:
        entry = doc["files"][name]
        if (type(entry) is not dict or set(entry) != {"bytes", "sha256"}
                or type(entry["bytes"]) is not int
                or entry["bytes"] < 0 or entry["bytes"] > MAX_FILE_BYTES
                or type(entry["sha256"]) is not str
                or HEX.fullmatch(entry["sha256"]) is None):
            raise PackageError("Invalid manifest file entry: " + name)
        total += entry["bytes"]
    if total > MAX_TOTAL_BYTES:
        raise PackageError("Portable payload exceeds limit")
    return doc


def _validate_checksum(archive, digest, checksum_path):
    if checksum_path is None:
        return
    path = Path(checksum_path)
    if path.is_symlink() or not path.is_file():
        raise PackageError("Detached checksum missing or symlink")
    if path.stat().st_size > 256:
        raise PackageError("Detached checksum too long")
    try:
        line = path.read_text(encoding="ascii")
    except UnicodeError as exc:
        raise PackageError("Detached checksum must be ASCII") from exc
    parsed = CHECKSUM.fullmatch(line)
    if parsed is None or parsed.group(2) != archive.name:
        raise PackageError("Detached checksum format or archive name mismatch")
    if not hmac.compare_digest(parsed.group(1), digest):
        raise PackageError("Detached SHA-256 mismatch")


def verify_archive(archive_path, checksum_path=None):
    """Strictly read and verify each member; never extract during verification."""
    archive = Path(archive_path)
    if archive.is_symlink() or not archive.is_file():
        raise PackageError("Archive missing or symlinked")
    if archive.stat().st_size > MAX_ARCHIVE_BYTES:
        raise PackageError("Archive exceeds size limit")
    _validate_checksum(archive, _sha(archive.read_bytes()), checksum_path)
    try:
        with zipfile.ZipFile(archive, "r") as z:
            infos = z.infolist()
            expected = {PREFIX + filename for filename in FILES} | {PREFIX + MANIFEST}
            observed = [info.filename for info in infos]
            if len(infos) != len(expected) or set(observed) != expected:
                raise PackageError("ZIP has missing, extra, duplicate or unsafe names")
            if z.comment:
                raise PackageError("ZIP global comment is unsupported")
            for info in infos:
                mode = (info.external_attr >> 16) & 0o170000
                if (info.is_dir() or info.flag_bits & 1 or info.compress_type != zipfile.ZIP_STORED
                        or info.file_size > MAX_FILE_BYTES
                        or mode not in (0, 0o100000)):
                    raise PackageError("ZIP entry has unsupported type/size/encryption")
                if info.filename == PREFIX + MANIFEST and info.file_size > MAX_MANIFEST_BYTES:
                    raise PackageError("Manifest entry is oversized")
            meta = _check_manifest(z.read(PREFIX + MANIFEST))
            for filename in FILES:
                data = z.read(PREFIX + filename)
                entry = meta["files"][filename]
                if len(data) != entry["bytes"] or not hmac.compare_digest(_sha(data), entry["sha256"]):
                    raise PackageError("Member checksum mismatch: " + filename)
            return {"status": "verified", "version": VERSION,
                    "files": len(FILES), "archive_sha256": _sha(archive.read_bytes())}
    except (zipfile.BadZipFile, RuntimeError, EOFError) as exc:
        raise PackageError("Malformed ZIP archive") from exc


def verify_directory(root_path):
    """Verify pristine extracted payload before adding local generated reports."""
    root = Path(root_path)
    if not root.is_dir() or root.is_symlink():
        raise PackageError("Extraction directory absent or symlinked")
    expected = set(FILES) | {MANIFEST}
    allowed_directories = {
        "/".join(filename.split("/")[:depth])
        for filename in expected
        for depth in range(1, len(filename.split("/")))
    }
    found = set()
    for entry in root.rglob("*"):
        name = entry.relative_to(root).as_posix()
        if entry.is_symlink():
            raise PackageError("Symlink in extracted payload")
        if entry.is_file():
            if name not in expected:
                raise PackageError("Unexpected extracted file")
            found.add(name)
        elif entry.is_dir():
            if name not in allowed_directories:
                raise PackageError("Unexpected extracted directory")
        else:
            raise PackageError("Unsupported extracted entry")
    if found != expected:
        raise PackageError("Extracted payload missing files")
    manifest = root / MANIFEST
    if manifest.stat().st_size > MAX_MANIFEST_BYTES:
        raise PackageError("Manifest too large")
    doc = _check_manifest(manifest.read_bytes())
    for filename in FILES:
        path = root / filename
        if path.stat().st_size > MAX_FILE_BYTES:
            raise PackageError("Extracted payload exceeds file size bound")
        data = path.read_bytes()
        entry = doc["files"][filename]
        if len(data) != entry["bytes"] or not hmac.compare_digest(_sha(data), entry["sha256"]):
            raise PackageError("Extracted content checksum mismatch: " + filename)
    return {"status": "verified_directory", "version": VERSION, "files": len(FILES)}


def extract_verified(archive_path, destination, checksum_path=None):
    """Verify first; extract only fixed allowlisted paths into a new destination."""
    verified = verify_archive(archive_path, checksum_path)
    # Pin the exact bytes that will be extracted. A locally replaced archive
    # between verification and extraction must never be trusted implicitly.
    # This bounded copy is held in memory and is NOT written to disk.
    archive = Path(archive_path)
    if archive.is_symlink() or not archive.is_file():
        raise PackageError("Archive changed after verification")
    data = archive.read_bytes()
    if (len(data) > MAX_ARCHIVE_BYTES or
            not hmac.compare_digest(_sha(data), verified["archive_sha256"])):
        raise PackageError("Archive changed after verification")
    target = Path(destination).absolute()
    if not target.parent.is_dir() or target.exists() or target.is_symlink():
        raise PackageError("Extraction destination must be new under an existing directory")
    # Creating the new directory fails instead of overwriting a pre-existing path.
    target.mkdir()
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for name in FILES + (MANIFEST,):
                target_file = target / name
                target_file.parent.mkdir(exist_ok=True, parents=True)
                with target_file.open("xb") as stream:
                    stream.write(z.read(PREFIX + name))
                    stream.flush()
                    os.fsync(stream.fileno())
        verify_directory(target)
    except Exception:
        # Only the newly-created target is cleaned. Interrupted extraction
        # may leave partial files; no crash-atomic filesystem claim.
        shutil.rmtree(target)
        raise
    return {"status": "extracted_verified", "directory": str(target),
            "files": verified["files"], "archive_sha256": verified["archive_sha256"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline SOVIA v0.11 candidate integrity verifier")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--archive", help="Check a portable ZIP without extracting")
    mode.add_argument("--directory", help="Check a pristine unpacked SOVIA folder")
    parser.add_argument("--sha256-file", help="Optional detached SHA-256 checksum file for ZIP")
    parser.add_argument("--extract-to", help="Extract into a NEW unused directory only after checking ZIP")
    args = parser.parse_args(argv)
    try:
        if args.directory:
            if args.extract_to or args.sha256_file:
                raise PackageError("--directory does not support --extract-to or --sha256-file")
            result = verify_directory(args.directory)
        elif args.extract_to:
            result = extract_verified(args.archive, args.extract_to, args.sha256_file)
        else:
            result = verify_archive(args.archive, args.sha256_file)
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
        return 0
    except (PackageError, OSError, ValueError, zipfile.BadZipFile) as exc:
        print("SOVIA portable verification error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
