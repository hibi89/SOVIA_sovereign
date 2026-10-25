"""SOVIA Audit Lite: offline, read-only synthetic event auditor (stdlib only)."""
from __future__ import annotations

import argparse
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import sys

VERSION = "0.2.0"
MAX_BYTES = 1_048_576
MAX_EVENTS = 1000
MAX_DEPTH = 16
SCHEMA = "1.0"
ID_PATTERN = re.compile(r"^[A-Za-z0-9_.:-]{1,80}$")
DOMAIN_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9.-]{0,251}[a-z0-9])?$")
EVENT_KEYS = ("event_id", "occurred_at_utc", "agent_id", "run_id", "tool_name", "target", "destination_domain", "permission_asserted", "outcome", "source_pointer")


class AuditInputError(ValueError):
    """Untrusted input fails validation without partial success."""


def _depth(value, level=0):
    if level > MAX_DEPTH:
        raise AuditInputError("JSON nesting limit exceeded")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise AuditInputError("Object keys must be text")
            _depth(item, level + 1)
    elif isinstance(value, list):
        for item in value:
            _depth(item, level + 1)


def _text(value, field, limit=120, *, required=False):
    if value is None and not required:
        return None
    if not isinstance(value, str) or (required and not value.strip()) or len(value) > limit:
        raise AuditInputError(f"Invalid {field}: expected text (max {limit})")
    if any(ord(c) < 32 or ord(c) == 127 for c in value):
        raise AuditInputError(f"Invalid control character in {field}")
    return value


def _timestamp(value):
    raw = _text(value, "occurred_at_utc", 40, required=True)
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AuditInputError("Invalid occurred_at_utc timestamp") from exc
    if dt.tzinfo is None:
        raise AuditInputError("Timestamp timezone required")
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _string_set(obj, key):
    value = obj.get(key)
    if value is None:
        return None  # Absence means UNVERIFIED, never safe.
    if not isinstance(value, list) or len(value) > MAX_EVENTS:
        raise AuditInputError(f"Invalid policy.{key}: expected bounded list")
    entries = []
    for item in value:
        entries.append(_text(item, f"policy.{key}", 120, required=True).lower())
    return set(entries)


def _no_duplicate_keys(pairs):
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise AuditInputError(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


def read_document(path):
    file = Path(path)
    if not file.is_file():
        raise AuditInputError("Input file not found")
    if file.stat().st_size > MAX_BYTES:
        raise AuditInputError("Input file too large (max 1 MiB)")
    raw = file.read_bytes()
    if len(raw) > MAX_BYTES:
        raise AuditInputError("Input file too large (max 1 MiB)")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=_no_duplicate_keys)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise AuditInputError("Invalid UTF-8 JSON") from exc
    _depth(data)
    return data


