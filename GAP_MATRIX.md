# SOVIA blueprint vs verified implementation (2026-10-26 KST)
P2 code commit 6b3be7a4512049caa5a329776e2a63462cd6c8fa, feature/p0-audit-core. Local Python 3.13.5 test 54 PASS / 0 FAIL. DONE_VERIFIED means synthetic local scope only.

| Original requirement | State | Evidence and remaining gap |
|---|---|---|
| Offline deterministic shared core and UTC event normalization | DONE_VERIFIED P1 | Five rules, fake events, no mandatory external API |
| Bounded structured JSON import | DONE_VERIFIED P1 | 1MiB / 1000 events / depth 16; security hardening P2 |
| Five evidence-linked rules, unknown coverage | DONE_VERIFIED (pointer coverage partial) | Independent provenance and false positives pending |
| Korean HTML findings and UTC timeline | DONE_VERIFIED P1 | Chromium markup inspected; actual Windows file-open unverified |
| JSON report | DONE_VERIFIED P1 | Machine-readable, fixed reporting schema |
| CSV **export** of findings and events | DONE_VERIFIED P2 local | Two optional flags, 5+3 rows, BOM/CRLF, formula-like cell guard, non-clobber; Excel version/import settings unverified |
| CSV **import** of source logs | PLANNED P2 | Not available; do not conflate with export |
| CSV spreadsheet-injection protection | PARTIAL P2 | Tested formula prefix cases, but no universal guarantee across spreadsheet apps |
| Atomic output (per file) and rollback | DONE_VERIFIED for tested failures | Multi-file publication not truly transactional, Windows/hardlinks pending |
| Reproducible CLI / tests | DONE_VERIFIED 54/54 | Isolated same-machine copy; fresh Windows not tested |
| Korean PDF report | PARTIAL VERIFIED P2 | Optional ReportLab 4.4.9 + installed Korean TTF; 1-page synthetic PDF and 6-page 115-event test. Separate Windows font/NTFS test pending |
| SQLite storage, history and dedup | PLANNED P2 | Need idempotency, schema/migration, recovery |
| Customer-oriented local GUI/dashboard | PLANNED P2 | Usability and install packaging |
| Sanitized n8n or other genuine authorized adapter | PLANNED P2 | Customer data/permission gate |
| Installer, deletion and backup/restore | PLANNED commercial P2 | Pre-sale mandatory |
| PII masking, adversarial inputs, false-positive review | PARTIAL (early basic tests) | Full pre-sale checks remain |
| Cloud / Private / Hybrid | NOT STARTED future | Revenue demand and explicit owner approvals |

Preserve the original final architecture. Nothing labeled sale-ready, production-ready or externally certified.

## PDF milestone, 2026-10-26
PDF is produced by --pdf-output when optional ReportLab is installed and a local Korean TrueType font exists. It includes findings, evidence state, UTC timeline, unknown scope and page footers. Rendered PNG and selectable Korean text inspected locally. This is not certified PDF/A, digital signature or verified original evidence. User's Windows system font, package install and arbitrary input robustness remain UNVERIFIED.
