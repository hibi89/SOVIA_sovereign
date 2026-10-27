## 2026-10-27 — P2 SQLite metadata idempotency integrity closure PR #56

[PR #56](https://github.com/hibi89/SOVIA_sovereign/pull/56) merged `develop` code SHA `bf435408b628817cc678bc8312e5fa68379390f6`. Repeat import checks persisted audit identity and count columns as well as findings digest, preventing silent `already_present` on altered metadata. Two tests / five synthetic subcases and [CI #40517663166](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40517663166) Win/Ubuntu Python 3.11/3.13 4/4 successful (826 discovered/job, 0 FAIL). Schema unchanged, old packages unchanged. This is local consistency, NOT cryptographic DB integrity against complete tampering and NOT permission to store real customer data. Sale gates remain user hardware/n8n provenance/PII/consent/licensing/retention/support/signing. No Vercel/Production.

---

## 2026-10-27 — candidate extracted-directory integrity milestone

Source-only `verify_portable_v012.verify_directory` previously ignored arbitrary unlisted empty directories even when reporting a pristine extraction. [PR #55](https://github.com/hibi89/SOVIA_sovereign/pull/55) on `develop` `ed19d73df8d5563d374125f9e4840e2416cee89e` now refuses unknown ancestor directories and unsupported entries. PR CI [40515324937](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40515324937) 4/4 PASS, 824 discovered/job, 0 FAIL. v0.10/v0.11.2 preserved, v0.12 beta test ZIP new SHA `facd78a00f024138363775c692b6e049bd29b76e4971c68d8f266f5106d35ba2`. Only strict local synthetic ZIP acceptance improved; not commercial/customer/owner acceptance. Remaining gates detailed in STATUS and HANDOFF.

---

## 2026-10-27 R3/R6/R9 new versioned portability/identity stage — PR #54

Synthetic-only separate 0.12.0-beta ZIP, nine-file strict manifest, verifier and CI artifact produced in [PR #54](https://github.com/hibi89/SOVIA_sovereign/pull/54), four-platform CI 821 tests/job zero fail. New SQLite metadata-only schema v2 prevents silently treating old source report_id from a changed rule version as the same report by using SHA-256(engine version + NUL + full normalized source digest), and stores findings digest to reject same-version conflict. Old v1 DB is refused; no automatic legal/migration assumptions or mixed version read. New CLI HTML uses true UTC sort. Historical v0.10 and v0.11.2 ZIP hash pinned unchanged. **NOT sellable or commercial P2 complete**: only synthetic tests, unsigned ZIP, no genuine approved n8n/PII/consent, owner Windows/Defender/manual Korean PDF/print, license/support/retention approval, Production or real customers. Issue #52 still open for supported-path default and release gates.

---

## 2026-10-27 — actual CI-verified source-only 0.12 UTC temporal successor, PR #53

[PR #53](https://github.com/hibi89/SOVIA_sovereign/pull/53) merged; 0.12.0-preview candidate now corrects BURST_TOOLS lexical timestamp false positives via timezone-aware UTC sort, 16 focused tests, 4/4 CI [40509368149](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40509368149) 797 tests/job, 0 failures. Existing 0.10/0.11.2 archive SHA unchanged. Opt-in next HTML preview calls successor. **R3 commercial supported release is still PARTIAL:** old packaged core still has defect, report identity shared across versioned findings breaks legacy SQLite idempotent meaning, new product package/strict installer/versioned history migration not implemented, no approved real n8n or owner Windows. Issue #52 OPEN. No production or sale.

---

## 2026-10-27 R3 Issue #52 v0.12 temporal engine source candidate

Reproducible old BURST_TOOLS false alert; versioned source-only candidate rewrites only sliding-window results in UTC-aware order. Opt-in v0.12 printable preview uses it; historic v0.10/v0.11.2 unchanged. Legacy SQLite identity can collide for same document and is NOT supported for candidate. See TEMPORAL_ENGINE_V012.md. Candidate CI pending; no real customer use or release.

---

## 2026-10-27 R2/R3 temporal event correctness — preview fix vs core open bug

Source-only v0.12 preview HTML chronology fixed in [PR #51](https://github.com/hibi89/SOVIA_sovereign/pull/51): real UTC datetime ordering handles mixed exact seconds and microseconds, tie breaks by event_id; 4/4 Windows/Linux CI verified (781 tests/job), immutable ZIPs unchanged. **R3 still PARTIAL:** existing frozen v0.10/v0.11.2 core `sovia_audit.evaluate` uses lexicographic UTC timestamp sort for 60-second BURST_TOOLS queue, potentially producing spurious alerts with valid fractional-second records. [Issue #52](https://github.com/hibi89/SOVIA_sovereign/issues/52) is OPEN and requires focused core regression plus separately versioned integrity-safe successor. Do not claim old version corrected, production accuracy, authorized native n8n or sale approval.

---

## 2026-10-27 R5 A4 print *preview* verified in hosted Edge (PR #49)

- **PROVEN on synthetic 3-event/5-finding case:** downloaded actual GitHub Windows Edge `--print-to-pdf`, A4 595×842 pt, 2 pages after print-only CSS compaction (was 3 with orphaned caveat), text-searchable, Korean and all sections visually intact. [PR #49](https://github.com/hibi89/SOVIA_sovereign/pull/49), [4/4 CI 40502431335](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40502431335), 2 immutable extracted ZIP smokes unchanged.
- **NOT proven:** owner PC, physical printer, longer/foreign-language data and pagination extremes, independent PII redaction/native authorized n8n integration, contracts/retention/signature/retail release. **Source-only next v0.12 preview only; existing v0.11.2 package HTML is not upgraded.**

---

## 2026-10-27 R4/R5 alternate report presentation — opt-in preview vs release

**SOURCE_ONLY_SCREEN_PREVIEW_VERIFIED:** [PR #48](https://github.com/hibi89/SOVIA_sovereign/pull/48) alternative HTML renderer merged `061195323638792ed7eafc431267c73743f395ad`; 4/4 CI, 775 tests/job. Actual Edge screenshot of next printable preview independently viewed: Korean cells and old narrow-column issue substantially improved for screen. Separate A4 print-only CSS exists but **no real printer/PDF print rendering or owner physical manual check yet**. Earlier PR #42 frozen package hash break avoided; v0.10/v0.11.2 immutable, no v0.12 distributable. **Owner Windows/Defender/SmartScreen/Korean PDF, authentic authorized n8n source/version/sanitization/privacy, retention/legal/signature/commercial release remain unresolved.**

---

## 2026-10-27 P2 browser visual evidence added (PR #47)

**Verified CI image:** GitHub-hosted real Windows Edge rendered *actual v0.11.2-beta synthetic local audit and dashboard* into two 1440×1600 PNGs and uploaded them; independently downloaded and viewed. Korean visible and dashboard 1/3/5/1; narrow audit evidence line-wrap and below-fold dashboard observed. **NOT VERIFIED:** complete print/viewport/responsive/accessibility, owner physical Windows/Defender/PDF, actual n8n native source authorization + PII redaction false-negatives, legal data/retention and signed commercial release. [PR #47](https://github.com/hibi89/SOVIA_sovereign/pull/47) merge `f21b5f58b0286fcdf45f8af2c2d5136eae629753`; artifact 12730803796 expires Nov 3 11:45 UTC. Existing versioned packages immutable.

---
## 2026-10-27 P2 browser compatibility evidence (PR #46)

**CI_BROWSER_DOM_PROVEN (synthetic):** Microsoft Edge on GitHub-hosted Windows Python 3.11 actually opened pristine extracted P2 ZIP's generated `file://` audit report and SQLite HTML dashboard; parsed Korean DOM labels/5 findings/CSP and exact inner ZIP SHA; 4/4 CI matrix with 766 tests/job and old/current clean ZIP smoke. **Still UNVERIFIED:** image/pixel/print layout, user's physical Windows/Defender/Korean font and optional PDF, comprehensive Edge background network absence, authenticated source provenance, native approved n8n version/PII redaction/consent, contracts/retention/support/quotas/signing/production or sale. Added tests do not edit protected v0.10/v0.11.2 release. [PR #46](https://github.com/hibi89/SOVIA_sovereign/pull/46) merged `6a72245db4ec3227958416b9812a1d1d99c7d370`.

---

## 2026-10-27 SOVIA P2 Windows NTFS junction proof vs commercial gate

**Verified via real GitHub-hosted Windows runner**: NTFS `mklink /J` child/direct-root/ancestor-root and review metadata refusal/exclusion, Python 3.11 & 3.13 Windows tests actually executed (not skipped), [PR #45](https://github.com/hibi89/SOVIA_sovereign/pull/45) merged at `a7bf1ae5b25b08c30801423e414d3615b8502eb5`; feature CI [40495478721](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40495478721) 4/4 success 762 tests/job, historic package smoke green. **Unverified**: adversarial TOCTOU race resistance, owner's own PC/install/Defender/visual Korean HTML/PDF, native authorized n8n/version/PII upstream, data-controller legal consent, privacy false negatives, retention legal obligations, signing/support/sale permission. Archive and core unchanged; no production.

---

## 2026-10-27 P2 Windows reparse point scan gate

**DONE_VERIFIED synthetic CI:** separate retention metadata inventory now rejects root and skips child NTFS reparse-point markers, preventing normal traversal of simulated junction/file/mount entries while retaining 1-pass category thresholds. [PR #44](https://github.com/hibi89/SOVIA_sovereign/pull/44) merged, 4/4 OS/Python CI success 757 tests/job, portable v0.10 and v0.11.2 ZIP smoke untouched. **PARTIAL_NOT_CERTIFIED:** Actual Windows junctions on owner device, concurrent path swaps (TOCTOU), native n8n supported source and consent, real PII sanitization, browser/Defender/PDF acceptance, legal retention/contract/signing/commercial release. No legal deletion permission created.

---

## 2026-10-27 P2 retention review performance — feature candidate, not a commercial gate completion

Offline read-only artifact retention policy previously scanned five times at distinct category thresholds. Source-only feature `feature/p2-retention-single-pass` permits one category-threshold scan, retains original single-threshold inventory and unchanged packaging/source checksums. Directories may still change during the scan, mtime is not legal retention start, hold/backup declarations remain unverified and deletion remains forbidden. Synthetic cross-check to legacy counts and OS/Python CI are required before integration. Owner Windows/manual, authorized native n8n and privacy, support/legal obligations, signing and sale approval remain OPEN.

---

## CURRENT P2 — one-step strict sanitized envelope→audit reports (2026-10-27 KST)

[PR #37](https://github.com/hibi89/SOVIA_sovereign/pull/37) merged `develop` SHA `6b7896f78005399a608486c93e18020c57c3c52e`. Source-only `sovia_n8n_direct_audit.py` merges two already-existing local commands: sanitized n8n-*like* envelope+SOVIA policy → strict existing canonical converter → actual five-rule evaluator → Korean HTML+JSON output, without creating a separate canonical file. 25 regression tests `tests/test_n8n_direct_audit.py`, guide `N8N_DIRECT_AUDIT.md`, tested feature SHA `0c764855ca96ff9f85b59911110fb9a679193f12`, [4/4 CI 40481135164](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40481135164) 722 discovered per OS/Python job 0 fail; old v0.10 ZIP unchanged and passing smoke.

**Remaining truth boundary:** no real native n8n API/export parser, authenticated source authorization, comprehensive upstream PII clearance, real version mapping/fixtures, owner Windows/browser/Defender/Korean PDF proof, supported quotas/contract, signed customer release or Production. Operator-claim approvals remain unsigned and unverified. One-command path is not yet in the old portable ZIP. Avoid treating source-only workflow as proof of sellability.

---

## CURRENT MVP→ORIGINAL BLUEPRINT RECONCILIATION (2026-10-27 KST)

[PR #36](https://github.com/hibi89/SOVIA_sovereign/pull/36) merged `0fab78dacf35c2048f329df882d6b76b16df7d57`: `MVP_BLUEPRINT_RECONCILIATION.md` records R1–R9 actual code path versus missing real acceptance; P1 functional MVP is **synthetically VERIFIED** already, not a reason to rebuild. Added source-only `sovia_ephemeral_diagnostic.py` with 16 regression tests covering R6 aggregate no-report-file diagnostic, local input acknowledgement, known rule counts and no input details stdout. `--ack-sanitized-source` does not prove real consent or cleaning. [CI 40479432652](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40479432652) Windows/Ubuntu × Python 3.11/3.13 **4/4 SUCCESS**, 697 tests/job, 0 FAIL, portable smoke PASS.

**Actual top P2 gaps (not synthetic tooling deficits):** real sanctioned installed n8n version/source fields/consent and pre-ingestion PII false-negative review; owner physical Windows clean-install/HTML browser, optional Korean PDF and Defender/SmartScreen manual acceptance; commercial support/retention/backup/output quota, package version/installer signing and owner launch approval. Cloud/Private/tenancy/billing are later gates. Existing source beta ZIP after PR #34 has new pinned inner hash `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`; old historical hash is not the new build. No sale or Production claims.

---

## CURRENT P2 — actual report writer rollback error path repaired (2026-10-27 KST)

[PR #34](https://github.com/hibi89/SOVIA_sovereign/pull/34) merged `60f9bc8cfb95012428f36064f0c29c1a54c93a40` after concurrently merged guarded source-only exporter [PR #35](https://github.com/hibi89/SOVIA_sovereign/pull/35). Previously `write_reports_atomically()` created a published hardlink before recording inode stat; if post-link stat raised, output might be orphaned despite overall failure. Writer now validates payload before allocating staging fd and stats before linking, preserving no-overwrite and best-effort rollback. Ten injected ENOSPC/stat/EIO/race tests. Old beta archive SHA `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`; current hardened source-build SHA `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`; BOTH explicitly pinned, unknown refused, neither signed.

[4-platform PR CI 40478529065](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40478529065) 681 tests/job, 0 fail, isolated portable smoke PASS. Initial old-hash pin mismatch was corrected after SHA diagnostic (no audit rule defect). Remaining: real hard-disk/quota/AV, power loss, concurrent readers, PDF and large/low-disk formats; this is **not a transactional guarantee**. Actual owner Windows/browser/Korean PDF/Defender, authorized n8n/privacy/legal support, signed release and commercial production are still open.

---

## CURRENT P2 — opt-in guarded real local HTML+JSON export (2026-10-27 KST)

[PR #35](https://github.com/hibi89/SOVIA_sovereign/pull/35) merged develop SHA 9d27e3468eb555ed72dfd2229cf414fbe674ebf1; new source-only sovia_guarded_export.py validates canonical JSON and real serialized HTML/indented JSON lengths against caller-selected LOCAL TEST 1/2/4MiB per-file limits *before* writing. Checks best-effort free space grouped by filesystem, uses original exclusive no-overwrite staged output writer, and emits redacted metadata only. 23 synthetic regression tests cover no-clobber, overflow, malformed/colliding paths, free-space reject, first/second hardlink injected failure and rollback. [CI 40478010428](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40478010428) Windows/Ubuntu × Python 3.11/3.13 4/4 SUCCESS, 671 discovered/job, 0 fail; v0.10 12-file portable beta unchanged by PR #35, isolated smoke PASS.

**Still open:** This opt-in script does not modify the default auditor CLI and is NOT in v0.10 ZIP. The 1/2/4MiB budgets are hypothetical developer test limits, not approved commercial quotas; no CSV/PDF protection, true disk exhaustion/concurrent atomic two-file transaction or crash durability proof. PR #34 independently proposes core writer fault-order changes and could alter portable checksum; coordinate regression after merge. Real owner Windows/Defender/browser/Korean PDF, sanctioned n8n+authorization, privacy/retention, supported volume, release/signing/support and commercial listing all outstanding.

---

## CURRENT P2 — bounded synthetic HTML/JSON output budget preflight (2026-10-27 KST)

[PR #33](https://github.com/hibi89/SOVIA_sovereign/pull/33) merged develop SHA `5d5f56106cd8aa5bf09ca5a35a10f74d764911ae`. New source-only `sovia_output_budget.py` checks actual audited HTML/indented JSON byte length against strictly hypothetical 1/2/4MiB per-file limits for fixed generated cases 10/100/500/1000 normal/alert_dense. Exit 0 within, 3 simulated exceed, 2 rejected. Metadata only, no report file, secrets or network, no changes to real core/portable ZIP. 16 adversarial tests. [Actions 40476502308](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40476502308) full 4/4 Windows/Ubuntu Python 3.11/3.13 SUCCESS, 648 discovered each, zero failure, clean portable smoke PASS unchanged SHA.

**Remaining export gap:** checker is NOT integrated into real CLI, so output size isn't enforced. No low-disk, CSV/PDF or all-or-nothing multi-output failure proof, nor approved limit. Do not conflate 1 MiB input cap with output budget or claim commercial SLA. Next distinct P2 work may test failure-safe optional real export under an explicitly agreed limit; owner device/browser/Defender/PDF, real sanctioned n8n, consent, privacy false negatives, retention/support and listing/release are still pending.

---

## CURRENT P2 — bounded synthetic core performance and input/output capacity (2026-10-27 KST)

[PR #32](https://github.com/hibi89/SOVIA_sovereign/pull/32) merged `develop` SHA `e8250fdac11ea1c89e482e26bcfca5ff23fe3183`. Added `sovia_capacity_benchmark.py` (source-only; no customer data), 33 adversarial tests, `SYNTHETIC_CAPACITY.md`, four-matrix CI workload step. Generates allowlisted 10/100/500/1000 events × 0-findings normal or dense 4N+(N−2) findings, uses bounded existing JSON reader/evaluator/HTML+JSON serializers and reports one-round elapsed time and Python tracemalloc peak, all WITHOUT customer/SLA claims. Does not persist benchmarks, run n8n, PDFs, SQLite or export files. Original core input 1 MiB/1000 records, main and old 12-file beta ZIP unchanged.

[CI 40473847652](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40473847652) feature `fa1fb31777667120ddce8bf465085715b701838e`, Win/Ubuntu 3.11/3.13 **4/4 SUCCESS**, 632 tests/job, no fail, all synthetic case measurements and portable smoke PASS. Dense 1000 generates 4998 findings, JSON report 2136699 bytes (> input 307201 bytes) and measured 314.6–568.2 ms across runners with tracemalloc overhead; not P95/RSS SLA. Post-doc final SHA CI to recheck.

**Open:** real customer workload/volume and PDF/SQLite/export full-path benchmarks, bounded report output policy, independent owner PC manual acceptance, lawful n8n data/API/version, privacy and retention, release signing/terms/supported quota, commercial approval. Next safe unit should be distinct from PR #32: e.g. fail-closed report-size policy for synthetic outputs or honest buyer-supported scope checklist. Existing 1MiB/1000 event reader limits are engineering guards only.

---

## CURRENT P2 — watermarked actual-engine synthetic sales sample generator (2026-10-27 KST)

[PR #31](https://github.com/hibi89/SOVIA_sovereign/pull/31) merged `develop` SHA `f76807c2ce1d9d72eac98d863d4ad1fd19a6caf6`. Fixed-fabricated-input-only `sovia_demo_pack.py` calls real five-rule audit engine and writes an UNUSED local folder containing visible+print SAMPLE HTML (offline CSP), explicitly wrapped synthetic JSON, buyer scope notes and unsigned SHA-256/byte-count manifest. `tests/test_demo_pack.py` 29 synthetic safety/regression tests, `SALES_SYNTHETIC_SAMPLE.md`. No actual screenshots, public listing, client data or external API. Unchanged 12-file v0.10 portable ZIP and main docs-only.

[Actions 40472609343](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40472609343) tested SHA `667a54319a3a6a36f01417ac29ff826745ddf7c4`: 4/4 success Windows/Ubuntu Python 3.11/3.13, 599 tests discovered/job, 0 FAIL, old portable smoke PASS. First CI run `40472528662` found 1 mistaken test import of portable allowlist, corrected in test and full rerun green. Post-doc final HEAD CI to confirm.

**Gaps:** Owner must actually run/view the sample and capture honest screenshots, verify Windows/browser/Defender/Korean PDF, independent real installed n8n/source data/consent and privacy false-negative, legal retention/backup/support, version and signed commercial release. Generator provides an **unpublished synthetic draft**, not a completed published sales portfolio. Next safe unit: quantify supported synthetic volume/resource timebox and define narrow honest customer scope.

---

## CURRENT P2 — source-only owner synthetic HTML/PDF static preflight (2026-10-27 KST)

[PR #30](https://github.com/hibi89/SOVIA_sovereign/pull/30) merged `develop` SHA `6a3a46ec5b1b3d6e99011aef485806f58993ac9d`. Added `sovia_owner_artifact_preflight.py`, 35 `tests/test_owner_artifact_preflight.py`, `OWNER_ARTIFACT_STATIC_PREFLIGHT.md` for distinct read-only post-selfcheck static artifact check: selfcheck v0.10 synthetic contract, output JSON 3 events/5 findings/five rules, audit HTML text and report ID, dashboard 1/3/5 counters and CSP, conservative active HTML/resources/CSS screening, optional PDF %PDF-/%%EOF only. Symlink/size inputs rejected; no writes/network. Result **manual pending**, not real Windows/browser/Defender/SmartScreen/Korean PDF visual or security proof. Owner checklist and earlier read-only evidence checker remain separate and unchanged.

[Actions 40471339135](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40471339135) tested feature SHA `7a08f4f1a20257301e8baca3d9402f595280a2b8` Windows/Ubuntu × Python 3.11/3.13 **4/4 SUCCESS**, 570 discovered/job, 0 fail, old portable smoke 12-file beta unchanged SHA `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`. Post-doc HEAD CI to verify.

**Open gaps:** Actual owner device Windows manual visual/AV, provenance of real client logs / controller consent, genuine n8n instance/version sanctioned raw-to-sanitized mapping, privacy false negatives and retention/backup legal policy, signed supported release and sales authorization. Current v0.10 ZIP excludes P2 modules; `main` docs-only; NO production. Next safe unit must be distinct from PR #30 and old work.

---

## CURRENT P2 — unsigned synthetic source/policy/canonical integrity & heuristic PII gate (2026-10-27 KST)

[PR #29](https://github.com/hibi89/SOVIA_sovereign/pull/29) merged `develop` SHA `fdd13e9c7fd599c51e3cc4d934c3fde30ccfb2cf`. New read-only `sovia_synthetic_evidence.py`, 35 adversarial tests `tests/test_synthetic_evidence.py`, `SYNTHETIC_EVIDENCE.md`. Strict 7-field unsigned synthetic manifest binds SHA256 of fabricated source, policy and regenerated canonical steps; existing offline PII-pattern preflight scans source/policy before conversion and canonical metadata afterward; no writing, API or real logs. Exactly one known fixed, >40 character protocol `source_kind` literal is excluded from heuristic opaque-token scan to avoid an internal false positive, while arbitrary other values remain inspected. This is NOT cryptographic source authentication, actual customer approval, complete PII clearance or n8n native import. Anyone can rehash/forge the unsigned claim.

[CI 40470007830](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40470007830) feature `223d1d80913382af6c418f0960a98e59a23516b6`: **4/4 SUCCESS**, Windows/Ubuntu Python 3.11/3.13, 535 tests discovered each, zero fails, old portable smoke passed. Initial CI 40469827503 had 8 failing/8 error synthetic tests on Ubuntu due solely to PII scanner matching internal source_kind constant, corrected by exact exemption and reverified full matrix. Post-doc HEAD CI to verify.

**Open:** actual customer data controller consent and authentic producer/key signatures; live installed n8n version and safe upstream redaction; true PII false-negative and operator review, physical Windows/Defender/browser/Korean PDF device acceptance, legal backup/retention/erasure and signed commercial release. Old v0.10 portable untouched, main docs-only, no Production/Vercel. Next safe work should address a distinct owner acceptance or synthetic security gap, not repeat this unsigned digest logic.

---

## CURRENT P2 — synthetic n8n execution summary bridge into canonical steps (2026-10-27 KST)

[PR #28](https://github.com/hibi89/SOVIA_sovereign/pull/28) merged `develop` SHA `d065dd2834ecc7499a0c551220ba5950ff7effed`. Synthetic-only strict `sovia_n8n_execution_bridge.py` accepts tagged metadata summary (`id/workflowId/status/startedAt`) paired **only with explicitly pre-sanitized** steps, enforces version-specific fabricated ID types and rejects raw data-bearing fields. It delegates to existing sanitized converter and 5-rule canonical evaluator; no invented actions or permission/evidence values and no n8n API/customer logs. New 31 `tests/test_n8n_execution_bridge.py` cases, 2 fabricated examples and `N8N_SYNTHETIC_EXECUTION_BRIDGE.md`. Verified [CI 40468563493](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40468563493) feature `381d7af46f29efb28e60bec608feece934e97de3`: 4/4 SUCCESS Windows/Ubuntu × Python 3.11/3.13, 500 discovered/job, zero fail, existing v0.10 portable smoke PASS all. First CI had incorrect timestamp test assumption; corrected and full suite reverified. Post-doc HEAD CI pending verification.

**Still OPEN:** real pinned installed n8n version and legal data controller authorization; independent genuine upstream sanitizer / privacy false-negative coverage / authenticated operator, actual API tests, Windows/Defender/browser/Korean PDF device review, backup/retention/erasure lineage, signed commercial release and support. `synthetic_only` is unverified user claim, not proof of safe source. Old ZIP unchanged, main docs-only, no Production/Vercel. Next safe work should prioritize a **new** privacy/provenance/owner-acceptance gate, not repeat this synthetic mapping.

---

## CURRENT P2 — pinned public n8n getExecution source field types (2026-10-27 KST)

[PR #27](https://github.com/hibi89/SOVIA_sovereign/pull/27) merged `develop` SHA `8c321ea8bd701f350d0a711f2544b5f729273251`. Official tagged `n8n-io/n8n` 1.x `spec/schemas/execution.yml` (blob `e20e27a02402563f3904c8b0468d56d32a42196c`) and 2.x `spec/paths/getExecution.generated.yml` (blob `329097122a6bfda7410314ff4ca73878c34b6918`) show 12 vs 23 Public API GET response properties and number→string changes of id/workflowId/retryOf/retrySuccessId. Added strictly synthetic name-only `sovia_n8n_execution_reference.py`, 27 `tests/test_n8n_execution_reference.py`, two fabricated manifests and `N8N_EXECUTION_PUBLIC_SCHEMA.md`; every recognized manifest remains IMPORT BLOCKED. 2.x query redaction/default references do NOT prove runtime privacy. No real execution API calls, customer data, credentials, native converter, live version verification or old beta ZIP changes. PR feature CI [40467364912](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40467364912) Windows/Ubuntu × Python 3.11/3.13 **4/4 SUCCESS**, 469 discovered per job, 0 fail; old portable smoke PASS. Post-doc HEAD CI pending verification.

**Still unsatisfied:** sanctioned real n8n instance/version compatibility, upstream PII redaction and data-controller approval, mapping and real negative tests; physical Windows manual acceptance; backup/retention erasure provenance; release signing and commercial permission. `main` is docs-only, no production/Vercel. Next safe unit: synthetic execution-to-canonical mapping **design only**, with customer/source permissions and actual API work gated.

---

## CURRENT P2 — n8n fixed-tag official public workflow key reference (2026-10-27 KST)

[PR #26](https://github.com/hibi89/SOVIA_sovereign/pull/26) **MERGED** to `develop` SHA `45d8c00ee3a898b599a3a75d2e1b219ae0da72e9`. New `sovia_n8n_pinned_reference.py`, 28 synthetic `tests/test_n8n_pinned_reference.py`, 2 fabricated key-only example manifests, `N8N_PINNED_PUBLIC_SCHEMA.md` and `N8N_VERSION_PROBE.md` crosslink. Official n8n-io/n8n release **tags, Git commits and Public API workflow.yml Git blob SHAs** were fetched and pinned: `n8n@1.123.88` / `6b88ad7f6be54df9f26efe17e0c249e345b40375` / blob `7f36ea82d077db612b6cea4807ccaa7ee1e1227e` and `n8n@2.44.7` / `cbe3950c51759577f9e611d28f8f5cd01828eaef` / blob `0eb571b216406d9d2d4b6e072195a1296124e6fc`. Tagged YAML top-level property sets 12 vs 21; both require `name/nodes/connections/settings`; exactly 9 added in the 2.44.7 file relative to 1.123.88 and none removed. **This is NOT the actual workflow export contract nor an execution API value mapping.** Code compares fabricated key names only; exact matches still **exit 3/IMPORT BLOCKED**; data-bearing `staticData/pinData` keys rejected; no n8n calls, payloads, conversion or consent proof.

[Actions 40466013364](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40466013364) on verified PR source SHA `4a428996f3d5f8cc146572adb60947b3b4aeb36d` **4/4 SUCCESS**, Windows/Ubuntu Python 3.11/3.13, 442 tests discovered/job, Windows 432 PASS/10 SKIP, Ubuntu 431 PASS/11 SKIP, zero FAIL, unchanged 12-file v0.10 extracted portable smoke PASS every job. Existing sanitized converter and PII/attestation gates untouched. Remaining P2: pinned external **execution** API schema/real version and authorized sanitizer mapping, customer legal authorization, privacy false negatives, real owner Windows HTML/Defender/PDF acceptance, backup/retention/erasure governance, signed commercial release and approval. `main` docs-only, old portable ZIP unchanged; source-only. CI at later documentation-only HEAD not independently checked.

---

## CURRENT P2 — synthetic n8n source family/version-claim probe (2026-10-27 KST)

[PR #25](https://github.com/hibi89/SOVIA_sovereign/pull/25) **MERGED** to `develop` at `4e25e3b08584d47261b24d3f296be129cdfbc7c7`. Added `sovia_n8n_compatibility.py`, 30 synthetic `tests/test_n8n_compatibility.py`, 3 source-family/claimed-version **key-only** example manifests, `N8N_VERSION_PROBE.md` and `N8N_SANITIZED.md` cross-link. Strict probe recognizes the FOUR expected keys of SOVIA sanitized v1 envelope only as **synthetic shape match**; mock n8n workflow-export and execution API keys, including claimed 1.x and 2.x versions, are ALWAYS **unverified and blocked**. Payload/credential/parameter/data-like fields, missing or extra keys, malformed version strings and raw exports are rejected. This is **NOT true n8n API/schema or release-version support** and cannot verify consent or that user assertions are synthetic.

[GitHub Actions 40464872399](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40464872399) **4/4 SUCCESS** on exact tested feature head `b103c6df4f1167eaaaf1f0724dc4452865799485`: Ubuntu/Windows Python 3.11/3.13 with 414 tests discovered per job; Windows 404 PASS/10 SKIP, Ubuntu 403 PASS/11 SKIP, 0 FAIL; old unmodified v0.10 12-file portable smoke PASS all. Existing `sovia_n8n_sanitized.py` converter, PII preflight, operator assertions, history and other P1/P2 modules unchanged. Probe is source-only and **not shipped in the old ZIP**. Remaining P2: independently verified native n8n pinned-release schema and approved sanitized source fixtures, genuine authorization, reliable PII handling, retention/deletion governance, owner physical Windows/Defender/Korean PDF acceptance, release/support and sale approval. `main` docs only; production NONE. Post-docs HEAD CI not independently verified.

---

## CURRENT P2 — read-only category retention review dry-run (2026-10-27 KST)

[PR #24](https://github.com/hibi89/SOVIA_sovereign/pull/24) **MERGED** into `develop` at `40ed61a7e93d1588a453f27223d688b31d6de5c4`. Added separate `sovia_retention_review.py`, strict synthetic `examples/demo_retention_review_policy.json`, 25 `tests/test_retention_review.py`, `RETENTION_REVIEW.md` and `RETENTION.md` link. This consumes **only** the existing read-only `sovia_retention.inventory` metadata counts, applies category-specific **review** thresholds and unverified operator hold/backup assertions, returns HOLD/VERIFY/HUMAN_REVIEW_ONLY by category. Never reads customer contents, returns file paths or names, executes purge/deletion, alters files/DB or authorizes disposal. Requires explicit `--dry-run`; 5 non-atomic scans with pinned clock and gross change detection are not an atomic snapshot.

Verified PR source SHA `4f835648412892a94bcf79db93eebe98f4153efd`: [GitHub Actions 40463702926](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40463702926), **4/4 success** on Windows/Ubuntu Python 3.11/3.13. 384 discovered/job, Windows 374 PASS/10 SKIP, Ubuntu 373 PASS/11 SKIP, 0 FAIL; prior unchanged clean-extracted 12-file portable beta smoke PASS all four. No actual customer input, legal retention-period evidence, independent hold/backup confirmation, deletion control approval, owner-PC acceptance, production or commercial signoff. New review helper is **outside** v0.10 portable ZIP. Remaining P2: genuine authorization and n8n versioned sanitized input, retention commencement & legal-hold lineage, backup disposal/secure erase policy, owner Windows/Defender/Korean PDF manual acceptance, packaging/release support and owner-approved paid pilot. `main` docs-only, production/Vercel NONE. CI at docs-only HEAD not independently verified.

---

## CURRENT P2 — owner Windows evidence consistency checker integrated (2026-10-27 KST)

[PR #23](https://github.com/hibi89/SOVIA_sovereign/pull/23) **MERGED** source-only `sovia_owner_evidence.py`, 30 synthetic unit tests (`tests/test_owner_evidence.py`), and `OWNER_EVIDENCE_CHECKER.md` into `develop` at `8e120a9db2baa1b490d2ce3987979366185fcf39`. Existing `OWNER_WINDOWS_ACCEPTANCE.md` was linked to the new checker. The checker reads and hashes the **actual local v0.10 inner portable ZIP**, requires documented SHA-256, validates the existing owner self-check JSON (Windows label, Python >=3.11, 6 PASS checks, synthetic 3/5/1 results, old manual statuses NOT_CHECKED) and validates a separate strictly allowlisted manual-review JSON; it never edits source ZIP, owner self-check, existing reports or policy. Inconsistent, omitted, failed or suspicious records are rejected or marked BLOCKED/PENDING. Even complete operator-declared reviews yield **OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED**, not real device verification, owner identity verification or commercial signoff. Optional PDF failure blocks a claimed complete review; skipped PDFs cannot be declared visually PASS.

Verified source PR head `212ec674e56afebfadcc7bcc65525acfa5015967`: [GitHub Actions run 40462591912](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40462591912) **4/4 SUCCESS** on Ubuntu/Windows Python 3.11/3.13, each 359 discovered; Windows 349 PASS/10 SKIP, Ubuntu 348 PASS/11 SKIP; zero fails; existing 12-file portable clean-extract smoke PASS in all jobs. The initial feature CI failed one test due to using the wrong manual field key; corrected and reran full matrix. New checker is **not in prior portable ZIP**; no independent actual owner-PC Windows/Defender/SmartScreen/Korean HTML/PDF visual evidence exists. Remaining P2: true owner-device human acceptance, real n8n version-specific mapping, authenticated permission and sanitized customer source validation, retention/backup disposal, production release/security, owner commercial approval. `main` remains docs-only; production/Vercel NONE. Latest docs HEAD CI remains unverified.

---

## CURRENT P2 — synthetic privacy triage and owner Windows acceptance gate (2026-10-27 KST)

[PR #22](https://github.com/hibi89/SOVIA_sovereign/pull/22) **MERGED** to `develop` SHA `431035b572625e42a94f83c69426700b9f00acb4`. New bounded stdlib `sovia_privacy_triage.py` and 24 `tests/test_privacy_triage.py` cases, synthetic baseline and deliberate-review fixtures, `PRIVACY_TRIAGE.md`, `OWNER_WINDOWS_ACCEPTANCE.md`; existing `FALSE_POSITIVE_REVIEW.md` cross-linked. Triages **labeled synthetic-only patterns**, returns aggregate TP/TN/FP/FN without case identifiers or samples. A deliberately mismatched synthetic suite returns exit 3/REVIEW_REQUIRED (one FP/one FN); scanner and safe-code mapping are **NOT relaxed**, and no override list is created. No real customer population testing or PII absence certificate.

[PR-head GitHub Actions 40461363016](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40461363016) **4/4 SUCCESS** on exact `e04713d1f5b7ae5b584ba111b51affc4e91f9235` Windows and Ubuntu Python 3.11/3.13: 329 discovered per job, Windows **319 PASS/10 SKIP**, Ubuntu **318 PASS/11 SKIP**, 0 FAIL, unchanged 12-file portable smoke PASS on all jobs. Previously integrated audit/PDF/CSV/SQLite/dashboard, n8n-like adapter, retention preflight, safe-code registry preserved. Neither new feature ships in old v0.10 ZIP nor does CI constitute owner's real Windows/Defender/SmartScreen/Korean HTML/PDF acceptance. Windows manual checks remain **NOT_CHECKED**. Open commercial gates: owner device evidence, genuine customer source consent, real n8n version mapping, validated PII handling, review identity, backup/retention/disposal, signed release/support, approval for sale. `main` docs only, production/Vercel NONE. Docs-head independent CI unverified.

---

## CURRENT P2 — synthetic safe-code registry integrated (2026-10-27 KST)

[PR #21](https://github.com/hibi89/SOVIA_sovereign/pull/21) merged into develop at `c882ac46a837cbadc33eb0465a39c20d0f35bb01`. Added `sovia_code_registry.py`, `tests/test_code_registry.py` (31 new cases), `examples/demo_code_registry.json`, `CODE_REGISTRY.md`, and `FALSE_POSITIVE_REVIEW.md`. Explicit injective lower-case tool/target codes map corresponding SOVIA policy allow/sensitive sets; unknown or ambiguous mappings fail closed. Source, policy, registry AND resulting canonical audit metadata are PII-pattern scanned. Existing five-rule finding signatures and coverage warnings must remain identical; any drift refuses output. This is **synthetic-only mapping of already sanitized codes**, not automatic PII redaction or proof of client authorization.

Verified PR head `2b50e2b8299ad74f8e757a090953e61a956c4050` [GitHub Actions 40460394248](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40460394248) 4/4 SUCCESS on Windows/Ubuntu Python 3.11/3.13: 305 discovered each, Windows 295 PASS/10 SKIP, Ubuntu 294 PASS/11 SKIP, 0 FAIL; full existing 12-file beta ZIP smoke PASS. Initial PR CI exposed a fixture tuple-mutation TEST error; fixed and re-ran the **entire matrix** successfully. New registry remains outside the v0.10 ZIP. Still OPEN: real versioned n8n inputs and owner/customer permissions, effective PII anonymization, reviewer authentication, false-positive review evidence, backup/retention/deletion policy, owner Windows/AV/Korean PDF manual validation, signed release/commercial gates. `main` and production untouched. Docs-head CI not independently tested.

---

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
