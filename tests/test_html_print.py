"""Print readability regression: formatting never changes evidence or detection."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from sovia_audit import evaluate, render_html


class Cells(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.rows = 0

    def handle_starttag(self, tag, attrs):
        if tag == "td":
            self.labels.append(dict(attrs).get("data-label"))
        if tag == "tr":
            self.rows += 1


class HtmlPrintTests(unittest.TestCase):
    def setUp(self):
        self.source = json.loads(
            (ROOT / "examples" / "demo_five_rules.json").read_text(encoding="utf-8")
        )
        self.report = evaluate(self.source)

    def test_five_rule_demo_data_not_changed(self):
        before = json.dumps(self.report, sort_keys=True, ensure_ascii=False)
        rendered = render_html(self.report)
        after = json.dumps(self.report, sort_keys=True, ensure_ascii=False)
        self.assertEqual(before, after)
        self.assertEqual((3, 5), (self.report["event_count"], self.report["finding_count"]))
        self.assertIn("위험 소견 5건", rendered)
        self.assertIn("evt-003", rendered)

    def test_all_print_labels_on_data_cells(self):
        rendered = render_html(self.report)
        parsed = Cells()
        parsed.feed(rendered)
        self.assertEqual(10, parsed.rows)  # 2 headers, 5 findings, 3 events
        self.assertEqual(57, len(parsed.labels))
        self.assertEqual(["등급", "규칙", "이벤트", "증거", "근거", "권고"], parsed.labels[:6])
        self.assertEqual(["일시", "이벤트", "에이전트", "실행", "도구",
                          "대상", "목적지", "결과", "증거 위치"], parsed.labels[-9:])

    def test_print_styles_isolated_and_screen_scroll_kept(self):
        rendered = render_html(self.report)
        self.assertIn("@media print{", rendered)
        self.assertIn("content:attr(data-label)", rendered)
        self.assertIn("break-inside:avoid", rendered)
        self.assertIn(".table-scroll{max-width:100%;overflow-x:auto}", rendered)
        self.assertEqual(2, rendered.count("class='table-scroll'"))

    def test_untrusted_values_remain_html_escaped(self):
        self.source["events"][-1]["agent_id"] = '<img src=x onerror=alert(1)>'
        self.source["events"][-1]["source_pointer"] = '<script>alert(1)</script>'
        rendered = render_html(evaluate(self.source))
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", rendered)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertNotIn("<img src=x", rendered)
        self.assertNotIn("<script>", rendered)

    def test_zero_findings_fallback_preserved(self):
        self.source["events"] = self.source["events"][:1]
        rendered = render_html(evaluate(self.source))
        self.assertIn("탐지된 규칙 위반 없음", rendered)
        self.assertIn("안전성 보증 아님", rendered)


if __name__ == "__main__":
    unittest.main()
