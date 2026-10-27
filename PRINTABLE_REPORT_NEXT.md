## Actual A4 print verification — CI 2026-10-27, PR #49 MERGED

One Windows Edge v155 GitHub-hosted `--print-to-pdf` run on the opt-in `v0.12.0-preview` first produced **3 pages**, a near-empty last page with caveats only. Compacting **print CSS only** then produced **2 A4 portrait pages** (594.96×841.92 PDF points). PDF was downloaded from [CI 40502431335](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40502431335), SHA256 `9c49e874abd73457a4c9dcbcef2eef6be719b6b5ea0b08aae30b16e2e5c0fd88` (illustrative, PDF timestamps affect repeat-build hashes). Independent `pdfinfo`, `pdftotext -layout` and PDF raster review confirm 5 fabricated risk findings, 3 timeline entries, Korean caveats and no observed page clipping. The previous 3-page PDF had a near-empty caveat page and is not the approved preview shape.

This verified **actual PDF file rendering of one fabricated fixture**; it is NOT optional ReportLab Korean PDF, paper printer validation, an owner's Windows/hardware test, all-input/page-break certification, customer authorization, or signed product. Existing packaged v0.10/v0.11.2 reports remain unchanged. See [PR #49](https://github.com/hibi89/SOVIA_sovereign/pull/49).

---

## 2026-10-27 genuine A4 browser-print validation — source-only candidate

New `--print-a4-pdf` switch on existing `windows_edge_local_smoke.py` prints the opt-in **separate source-only v0.12 preview** with Windows-hosted Microsoft Edge `--print-to-pdf`; the stylesheet has `@page{size:A4 portrait;margin:13mm}` and print-only labeled cards. The optional switch requires `--next-print-preview` and `--screenshot-dir`; the output is exclusively new fabricated `synthetic-next-preview-a4.pdf` in the existing 7-day Actions artifact. Strict upper/lower file size, `%PDF-` header and `%%EOF` trailer detect empty/failed output. These checks alone do NOT verify actual A4 page dimensions or visual text legibility; the printed PDF must be downloaded, independently rasterized and inspected for page count, clipping, missing glyphs and table rows. CI must pass the Windows printer step and full Windows/Ubuntu 3.11/3.13 matrix and both portable ZIP smoke tests before merge. No customer records or output from an owner's PC.

Old frozen v0.10/v0.11.2 ZIP contents, SHA pins, and product auditor are unchanged. This is neither the optional ReportLab Korean PDF module nor a signed v0.12 package, native n8n integration, real-world safety guarantee, Windows Defender/SmartScreen approval, or sale authorization. If actual A4 pages are broken, record the defect and amend **only this distinct future renderer** before a new versioned package is designed.

---

## Actual Edge preview gate (added after initial 4/4 source-only tests, pending refreshed CI)

The existing source-only preview now participates in the **actual Windows Edge** smoke on Python 3.11 via `--next-print-preview`: execute the new `sovia_report_print_preview.py` in isolated Python against the fabricated example from a pristine extracted v0.11.2 ZIP, open the **independently generated next-version HTML** in a real headless Edge `file://` tab, verify Korean labels `data-label`, and upload a third synthetic image `synthetic-next-print-preview-edge.png` alongside the unchanged current audit/dashboard images. The new module is loaded from the **repository only**, explicitly NOT from or included in the legacy ZIP. This is a visual design candidate, not a v0.12 signed installer or proof of physically printed A4 output. A screenshot must be retrieved and inspected before claiming a visual improvement. All three pages must be synthetic; the CI screenshot artifact remains short-retention and no customer data may be used.

---

# SOVIA source-only NEXT printable HTML preview — v0.12.0-preview

## Motivation and exact scope
Actual Windows Edge screenshots of the current v0.11.2 beta audit report (GitHub Actions PR #47, artifact 12730803796) showed a narrow six-column findings table where Korean source/evidence content can wrap awkwardly. The dashboard is readable but naturally scrolls. Directly modifying `sovia_audit.render_html` in PR #42 broke **immutable historical portable ZIP checksum tests**. Do not repeat the v0.10/v0.11.2 hash mistake.

**Decision:** build a separately named, **source-only**, opt-in `sovia_report_print_preview.py` for the future v0.12 presentation. It loads the existing bounded canonical evaluator unchanged; produces escaped Korean screen-readable table cells with horizontal scrolling, print-only per-row labeled cards, a strict static HTML CSP, and no JavaScript, external fonts/assets, network, cookies or customer data. The original auditor and 18-file v0.11.2 packaging allowlist remain untouched. A fresh preview HTML is the output, not a new signed customer version, original core change or new ZIP.

## Usage — SYNTHETIC ONLY, NOT A CUSTOMER EXPORT
From a trusted checked-out repo, Python 3.11+:

```powershell
py -3 -I -B sovia_report_print_preview.py --input examples\demo_five_rules.json --output NEW_PREVIEW.html --synthetic-only
```

Open `NEW_PREVIEW.html` locally. Screen retains table column headings, scrollable width, and all five core findings plus three chronological events. Printing (A4 portrait) uses a two-table row-card layout with the fixed Korean column name repeated before each escaped value so 9-column text is not squeezed into illegible columns. A4 page-break behavior, full browser/device font rendering, optional Python PDF, print media edge cases, real n8n and owner PC require independent tests. It does NOT write into original install or overwrite a prior output.

## Tests and trust boundaries
- `tests/test_printable_preview.py`: screen/print CSS, 6+9 trusted column labels matching every emitted finding/event cell, precise 3-event/5-finding fixture, HTML escaping for hostile synthetic markup, empty-state labeling, subprocess Python `-I -B`, no-clobber, explicit synthetic CLI acknowledgement and input alias rejection.
- Full GitHub Actions Windows/Ubuntu Python 3.11/3.13 and unchanged v0.10/v0.11.2 extracted portable smoke is required before integration. Browser **print** visual pending; source-only preview is NOT included in existing ZIP. Releasing it requires a separately versioned v0.12 packaging/manifest/owner signoff, not silent replacement or re-baselining the v0.11.2 hash.
- `--synthetic-only` is an operator claim; it does NOT authenticate source provenance or prove de-identification. No live/customer/n8n records permitted. Preview HTML will display sanitized event metadata, so treat it as potentially sensitive if a future operator uses approved real data. Input source/legal consent, retention, expiry, signing, support/price and owner commercial approval remain OPEN.
- This is the **last stylistic print experiment until owner/user has decided** whether to ship it; do not spend repeated iterations making synthetic screenshot wrappers. Core audit rules, SHA and legacy package must remain unchanged.

