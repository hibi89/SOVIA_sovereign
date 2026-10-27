"""SOVIA source-only local artifact static preflight for owner synthetic self-check.

Reads existing files; never writes, launches a browser/PDF viewer, changes Windows
security settings or establishes real owner approval. No customer files allowed.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import re
import sys

MAX_HTML = 1_048_576
MAX_PDF = 10 * 1_048_576
ALLOWED_TAGS = frozenset({
    "html", "head", "meta", "title", "style", "body", "h1", "h2",
    "p", "table", "thead", "tbody", "tr", "th", "td", "ul", "li",
    "div", "main", "section", "aside", "footer",
})
ALLOWED_ATTRS = frozenset({
    "lang", "charset", "name", "content", "http-equiv", "class",
    "role", "scope", "colspan",
})
FORBIDDEN_CSS = re.compile(r"(?i)@import\b|url\s*\(|expression\s*\(")


class StaticPreflightError(ValueError):
    """Fixed codes only; do not return paths, source content or Windows identifiers."""


def _local(name, module):
    path = Path(__file__).resolve().with_name(name)
    spec = spec_from_file_location(module, path)
    if spec is None or spec.loader is None:
        raise StaticPreflightError("LOCAL_DEPENDENCY_UNAVAILABLE")
    loaded = module_from_spec(spec)
    try:
        spec.loader.exec_module(loaded)
    except (OSError, ImportError) as exc:
        raise StaticPreflightError("LOCAL_DEPENDENCY_UNAVAILABLE") from exc
    return loaded


def _read(root, name, *, limit=MAX_HTML):
    file = root / name
    if file.is_symlink() or not file.is_file():
        raise StaticPreflightError("ARTIFACT_MISSING_OR_SYMLINK")
    try:
        with file.open("rb") as handle:
            data = handle.read(limit + 1)
    except OSError as exc:
        raise StaticPreflightError("ARTIFACT_UNREADABLE") from exc
    if len(data) > limit:
        raise StaticPreflightError("ARTIFACT_SIZE_LIMIT")
    return data


class _SafeStaticHTML(HTMLParser):
    """Document-shape inspection, NOT proof of browser rendering or XSS safety."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = {}
        self.text = []
        self.csp = []
        self.metric_numbers = []
        self._in_metric = False
        self._in_style = False
        self.style_text = []

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS or any(
            key not in ALLOWED_ATTRS or key.startswith("on") for key, _ in attrs
        ):
            raise StaticPreflightError("ACTIVE_OR_UNEXPECTED_HTML")
        # Disallow unexpected external/resource-bearing attributes even if they
        # are misencoded or decorated with mixed case by the HTML parser.
        if len(set(k for k, _ in attrs)) != len(attrs):
            raise StaticPreflightError("DUPLICATE_HTML_ATTRIBUTE")
        if tag == "meta":
            attr = dict(attrs)
            if attr.get("http-equiv") is not None and attr["http-equiv"] != "Content-Security-Policy":
                raise StaticPreflightError("ACTIVE_OR_UNEXPECTED_HTML")
            if attr.get("name") is not None and attr["name"] != "viewport":
                raise StaticPreflightError("ACTIVE_OR_UNEXPECTED_HTML")
            if attr.get("charset") is not None and attr["charset"].lower() != "utf-8":
                raise StaticPreflightError("ACTIVE_OR_UNEXPECTED_HTML")
        self.tags[tag] = self.tags.get(tag, 0) + 1
        if tag == "style":
            self._in_style = True
        if tag == "div" and ("class", "metric-number") in attrs:
            self._in_metric = True
        if tag == "meta" and ("http-equiv", "Content-Security-Policy") in attrs:
            self.csp.extend(value for key, value in attrs if key == "content")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag not in ALLOWED_TAGS:
            raise StaticPreflightError("ACTIVE_OR_UNEXPECTED_HTML")
        if tag == "style":
            self._in_style = False
        if tag == "div" and self._in_metric:
            self._in_metric = False

    def handle_data(self, data):
        self.text.append(data)
        if self._in_metric:
            self.metric_numbers.append(data)
        if self._in_style:
            self.style_text.append(data)


def _scan_html(data):
    try:
        page = data.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise StaticPreflightError("INVALID_UTF8_HTML") from exc
    if not page.lower().startswith("<!doctype html>"):
        raise StaticPreflightError("INVALID_HTML_DOCUMENT")
    parser = _SafeStaticHTML()
    try:
        parser.feed(page)
        parser.close()
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        if isinstance(exc, StaticPreflightError):
            raise
        raise StaticPreflightError("HTML_PARSE_REJECTED") from exc
    if FORBIDDEN_CSS.search("".join(parser.style_text)):
        raise StaticPreflightError("ACTIVE_EXTERNAL_CSS_REJECTED")
    if parser.tags.get("html") != 1 or parser.tags.get("head") != 1 or parser.tags.get("body") != 1:
        raise StaticPreflightError("INVALID_HTML_DOCUMENT")
    return parser, "".join(parser.text)


