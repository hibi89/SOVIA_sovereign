"""SOVIA P2 offline read-only HTML dashboard for opt-in v1 SQLite history.

No JavaScript, local web server, external asset, network call or DB modification.
The static HTML snapshot displays only already-stored pseudonymous metadata.
"""
from __future__ import annotations

import argparse
from importlib.util import module_from_spec, spec_from_file_location
import html
from pathlib import Path
import sqlite3
import sys

MAX_ROWS = 100
MAX_GROUPS = 20
MAX_CELL_CHARS = 160
MAX_HTML_BYTES = 2_000_000
DASHBOARD_VERSION = "0.8.0"


class DashboardError(ValueError):
    """Cannot safely generate a dashboard from this SQLite history."""


def _local_module(filename, name):
    sibling = Path(__file__).resolve().with_name(filename)
    spec = spec_from_file_location(name, sibling)
    if spec is None or spec.loader is None:
        raise DashboardError("Required local source missing: " + filename)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_snapshot(db_path):
    """Read a bounded, consistent metadata view. Never create or update SQLite."""
    history = _local_module("sovia_history.py", "_sovia_dashboard_history")
    conn = history._connect(db_path, readonly=True)
    try:
        history._verify_schema(conn)
        conn.execute("BEGIN")  # Consistent multi-query read snapshot.
        totals = dict(zip(
            ("reports", "events", "findings", "report_events", "missing_pointers"),
            conn.execute("""SELECT
                (SELECT COUNT(*) FROM reports),
                (SELECT COUNT(*) FROM events),
                (SELECT COUNT(*) FROM findings),
                (SELECT COUNT(*) FROM report_events),
                (SELECT COUNT(*) FROM events WHERE source_pointer_present = 0)
            """).fetchone()
        ))
        severities = conn.execute(
            """SELECT severity, COUNT(*) AS n FROM findings
               GROUP BY severity ORDER BY n DESC, severity ASC LIMIT ?""",
            (MAX_GROUPS,),
        ).fetchall()
        rules = conn.execute(
            """SELECT rule_id, COUNT(*) AS n FROM findings
               GROUP BY rule_id ORDER BY n DESC, rule_id ASC LIMIT ?""",
            (MAX_GROUPS,),
        ).fetchall()
        reports = conn.execute(
            """SELECT report_id, imported_utc, engine_version, event_count, finding_count
               FROM reports ORDER BY imported_utc DESC, report_id DESC LIMIT ?""",
            (MAX_ROWS,),
        ).fetchall()
        findings = conn.execute(
            """SELECT f.severity, f.rule_id, f.evidence_status, f.report_id,
                      substr(f.identity_sha256, 1, 12)
               FROM findings AS f
               JOIN reports AS r ON r.report_id=f.report_id
               ORDER BY r.imported_utc DESC, f.report_id DESC, f.rule_id, f.finding_sha256
               LIMIT ?""",
            (MAX_ROWS,),
        ).fetchall()
        events = conn.execute(
            """SELECT occurred_at_utc, substr(identity_sha256, 1, 12),
                      substr(agent_sha256, 1, 12), substr(run_sha256, 1, 12),
                      source_pointer_present
               FROM events ORDER BY occurred_at_utc DESC, identity_sha256 DESC LIMIT ?""",
            (MAX_ROWS,),
        ).fetchall()
        return {"totals": totals, "severities": severities, "rules": rules,
                "reports": reports, "findings": findings, "events": events}
    finally:
        conn.rollback()
        conn.close()


def _esc(value):
    """Never render untrusted SQLite text as HTML markup."""
    if value is None:
        return "미제공"
    return html.escape(str(value)[:MAX_CELL_CHARS], quote=True)


def _table(title, columns, records, *, limit=None):
    head = "".join("<th scope='col'>" + _esc(key) + "</th>" for key in columns)
    if records:
        body = "".join("<tr>" + "".join("<td>" + _esc(value) + "</td>"
                                         for value in record) + "</tr>"
                       for record in records)
    else:
        body = "<tr><td colspan='" + str(len(columns)) + "'>기록 없음 (안전성 보증 아님)</td></tr>"
    note = ("<p class='table-note'>최신 " + str(limit) +
            "건까지만 표시합니다. 전체 수치는 상단 요약을 확인하세요.</p>") if limit is not None else ""
    return ("<section><h2>" + _esc(title) + "</h2><div class='table-scroll'>"
            "<table><thead><tr>" + head + "</tr></thead><tbody>" + body +
            "</tbody></table></div>" + note + "</section>")


