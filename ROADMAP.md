# Delivery roadmap / low cash to enterprise evolution
Date basis: 2026-10-25 KST; all dates are targets, not completion promises.
Prioritize verifiable end-to-end operation over attractive mockups.

## Time-boxes and gates
| Phase | Target window | Deliverables | Exit criteria | Cash gate |
|---|---|---|---|---|
| P0 Foundation | Oct 25-26 | Repo, policies, ADRs, specs, branches, issue backlog | Docs, owner links, commit/permissions verified | 0 KRW |
| P1 3-day functional MVP | Oct 26-28 | Local importer, canonical model, 5 deterministic checks, CLI, HTML/PDF report, synthetic tests | Testable demo and exact pass/fail evidence | 0 KRW target |
| P2 Sellable local Lite | Oct 29-Nov 8 | Supported real integration (n8n candidate), polished local UI, scrubbed fixtures, docs, installer, error recovery | Non-synthetic sanitized input test, security smoke checks, report accuracy | 0-50k KRW discretionary cap pending approval |
| P3 Market validation | Nov 2-Nov 22 overlapping P2 | Free demo, technical content, remote outreach, 10-15 leads, pilot offer | Real objections, 1+ willing-to-pay customer, no unsupported claims | No ads initially |
| P4 Cloud alpha | After paid signal, ~4-8 weeks | Tenant auth/isolation, event cap, reliable queue, alert, dashboard, billing plan | Isolation tests, replay/restore, cost limits, end-to-end live smoke | Only after funded/approved |
| P5 Private pilot | After contracted demand, ~3-6 weeks additional | Docker/offline package, local alert, no-egress test, offline upgrade/restore | Air-gapped reproducible install, customer data kept local, support SLA scoped | Contract/funding gate |
| P6 Productized SaaS | After retention proof, 2-4 months | Onboarding, integrations, health SLO, recurring payment, audit retention, billing, docs | Real customer operating KPIs and recovery evidence | Revenue-backed |
| P7 Enterprise maturity | Customer-led | Hybrid relay, advanced approvals/evidence, deeper controls, external audits/certification where needed | Verified scope and expert signoff | Quote-driven |

Dates after P3 deliberately conditional; no blanket deadline for an unvalidated B2B platform. Overlap research with building, but do not skip security minimums for external customer data.

## Stage-by-stage work breakdown
P0: verify GitHub visibility/branch/auth -> create docs/branches -> make work issues -> establish handoff.
P1: schema+fixtures -> importer -> five policy rules -> evidence+report -> CLI -> deterministic tests -> demo acceptance.
P2: first supported agent integration -> local UI -> install/export/delete -> safety testing -> pricing demo package.
P3: target agency/SMB interviews -> free local demo -> paid scope statement -> measure conversion and hours of work -> decide GO/PIVOT.
P4: multi-tenant auth/RBAC/RLS -> queues -> budget quotas -> alert delivery -> backups -> real deployment smoke -> terms/billing.
P5: offline packaging -> no outbound network tests -> customer-owned backups -> licensing and updates -> restricted hardware matrix.
P6: self-service setup, billing lifecycle, retention, monitoring, cost optimization, customer support playbook.
P7: integrations driven by contracts; do not claim regulatory certification without external verification.

## Status standard
Planned != implemented. Mark DONE only after commit + exact test evidence. GitHub push != deployed. Deployed != production function verified. Public-facing production is NOT_APPLICABLE until configured. Always document blocked dependencies and approval gates.

## Key performance gates
- Local: measurable precision/false-positive rate against a labeled synthetic+authorized sanitized fixture set.
- Commercial pilot: at least one actual customer willing to pay; service time and support burden logged.
- SaaS: tenant isolation proof, safe deletion, a restored backup, alert success/failure replay, customer monthly spend limit and billing correctness.
- Private: offline-first install and no-egress verification; not every NAS model supported by default.