def inspect(root_path):
    """Inspect existing owner_selfcheck artifacts without changing a byte."""
    root = Path(root_path)
    if root.is_symlink() or not root.is_dir():
        raise StaticPreflightError("INVALID_RESULT_DIRECTORY")
    owner = _local("sovia_owner_evidence.py", "_sovia_static_owner")
    audit = _local("sovia_audit.py", "_sovia_static_audit")
    for name in ("SELF_CHECK_RESULT.json", "synthetic-audit.json"):
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise StaticPreflightError("ARTIFACT_MISSING_OR_SYMLINK")
    try:
        selfcheck = audit.read_document(root / "SELF_CHECK_RESULT.json")
        pdf_state = owner._validate_selfcheck(selfcheck)
        report = audit.read_document(root / "synthetic-audit.json")
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise StaticPreflightError("SELF_CHECK_OR_REPORT_REJECTED") from exc
    if (type(report) is not dict or
            report.get("report_schema_version") != "1.0" or
            report.get("event_count") != 3 or report.get("finding_count") != 5 or
            type(report.get("events")) is not list or len(report["events"]) != 3 or
            type(report.get("findings")) is not list or len(report["findings"]) != 5 or
            {f.get("rule_id") for f in report["findings"] if type(f) is dict} != {
                "UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION", "SENSITIVE_ACCESS",
                "MISSING_EVIDENCE", "BURST_TOOLS",
            }):
        raise StaticPreflightError("SYNTHETIC_REPORT_COUNTS_OR_RULES")
    rid = report.get("report_id")
    if type(rid) is not str or re.fullmatch(r"[a-f0-9]{16}", rid) is None:
        raise StaticPreflightError("SYNTHETIC_REPORT_ID_INVALID")

    audit_page, audit_text = _scan_html(_read(root, "synthetic-audit.html"))
    if (audit_page.tags.get("table") != 2 or rid not in audit_text or
            "검토 이벤트 3건 · 위험 소견 5건" not in audit_text or
            "관측 범위 및 미확인 사항" not in audit_text):
        raise StaticPreflightError("AUDIT_HTML_SEMANTIC_MISMATCH")

    dashboard, dashboard_text = _scan_html(_read(root, "synthetic-dashboard.html"))
    if (dashboard.tags.get("table") != 5 or
            "최근 이벤트 타임라인" not in dashboard_text or
            "SOVIA SOVEREIGN" not in dashboard_text or
            [val.strip() for val in dashboard.metric_numbers[:3]] != ["1", "3", "5"] or
            len(dashboard.metric_numbers) != 4 or
            len(dashboard.csp) != 1 or
            "script-src 'none'" not in dashboard.csp[0] or
            "connect-src 'none'" not in dashboard.csp[0] or
            "default-src 'none'" not in dashboard.csp[0]):
        raise StaticPreflightError("DASHBOARD_HTML_SEMANTIC_OR_CSP_MISMATCH")

    pdf_path = root / "synthetic-audit.pdf"
    if pdf_state == "GENERATED_NEEDS_VISUAL_REVIEW":
        pdf = _read(root, "synthetic-audit.pdf", limit=MAX_PDF)
        if not pdf.startswith(b"%PDF-") or b"%%EOF" not in pdf[-2048:]:
            raise StaticPreflightError("PDF_STATIC_MARKER_MISSING")
        pdf_check = "PDF_HEADER_TRAILER_PRESENT_VISUAL_PENDING"
    elif pdf_state == "FAILED_OPTIONAL_PDF":
        raise StaticPreflightError("OPTIONAL_PDF_AUTOCHECK_FAILED")
    else:
        if pdf_path.exists() or pdf_path.is_symlink():
            raise StaticPreflightError("UNEXPECTED_PDF_ARTIFACT")
        pdf_check = "PDF_NOT_GENERATED_NOT_TESTED"

    return {
        "status": "SYNTHETIC_ARTIFACT_STATIC_CHECKS_PASSED_MANUAL_PENDING",
        "synthetic_events": 3,
        "synthetic_findings": 5,
        "offline_static_html_checks": "PASS_HEURISTIC",
        "pdf_static_check": pdf_check,
        "browser_visual_verified": False,
        "korean_pdf_visual_verified": False,
        "windows_defender_smartscreen_verified": False,
        "actual_owner_device_verified": False,
        "source_or_owner_identity_authenticated": False,
        "commercial_approval": False,
        "customer_data_processed": False,
        "writes_performed": False,
        "network_called": False,
    }


def main(argv=None):
    p = argparse.ArgumentParser(description="Read-only static checks on existing synthetic owner diagnostics")
    p.add_argument("--results-dir", required=True, help="existing SOVIA_SELF_CHECK_* output dir")
    args = p.parse_args(argv)
    try:
        print(json.dumps(inspect(args.results_dir), sort_keys=True))
    except (StaticPreflightError, OSError, ValueError, TypeError, OverflowError) as exc:
        code = str(exc) if isinstance(exc, StaticPreflightError) else "STATIC_PREFLIGHT_REJECTED"
        print(json.dumps({"status": "REJECTED", "error_code": code}), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
