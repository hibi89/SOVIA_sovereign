# SOVIA new-chat continuation entrypoint — P2 SQLite milestone

**LATEST INTEGRATION VERIFIED — 2026-10-26 KST:** PR [#13](https://github.com/hibi89/SOVIA_sovereign/pull/13) MERGED the opt-in SQLite history (version 1, recovery and purge) into `develop` at `edf8ea3de4a4fd781de34642b3d3f07a1ff67e10`. [Develop post-merge CI 40214911902](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214911902) 4/4 SUCCESS, Windows/Ubuntu × Python 3.11/3.13; each 125 tests discovered, 115 PASS, 10 optional PDF SKIP, 0 FAIL. Source/feature integration is DONE, NOT waiting for a PR. Next safe task on `ㄱ`: create a new scoped branch from latest `develop` and implement a read-only, generated offline HTML history dashboard (no local server/network) with output no-clobber, escaped metadata, report/rule/time overview, tests; then continue installer/retention/customer authorization gates. Do not reimplement P1/CSV/PDF/SQLite. Production/Vercel none; `main` remains documentation-only, not sale-ready. The earlier feature-branch notes below are archival.

Exact trigger: [소비아소버린 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. Verify live GitHub first; this is the continuation signal, not a request for a recap. After checking HANDOFF and STATUS on newest active branch/develop, read AGENTS/REQUIREMENTS/GAP_MATRIX/HISTORY and real code/tests. P1, CSV input/output and optional PDF are completed synthetic checkpoints and MUST NOT be restarted.

Current next milestone: P2 v0.7 SQLite opt-in history completed on feature/p2-sqlite-history at tested SHA 59b982bc8960e38a948c68e49d874457de3e01fa, CI run 40214522381 4/4 OS/Python green (115 pass/10 PDF skip each). PR #13 already merged and verified on develop at edf8ea3de4a4fd781de34642b3d3f07a1ff67e10; DO NOT repeat the integration. Then next P2 priority is read-only local history dashboard, installation/recovery/retention/PII and authorized input adapter. main default remains documentation-only; production not deployed. No need for new permissions for synthetic-only safe development; obtain approval for external data/payments/visibility/production.

---

# SOVIA — new-chat one-line continuation protocol

**CURRENT INTEGRATION (2026-10-26 KST):** PR [#12](https://github.com/hibi89/SOVIA_sovereign/pull/12) merged synthetic Audit Lite P1/P2 into `develop` at merge SHA `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26`. The previous no-code baseline on `main` is HISTORICAL and `main` is intentionally not promoted. Windows+Ubuntu Python 3.11/3.13 CI run [40213287272](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272): 4/4 success, 82 passed / 10 optional PDF skipped / 0 failed per job; PR validation [40213518280](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213518280) SUCCESS. Next unblocked work is P2 SQLite metadata-only history and recovery on a **new feature branch from develop**. Verify latest HEAD, then read HANDOFF/STATUS/GAP_MATRIX. No production or user Windows/real customer-data verification.


Updated: 2026-10-26 KST. Applies to repository `hibi89/SOVIA_sovereign`.

## Exact user trigger
`[소비아소버린 깃헙 레포지토리 보고 작업이어가셈]`

Also accept `ㄱ` as continue-the-next-task after repository context is restored.

## First response to trigger: ACT, not re-onboard
1. Use linked GitHub connection. Verify the exact `hibi89/SOVIA_sovereign` repository, `main`, `develop`, `feature/p0-audit-core` branch heads, latest commits/changed files, outstanding issues and repository visibility. Never use a memorized SHA as if current.
2. Read **HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → MVP_72H.md → GAP_MATRIX.md → ARCHITECTURE.md → ROADMAP.md → actual code/tests** (and SECURITY.md / TEST_PLAN.md / LISTING_PREP.md as relevant). Resolve discrepancies by inspected repo/test/deployment evidence, not by stale documentation.
3. Choose the *next safe and unblocked* task, not an already finished task. Unless new code exists, default to GitHub issue #2: event schema, synthetic fixtures and a smallest runnable local JSON → canonical event → 1+ policy finding → CLI/HTML vertical slice on `feature/p0-audit-core`.
4. Implement it directly using available tools and permissions, run actual tests, inspect code and output, commit to the appropriate branch, and advance through #3 → #4 → #5 → #11 with MVP-first priority. Integration goes to `develop`, validation to `main` only with reviewed evidence. Don't fabricate work performed asynchronously or over multiple dates.
5. After any meaningful change, update `GAP_MATRIX.md`, `STATUS.md`, `HANDOFF.md` with actual SHA/test command/pass-fail counts, current phase, exact next task, blockers and deployment state; verify commit head. If no state change, do not create an empty or ceremonial commit.
6. Respond with concise completed work + evidence, remaining work + blockers. **Do not ask for recap, a new prompt, or generic confirmation** when previously approved, safe work can proceed. Ask only for essential new permission/inputs.

## Canonical confirmed strategy
- Single shared offline-first SOVIA Core (Python/deterministic policies/evidence), Audit Lite first; future revenue-funded Cloud and customer-owned Private share the core. Do not build separate redundant products.
- Zero-cash MVP using current PC and open-source tools, synthetic-only data. No hosting, paid APIs, ad spend or external transmission without approval.
- **3 active workday MVP target 2026-10-26 through 2026-10-28**: input → safe normalization → at least 3 explainable risk rules → evidence pointers → Korean HTML report → reproducible CLI/unit/smoke tests. Dates are historical targets when read later, not assertions of completion.
- After minimal working MVP: compare against the original blueprint using GAP_MATRIX; incrementally fill CSV/PDF/SQLite/local UI/connectors; prepare product listing images, demo and terms in parallel as drafts. Do not publish/charge until real product, privacy/security and owner approvals.
- Advanced penetration/endurance/reliability testing happens before relevant commercial production. **Basic safe input parsing, nonexecution of payloads, secret hygiene, redaction, HTML escaping and smoke tests always apply.**
- Full product path: validated Audit Lite → initial paid customer proof → Cloud SaaS subscriptions → contract-backed Private/offline → Hybrid/advanced governance where justified.
- User prefers concrete tested artifacts, minimal up-front cost and autonomous progress. Do not count planning as coded features.

## Actual known stop point (at handoff authoring)
Verified baseline before this handoff-doc-only update: `453a5345f6ba7819956caf4fb9de9038148d0292` on main/develop/feature/p0-audit-core. Repo is **PUBLIC** although earlier preference was Private; do not alter visibility or upload confidential content without owner approval. P0 docs/branch/issue backlog completed; **no app source, no tests run, no deployments, no customers**. No Vercel project/production URL. Check fresh GitHub truth before assuming these remain true.

## Next recommended atomic execution
Issue #2 (potentially combine minimal #3): create runnable schema, synthetic fixtures, a JSON importer, one rule and a basic HTML/CLI output with tests; aim at Day-1 working vertical slice rather than days of abstract coding. Progress to three rules and final 72h demo as work continues. If actual implementation is already ahead, skip completed work and advance to the highest-priority gap.

## Stop/go rules
- Security/visibility/privacy/payment/domain/hosting/customer data transmission/production deployment changes require owner approval.
- Public repo: public-safe code and synthetic fixtures only; no .env, secrets or customer records.
- Tool fails: diagnose once, improved retry at most once; if blocked, explain failed evidence and continue unrelated safe tasks where possible.
- No false claims about active background process, tests, runtime, legal compliance, live monitoring, production SLA, or cost savings.
- Don't automatically change GitHub/Vercel bindings or release a public commercial listing.

## Final response template
`Repo / branch / actual commit SHA / implemented changes / tests (command, pass, fail) / Cloud-Vercel deployment status or NOT_APPLICABLE / remaining gaps / next task / owner action only if truly needed.`
