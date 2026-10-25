# SOVIA Audit Lite — offline quickstart (synthetic-only)
Status: feature branch prototype, NOT a commercial-ready or certified audit product. Requires Python 3.10+ and no third-party packages. No network/API calls are made by the Python code.

## Run
From the repository root:
```powershell
py -3 sovia_audit.py --input examples/demo.json --output report.html --json-output report.json
py -3 -m unittest discover -s tests -v
```
On Linux/macOS substitute `python3`. Open the generated `report.html` locally in a browser. The CLI writes only the files specified by the user; output folder must already exist. Never point an output at the input file.

## Example input contract (schema_version 1.0)
```json
{
  "schema_version": "1.0",
  "policy": {
    "allowed_tools": ["approved_lookup"],
    "approved_destinations": ["internal.example"],
    "sensitive_targets": ["client_records"]
  },
  "events": [{
    "event_id": "evt-001",
    "occurred_at_utc": "2026-10-26T00:01:00+09:00",
    "agent_id": "demo-agent",
    "run_id": "demo-001",
    "tool_name": "approved_lookup",
    "target": "public_docs",
    "destination_domain": "internal.example",
    "permission_asserted": true,
    "outcome": "ok",
    "source_pointer": "synthetic:1"
  }]
}
```
The source file is capped at 1 MiB, maximum 1,000 events, 16 levels of JSON nesting. Required per-event fields: event_id, occurred_at_utc with timezone, agent_id, run_id, tool_name. Domain is hostname only. Unknown log fields are excluded from normalized outputs; raw prompts are not copied. Input never executes tool calls.

## Rule interpretations and limitations
- UNAUTHORIZED_TOOL: tool name not listed in explicitly provided allowed_tools.
- UNAPPROVED_DESTINATION: supplied destination not in explicitly provided approved_destinations.
- SENSITIVE_ACCESS: event target matches supplied sensitive_targets and permission_asserted is not explicitly true.
- Missing policy lists produce UNKNOWN coverage, not a pass; missing destination/source pointer is noted as a coverage limit.
- Findings are rule matches against a supplied **unverified synthetic event feed**, not independent verification of a real system or factual evidence integrity.
- HTML content is escaped, but input should contain only synthetic / authorized sanitized material; full PII/secret scanning and commercial incident validation are not complete.
- Current exports are HTML and JSON only. No PDF, CSV, SQLite, dashboard, real agent connector, installer, or live monitoring.
- Do not claim zero leaks, certified compliance, production-readiness, or 24/7 protection.

## Test evidence
On 2026-10-26 KST: `python -m unittest discover -s tests -v` → **12 passed, 0 failed**; `python sovia_audit.py --input examples/demo.json --output report.html --json-output report.json` → **2 synthetic events, 3 findings**, rules above. Executed in a local isolated runtime against files whose Git blob SHAs match the files committed to the feature branch. Clean Windows install, independent GitHub CI and browser rendering remain UNVERIFIED.
