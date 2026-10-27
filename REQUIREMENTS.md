# SOVIA product requirements (PRD)

> **2026-10-28 OWNER INTEGRATION PRIORITY:** Keep SOVIA an independent retrospective agent audit product. **First-party Lightning Azent (LA)** is now the primary engine integration target; n8n/other third-party adapters are optional later. LA execution integration, pre-execution risk checks and in-run policy checks are future work, NOT implemented or verified by present offline synthetic Audit Lite. Full cross-product architecture is recorded in the owner's PRIVATE `hibi89/HAE@main/docs/ECOSYSTEM_CANONICAL.md`; do not replicate private details in this PUBLIC repo.

Revision: 0.1 / 2026-10-25 KST
Status: approved strategic direction; detailed functional acceptance criteria are design proposals pending implementation.

## Vision
Independent evidence-based audit of AI agent behavior and policy, with a single common core that runs locally first and can later power Cloud and Private offerings. Avoid becoming a generic token/cost observability clone.

## Customer jobs
A. AI integration agency: produce a credible, repeatable post-deployment safety/audit report and optional monitoring package for clients.
B. SMB with its own AI agents: know what tools and data scopes were accessed, and receive actionable alerts without hiring a dedicated audit engineer.
C. Confidential organization: run audit locally without mandatory offsite telemetry or raw-document export.

## MVP: Audit Lite (must)
R1. Import synthetic or explicitly authorized, sanitized agent execution records from one defined JSON/CSV schema; reject malformed/oversized inputs safely.
R2. Transform into typed canonical events with timestamps (UTC + locale rendering), actor/agent, run/session, action/tool, target, result, source reference, permission/policy context if present.
R3. Detect deterministic, explainable sample risks: unauthorized tool according to supplied policy, new outbound destination, sensitive-target access without asserted permission, burst of tool calls, missing evidence. Unobserved action != safe action.
R4. Provide event timeline, counts, finding severity, evidence pointer and remediation text. Severity explains rationale; no invented probabilities.
R5. Export HTML report and PDF report (where supported); machine-readable JSON/CSV; label unverified/unknown and coverage limitations.
R6. Operate offline on a developer PC without sending source logs to external AI APIs; allow data deletion and a no-persist diagnostic mode.
R7. Include synthetic fixtures, CLI, install/usage instructions, deterministic unit and integration tests and a demonstration scenario.
R8. No raw prompt/document content by default; read-only audit (never execute captured tool requests).
R9. Product identity, version and report schema; transparent limitations.

## MVP: explicit exclusions
No guarantee of zero leaks, certified compliance, legal opinions, runtime blocking, 24/7 SOC human response, NAS vendor matrix, live multi-tenant SaaS, live billing or automatic legal certification.

## After MVP: stage gates
P2 Sellable Audit Lite: supported first-party Lightning Azent (LA) event/approval provenance integration, only after feasibility and explicit authorized data review; n8n or other third-party systems are optional later adapters, reproducible import of real sanitized fixtures, installer, input guide, false-positive review, recovery, customer contract scope.
P3 Paid pilot: 1-2 real authorized customers, defined event limits/retention, incident ownership, no sensitive original logs without formal consent.
P4 Cloud: opt-in agent -> ingestion API -> queue/DB -> tenant-scoped policy engine -> dashboards, notifications, billing; privacy, rate limits, backup/restore, delete/export, incident response required before production.
P5 Private: same core and user interface, Docker/offline local database, disconnected license/update/install/restore workflows, local alerts, explicit support boundaries and platform certification matrix.
P6 Hybrid and expanded integrations only on proven demand.
P7 Advanced governance: evidence chain, approvals, controls mapping, audit export and optional high assurance controls subject to professional review.

## Non-functional
Deterministic testability; import idempotency; bounded CPU/memory use; explicit partial coverage; no cross-tenant access; structured redacted logs; no mandatory LLM; safe failure/rollback; accessibility of dashboard; Korean report first, English later.

## Success criteria
MVP = import/test/review/export work on synthetic fixtures with declared passed tests. Commercial-ready requires verified real supported environment, agreements, access isolation, backup/restore, and validated support/price. Production-ready requires end-to-end live checks; a passing build alone is insufficient.


## 2026-10-26 MVP-first execution scope clarification (takes precedence for P1 timebox)
The R1-R9 above remain the **target Audit Lite full blueprint**, not a claim that every item fits into 72 hours. User approved a first runnable subset with later gap filling, without dropping final requirements.

**P1 72-hour mandatory proof:** a local-offline end-to-end demo with one supported structured JSON schema, safe validation, canonical event parsing, at least **three** deterministic rules (unauthorized tool, unapproved destination, sensitive-target access without asserted permission), evidence ID/source pointer + rule rationale and unknown coverage, human-readable Korean HTML risk report, one documented CLI invocation and executable unit/smoke tests. No external calls or live customer data.
**Stretch if verified within time:** all 5 rules, CSV, PDF, SQLite, read-only browser UI. Stretch items can be deferred into P2 with explicit GAP_MATRIX status. At least one local report must be reproducible; no claim of "finished P1 blueprint" if stretch requirements are missing.
**P2 before selling:** fulfill the planned format/report/installer/UX/customer-relevant integration and real sanitized input validation, security and recovery gates. Prepare listing collateral as parallel DRAFT work, do not publish until owner approves and capability is verified.
Safety floor for every stage: imported log data never executed; bounded safe parsing; secrets/raw prompts excluded by default; HTML escaped; unknown events not mislabeled safe.
