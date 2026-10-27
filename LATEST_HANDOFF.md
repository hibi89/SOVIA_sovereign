# DRAFT PR #42 — v0.11.2-source print readability, awaiting CI/review (2026-10-27 KST)

- Branch `feature/p2-html-print-legibility` based on verified `develop` SHA `e5d91766782f618e052a0b83afb6730f1757a98e`. [Draft PR #42](https://github.com/hibi89/SOVIA_sovereign/pull/42); source/test branch SHA initially `8938eb5080afd563128b4d0fe766a85813afb4fe`. **NOT MERGED, NOT RELEASED.** The verified original `develop` and v0.11.2 portable ZIP are unchanged.
- Original HTML A4 print rendering via WeasyPrint compressed Korean strings into extremely narrow 6/9-column cells. Design A: landscape CSS only (smaller but still cramped). Chosen B: keep regular on-screen tables and original data/evidence; add horizontal scrolling only for narrow screens and `@media print` stacked rows with trusted static `data-label` in printed cards. No event evaluation/JSON/CSV/SQLite/PDF code changes.
- Local Linux Python 3.13.5 synthetic oracle unchanged: 3 events, 5 findings, both table cell datasets equal before/after, HTML escaping for injected HTML retained, no-finding fallback retained. New `tests/test_html_print.py`: 5 stdlib regressions. WeasyPrint 3-page A4 synthetic rendering visually readable. WeasyPrint is a static renderer, **not an actual browser/Windows acceptance**. Chromium headless retry with improved flags timed out (exit 124); STOP retrying this environment without a different viable method. Do not claim a product defect from container browser startup failure.
- GitHub Actions feature PR CI run [40491371943](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40491371943) started, outcome pending as this note was prepared. Verify latest SHA/4 matrix jobs prior to accepting. Changes are isolated as DRAFT to require owner review/approval before merge.
- Original owner Windows/Defender/browser/PDF and authorized n8n version/source, PII false negatives, legal consent, signing, retention and commercial approval remain **NOT_CHECKED**. No user data, payments, production or Vercel. NEXT: verify CI result, fix only proven regression; seek owner approval to merge, then continue actual Windows manual acceptance.

---

## INDEPENDENT PACKAGE ACCEPTANCE — 2026-10-27 KST (model Linux container; owner Windows remains NOT_CHECKED)

- Source of evidence: GitHub Actions **develop** run [40487176510](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40487176510), exact tested SHA `2125cc66b6ac57e38e196be0f0aff425903afbad`, four CI jobs SUCCESS. Retrieved artifact `sovia-portable-p2-beta` ID **12724979578** (14-day retention; expires 2026-11-10 KST), extracted **inner** `SOVIA-Audit-Lite-0.11.2-beta.zip` checksum `5667be53c206af5b8e4c0c96239595988b7866a655587d73d6a18a8078a8a71e`, matching pinned handoff checksum and bundled detached SHA256. Do not confuse hash of GitHub's outer artifact with inner ZIP.
- Independently verified the actual downloaded inner 18-file payload + manifest on the assistant Linux/Python **3.13.5** container; `verify_portable_p2.py --archive ... --sha256-file ... --extract-to fresh-install` then `--directory fresh-install` both SUCCESS. Ran `python -I -B fresh-install/owner_p2_selfcheck.py --output-dir fresh-output` (output outside install): `AUTOMATED_PASS_MANUAL_PENDING`, 3 fabricated events / 5 findings / 1 report; package_integrity/python/audit/direct_sanitized/direct_metadata_pattern_scan/aggregate_no_report/sqlite/dashboard/recovery all **PASS**. No local customer data used.
- Synthetic privacy negative: injected fabricated `ghp_`-shaped token in pre-sanitized step ID, called direct `--synthetic-only` CLI; exit **2**, generic `CONTRACT_OR_REVIEW_REJECTED`, **no HTML/JSON output and no token echoed**.
- Optional PDF: generated **one A4 page** within independent Linux selfcheck; independently rasterized/inspected with readable Korean headings, table and timeline and extracted Korean text. This is **Linux synthetic-only visual evidence**; PDF status inside untouched selfcheck JSON is `GENERATED_NEEDS_VISUAL_REVIEW`. Owner Windows-installed fonts/PDF remains **NOT_CHECKED**.
- HTML/browser physical visual, Windows Defender/SmartScreen and native n8n authorized real-version/source tests are **NOT_CHECKED**. A Linux Chromium screenshot attempt timed out: browser QA is **UNVERIFIED**, not a product failure. Real upstream PII redaction, false negatives, source authorization, legal/retention and commercial sign-off remain **OPEN**. No code was changed, no user PC was remotely accessed, no paid/production/release action.
- NEXT: **owner physical Windows**: download the exact latest successful `sovia-portable-p2-beta` artifact, verify **inner** SHA above using `Get-FileHash`, fresh local non-synced directory, run extracted `RUN_P2_SELF_CHECK.cmd`, manually inspect Korean HTML/dashboard, optional PDF and Windows Defender without disabling controls. Record `SELF_CHECK_RESULT.json` and manual verdict as operator evidence only. If owner unavailable, do not produce more redundant synthetic wrappers or claim sale readiness.

---

# LATEST SOVIA HANDOFF — 2026-10-27 PR #41 v0.11.2-beta privacy-gate fix (10 sections)

## 1. Owner goal and current phase
Owner approved workflow: functional MVP → reconcile R1–R9 original blueprint → harden security/stability/compatibility for deliverable. P1 MVP and P2 pre-sanitized offline workflow plus separate portable beta are synthetically verified. Not customer-ready until real evidence.

## 2. Concrete delivered change
[PR #41](https://github.com/hibi89/SOVIA_sovereign/pull/41) merged at `e5754eb08d98339d93dd14fdb604832298bf9fc7`. **Confirmed direct-audit mode loophole**: prior `sovia_n8n_direct_audit.py` ran PII/credential pattern screening only in `approved-local`; choosing `--synthetic-only` skipped it. Now both modes always run the existing bounded `sovia_pii_preflight.assert_no_high_risk_patterns(document, policy_doc)` BEFORE report render/publish. Approved-local additionally requires the previous unsigned review-claim attestation; a synthetic flag still does not prove data provenance. Output `pii_pattern_scan_executed=true` in both modes, `pii_absence_proven=false`, `source_authorization_independently_verified=false`. Source and policy token-like patterns rejected with no raw-content/path disclosure. Bundled owner P2 selfcheck now asserts the above flags, otherwise fails. No broad claim about the separate canonical base auditor or synthetic converter, which are not automatically covered.

## 3. Exact tests / reproducer
[GitHub Actions PR run 40486828662](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40486828662) feature head `e5f58509e475e4f1e17e7c180428d684a49a4598`: Windows/Ubuntu × Python 3.11/3.13 **4/4 SUCCESS**, **750 tests discovered/job**, zero failed (Windows 740 pass/10 skip, Ubuntu 739 pass/11 skip). Four new `tests/test_n8n_direct_audit.py` regressions: clean mode scan confirmed, synthetic Luhn-like ID rejected, fabricated secret-like policy rejected, isolated CLI generic rejection with no value/path echo. Packaged `tests/test_portable_p2.py` additionally verifies `checks.direct_metadata_pattern_scan=PASS` from extracted v0.11.2 ZIP owner selfcheck. Legacy v0.10 smoke and new v0.11.2 extracted-package smoke PASS. New **v0.11.2-beta inner ZIP SHA256 `5667be53c206af5b8e4c0c96239595988b7866a655587d73d6a18a8078a8a71e`**; legacy **v0.10 ZIP SHA256 `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`** remains unchanged. Historic v0.11.1 inner ZIP `a31073a4fec63916ffa0b5f18fcb577bccaad7fc453bc644df939c3ab8aabf27`. CI uploaded separate `sovia-portable-p2-beta` artifact, UNSIGNED and not a release.

## 4. DONE and unresolved
DONE loophole prevention in direct offline pre-sanitized mode, owner selfcheck assertion, extracted packaging, four-platform regression, versioned v0.11.2 beta. UNVERIFIED: actual owner's Windows/browser/Defender/SmartScreen/Korean PDF manual acceptance, lawful approved genuine native n8n source/version and upstream PII false-negative evaluation, customer contract quotas/retention/support and commercial signing/release. No production or buyer evidence.

## 5. Limitation and adverse case
Metadata PII/credential detection is pattern-based, can produce false positives and misses unseen patterns. `--synthetic-only` remains a user assertion, not a proof of fabricated source. Separate legacy `sovia_audit.py` and `sovia_n8n_sanitized.convert_paths` synthetic path do not universally enforce the new direct-audit mode gate. Never claim end-to-end data protection, zero leak, native n8n compatibility, legal consent or SOC certification.

## 6. Repo, branches, SHA and changed files
PUBLIC `hibi89/SOVIA_sovereign` authoritative code `develop`, `main` docs-only. PR #41 merged `e5754eb08d98339d93dd14fdb604832298bf9fc7`, tested head `e5f58509e475e4f1e17e7c180428d684a49a4598`. Paths: `sovia_n8n_direct_audit.py`, `sovia_pii_preflight.py` docstring, `owner_p2_selfcheck.py`, `tests/test_n8n_direct_audit.py`, `tests/test_portable_p2.py`, `build_portable_p2.py`, `verify_portable_p2.py`, `P2_PORTABLE_README.md`, `N8N_DIRECT_AUDIT.md`, `P2_PORTABLE_SECURITY_0112.md` and CI. Post-doc commit will advance HEAD; verify current state on continuation.

## 7. Runtime, artifacts, costs
Source-only demo from verified extracted candidate: `python -I -B sovia_n8n_direct_audit.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --html-output NEW_REPORT.html --json-output NEW_REPORT.json --synthetic-only --local-test-budget-bytes 1048576` (write report OUTSIDE install). `RUN_P2_SELF_CHECK.cmd` uses only synthetic packaged data and writes outside install. P2 `SOVIA-Audit-Lite-0.11.2-beta.zip` via GitHub Actions `sovia-portable-p2-beta` (14-day artifact retention). No chargeable API, real customer log, Vercel or Production URL, digital signature or public commercial listing.

## 8. Original data and access
No customer records, secrets, fonts, local device path/screenshots or private inputs were used. Old v0.10 and previous v0.11.1 package provenance preserved by previous GitHub commit/CI run. No force push, branch access/security changes, deletion or deployment.

## 9. NEXT `ㄱ` order and actual blocker
**Physical owner Windows synthetic acceptance is next**. Select v0.11.2 package artifact from successful final `develop` Actions run, verify inner SHA256 against `5667be53c206af5b8e4c0c96239595988b7866a655587d73d6a18a8078a8a71e`, extract into a fresh non-synced folder and run `RUN_P2_SELF_CHECK.cmd`. Manually view Korean HTML/dashboard, any optional PDF, and note Defender/SmartScreen without disabling security. Report `SELF_CHECK_RESULT.json` outcome only if user chooses; avoid source/customer secrets. Real native n8n API/consent blocked without explicitly approved version/source. If user declines device check, offer a precise owner manual command/checklist rather than claiming completed; avoid new redundant helper scripts and avoid repeatedly rebuilding feature MVP.

## 10. Cutoff KST
2026-10-27. Latest completed tested feature PR #41: [Actions 40486828662](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40486828662), 4/4 success, 750 tests/job. Post-document HEAD CI must be confirmed after docs update. No owner hardware, customer consent, production or signed release verification.

---

# LATEST SOVIA HANDOFF — 2026-10-27 P2 v0.11.1-beta safety patch (10 sections)

## 1. Goal
P1 MVP done synthetically. Follow initial blueprint gaps, then security/stability/compatibility and owner real-world acceptance. No sale or production authority.

## 2. Changes
[PR #40](https://github.com/hibi89/SOVIA_sovereign/pull/40) merged `92297cb1bc0b62bba0df5d14d3cdc485415924b9` on `develop`. In `verify_portable_p2.extract_verified`, ZIP bytes are now SNAPSHOTTED after verify, hash-matched against the verified archive digest and extracted from `io.BytesIO` (prevents locally substituted ZIP between validation and extraction). `owner_p2_selfcheck.check` now verifies pristine installation before ANY result directory creation and rejects output resolving within the installation. All default core/report functionality retained. Modified candidate bumped from v0.11.0-beta to separate v0.11.1-beta filename, manifest, selfcheck and CI paths; historical older artifacts not overwritten.

## 3. Verification
[CI 40485607132](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40485607132) PR #40 feature SHA `5c646953f2b88d0179da977cad2af4bf27bb644b`: **4/4 SUCCESS** Windows/Ubuntu × Python 3.11/3.13, **746 tests/job; 0 FAIL**; four new regressions for swapped archive, tampered installed source with zero diagnostics, inside-install diagnostic refusal, normal sibling results. New v0.11.1-beta ZIP SHA256 `a31073a4fec63916ffa0b5f18fcb577bccaad7fc453bc644df939c3ab8aabf27`. v0.10 ZIP unchanged SHA256 `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`. Prior v0.11.0-beta historic SHA `a15ce8bebcb894c991fcb6e2b4fdc793e6460c31fb5067b97f73acf820cd1d70`. v0.11.1 is an unsigned CI artifact `sovia-portable-p2-beta`, NOT released to customers. Recheck post-doc HEAD CI.

## 4. DONE vs pending
DONE source extraction snapshot, owner selfcheck no contamination, source and extracted-portable CI smoke. PENDING genuine owner hardware Windows/browser/Defender/SmartScreen/Korean PDF, independently permitted real n8n version/source mapping and PII assessment, signing and paid support/privacy/retention contract.

## 5. Risks and limits
TOCTOU is narrowed by pinning in-memory extraction bytes, but local trusted verifier source, authentic publisher signature and crash-atomic filesystem guarantees are not supplied. CI hosted Windows differs from owner's actual machine. No claim of legal consent, customer quota, n8n native API, 24/7 SOC, zero PII leakage or commercial security certification.

## 6. Repo identity
PUBLIC `hibi89/SOVIA_sovereign`, source `develop`, default `main` docs-only. Key changed `verify_portable_p2.py`, `owner_p2_selfcheck.py`, `build_portable_p2.py`, `P2_PORTABLE_README.md`, `tests/test_portable_p2.py`, CI, and `P2_PORTABLE_SECURITY_0111.md`. No force push, secrets, visibility or access changes.

## 7. Commands / runtime
From trusted source: `python -m unittest discover -s tests -v`, `python portable_smoke_p2.py`. To build, first create `dist`, then `python -I -B build_portable_p2.py --output dist/SOVIA-Audit-Lite-0.11.1-beta.zip`. Verify separately and extract to a new folder with `verify_portable_p2.py`. P2 self-check results MUST be outside installation. No Vercel, Production URL, paid dependencies or customer data.

## 8. Original inputs / backups
No customer or local owner source files, credentials, PDF fonts, screenshots or real logs handled. Existing historical v0.10 and v0.11.0 source provenance available by previous commits; avoid silently replacing historical ZIPs. Synthetic-only workspace artifacts used.

## 9. NEXT `ㄱ`
**STOP new wrapper tooling**. Owner must run v0.11.1 extracted `RUN_P2_SELF_CHECK.cmd` on actual Windows and confirm browser report/optional Korean PDF/Defender (manual gates remain NOT_CHECKED) before real release. If physical access unavailable, prioritize actual product bug discovered in user acceptance or verifiable integration specs, not more synthetic breadth. Native n8n/API and customer consent/privacy remain blocked on owner-approved real source/version. Commercial release requires explicit approval. Do not duplicate PRs #16–#40.

## 10. Cutoff
2026-10-27 KST. [PR #40](https://github.com/hibi89/SOVIA_sovereign/pull/40) merged `92297cb1bc0b62bba0df5d14d3cdc485415924b9`; PR CI 40485607132 4/4 SUCCESS. Final docs commit & CI check separately.

---

# CURRENT SOVIA HANDOFF — 2026-10-27 v0.11.0-beta packaged P2 candidate (10 sections)

## 1. Goal / stack
MVP → original blueprint gaps → security/stability/compatibility before commercial use. P1 offline 5-rule engine already synthetically verified. Python 3.11+ stdlib, optional PDF ReportLab + local font.

## 2. Delivered
[PR #39](https://github.com/hibi89/SOVIA_sovereign/pull/39) MERGED: separately versioned `SOVIA-Audit-Lite-0.11.0-beta.zip` with strict 18-file allowlist, independent `build_portable_p2.py`, `verify_portable_p2.py`, `owner_p2_selfcheck.py`, `RUN_P2_SELF_CHECK.cmd`, `P2_PORTABLE_README.md`, and `portable_smoke_p2.py`. Package contains original audit/CSV/PDF(optional)/history/dashboard plus pre-sanitized direct n8n-like metadata audit, PII pattern scanner, optional guarded output and no-report aggregate diagnosis. v0.10 remains separate and unchanged.

## 3. CI and artifact identity
[PR CI 40484567239](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40484567239) on `15f221364f44e3cf8f2602a913e7785bb2a3552a` Windows+Ubuntu × Python 3.11/3.13 **4/4 SUCCESS**, **742 tests/job, 0 failures**. Windows 732 PASS/10 optional PDF SKIP; Ubuntu 731 PASS/11 SKIP. Both P2 extracted-package smoke + legacy v0.10 portable smoke PASS. v0.11 ZIP SHA256 `a15ce8bebcb894c991fcb6e2b4fdc793e6460c31fb5067b97f73acf820cd1d70` identical across tested OS; v0.10 SHA256 unchanged `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`. Separate **`sovia-portable-p2-beta` CI artifact** (14-day retention) uploaded on Ubuntu 3.11; not a signed Release.

## 4. DONE / PENDING
DONE new v0.11 isolated build+verification+extraction+owner test, 10 P2 suite regressions including tamper, version separation, old ZIP immutability, no-clobber, isolated source-only direct and aggregate CLI, synthetic owner selfcheck. PENDING owner actual Windows/browsers/Defender/SmartScreen/Korean PDF visual, real authorized native n8n version/source/consent/PII false negatives, verified support/retention/quotas, signing and commercial release.

## 5. Failure notes / boundaries
No full CI failures at tested PR head. 18-file P2 package is unsigned and not a standalone executable installer. ZIP SHA256 is NOT publisher authenticity. Verifier checks fixed allowlist/hash and refuses unknown paths, but output logs must live outside pristine extracted directory. Existing per-file 1/2/4 MiB output test cap is not an approved customer SLA; disk capacity snapshot and multi-output writes are not crash-atomic. No real n8n raw export/API.

## 6. GitHub refs
PUBLIC `hibi89/SOVIA_sovereign`, authoritative code `develop`; default `main` docs-only. [PR #39](https://github.com/hibi89/SOVIA_sovereign/pull/39) merged `f677c337c9884d8d008c7d79edc190d5562ebe42`, tested feature HEAD `15f221364f44e3cf8f2602a913e7785bb2a3552a`. Latest docs commit will advance HEAD; refresh live before editing. Old PRs #16–#39 complete; no duplicate work.

## 7. Commands / cost / production
From checkout create `dist` folder then `python -I -B build_portable_p2.py --output dist/SOVIA-Audit-Lite-0.11.0-beta.zip`. `python -I -B verify_portable_p2.py --archive dist/SOVIA-Audit-Lite-0.11.0-beta.zip --sha256-file dist/SOVIA-Audit-Lite-0.11.0-beta.zip.sha256 --extract-to NEW-FOLDER`. Extracted under `NEW-FOLDER/SOVIA-P2`, invoke `RUN_P2_SELF_CHECK.cmd` on owner Windows or `python -I -B owner_p2_selfcheck.py --output-dir ../SOVIA_P2_DIAGNOSTICS`. No API, paid hosting, Vercel/Production URL, commercial listing or signed release.

## 8. Originals, secrets, access, preservation
No private customer logs, real data, credentials, fonts, device paths or secrets committed. No forced push, main rewrite, existing v0.10 artifact modification, GitHub visibility/access change, destructive file history, paid deployment or production. Public repo remains PUBLIC. Synthesized sample outputs outside app install, owner source/backup untouched.

## 9. NEXT ㄱ priority
Stop building wrappers. Take the **owner manual acceptance package** from v0.11: physical Windows selfcheck and offline browser/Korean PDF/Defender audit still NOT_CHECKED. Without owner access, precise handoff of steps and verification rubric rather than pretending CI runner = physical PC. Genuine n8n API/schema+consent requires permitted real source version and approval. Next engineering hardening: output isolation and package link/no-clobber power-loss boundaries, compatibility only where tests reveal concrete gaps, then approved launch criteria. Do not publish as customer product without explicit user decision.

## 10. Date and evidence cutoff
2026-10-27 KST. PR #39 feature 4/4 PASS [40484567239](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40484567239); merged `f677c337c9884d8d008c7d79edc190d5562ebe42`. Post-docs final HEAD CI must be checked before asserting full current-head SUCCESS. No owner manual acceptance or real customer API proof.

---

# SOVIA latest P2 checkpoint — 2026-10-27, PR #38

## 1 Mission
Owner priority: MVP first (already synthetic-verified), then original R1–R9 blueprint gaps, then final security/stability/compatibility before approved real customer use.

## 2 New implementation
[PR #38](https://github.com/hibi89/SOVIA_sovereign/pull/38) merged to develop at `19d715062787bacbf24e6e3b1e8ebdf1501dad5f`. Existing `sovia_n8n_direct_audit.py` now accepts optional `--local-test-budget-bytes 1048576|2097152|4194304`, refusing oversized actual HTML/JSON before writes and checking a best-effort free-space snapshot with reused `sovia_guarded_export._check_storage`. Unspecified budget keeps previous behavior.

## 3 Portable publisher repair
`build_portable._atomic_publish` now validates payload is bytes before staging and reads staging inode metadata BEFORE publishing its ZIP/checksum via exclusive hardlink. Old order could orphan an output if stat failed after link. Existing v0.10 package member bytes unchanged.

## 4 Verification
[CI 40482664680](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40482664680) on feature `0822ed9c8fc7bbc8b9fc5bd81e5b0f5ac3a27440`: Windows/Ubuntu x Python 3.11/3.13 **4/4 SUCCESS**, 732 tests discovered/job, 0 failures (Windows 722 PASS/10 SKIP; Ubuntu 721 PASS/11 SKIP). Fresh extracted 12-file unsigned portable smoke PASS, unchanged ZIP SHA256 `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`. The **merge** SHA was not the feature SHA; docs-only final SHA CI should be checked live.

## 5 Failures and risk
No CI failures at tested PR head. Best-effort disk check is time-of-check only; multi-file writes are not a crash-atomic transaction. Optional cap is developer test budget, not a customer promise. Unsupported hardlink filesystems may refuse publishing safely.

## 6 Repo and source
PUBLIC `hibi89/SOVIA_sovereign`, code `develop`, default `main` docs-only. `sovia_n8n_direct_audit.py`, `build_portable.py`, `tests/test_n8n_direct_audit.py`, `tests/test_portable.py`, `N8N_DIRECT_AUDIT.md` changed. Previous HANDOFF.md/STATUS.md/RESUME.md contain archived details through PR #37; this file adds the latest validated PR #38.

## 7 Production and cost
Offline stdlib source utilities, optional PDF dependency. No live service, Production URL, signed commercial release, customer sale, paid API or cost. v0.10 ZIP unsigned and does NOT include later source-only n8n helpers.

## 8 Originals and safety
No real customer input, credentials, fonts, local device data, deletion, access changes, force push or repository visibility change. Old ZIP contents and SHA retained. This public repo must hold only synthetic safe fixtures.

## 9 Next unblocked goal
Build a distinct **versioned clean-install beta candidate** that integrates P2 optional tools into the deliverable rather than adding more standalone utility wrappers. Preserve old v0.10 ZIP and verify its identity. Real native n8n instance/source version and consent, upstream redaction effectiveness, owner physical Windows browser/Defender/Korean PDF, support/retention/limits and signed customer release remain BLOCKED/UNVERIFIED without owner evidence/authorization. Do not redo PRs #16–#38.

## 10 Cutoff
2026-10-27 KST. Latest validated feature `0822ed9c8fc7bbc8b9fc5bd81e5b0f5ac3a27440`, merged `19d715062787bacbf24e6e3b1e8ebdf1501dad5f`. Refresh HEAD and CI before work. No actual customer acceptance.
