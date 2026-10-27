## P2 current — 2026-10-27 metadata preflight

PR #20 merged into develop at be1562c520be62d0e5341abe72a48a527b490987. Added bounded offline metadata-pattern rejection to approved-local mode only; synthetic mode and v0.10 portable ZIP are unchanged. New files: sovia_pii_preflight.py, tests/test_pii_preflight.py (29 synthetic cases), PII_PREFLIGHT.md. PR-head CI https://github.com/hibi89/SOVIA_sovereign/actions/runs/40459232377 passed Windows/Ubuntu with Python 3.11/3.13, 4/4 success; each 274 discovered, Windows 264 pass/10 skip, Ubuntu 263 pass/11 skip, zero fails. Existing portable smoke passed. This is heuristic scanning, NOT comprehensive privacy assurance, actual customer authorization, production release or real n8n integration. Remaining: consent verification, authorized source mapping, retention deletion governance, false-positive review, owner PC/AV/PDF acceptance. Post-document HEAD CI unverified. main remains documentation-only.

---

## CURRENT P2 — operator-review integrity gate integrated (2026-10-27 KST)

PR [#19](https://github.com/hibi89/SOVIA_sovereign/pull/19) MERGED into `develop` at `0a2a8cd7eeb78c2e8b5cf7e387ab2d50d6e34509`. Existing strict pre-sanitized n8n-like metadata adapter now offers optional `approved-local` pathway that requires an operator-supplied exact schema, three boolean review assertions, source/policy canonical SHA-256 digests, and bounded UTC expiry ≤30 days; default synthetic behavior preserved. SHA binds already-parsed JSON, not publisher identity. No-clobber, withheld output on failed checks; errors redacted. [PR CI #40458082863](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40458082863) 4/4 SUCCESS Windows/Ubuntu × Python 3.11/3.13, each 245 discovered (Windows 235 PASS/10 SKIP; Ubuntu 234 PASS/11 SKIP), 0 FAIL; extracted portable smoke unchanged/PASS. New tests: 25. This closes **only format/assertion and tamper-binding subgap**, not verified customer authorization or legal approval; attestation may be self-forged. Still open: actual n8n version/raw export mapping and consent, upstream real PII sanitization, retention/legal hold/deletion, owner Windows/AV/browser/PDF, signed build/portable inclusion, commercial pilot. `main` and existing 12-file ZIP unchanged, production NONE. Documentation-only post-merge HEAD CI not yet independently verified. Source [N8N_APPROVAL_GATE.md](N8N_APPROVAL_GATE.md).

---

## CURRENT P2 n8n sanitized-contract checkpoint — 2026-10-27 KST
[PR #18](https://github.com/hibi89/SOVIA_sovereign/pull/18) **MERGED** the synthetic-only strict metadata contract adapter at `db44dccb81f5d867de47df2797451b69de86d260` on `develop`. It adds `sovia_n8n_sanitized.py`, 20 new tests, the synthetic `examples/demo_n8n_sanitized.json`, and `N8N_SANITIZED.md`. Source n8n execution dumps (raw `data`, `resultData`, `json`, credentials/parameters/prompt) are deliberately **REJECTED**, not sanitized. No API connection; explicit pre-sanitized contract only, canonical SOVIA JSON output, no-clobber, evidence permission not inferred. [PR CI 40456761731](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40456761731) **4/4 SUCCESS** Windows/Ubuntu × Python 3.11/3.13, 220 discovered per job, Windows 210 PASS/10 SKIP and Ubuntu 209 PASS/11 SKIP, 0 FAIL, existing portable smoke PASS. **Actual n8n compatibility, customer consent/PII, retention disposal, owner-PC/visual PDF, signed release and commercial readiness remain OPEN**. New module is NOT in old v0.10 ZIP. Post-merge/docs HEAD CI not verified yet.

---

## CURRENT P2 GAP — 2026-10-27 (integrated, not commercial)
PR [#17](https://github.com/hibi89/SOVIA_sovereign/pull/17) merged the read-only local retention inventory into `develop` at `c462f480eb2fee35e5830ceb807c9cf2396f31d4`. PR head [CI 40454869234](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40454869234) **4/4 PASS** (Ubuntu/Windows × Python 3.11/3.13); each job ran 200 tests, 0 failed; 10/11 optional/platform tests skipped respectively, and the pre-existing 12-file portable smoke passed unchanged. This closes ONLY the *development-only, read-only inventory* subgap. Explicit deletion/retention enforcement, inventory coverage proof, authorized sanitized n8n source, owner Windows acceptance, actual customers and commercial security gates all remain **OPEN**. Post-merge push CI is not independently verified yet. See RETENTION.md. Prior feature-only checkpoint below is archived.

---

## P2 retention inventory checkpoint — 2026-10-27 KST (feature only)
Read-only `sovia_retention.py` inventory and `RETENTION.md` design drafted and locally tested: **11 PASS / 0 FAIL** (synthetic temporary files, Python compileall pass). Safe output is aggregated only, no file names/paths/content, no network/read of contents/deletion; bounded recursion and symlink avoidance. GitHub blob hashes of code/tests/docs matched local tested snapshots. This work is **FEATURE-ONLY, NOT PACKAGED IN v0.10 ZIP**, and full repository GitHub Actions CI is pending. Privacy/PII, consented n8n inputs, definitive retention policy, backup lineage, customer machine and sale acceptance remain OPEN. See `RETENTION.md`. Never mark automated deletion, real retention enforcement or customer clearance complete.

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

## P2 v0.9 portable beta snapshot
**CURRENT P2 PORTABLE BETA CHECKPOINT (2026-10-26 KST):** The feature/p2-portable-package branch now builds an offline SOVIA Audit Lite 0.9.0-beta ZIP with an allowlisted 10-file source/synthetic payload, embedded manifest, detached checksum, strict verifier and new-directory-only extraction. Test SHA 7dffc94401e6843b9fa792edfd1a886e4757950b. [GitHub Actions result](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40216762276) finished **4/4 success**, Windows and Ubuntu × Python 3.11/3.13, each **177 discovered / 167 PASS / 10 optional-PDF SKIP / 0 FAIL**. Clean extracted portable ZIP passed real isolated Python audit (3 events/5 findings) → SQLite idempotency → offline HTML dashboard → SQLite backup/restore on all four jobs. Archive SHA256 **6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3** matched all four environments. The unsigned ZIP + detached checksum were uploaded as GitHub Actions artifact **sovia-portable-beta**, artifact ID 12607951989. NOT a signed installer, real customer use, user-PC validation or production. NEXT: green PR merge to develop, then owner Windows installation/browser/optional PDF testing and commercial privacy gates. Default main is docs only.
Portable offline Python ZIP and Windows+Ubuntu extracted synthetic run DONE_VERIFIED in CI; signed installer, user PC/AV/optional PDF font, real sanitized n8n adapter, backup policy, retention, false positive and commercial approval PENDING. The default audit remains stateless and the dashboard stays local static HTML.

## P2 owner-PC readiness v0.10 checkpoint
**2026-10-26 KST P2 owner-PC synthetic acceptance v0.10.0-beta:** Feature branch feature/p2-owner-selfcheck implements 12-file source ZIP with RUN_SELF_CHECK.cmd + owner_selfcheck.py, an offline versioned manifest verifier, automatic synthetic audit → SQLite → HTML dashboard → backup/restore, and explicit optional Korean PDF status. Tested source SHA cadc2baf8302f9583196fba7b6618c5c264d5a24, [CI 40218607947](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218607947) 4/4 SUCCESS: Windows Python 3.11/3.13 each 189 discovered, **179 PASS / 10 optional PDF SKIP / 0 FAIL**; Ubuntu 3.11/3.13 each 189 discovered, **178 PASS / 11 SKIP / 0 FAIL** (10 optional PDF + 1 Windows launcher only). Windows RUN_SELF_CHECK.cmd executed successfully in CI; clean-extracted ZIP owner_selfcheck status AUTOMATED_PASS_MANUAL_PENDING. Exactly reproducible inner ZIP SHA256 894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b on all four environments, 12 fixed files, uploaded CI artifact sovia-portable-beta (ID 12608344203). This is GitHub-hosted synthetic acceptance, NOT actual owner's PC, browser appearance/antivirus, PDF visual verification or real client consent; sale/production not authorized. Current docs+CLI-help follow-up commit to be reverified. NEXT: PR #16 integration to develop after green head, then privacy/retention/authorized source P2 gates. main docs-only.

Automated Windows CMD synthetic self-check and code/ZIP integrity DONE_VERIFIED in CI. Actual owner PC/browser PDF readability, AV and SmartScreen, signed release and real customer data/privacy/retention certification PENDING. A structured result with `AUTOMATED_PASS_MANUAL_PENDING` is not a commercial acceptance.
