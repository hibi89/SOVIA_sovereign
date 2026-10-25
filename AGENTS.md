# SOVIA operating instructions

> **ACTIVE WORK HAS MOVED — 2026-10-26 KST.** This default `main` branch intentionally remains a documentation-only/non-released baseline. **DO NOT** restart P1/issue #2 based on the archived snapshot below. The actual implemented product core is on `develop` (verified integration merge `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26`, follow-up docs `cd154200821054b8596d2decf7dc2f55fc93e22e`). It includes 5 offline deterministic audit rules, JSON+strict CSV source ingest, HTML/JSON/CSV exports and optional Korean PDF. PR [#12](https://github.com/hibi89/SOVIA_sovereign/pull/12) is MERGED into develop; Ubuntu/Windows × Python 3.11/3.13 [CI](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272) succeeded 4/4, 82 tests PASS/10 optional PDF SKIP/0 FAIL per job. **On the exact new-chat trigger or ㄱ: read `develop:HANDOFF.md` → `develop:STATUS.md` → `develop:AGENTS.md` → REQUIREMENTS/GAP/code**, verify fresh SHAs, and continue *P2 SQLite metadata-only history* in a scoped feature branch based on develop. No Production URL/Vercel, no real customer data or sale-ready release; real owner Windows font/PDF remains unverified. Repo PUBLIC: synthetic-only. Historical contents below remain preserved for the audit trail. Never auto-promote main or change repo visibility.


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
