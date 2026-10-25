# SOVIA STATUS — P2 Korean PDF milestone
Updated: 2026-10-26 KST. Repository hibi89/SOVIA_sovereign (PUBLIC).
Branch feature/p0-audit-core; tested code commit e2ffa99485b57d1e07d6b1ac119226fb86b045ed. This documentation commit will follow; check live HEAD. main and develop last verified at 51ebaf92cbb278a10978d906da927ec644c76d97 unchanged.

## Implemented and verified locally
- P1 v0.3 core retained: bounded synthetic JSON, UTC normalization, five deterministic risk rules, honest source-pointer/unknown coverage, Korean HTML and JSON, per-file no-clobber and best-effort rollback.
- P2 v0.4 exports retained: findings/events CSV, BOM/CRLF, formula-like guard with limitations.
- P2 v0.5 optional Korean PDF: new `sovia_pdf.py` uses ReportLab only on --pdf-output, system Korean TTF auto-discovery or --pdf-font. A4 landscape, findings/severity/evidence/rationale/remedy, UTC timeline, source-not-verified disclaimer and page numbers. No standalone fonts included, no cloud or external API; base CLI has no new mandatory dependencies.
- Writer now stages strings and complete PDF bytes with exclusive no-clobber publish and best-effort rollback. Not a fully transactional multi-file system-crash guarantee.
- Local Python 3.13.5 + ReportLab 4.4.9: `python -m unittest discover -s tests -q` 66 PASS/0 FAIL. Compile PASS. Synthetic 3 event/5 finding HTML+JSON+PDF CLI PASS; PDF 1 page with Korean text extraction and visual PNG inspection PASS. Synthetic 115 event multi-page PDF 6 pages with no extracted-text coordinate overflow PASS.
- Source + PDF module + test code Git blob SHAs match validated local bytes: sovia_audit.py b63a21b48f772e8c012ae94479bc15f2f9506af1, sovia_pdf.py 84ac0387d2ae101034e247aca14603a98287f3f3, tests/test_pdf.py 666749101f9affca6f6b65559a578f9239adaa97.

## Pending or unverified
- PDF optional dependency must be installed separately by user for PDF output; font installed on OS, no standalone font shipped. Fresh independent Windows/NTFS/font rendering/Office viewer NOT VERIFIED.
- Product blueprint still missing CSV source import, SQLite persistence/idempotency, local customer UI/dashboard, sanitized authorized agent adapter, installer/backup/delete/restore, robust PII/secret and actual false-positive/operational tests. PDF is locally verified output, not product launch or certification.
- No real customer records, credentials, spending, release or production deployment. Vercel status/URL/SHA comparison NOT_APPLICABLE.
- PUBLIC repo restricts confidential content; owner permission required to change visibility, real-data flow, billing, live commercial listings, hosting.

## Next ㄱ
Check live SHA and HANDOFF first. Continue P2 #6 by scoping offline SQLite history/idempotent import and/or supported CSV source ingest. Prefer shared engine, no raw prompt storage, carefully handle persistent data backup/recovery and non-destructive migrations. Test and update docs. Do NOT close #6 or sell until the commercial gates pass.
