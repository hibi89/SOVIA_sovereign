# CURRENT SOVIA HANDOFF — 2026-10-27 P2 n8n sanitized contract (10 sections)

## 1. Goal, confirmed requirements, technology
Develop zero-cost offline-first retrospective AI agent behavior audit. P1 audit, P2 CSV/PDF/SQLite/dashboard, v0.10 self-check and previous retention inventory already integrated. This iteration adds **synthetic-only strict n8n-like metadata ingest**, Python stdlib and existing canonical audit engine; NOT n8n raw export ingest or n8n API.
## 2. Completed changes, decisions and reasons
Compared raw native n8n execution ingest (high PII exposure/version-specific and maintenance) vs strict pre-sanitized contract (explicit human sanitization, small zero-cost safe surface). Chose latter. Added `sovia_n8n_sanitized.py`, `tests/test_n8n_sanitized.py` (20 new cases), `examples/demo_n8n_sanitized.json`, `N8N_SANITIZED.md`; fail-closed unknown fields, limits 1 MiB/1000 events, source/evidence/permission not trusted, no-clobber canonical JSON. [PR #18](https://github.com/hibi89/SOVIA_sovereign/pull/18) merged; old runtime modules and 12-file portable ZIP untouched.
## 3. Test commands and actual outcome
CI [40456761731](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40456761731) on PR-head `76a898e175dfcfce8fa7b188bf9b21a72eb8eeb2` 4/4 success: Ubuntu and Windows, Python 3.11/3.13 each 220 discovered; Windows 210 PASS/10 SKIP, Ubuntu 209 PASS/11 SKIP, failures 0. `python -m unittest discover -s tests -v`, source compile, and `python portable_smoke.py` end-to-end all green incl 3-event/5-finding old ZIP, SQLite/dashboard/restore. Current post-merge/docs HEAD workflow and owner's actual Windows/browser are **UNVERIFIED**. Local container clone failed DNS; not treated as test failure. No real customer data used.
## 4. Done / in progress / pending / stop
DONE synthetic contract converter and 20 tests, reviewed PR + develop integration. P2 real n8n adapter, authorization/PII upstream sanitization and legitimate retention/removal remain **OPEN**. Owner Windows self-check and optional PDF/Defender visual inspection **PENDING**. Stopping point after integration and docs update.
## 5. Errors/evidence/root causes/retry/pivot
Local unauthenticated container clone could not resolve `github.com` (network DNS unavailable); instead used connected GitHub connector and successful independent Actions CI. No source defect detected by the 4-job matrix. Any unexpected native n8n fields are REJECTED deliberately rather than silently copied or executed. Do not loop on network clone or reimplement existing P1/P2.
## 6. Repository/branch/SHA/paths
Repo `hibi89/SOVIA_sovereign` PUBLIC, default `main` docs-only. Source feature `feature/p2-n8n-sanitized-contract` verified CI SHA `76a898e175dfcfce8fa7b188bf9b21a72eb8eeb2`; merge to `develop` SHA `db44dccb81f5d867de47df2797451b69de86d260`. Main changed files `sovia_n8n_sanitized.py`, `tests/test_n8n_sanitized.py`, `examples/demo_n8n_sanitized.json`, `N8N_SANITIZED.md`, `STATUS.md`, `HANDOFF.md`, `GAP_MATRIX.md`. Refresh develop HEAD after docs.
## 7. Production URL/Vercel/project/commands
Production URL NONE, Vercel NONE, deployment N/A; no paid usage. Developer CLI: `python sovia_n8n_sanitized.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --output NEW_CANONICAL.json`, then `python sovia_audit.py --input NEW_CANONICAL.json --output NEW_REPORT.html`. Existing portable beta v0.10 unchanged, not packaged with converter.
## 8. Originals, backup, credentials, protected assets
No real customer logs, secrets, raw prompts or credentials sent to GitHub; all fixtures synthetic. No external APIs, access/visibility changes, destructive backups/retention automation or raw log collection. Output is new-file-only. Sanitized IDs/domain are syntactically restricted but may still be personal/linkable; requires customer authorization and independent review before pilot.
## 9. Next tasks, acceptance, approvals
Verify updated develop SHA and workflow if available. Next P2 implement/test strict consent/sanitization guidance and negative synthetic fixtures, then formal retention/privacy, supported n8n version contract and independent owner's Windows/AV/Korean PDF acceptance. Owner approval required for actual data, raw ingestion, privacy setting changes, external API/customer information, deployment, sales, or deletion.
## 10. KST update/verification scope/document basis
2026-10-27 KST. Verified live develop merge SHA `db44dccb81f5d867de47df2797451b69de86d260` and PR CI 40456761731 success. Post-document HEAD must be checked separately; no production/end-user/real data verification. This latest section supersedes earlier archived snapshots below.

---

# CURRENT HANDOFF — 2026-10-27 P2 read-only retention inventory integration

## 1. Goal, requirements, technology
Continue SOVIA offline-first retrospective agent evidence audit. P1/P2 Audit Lite base already developed. This checkpoint closes only a safe P2 inventory subgap with stdlib Python read-only metadata traversal; no auto-delete, live client input or cloud.
## 2. Completed work and decisions
Compared automatic expiration/deletion (potentially irreversible without approval and legal-hold rules) vs read-only candidates summary (non-destructive). Implemented latter as `sovia_retention.py` + `tests/test_retention.py` + `RETENTION.md`; fixed directory scanning to streaming under max-entry cap. PR #17 merged to develop SHA `c462f480eb2fee35e5830ceb807c9cf2396f31d4`. Existing 12-file portable ZIP unchanged; prior audit modules untouched.
## 3. Tests and scope
Local 11/11 pass, compileall pass; reviewed matching GitHub SHA blobs. PR-head GitHub [Actions 40454869234](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40454869234) 4/4 successful, each 200 tests discovered / zero fails; Windows 190 passed, 10 optional PDF skipped, Ubuntu 189 passed, 11 skipped. Extracted 12-file ZIP smoke 3 events/5 findings + SQLite/dashboard/recovery passed all jobs. Actual owner machine and post-merge/docs CI not independently verified.
## 4. Done, active, pending, stop point
DONE P2 inventory synthetic integration; IN PROGRESS privacy/retention/customer adapter gates; PENDING owner-device visual acceptance, sanctioned real data, policy deletion safeguards and commercial readiness. Stop after verified PR #17 merge and document refresh; do not re-merge #17.
## 5. Failures, cause, retries, alternatives
First local test failed because synthetic fixture timestamp `now=2000000000` was ahead of actual subprocess time. Fixed CLI-only test timestamp and retested 11 green. Review identified memory scaling issue in directory listing; changed to streaming and retested 11 green, PR matrix 4 green. No production failure observed. Alternatives compared in `RETENTION.md`.
## 6. Repo, refs, SHAs, paths
GitHub `hibi89/SOVIA_sovereign` PUBLIC; working integration `develop` merged `c462f480eb2fee35e5830ceb807c9cf2396f31d4`; source PR head `deb8b941d0e65d314a8ef728e5321278116de9b0`; default `main` docs-only/unreleased. Modified `sovia_retention.py`, `tests/test_retention.py`, `RETENTION.md`, `STATUS.md`, `HANDOFF.md`, `GAP_MATRIX.md`. Check freshest develop HEAD after docs.
## 7. Production URL, Vercel, commands
Production NONE, Vercel NONE, pricing/payment NONE (N/A). Development command `python sovia_retention.py --root PRIVATE_FOLDER --older-than-days 30`; tests `python -m unittest discover -s tests -v`. Read-only code not yet packaged for owner.
## 8. Originals, backup, credentials
No private customer data read or uploaded, no secrets committed; GitHub PUBLIC, no visibility/access/security settings modified. Inventory never opens file contents, never returns file names/paths, never deletes or mutates files. Metadata candidates do not prove lawful expiration; backups/sidecars/exports need independent retention policy. No backup loss.
## 9. Next action, acceptance and approvals
Verify latest develop SHA and any post-merge workflow; next implement supported authorized *synthetic n8n-like* sanitized adapter and PII/retention review tests without customer logs, preserve prior work. Require owner permission for repo privacy, deletion, external transfer, commercial listing and deployment. Owner must independently accept Windows/browser/AV/font PDF behavior before sale.
## 10. Updated date/time, scope, basis
2026-10-27 KST, verified live repository PR #17 merge and PR-head Actions matrix (4/4). This handoff is documentation after code merge, so source merge SHA above is the baseline; latest documentation HEAD must be fetched after commit. Not a production or owner-client acceptance. Newest current section supersedes older dated snapshots below.

---

# SOVIA HANDOFF — 2026-10-27 retention inventory feature (10 mandatory sections)

## 1. Goal/confirmed scope/technology
Continue SOVIA offline-first Audit Lite P2 commercial gates after v0.10 synthetic Windows self-check. This unit is Python standard-library **read-only aggregate retention inventory**, not real retention enforcement/deletion. Repo public and synthetic only.
## 2. Completed functions and decision
Created `sovia_retention.py`, 11 focused synthetic regression tests, `RETENTION.md`. Compared auto-expiry deletion (convenient but destructive and requires consent/legal-hold/backup rules) versus read-only candidate inventory (low-risk); selected read-only. Old P1 five rules, CSV, optional PDF, SQLite, dashboard, portable, self-check untouched; v0.10 shipped ZIP unchanged.
## 3. Tests and evidence
Executed local isolated `python -m unittest discover -s /mnt/data/sovia_retention_dev/tests -v`: **11 PASS / 0 FAIL**. `compileall` PASS. One initial test fixture used a future synthetic clock for a subprocess relying on actual time; corrected test fixture and reran green. Exact three GitHub file blob SHAs matched corresponding local `git hash-object`. Full repo CI and owner Windows end-to-end remain **NOT VERIFIED** at this checkpoint; get live GitHub Actions results after PR.
## 4. Work status/stopping point
DONE scoped read-only tool + local focused tests; IN PROGRESS PR/CI and handoff docs; PENDING owner PC acceptance and verified authorized n8n data privacy/retention, real customer workflows. Automatic deletion and sales not approved.
## 5. Errors/root cause/attempt/pivot
Initial local CLI age threshold test failed because `now=2000000000` test setup made fixtures future-relative to subprocess wall clock; adjusted only CLI test file mtime to actual wall clock minus 40 days. Single improved retry passed all 11. No runtime production incident. Do not reimplement P1/CSV/SQLite/dashboard/self-check.
## 6. Repository/branch/SHA/paths
`hibi89/SOVIA_sovereign`, PUBLIC; `feature/p2-retention-inventory` from develop `76d338fd43efa531364c1536fbd3d88ebca594c3`. Code+tests+doc commit (before these status commits) `37204080951451f6ca9bac7936882517b4d9aafd`. Changed `sovia_retention.py`, `tests/test_retention.py`, `RETENTION.md`, `STATUS.md`, `HANDOFF.md`, `GAP_MATRIX.md`. Check latest HEAD and PR before merging.
## 7. Production/environment/commands
No Vercel project or production URL; deployment N/A. Developer-only command: `python sovia_retention.py --root PRIVATE_FOLDER --older-than-days 30`, metadata-only aggregated stdout. Local tests above, CI `python -m unittest discover -s tests -v`. Not included in 12-file v0.10 portable ZIP.
## 8. Originals/backups/credentials
No real customer files accessed. Script reads only filesystem metadata in user-specified local directory, outputs no filenames/paths, and does not delete/modify anything. No external APIs, secrets, account changes, data uploads, remote storage, or GitHub visibility change.
## 9. Next priority/acceptance/approval
Review PR head/test identity and cross-OS full GitHub Actions. If green, integrate to `develop` through normal PR, refresh STATUS/HANDOFF there. Next: controlled synthetic n8n-like sanitized source validation and real ownership/retention rules; manual owner Windows/visual check. Seek owner approval before deletion semantics, repository privacy change, real customer data, sales or deployment.
## 10. KST verification/scope/document basis
2026-10-27 KST. Based on GitHub develop `76d338...`, current feature code `3720408...` and local file-level parity/tests; no independent remote full CI or production evidence claimed yet. Verify final doc commit SHA after writing; subsequent CI evidence supersedes this checkpoint.

---

# SOVIA HANDOFF — P2 v0.10 Windows owner self-check (ten sections)

**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #16](https://github.com/hibi89/SOVIA_sovereign/pull/16) merged SOVIA v0.10.0-beta Windows one-click synthetic self-check, 12-file portable ZIP and optional Korean PDF/font diagnostic into `develop` at merge SHA `60a2ea28fed91d320211ee8f8ec594c24971d472`. [Post-merge CI run 40218991467](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218991467) **4/4 SUCCESS**: Windows Python 3.11/3.13 each 189 discovered/179 PASS/10 PDF SKIP/0 FAIL, Ubuntu 3.11/3.13 each 189 discovered/178 PASS/11 SKIP (Windows .cmd test)/0 FAIL; all four include full extracted-ZIP synthetic audit/SQLite/dashboard/recovery/self-check. Same 12-file ZIP SHA256 `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`, unsigned CI artifact `sovia-portable-beta` available. **PR integration DONE; DO NOT repeat.** On `ㄱ` next: verify latest develop HEAD and continue P2 product acceptance/privacy/retention/authorized n8n-like sanitized source or adversarial tests, prioritizing safe offline work. Actual owner's Windows PC, browser visuals, AV/SmartScreen, ReportLab+Korean TTF PDF visual, customer data and commercial/production are **NOT VERIFIED** and need owner/local evidence. `main` remains docs-only and unreleased. Earlier feature-only references are archived.


**2026-10-26 KST P2 owner-PC synthetic acceptance v0.10.0-beta:** Feature branch feature/p2-owner-selfcheck implements 12-file source ZIP with RUN_SELF_CHECK.cmd + owner_selfcheck.py, an offline versioned manifest verifier, automatic synthetic audit → SQLite → HTML dashboard → backup/restore, and explicit optional Korean PDF status. Tested source SHA cadc2baf8302f9583196fba7b6618c5c264d5a24, [CI 40218607947](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218607947) 4/4 SUCCESS: Windows Python 3.11/3.13 each 189 discovered, **179 PASS / 10 optional PDF SKIP / 0 FAIL**; Ubuntu 3.11/3.13 each 189 discovered, **178 PASS / 11 SKIP / 0 FAIL** (10 optional PDF + 1 Windows launcher only). Windows RUN_SELF_CHECK.cmd executed successfully in CI; clean-extracted ZIP owner_selfcheck status AUTOMATED_PASS_MANUAL_PENDING. Exactly reproducible inner ZIP SHA256 894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b on all four environments, 12 fixed files, uploaded CI artifact sovia-portable-beta (ID 12608344203). This is GitHub-hosted synthetic acceptance, NOT actual owner's PC, browser appearance/antivirus, PDF visual verification or real client consent; sale/production not authorized. Current docs+CLI-help follow-up commit to be reverified. NEXT: PR #16 integration to develop after green head, then privacy/retention/authorized source P2 gates. main docs-only.


## 1. Goal, user requirements and technical direction
Zero-cost offline-first deterministic agent action audit; P1 five evidence-linked rules, P2 CSV/optional PDF, SQLite digest-only history/static dashboard and portable ZIP. Owner authorizes incremental synthetic-only development, not live client data, production or paid listing.
## 2. Completed, reasons and decisions
Retain previous P1/v0.9 source behavior, with v0.10 owner_selfcheck.py and RUN_SELF_CHECK.cmd added to 12-file strict portable allowlist. The Windows command launches Python (fallback) in isolated -I -B mode without downloads. Self-check verifies a pristine manifest BEFORE audit subprocess; then synthetic 3 events/5 findings, SQLite import/idempotency/recovery and dashboard. Results stored in new sibling SOVIA_DIAGNOSTICS subfolder, with safe structured codes and no private paths/customer data. Optional ReportLab/OS Korean TTF inspected but never installed; PDF generated only if supported, clearly MANUAL_REVIEW. All browser/AV/privacy/manual items remain NOT_CHECKED. Portable version bumped to 0.10.0-beta, deterministic Windows CMD CRLF. ADR-013 documents user-run synthetic diagnostic over an installer/bypass.
## 3. Test commands and actual evidence
GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218607947 at code SHA cadc2baf8302f9583196fba7b6618c5c264d5a24: 4/4 SUCCESS, Windows 3.11/3.13 189 total 179 pass/10 skip, Ubuntu 3.11/3.13 189 total 178 pass/11 skip (the extra skip is real Windows .cmd test). All 0 fail. Real Windows cmd script test PASS, clean-extracted ZIP owner_selfcheck in isolated Python PASS, correct synthetic output/backup/restore, reproducible 12-file SHA 894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b verified all OS. Earlier run 40218266884 had one failing TEST ASSERTION expecting zero checks after tampered-manifest refusal; prerequisite python check had passed correctly. Test assertion corrected in commit cadc2baf..., green run 40218607947. No owner physical PC or real browser visual was tested.
## 4. Done/in progress/pending and stop
DONE v0.10 owner diagnostic synthetic CI and packaged beta as feature. PENDING PR review/merge, user owner Windows manual installation and Korean PDF/browser/Defender checks, consented n8n source, retention/backups, privacy, real risk accuracy and commercial release. No background tasks.
## 5. Failures/root causes/attempts
First CI assertion failure only: tampered source correctly failed closed after Python version prerequisite was logged PASS. Updated test expectation from {} to {python:PASS}, reran all four OS/Python green. No implementation defect or original data loss demonstrated. No attempts to bypass Windows code/signing defenses or to automatically install reportlab/fonts.
## 6. Repository refs, SHAs, paths
PUBLIC GitHub https://github.com/hibi89/SOVIA_sovereign; feature/p2-owner-selfcheck based on develop 0070339329684d880a0503aa7eb690ba642ebaed, last tested executable SHA cadc2baf8302f9583196fba7b6618c5c264d5a24, subsequent help correction 79b2837cdb432e5e3ab5cf8ea0c812c2778f33fd. Changes owner_selfcheck.py, RUN_SELF_CHECK.cmd, tests/test_owner_selfcheck.py, build_portable.py, verify_portable.py, portable_smoke.py, PORTABLE_README.md, OWNER_ACCEPTANCE.md, Actions workflow. Feature PR #16 opened. Default main docs-only, not release.
## 7. Production URL/Vercel and commands/environment
No production URL/Vercel/paid service/service ports. NOT_APPLICABLE production. User downloads CI beta artifact, independently verifies inner ZIP SHA, extracts new SOVIA folder and double clicks RUN_SELF_CHECK.cmd. Diagnostics go next to app under SOVIA_DIAGNOSTICS/SOVIA_SELF_CHECK_<unique>, with SELF_CHECK_RESULT.json and sample HTML/SQLite. Python 3.11+ and Windows cmd, optional local ReportLab and Korean OS TTF; docs in PORTABLE_README.md and OWNER_ACCEPTANCE.md.
## 8. Originals, backup and protected inputs
Only synthetic public examples in ZIP. No private customer logs/API token/standalone font/access modification. Manifest checksum proves byte integrity but not software publisher authenticity; unsigned distribution. No original DB overwrite, exclusive new output paths; manual private retention required for diagnostic folders (even synthetic) and future production records. Avoid public upload of local diagnostic files.
## 9. Next priorities and owner approvals
Verify latest PR #16 head CI, merge into develop if all green, confirm develop post-merge. Then prepare/execute **owner PC manual checklist** only if user chooses to run local beta, without claiming their actual desktop passed. Continue remaining P2 sanitized authorized n8n adapter, privacy/retention, adverse-input, false-positive, business support and optional font checks. Owner approval required for external data, repo visibility, paid listing, production deploy, main promotion.
## 10. Latest verification and limitations
2026-10-26 KST. 40218607947 all four passing, 12-file ZIP sha256 894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b. This docs commit cannot self-reference. GitHub-hosted Windows runner passed cmd; owner's PC/browser/AV/optional Korean PDF visual/sale compliance UNVERIFIED. No production.

---

## Prior handoff (archived, overridden by current above)

# SOVIA HANDOFF — portable v0.9 beta (10 mandatory sections)

**LATEST INTEGRATION (2026-10-26 KST):** [PR #15](https://github.com/hibi89/SOVIA_sovereign/pull/15) merged v0.9.0-beta deterministic portable ZIP/verifier/synthetic full smoke into `develop`, merge SHA `0a16a032dc26970ba197aa8e874a22fcb2a2c0a6`. [Post-merge Actions run 40217328939](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40217328939) **4/4 SUCCESS** (Windows+Ubuntu × Python 3.11/3.13), per job 177 discovered / 167 PASS / 10 optional PDF SKIP / 0 FAIL, and full clean-extracted isolated-Python audit→SQLite→dashboard→backup/restore PASS. Tested reproducible ZIP SHA256 `6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3`. `sovia-portable-beta` downloadable from Actions artifacts, unsigned ZIP+checksum, NOT an official signed Release. **On ㄱ**: inspect newest `develop`, then start P2 owner-Windows acceptance/self-check workflow (one-command local diagnostics; sample/fresh-folder tests), optional PDF/font/visual/manual verification guidance, then real authorized data/privacy/retention/failure-handling commercial gates. Do NOT redo JSON/CSV/SQLite/dashboard/package or merge PR #15 again. `main` remains docs-only; no Production/Vercel, no owner device/customer validation or sale approval. Earlier sections are archival.


**CURRENT P2 PORTABLE BETA CHECKPOINT (2026-10-26 KST):** The feature/p2-portable-package branch now builds an offline SOVIA Audit Lite 0.9.0-beta ZIP with an allowlisted 10-file source/synthetic payload, embedded manifest, detached checksum, strict verifier and new-directory-only extraction. Test SHA 7dffc94401e6843b9fa792edfd1a886e4757950b. [GitHub Actions result](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40216762276) finished **4/4 success**, Windows and Ubuntu × Python 3.11/3.13, each **177 discovered / 167 PASS / 10 optional-PDF SKIP / 0 FAIL**. Clean extracted portable ZIP passed real isolated Python audit (3 events/5 findings) → SQLite idempotency → offline HTML dashboard → SQLite backup/restore on all four jobs. Archive SHA256 **6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3** matched all four environments. The unsigned ZIP + detached checksum were uploaded as GitHub Actions artifact **sovia-portable-beta**, artifact ID 12607951989. NOT a signed installer, real customer use, user-PC validation or production. NEXT: green PR merge to develop, then owner Windows installation/browser/optional PDF testing and commercial privacy gates. Default main is docs only.

## 1. Goal and approved scope
Offline-first deterministic AI-agent event audit and optional SQLite history and static dashboard. MVP-first followed by blueprint gaps. Synthetic-only work permitted without external spending, production or customer log access.
## 2. Changes and decisions
Previously P1 JSON and five rules, P2 source CSV/CSV export, optional PDF, SQLite hash-only idempotent history/recovery, static Korean HTML history. NEW build_portable.py, verify_portable.py, portable_smoke.py, tests/test_portable.py, PORTABLE_README.md and CI workflow. Fixed 10-file public allowlist, stable ZIP metadata and normalized CRLF, manifest plus SHA256 file, path/duplicate/size/symlink rejection and no-clobber extraction. ADR-012 below compares ZIP to .exe installer; choose source ZIP first.
## 3. Actually executed tests and constraints
Code SHA 7dffc94401e6843b9fa792edfd1a886e4757950b. CI https://github.com/hibi89/SOVIA_sovereign/actions/runs/40216762276 all four OS/Python jobs SUCCESS. Per job unittest discover: 177 total, 167 passed, 10 skipped optional ReportLab/PDF, 0 failed. compileall PASS; python portable_smoke.py PASS under -I -B with ZIP verified, extracted into clean dir, audit/SQLite/dashboard/backup/restore. 29 new portable regression tests. Identical SHA256 on Windows and Ubuntu 3.11/3.13: 6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3. CI artifact ID 12607951989 confirmed from API. Owner PC/browser/font/AV/real customer unverified.
## 4. Done, pending, stopping point
DONE beta package generation, artifact, synthetic extraction and smoke tests on feature branch. PENDING reviewed PR to develop, clean owner Windows install, optional PDF font, customer privacy/retention and risk accuracy/security before sale. No production or Vercel.
## 5. Failures/root causes/attempts
No failed portable matrix in CI run 40216762276. Previous SQLite Windows readonly-fsync/file handle failures were fixed and retested in earlier milestones. Current documentation update is isolated from tested executable. SHA file beside ZIP is not a cryptographic publisher signature.
## 6. Repository/branches/SHA/files
PUBLIC repo https://github.com/hibi89/SOVIA_sovereign. Base develop b6e994038d7f9597a12752926910578b32bf748d. Active branch feature/p2-portable-package. Executable tested commit 7dffc94401e6843b9fa792edfd1a886e4757950b; this doc commit will follow. Default main is documentation-only. Build scripts and portable docs/tests in repository root.
## 7. Commands/environment/deployment
Windows Python 3.11+ (CI 3.11 and 3.13) / Linux Python 3.11+. Create unused dist directory then python build_portable.py --output dist/SOVIA-Audit-Lite-0.9.0-beta.zip; verify with python verify_portable.py --archive ZIP --sha256-file ZIP.sha256 --extract-to NEW_FOLDER, then use extracted sovia_audit.py, sovia_history.py, sovia_dashboard.py with synthetic examples. Full PowerShell examples in PORTABLE_README.md. No Vercel, Production URL, paid account, or deployment. Production check NOT_APPLICABLE.
## 8. Originals/privacy/backup/authentication
Only 10 explicitly named tracked public files; no real customer data, keys, raw logs, fonts or private examples. Original develop/main unchanged until verified integration. ZIP and checksum check integrity, NOT producer identity; no code signing. SQLite backups/reports under private output dir, not app install or public Git. Input sources remain unmodified.
## 9. Next work and approvals
Check PR and latest HEAD, merge only with green CI into develop, verify develop CI. Then prepare manual owner Windows install/browser/antivirus/font acceptance and retention/authorization policy, support boundaries, legal/commercial gates. Require owner approval for external data, visibility, production, release, billing or actual sale.
## 10. Updated time/evidence
2026-10-26 KST. Tested executable SHA 7dffc94401e6843b9fa792edfd1a886e4757950b and CI 40216762276 4/4 green; per job 167 pass/10 PDF skip. ZIP sha256 6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3. No actual owner Windows/customer/production proof. Confirm documentation commit SHA after writing.

---
## Historical handoff (superseded by above)

# SOVIA HANDOFF — P2 v0.8 offline dashboard, mandatory 10 sections

**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #14](https://github.com/hibi89/SOVIA_sovereign/pull/14) merged P2 v0.8 static offline SQLite history dashboard into `develop`, merge SHA `1123851900aee34d1c02d2a4590c6a0b5852727d`. [Post-merge CI run 40215946752](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215946752) completed **4/4 SUCCESS** on Windows/Ubuntu × Python 3.11/3.13; each 148 tests discovered / 138 PASS / 10 optional PDF SKIP / 0 FAIL. All P1 and v0.7 SQLite work remain integrated. **NEXT on ㄱ**: begin P2 portable offline package/fresh-install validation on a new branch from actual latest develop, with deterministic manifest/checksums/verification, sample CLI and user setup instructions. Do not redo the dashboard/SQLite/JSON work. `main` stays documentation-only, no Vercel/production or real customer-data evidence. Independent owner-machine browser visual QA remains UNVERIFIED.

2026-10-26 KST: P2 v0.8 feature/p2-offline-dashboard implements a read-only SQLite v1 to standalone Korean HTML dashboard; no local server, JS, outbound network, data write or output overwrite. Tested source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334 4/4 SUCCESS, Windows/Ubuntu x Python 3.11/3.13, each 148 discovered/138 PASS/10 optional PDF SKIP/0 FAIL. New tests 23. Not owner PC/browser visual QA, real customer records or production.

## 1. Goals/requirements/technology
Python standard-library-first local agent evidence/risk audit; 5 deterministic policy checks; opt-in history and report. User approved zero-cash MVP-first, then blueprint gaps, security before commercial sale. Future Cloud/Private share core, no live release yet.

## 2. Completed functionality and decisions
Existing five-rule JSON audit, guarded metadata CSV import/export, optional PDF (ReportLab+OS TTF), SQLite v1 metadata-only idempotent history/backups/restore/purge unchanged. NEW sovia_dashboard.py static HTML: 4 metrics, rule/severity aggregates and recent 100 report/finding/event rows from SQLite read-only snapshot, escaped/size-capped values, CSP disallowing scripts/network, zero remote assets, no-clobber output. ADR-011 chooses static HTML over local HTTP server to minimize setup/security/maintenance for MVP; live filtering deferred.

## 3. Actual tests, pass/fail, verified/unverified
GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334, code+workflow commit c8bcbc9d9191c0bd98da66750fae3b456258391f, Windows/Ubuntu Python 3.11/3.13 all four jobs SUCCESS. Command: python -m unittest discover -s tests -v. Each: 148 discovered, 138 PASS, 10 SKIP (optional PDF/ReportLab), 0 FAIL. Compileall -q sovia_audit.py sovia_csv_input.py sovia_pdf.py sovia_history.py sovia_dashboard.py tests PASS. 23 new tests verify DOM, synthetic counts, empty state, HTML injection escape, no script/network dependencies, identical DB before/after, bounded query result, no overwrite, symlink/source alias protection, isolated Python -I package and corrupt DB safe failure. Browser visual, owner Windows fonts, real data, power-loss and sale tests UNVERIFIED.

## 4. Completed/in progress/pending/stop
DONE safe synthetic read-only dashboard source+tests integrated into develop via PR #14, 4/4 post-merge CI green. NEXT portable clean-install packaging, owner-side browser UX check, retention/privacy, authorized sanitized n8n mapping and commercial tests. P2 overall remains incomplete. No Vercel/production.

## 5. Failed attempts, evidence, root causes and pivots
No failed dashboard CI run at code checkpoint. Earlier Windows SQLite snapshot fsync and test handle issues were fixed and verified (run 40214522381). Initial malformed documentation-tool draft did not reach GitHub (source unchanged); continue using a smaller docs write. No network server built. If screenshots/actual browser not supported, label appearance unverified instead of claiming a rendered QA pass.

## 6. GitHub/branches/SHAs/files
Repository https://github.com/hibi89/SOVIA_sovereign, PUBLIC. Feature feature/p2-offline-dashboard based on develop ff11358e7103816addecca898cf194d901e2ab97, tested code SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; docs SHA to be confirmed separately. Paths sovia_dashboard.py, tests/test_dashboard.py, DASHBOARD.md, updated workflow. Core source unchanged. main is documentation-only, deliberately not released.

## 7. Production URL, project, commands, environment
Production/Vercel: NONE, NOT_APPLICABLE. Windows PowerShell synthetic: py -3 sovia_history.py import --input examples/demo_five_rules.json --db sample-history.sqlite; then py -3 sovia_dashboard.py --db sample-history.sqlite --output sample-dashboard.html; open local HTML in browser. Python 3.11/3.13 Windows+Ubuntu CI success; no API token/network/paid services.

## 8. Originals, backup, protected data, credentials
Original develop/main preserved until reviewed PR. Test data synthetic only, no secrets/customer logs or fonts committed. History contains hashed identifiers/timestamps, not guaranteed anonymous; dashboard may expose linkable hash prefixes and timings. HTML is local and should not be placed in PUBLIC Git. Existing SQLite input never edited; output new filename only. Existing backups remain independent and retention/secure erasure not complete.

## 9. Next priorities, success and approvals
Check feature PR and CI, integrate into develop only after green reviewed. Next scoped P2 work: zero-cost clean-install ZIP/portable demo with manifest/checksums and owner Windows/browser validation; retention and real sanitized adapter later. Payments, external data, visibility, customer logs, Vercel and public sale require explicit owner approval; synthetic-only code/docs do not.

## 10. KST update / verification time/scope / basis
2026-10-26 KST, checked source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f and CI 40215480334. The current documentation commit cannot reference itself. No actual browser/production/customer compliance proof.

---

## Archived previous handoff
# SOVIA HANDOFF — P2 v0.7 SQLite metadata history (10 required items)

**LATEST INTEGRATION VERIFIED — 2026-10-26 KST:** PR [#13](https://github.com/hibi89/SOVIA_sovereign/pull/13) MERGED the opt-in SQLite history (version 1, recovery and purge) into `develop` at `edf8ea3de4a4fd781de34642b3d3f07a1ff67e10`. [Develop post-merge CI 40214911902](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214911902) 4/4 SUCCESS, Windows/Ubuntu × Python 3.11/3.13; each 125 tests discovered, 115 PASS, 10 optional PDF SKIP, 0 FAIL. Source/feature integration is DONE, NOT waiting for a PR. Next safe task on `ㄱ`: create a new scoped branch from latest `develop` and implement a read-only, generated offline HTML history dashboard (no local server/network) with output no-clobber, escaped metadata, report/rule/time overview, tests; then continue installer/retention/customer authorization gates. Do not reimplement P1/CSV/PDF/SQLite. Production/Vercel none; `main` remains documentation-only, not sale-ready. The earlier feature-branch notes below are archival.


Updated 2026-10-26 KST; tested P2 source integrated into develop via PR #13; main intentionally unpromoted. New chat/ㄱ: read the latest DEVELOP branch when integrated, otherwise this feature branch, then HANDOFF → STATUS → AGENTS → REQUIREMENTS → source and tests. Fresh SHA takes precedence over archival text.

## 1. Goal, confirmed needs and stack
Local-offline AI agent risk/evidence auditing with one deterministic Python core; staged Audit Lite then commercial hardening; Cloud/Private future conditional. User approves MVP first, incremental gap filling, no initial spending, no unapproved live data.

## 2. Completed functionality/changes/decision
Existing P1 five-rule JSON core/HTML/JSON and P2 strict CSV ingest/export and optional Korean PDF unchanged. NEW separate sovia_history.py v0.7 opt-in SQLite store with digest-only event identity/content, pseudonymized actor/run/tool, rule IDs, import time/counters; original prompt/target/destination/source pointer not persisted. Same report repeat no-op; same event identity with modified payload rejects transaction. SQLite version 1 schema, backup API to unused filename, restore to unused filename, report/all purge with explicit --confirm-delete + VACUUM. No automatic DB writes from normal sovia_audit.py CLI. ADR-010 compares JSONL vs SQLite; selected SQLite for transactional/idempotent recovery. HISTORY.md is user guide.

## 3. Test commands/pass-fail and scope
GitHub Actions CI run 40214522381 (source SHA 59b982bc8960e38a948c68e49d874457de3e01fa): python -m compileall -q sovia_audit.py sovia_csv_input.py sovia_pdf.py sovia_history.py tests PASS; python -m unittest discover -s tests -v **each OS/version 125 total, 115 PASS / 10 PDF SKIP / 0 FAIL**, Windows/Ubuntu × Python 3.11/3.13 4/4 success. 33 new SQLite tests; source-only and snapshot/restore/dedup/rollback/purge/isolation covered. CI evidence URL https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214522381. No real consumer desktop/real logs/power-loss stress or PDF optional dependency rerun.

## 4. Done/in progress/pending/stopping point
DONE verified synthetic P2 SQLite metadata local slice on develop, along with existing JSON/CSV and optional prior PDF. IN PROGRESS P2 overall commercial gates. PR #13 merged/validated into develop. NEXT: new feature branch with read-only offline history dashboard, clean installation, authorized n8n mapping feasibility, clear retention/deletion/PII false-positive test and actual owner PC testing. P2 not sale-ready. P4/P5 production NOT_STARTED.

## 5. Failures, evidence, cause, attempts/pivot
Initial Github run 40214395712 Linux PASS but Windows FAIL: sqlite backup fsync on read-only file was EBADF, and with sqlite3.connect context didn't close Windows temp handles. Scoped fix in commits 60d2d3faf6f6bd0f0ba2925ebcbcada46554e3e9 / 59b982bc8960e38a948c68e49d874457de3e01fa: writable fsync handle, close connections on config failure, contextlib.closing for test handles. Rerun 40214522381 all 4/4 PASS; no need to retry failed design.

## 6. Repo/branch/SHA/files
Repo https://github.com/hibi89/SOVIA_sovereign PUBLIC. Feature branch feature/p2-sqlite-history base develop cd154200821054b8596d2decf7dc2f55fc93e22e. Last fully tested source SHA 59b982bc8960e38a948c68e49d874457de3e01fa (before docs commit). Files sovia_history.py, tests/test_history.py, HISTORY.md, workflow .github/workflows/sovia-offline-regression.yml. Develop still previous stable P1/P2 through PR #12 until SQLite PR merged; main documentation-only, not production. Verify all actual heads freshly.

## 7. Production, Vercel, commands and environment
No Vercel, production URL, live service, subscription or external API. NOT_APPLICABLE Production verification/SHA. Python 3.11/3.13 Ubuntu & Windows CI. CLI examples in HISTORY.md: python sovia_history.py import --input examples/demo_five_rules.json --db new-history.sqlite; status, backup, restore, purge commands. No required third-party package for SQLite. Optional PDF requires ReportLab+local Korean TTF and was skipped in this CI.

## 8. Source/backup/secrets/protected data
Original main/develop source unchanged by feature until integration; commits and PR supply code rollback. No private/user/customer records touched; PUBLIC repository contains only synthetic fixtures. SQLite import is opt-in; metadata is pseudonymized NOT proven anonymous; SHA dictionary/linkage and timestamps can be sensitive. DB/backups & source files kept outside Git. Snapshot/restore is implemented with unique targets but automatic backup, lifetime/retention and physical secure erase remain missing. For any real existing DB, explicit backup+test restore before further imports. Never share fonts/tokens/.env/customer logs.

## 9. Next priority/steps/approvals
PR #13 integration is done and verified green at develop SHA edf8ea3de4a4fd781de34642b3d3f07a1ff67e10. Now implement first read-only local dashboard via standalone UI; add install+user-PC tests, historical browsing, retention, authorized sanitized source adapter, adversarial tests before selling. Owner approval needed for visibility change, money, external data, real customer input, production/Vercel, publication. No owner action required for synthetic-only next work.

## 10. Updated time/basis SHA/verification boundaries
2026-10-26 KST. Verified 59b982bc8960e38a948c68e49d874457de3e01fa and 40214522381 on GitHub. This documentation commit cannot self-reference. Source+CI, NOT production or user Windows. Documentation may be superseded by merged DEVELOP HEAD; check live ref.

---

## Historical handoff from before SQLite

# SOVIA HANDOFF — current P2 source CSV checkpoint (10 mandatory sections)

**CURRENT INTEGRATION (2026-10-26 KST):** PR [#12](https://github.com/hibi89/SOVIA_sovereign/pull/12) merged synthetic Audit Lite P1/P2 into `develop` at merge SHA `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26`. The previous no-code baseline on `main` is HISTORICAL and `main` is intentionally not promoted. Windows+Ubuntu Python 3.11/3.13 CI run [40213287272](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272): 4/4 success, 82 passed / 10 optional PDF skipped / 0 failed per job; PR validation [40213518280](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213518280) SUCCESS. Next unblocked work is P2 SQLite metadata-only history and recovery on a **new feature branch from develop**. Verify latest HEAD, then read HANDOFF/STATUS/GAP_MATRIX. No production or user Windows/real customer-data verification.


Last material update: 2026-10-26 KST. Exact restart trigger: [소비아소버린 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. This is approval to continue unblocked synthetic-only work on the existing branch; always verify fresh GitHub HEAD and branch ancestry.

## 1. Goal / approved requirements / technology
Shared offline-first Python deterministic agent event auditing core, evidence-linked policy findings, Korean reports. MVP-first followed by blueprint gap closure; zero cash/API costs for prototype. Cloud/Private are future market-gated variants sharing the same core, not current deployments. P2 must reach real installer/recovery/privacy/customer input gates before sale.

## 2. Completed functionality / changes / reasons
P1 local vertical slice: bounded JSON normalization, five risk rules (unauthorized tool, unapproved destination, sensitive target, burst, missing evidence), UTC timeline, evidence/unknown disclaimers, Korean HTML+JSON. P2 v0.4 CSV findings/events **export**; P2 v0.5 optional Korean PDF via locally installed ReportLab and Korean TTF; P2 v0.6 source CSV **import** via explicit `--input example.csv --policy policy.json` with strict header allowlist, max 1 MiB/1000 events, duplicate header/extra cell/type guards and raw-prompt-header rejection. CSV blank permission means unknown. The CSV+JSON policy feeds existing unchanged evaluate engine; original JSON path remains supported. No automatic external calls. GitHub Actions new stdlib Python 3.11/3.13 regression workflow on feature branch.

## 3. Tests actually run / evidence and unverified
- Prior standalone PDF checkpoint on developer Linux Python 3.13.5/ReportLab 4.4.9: 67/67, 1-page Korean and 6-page synthetic PDF render; extracted ZIP isolated PDF 67/67. This is **historical**, not repeated here.
- New CSV parser built and run locally in workspace with `python -m unittest discover -s tests -v`: 17 cases PASS, 0 FAIL; `python -m compileall -q sovia_csv_input.py tests` PASS. This was a separate parser-only sandbox, not the full repository.
- GitHub Actions run https://github.com/hibi89/SOVIA_sovereign/actions/runs/40212874275 at code/CI commit 5c99ca3ca1205a26b586a057874172f6607d3e19: Python 3.11 and 3.13 on Ubuntu each ran `python -m unittest discover -s tests -v` **92 total, 82 PASS, 10 SKIP, 0 FAIL** and Python compile PASS. Logs confirm CSV CLI, JSON-equivalence and isolated Python CSV tests PASS. The 10 skips are optional PDF dependency/font scenarios on runners; do not report them as passed.
- UNVERIFIED: user's own Windows installation and real Office/PDF font rendering, actual client/n8n logs, all optional PDF tests in the CI environment, real install/restore/delete, significant adversarial/fuzz test, power-loss multi-output transactions, live UI and production.

## 4. Done / in progress / pending / stop
DONE under synthetic offline scope: P1 JSON core and five rules; CSV export and source import; optional Linux-tested PDF; repeatable CI with two Python versions. IN PROGRESS P2 sellability closure; no running task outside this chat. NEXT: SQLite metadata-only history with idempotent import, immutable hashes, explicit delete, deterministic migration, local backup/restore tests; then local read-only dashboard and optional genuine sanctioned adapter. No completed live deployment, sale or production claim.

## 5. Failures / root causes / attempts / pivot
Old 2026-10-26 isolated PDF import failed due Python -I removing script directory from search path; corrected by explicit sibling module load and verified extracted ZIP 67 tests. CSV importer uses same fixed-path sibling import to avoid repeating this failure. New CSV module unit and GitHub Actions runs PASS. Local sandbox cannot directly clone GitHub because `github.com` DNS/network is unavailable there; instead matched source was committed using connected GitHub API and full repository tests actually executed via GitHub Actions. Do not confuse local parser subset with GitHub full regression. A first Windows test at CI run 40213209092 exposed an old path-collision error-message mismatch: a case-insensitive alias fell through to the no-clobber filesystem guard (original still preserved), causing 1 failed assertion. Fixed by comparing `Path.resolve()` canonical output targets in commit d204b76fdb545b32696a3d8aa97c35c1ffbb1355; run 40213287272 passed all four jobs. No remaining demonstrated test failure.

## 6. Repository / branches / code SHA / paths
Repo https://github.com/hibi89/SOVIA_sovereign, visibility PUBLIC. feature/p0-audit-core latest cross-platform tested code SHA `d204b76fdb545b32696a3d8aa97c35c1ffbb1355` (CSV feature commit `770172baa1dfe0eb0fd4b1a63d0afead0eaf6bc2`). Before this docs-only commit, main and develop both `51ebaf92cbb278a10978d906da927ec644c76d97`, still not promoted. Code: sovia_audit.py, sovia_csv_input.py, sovia_pdf.py; tests: tests/test_csv_input.py plus four prior suites; examples/demo_source.csv, examples/demo_policy.json, demo_five_rules.json; CI .github/workflows/sovia-offline-regression.yml. Resolve branch HEAD again after docs commit.

## 7. Production/Vercel URL / commands / environment
Vercel project NONE, Production URL NONE, release/billing/tenant auth NONE; deployment verification NOT_APPLICABLE. Python 3.10+ intended; CI tested Python 3.11/3.13 on Ubuntu AND Windows GitHub-hosted runners. Run: `python sovia_audit.py --input examples/demo_source.csv --policy examples/demo_policy.json --output report.html --json-output report.json`. JSON still `python sovia_audit.py --input examples/demo_five_rules.json --output report.html`. Outputs require unique unused file names. Windows PowerShell: replace python with py -3. Optional --pdf-output needs reportlab>=4,<5 and OS-installed Korean TTF.

## 8. Originals / backups / authentication and protection
Original main/develop untouched; feature branch commit ancestry is code rollback. The existing JSON fixtures and code remain intact; no real data or secrets imported. Public repository: synthetic fixtures only; no private policies, logs, standalone fonts, API tokens, customer samples, .env or privileged material. GitHub authenticated committer on the CSV and CI commits verified as hibi89 / godls5898@gmail.com via API. Filesystem/report output excludes input overwrites by check; no guarantee of power-loss atomicity. Before introducing SQLite persistent user data, implement snapshot/restore and no hidden prompt storage; never overwrite actual originals.

## 9. Next priority / acceptance / approvals
Continue GitHub issue #6 using least-risk standalone SQLite **metadata-only** store on feature/p0-audit-core with testable migrations, repeated import idempotency, event conflict handling, explicit purge, backup/restore and no raw prompts; preserve default stateless CLI behavior. Compare SQLite vs file-based append history for reliability/cost/maintenance and document ADR. Prioritize P2 UX, install, genuine authorized sanitized input, privacy and security tests before sale. Owner approval required for repository visibility, real customer data/external transmission, service deployment, billing and actual listing. No owner action required for safe synthetic work.

## 10. Time / verified scope / documentation basis
2026-10-26 KST. Verified feature/CI SHA `5c99ca3ca1205a26b586a057874172f6607d3e19`, workflow run 40212874275 (2 completed-success jobs; 92 total/10 skipped each). Four-matrix CI (Windows/Ubuntu, Python 3.11/3.13) at https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272 completed SUCCESS: each 92 tests discovered, 82 PASS / 10 optional-PDF SKIP / 0 FAIL, compile PASS. Windows GitHub-hosted smoke/NTFS paths covered; independent owner's PC and Korean PDF font not covered. This new documentation commit cannot self-reference; verify GitHub HEAD on subsequent turn. No production URL/API/browser claim.

---

## Archived previous handoff (PDF milestone; superseded by the 10 sections above)

# SOVIA HANDOFF — P2 optional PDF output (ten mandatory items)
Updated 2026-10-26 KST. Exact trigger [소비아소버린 깃헙 레포지토리 보고 작업이어가셈], shorthand ㄱ. Recheck live GitHub HEAD before acting.

## 1. Goal / use / confirmed needs / stack
Offline-first retrospective AI agent evidence/risk audit with a single shared Python core. User-approved MVP-first then gap-filling, commercial/privacy tests before real customer data, cost target 0 KRW. Future Cloud/Private conditional on demand. Current P2 phase: verified CSV exports and optional automatic Korean PDF.

## 2. Completed / changes / decisions
P1 five deterministic rules and evidence-linked HTML/JSON; P2 CSV findings/events exports, safe quoting/formula-like cells; now v0.5 PDF in `sovia_pdf.py` with optional ReportLab 4.x and locally installed Korean TTF. HTML/JSON/CSV remain stdlib-only, no remote API. PDF includes findings, risk rating, event timeline, source pointer status, caveats and pages. PDF output is staged bytes by safe writer, rejects existing files. ADR-008 compares browser print vs optional ReportLab; automatic ReportLab selected due predictable CLI while manual HTML print stays possible.

## 3. Test commands / pass fail / verified-unverified
2026-10-26 KST, local Python 3.13.5 / ReportLab 4.4.9:
- `python -m unittest discover -s tests -q` = 66 PASS 0 FAIL (54 existing + 13 PDF cases).
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

## Isolated-Python PDF hotfix — 2026-10-26 KST
- During extracted ZIP independent smoke, `python -I -B sovia_audit.py ... --pdf-output ...` initially failed because isolated Python excludes the script directory from sys.path. Existing normal-mode PDF and prior 66 tests worked; this exposed an untested packaging path, not a runtime production incident.
- Fixed optional module loading to import ONLY the adjacent `sovia_pdf.py` via `importlib.util.spec_from_file_location`, without network or global sys.path mutation. Added isolated-PDF regression; final developer run `python -m unittest discover -s tests -q`: **67 PASS / 0 FAIL**, syntax PASS, isolated `-I -B` output PASS.
- Verified from extracted ZIP `SOVIA_Audit_Lite_P2_PDF_verified.zip`: 67 tests PASS, HTML+JSON+PDF CLI smoke PASS (3 events / 5 findings). ZIP SHA-256 `2fdc573567edd691a3c19280b24ca4932ea5d0092a6ab327ee1da394375639ff`. No standalone font files in ZIP.
- Final tested code hotfix GitHub SHA `a7a1c6b8e1518887c357aa101c8d254b228c4270`. P2 incomplete: Windows/NTFS and user-side ReportLab/Malgun Gothic, genuine sanctioned input and commercial safety remain UNVERIFIED. Deployment NONE.
