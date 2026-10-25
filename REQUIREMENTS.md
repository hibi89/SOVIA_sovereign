# SOVIA product requirements (PRD)
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
P2 Sellable Audit Lite: supported integration (n8n first candidate, only after feasibility), reproducible import of real sanitized fixtures, installer, input guide, false-positive review, recovery, customer contract scope.
P3 Paid pilot: 1-2 real authorized customers, defined event limits/retention, incident ownership, no sensitive original logs without formal consent.
P4 Cloud: opt-in agent -> ingestion API -> queue/DB -> tenant-scoped policy engine -> dashboards, notifications, billing; privacy, rate limits, backup/restore, delete/export, incident response required before production.
P5 Private: same core and user interface, Docker/offline local database, disconnected license/update/install/restore workflows, local alerts, explicit support boundaries and platform certification matrix.
P6 Hybrid and expanded integrations only on proven demand.
P7 Advanced governance: evidence chain, approvals, controls mapping, audit export and optional high assurance controls subject to professional review.

## Non-functional
Deterministic testability; import idempotency; bounded CPU/memory use; explicit partial coverage; no cross-tenant access; structured redacted logs; no mandatory LLM; safe failure/rollback; accessibility of dashboard; Korean report first, English later.

## Success criteria
MVP = import/test/review/export work on synthetic fixtures with declared passed tests. Commercial-ready requires verified real supported environment, agreements, access isolation, backup/restore, and validated support/price. Production-ready requires end-to-end live checks; a passing build alone is insufficient.
