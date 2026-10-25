# SOVIA Sovereign — local-first AI agent evidence audit

SOVIA Audit Lite is a **retrospective** (not real-time blocking) deterministic risk audit of supplied agent events. This repository is currently PUBLIC; only synthetic inputs and public-safe code are committed.

## Working prototype (2026-10-26 KST)
- Branch: feature/p0-audit-core (main/develop remain unpromoted).
- P1: offline Python audit with 5 policies, evidence pointers/unknown disclosure, Korean HTML risk report + UTC event timeline, optional JSON.
- P2 v0.4: optional **CSV export** for risk findings and chronological events, with UTF-8 BOM and spreadsheet formula-like cell escaping. **CSV import is not built.**
- Developer Python 3.13.5 tests: **54 PASS / 0 FAIL**; local synthetic four-output smoke passed and isolated same-machine copy passed.
- No required hosting, API key or paid dependency.

## Run (feature branch)
    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json --findings-csv findings.csv --events-csv events.csv
    py -3 -m unittest discover -s tests -v

All output filenames must be unused. Read QUICKSTART.md for full schema and limits. Download/checkout the feature branch rather than expecting runnable code on main.

## Delivery stages / claims
P1 local proof done; P2 CSV export verified locally; PDF, CSV ingest, SQLite, local GUI, integration with real sanitized logs, clean Windows installation and commercial privacy/security remain incomplete. Cloud, Private, Vercel deployment, public site, sale and certifications not present. Never import original customer logs without explicit authorization and P2 data controls.

## Continue
Message: [소비아소버린 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. Read current HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → code/tests on live branch. Verify SHA and advance next unblocked blueprint gap.
