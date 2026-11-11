"""Offline, synthetic-only LA review handoff: no source rows or API access.

Uses the existing plan, post-audit and correlation engines. Produces a new-only
static Korean review bundle. Manifest hashes detect accidental/incomplete
changes, not malicious replacement or genuine event provenance.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import hmac
import json
import os
from pathlib import Path
import stat
import sys

import sovia_la_plan_reconcile as engine
from sovia_audit import read_document

SCHEMA = "sovia.la_owner_review.v1"
FILES = ("review.json", "review.html", "manifest.json")
MAX_FILE = 1_048_576


class ReviewError(ValueError):
    """Opaque, non-disclosing operator refusal."""


def _json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       allow_nan=False, separators=(",", ":")) + "\n").encode("utf-8")


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _safe_path(path, *, expect_file=False):
    target = Path(os.path.abspath(path))
    for component in (target, *target.parents):
        try:
            info = component.lstat()
        except FileNotFoundError:
            if component != target:
                raise ReviewError("PARENT_MISSING")
            continue
        if (stat.S_ISLNK(info.st_mode) or
                bool(getattr(info, "st_file_attributes", 0) &
                     getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))):
            raise ReviewError("LINKED_PATH_REFUSED")
    if expect_file:
        try:
            info = target.stat()
        except OSError as exc:
            raise ReviewError("SOURCE_UNAVAILABLE") from exc
        if not stat.S_ISREG(info.st_mode):
            raise ReviewError("SOURCE_NOT_REGULAR")
    return target


def _esc(value):
    return html.escape(str(value), quote=True)


def render_html(review):
    """Script-free self-contained human review. No source content is rendered."""
    findings = review["reconciliation_findings"]
    rows = "".join(
        "<tr><td>" + _esc(item["step_or_event_id"]) + "</td><td>" +
        _esc(item["rule_id"]) + "</td><td>" + _esc(item["severity"]) +
        "</td></tr>"
        for item in findings
    ) or "<tr><td colspan='3'>계획·관측 식별자 차이 없음. 안전성 승인 아님.</td></tr>"
    limits = "".join("<li>" + _esc(x) + "</li>"
                     for x in review["coverage_limits"])
    return (
        "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta http-equiv='Content-Security-Policy' "
        "content=\"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'\">"
        "<title>SOVIA · LA 합성 검수</title>"
        "<style>body{margin:0;background:#111827;color:#e5edf7;"
        "font:16px system-ui,sans-serif}main{max-width:1050px;margin:auto;padding:32px}"
        "h1{font-size:30px}h2{margin-top:32px}strong{color:#fbbf24}"
        ".sub{color:#a5b4ca}.stats{display:flex;gap:12px;flex-wrap:wrap}"
        ".stat{background:#1f2937;padding:18px;border-radius:10px;min-width:115px}"
        "table{width:100%;border-collapse:collapse}td,th{border-bottom:1px solid #46536a;"
        "padding:11px;text-align:left;overflow-wrap:anywhere}li{margin:8px 0}"
        "@media print{body{background:#fff;color:#111} .stat{background:#eee}}"
        "</style></head><body><main>"
        "<p class='sub'>SOVIA / LOCAL FIRST / SYNTHETIC ONLY</p>"
        "<h1>Lightning Azent 실행 검수 초안</h1>"
        "<p><strong>실행 승인·증거 진위·실제 LA 연동 검증 아님.</strong> "
        "합성 계획과 제공된 관측 주장만 사후 대조합니다.</p>"
        "<h2>검토 상태: " + _esc(review["status"]) + "</h2>"
        "<section class='stats'>"
        + "".join("<div class='stat'><b>" + _esc(label) + "</b><p>" +
                  _esc(review[key]) + "</p></div>" for label, key in (
                      ("계획 단계", "planned_steps"), ("관측 이벤트", "observed_events"),
                      ("계획 위험", "plan_risk_finding_count"),
                      ("감사 위험", "post_audit_finding_count"),
                      ("대조 차이", "reconciliation_finding_count")))
        + "</section><h2>계획 ↔ 관측 차이</h2>"
        "<table><thead><tr><th>단계/이벤트</th><th>규칙</th><th>심각도</th>"
        "</tr></thead><tbody>" + rows + "</tbody></table>"
        "<h2>제약·미확인</h2><ul>" + limits + "</ul>"
        "<p class='sub'>정본 원본 입력은 이 폴더에 포함되지 않습니다. "
        "해시 목록은 서명이나 인증이 아니며, 누락된 사건은 미발생을 뜻하지 않습니다.</p>"
        "</main></body></html>\n"
    )


def _require_review_structure(result):
    if (type(result) is not dict or
            result.get("schema_version") != "sovia.plan_observation_reconcile.v1" or
            result.get("execution_authorized") is not False or
            result.get("real_la_integration_verified") is not False or
            result.get("observation_completeness_verified") is not False or
            type(result.get("reconciliation_findings")) is not list or
            result.get("reconciliation_finding_count") != len(result["reconciliation_findings"]) or
            result.get("status") not in ("SYNTHETIC_REVIEW_REQUIRED",
                                         "SYNTHETIC_MATCH_NOT_AUTHENTICATED")):
        raise ReviewError("REVIEW_SCHEMA_REFUSED")
    for key in ("planned_steps", "observed_events", "plan_risk_finding_count",
                "post_audit_finding_count", "reconciliation_finding_count"):
        if type(result.get(key)) is not int or not 0 <= result[key] <= 1000:
            raise ReviewError("REVIEW_SCHEMA_REFUSED")
    if result["status"] == "SYNTHETIC_MATCH_NOT_AUTHENTICATED" and (
        result["plan_risk_finding_count"] or
        result["post_audit_finding_count"] or
        result["reconciliation_finding_count"]
    ):
        raise ReviewError("RISK_STATUS_CONFLICT")
    return result


def _fresh_write(path, raw):
    # No overwrite even if a new path is created concurrently.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def create_bundle(plan_path, policy_path, observations_path, output_dir):
    sources = [_safe_path(p, expect_file=True)
               for p in (plan_path, policy_path, observations_path)]
    destination = _safe_path(output_dir)
    if not destination.parent.is_dir():
        raise ReviewError("OUTPUT_PARENT_MISSING")
    if destination.exists() or destination.is_symlink():
        raise ReviewError("OUTPUT_EXISTS")
    if destination in sources:
        raise ReviewError("OUTPUT_SOURCE_COLLISION")

    try:
        result = _require_review_structure(engine.reconcile(
            *(read_document(path) for path in sources)))
    except ReviewError:
        raise
    except (OSError, ValueError, TypeError, KeyError, OverflowError, RecursionError) as exc:
        raise ReviewError("SYNTHETIC_REVIEW_REJECTED") from exc

    body = _json_bytes(result)
    page = render_html(result).encode("utf-8")
    if max(len(body), len(page)) > MAX_FILE:
        raise ReviewError("REPORT_TOO_LARGE")
    manifest = _json_bytes({
        "schema_version": SCHEMA,
        "synthetic_only": True,
        "evidence_authenticated": False,
        "files_sha256": {"review.json": _sha(body), "review.html": _sha(page)},
    })
    # Any failure leaves a visible incomplete folder, never silently certified.
    # No customer files, sources, or existing outputs are removed/overwritten.
    try:
        destination.mkdir(mode=0o700)
    except FileExistsError as exc:
        raise ReviewError("OUTPUT_EXISTS") from exc
    _fresh_write(destination / ".SOVIA_INCOMPLETE", b"NOT_VERIFIED\n")
    _fresh_write(destination / "review.json", body)
    _fresh_write(destination / "review.html", page)
    _fresh_write(destination / "manifest.json", manifest)
    (destination / ".SOVIA_INCOMPLETE").unlink()
    return {"status": "SYNTHETIC_REVIEW_BUNDLE_CREATED_NOT_AUTHENTICATED",
            "review_status": result["status"], "files": list(FILES)}


def _parse_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ReviewError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReviewError("INVALID_JSON") from exc


def verify_bundle(output_dir):
    root = _safe_path(output_dir)
    if not root.is_dir() or set(p.name for p in root.iterdir()) != set(FILES):
        raise ReviewError("INCOMPLETE_OR_EXTRA_OUTPUT")
    data = {}
    for name in FILES:
        path = _safe_path(root / name, expect_file=True)
        with path.open("rb") as stream:
            raw = stream.read(MAX_FILE + 1)
        if len(raw) > MAX_FILE:
            raise ReviewError("OUTPUT_TOO_LARGE")
        data[name] = raw
    manifest = _parse_json(data["manifest.json"])
    if (type(manifest) is not dict or set(manifest) !=
            {"schema_version", "synthetic_only", "evidence_authenticated", "files_sha256"} or
            manifest["schema_version"] != SCHEMA or
            manifest["synthetic_only"] is not True or
            manifest["evidence_authenticated"] is not False or
            type(manifest["files_sha256"]) is not dict or
            set(manifest["files_sha256"]) != {"review.json", "review.html"}):
        raise ReviewError("MANIFEST_INVALID")
    for name in ("review.json", "review.html"):
        digest = manifest["files_sha256"][name]
        if type(digest) is not str or not hmac.compare_digest(digest, _sha(data[name])):
            raise ReviewError("INTEGRITY_MISMATCH")
    result = _require_review_structure(_parse_json(data["review.json"]))
    if render_html(result).encode("utf-8") != data["review.html"]:
        raise ReviewError("RENDER_MISMATCH")
    return {"status": "SYNTHETIC_BUNDLE_CONSISTENT_NOT_AUTHENTICATED",
            "review_status": result["status"], "files": list(FILES)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA synthetic LA offline review handoff")
    parser.add_argument("--plan")
    parser.add_argument("--policy")
    parser.add_argument("--observations")
    parser.add_argument("--output-dir")
    parser.add_argument("--verify-output-dir")
    parser.add_argument("--synthetic-only", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.verify_output_dir is not None:
            if any((args.plan, args.policy, args.observations, args.output_dir, args.synthetic_only)):
                raise ReviewError("INVALID_VERIFY_ARGUMENTS")
            answer = verify_bundle(args.verify_output_dir)
        else:
            if (not args.synthetic_only or
                    not all((args.plan, args.policy, args.observations, args.output_dir))):
                raise ReviewError("SYNTHETIC_ACK_AND_INPUTS_REQUIRED")
            answer = create_bundle(args.plan, args.policy, args.observations,
                                   args.output_dir)
    except (ReviewError, OSError, ValueError) as exc:
        code = str(exc) if isinstance(exc, ReviewError) else "REVIEW_IO_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}),
              file=sys.stderr)
        return 2
    print(json.dumps(answer, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
