"""SOVIA Audit Lite NEXT HTML report preview (source-only, opt-in).

Independent renderer. Does NOT modify the immutable v0.10/v0.11.2 portable
payload or claim an approved v0.12 customer release. Uses existing evaluator,
bound input reader, and exclusive publication writer without network or JS.
"""
from __future__ import annotations

import argparse
from html import escape
from importlib.util import module_from_spec, spec_from_file_location
import json
import os
from pathlib import Path
import sys

PREVIEW_VERSION = "0.12.0-preview"
FINDING_COLUMNS = (
    ("등급", "severity"), ("규칙", "rule_id"), ("이벤트", "event_ids"),
    ("증거", "source_pointer"), ("근거", "rationale"), ("권고", "recommended_action"),
)
EVENT_COLUMNS = (
    ("일시 (UTC)", "occurred_at_utc"), ("이벤트", "event_id"),
    ("에이전트", "agent_id"), ("실행", "run_id"), ("도구", "tool_name"),
    ("대상", "target"), ("목적지", "destination_domain"),
    ("결과", "outcome"), ("증거 위치", "source_pointer"),
)
MAX_HTML_BYTES = 2_000_000


class PreviewError(ValueError):
    """Stable non-disclosing preview-only refusal codes."""


def _audit():
    src = Path(__file__).resolve().with_name("sovia_audit.py")
    spec = spec_from_file_location("_sovia_next_print_audit", src)
    if spec is None or spec.loader is None:
        raise PreviewError("AUDITOR_UNAVAILABLE")
    result = module_from_spec(spec)
    try:
        spec.loader.exec_module(result)
    except (OSError, ImportError) as exc:
        raise PreviewError("AUDITOR_UNAVAILABLE") from exc
    return result


def _value(raw):
    if raw is None:
        return "미제공"
    if isinstance(raw, list):
        return ", ".join(map(str, raw))
    return str(raw)


def _cell(label, value):
    # Column names are fixed code constants; event metadata is escaped for HTML
    # text content, never inserted as CSS attributes or script.
    return '<td data-label="' + label + '">' + escape(_value(value), quote=True) + '</td>'


def _table(columns, records, *, empty_label):
    header = "<tr>" + "".join("<th scope='col'>" + label + "</th>" for label, _ in columns) + "</tr>"
    rows = "".join(
        "<tr>" + "".join(_cell(label, record.get(key))
                         for label, key in columns) + "</tr>"
        for record in records
    )
    if not rows:
        rows = "<tr><td colspan='" + str(len(columns)) + "'>" + empty_label + "</td></tr>"
    return (
        "<div class='table-scroll'><table><thead>" + header +
        "</thead><tbody>" + rows + "</tbody></table></div>"
    )


