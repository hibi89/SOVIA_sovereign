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

