# SOVIA Sovereign — local-first AI agent evidence audit

## 2026-10-28 accelerated P2: one-command synthetic n8n-like metadata accepted

[PR #60](https://github.com/hibi89/SOVIA_sovereign/pull/60) merged into active `develop`, code SHA `58281a01a6067e4787a0ce5c47dc5b65f62f6776`. In addition to prior canonical synthetic JSON, the existing v0.12 one-command CLI supports the strict already-sanitized, fabricated `sovia.n8n_sanitized.v1` envelope plus separate policy. Python 3.11+ stdlib, offline, no UI/dependency install:

```sh
python -I -B sovia_mvp_v012.py --source-format n8n-sanitized --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --output-dir ../n8n-demo-output --synthetic-only
```

Three output files: HTML report, JSON report, SQLite v2 metadata history; 3 synthetic events/5 findings. Corrected v0.12 UTC rules and heuristic metadata/PII checks remain active; no original raw execution body or secret field accepted, intermediate canonical file staged temporarily and not published. [PR CI #40530323186](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40530323186) Windows/Ubuntu × Python3.11/3.13 4/4 SUCCESS, 847 tests discovered per job, zero failures; separately packaged 13-file v0.12 ZIP smoke succeeded. This is **NOT** native n8n execution/API integration, actual version proof, source authorization, full PII clearance or a commercial release; no real customer data. See [MVP_20261028_RUNBOOK.md](MVP_20261028_RUNBOOK.md) and [HANDOFF.md](HANDOFF.md).

---


## 2026-10-28 deadline: one-command **minimum working unit now integrated on develop**

The **source/ZIP synthetic-only v0.12 MVP** is callable with one command: `python -I -B sovia_mvp_v012.py --input examples/demo_five_rules.json --output-dir ../sovia-mvp-output --synthetic-only`. It creates `report.html`, `report.json`, `history.sqlite3` in a fresh output directory; audit uses the corrected v0.12 UTC temporal rule. [PR #59](https://github.com/hibi89/SOVIA_sovereign/pull/59), [four-platform CI](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40526564129): Windows/Ubuntu × Python 3.11/3.13 all green, 840 discovered/job and 0 failures; clean-extracted ten-file ZIP end-to-end smoke. See [MVP_20261028_RUNBOOK.md](MVP_20261028_RUNBOOK.md). Frontend redesign and optional enhancements follow later. Real n8n/native customer inputs, verified consent, privacy review, owner Windows installation, signed release and sales remain **NOT COMPLETE**. GitHub `main` is documentation-only; use `develop` for running source.

---


## Verified working baseline — 2026-10-27 (active `develop`)

**P1 offline functional MVP is implemented and synthetically verified**: canonical JSON/CSV, five explainable risk rules, evidence/unknown limits, Korean HTML/JSON/CSV, optional PDF, SQLite metadata history, dashboard, portable 12-file offline beta and owner synthetic self-check. The latest regression at [GitHub Actions 40479432652](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40479432652) succeeded across Windows/Ubuntu × Python 3.11/3.13 (697 discovered/job, zero failures). Do not confuse GitHub-runner checks with actual owner Windows/browser/Defender/Korean PDF review, sanctioned real n8n integration or customer readiness.

**New source-only, not in v0.10 ZIP:** `sovia_ephemeral_diagnostic.py` offers aggregate read-only counts without generating report/DB files:

```sh
python -I -B sovia_ephemeral_diagnostic.py --input examples/demo_five_rules.json --ack-sanitized-source
```

The declaration is an operator acknowledgement, not authenticated consent. Shell/OS logs are not excluded. Read [MVP_BLUEPRINT_RECONCILIATION.md](MVP_BLUEPRINT_RECONCILIATION.md) and [HANDOFF.md](HANDOFF.md) for accurate R1–R9 state and next commercial gates. **No production service or signed commercial release exists.** Older paragraphs below are historical milestones and may describe features as missing that are now implemented.

---


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

## Windows CLI smoke and CI verified
In GitHub Actions [run 40213287272](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272), Ubuntu/Windows × Python 3.11/3.13 all succeeded (per-job 82 PASS, 10 optional PDF SKIP, 0 FAIL). The Windows path-alias mismatch was repaired in source commit `d204b76fdb545b32696a3d8aa97c35c1ffbb1355` with no original data loss. CI is synthetic-only; real Windows machine/PDF font and commercial gates remain pending.

## develop integration (2026-10-26)
PR [#12](https://github.com/hibi89/SOVIA_sovereign/pull/12) successfully merged tested synthetic core and P2 CSV/PDF to `develop` at `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26`. `main` remains documentation-only stable baseline by design. Future SQLite work should branch from `develop`; no public release/deployment was performed.


## P2 v0.7 optional SQLite audit history
`sovia_history.py` is separate from the stateless `sovia_audit.py` CLI. With a NEW, locally chosen DB file: `py -3 sovia_history.py import --input examples/demo_five_rules.json --db history.sqlite`. Query with `py -3 sovia_history.py status --db history.sqlite`; see [HISTORY.md](HISTORY.md) for backup, restore, purge, CSV policy support and privacy limitations. No mandatory external packages or network, no raw prompt or tool/target labels stored in the history DB, but hash/timestamp metadata is NOT fully anonymous. Tested on Ubuntu/Windows Python 3.11/3.13 (CI run 40214522381), each 115 PASS/10 PDF SKIP/0 FAIL. Customer device/real-input/installer/secure-retention gates pending. **Not sale-ready.**

## Offline P2 v0.8 history dashboard
Generate a self-contained Korean HTML dashboard from an existing v1 SQLite history, without API keys, internet, local server or JavaScript:
    py -3 sovia_history.py import --input examples/demo_five_rules.json --db sample-history.sqlite
    py -3 sovia_dashboard.py --db sample-history.sqlite --output sample-dashboard.html
    start .\sample-dashboard.html
See DASHBOARD.md for prerequisites and privacy. Output requires unused filename and exposes pseudonymized (not anonymous) metadata; don't commit it to PUBLIC repo. 2026-10-26 KST: P2 v0.8 feature/p2-offline-dashboard implements a read-only SQLite v1 to standalone Korean HTML dashboard; no local server, JS, outbound network, data write or output overwrite. Tested source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334 4/4 SUCCESS, Windows/Ubuntu x Python 3.11/3.13, each 148 discovered/138 PASS/10 optional PDF SKIP/0 FAIL. New tests 23. Not owner PC/browser visual QA, real customer records or production.

## Develop integration of v0.8 offline dashboard
PR [#14](https://github.com/hibi89/SOVIA_sovereign/pull/14) merged at SHA 1123851900aee34d1c02d2a4590c6a0b5852727d. Post-merge CI [40215946752](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215946752) 4/4 success across Windows/Ubuntu 3.11/3.13; each 138 PASS / 10 optional PDF SKIP / 0 FAIL. Original DB and main unchanged; P2 clean-install/retention/commercial security gates are next and not complete.

## P2 v0.9.0-beta portable offline package
Reproducible allowlisted ZIP of the five Python modules, offline verifier, synthetic samples and instructions. Build via python build_portable.py --output dist/SOVIA-Audit-Lite-0.9.0-beta.zip (dist must exist and output unused); verify/extract using verify_portable.py --archive ZIP --sha256-file ZIP.sha256 --extract-to NEW_DIRECTORY. See PORTABLE_README.md. CI https://github.com/hibi89/SOVIA_sovereign/actions/runs/40216762276 4/4 Windows/Linux success, each 167 PASS and 10 optional PDF SKIP, archive hash 6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3. Download CI artifact sovia-portable-beta from the run. Unsigned beta, not commercial release.


## Latest portable v0.9 develop checkpoint 2026-10-26
**LATEST INTEGRATION (2026-10-26 KST):** [PR #15](https://github.com/hibi89/SOVIA_sovereign/pull/15) merged v0.9.0-beta deterministic portable ZIP/verifier/synthetic full smoke into `develop`, merge SHA `0a16a032dc26970ba197aa8e874a22fcb2a2c0a6`. [Post-merge Actions run 40217328939](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40217328939) **4/4 SUCCESS** (Windows+Ubuntu × Python 3.11/3.13), per job 177 discovered / 167 PASS / 10 optional PDF SKIP / 0 FAIL, and full clean-extracted isolated-Python audit→SQLite→dashboard→backup/restore PASS. Tested reproducible ZIP SHA256 `6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3`. `sovia-portable-beta` downloadable from Actions artifacts, unsigned ZIP+checksum, NOT an official signed Release. **On ㄱ**: inspect newest `develop`, then start P2 owner-Windows acceptance/self-check workflow (one-command local diagnostics; sample/fresh-folder tests), optional PDF/font/visual/manual verification guidance, then real authorized data/privacy/retention/failure-handling commercial gates. Do NOT redo JSON/CSV/SQLite/dashboard/package or merge PR #15 again. `main` remains docs-only; no Production/Vercel, no owner device/customer validation or sale approval. Earlier sections are archival.


## v0.10 Windows one-click owner synthetic diagnostic
The newest 12-file v0.10 portable beta includes RUN_SELF_CHECK.cmd and owner_selfcheck.py. Verify ZIP manifest from trusted source, extract to NEW folder, double-click launcher on Windows. Creates a NEW sibling SOVIA_DIAGNOSTICS/SOVIA_SELF_CHECK_... folder containing only 3-event/5-finding synthetic audits, SQLite history/recovery, standalone dashboard and SELF_CHECK_RESULT.json. If ReportLab/Korean TTF installed, optional PDF generated for visual inspection, not automatically passed. See OWNER_ACCEPTANCE.md and PORTABLE_README.md. GitHub [CI 40218607947](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218607947) Windows Python 3.11/3.13 each 179 PASS/10 PDF SKIP and Ubuntu each 178 PASS/11 SKIP. Unsigned ZIP, not a paid release. Archive SHA256 894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b.


## v0.10 integration checkpoint (2026-10-26)
**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #16](https://github.com/hibi89/SOVIA_sovereign/pull/16) merged SOVIA v0.10.0-beta Windows one-click synthetic self-check, 12-file portable ZIP and optional Korean PDF/font diagnostic into `develop` at merge SHA `60a2ea28fed91d320211ee8f8ec594c24971d472`. [Post-merge CI run 40218991467](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218991467) **4/4 SUCCESS**: Windows Python 3.11/3.13 each 189 discovered/179 PASS/10 PDF SKIP/0 FAIL, Ubuntu 3.11/3.13 each 189 discovered/178 PASS/11 SKIP (Windows .cmd test)/0 FAIL; all four include full extracted-ZIP synthetic audit/SQLite/dashboard/recovery/self-check. Same 12-file ZIP SHA256 `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`, unsigned CI artifact `sovia-portable-beta` available. **PR integration DONE; DO NOT repeat.** On `ㄱ` next: verify latest develop HEAD and continue P2 product acceptance/privacy/retention/authorized n8n-like sanitized source or adversarial tests, prioritizing safe offline work. Actual owner's Windows PC, browser visuals, AV/SmartScreen, ReportLab+Korean TTF PDF visual, customer data and commercial/production are **NOT VERIFIED** and need owner/local evidence. `main` remains docs-only and unreleased. Earlier feature-only references are archived.

