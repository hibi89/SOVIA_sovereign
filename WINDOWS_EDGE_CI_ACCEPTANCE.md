## Screenshot evidence extension — 2026-10-27 (PR proposal)

**Why:** The existing Windows Edge `--dump-dom` proof verifies Korean text and offline HTML parsing, but not rendered pixels. On the same temporary, verified/extracted v0.11.2 beta package, run Microsoft Edge headless to capture a **1440×1600 viewport** of the actual generated synthetic audit report and SQLite dashboard using `--screenshot`; validate expected PNG header and plausible dimensions with Python stdlib, upload precisely two PNGs as a **7-day GitHub Actions synthetic evidence artifact**. Rendered screenshots are real browser output, never fabricated illustrative images. Screenshots and browser profiles live outside pristine extracted ZIP; legacy archive SHA remains immutable.

**Acceptance criteria:** Windows Python 3.11 Edge must succeed in both DOM and screenshot creation; `sovia-p2-synthetic-edge-visuals` artifact must contain `synthetic-audit-edge.png` and `synthetic-dashboard-edge.png`; entire Windows/Ubuntu 3.11/3.13 suite and legacy/current portable ZIP smokes must pass. Human/assistant inspection of the retrieved PNGs is a **separate** step; uploading PNGs does not imply someone viewed them, and image header checks cannot certify legibility. If screenshots reveal a readability issue, preserve stable v0.11.2 provenance; don't patch bundled historical source or change the v0.10 hash.

**Limitations:** Viewport screenshots aren't printed pages, exhaustive scrolling, accessibility, customer UI validation, owner machine, Korean PDF, Defender/SmartScreen or a proof of Edge network silence. Browser flags reduce background network but no packet capture runs. All pages are generated from three fabricated events and offline metadata. No customer data, tokens, paid dependency, real n8n instance, Vercel or production release.

---

# P2 Windows Edge offline browser DOM smoke — synthetic, CI-only

## Need and design
Existing v0.11.2 ZIP synthetic acceptance exercises Python, SQLite and writes two HTML files; static preflights inspect strings but **do not launch a browser**. This feature runs the local Windows-installed Microsoft Edge **headless** with `--dump-dom` against **file://** copies of actual HTML generated from a freshly verified/extracted v0.11.2 beta candidate.

Alternatives: (A) repeat static HTML scans (no new evidence); (B) install an extra browser automation framework (network/dependencies, ongoing maintenance); (C) use preinstalled Windows Edge via Python stdlib subprocess (chosen; no extra dependency, narrow browser compatibility coverage, risk that runner image changes Edge path). The temporary folder and Edge profiles are synthetic only and deleted after test, with a 45-second per-page timeout.

## What CI actually verifies
1. Original pinned ZIP archive is built/verified/extracted without modifying the 18-file package, and remains pristine.
2. Offline extracted auditor generates a synthetic 3-event/5-finding HTML report.
3. SQLite import and extracted dashboard create an offline HTML dashboard.
4. On **Windows Python 3.11** CI, preinstalled Edge opens both `file://` documents and returns a parsed HTML DOM with expected Korean report sections, report count and dashboard CSP. No HTTP server and no live n8n.
5. Existing Windows/Ubuntu Python 3.11/3.13 unit/package smoke remains required, with separate portable ZIP hashes unchanged.

## Explicit limits / refusal
Headless DOM markers **do not prove visual pixel layout, print readability, keyboard accessibility, owner PC, Korean optional PDF font appearance, Defender/SmartScreen acceptance, browser absence of all network/background activity, authorized native n8n source, PII clearance or commercial readiness**. The generated HTML has no external resources; the Edge process is asked to disable background network but no packet capture runs. A missing/failed Edge installation or launch is an actual CI failure, not silently skipped. This tests a **GitHub-hosted Windows runner**, not the user's Windows installation.

No production/Vercel, paid resource, credentials, client data or real network destinations are involved. The test does not modify immutable v0.10/v0.11.2 candidate files. On repeated Edge timeout, stop and retain accurate UNVERIFIED result rather than weakening the check.

