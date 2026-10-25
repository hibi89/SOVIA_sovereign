# SOVIA Sovereign

**CURRENT RESUME ROUTE (2026-10-26 KST):** `main` is **documentation-only**; the latest tested/implemented SOVIA is on `develop` (PR [#13](https://github.com/hibi89/SOVIA_sovereign/pull/13) merged SQLite history at `edf8ea3de4a4fd781de34642b3d3f07a1ff67e10`, follow-up handoff/STATUS commit `ff11358e7103816addecca898cf194d901e2ab97`). [Merge CI](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214911902) 4/4 successful with 115 pass / 10 optional PDF skip per OS+Python matrix job. The P1/P2 audit core, JSON/CSV, optional PDF, and v0.7 SQLite idempotency/backup/restore/purge are completed *synthetic-only*. **On `ㄱ` or the exact new-chat trigger, read develop:HANDOFF.md then develop:STATUS.md and actual code; next P2 is an offline read-only HTML history dashboard, NOT SQLite or P1 again.** Keep default `main` unreleased, no production/Vercel/sale, no user private data.


**Independent AI Agent Audit**: evidence-based, explainable retrospective audit for AI agents.
**Current status at 2026-10-26 KST: docs and project plan only; NO RUNNABLE APP, NO PRODUCT TESTS, NO PRODUCTION.**

> Repository PUBLIC at last verification. Never add credentials, customer data, proprietary rules or raw prompts. Visibility changes require owner approval.

## Resume in a completely new ChatGPT session
User can enter exactly:
```text
[소비아소버린 깃헙 레포지토리 보고 작업이어가셈]
```
The designated lead should read [RESUME.md](RESUME.md) -> [HANDOFF.md](HANDOFF.md) -> [STATUS.md](STATUS.md), verify latest GitHub state, then immediately **implement the next unblocked task**, not ask for repeated context. For continuation in an active chat, `ㄱ` is sufficient.

## Delivery sequence
1. `P1` **3 active-day runnable local MVP**, original target Oct 26–28: structured synthetic JSON -> canonical events -> ≥3 explainable deterministic policy checks -> evidence-linked Korean HTML report -> CLI+tests.
2. `P2` compare against original design [GAP_MATRIX.md](GAP_MATRIX.md), incrementally add PDF/CSV/SQLite/local dashboard/validated integration, complete commercial safety checks.
3. `P3` prepare marketplace listing collateral during development; do not claim a live commercial product or publish before reviewed owner approval and testing.
4. `P4+` after paying signal: Cloud SaaS, Private offline installs, eventually Hybrid/advanced governance based on contracts. Shared [SOVIA Core architecture](ARCHITECTURE.md) prevents duplicate platform work.

## Zero-cash starting architecture
Existing PC + Python and locally installed free packages; no required cloud hosting, paid LLM APIs, ad campaigns or customer data upload for the MVP. Basic security input checks and synthetic test correctness run from the start. Heavier verification happens before commercial launch and customer-data ingestion, not after.

## Project operating references
[AGENTS](AGENTS.md) · [Requirements](REQUIREMENTS.md) · [72-hour MVP plan](MVP_72H.md) · [Roadmap](ROADMAP.md) · [Feature gaps](GAP_MATRIX.md) · [Listing draft](LISTING_PREP.md) · [Security](SECURITY.md) · [Test plan](TEST_PLAN.md) · [Business](GO_TO_MARKET.md) · [Decision log](DECISIONS.md) · [Branches](BRANCHING.md) · [Current status](STATUS.md) · [Handoff](HANDOFF.md).

**main** = stable, **develop** = integration, **feature/p0-audit-core** = first implementation. Nothing is deployed to Vercel.
