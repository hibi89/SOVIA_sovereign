# SOVIA HANDOFF — P2 optional PDF output (ten mandatory items)
Updated 2026-10-26 KST. Exact trigger [소비아소버린 깃헙 레포지토리 보고 작업이어가셈], shorthand ㄱ. Recheck live GitHub HEAD before acting.

## 1. Goal / use / confirmed needs / stack
Offline-first retrospective AI agent evidence/risk audit with a single shared Python core. User-approved MVP-first then gap-filling, commercial/privacy tests before real customer data, cost target 0 KRW. Future Cloud/Private conditional on demand. Current P2 phase: verified CSV exports and optional automatic Korean PDF.

## 2. Completed / changes / decisions
P1 five deterministic rules and evidence-linked HTML/JSON; P2 CSV findings/events exports, safe quoting/formula-like cells; now v0.5 PDF in `sovia_pdf.py` with optional ReportLab 4.x and locally installed Korean TTF. HTML/JSON/CSV remain stdlib-only, no remote API. PDF includes findings, risk rating, event timeline, source pointer status, caveats and pages. PDF output is staged bytes by safe writer, rejects existing files. ADR-008 compares browser print vs optional ReportLab; automatic ReportLab selected due predictable CLI while manual HTML print stays possible.

## 3. Test commands / pass fail / verified-unverified
2026-10-26 KST, local Python 3.13.5 / ReportLab 4.4.9:
- `python -m unittest discover -s tests -q` = 66 PASS 0 FAIL (54 existing +12 PDF cases).
- `python -m compileall -q sovia_audit.py sovia_pdf.py tests` PASS.
- `python sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json --pdf-output report.pdf` PASS exit 0, 3 events and 5 risk findings.
- PDF visually rendered at 145 DPI, one A4 landscape page; Korean headings and all five risk rule names extracted via PyMuPDF, no visible clipping.
- Additional 115 synthetic events -> PDF 6 pages, table header repeated in timeline pages, no word bbox outside page.
- New PDF tests check dependency-free default, bad-font fails before all output, PDF magic/header, deterministic bytes, safe finding-less case, HTML+PDF coexist, no-clobber, file rollback, raw prompt omitted and HTML/JSON/CSV/PDF all flags.
NOT VERIFIED: separate Windows/NTFS/Malgun TTF install; actual customer or n8n data, penetration/security certification, power-loss atomic batch.

## 4. Done / ongoing / pending / stopping point
P1 local proof DONE; P2 CSV output and optional Korean PDF locally verified. Pending P2 input CSV, SQLite, dashboard, genuine authorized adapter, secure redaction/PII, backup/restore/delete, installer, real Windows compatibility and commercial support/terms. Do not describe product sale-ready. Stop point after code commit e2ffa99485b57d1e07d6b1ac119226fb86b045ed and subsequent documentation commit.

## 5. Failures, evidence, root cause, attempts, pivots
Initial PDF failed locally: custom ReportLab canvas passed duplicate invariant keyword. Fixed once to override kwargs['invariant']=1; rerun PDF generation and all 66 tests PASS. Earlier browser file:// block remains testing-environment limitation, not product failure. PDF path: if optional ReportLab is absent, CLI reports installation instruction and does not publish outputs; if system TTF is missing, pass --pdf-font or use manual HTML printing. No blind retry.

## 6. Repository / branch / SHA / key files
Repo https://github.com/hibi89/SOVIA_sovereign PUBLIC; branch feature/p0-audit-core. Latest tested code commit e2ffa99485b57d1e07d6b1ac119226fb86b045ed, parent c5a61704810ffdd567e9f5e488a8648fee3bc3d5. Source sovia_audit.py, new sovia_pdf.py, tests/test_pdf.py, existing tests/test_audit.py, tests/test_delivery.py, tests/test_csv.py, examples/demo_five_rules.json. Docs STATUS.md, HANDOFF.md, GAP_MATRIX.md, TEST_PLAN.md, QUICKSTART.md, README.md, DECISIONS.md. Doc commit follows, verify live hash. main/develop unchanged at last check 51ebaf92cbb278a10978d906da927ec644c76d97.

## 7. Production URL / Vercel / run / environment
None: no Vercel project, production site, paid server/API, deployment status or production SHA mapping (NOT_APPLICABLE). Python 3.10+ planned, local 3.13.5 tested. PDF optional `python -m pip install 'reportlab>=4,<5'` then `python sovia_audit.py --input examples/demo_five_rules.json --output report.html --pdf-output report.pdf`. Windows PowerShell use `py -3`. Auto find local Korean TTF; `--pdf-font` optional. PDF package not needed for base formats.

## 8. Originals / backup / auth / protected content
main/develop unchanged, feature commit ancestry provides rollback. No original user/customer data or credentials touched. GitHub is source canonical; reports and working copies are temporary. Never upload standalone font files, raw prompts, private logs, API secrets or confidential policies to PUBLIC repo. No repo visibility, auth, billing, domain or production setting changed.

## 9. Next priorities / acceptance / approvals
On ㄱ verify latest refs/docs/code, then implement next small P2 gap: SQLite history with local deletion/recovery and stable idempotency OR structured CSV source ingest with schema-first validation. Compare storage/scope/cost, preserve read-only audit semantics and no hidden prompt persistence. Tests including normal, invalid, duplicates, and migration. Do not close issue #6 until P2 gates pass; #11 commercial security also remains. Owner approval necessary for external customer data, visibility, spending, live deployment and commercial listing. Validate Windows font/link/install when a real Windows environment is available, clearly mark unverified otherwise.

## 10. KST date, verified scope, doc basis commit
2026-10-26 KST. Basis source commit e2ffa99485b57d1e07d6b1ac119226fb86b045ed; 66 local tests, one/6-page PDF QA, source Git blob matching; no real Windows/customer/production checks. This documentation's own commit SHA must be queried after update.
