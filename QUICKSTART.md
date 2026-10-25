# SOVIA Audit Lite v0.2.0 — synthetic offline quickstart
Status: local source prototype on feature/p0-audit-core. Requires Python 3.10+ by design (actually tested Python 3.13.5); Python standard library only. No paid API/hosting. Do NOT use real confidential logs until P2 privacy/retention/contract gates.

## Run 5-rule example
From the root of the feature branch, run:

    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json
    py -3 -m unittest discover -s tests -q

Linux/macOS: substitute python3 for py -3. Open local report.html. If desired, the simpler examples/demo.json produces 2 events and 3 findings. Do not set output path equal to input path. Output directories must already exist.

## Event JSON contract 1.0
Top level object: schema_version = "1.0"; policy object; events array (<=1000, <=1 MiB file, <=16 JSON nesting). Each event requires event_id (unique), occurred_at_utc (timezone), agent_id, run_id, tool_name. Optional target, destination_domain (hostname only), permission_asserted (boolean/null), outcome, source_pointer. Raw prompts and unknown event fields omitted from normalized output, not executed. See examples for complete format.

Policy keys: allowed_tools, approved_destinations, sensitive_targets (lists of exact strings; absent policy => unknown) and optional max_tool_calls_per_minute (integer 1..1000). Five rules:
1. UNAUTHORIZED_TOOL — not in allowed_tools.
2. UNAPPROVED_DESTINATION — provided hostname not in approved_destinations.
3. SENSITIVE_ACCESS — target in sensitive_targets with permission_asserted not explicitly true.
4. BURST_TOOLS — number of events from same agent+run within a trailing 60 seconds exceeds configured maximum; unconfigured => unknown, no alert.
5. MISSING_EVIDENCE — source_pointer missing/empty.

Risk findings contain rule ID/version, severity and reason, event ID, source pointer and human review advice. Provided source pointers are labeled POINTER_PROVIDED_UNVERIFIED, NOT externally verified. Report has UTC-sorted event timeline. JSON contains normalized_policy_sha256, a hash of canonicalized events+policy, **not the original file SHA-256**. This only diagnoses observed supplied data, never proves absence of attacks or compliance.

## Validation evidence and limitations
2026-10-26: local Python 3.13.5, 29 unit tests PASS, 0 FAIL, five-rule CLI 3 events / 5 findings. Clean Windows install, browser UI, PDF/CSV/SQLite, persistence, customer adapters, SaaS/Private, real log validation, install/backup/recovery and commercial security gates remain NOT_DONE / UNVERIFIED. HTML escapes content, but it is not a comprehensive PII/secret scanner; use synthetic inputs.
