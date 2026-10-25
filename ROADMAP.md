# Delivery roadmap / zero cash to enterprise
As of 2026-10-25 KST; estimated windows and labor are planning assumptions, not guarantees. See issues for actionable tasks and STATUS.md for actual completion.

| Phase | Goal window | Engineering effort estimate | Deliverable / hard completion gate | Cash strategy |
|---|---|---|---|---|
| P0 Setup | Oct 25 | 2-5 h | Verified repo docs, issue backlog and branches | 0 KRW |
| P1 Functional MVP | Oct 26-28 | 18-30 h | Runnable local evidence demo, deterministic rules, HTML/PDF, tests | 0 KRW target |
| P2 Sellable Audit Lite | Oct 29-Nov 08 | 25-60 h | Supported sanitized real-format adapter, UI/install, privacy and recovery checks | 0-50k KRW optional with approval |
| P3 Market validation (overlap) | Nov 02-22 | 10-30 h sales/testing | 10-15 interviews/outreach, verified willingness to pay, one paid pilot goal | No paid ads |
| P4 Cloud Alpha | After paid proof, 4-8 weeks estimated | 100-220 h | Multi-tenant isolated real service, verified login/API/backup/alerts/budget/real deployment | Only revenue+approval |
| P5 Private Pilot | After signed need, 3-6 weeks estimated | 70-160 h | Offline customer-controlled install, no-egress tests, local alerts and upgrade/restore | Customer-funded/approval |
| P6 SaaS scale | Retention-dependent, 2-4 months | 100-250 h | Self-service onboarding/billing, operational SLO, runbooks, integrations | Revenue-funded |
| P7 Enterprise Hybrid | Demand-dependent | TBD by contract | Verified evidence chain, optional hybrid, independent controls mapping | Quote and signoff |

Caution: P4-P7 depend on evidence and may change radically; no unconditional full-company delivery deadline. Three-day MVP is a prototype, not a certified security product.

## Critical path
P0 -> P1 event schema (#2) -> safe ingest (#3) -> evidence rules (#4) -> report/demo (#5) -> security/QA (#11).
P2 commercial install/UI/connector (#6) follows working P1; P3 online GTM (#7) can overlap. P4 (#8) and P5 (#9) are alternative monetization deployments of the *same* core; P6/7 (#10) follow retention and contract proof.

## Spending gates and pivots
1. Do not buy hosting, domain, ads or external LLM for P1.
2. MVP built/tested locally using synthetic input; do not send customer raw documents anywhere.
3. No real client ingestion without contract, explicit data path, legal/privacy/security minimums.
4. Paid Cloud only after actual paying signal and owner-approved monthly spend cap.
5. Private support and NAS compatibility only for verified contract-backed environments.
6. At 10+ prospects without a paying signal, review offer/target and consider pivot before funding more development.

## Product release definition
- P1: runnable demonstrator, exact test commands and pass/fail numbers.
- P2: packaged repeatable real supported input path, report limitations, confidentiality handling, recovery test.
- Cloud: monitored production, tenancy tests, backup restored, alert delivery and billing check, live URL/HTTP/UI/API/console inspection, GitHub SHA matching deployment.
- Private: customer-hosted air-gapped runtime, no-egress proof, reproducible restore/update, supported platform list.
- "Done" is never inferred from plan, Git commit, CI green or cloud Ready status alone.

## Working branch and operator discipline
main baseline, develop integration, feature/p0-audit-core next development branch; on-demand feature branches for future phases. Next chat "ㄱ" resumes using HANDOFF -> STATUS -> AGENTS -> REQUIREMENTS -> code.


## AUTHORITATIVE UPDATE 2026-10-26 — MVP first, blueprint gaps second, product listing in parallel
This section supersedes any interpretation of the earlier timeline that requires completing all polished P1/R1-R9 functionality **before** the first runnable demonstration. Work remains date-targeted, NOT guaranteed to run automatically.

| Date | Milestone | Actual deliverable / acceptance | Parallel commercialization |
|---|---|---|---|
| Oct 26 (Day 1) | "it runs" | synthetic JSON -> safe canonical parse -> policy finding -> CLI/HTML output, smoke tests | headline + ideal buyer draft |
| Oct 27 (Day 2) | "it finds something useful" | >=3 evidence-based deterministic rules, healthy/risky cases, Korean risk explanation; add others if time | FAQ, offer scope, sample report outline |
| Oct 28 (Day 3) | "MVP demonstrable" | run from fresh local environment, output a usable report, actual unit/smoke results; record gap matrix | real demo screenshot AFTER working software, draft price/collateral |
| Oct 29-Nov 04 | blueprint gap filling | improve PDF/CSV/local UI/SQLite, support actual sanitized agent format; regression tests per slice | listing description/images/FAQ and checkout/revision terms |
| Nov 05-08 | sellability quality gate | install on clean PC, test bad inputs, redaction, evidence accuracy, report generation, backup/delete and integration; fix critical bugs | prepare to list; publish only when verified + owner approved |
| Nov 02-22 overlap | customer discovery | remote agency/SMB outreach and customer willingness-to-pay evidence; no assumed sales | free demo + controlled paid pilot if ready |

**P4-P7 remain original long-term plan:** Cloud only when revenue-backed and security gate satisfied; Private only when contract-backed; productized SaaS and hybrid after retention proof. Full-product 4-8 months or longer is a conditional estimate, not an MVP scope.

**Minimum Day-3 MVP:** one structured input, 3 deterministic findings, evidence + unknown status, offline CLI, Korean HTML, executable tests. Stretch: 5 rules, CSV, PDF, SQLite, local GUI. See [MVP_72H.md](MVP_72H.md) and [GAP_MATRIX.md](GAP_MATRIX.md).
**Safe prioritization:** day-zero basic guards and smoke/regression tests on every slice; deeper security/soak/recovery tests toward commercial gate. No real client secret/data or SaaS operator responsibility prior to gates.
**Pricing:** hypothesis 199,000 KRW one-time audit, not a verified price; no paid hosting or ads until evidence + approval.
