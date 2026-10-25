# Blueprint-versus-shipped feature gap matrix
Baseline 2026-10-26 KST; nothing below is implemented yet. This is the live comparison between the original SOVIA final architecture and the actual released slice. Update per meaningful commit with evidence SHA, tests and status.

States: PLANNED / IN_PROGRESS / DONE_VERIFIED / PARTIAL / BLOCKED / DEFERRED (reason+phase). Never mark a mock screenshot as functional.

| Requirement from original blueprint | Day-3 MVP minimum | Current verified state | Gap-fill phase / gate |
|---|---|---|---|
| Offline common canonical schema + audit core | Required | PLANNED | P1 Day 1 |
| Structured JSON intake + constraints | Required | PLANNED | P1 Day 1 |
| Deterministic rules + explanations | >=3 required, 5 target | PLANNED | P1 Day 2 then P2 |
| Evidence IDs and explicit unobserved limits | Required | PLANNED | P1 Day 2 |
| HTML Korean risk report | Required | PLANNED | P1 Day 2-3 |
| Reproducible one-command demo + actual test results | Required | PLANNED | P1 Day 3 |
| CSV adapter | Stretch | PLANNED | P1 stretch / P2 |
| PDF report | Stretch or print-to-PDF | PLANNED | P1 stretch / P2 hard gate |
| SQLite ingestion/history | Stretch | PLANNED | P2 |
| GUI/local dashboard | Stretch | PLANNED | P2 |
| Sanitized genuine n8n (candidate) adapter | No | PLANNED | P2 pilot gate |
| Packaged install/restore/delete | No | PLANNED | P2 commercial gate |
| Cloud tenants/auth/billing | No | PLANNED | P4 funded gate |
| Cloud automatic notifications and operator command center | No | PLANNED | P4 funded gate |
| Private air-gapped packaging | No | PLANNED | P5 customer-backed gate |
| Hybrid, real-time blocking, expanded connectors, SOC | No | DEFERRED | P6-P7 need validated demand |

## Change policy
Any feature not in the day-three working slice must be tagged; do not delete or downplay the original final design. Only customer evidence or explicit owner approval may permanently remove a final feature. A commercial-ready label requires independent gates in REQUIREMENTS/SECURITY/TEST_PLAN.
