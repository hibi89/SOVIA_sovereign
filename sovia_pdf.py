"""Optional, locally-rendered Korean PDF. Never imports an agent connector or sends data out."""
from __future__ import annotations

from io import BytesIO
import os
from pathlib import Path
from xml.sax.saxutils import escape


def _locate_korean_font(explicit=None):
    """Return existing system TTF; never download, vendor, or publish a font file."""
    if explicit is not None:
        path = Path(explicit).expanduser()
        if not path.is_file():
            raise ValueError("PDF font file not found; supply an installed Korean .ttf")
        if path.suffix.lower() != ".ttf":
            raise ValueError("PDF font must be a .ttf; CJK .ttc font collections are not supported")
        return path
    windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
    candidates = [
        windir / "Fonts/malgun.ttf", windir / "Fonts/NanumGothic.ttf",
        Path.home() / "Library/Fonts/NanumGothic.ttf",
        Path("/Library/Fonts/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumGothic.ttf"),
        Path("/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf"),
        Path("/usr/share/fonts/truetype/unfonts-core/UnDotum.ttf"),
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ValueError("No Korean TrueType font found; install one or pass --pdf-font <path-to-font.ttf>")


def render_pdf(report, font_path=None):
    """Return complete PDF bytes: bounded, escaped, Korean text and repeated table headers.

    Requires the free optional 'reportlab' package and a locally installed CJK TTF.
    A source pointer is never represented as verified source evidence.
    """
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen.canvas import Canvas
        from reportlab.platypus import KeepTogether, LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle
    except ImportError as exc:
        raise ImportError("Install optional dependency with: python -m pip install 'reportlab>=4,<5'") from exc

    font = _locate_korean_font(font_path)
    # Font file is read from local OS, embedded only into generated PDF, never shared separately.
    try:
        pdfmetrics.registerFont(TTFont("SOVIA_Korean", str(font)))
    except Exception as exc:
        raise ValueError("Selected TTF font cannot be registered for Korean PDF") from exc

    esc = lambda value: escape(str("미제공" if value is None else value))
    title = ParagraphStyle("soviaTitle", fontName="SOVIA_Korean", fontSize=19, leading=25,
                           textColor=colors.HexColor("#172b46"), spaceAfter=8)
    section = ParagraphStyle("soviaSection", fontName="SOVIA_Korean", fontSize=12, leading=17,
                             textColor=colors.HexColor("#172b46"), spaceBefore=12, spaceAfter=5)
    body = ParagraphStyle("soviaBody", fontName="SOVIA_Korean", fontSize=8.3, leading=13,
                          textColor=colors.HexColor("#24364a"), splitLongWords=1)
    small = ParagraphStyle("soviaSmall", parent=body, fontSize=7, leading=10)
    smallhead = ParagraphStyle("soviaHead", parent=small, textColor=colors.white)
    remark = ParagraphStyle("soviaRemark", parent=body, textColor=colors.HexColor("#6a3a14"), spaceAfter=4)

    buf = BytesIO()
    page_size = landscape(A4)
    page_width, _ = page_size
    doc = SimpleDocTemplate(buf, pagesize=page_size, leftMargin=30, rightMargin=30,
                            topMargin=28, bottomMargin=34, title="SOVIA Audit Lite 위험 진단 보고서",
                            author="SOVIA Audit Lite")
    width = page_width - 60

    def make_table(header, rows, widths):
        def cells(values, style):
            return [Paragraph(esc(value), style) for value in values]
        matrix = [cells(header, smallhead)] + [cells(row, small) for row in rows]
        tbl = LongTable(matrix, colWidths=widths, repeatRows=1, hAlign="LEFT", splitByRow=1)
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,0),colors.HexColor("#233c5c")),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f2f5fa")]),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#d4dce6")),
            ("LEFTPADDING",(0,0),(-1,-1),6), ("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),5), ("BOTTOMPADDING",(0,0),(-1,-1),5),
            ("VALIGN",(0,0),(-1,-1),"TOP"),
        ]))
        return tbl

    story = [Paragraph("SOVIA Audit Lite | AI 에이전트 사후 감사", title),
             Paragraph(f"보고서 {esc(report['report_id'])} · 엔진 {esc(report['engine_version'])} · 이벤트 {report['event_count']}건 · 위험 소견 {report['finding_count']}건", body),
             Spacer(1,6),
             Paragraph("합성·제공 이벤트에 대한 규칙 기반 분석입니다. 원본의 진위, 미관측 행동의 안전성, 준법성은 검증하지 않습니다.", remark),
             Paragraph("위험 탐지 결과",section)]
    finding_rows=[]
    for f in report["findings"]:
        finding_rows.append((f["severity"],f["rule_id"], ", ".join(f["event_ids"]),
                             f["source_pointer"] or "미제공", f["evidence_status"],
                             f["rationale"],f["recommended_action"]))
    if not finding_rows:
        finding_rows=[("—", "규칙 위반 미검출", "—", "—", "미검증", "관측된 위반이 없다는 뜻이며 안전함을 보증하지 않습니다.", "입력 범위와 정책을 확인하세요.")]
    fw=[46,120,75,92,94,171,width-598]
    story.append(make_table(["등급","규칙","이벤트","원본 위치","증거 상태","판정 근거","권고"],finding_rows,fw))
    story.append(Paragraph("시간순 이벤트 타임라인 (UTC)",section))
    event_rows=[]
    for e in sorted(report["events"],key=lambda x:(x["occurred_at_utc"],x["event_id"])):
        event_rows.append((e["occurred_at_utc"],e["event_id"],e["agent_id"],e["run_id"],e["tool_name"],
                           e["target"],e["destination_domain"],e["source_pointer"]))
    if not event_rows:
        event_rows=[("이벤트 없음", "—","—","—","—","—","—","—")]
    ew=[100,73,79,72,93,87,98,width-602]
    story.append(make_table(["UTC 일시","이벤트","에이전트","실행","도구","대상","목적지","증거 위치"],event_rows,ew))
    story.append(Paragraph("관측 범위 및 미확인 사항",section))
    for limitation in report["coverage_limits"]:
        story.append(Paragraph("• "+esc(limitation),body))
    story.append(Spacer(1,10))
    story.append(Paragraph("본 보고서는 탐지 보증, 규제 인증, 24시간 감시 서비스 또는 법적 판단이 아닙니다.", remark))

    def page_number(canv, doc_):
        canv.saveState()
        canv.setFont("SOVIA_Korean", 7)
        canv.setFillColor(colors.HexColor("#627184"))
        canv.drawString(30,17,"SOVIA · 제공 로그 기반 참고 진단 · 원본 증거 독립 검증 안 됨")
        canv.drawRightString(page_width-30,17,f"{doc_.page} 페이지")
        canv.restoreState()

    def canvas_factory(*args, **kwargs):
        kwargs["invariant"] = 1
        return Canvas(*args, **kwargs)

    try:
        doc.build(story, onFirstPage=page_number, onLaterPages=page_number,
                  canvasmaker=canvas_factory)
    except Exception as exc:
        raise ValueError("PDF layout failed for the supplied normalized report") from exc
    data=buf.getvalue()
    if not data.startswith(b"%PDF-"):
        raise ValueError("ReportLab did not produce a valid PDF header")
    return data
