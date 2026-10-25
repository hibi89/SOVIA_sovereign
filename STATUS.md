# SOVIA STATUS — P2 CSV export milestone
Updated: 2026-10-26 KST. Repository: hibi89/SOVIA_sovereign, PUBLIC.
Working branch: feature/p0-audit-core. Verified code+test commit: 6b3be7a4512049caa5a329776e2a63462cd6c8fa.
Docs commit follows separately; always verify live branch head. main/develop remain at 51ebaf92cbb278a10978d906da927ec644c76d97 at inspection.

## Verified DONE (synthetic, local)
- P1 shared offline Python standard library audit v0.3: 5 deterministic rules, HTML findings/event timeline + JSON, event IDs and unverified evidence-pointer statuses, safe bounded JSON ingest and no-clobber report writes.
- P2 CSV export v0.4.0 added: two OPTIONAL flags --findings-csv and --events-csv, alongside existing --output HTML and optional --json-output. Findings contain rule, severity, event ID, source pointer, evidence status, rationale and remedy. Events sorted by normalized UTC time. Stable column schema; UTF-8 BOM, CRLF, csv.writer quote handling. Common spreadsheet formula-like cell prefixes guarded by leading apostrophe, not a universal Excel/Google Sheets security certification.
- Reuses original write_reports_atomically staging/exclusive-hardlink no-clobber; pre-existing CSV blocks all outputs, simulated fourth publish failure unwinds files. No data transmitted externally.
- Command: python -m unittest discover -s tests -v => 54 PASS / 0 FAIL on Python 3.13.5. python -m compileall -q sovia_audit.py tests => PASS.
- End-to-end synthetic four-file smoke (HTML/JSON/findings CSV/events CSV): PASS, 3 events / 5 findings / 5 CSV rows for findings / 3 rows for events. Clean temporary copy with python -I -B and all four outputs: PASS on same machine.
- Local Git blob SHA matched uploaded remote blobs: sovia_audit.py eb886ab5d9a24663f3414cecf74c5dcd9d48f205; tests/test_csv.py 29858eca381a9e161554bc02cd78776278d7034f.

## NOT IMPLEMENTED / UNVERIFIED
- CSV IMPORT is NOT implemented. CSV exports are synthetic and rule evidence is not independently verified. Actual spreadsheet app tests across Excel versions, formula guard under arbitrary import settings, Windows NTFS hardlinks, separate Windows clean install are UNVERIFIED.
- PDF, SQLite history/idempotency, local dashboard, genuine authorized n8n adapter, PII/secret scanning and disclosure, deletion/backup/recovery, packaging/license and sales-readiness security are P2 pending.
- Cloud, Private, Hybrid, production/Vercel and paid users: NOT STARTED/NOT APPLICABLE.
- PUBLIC repo: do not commit raw customer logs, private prompts, API tokens or sensitive company policy.
- HTML/JSON/CSV multi-file publication uses best-effort rollback; NOT atomic as a group under concurrent readers/power failure.

## Next priority (ㄱ)
P2 #6: test PDF via print-ready HTML or a dependency-free PDF path and compare feasibility; alternatively implement SQLite event history with deterministic dedup. Prioritize customer-visible output and offline packaging while protecting P1/P2 tested behavior. Keep CSV import distinct from CSV exports in GAP_MATRIX. Run regression, update HANDOFF/STATUS, then review develop integration. User approval needed before repo privacy change, real data, payments, commercial release or production deployment.
