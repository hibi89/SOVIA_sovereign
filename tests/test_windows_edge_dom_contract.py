"""Fail-closed parser oracle for optional Windows Edge local-file smoke."""
from pathlib import Path
import os
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from windows_edge_local_smoke import EdgeSmokeError, assert_dom, locate_edge


class EdgeDomContractTests(unittest.TestCase):
    def test_synthetic_html_markers_pass(self):
        html = "<!DOCTYPE html><html lang='ko'><body>SOVIA Audit Lite 위험 소견 5건</body></html>"
        assert_dom(html, ("SOVIA Audit Lite", "위험 소견 5건"))

    def test_invalid_dom_or_missing_markers_fail_closed(self):
        for markup in ("", "<html><body>missing DOCTYPE</body></html>",
                       "<!DOCTYPE html><html><body>missing marker</body></html>",
                       None):
            with self.subTest(markup=markup), self.assertRaises(EdgeSmokeError):
                assert_dom(markup, ("SOVIA Audit Lite",))

    def test_marker_presence_not_a_browser_pixel_proof(self):
        html = "<!doctype html><html><body>SOVIA Audit Lite</body></html>"
        self.assertIsNone(assert_dom(html, ("SOVIA Audit Lite",)))
        with self.assertRaisesRegex(EdgeSmokeError, "BROWSER_DOM_MISSING_SYNTHETIC_MARKER"):
            assert_dom(html, ("SOVIA Audit Lite", "invalid fake text"))

    @unittest.skipIf(os.name == "nt", "Real Windows Edge tested only by integration workflow")
    def test_nonwindows_browser_probe_rejected(self):
        with self.assertRaisesRegex(EdgeSmokeError, "WINDOWS_REQUIRED"):
            locate_edge()


if __name__ == "__main__":
    unittest.main()