def render_html(snapshot):
    """Produce standalone Korean HTML with CSP and no executable behavior."""
    totals = snapshot["totals"]
    metrics = (
        ("감사 보고서", totals["reports"]),
        ("서로 다른 이벤트", totals["events"]),
        ("위험 소견", totals["findings"]),
        ("증거 포인터 누락", totals["missing_pointers"]),
    )
    cards = "".join(
        "<div class='metric'><div class='metric-label'>" + _esc(name) +
        "</div><div class='metric-number'>" + _esc(value) + "</div></div>"
        for name, value in metrics
    )
    warning = ("본 문서는 저장된 메타데이터의 읽기 전용 스냅샷입니다. "
               "해시와 시각 정보는 재식별·연계가 가능할 수 있으며 익명화나 보안 인증을 뜻하지 않습니다. "
               "원본 로그·이벤트·증거 포인터는 독립 검증되지 않았고, 미관측 행위는 안전함을 뜻하지 않습니다. "
               "보이는 소견은 규칙 기반 사후 감사 결과이며 실시간 차단이나 무사고 보장이 아닙니다.")
    parts = [
        _table("위험 등급별 분포", ("심각도", "소견 수"), snapshot["severities"]),
        _table("규칙별 감지 건수", ("규칙", "소견 수"), snapshot["rules"]),
        _table("최근 감사 보고서", ("보고서 ID", "가져온 시각 (UTC)", "엔진",
                               "이벤트", "소견"), snapshot["reports"], limit=MAX_ROWS),
        _table("최근 위험 소견", ("심각도", "규칙", "증거 상태", "보고서 ID",
                              "이벤트 해시 앞 12자리"), snapshot["findings"], limit=MAX_ROWS),
        _table("최근 이벤트 타임라인", ("발생 시각 (UTC)", "이벤트 해시 앞 12자리",
                                   "에이전트 해시 앞 12자리", "실행 해시 앞 12자리",
                                   "증거 포인터 제공"), [
                (date, eid, actor, run, "제공(미검증)" if present == 1 else "미제공")
                for date, eid, actor, run, present in snapshot["events"]
            ], limit=MAX_ROWS),
    ]
    output = (
        "<!doctype html><html lang='ko'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<meta http-equiv='Content-Security-Policy' content=\"default-src 'none';"
        " img-src 'none'; style-src 'unsafe-inline'; script-src 'none';"
        " connect-src 'none'; object-src 'none'; form-action 'none'; base-uri 'none'\">"
        "<title>SOVIA — 오프라인 감사 이력</title><style>"
        ":root{color-scheme:light;font-family:system-ui,'Malgun Gothic',sans-serif;"
        "color:#142b42;background:#f3f6fa}"
        "body{margin:0 auto;max-width:1180px;padding:32px 24px}"
        "h1{font-size:2rem;margin:0 0 8px}h2{font-size:1.17rem;margin:0 0 16px}"
        ".eyebrow{color:#476a92;font-weight:700;letter-spacing:.08em;font-size:.78rem}"
        ".sub{color:#486075;margin:0 0 24px}.metrics{display:grid;"
        "grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}"
        ".metric,section,.notice{background:white;border:1px solid #dae2eb;"
        "border-radius:12px;padding:20px;margin:0 0 18px}"
        ".metric-label{font-size:.85rem;color:#576a80}.metric-number{font-size:2rem;"
        "font-weight:750;font-variant-numeric:tabular-nums;margin-top:8px}"
        ".notice{margin-top:18px;background:#f9fbfd;color:#40556e;line-height:1.65}"
        ".table-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;"
        "font-size:.88rem}th,td{border-bottom:1px solid #e4eaf0;padding:10px;"
        "text-align:left;vertical-align:top;overflow-wrap:anywhere}"
        "th{background:#eff3f8;color:#435a73}tbody tr:nth-child(even){background:#fbfcfe}"
        ".table-note,footer{font-size:.81rem;color:#63768a}"
        "footer{padding-bottom:36px}@media print{body{padding:10px}"
        "section,.metric,.notice{break-inside:avoid}}"
        "</style></head><body><main>"
        "<p class='eyebrow'>SOVIA SOVEREIGN · OFFLINE AUDIT</p>"
        "<h1>에이전트 감사 이력</h1>"
        "<p class='sub'>로컬 SQLite 스냅샷 · 저장된 메타데이터만 표시 · v" +
        _esc(DASHBOARD_VERSION) + "</p><div class='metrics'>" +
        cards + "</div><aside class='notice' role='note'>" + _esc(warning) +
        "</aside>" + "".join(parts) + "</main>"
        "<footer>정적 HTML / 서버·스크립트·외부 요청 없음. "
        "이 보고서를 공유하면 일부 메타데이터도 함께 공유됩니다.</footer></body></html>"
    )
    if len(output.encode("utf-8")) > MAX_HTML_BYTES:
        raise DashboardError("HTML dashboard exceeds bounded output size")
    return output


def export_dashboard(db_path, output_path):
    source = Path(db_path).resolve()
    destination = Path(output_path).absolute()
    if source == destination.resolve():
        raise DashboardError("Output must differ from source SQLite database")
    if not destination.parent.is_dir():
        raise DashboardError("Output directory must already exist")
    if destination.is_symlink() or destination.exists():
        raise DashboardError("Output already exists; no overwrite allowed")
    data = read_snapshot(db_path)
    report = render_html(data)
    audit = _local_module("sovia_audit.py", "_sovia_dashboard_publisher")
    audit.write_reports_atomically([(destination, report)])
    return {"status": "dashboard_created", "reports": data["totals"]["reports"],
            "events": data["totals"]["events"], "findings": data["totals"]["findings"]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="SOVIA offline read-only SQLite dashboard")
    parser.add_argument("--db", required=True, help="Existing SOVIA SQLite v1 history database")
    parser.add_argument("--output", required=True, help="NEW standalone HTML output path")
    args = parser.parse_args(argv)
    try:
        result = export_dashboard(args.db, args.output)
        import json
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except (DashboardError, ValueError, OSError, sqlite3.Error) as exc:
        print("SOVIA dashboard error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
