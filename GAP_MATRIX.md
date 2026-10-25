# SOVIA blueprint-to-working gap matrix
Last update: 2026-10-26 KST. Tested implementation code commit: 2eda8c37a3ed06702aba14cb53790da3cbaf8e83, feature/p0-audit-core. Local tests 29 PASS, 0 FAIL. Evidence limited to synthetic fixtures.

| Full blueprint feature | 72h MVP | Actual verified status | Next gap/gate |
|---|---|---|---|
| Shared local audit core | Required | DONE_VERIFIED local Python | Packaging P1/P2 |
| Bounded structured JSON | Required | DONE_VERIFIED | Broader malicious inputs P2 |
| Typed UTC events and IDs | Required | DONE_VERIFIED | Provenance/real adapter P2 |
| 3 deterministic rules | Required | DONE_VERIFIED 5 total | Evaluate false positives on genuine sanitized cases |
| Tool/destination/sensitive access | Required | DONE_VERIFIED | Real-policy semantics review |
| Burst rule | Stretch | DONE_VERIFIED when threshold configured | Tune threshold per customer |
| Missing evidence pointer rule | Stretch | DONE_VERIFIED | Genuine pointer validation not done |
| Evidence states and unknown disclosure | Required | PARTIAL | Verify original evidence and coverage provenance P2 |
| Korean HTML findings + timeline | Required | DONE_VERIFIED static markup | Browser/UX visual check P1 |
| Offline CLI + JSON export | Required | DONE_VERIFIED local | Fresh machine and robust write recovery |
| Tests and reproducible five-rule demo | Required | DONE_VERIFIED local: 29 tests | Clean Windows + CI P1/P2 |
| CSV import/export | Stretch | DEFERRED | P2 |
| PDF | Stretch | DEFERRED | P2 |
| SQLite history/idempotent stored imports | Stretch | DEFERRED | P2 |
| GUI/dashboard | Stretch | DEFERRED | P2 |
| n8n/real sanitized supported connector | Post MVP | PLANNED | Commercial pilot gate |
| Installer/delete/backup/restore | Post MVP | PLANNED | P2 mandatory before sale |
| Commercial security/privacy and claims | Pre-sale | PLANNED | P2 mandatory |
| Cloud tenants/auth/billing/alerts | Conditional | PLANNED | P4 revenue-backed |
| Private air-gapped packaging | Conditional | PLANNED | P5 contracted |
| Hybrid, governance, SOC | Future | DEFERRED | P6-P7 demand validation |

No original blueprint feature removed. DONE_VERIFIED never means independent production/security certification.
