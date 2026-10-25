# SOVIA Audit Lite P1 v0.3.0 — quickstart
Status: local synthetic MVP proof, NOT a commercial/production security service.
Python >=3.10 expected, **tested 3.13.5 on Linux**; Python standard library only, no external API or paid services.

## Windows (PowerShell)
1. In the folder containing sovia_audit.py, ensure Python 3 is installed.
2. Run with unused report names:
    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json
3. Open report.html in a local browser. Review report.json if a machine-readable report is needed.
4. Run tests:
    py -3 -m unittest discover -s tests -q

Linux/macOS: use python3 instead of py -3. If running from GitHub, use the feature/p0-audit-core branch; main may have documents only until integration.

## Demonstration and schema
examples/demo_five_rules.json contains 3 fictional events yielding 5 findings and 5 different rules. examples/demo.json contains 2 events yielding 3 rule findings. Input: one UTF-8 JSON document with schema_version "1.0", policy object, events array. Each event requires event_id, occurred_at_utc (with timezone), agent_id, run_id and tool_name. Optional target, destination_domain, permission_asserted, outcome, source_pointer. Policy: allowed_tools, approved_destinations, sensitive_targets, optional max_tool_calls_per_minute integer 1..1000. Missing policies are explicitly unknown. A present pointer is unverified, not proof.

## Output overwrite/compatibility
Output files must not already exist. Reuse creates a safe error (exit 2) and NEVER overwrites prior reports. Choose distinct new report paths per run. Output parent folders must exist. Files are staged locally and linked exclusively; requires hard-link-capable filesystem. On unsupported filesystems (e.g. some removable drives), generation fails safely rather than weakening the no-clobber behavior. Windows NTFS behavior is still UNVERIFIED. Single file publication is atomic; HTML+JSON pair uses best-effort rollback on failure and is NOT an all-or-nothing power-loss transaction.

Input is limited to 1 MiB, 1000 events, 16 JSON levels; imported instructions never executed. Unknown fields such as raw_prompt are not carried into reports; do not interpret this as full PII scanning. Logs are user-supplied, origin and completeness independently unverified. No real client/customer data before approved P2 safeguards. Report does not certify compliance or guarantee zero incidents.

## Tested baseline
2026-10-26 KST: Python 3.13.5 local, 40/40 unit cases, 3-event / 5-finding CLI case, isolated same-machine -I -B execution. Chromium rendered HTML content and confirmed tables; actual file:// open was blocked by this test environment. CSV/PDF/SQLite/local dashboard/n8n/installer and real customer verification remain P2.
