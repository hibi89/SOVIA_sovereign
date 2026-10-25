# Architecture — one core, multiple deployment modes
Version 0.1 / design only / 2026-10-25 KST

## Deployment-independent architecture
SOURCE (approved JSON/CSV, later n8n/OpenTelemetry) -> ADAPTER -> VALIDATOR + REDACTOR -> NORMALIZER -> EVENT STORE -> POLICY RULES -> FINDING + EVIDENCE -> REPORT/ALERT -> DASHBOARD/EXPORT.

Boundaries:
- Ingestion never executes imported commands. Treat file contents and text prompts as untrusted bytes.
- Policies are deterministic, versioned and run on canonical event objects; reports link to event IDs and policy versions.
- Evidence completeness is a first-class property: observed / missing / unknown. A hash alone is not proof of factual completeness.
- Local mode runs with outbound-network access not required.

## Suggested code layout (future; does not mean code exists)
src/sovia/domain/{events,policies,findings,evidence}.py
src/sovia/adapters/{file_json,file_csv,n8n,otel}.py
src/sovia/services/{ingest,normalize,evaluate,report}.py
src/sovia/storage/{sqlite,postgres}.py
src/sovia/interfaces/{cli,api}.py
web/ (only once dashboard work begins)
tests/{unit,integration,e2e,security,fixtures}/
docs/ (deployment and commercial guides)
Only add directories as they receive real code.

## Canonical data contracts (proposal)
Event: schema_version, event_id (stable hash or upstream ID), tenant_id (optional in local), source_id, run_id, agent_id, principal_id (pseudonymized), occurred_at_utc, observed_at_utc, action_kind, tool_name, target_class, destination_domain (when explicitly supplied), outcome, policy_context, payload_digest, source_pointer.
Finding: finding_id, rule_id, rule_version, severity, event_ids[], rationale, evidence_status, recommended_action, created_at_utc, resolution_status.
Report: report_id, engine_version, policy_set_digest, input_count, valid_count, rejected_count, time_window, findings[], coverage_limits, generated_at_utc, report_digest.
Do not persist unrestricted prompts or client documents in the canonical schema.

## Storage separation
Local Lite: SQLite within a user-selected local directory; deterministic migrations, export, explicit purge and backup tests. Separate original import staging from normalized store.
Cloud: managed Postgres with per-tenant isolation enforcement in DB and API; object store for bounded exports, worker queue for analysis and retry. Never use user-supplied tenant ID as sole authorization.
Private: customer-controlled Postgres/SQLite as appropriate; local-only identity, no mandatory telemetry, export only by customer action.

## Ingest and reliability
- Idempotency: deduplicate on stable source+event ID and content digest, report collisions. Store raw source pointer not raw text by default.
- Reject/truncate oversize inputs before parsing; cap rows/files, validate timestamps and policy schema.
- Worker: bounded batch -> transactional commit -> checkpoint -> resume; on unexpected failure produce partial status and no false success.
- Cloud retry: backoff, dead-letter queue, per-tenant quota, cost caps, health monitoring, replay tests.
- Missing heartbeat is an ingestion health alert, not a claim of a security incident.

## Alert routing
Cloud customer: severity threshold + dedupe + cooldown -> email/webhook, delivery states and retries. Operator receives infrastructure incidents, not private case data by default.
Private: local notifications; air-gapped deployment never promises offsite phone notification. Optional outbound bridge only with explicit signed data-flow approval.

## Deployment modes and dependency rule
Audit Lite: local CLI + local UI, offline and zero monthly server fee.
Cloud: hosted gateway/worker/UI, subscriptions, tenant/role/auth separation.
Private: packaged container offline-capable, customer managed; updates and support are optional controlled processes.
One versioned domain/policy engine; environment adapters provide identity, persistence, notification and transport.

## Risks, anti-goals and rollout
Avoid a single central service holding confidential raw prompts; no automatic external LLM calls; do not market as legal certification or total attack prevention.
Design security review: ingestion validation, prompt injection as data, tenant isolation, event tampering detection, report reproducibility, deletion+retention, import recovery, human approvals and supplier outage.
Cloud deployment/Production URL do not exist yet; Vercel/Railway/Supabase are options, not registered projects.