def evaluate(document):
    if not isinstance(document, dict) or document.get("schema_version") != SCHEMA:
        raise AuditInputError("Unsupported schema_version (expected 1.0)")
    policy = document.get("policy")
    events = document.get("events")
    if not isinstance(policy, dict) or not isinstance(events, list) or len(events) > MAX_EVENTS:
        raise AuditInputError("Expected policy object and <= 1000 events")
    allowed = _string_set(policy, "allowed_tools")
    destinations = _string_set(policy, "approved_destinations")
    sensitive = _string_set(policy, "sensitive_targets")
    threshold = policy.get("max_tool_calls_per_minute")
    if threshold is not None and (type(threshold) is not int or not 1 <= threshold <= MAX_EVENTS):
        raise AuditInputError("policy.max_tool_calls_per_minute must be integer 1..1000")
    normalized = []
    findings = []
    seen = set()

    def add(event, rule_id, severity, reason, remedy):
        ident = event["event_id"]
        findings.append({"finding_id": f"{rule_id}:{ident}", "rule_id": rule_id,
                         "rule_version": "1.0", "severity": severity,
                         "event_ids": [ident], "source_pointer": event["source_pointer"],
                         "evidence_status": "POINTER_PROVIDED_UNVERIFIED" if event["source_pointer"] else "POINTER_MISSING",
                         "rationale": reason, "recommended_action": remedy})
    for index, item in enumerate(events):
        if not isinstance(item, dict):
            raise AuditInputError(f"events[{index}] must be an object")
        ident = _text(item.get("event_id"), "event_id", 80, required=True)
        if not ID_PATTERN.fullmatch(ident) or ident in seen:
            raise AuditInputError(f"Invalid or duplicate event_id: {ident}")
        seen.add(ident)
        event = {"event_id": ident, "occurred_at_utc": _timestamp(item.get("occurred_at_utc"))}
        for field in ("agent_id", "run_id", "tool_name"):
            event[field] = _text(item.get(field), field, 120, required=True)
        for field in ("target", "destination_domain", "outcome", "source_pointer"):
            event[field] = _text(item.get(field), field, 200)
        permission = item.get("permission_asserted")
        if permission is not None and type(permission) is not bool:
            raise AuditInputError("permission_asserted must be true, false or null")
        event["permission_asserted"] = permission
        domain = event["destination_domain"]
        if domain is not None:
            domain = domain.lower()
            if not DOMAIN_PATTERN.fullmatch(domain) or ".." in domain:
                raise AuditInputError("destination_domain must be a hostname, not URL")
            event["destination_domain"] = domain
        normalized.append(event)
        if allowed is not None and event["tool_name"].lower() not in allowed:
            add(event, "UNAUTHORIZED_TOOL", "HIGH", "허용 도구 목록에 없는 호출", "허용 도구 정책과 해당 호출을 확인하세요.")
        if destinations is not None and domain is not None and domain not in destinations:
            add(event, "UNAPPROVED_DESTINATION", "HIGH", "승인 목록 밖의 목적지", "외부 목적지 승인 여부와 전송 기록을 확인하세요.")
        if sensitive is not None and event["target"] is not None and event["target"].lower() in sensitive and permission is not True:
            add(event, "SENSITIVE_ACCESS", "HIGH", "민감 대상 접근에 명시적 허용 근거 없음", "접근 권한과 실행 주체를 확인하세요.")
        if not event["source_pointer"]:
            add(event, "MISSING_EVIDENCE", "MEDIUM", "원본 증거 위치가 제공되지 않음", "원본 로그의 위치와 감사 가능한 증거를 확보하세요.")
    if threshold is not None:
        windows = defaultdict(deque)
        # Sort independently of input order; compare only within the same agent and run.
        for event in sorted(normalized, key=lambda e: (e["occurred_at_utc"], e["event_id"])):
            instant = datetime.fromisoformat(event["occurred_at_utc"].replace("Z", "+00:00"))
            window = windows[(event["agent_id"], event["run_id"])]
            while window and instant - window[0] >= timedelta(seconds=60):
                window.popleft()
            window.append(instant)
            if len(window) > threshold:
                add(event, "BURST_TOOLS", "MEDIUM", f"같은 실행에서 60초 이내 호출 {len(window)}건 (설정 한도 {threshold}건 초과)", "호출량 급증 원인과 승인된 자동화를 확인하세요.")
    unknown = []
    if allowed is None:
        unknown.append("허용 도구 정책이 없어 미승인 도구 여부를 판정하지 못함")
    if destinations is None:
        unknown.append("승인 목적지 정책이 없어 목적지 적정성을 판정하지 못함")
    if sensitive is None:
        unknown.append("민감 대상 정책이 없어 민감정보 접근 여부를 판정하지 못함")
    if threshold is None:
        unknown.append("호출량 임계치 정책이 없어 60초 호출 집중도는 판정하지 못함")
    if any(not e["source_pointer"] for e in normalized):
        unknown.append("일부 이벤트에 원본 증거 포인터가 없음")
    if any(e["destination_domain"] is None for e in normalized):
        unknown.append("일부 이벤트에 목적지 정보가 없음 (미관측은 안전을 뜻하지 않음)")
    unknown.append("입력 이벤트와 제공된 원본 포인터는 독립 검증되지 않았으며, 미관측 행동은 안전을 뜻하지 않음")
    digest = hashlib.sha256(json.dumps({"events": normalized, "policy": policy}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    return {"report_schema_version": SCHEMA, "engine_version": VERSION, "report_id": digest[:16], "event_count": len(normalized), "finding_count": len(findings), "events": normalized, "findings": findings, "coverage_limits": unknown, "input_sha256": digest}


def render_html(report):
    esc = lambda v: html.escape(str(v if v is not None else "미제공"), quote=True)
    rows = "".join(f"<tr><td>{esc(f['severity'])}</td><td>{esc(f['rule_id'])}</td><td>{esc(f['event_ids'][0])}</td><td>{esc(f['source_pointer'])}</td><td>{esc(f['rationale'])}</td><td>{esc(f['recommended_action'])}</td></tr>" for f in report["findings"])
    if not rows:
        rows = "<tr><td colspan='6'>탐지된 규칙 위반 없음 (안전성 보증 아님)</td></tr>"
    timeline = "".join("<tr>" + "".join(f"<td>{esc(event.get(k))}</td>" for k in
               ("occurred_at_utc", "event_id", "agent_id", "run_id", "tool_name", "target", "destination_domain", "outcome", "source_pointer")) + "</tr>"
               for event in sorted(report["events"], key=lambda e: (e["occurred_at_utc"], e["event_id"])))
    if not timeline:
        timeline = "<tr><td colspan='9'>입력된 이벤트 없음</td></tr>"
    limits = "".join(f"<li>{esc(x)}</li>" for x in report["coverage_limits"])
    return ("<!doctype html><html lang='ko'><head><meta charset='utf-8'><title>SOVIA 감사 결과</title>"
            "<style>body{font-family:system-ui,sans-serif;margin:2rem;max-width:1200px;color:#152335}table{border-collapse:collapse;width:100%}th,td{border:1px solid #cad1da;padding:9px;text-align:left;vertical-align:top}th{background:#e9eef5}li{margin:8px 0}</style></head><body>"
            f"<h1>SOVIA Audit Lite</h1><p>엔진 {esc(report['engine_version'])} · 보고서 {esc(report['report_id'])}</p>"
            f"<p>검토 이벤트 {report['event_count']}건 · 위험 소견 {report['finding_count']}건</p>"
            "<h2>탐지 결과</h2><table><thead><tr><th>등급</th><th>규칙</th><th>이벤트</th><th>증거</th><th>근거</th><th>권고</th></tr></thead><tbody>"
            + rows + "</tbody></table><h2>이벤트 타임라인 (UTC)</h2><table><thead><tr><th>일시</th><th>이벤트</th><th>에이전트</th><th>실행</th><th>도구</th><th>대상</th><th>목적지</th><th>결과</th><th>증거 위치</th></tr></thead><tbody>"
            + timeline + "</tbody></table><h2>관측 범위 및 미확인 사항</h2><ul>" + limits + "</ul>"
            "<p>합성 데이터용 사후 규칙 진단입니다. 침해 탐지·사고 부재·컴플라이언스를 보증하지 않습니다.</p></body></html>")


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA offline read-only audit")
    parser.add_argument("--input", required=True, help="Structured JSON events (max 1 MiB)")
    parser.add_argument("--output", required=True, help="Output report HTML path")
    parser.add_argument("--json-output", help="Optional machine-readable report path")
    args = parser.parse_args(argv)
    try:
        report = evaluate(read_document(args.input))
        source = Path(args.input).resolve()
        targets = [Path(args.output).resolve()] + ([Path(args.json_output).resolve()] if args.json_output else [])
        if source in targets or len(set(targets)) != len(targets):
            raise AuditInputError("Output paths must differ from input and each other")
        for target in targets:
            if not target.parent.is_dir():
                raise AuditInputError("Output directory does not exist")
        targets[0].write_text(render_html(report), encoding="utf-8")
        if args.json_output:
            targets[1].write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"SOVIA: events={report['event_count']} findings={report['finding_count']} report={targets[0]}")
        return 0
    except (AuditInputError, OSError) as exc:
        print(f"SOVIA input/output error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
