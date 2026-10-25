# SOVIA operating instructions
Updated: 2026-10-26 KST

## One-line new chat entrypoint (MANDATORY)
Exact user message: **[소비아소버린 깃헙 레포지토리 보고 작업이어가셈]**.
Treat this as unconditional continuation of the latest authorized, safe repository work, not a request for a recap. Start with [RESUME.md](RESUME.md), verify live repository state, restore [HANDOFF.md](HANDOFF.md) -> [STATUS.md](STATUS.md) -> AGENTS.md -> REQUIREMENTS.md -> MVP_72H.md -> GAP_MATRIX.md -> actual code. Don't ask for repeat background or new confirmation if safe authorized work is available. `ㄱ` means continue similarly.
Do not assume files/branches/SHAs are unchanged since this document. An inaccessible repository is a tool/access blocker, not proof of a feature failure.

## Mission and decision authority
User is owner. ChatGPT acts as lead designer/developer/reviewer with available tools. GitHub is canonical for code, requirements, tests and handoff. Owner approves external payments, privacy/visibility changes, security and access settings, external customer data transfer, live commercial listing, production deployments and consequential scope cuts. No forced push or destructive repo history rewrite. Verify author/committer attribution and SHA.

## Strategic execution
- Fastest measurable loop: runnable local vertical slice -> blueprint gap reconciliation -> iterative feature fill -> commercial security/readiness gate -> market proof -> Cloud and Private.
- Target for the initial 72h active development: one synthetic JSON input -> validated canonical events -> explainable risk findings (3 minimum) -> evidence-linked Korean HTML report -> CLI + real smoke/unit test evidence. 2026-10-26~28 is a **target**, not an assertion of work completed.
- P1 initially uses `feature/p0-audit-core`, integration `develop`, stable `main`; new branches created on demand only.
- Not negotiable early: input type/size checks, imported text never executed, secrets/redaction, HTML escaping, synthetic data, basic tests. More expensive penetration, endurance, backup/restore, tenant and offline validations are gated **before** relevant pilot/production and may follow the synthetic MVP.
- Sales collateral may be drafted concurrently (LISTING_PREP.md). No fabricated screenshots, invented certifications, 24/7 SOC guarantee or actual listing before test and approval.
- If import integration/PDF/UI blocks runnable flow, fall back to supported JSON + HTML, document the missing piece in GAP_MATRIX. One improved retry on failure then pivot.
- Prefer zero-cash work. Real customers and API/data costs require informed consent and budget.
- No secrets, customer documents, prompt bodies, restricted policy data in repo. Repository was PUBLIC at most recent verification; confirm before each sensitive step.

## Standard operational cycle
1. Inspect latest GitHub refs, HANDOFF, STATUS, requirements, exact code and tests.
2. Identify next unblocked issue and smallest implementation unit; compare alternative designs for consequential changes.
3. Implement, run tests, inspect actual output; distinguish DONE, PARTIAL, UNVERIFIED, BLOCKED and NOT_APPLICABLE.
4. Commit reviewed work with GitHub identity check; integrate when approved/validated. Never treat push, green CI or a Vercel Ready indicator alone as production verification.
5. Update GAP_MATRIX, STATUS, HANDOFF (all 10 sections) after material changes. Verify last SHA and branch location. Don't produce empty commits.
6. Report exact changes, test commands/pass-fail, repository/branch/SHA, deployment status/URL or NOT_APPLICABLE, next priority and approvals.

## New session first executable unit (unless repo moved ahead)
Issue #2: initial schema + synthetic fixture + runnable JSON parse -> single deterministic rule -> terminal/HTML finding report, basic offline tests. Continue #3/#4/#5/#11 to the three-rule working demo; don't merely replan it.

## Live integration override (2026-10-26)
`develop` now contains verified P1 and P2 source CSV/PDF through PR #12 at `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26`. Do not restart P1 issue #2 or assume no source on `develop`. On `ㄱ` create one scoped P2 SQLite metadata-history feature branch from current `develop` after fresh inspection; preserve default stateless CLI and original input, run real tests, update HANDOFF/STATUS. `main` remains unpromoted and documentation-only.

## SQLite P2 verified update 2026-10-26
Source branch `feature/p2-sqlite-history` implements optional hashed metadata-only SQLite history with idempotent ingest/conflict rollback, version 1 gate, no-clobber backup/restore, explicit purge, 33 regression tests. CI run 40214522381 4/4 green; per job 125 discovered/115 passed/10 optional PDF skipped/0 fail. Continue P2 review/merge to develop, then GUI and commercial acceptance gates; do not silently make stateless audit persistent or claim hashes anonymous. Active feature HEAD must be refreshed before editing; PR not yet merged at this checkpoint.

## P2 v0.7 develop integration override — 2026-10-26 KST
PR #13 merged SQLite history at `edf8ea3de4a4fd781de34642b3d3f07a1ff67e10`; post-merge CI 40214911902 4/4 SUCCESS, each 115 PASS/10 optional PDF SKIP. On `ㄱ`, start next P2 safe local dashboard feature from latest develop, NOT SQLite redo, keeping original stateless path and no external telemetry. Proposed fastest GUI slice: static, read-only HTML generated from SQLite, with locally escaped hashed metadata and no-clobber output; compare with localhost server, log decision in ADR. No production/sale approval.

## P2 v0.8 dashboard checkpoint 2026-10-26
2026-10-26 KST: P2 v0.8 feature/p2-offline-dashboard implements a read-only SQLite v1 to standalone Korean HTML dashboard; no local server, JS, outbound network, data write or output overwrite. Tested source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334 4/4 SUCCESS, Windows/Ubuntu x Python 3.11/3.13, each 148 discovered/138 PASS/10 optional PDF SKIP/0 FAIL. New tests 23. Not owner PC/browser visual QA, real customer records or production.
On ㄱ first determine PR and develop integration, then continue portable install/clean-machine UX and privacy/retention gates. Do not claim UI visual QA from HTMLParser tests or market release. Main remains docs-only.

## v0.8 develop integration and next step 2026-10-26
**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #14](https://github.com/hibi89/SOVIA_sovereign/pull/14) merged P2 v0.8 static offline SQLite history dashboard into `develop`, merge SHA `1123851900aee34d1c02d2a4590c6a0b5852727d`. [Post-merge CI run 40215946752](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215946752) completed **4/4 SUCCESS** on Windows/Ubuntu × Python 3.11/3.13; each 148 tests discovered / 138 PASS / 10 optional PDF SKIP / 0 FAIL. All P1 and v0.7 SQLite work remain integrated. **NEXT on ㄱ**: begin P2 portable offline package/fresh-install validation on a new branch from actual latest develop, with deterministic manifest/checksums/verification, sample CLI and user setup instructions. Do not redo the dashboard/SQLite/JSON work. `main` stays documentation-only, no Vercel/production or real customer-data evidence. Independent owner-machine browser visual QA remains UNVERIFIED.

On ㄱ, start a scoped portable offline package/installer and clean-machine acceptance test from develop (without secrets, unapproved deployment, or external data), then review/merge after CI. The HTML view is static; do not claim production or owner-device browser visual verification.
