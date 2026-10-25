# SOVIA Sovereign — local-first AI agent evidence audit

SOVIA Audit Lite is a **retrospective** (not real-time blocking) deterministic risk audit of supplied agent events. This repository is currently PUBLIC; only synthetic inputs and public-safe code are committed.

## Working prototype (2026-10-26 KST)
- Branch: feature/p0-audit-core (main/develop remain unpromoted).
- P1: offline Python audit with 5 policies, evidence pointers/unknown disclosure, Korean HTML risk report + UTC event timeline, optional JSON.
- P2 v0.5: optional **CSV export** for risk findings and chronological events, with UTF-8 BOM and spreadsheet formula-like cell escaping. **CSV source import is now built (v0.6) with a separate JSON policy; genuine customer format validation is pending.**
- Developer Python 3.13.5 tests: **66 PASS / 0 FAIL**; local synthetic four-output smoke passed and isolated same-machine copy passed.
- No required hosting, API key or paid dependency.

## Run (feature branch)
    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json --findings-csv findings.csv --events-csv events.csv
    py -3 -m unittest discover -s tests -v

All output filenames must be unused. Read QUICKSTART.md for full schema and limits. Download/checkout the feature branch rather than expecting runnable code on main.

## Delivery stages / claims
P1 local proof done; P2 CSV export verified locally; SQLite, local GUI, integration with real sanitized logs, clean Windows installation and commercial privacy/security remain incomplete. Cloud, Private, Vercel deployment, public site, sale and certifications not present. Never import original customer logs without explicit authorization and P2 data controls.

## Continue
Message: [소비아소버린 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. Read current HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → code/tests on live branch. Verify SHA and advance next unblocked blueprint gap.

## PDF output (optional; tested locally)
Use `--pdf-output report.pdf` after `py -3 -m pip install "reportlab>=4,<5"`; a local Korean TTF is also required (auto-discovered or passed by --pdf-font). PDF generated with Korean text, table and event timeline and visually inspected; Windows font/install and real customer data are unverified. Read QUICKSTART.md. No packaged fonts or paid services.

P2 PDF isolated-mode hotfix a7a1c6b8e151: extracted ZIP 67 tests PASS and `python -I -B` PDF+HTML+JSON smoke PASS, still synthetic local. Handoff/STATUS contain exact evidence.

## P2 v0.6 source CSV + CI checkpoint (2026-10-26 KST)
```powershell
py -3 sovia_audit.py --input examples/demo_source.csv --policy examples/demo_policy.json --output report.html --json-output report.json
```
CSV import accepts allowlisted canonical event metadata only, never arbitrary prompt bodies. --policy JSON is mandatory for CSV, unused for original JSON input. GitHub Actions [run 40212874275](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40212874275) verified Python 3.11/3.13 each 92 tests total (82 PASS, 10 optional PDF SKIP, 0 FAIL). P2 is not sale-ready; Windows/real-data/SQLite/GUI/backup remain open. Source commit `770172baa1dfe0eb0fd4b1a63d0afead0eaf6bc2`, CI commit `5c99ca3ca1205a26b586a057874172f6607d3e19`.
