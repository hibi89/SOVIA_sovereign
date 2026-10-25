# Security minimums and deployment trust boundaries
Planning document; no security audit or service warranty has been performed.
Updated 2026-10-25 KST.

## Scope and threat model
Assets: customer event logs, tenant memberships, alert destinations, audit policies, evidence reports, service secrets. Actors: malicious upload, compromised agent/source, tenant user, operator account, adversarial prompt text. Risks: injection, parser denial of service, cross-tenant disclosure, privilege escalation, false evidence, poisoned reports, missing logs, exfiltration and notification leaks.

## Day-zero controls (cannot be deferred)
1. Source files are data, not commands; do not eval/execute imported action payloads. Only safe parsers with bounded bytes/rows/depth and deterministic schema validation.
2. Use synthetic data for development; do not check in real customer documents/prompts/tokens/.env/SQLite databases.
3. Redact sensitive payloads by default; evidence source pointers should be pseudonymized. No mandatory external LLM.
4. Report unknown coverage, missing evidence and false-positive possibilities. Preserve provenance (source, timestamp, rule version).
5. Local mode has no required outbound network calls; implement explicit deletion and user-selected storage paths.
6. Third-party library audit/locking before release; protect against path traversal and HTML/PDF injection in report export.

## Cloud production gates
Prove API authorization + database tenant isolation + cross-tenant negative tests. Enforce least privilege, encryption in transit/at rest, key rotation, rate limits/usage limits, secure logging and incident playbook. Event stores require backup restore verification and retention/erasure policy. Separate operational alert metadata from customer content. No real tenant production until those checks pass.

## Private production gates
Local account/authorization, customer-managed keys, offline capability verified at runtime, no silent telemetry or auto-update, repeatable backup/restore, signed update path where required, supported hardware matrix and ownership of alerts documented. Offline system cannot promise operator push notification.

## Responsible claims
This product assists with policy/audit inspection within observed logs; it cannot prove no breach, guarantee compliance, replace counsel, or automatically prevent actions in post-event mode. Any enterprise or regulated client requires contract/privacy review and independent assurance as requested.


## MVP-first schedule security split (2026-10-26)
Security cannot all move to the end: Day-1 floor is bounded parse, no evaluation/execution of log text, no secrets/raw prompts in repo, explicit offline operation, minimal redaction, output encoding/HTML escaping and repeatable smoke tests. Those are functional correctness boundaries of an audit product.
Post-3-day MVP but pre-first-real-customer/P2-commercial gate: malformed/adversarial file tests, import integrity and false-positive review, safe CSV/PDF exports, dependency review, privacy/contract scope, packaging install/restore/delete, customer-controlled data disposal. Any critical issue blocks selling.
Pre-Cloud/Private production: rigorous tenant isolation/RBAC, no-egress offline verification, failover/restore, alert delivery and cost controls, independent security testing as required. Detailed acceptance in TEST_PLAN.md. Unsupported is explicitly marked; do not lower stated security quality for schedule.
