# SOVIA Sovereign

**Independent AI Agent Audit** — evidence-first audit and risk review for AI agents.  
**Status:** Planning / architecture approved for documentation only; application code and production service **not yet implemented**.

> This repository is currently PUBLIC (verified 2026-10-25 KST). Never commit secrets, customer data, or confidential business materials. Planned private status requires the repository owner's approval/action.

## Product direction

Build **one reusable SOVIA Core**, then offer:
- **Audit Lite (local/offline first):** read-only import of supported agent logs, deterministic policy checks, evidence-bound Korean reports.
- **SOVIA Cloud (later):** managed multi-tenant dashboards, customer-controlled alerts, subscriptions.
- **SOVIA Private (later):** customer-operated, air-gapped-compatible deployment for confidential environments.

**Non-goals for MVP:** runtime threat blocking, certification issuance, full legal compliance guarantees, 24/7 human monitoring, ingesting confidential source documents.

## Zero-cash-first delivery

1. Synthetic-data-only development on an existing PC using open-source software.
2. Three-day functional MVP target: CSV/JSON adapter, normalizer, risk rules, timeline, HTML/PDF report, tests.
3. Harden local Audit Lite using sanitized realistic examples; validate before commercial use.
4. Sell limited-scope audit pilots, fund the cloud build with verified revenue.
5. Extend to Cloud and Private **only after objective demand and security gates**.

See [AGENTS.md](AGENTS.md), [REQUIREMENTS.md](REQUIREMENTS.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ROADMAP.md](ROADMAP.md), [GO_TO_MARKET.md](GO_TO_MARKET.md), [SECURITY.md](SECURITY.md), [TEST_PLAN.md](TEST_PLAN.md), [STATUS.md](STATUS.md), and [HANDOFF.md](HANDOFF.md).

## Governance

- `main`: stable, reviewed documentation/code. No production deployment assumed.
- `develop`: integration of work after checks.
- `feature/p0-audit-core`: initial implementation working branch.
- Other feature branches are created **as needed**, not in bulk. No force push; no secrets in Git.
- User shorthand `ㄱ` means: inspect HANDOFF → STATUS → AGENTS → REQUIREMENTS → source; proceed with the next unblocked work item, verify, update status/handoff.

**Important:** Public README is a project description, not an assertion of completed or certified security capabilities.


## 72-hour MVP-first execution — updated 2026-10-26 KST
- [MVP_72H.md](MVP_72H.md) sets day-by-day 2026-10-26~28 implementation and true runnable exit criteria.
- [GAP_MATRIX.md](GAP_MATRIX.md) tracks every originally planned feature against VERIFIED implementation; no silent scope removal.
- [LISTING_PREP.md](LISTING_PREP.md) contains only pre-publication product-listing materials and release conditions.
- Early safety and repeatable smoke/unit tests are mandatory; advanced security and reliability acceptance take place **before** handling real customer data and selling/hosting, not after.
- Current phase is plans only; code/demo/customer payments are NOT yet present.