def render(report):
    """Create offline screen tables + print-only labeled rows from evaluated report.

    The caller supplies the original evaluator's validated report, never raw
    n8n exports. No change to findings, event ordering, or source citations.
    """
    findings = []
    for finding in report["findings"]:
        copy = dict(finding)
        copy["event_ids"] = ", ".join(str(k) for k in finding["event_ids"])
        findings.append(copy)
    events = sorted(report["events"],
                    key=lambda event: (event["occurred_at_utc"], event["event_id"]))
    limits = "".join("<li>" + escape(_value(x), quote=True) + "</li>"
                     for x in report["coverage_limits"])
    style = (
        ":root{color-scheme:light;font-family:system-ui,'Malgun Gothic',sans-serif;"
        "background:#f4f6f9;color:#17293f}"
        "body{max-width:1200px;padding:32px 22px;margin:0 auto}"
        "header,section,aside{background:#fff;border:1px solid #dce3ee;"
        "border-radius:12px;padding:20px;margin-bottom:18px}"
        "h1{font-size:1.8rem;margin:0 0 12px}h2{font-size:1.15rem}"
        ".meta{color:#425a76}.stats{display:flex;gap:18px;flex-wrap:wrap;"
        "font-weight:650;font-variant-numeric:tabular-nums}"
        ".table-scroll{width:100%;overflow-x:auto}"
        "table{border-collapse:collapse;width:100%;min-width:760px;font-size:.88rem}"
        "th,td{border:1px solid #dce3ee;padding:10px;text-align:left;"
        "vertical-align:top;overflow-wrap:anywhere}"
        "th{background:#eaf0f7;text-align:left}tbody tr:nth-child(even){background:#f9fbfd}"
        ".caution{line-height:1.6;font-size:.88rem;color:#394e67}"
        "@media print{"
        "@page{size:A4 portrait;margin:13mm}"
        ":root{background:#fff}body{margin:0;padding:0;font-size:9.5pt;"
        "max-width:none}header,section,aside{border:0;padding:0;margin:0 0 6px;"
        "border-radius:0}h1{font-size:16pt}h2{margin:4px 0 6px;break-after:avoid}"
        ".table-scroll{overflow:visible}"
        "table,tbody{display:block;width:100%;min-width:0}"
        "thead{display:none}"
        "tbody tr{display:block;border:1px solid #bac8d8;margin:0 0 5px;"
        "break-inside:avoid;page-break-inside:avoid;background:#fff}"
        "tbody td{display:block;border:0;border-bottom:1px solid #e5eaf0;"
        "padding:2px 7px;overflow-wrap:anywhere}"
        "tbody td:last-child{border-bottom:0}"
        "tbody td[data-label]::before{content:attr(data-label) ' · ';"
        "font-weight:700;color:#173a5b}"
        "aside.caution{font-size:9pt;line-height:1.28;break-inside:avoid}"
        "aside.caution ul{margin:5px 0;padding-left:20px}"
        "aside.caution li{margin:1px 0}"
        "aside.caution p{margin:5px 0}"
        "}"
    )
    html_doc = (
        "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;;'
        ' img-src &#39;none&#39;; style-src &#39;unsafe-inline&#39;; script-src &#39;none&#39;;'
        ' connect-src &#39;none&#39;; object-src &#39;none&#39;; form-action &#39;none&#39;">'
        "<title>SOVIA 감사 보고서 — 출력 미리보기</title><style>" + style +
        "</style></head><body>"
        "<header><h1>SOVIA Audit Lite — 차기 출력 미리보기</h1>"
        "<p class='meta'>출력 버전 " + PREVIEW_VERSION + " · 감사 엔진 " +
        escape(_value(report["engine_version"]), quote=True) +
        " · 보고서 " + escape(_value(report["report_id"]), quote=True) +
        "</p><div class='stats'><span>검토 이벤트 " + str(report["event_count"]) +
        "건</span><span>위험 소견 " + str(report["finding_count"]) +
        "건</span></div></header><main>"
        "<section><h2>탐지 결과</h2>" +
        _table(FINDING_COLUMNS, findings,
               empty_label="탐지된 규칙 위반 없음 (안전성 보증 아님)") +
        "</section><section><h2>이벤트 타임라인 (UTC)</h2>" +
        _table(EVENT_COLUMNS, events, empty_label="입력된 이벤트 없음") +
        "</section><aside class='caution'><h2>관측 범위 및 미확인 사항</h2><ul>" +
        limits + "</ul><p>합성 데이터용 사후 규칙 진단입니다. "
        "미관측 행위의 안전성·침해 부재·컴플라이언스를 보증하지 않습니다. "
        "이 출력은 서명되지 않은 별도 미리보기이며 기존 포터블 상품에 포함되지 않습니다."
        "</p></aside></main></body></html>"
    )
    if len(html_doc.encode("utf-8")) > MAX_HTML_BYTES:
        raise PreviewError("PREVIEW_OUTPUT_LIMIT")
    return html_doc


def preview_files(input_path, output_path):
    """Read sanitized canonical input and exclusively publish one new HTML file."""
    source = Path(input_path).resolve()
    destination = Path(os.path.abspath(output_path))
    if destination.resolve() == source:
        raise PreviewError("PREVIEW_OUTPUT_ALIASES_INPUT")
    if not destination.parent.is_dir():
        raise PreviewError("PREVIEW_OUTPUT_PARENT_MISSING")
    if destination.is_symlink() or destination.exists():
        raise PreviewError("PREVIEW_OUTPUT_EXISTS")
    audit = _audit()
    try:
        report = audit.evaluate(audit.read_document(source))
        payload = render(report)
        audit.write_reports_atomically([(destination, payload)])
    except (ValueError, TypeError, OSError, OverflowError, RecursionError) as exc:
        if isinstance(exc, PreviewError):
            raise
        raise PreviewError("PREVIEW_INPUT_OR_OUTPUT_REJECTED") from exc
    return report["event_count"], report["finding_count"]


def main(argv=None):
    p = argparse.ArgumentParser(description="Opt-in SOVIA printable HTML next-version preview")
    p.add_argument("--input", required=True, help="Explicit local canonical sanitized JSON")
    p.add_argument("--output", required=True, help="A NEW HTML path outside input/install")
    p.add_argument("--synthetic-only", action="store_true",
                   help="Required; does NOT independently authenticate synthetic origin")
    args = p.parse_args(argv)
    if not args.synthetic_only:
        print(json.dumps({"status": "REJECTED",
                          "error_code": "PREVIEW_SYNTHETIC_ACK_REQUIRED"}), file=sys.stderr)
        return 2
    try:
        events, findings = preview_files(args.input, args.output)
    except PreviewError as exc:
        print(json.dumps({"status": "REJECTED", "error_code": str(exc)}),
              file=sys.stderr)
        return 2
    print(json.dumps({
        "status": "SYNTHETIC_NEXT_REPORT_PREVIEW_ONLY",
        "events": events, "findings": findings,
        "prior_portable_modified": False,
        "customer_origin_independently_verified": False,
        "owner_visual_or_print_verified": False,
        "commercial_release_authorized": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
