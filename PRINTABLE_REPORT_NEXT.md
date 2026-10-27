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

