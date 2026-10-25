# SOVIA original blueprint vs verified shipped prototype
Updated 2026-10-26 KST. P1 tested source commit 8957e872a0519dae208f49c51c848f95f35f7046, local 40 PASS / 0 FAIL. DONE_VERIFIED means synthetic development environment only.

| Original design feature | P1 MVP | Actual status | Remaining gate |
|---|---|---|---|
| Shared offline core | Required | DONE_VERIFIED (Python stdlib CLI) | Production packaging |
| 1 MiB JSON cap / 1000 events / depth 16 | Required | DONE_VERIFIED | Extreme malformed/fuzz P2 |
| Typed canonical UTC event IDs | Required | DONE_VERIFIED locally | Independent original provenance |
| Five deterministic policy rules | >=3 required | DONE_VERIFIED all five | Real false-positive review |
| Unknown/missing coverage / pointer status | Required | PARTIAL | Independent source evidence checking P2 |
| Korean HTML finding report + UTC timeline | Required | DONE_VERIFIED, Chromium set_content | External Windows file-browser open |
| JSON output / reproducible CLI | Required | DONE_VERIFIED locally | Independent device install |
| No-clobber staged outputs / rollback | P1 Day3 | DONE_VERIFIED in local tests | Non-NTFS Windows/hardlink + crash recovery |
| Unit/smoke tests | Required | DONE_VERIFIED 40/40 | Windows platform/CI review |
| Network-independent local execution | Required | DONE_VERIFIED mocked socket/isolated -I | Packet capture / real integration P2 |
| CSV input/export | Stretch | DEFERRED | P2 |
| PDF report / print-ready installer | Stretch | DEFERRED | P2 |
| SQLite history and idempotency | Stretch | DEFERRED | P2 |
| Local GUI/dashboard | Stretch | DEFERRED | P2 |
| n8n and sanitized genuine agent data | Later | PLANNED | P2 authorized integration pilot |
| Installer, retention/delete, backup/restore | Commercial | PLANNED | P2 BEFORE SALE |
| PII/secret redaction, abuse and security review | Commercial | PLANNED | P2 BEFORE SALE |
| Cloud multi-tenant auth/alerts/billing | Future | PLANNED | P4 demand + owner approval |
| Private airgapped customer deployment | Future | PLANNED | P5 contract + no-egress checks |
| Hybrid, advanced governance, SOC | Future | DEFERRED | P6/7 based on real demand |

Full blueprint is preserved; passing synthetic tests does not confer production or commercial security certification.
