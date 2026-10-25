# SOVIA original blueprint versus actual implementation
Updated 2026-10-26 KST. Evidence: source commit `a1c566921a626d4f4c24fb4eb8b2c405ff67db8e` on `feature/p0-audit-core`, 12 local unit tests PASS and 0 FAIL, one full CLI smoke PASS. Status is based on execution, not files existing only.

| Original requirement | 72h MVP priority | Verified status | Missing / next stage |
|---|---|---|---|
| One shared offline local core | Mandatory | DONE_VERIFIED (CLI only) | Packaging, persistence P2 |
| Structured JSON ingest / bound validation | Mandatory | DONE_VERIFIED for synthetic JSON | More adversarial and real sanitized input tests |
| Event normalization UTC + evidence IDs | Mandatory | PARTIAL: IDs, UTC, source pointers | Full event timeline; ingestion provenance verification |
| At least three explainable policies | Mandatory | DONE_VERIFIED: 3 rules | Burst, missing evidence → next/P2 |
| Coverage unknown rather than false 'safe' | Mandatory | PARTIAL | Distinguish pointer given versus genuine independent verification |
| Korean HTML report | Mandatory | DONE_VERIFIED: report generated | Independent browser rendering / print |
| One-command CLI with synthetic demonstration | Mandatory | DONE_VERIFIED locally | Clean Windows environment reproduction |
| 12 executable smoke/unit tests | Mandatory | DONE_VERIFIED locally | CI, more negative tests |
| JSON machine-readable export | Helpful | DONE_VERIFIED locally | Formal versioned export contract |
| CSV input/export | Stretch | DEFERRED | P2 |
| PDF output | Stretch | DEFERRED | P2 |
| SQLite history/dedup | Stretch | DEFERRED | P2 |
| Local dashboard/browser UI | Stretch | DEFERRED | P2 |
| Sanitized n8n (candidate) integration | Commercial | PLANNED | P2 customer pilot gate |
| Installer, deletion, backup/restore, false positive review | Commercial | PLANNED | P2 before sale |
| Cloud SaaS tenant isolation/auth/billing/alerts | Future | PLANNED | P4 after proven demand and approval |
| Private offline/no-egress install | Future | PLANNED | P5 customer-backed |
| Hybrid/advanced governance/SOC | Future | DEFERRED | P6/P7 demand gated |

No requirement from the original blueprint has been silently removed. 'DONE_VERIFIED' here refers only to the tested synthetic development environment, not security certification or customer readiness.
