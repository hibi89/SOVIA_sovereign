# SOVIA — watermarked synthetic buyer sample pack (P2 source-only)

**Not published. No screenshots generated or represented as real. No customer records, signatures, production deployment or supported live n8n instance.**

## Why this is distinct

Existing `sovia_audit.py` already generates a valid offline retrospective report; `owner_selfcheck.py` tests a 12-file portable v0.10 demo, and the owner static preflight checks the generated HTML/JSON. However [LISTING_PREP.md](LISTING_PREP.md) still lacks a reproducible customer-facing **sample report** with obvious visible and printable synthetic warnings. This module supplies exactly that marketing review artifact without inventing a client case or opening a marketplace listing.

## Generate an actual local draft

From trusted `develop` source, with Python 3.11+:

```powershell
py -3 -I -B sovia_demo_pack.py --synthetic-only --output-dir "LOCAL_NEW_UNUSED_DIRECTORY"
```

It accepts **no arbitrary customer input**, only the repository's locked fabricated `examples/demo_five_rules.json`. Exact decoded JSON equality guards against any altered example file or hidden extra prompt/content field. It runs the actual canonical SOVIA `evaluate()` then `render_html()`: 3 fabricated events and precisely the 5 original explainable rules. Output is an entirely new empty directory; no file overwrites, network calls, dependency installation or remote publication.

Files generated:

| File | Meaning |
|---|---|
| `SOVIA_SAMPLE_REPORT.html` | Real engine HTML with bold visible **SAMPLE / 합성 예시** banner, printable warning and offline restrictive CSP |
| `SOVIA_SAMPLE_REPORT.json` | Exact engine report wrapped in mandatory synthetic sample label and false release/permission flags |
| `SOVIA_SAMPLE_SCOPE.md` | Buyer-facing scope and all remaining unverified assumptions |
| `SOVIA_SAMPLE_MANIFEST.json` | Unsigned SHA-256 and byte length of other three files to detect accidental edits, **not** identity or provenance authentication |

The demo uses fictitious IDs, `.example` hostnames and `synthetic:` evidence pointers. The original HTML is enhanced only at rendering time; `sovia_audit.py` stays unchanged. All five findings remain algorithmically generated, not hardcoded into the report. JSON values are fabricated, not sanitized real customer records.

## Important limits

- **A sample is not a verified customer case, positive security audit, compliance result, or independent approval.** The file-level SHA-256 manifest can be recomputed and is not signed.
- The watermark is a straightforward on-screen/print banner, not tamper-proof watermarking, secure screenshot enforcement or a PDF watermark.
- Actual screenshots for a sales listing must be captured from the real running app and reviewed by the owner. This source-only draft does **not** publish a listing, public website, GitHub Release, marketing outreach, invoice or download.
- Owner's physical Windows/browser/Korean optional PDF/Defender checks remain unverified, as do installed n8n compatibility, customer permission and privacy/retention/backup/support terms.
- This is *not* included in unchanged v0.10 12-file portable ZIP and `main` is still docs-only. Production and sales require owner approval.

## Reproducible QA

```powershell
py -3 -m unittest discover -s tests -p test_demo_pack.py -v
py -3 -m unittest discover -s tests -v
py -3 portable_smoke.py
```

Tests cover full real-engine reproduction, exact five findings, visible and printable SAMPLE notice, JSON metadata, local SHA integrity, no network, isolated CLI, existing-output protection, simulated altered/private fixture, writer rollback, and unchanged portable-file list. CI on GitHub-hosted Windows/Ubuntu is **not** a real owner desktop acceptance.
