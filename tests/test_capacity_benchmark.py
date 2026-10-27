"""Deterministic synthetic capacity tests. Never set machine speed or memory SLAs."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import sovia_capacity_benchmark as bench
import sovia_audit as audit


class CapacityBenchTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_capacity_benchmark.py"),
             *args], text=True, capture_output=True, timeout=50)

    def test_deterministic_normal_sample(self):
        a = bench.make_synthetic(100, "normal")
        self.assertEqual(a, bench.make_synthetic(100, "normal"))
        self.assertEqual(100, len(a["events"]))
        self.assertEqual(["sim-0001", "sim-0002"], [e["event_id"] for e in a["events"][:2]])
        self.assertEqual("2026-10-26T00:00:00Z", a["events"][0]["occurred_at_utc"])

    def test_deterministic_dense_sample(self):
        a = bench.make_synthetic(100, "alert_dense")
        self.assertEqual(a, bench.make_synthetic(100, "alert_dense"))
        self.assertEqual(100, len(a["events"]))
        self.assertTrue(all(e["source_pointer"] is None for e in a["events"]))

    def test_normal_sample_has_no_rule_findings(self):
        for size in (10, 100):
            with self.subTest(size=size):
                report = audit.evaluate(bench.make_synthetic(size, "normal"))
                self.assertEqual(0, report["finding_count"])
                self.assertEqual(size, report["event_count"])

    def test_dense_sample_exercises_all_five_rules(self):
        report = audit.evaluate(bench.make_synthetic(10, "alert_dense"))
        self.assertEqual(48, report["finding_count"])
        self.assertEqual({
            "UNAUTHORIZED_TOOL", "UNAPPROVED_DESTINATION", "SENSITIVE_ACCESS",
            "MISSING_EVIDENCE", "BURST_TOOLS",
        }, {f["rule_id"] for f in report["findings"]})
        self.assertEqual(10, report["event_count"])

    def test_dense_burst_exact_bound_at_10(self):
        r = audit.evaluate(bench.make_synthetic(10, "alert_dense"))
        self.assertEqual(8, sum(f["rule_id"] == "BURST_TOOLS" for f in r["findings"]))
        self.assertEqual(40, sum(f["rule_id"] != "BURST_TOOLS" for f in r["findings"]))

    def test_capacity_1000_events_exact_five_rule_volume(self):
        report = audit.evaluate(bench.make_synthetic(1000, "alert_dense"))
        self.assertEqual(1000, report["event_count"])
        self.assertEqual(4998, report["finding_count"])

    def test_all_fixture_jsons_fit_source_input_hard_limits(self):
        for count in bench.COUNTS:
            for profile in bench.PROFILES:
                with self.subTest(count=count, profile=profile):
                    data = bench.make_synthetic(count, profile)
                    blob = bench._input_bytes(data, audit)
                    self.assertLessEqual(len(blob), audit.MAX_BYTES)
                    self.assertLessEqual(len(data["events"]), audit.MAX_EVENTS)
                    self.assertEqual(data, json.loads(blob.decode("utf-8")))

    def test_fixture_domain_and_pointer_are_fabricated(self):
        for profile in bench.PROFILES:
            document = bench.make_synthetic(100, profile)
            for event in document["events"]:
                self.assertTrue(event["destination_domain"].endswith(".example"))
                self.assertIn(event["source_pointer"], (None, "synthetic:" + event["event_id"][-4:]))
                self.assertTrue(event["agent_id"].startswith("synthetic-"))

    def test_generating_fixture_does_not_touch_disk(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual([], list(folder.iterdir()))
            bench.make_synthetic(1000, "normal")
            self.assertEqual([], list(folder.iterdir()))

    def test_reject_unsupported_count_and_bool_count(self):
        for count in (0, 1, 999, 1001, -1, 10.0, True, False, "100", None):
            with self.subTest(count=count), self.assertRaisesRegex(
                bench.CapacityError, "UNSUPPORTED_SYNTHETIC_COUNT"):
                bench.make_synthetic(count, "normal")

    def test_reject_unsupported_profile_and_case(self):
        for profile in ("live", "n8n", "customer", "", None, 1):
            with self.subTest(profile=profile), self.assertRaises(bench.CapacityError):
                bench.make_synthetic(10, profile)

    def test_reject_higher_than_input_contract_bytes(self):
        sample = bench.make_synthetic(10, "normal")
        class ArtificialLimit:
            MAX_EVENTS = 1000
            MAX_BYTES = 2
        with self.assertRaisesRegex(
            bench.CapacityError, "SYNTHETIC_CASE_EXCEEDS_AUDIT_INPUT_CONTRACT"
        ):
            bench._input_bytes(sample, ArtificialLimit())

    def test_reject_higher_than_event_contract(self):
        sample = bench.make_synthetic(10, "normal")
        class ArtificialLimit:
            MAX_EVENTS = 2
            MAX_BYTES = 1048576
        with self.assertRaisesRegex(
            bench.CapacityError, "SYNTHETIC_CASE_EXCEEDS_AUDIT_INPUT_CONTRACT"
        ):
            bench._input_bytes(sample, ArtificialLimit())

    def test_measurement_includes_file_read_audit_html_json(self):
        r = bench.run_case(10, "normal", 1)
        self.assertEqual(10, r["events"])
        self.assertEqual("normal", r["profile"])
        self.assertEqual(0, r["findings"])
        self.assertGreater(r["synthetic_input_bytes"], 0)
        self.assertGreater(r["html_bytes"], 0)
        self.assertGreater(r["json_report_bytes"], 0)
        self.assertGreaterEqual(r["median_pipeline_ms"], 0)
        self.assertGreater(r["max_python_tracemalloc_peak_kib"], 0)

    def test_dense_runtime_no_hard_sla(self):
        r = bench.run_case(10, "alert_dense", 1)
        self.assertEqual(48, r["findings"])
        self.assertGreater(r["json_report_bytes"], r["synthetic_input_bytes"])
        self.assertIn("median_pipeline_ms", r)
        self.assertNotIn("fast_enough", r)
        self.assertNotIn("customer_supported", r)

    def test_two_rounds_min_median_max_consistent(self):
        r = bench.run_case(10, "normal", 2)
        self.assertEqual(2, r["rounds"])
        self.assertLessEqual(r["min_pipeline_ms"], r["median_pipeline_ms"])
        self.assertLessEqual(r["median_pipeline_ms"], r["max_pipeline_ms"])

    def test_unsupported_rounds_never_executed(self):
        for rounds in (0, 4, -1, True, False, 1.0, "1", None):
            with self.subTest(rounds=rounds), self.assertRaises(bench.CapacityError):
                bench.run_case(10, "normal", rounds)

    def test_small_suite_has_truthful_non_sla_result(self):
        result = bench.run_suite((10,), ("normal", "alert_dense"), 1)
        self.assertEqual(bench.SCHEMA, result["schema"])
        self.assertEqual("SYNTHETIC_MEASUREMENTS_ONLY_NOT_CUSTOMER_SLA",
                         result["status"])
        self.assertEqual(2, len(result["results"]))
        self.assertEqual(1000, result["auditor_max_events"])
        self.assertEqual(1048576, result["auditor_max_input_bytes"])
        self.assertIn("read_evaluate", result["coverage"])
        self.assertFalse(result["sample_is_representative_of_customers"])
        self.assertFalse(result["performance_sla_or_commercial_quota_approved"])
        self.assertFalse(result["actual_customer_data_used"])
        self.assertFalse(result["independent_owner_machine_verified"])
        self.assertFalse(result["persisted_benchmark_input_or_report"])
        self.assertIn("NOT process RSS", result["memory"])
        self.assertIn("output_file_write", result["excludes"])

    def test_suite_rejects_unsupported_case_arrays_and_duplicates(self):
        examples = [
            ((), ("normal",), 1),
            ((10,), (), 1),
            ((10, 10), ("normal",), 1),
            ((10,), ("normal", "normal"), 1),
            ((1,), ("normal",), 1),
            ((10,), ("private_data",), 1),
            (("10",), ("normal",), 1),
            ((True,), ("normal",), 1),
            ((10,), ("normal",), 4),
        ]
        for counts, profiles, rounds in examples:
            with self.subTest(cases=(counts, profiles, rounds)), self.assertRaises(
                bench.CapacityError):
                bench.run_suite(counts, profiles, rounds)

    def test_cli_requires_explicit_synthetic_ack(self):
        r = self.cli("--counts", "10", "--profiles", "normal")
        self.assertEqual(2, r.returncode)
        self.assertIn("SYNTHETIC_ONLY_ACK_REQUIRED", r.stderr)

    def test_cli_success_is_machine_readable_and_does_not_claim_sla(self):
        r = self.cli("--synthetic-only", "--counts", "10", "--profiles", "normal",
                     "--rounds", "1")
        self.assertEqual(0, r.returncode, r.stderr)
        data = json.loads(r.stdout)
        self.assertEqual(1, len(data["results"]))
        self.assertEqual(10, data["results"][0]["events"])
        self.assertFalse(data["performance_sla_or_commercial_quota_approved"])
        self.assertFalse(data["actual_customer_data_used"])

    def test_cli_rejects_unknown_count_does_not_run(self):
        for counts in ("10000", "0010", "10,10", "10,10000", "10 ; rm", "", "10,"):
            with self.subTest(counts=counts):
                r = self.cli("--synthetic-only", "--counts", counts, "--profiles", "normal")
                self.assertEqual(2, r.returncode)
                self.assertIn("REJECTED", r.stderr)
                self.assertNotIn("Traceback", r.stderr)

    def test_cli_rejects_wrong_profiles(self):
        for profile in ("raw_execution", "normal,normal", "alert_dense,real", "", "normal,"):
            with self.subTest(profile=profile):
                r = self.cli("--synthetic-only", "--counts", "10", "--profiles", profile)
                self.assertEqual(2, r.returncode)
                self.assertNotIn("Traceback", r.stderr)

    def test_cli_rounds_cap_prevents_unbounded_benchmark(self):
        r = self.cli("--synthetic-only", "--counts", "10", "--profiles", "normal",
                     "--rounds", "1000")
        self.assertEqual(2, r.returncode)
        self.assertIn("UNSUPPORTED_SYNTHETIC_ROUNDS", r.stderr)

    def test_no_socket_connect_for_generated_benchmarks(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            r = bench.run_suite((10,), ("normal",), 1)
        self.assertFalse(r["actual_customer_data_used"])

    def test_readonly_preserves_actual_sovia_audit_source(self):
        code = ROOT / "sovia_audit.py"
        before = hashlib.sha256(code.read_bytes()).hexdigest()
        bench.run_suite((10,), ("normal",), 1)
        self.assertEqual(before, hashlib.sha256(code.read_bytes()).hexdigest())

    def test_times_not_measured_as_service_level_objectives(self):
        r = bench.run_suite((10,), ("normal",), 1)
        self.assertNotIn("sla_ms", r)
        self.assertNotIn("approved_customer_quota", r)
        self.assertNotIn("guaranteed_throughput", r)

    def test_benchmark_is_not_bundled_in_old_portable(self):
        from verify_portable import FILES
        self.assertEqual(12, len(FILES))
        self.assertFalse(any("capacity_benchmark" in name for name in FILES))

    def test_count_argument_parser_strict_and_integer_conversion(self):
        self.assertEqual((10, 500),
            bench._parse_csv_option("10,500", bench.COUNTS, "FAIL"))
        self.assertEqual(("normal", "alert_dense"),
            bench._parse_csv_option("normal,alert_dense", bench.PROFILES, "FAIL"))

    def test_count_parser_rejects_numeric_tricks(self):
        for val in ("10.0", "010", "+10", "1e1", "10, 100", "10,10"):
            with self.subTest(val=val), self.assertRaises(bench.CapacityError):
                bench._parse_csv_option(val, bench.COUNTS, "INVALID_INPUT")

    def test_fixture_itself_never_contains_raw_prompt_or_customer_keys(self):
        for mode in bench.PROFILES:
            text = json.dumps(bench.make_synthetic(10, mode), ensure_ascii=False)
            for forbidden in ("raw_prompt", "customer_id", "api_key",
                              "workflowData", "credentials"):
                self.assertNotIn(forbidden, text)

    def test_report_finding_counts_remain_consistent_after_serializing(self):
        for profile in bench.PROFILES:
            r = audit.evaluate(bench.make_synthetic(100, profile))
            serialized = json.loads(json.dumps(r))
            self.assertEqual(serialized["finding_count"], len(serialized["findings"]))
            self.assertEqual(bench.expected_findings(100, profile),
                             serialized["finding_count"])

    def test_memory_metric_is_python_tracemalloc_not_rss(self):
        r = bench.run_suite((10,), ("normal",), 1)
        self.assertIn("tracemalloc", r["memory"])
        self.assertNotIn("rss_bytes", r["results"][0])
        self.assertIn("median_python_tracemalloc_peak_kib", r["results"][0])


if __name__ == "__main__":
    unittest.main()
