# SOVIA blueprint vs verified implementation (2026-10-26 KST, CSV-source checkpoint)
Feature CSV commit 770172baa1dfe0eb0fd4b1a63d0afead0eaf6bc2; CI 5c99ca3ca1205a26b586a057874172f6607d3e19. Windows+Ubuntu Python 3.11/3.13 on GitHub Actions run 40213287272: 4/4 success, each 92 tests discovered, 82 pass, 10 optional-PDF skip, 0 fail. DONE_VERIFIED means synthetic scope only.

| Original requirement | State | Evidence and remaining gap |
|---|---|---|
| Offline deterministic shared core and UTC event normalization | DONE_VERIFIED P1 | Five rules, fake events, no mandatory external API |
| Bounded structured JSON import | DONE_VERIFIED P1 | 1MiB / 1000 events / depth 16; security hardening P2 |
| Five evidence-linked rules, unknown coverage | DONE_VERIFIED (pointer coverage partial) | Independent provenance and false positives pending |
| Korean HTML findings and UTC timeline | DONE_VERIFIED P1 | Chromium markup inspected; actual Windows file-open unverified |
| JSON report | DONE_VERIFIED P1 | Machine-readable, fixed reporting schema |
| CSV **export** of findings and events | DONE_VERIFIED P2 local | Two optional flags, 5+3 rows, BOM/CRLF, formula-like cell guard, non-clobber; Excel version/import settings unverified |
| CSV **import** of source logs | DONE_VERIFIED P2 synthetic | Strict allowlisted CSV + separate bounded JSON policy; 1MiB/1000 events, 25 new CI cases, JSON report oracle equality; real n8n/customer shape unverified |
| CSV spreadsheet-injection protection | PARTIAL P2 | Tested formula prefix cases, but no universal guarantee across spreadsheet apps |
| Atomic output (per file) and rollback | DONE_VERIFIED for tested failures | Multi-file publication not truly transactional, Windows/hardlinks pending |
| Reproducible CLI / tests | DONE_VERIFIED 82 executed / 10 skipped × 4 OS/Python CI jobs | GitHub Actions Ubuntu+Windows 3.11/3.13 with isolated CLI; optional PDF dependency/font skipped, owner's independent Windows not verified |
| Korean PDF report | PARTIAL VERIFIED P2 | Optional ReportLab 4.4.9 + installed Korean TTF; 1-page synthetic PDF and 6-page 115-event test. Separate Windows font/NTFS test pending |
| SQLite storage, history and dedup | DONE_VERIFIED P2 synthetic scope | Opt-in v1 hash-only SQLite, transaction/idempotency/conflict, explicit backup/restore/purge; retention UI, future migrations, customer machine & stress not verified |
| Customer-oriented local GUI/dashboard | PARTIAL VERIFIED P2 | Read-only static Korean HTML, 4 KPI metrics, severity/rule/reports/findings/event view, 23 tests in four OS/Python CI jobs; no live filtering/customer install/browser QA |
| Sanitized n8n or other genuine authorized adapter | PLANNED P2 | Customer data/permission gate |
| Installer, deletion and backup/restore | PLANNED commercial P2 | Pre-sale mandatory |
| PII masking, adversarial inputs, false-positive review | PARTIAL (early basic tests) | Full pre-sale checks remain |
| Cloud / Private / Hybrid | NOT STARTED future | Revenue demand and explicit owner approvals |

Preserve the original final architecture. Nothing labeled sale-ready, production-ready or externally certified.

## PDF milestone, 2026-10-26
PDF is produced by --pdf-output when optional ReportLab is installed and a local Korean TrueType font exists. It includes findings, evidence state, UTC timeline, unknown scope and page footers. Rendered PNG and selectable Korean text inspected locally. This is not certified PDF/A, digital signature or verified original evidence. User's Windows system font, package install and arbitrary input robustness remain UNVERIFIED.

## Source CSV milestone (2026-10-26)
Only canonical metadata headers accepted: event_id, occurred_at_utc, agent_id, run_id, tool_name, target, destination_domain, permission_asserted, outcome, source_pointer. Required core five headers. `--policy` JSON must contain schema_version 1.0 and policy object only. CSV does not execute tool_name or formulas. Source CSV and policy never overwritten by an output path. CI linked in STATUS. SQLite, dashboard and true sanitized customer adapter still pending.

## SQLite v0.7 (2026-10-26)
Verified GitHub Actions run 40214522381 on Ubuntu+Windows Python 3.11/3.13: 4/4 success; each 125 discovered/115 PASS/10 PDF SKIP/0 FAIL. Historical first Windows regression run 40214395712 failed on read-only fsync and SQLite connection cleanup; fixed and green rerun. Database and backups contain pseudonymized hashes and timestamps, not raw prompt/target/tool/agent/source-pointer strings. SHA-256 pseudonymization is not full anonymity, and original files/exported reports/backups need separate retention and deletion procedures. Full P2 commercial gate OPEN.

## P2 v0.8 static GUI scope 2026-10-26
2026-10-26 KST: P2 v0.8 feature/p2-offline-dashboard implements a read-only SQLite v1 to standalone Korean HTML dashboard; no local server, JS, outbound network, data write or output overwrite. Tested source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334 4/4 SUCCESS, Windows/Ubuntu x Python 3.11/3.13, each 148 discovered/138 PASS/10 optional PDF SKIP/0 FAIL. New tests 23. Not owner PC/browser visual QA, real customer records or production.
This is a local snapshot, not a live customer admin portal. Do not mark commercial dashboard DONE until owner-machine and consent/privacy/install gates.
