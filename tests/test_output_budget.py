"""Regression for synthetic-only report output budget, without customer data."""
import contextlib
import io
import json
import unittest

import sovia_output_budget as budget


class OutputBudgetTests(unittest.TestCase):
    def test_small_case_within_four_mib(self):
        result = budget.synthetic_preflight(10, "normal", 4_194_304)
        self.assertEqual(result["status"], "SIMULATED_WITHIN_BUDGET")
        self.assertEqual(result["events"], 10)
        self.assertEqual(result["findings"], 0)
        self.assertEqual(result["exceeded_formats"], [])

    def test_dense_case_fails_one_mib(self):
        result = budget.synthetic_preflight(1000, "alert_dense", 1_048_576)
        self.assertEqual(result["status"], "SIMULATED_EXPORT_BLOCKED")
        self.assertGreater(result["json_bytes"], 1_048_576)
        self.assertIn("json", result["exceeded_formats"])
        self.assertEqual(result["findings"], 4998)

    def test_dense_case_allows_four_mib_simulation_only(self):
        result = budget.synthetic_preflight(1000, "alert_dense", 4_194_304)
        self.assertEqual(result["status"], "SIMULATED_WITHIN_BUDGET")
        self.assertFalse(result["production_export_enforced"])
        self.assertFalse(result["customer_quota_or_sla_approved"])

    def test_serialization_matches_actual_cli_indent(self):
        report = {"event_count": 1, "finding_count": 0, "events": [], "findings": []}
        class Fake:
            @staticmethod
            def render_html(_): return "<p>가</p>"
        measured = budget.assess_report(report, 1_048_576, Fake)
        self.assertEqual(measured["html_bytes"], len("<p>가</p>".encode()))
        self.assertEqual(measured["json_bytes"],
                         len(json.dumps(report, ensure_ascii=False, indent=2).encode()))

    def test_report_gate_exact_ceiling_inclusive(self):
        report = {"event_count": 1, "finding_count": 0}
        class Fake:
            @staticmethod
            def render_html(_): return "A" * 1_048_576
        measured = budget.assess_report(report, 1_048_576, Fake)
        self.assertEqual(measured["status"], "SIMULATED_WITHIN_BUDGET")
        self.assertEqual(measured["html_bytes"], 1_048_576)

    def test_one_byte_over_limit_blocks(self):
        report = {"event_count": 1, "finding_count": 0}
        class Fake:
            @staticmethod
            def render_html(_): return "A" * (1_048_576 + 1)
        measured = budget.assess_report(report, 1_048_576, Fake)
        self.assertEqual(measured["exceeded_formats"], ["html"])

    def test_invalid_counts_fail_closed(self):
        for c in (True, 0, 1, 999, 1001, -10, 10.0, "10", [], None):
            with self.subTest(c=c), self.assertRaises(budget.BudgetError):
                budget.synthetic_preflight(c, "normal", 1_048_576)

    def test_invalid_profiles_fail_closed(self):
        for p in (None, True, "mixed", "alert_dense,normal", {}, ""):
            with self.subTest(p=p), self.assertRaises(budget.BudgetError):
                budget.synthetic_preflight(10, p, 1_048_576)

    def test_invalid_budgets_fail_closed(self):
        for n in (None, True, -1, 0, 1, 1_048_575, 3_000_000, 50_000_000, "1048576", 1.0):
            with self.subTest(n=n), self.assertRaises(budget.BudgetError):
                budget.synthetic_preflight(10, "normal", n)

    def test_report_invalid_shapes_fail_closed(self):
        class Fake:
            @staticmethod
            def render_html(_): return "ok"
        for r in ({}, None, [], {"event_count": True, "finding_count": 0},
                  {"event_count": 1, "finding_count": "0"}):
            with self.subTest(r=r), self.assertRaises(budget.BudgetError):
                budget.assess_report(r, 1_048_576, Fake)

    def test_serialization_error_redacts_details(self):
        class Fake:
            @staticmethod
            def render_html(_): raise ValueError("secret raw report content")
        with self.assertRaisesRegex(budget.BudgetError, "^REPORT_SERIALIZATION_REJECTED$"):
            budget.assess_report({"event_count": 1, "finding_count": 0}, 1_048_576, Fake)

    def test_metadata_excludes_event_content(self):
        result = budget.synthetic_preflight(10, "alert_dense", 1_048_576)
        serialized = json.dumps(result)
        self.assertNotIn("source_pointer", serialized)
        self.assertNotIn("unapproved.example", serialized)
        self.assertNotIn("events\": [", serialized)
        self.assertFalse(result["real_source_or_customer_data_used"])

    def test_no_ack_blocks_without_running_pipeline(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            result = budget.main(["--events", "10"])
        self.assertEqual(result, 2)
        self.assertIn("SYNTHETIC_ONLY_ACK_REQUIRED", err.getvalue())

    def test_cli_block_exit_three_and_no_raw_event_json(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = budget.main(["--synthetic-only", "--events", "1000",
                                  "--profile", "alert_dense", "--budget-bytes", "1048576"])
        self.assertEqual(status, 3)
        self.assertEqual(json.loads(out.getvalue())["status"], "SIMULATED_EXPORT_BLOCKED")
        self.assertNotIn("sim-0001", out.getvalue())

    def test_cli_allow_exit_zero(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = budget.main(["--synthetic-only", "--events", "10",
                                  "--profile", "normal", "--budget-bytes", "4194304"])
        self.assertEqual(status, 0)
        self.assertFalse(json.loads(out.getvalue())["production_export_enforced"])

    def test_cli_invalid_returns_two_no_raw_input(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            status = budget.main(["--synthetic-only", "--events", "7"])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(err.getvalue())["error_code"],
                         "UNSUPPORTED_SYNTHETIC_COUNT")


if __name__ == "__main__":
    unittest.main()
