"""Offline synthetic triage: aggregate-only confusion counts and safe failure."""
import copy
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
import sovia_privacy_triage as triage


def baseline():
    return json.loads((ROOT / "examples/synthetic_privacy_baseline.json").read_text(encoding="utf-8"))


def queue():
    return json.loads((ROOT / "examples/synthetic_privacy_review_queue.json").read_text(encoding="utf-8"))


class PrivacyTriageTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.input = self.root / "synthetic.json"
        self.set_document(baseline())

    def set_document(self, data):
        self.input.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def cli(self, *extra):
        return subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "sovia_privacy_triage.py"),
             "--input", str(self.input), *extra],
            capture_output=True, text=True, timeout=25
        )

    def test_baseline_summary_counts(self):
        result = triage.score_suite(baseline())
        self.assertEqual("SYNTHETIC_SUITE_MATCHED", result["status"])
        self.assertEqual((9, 6, 3, 0, 0),
                         (result["total_cases"], result["true_positives"],
                          result["true_negatives"], result["false_positives"],
                          result["false_negatives"]))

    def test_review_queue_has_one_fp_and_one_fn(self):
        result = triage.score_suite(queue())
        self.assertEqual("REVIEW_REQUIRED", result["status"])
        self.assertEqual((3, 0, 1, 1, 1),
                         (result["total_cases"], result["true_positives"],
                          result["true_negatives"], result["false_positives"],
                          result["false_negatives"]))

    def test_no_raw_values_or_case_ids_returned(self):
        result = json.dumps(triage.score_suite(queue()))
        for case in queue()["cases"]:
            self.assertNotIn(case["specimen"], result)
            self.assertNotIn(case["case_id"], result)

    def test_clear_suite_not_claiming_privacy_safety(self):
        result = triage.score_suite(baseline())
        self.assertIs(False, result["privacy_absence_proven"])
        self.assertIs(False, result["representative_population_validated"])
        self.assertIs(False, result["suppression_applied"])

    def test_review_issues_do_not_create_suppression(self):
        result = triage.score_suite(queue())
        self.assertIs(False, result["suppression_applied"])
        # Existing PII checker still rejects fabricated internal IP.
        from sovia_pii_preflight import assert_no_high_risk_patterns, PreflightError
        with self.assertRaises(PreflightError):
            assert_no_high_risk_patterns("10.0.0.5")

    def test_refuse_unspecified_provenance(self):
        doc = baseline()
        del doc["synthetic_only"]
        with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_ENVELOPE"):
            triage.score_suite(doc)

    def test_refuse_false_or_string_synthetic_flag(self):
        for value in (False, 1, "true", None):
            with self.subTest(value=value):
                doc = baseline()
                doc["synthetic_only"] = value
                with self.assertRaises(triage.TriageError):
                    triage.score_suite(doc)

    def test_refuse_unknown_top_level_keys(self):
        doc = baseline()
        doc["customer_email"] = "forbidden"
        with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_ENVELOPE"):
            triage.score_suite(doc)

    def test_refuse_unknown_schema(self):
        doc = baseline()
        doc["schema_version"] = "2.0"
        with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_ENVELOPE"):
            triage.score_suite(doc)

    def test_refuse_empty_or_excessive_case_sets(self):
        for count in (0, triage.MAX_CASES + 1):
            with self.subTest(count=count):
                doc = baseline()
                doc["cases"] = [{"case_id": f"c{i}", "specimen": "safe",
                                 "expected_reject": False} for i in range(count)]
                with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_CASES"):
                    triage.score_suite(doc)

    def test_refuse_duplicate_case_identifiers(self):
        doc = baseline()
        doc["cases"][1]["case_id"] = doc["cases"][0]["case_id"]
        with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_CASE_ID"):
            triage.score_suite(doc)

    def test_refuse_invalid_case_identifiers(self):
        for value in ("MY_CUSTOMER", "user@example.com", "x" * 41, "", 4):
            with self.subTest(value=value):
                doc = baseline()
                doc["cases"][0]["case_id"] = value
                with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_CASE_ID"):
                    triage.score_suite(doc)

    def test_refuse_extra_or_missing_case_fields(self):
        for mutate in ("extra", "missing"):
            doc = baseline()
            if mutate == "extra":
                doc["cases"][0]["private_token"] = "not allowed"
            else:
                del doc["cases"][0]["expected_reject"]
            with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_CASE_FIELDS"):
                triage.score_suite(doc)

    def test_refuse_non_boolean_labels(self):
        for value in ("true", 1, None, [], {}):
            with self.subTest(value=value):
                doc = baseline()
                doc["cases"][0]["expected_reject"] = value
                with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_CASE_VALUE"):
                    triage.score_suite(doc)

    def test_refuse_nontext_blank_or_excessively_long_specimens(self):
        for value in ("", "s" * (triage.MAX_SPECIMEN_CHARS+1), 1, None):
            with self.subTest(value=type(value).__name__):
                doc = baseline()
                doc["cases"][0]["specimen"] = value
                with self.assertRaisesRegex(triage.TriageError, "TRIAGE_INVALID_CASE_VALUE"):
                    triage.score_suite(doc)

    def test_deep_or_oversized_specimen_rejected_without_content(self):
        doc = baseline()
        doc["cases"][0]["specimen"] = "x" * (triage.MAX_SPECIMEN_CHARS+1)
        self.set_document(doc)
        outcome = self.cli("--synthetic-only")
        self.assertEqual(2, outcome.returncode)
        self.assertIn("TRIAGE_INVALID_CASE_VALUE", outcome.stderr)
        self.assertNotIn(doc["cases"][0]["specimen"], outcome.stderr)

    def test_cli_requires_explicit_synthetic_ack(self):
        denied = self.cli()
        self.assertEqual(2, denied.returncode)
        self.assertIn("TRIAGE_SYNTHETIC_ONLY_ACK_REQUIRED", denied.stderr)
        self.assertEqual("", denied.stdout)

    def test_isolated_cli_baseline_succeeds_without_sample_text(self):
        result = self.cli("--synthetic-only")
        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads(result.stdout)
        self.assertEqual("SYNTHETIC_SUITE_MATCHED", summary["status"])
        self.assertNotIn(str(self.root), result.stdout)
        self.assertNotIn("user@example.com", result.stdout)

    def test_isolated_cli_review_queue_exits_nonzero_without_samples(self):
        self.set_document(queue())
        result = self.cli("--synthetic-only")
        self.assertEqual(3, result.returncode)
        summary = json.loads(result.stdout)
        self.assertEqual("REVIEW_REQUIRED", summary["status"])
        self.assertEqual(1, summary["false_negatives"])
        self.assertEqual(1, summary["false_positives"])
        self.assertNotIn("10.0.0.5", result.stdout + result.stderr)
        self.assertNotIn(str(self.root), result.stdout + result.stderr)

    def test_duplicate_json_keys_rejected_no_traceback(self):
        self.input.write_text('{"synthetic_only":true,"synthetic_only":false}', encoding="utf-8")
        result = self.cli("--synthetic-only")
        self.assertEqual(2, result.returncode)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn(str(self.root), result.stderr)

    def test_oversized_input_file_rejected_no_traceback(self):
        self.input.write_bytes(b"x" * 1_048_577)
        result = self.cli("--synthetic-only")
        self.assertEqual(2, result.returncode)
        self.assertNotIn("Traceback", result.stderr)
        self.assertNotIn(str(self.root), result.stderr)

    def test_no_network_in_scoring(self):
        with patch.object(socket.socket, "connect", side_effect=AssertionError("network")):
            self.assertEqual(9, triage.score_file(self.input)["total_cases"])

    def test_checker_invalid_sample_is_error_not_false_positive(self):
        # Distinguish matcher errors from a genuine 'suspect' classification.
        class BadChecker:
            class PreflightError(ValueError):
                pass
            @staticmethod
            def assert_no_high_risk_patterns(*args):
                raise BadChecker.PreflightError("PREFLIGHT_LIMIT_EXCEEDED")
        with self.assertRaisesRegex(triage.TriageError, "TRIAGE_CHECKER_REFUSED_INPUT"):
            triage.score_suite(baseline(), checker=BadChecker)

    def test_synthetic_population_stats_cannot_be_generalized(self):
        result = triage.score_suite(baseline())
        self.assertFalse(result["representative_population_validated"])
        self.assertNotIn("accuracy", result)
        self.assertNotIn("precision", result)
        self.assertNotIn("recall", result)


if __name__ == "__main__":
    unittest.main()
