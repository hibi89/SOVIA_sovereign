"""Fail-closed parser oracle for optional Windows Edge local-file smoke."""
from pathlib import Path
import os
import sys
import tempfile
import struct
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from windows_edge_local_smoke import EdgeSmokeError, assert_dom, locate_edge, _png_size, validate_printed_pdf, smoke


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

    def test_screenshot_png_header_and_viewport_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.png"
            p.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) +
                          b"IHDR" + struct.pack(">II", 1440, 1600) +
                          b"X" * 1100)
            self.assertEqual([1440, 1600], _png_size(p))

    def test_screenshot_invalid_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.png"
            for payload in (
                b"not a PNG" * 200,
                b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) +
                b"IHDR" + struct.pack(">II", 1, 1) + b"X" * 1100,
                b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) +
                b"IHDR" + struct.pack(">II", 1440, 1600),  # truncated
            ):
                p.write_bytes(payload)
                with self.assertRaisesRegex(EdgeSmokeError, "EDGE_SCREENSHOT_INVALID"):
                    _png_size(p)

    def test_pdf_transport_header_and_trailer_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "synthetic.pdf"
            p.write_bytes(b"%PDF-1.7\n" + b"0" * 2048 + b"\n%%EOF\n")
            self.assertTrue(validate_printed_pdf(p))
            for body in (b"X" * 4096, b"%PDF-1.7\n" + b"A" * 4096,
                         b"%PDF-1.7\n%%EOF\n"):
                p.write_bytes(body)
                with self.subTest(size=len(body)), self.assertRaisesRegex(
                        EdgeSmokeError, "EDGE_PRINT_PDF_INVALID"):
                    validate_printed_pdf(p)

    def test_print_pdf_requires_explicit_preview_and_new_results(self):
        with patch("windows_edge_local_smoke.locate_edge", return_value=Path("synthetic-edge")):
            with self.assertRaisesRegex(EdgeSmokeError, "A4_PREVIEW_OUTPUT_REQUIRED"):
                smoke(None, next_print_preview=True, print_a4_pdf=True)
            with self.assertRaisesRegex(EdgeSmokeError, "A4_PREVIEW_OUTPUT_REQUIRED"):
                smoke("any-new-folder", next_print_preview=False, print_a4_pdf=True)

    @unittest.skipIf(os.name == "nt", "Real Windows Edge tested only by integration workflow")
    def test_nonwindows_browser_probe_rejected(self):
        with self.assertRaisesRegex(EdgeSmokeError, "WINDOWS_REQUIRED"):
            locate_edge()


if __name__ == "__main__":
    unittest.main()
