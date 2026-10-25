# SOVIA STATUS — authoritative verified P2 CSV-source checkpoint
Updated 2026-10-26 KST. Live repository: https://github.com/hibi89/SOVIA_sovereign, PUBLIC, feature/p0-audit-core.

## What actually works
- P1: offline bounded JSON ingestion, UTC normalization, 5 deterministic explainable rules, evidence/coverage warnings, Korean HTML+JSON; prior 67-test source scope.
- P2: guarded findings/events CSV export, optional Korean PDF on ReportLab+OS Korean TTF (historically Linux locally tested), **NEW v0.6 CSV source ingestion** with separate JSON policy, strict metadata headers/typed permission, <=1MiB/<=1000 events, existing rules unchanged.
- Commit 770172baa1dfe0eb0fd4b1a63d0afead0eaf6bc2 added importer, CLI, 25 regression tests and fake fixtures. Commit 5c99ca3ca1205a26b586a057874172f6607d3e19 added GitHub Actions for Python 3.11 & 3.13.
- GitHub run https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272 on code SHA d204b76fdb545b32696a3d8aa97c35c1ffbb1355: **4/4 SUCCESS** (Windows/Ubuntu × Python 3.11/3.13), each 92 discovered / 82 PASS / 10 optional PDF SKIP / 0 FAIL. First Windows attempt (run 40213209092) exposed a collision-error-message mismatch; the original file was still safely preserved, then Path.resolve() alias compare fixed it and rerun passed. Local CSV parser separate sandbox 17 PASS/0 FAIL. This validates synthetic GitHub-hosted Windows/NTFS basic CLI behavior but NOT the owner's actual Windows environment, optional Korean font/PDF, customers, production or release.
- Current branch is still **feature only**. main/develop 51ebaf92cbb278a10978d906da927ec644c76d97 before docs milestone, not promoted. No cloud/Vercel, public site, paid account or customers.

## Pending (P2 before selling)
Metadata-only SQLite/history, idempotent/recoverable import, clear purge+backup, read-only local GUI, n8n authorized sanitized adapter, owner-PC Windows/package/optional font check, PII & false positive suite, commercial terms and customer support boundaries. Security minimum on now; no true live intrusion prevention or certification. PUBLIC repo: synthetic data only.

## Next action on ㄱ
Verify branch HEAD and HANDOFF, compare SQLite vs flat-file storage, implement smallest backward-compatible offline SQLite history slice with determinism, duplicate/collision guards and backup/restore/delete tests. Do not change repo privacy, external transfers, payment or production without authorization.

## Historical prior snapshot (for audit trail)
# SOVIA STATUS — P2 Korean PDF milestone
Updated: 2026-10-26 KST. Repository hibi89/SOVIA_sovereign (PUBLIC).
Branch feature/p0-audit-core; tested code commit e2ffa99485b57d1e07d6b1ac119226fb86b045ed. This documentation commit will follow; check live HEAD. main and develop last verified at 51ebaf92cbb278a10978d906da927ec644c76d97 unchanged.

## Implemented and verified locally
- P1 v0.3 core retained: bounded synthetic JSON, UTC normalization, five deterministic risk rules, honest source-pointer/unknown coverage, Korean HTML and JSON, per-file no-clobber and best-effort rollback.
- P2 v0.4 exports retained: findings/events CSV, BOM/CRLF, formula-like guard with limitations.
- P2 v0.5 optional Korean PDF: new `sovia_pdf.py` uses ReportLab only on --pdf-output, system Korean TTF auto-discovery or --pdf-font. A4 landscape, findings/severity/evidence/rationale/remedy, UTC timeline, source-not-verified disclaimer and page numbers. No standalone fonts included, no cloud or external API; base CLI has no new mandatory dependencies.
- Writer now stages strings and complete PDF bytes with exclusive no-clobber publish and best-effort rollback. Not a fully transactional multi-file system-crash guarantee.
- Local Python 3.13.5 + ReportLab 4.4.9: `python -m unittest discover -s tests -q` 67 PASS/0 FAIL. Compile PASS. Synthetic 3 event/5 finding HTML+JSON+PDF CLI PASS; PDF 1 page with Korean text extraction and visual PNG inspection PASS. Synthetic 115 event multi-page PDF 6 pages with no extracted-text coordinate overflow PASS.
- Source + PDF module + test code Git blob SHAs match validated local bytes: sovia_audit.py b63a21b48f772e8c012ae94479bc15f2f9506af1, sovia_pdf.py 84ac0387d2ae101034e247aca14603a98287f3f3, tests/test_pdf.py 666749101f9affca6f6b65559a578f9239adaa97.

## Pending or unverified
- PDF optional dependency must be installed separately by user for PDF output; font installed on OS, no standalone font shipped. Fresh independent Windows/NTFS/font rendering/Office viewer NOT VERIFIED.
- Product blueprint still missing CSV source import, SQLite persistence/idempotency, local customer UI/dashboard, sanitized authorized agent adapter, installer/backup/delete/restore, robust PII/secret and actual false-positive/operational tests. PDF is locally verified output, not product launch or certification.
- No real customer records, credentials, spending, release or production deployment. Vercel status/URL/SHA comparison NOT_APPLICABLE.
- PUBLIC repo restricts confidential content; owner permission required to change visibility, real-data flow, billing, live commercial listings, hosting.

## Next ㄱ
Check live SHA and HANDOFF first. Continue P2 #6 by scoping offline SQLite history/idempotent import and/or supported CSV source ingest. Prefer shared engine, no raw prompt storage, carefully handle persistent data backup/recovery and non-destructive migrations. Test and update docs. Do NOT close #6 or sell until the commercial gates pass.

## Isolated-Python PDF hotfix — 2026-10-26 KST
- During extracted ZIP independent smoke, `python -I -B sovia_audit.py ... --pdf-output ...` initially failed because isolated Python excludes the script directory from sys.path. Existing normal-mode PDF and prior 66 tests worked; this exposed an untested packaging path, not a runtime production incident.
- Fixed optional module loading to import ONLY the adjacent `sovia_pdf.py` via `importlib.util.spec_from_file_location`, without network or global sys.path mutation. Added isolated-PDF regression; final developer run `python -m unittest discover -s tests -q`: **67 PASS / 0 FAIL**, syntax PASS, isolated `-I -B` output PASS.
- Verified from extracted ZIP `SOVIA_Audit_Lite_P2_PDF_verified.zip`: 67 tests PASS, HTML+JSON+PDF CLI smoke PASS (3 events / 5 findings). ZIP SHA-256 `2fdc573567edd691a3c19280b24ca4932ea5d0092a6ab327ee1da394375639ff`. No standalone font files in ZIP.
- Final tested code hotfix GitHub SHA `a7a1c6b8e1518887c357aa101c8d254b228c4270`. P2 incomplete: Windows/NTFS and user-side ReportLab/Malgun Gothic, genuine sanctioned input and commercial safety remain UNVERIFIED. Deployment NONE.
