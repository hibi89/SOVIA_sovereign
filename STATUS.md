# CURRENT SOVIA STATUS — 2026-10-27 P2 privacy/retention inventory merged

**GitHub source:** `hibi89/SOVIA_sovereign` public; active code `develop` PR [#17](https://github.com/hibi89/SOVIA_sovereign/pull/17) merge SHA `c462f480eb2fee35e5830ceb807c9cf2396f31d4`, HEAD will advance with this documentation update. `main` remains documentation-only/unreleased. GitHub connected account hibi89; PR commit attributed to hibi89, merge via web-flow.

**Verified scope:** new `sovia_retention.py` aggregate/read-only offline inventory, 11 focused synthetic tests and `RETENTION.md`, no file contents read, source modifications or deletion. Fixed unbounded directory-list materialization to bounded streaming. File SHA parity with local tested source verified before PR. `feature/p2-retention-inventory` integrated and **not active/reopen required**.

**PR CI:** [Actions 40454869234](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40454869234) SUCCESS **4/4** Windows/Ubuntu Python 3.11/3.13. Each job **200 tests discovered**, Windows **190 PASS / 10 SKIP**, Ubuntu **189 PASS / 11 SKIP**, **0 FAIL**; full clean extracted v0.10 ZIP self-check and SQLite/dashboard/restore still passed on all. Local module tests 11/11 pass; compileall pass. New code not included in unchanged 12-file ZIP. Post-merge push / docs-head CI **NOT VERIFIED**, do not conflate with PR CI.

**Remaining:** actual owner's Windows/browser/font/Defender acceptance, real customer authorization, supported sanitized n8n formats, original/report/backup retention and deletion policy, PII/adversarial/false-positive reviews and approval for sales. No production URL, Vercel, cloud or paid product. Do not auto-delete files or disclose private file paths. On `ㄱ` inspect latest develop HEAD, post-merge status, and proceed with safe synthetic n8n-like adapter/contract validation or privacy gate—not previous finished P1/dashboard/ZIP.

---

# SOVIA STATUS — 2026-10-27 P2 retention inventory feature checkpoint

- **Active scoped branch:** `feature/p2-retention-inventory` derived from verified develop HEAD `76d338fd43efa531364c1536fbd3d88ebca594c3` (v0.10 self-check); **main docs-only**, develop unchanged until reviewed PR.
- **Code:** `sovia_retention.py` read-only local candidate inventory, no customer file reading, no data deletion, no telemetry; tests `tests/test_retention.py`; risk/limits and manual gates in `RETENTION.md`. Exact local ↔ GitHub blob hashes verified for all three. Current code commit before status/doc commits: `37204080951451f6ca9bac7936882517b4d9aafd`.
- **Local verification 2026-10-27:** `python -m unittest discover -s /mnt/data/sovia_retention_dev/tests -v` **11 PASS / 0 FAIL** after one test-clock fixture correction; `python -m compileall` **PASS**. This is a local isolated module test, NOT full integrated or Windows CI. Pending GitHub Actions feature PR matrix review.
- **P2 gaps still OPEN:** consented/validated n8n sanitized inputs, source/report/backups retention+removal policy, PII/false-positive security review, owner Windows/browser/Defender and Korean PDF visual acceptance, paid listing approvals.
- **No production or Vercel**, no customer data, no public commercial claim, no packaging of new inventory module. New module has deliberately no removal pathway, so owner originals protected.

---

# SOVIA STATUS — P2 v0.10 owner self-check synthetic verified

**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #16](https://github.com/hibi89/SOVIA_sovereign/pull/16) merged SOVIA v0.10.0-beta Windows one-click synthetic self-check, 12-file portable ZIP and optional Korean PDF/font diagnostic into `develop` at merge SHA `60a2ea28fed91d320211ee8f8ec594c24971d472`. [Post-merge CI run 40218991467](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218991467) **4/4 SUCCESS**: Windows Python 3.11/3.13 each 189 discovered/179 PASS/10 PDF SKIP/0 FAIL, Ubuntu 3.11/3.13 each 189 discovered/178 PASS/11 SKIP (Windows .cmd test)/0 FAIL; all four include full extracted-ZIP synthetic audit/SQLite/dashboard/recovery/self-check. Same 12-file ZIP SHA256 `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`, unsigned CI artifact `sovia-portable-beta` available. **PR integration DONE; DO NOT repeat.** On `ㄱ` next: verify latest develop HEAD and continue P2 product acceptance/privacy/retention/authorized n8n-like sanitized source or adversarial tests, prioritizing safe offline work. Actual owner's Windows PC, browser visuals, AV/SmartScreen, ReportLab+Korean TTF PDF visual, customer data and commercial/production are **NOT VERIFIED** and need owner/local evidence. `main` remains docs-only and unreleased. Earlier feature-only references are archived.


**2026-10-26 KST P2 owner-PC synthetic acceptance v0.10.0-beta:** Feature branch feature/p2-owner-selfcheck implements 12-file source ZIP with RUN_SELF_CHECK.cmd + owner_selfcheck.py, an offline versioned manifest verifier, automatic synthetic audit → SQLite → HTML dashboard → backup/restore, and explicit optional Korean PDF status. Tested source SHA cadc2baf8302f9583196fba7b6618c5c264d5a24, [CI 40218607947](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218607947) 4/4 SUCCESS: Windows Python 3.11/3.13 each 189 discovered, **179 PASS / 10 optional PDF SKIP / 0 FAIL**; Ubuntu 3.11/3.13 each 189 discovered, **178 PASS / 11 SKIP / 0 FAIL** (10 optional PDF + 1 Windows launcher only). Windows RUN_SELF_CHECK.cmd executed successfully in CI; clean-extracted ZIP owner_selfcheck status AUTOMATED_PASS_MANUAL_PENDING. Exactly reproducible inner ZIP SHA256 894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b on all four environments, 12 fixed files, uploaded CI artifact sovia-portable-beta (ID 12608344203). This is GitHub-hosted synthetic acceptance, NOT actual owner's PC, browser appearance/antivirus, PDF visual verification or real client consent; sale/production not authorized. Current docs+CLI-help follow-up commit to be reverified. NEXT: PR #16 integration to develop after green head, then privacy/retention/authorized source P2 gates. main docs-only.

DONE synthetic: five risk-rule audit, source CSV/report CSV, optional PDF (not current CI), metadata-only SQLite recovery, offline static HTML dashboard, deterministic 12-file portable ZIP, new verified Windows one-click local self-check with sanitized JSON outputs and explicit manual acceptance. Original stateless CLI intact.

DONE PR #16 integration verified after merge. PENDING owner physical machine acceptance; browser Korean visual and optional PDF/TTF, Windows Defender/SmartScreen, supported consented n8n adapter, privacy/PII/retention/backups and commercial support gates. Not a signed binary, real-time blocking or ready-to-sell certified product. Production/Vercel none; main unpromoted.

NEXT on ㄱ: check current PR #16 state, merge only on verified green; then user Windows manual-run instructions and remaining P2 consent/retention+authorized synthetic connector tests, NOT restarting P1/SQLite/dashboard/installer.

---
## Archived previous status

# SOVIA STATUS — P2 v0.9 beta portable integration pending

**LATEST INTEGRATION (2026-10-26 KST):** [PR #15](https://github.com/hibi89/SOVIA_sovereign/pull/15) merged v0.9.0-beta deterministic portable ZIP/verifier/synthetic full smoke into `develop`, merge SHA `0a16a032dc26970ba197aa8e874a22fcb2a2c0a6`. [Post-merge Actions run 40217328939](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40217328939) **4/4 SUCCESS** (Windows+Ubuntu × Python 3.11/3.13), per job 177 discovered / 167 PASS / 10 optional PDF SKIP / 0 FAIL, and full clean-extracted isolated-Python audit→SQLite→dashboard→backup/restore PASS. Tested reproducible ZIP SHA256 `6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3`. `sovia-portable-beta` downloadable from Actions artifacts, unsigned ZIP+checksum, NOT an official signed Release. **On ㄱ**: inspect newest `develop`, then start P2 owner-Windows acceptance/self-check workflow (one-command local diagnostics; sample/fresh-folder tests), optional PDF/font/visual/manual verification guidance, then real authorized data/privacy/retention/failure-handling commercial gates. Do NOT redo JSON/CSV/SQLite/dashboard/package or merge PR #15 again. `main` remains docs-only; no Production/Vercel, no owner device/customer validation or sale approval. Earlier sections are archival.


**CURRENT P2 PORTABLE BETA CHECKPOINT (2026-10-26 KST):** The feature/p2-portable-package branch now builds an offline SOVIA Audit Lite 0.9.0-beta ZIP with an allowlisted 10-file source/synthetic payload, embedded manifest, detached checksum, strict verifier and new-directory-only extraction. Test SHA 7dffc94401e6843b9fa792edfd1a886e4757950b. [GitHub Actions result](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40216762276) finished **4/4 success**, Windows and Ubuntu × Python 3.11/3.13, each **177 discovered / 167 PASS / 10 optional-PDF SKIP / 0 FAIL**. Clean extracted portable ZIP passed real isolated Python audit (3 events/5 findings) → SQLite idempotency → offline HTML dashboard → SQLite backup/restore on all four jobs. Archive SHA256 **6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3** matched all four environments. The unsigned ZIP + detached checksum were uploaded as GitHub Actions artifact **sovia-portable-beta**, artifact ID 12607951989. NOT a signed installer, real customer use, user-PC validation or production. NEXT: green PR merge to develop, then owner Windows installation/browser/optional PDF testing and commercial privacy gates. Default main is docs only.

Completed synthetic: P1, CSV input/output, optional historic PDF, SQLite metadata-only history/backup/restore/purge, static Korean dashboard, new allowlisted portable ZIP with checksum and verified isolated clean install. CI 4/4 success (167 pass/10 optional PDF skip each). Artifact sovia-portable-beta is an unsigned CI output, not commercial release.

PENDING: PR review and develop integration, owner Windows fresh install/browser visual/font/AV, signed installer, privacy/retention/false positive, authorized real inputs, commercial acceptance, production (NONE). On ㄱ verify PR first, then owner acceptance and P2 hardening. Do not redo completed modules.

---

Historical status

# SOVIA STATUS — P2 v0.8 offline dashboard

**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #14](https://github.com/hibi89/SOVIA_sovereign/pull/14) merged P2 v0.8 static offline SQLite history dashboard into `develop`, merge SHA `1123851900aee34d1c02d2a4590c6a0b5852727d`. [Post-merge CI run 40215946752](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215946752) completed **4/4 SUCCESS** on Windows/Ubuntu × Python 3.11/3.13; each 148 tests discovered / 138 PASS / 10 optional PDF SKIP / 0 FAIL. All P1 and v0.7 SQLite work remain integrated. **NEXT on ㄱ**: begin P2 portable offline package/fresh-install validation on a new branch from actual latest develop, with deterministic manifest/checksums/verification, sample CLI and user setup instructions. Do not redo the dashboard/SQLite/JSON work. `main` stays documentation-only, no Vercel/production or real customer-data evidence. Independent owner-machine browser visual QA remains UNVERIFIED.

2026-10-26 KST: P2 v0.8 feature/p2-offline-dashboard implements a read-only SQLite v1 to standalone Korean HTML dashboard; no local server, JS, outbound network, data write or output overwrite. Tested source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334 4/4 SUCCESS, Windows/Ubuntu x Python 3.11/3.13, each 148 discovered/138 PASS/10 optional PDF SKIP/0 FAIL. New tests 23. Not owner PC/browser visual QA, real customer records or production.

DONE synthetic: P1 5-rule report, source JSON/CSV, guarded CSV export, optional historical PDF, opt-in SQLite v1 metadata-only history, NEW static Korean dashboard with read-only bounded queries, four KPI summaries and five tables. Original audit remains stateless. Tests 23 new; CI all 4 OS/Python jobs green. Existing records unchanged; no external service or actual customer data.

DONE: PR #14 merged into develop and 4/4 CI green. PENDING: actual owner-device HTML visual check, portable installation/upgrade/backups, retention/privacy, user support, real authorized sanitized integration, false-positive/recovery security gates. Local HTML is NOT interactive live dashboard, cryptographic anonymity, or commercial-ready product. No Vercel/Production deployed.

NEXT on ㄱ: PR #14 already merged/validated. Start portable install and packaging from current develop. Never restart P1/SQLite.

---

## Archived previous status
# SOVIA STATUS — P2 v0.7 verified synthetic SQLite history

**LATEST INTEGRATION VERIFIED — 2026-10-26 KST:** PR [#13](https://github.com/hibi89/SOVIA_sovereign/pull/13) MERGED the opt-in SQLite history (version 1, recovery and purge) into `develop` at `edf8ea3de4a4fd781de34642b3d3f07a1ff67e10`. [Develop post-merge CI 40214911902](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214911902) 4/4 SUCCESS, Windows/Ubuntu × Python 3.11/3.13; each 125 tests discovered, 115 PASS, 10 optional PDF SKIP, 0 FAIL. Source/feature integration is DONE, NOT waiting for a PR. Next safe task on `ㄱ`: create a new scoped branch from latest `develop` and implement a read-only, generated offline HTML history dashboard (no local server/network) with output no-clobber, escaped metadata, report/rule/time overview, tests; then continue installer/retention/customer authorization gates. Do not reimplement P1/CSV/PDF/SQLite. Production/Vercel none; `main` remains documentation-only, not sale-ready. The earlier feature-branch notes below are archival.


Updated 2026-10-26 KST. Repository PUBLIC. Active integrated source develop merge SHA edf8ea3de4a4fd781de34642b3d3f07a1ff67e10 (docs follows), 4/4 post-merge CI successful; main still not a released code branch.

DONE_VERIFIED on synthetic Windows+Ubuntu CI: strict JSON/CSV import, 5 policies, evidence-linked HTML/JSON, findings/events CSV export, optional earlier Linux-tested PDF, **NEW opt-in SQLite metadata-history module** with no raw event names/prompt/target/pointer persistence, report idempotency, event identity collision rollback, version-1 schema and explicit no-clobber snapshot/restore and verified purge. Baseline audit CLI remains stateless. Tests CI 40214522381: 4/4 jobs PASS, per job 125 discovered, 115 executed PASS, 10 optional PDF SKIP, 0 FAIL; 33 history cases. First Windows test failed on read-only fsync and unclosed connection test handles (run 40214395712); both fixed and rerun passed.

NOT VERIFIED: local customer's Windows/font install, real n8n/customer data, GUI, true data lifecycle beyond local history (original inputs/backups still retained), multi-process stress/disk failure, privacy legal requirements, product installer, commercial sale/production. SQLite hashed metadata is still potentially linkable and must not be described as anonymous or certified safe. No live Vercel, fees or customer secrets.

NEXT: create scoped feature branch from current develop and implement read-only offline history dashboard, clean-device packaging and P2 privacy/recovery gates. No unnecessary duplicate P1 work. Refer HISTORY.md/TEST_PLAN.md/GAP_MATRIX.md and live HANDOFF.

---

## Previous status (archived)
# SOVIA STATUS — authoritative verified P2 CSV-source checkpoint

**CURRENT INTEGRATION (2026-10-26 KST):** PR [#12](https://github.com/hibi89/SOVIA_sovereign/pull/12) merged synthetic Audit Lite P1/P2 into `develop` at merge SHA `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26`. The previous no-code baseline on `main` is HISTORICAL and `main` is intentionally not promoted. Windows+Ubuntu Python 3.11/3.13 CI run [40213287272](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272): 4/4 success, 82 passed / 10 optional PDF skipped / 0 failed per job; PR validation [40213518280](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213518280) SUCCESS. Next unblocked work is P2 SQLite metadata-only history and recovery on a **new feature branch from develop**. Verify latest HEAD, then read HANDOFF/STATUS/GAP_MATRIX. No production or user Windows/real customer-data verification.


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
