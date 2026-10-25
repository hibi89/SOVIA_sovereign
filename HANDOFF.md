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
