# P1 verified MVP versus original blueprint — 2026-10-27 checkpoint

Scope: \`hibi89/SOVIA_sovereign\` active \`develop\`, original \`REQUIREMENTS.md\`, \`ARCHITECTURE.md\` and \`MVP_72H.md\`. A status of **source verified** means code and automated synthetic tests exist, NOT that the owner's PC, real customers, official integrations or production work.

## Decision: stop rebuilding MVP and focus on missing deliverable gates

The 72-hour P1 minimum was **>=3 deterministic findings, structured JSON, evidence/unknown, Korean HTML, offline CLI and repeatable test**, not a signed or saleable app. All those paths exist and are covered by 4-job CI and portable extraction smoke. Five rules, CSV import/export, optional PDF, local SQLite, backup/restore, dashboard and portable selfcheck exceed the P1 minimum.

### Original R1–R9 inventory

| Requirement | Real code / evidence | Status and remaining gap |
|---|---|---|
| R1 bounded sanitized structured import | \`sovia_audit.py\`, \`sovia_csv_input.py\`, strict caps and adversarial tests | **SYNTHETIC PASS**; real sanctioned source not verified |
| R2 normalized canonical event/timestamp | \`sovia_audit.evaluate\`, UTC, metadata and pointer | **SYNTHETIC PASS**; original proposed \`principal_id/observed_at/action_kind\` not fully modeled |
| R3 explainable five rules | \`sovia_audit.evaluate\`, 5-rule fixture; tests | **SYNTHETIC PASS**; real-world false positive/negative calibration pending |
| R4 report timeline/evidence/limits | \`sovia_audit.render_html\`, JSON and CSV | **SYNTHETIC PASS**; evidence source pointers not authenticated |
| R5 HTML/PDF/JSON/CSV | \`sovia_audit.py\`, \`sovia_pdf.py\` (optional ReportLab/font) | HTML/JSON/CSV synthetic CI PASS; **PDF optional and Windows Korean visual UNVERIFIED** |
| R6 offline, explicit purge, no-persist option | \`sovia_history.py\` opt-in purge/backup; \`sovia_ephemeral_diagnostic.py\` source-only aggregate no-report-file CLI | **NEW source-only implementation**; OS/shell logs and owner offline review NOT verified |
| R7 sample/demo/CLI/tests | \`examples/\`, \`RUN_SELF_CHECK.cmd\`, \`portable_smoke.py\`, GitHub Actions | **SYNTHETIC PASS**, actual owner PC manual pending |
| R8 imported commands never run, raw prompts default excluded | schema allowlist, safe HTML escapes, sanitized n8n adapter | **SYNTHETIC PASS**, upstream real PII redaction and consent unverified |
| R9 version/schema/limits | \`sovia_audit.VERSION/SCHEMA\`, portable manifest, docs | **PARTIAL**: core/version/package branding harmonization and final signed release pending |

### First 3 P2 priorities based on blocking real use

1. **Supported genuine n8n source, legal authorization and sanitization evidence (BLOCKED without independently permitted test data).** Synthetic key probes/adapter claims are not actual API compatibility or legal consent. Require owner-approved data provenance, installed version, human review and privacy negative tests first. Do not connect APIs by guesswork.
2. **Owner physical Windows clean-install, Korean browser report and optional PDF/Defender/SmartScreen acceptance (MANUAL PENDING).** Follow \`OWNER_WINDOWS_ACCEPTANCE.md\` and \`PORTABLE_README.md\`. CI Windows is not owner's Windows.
3. **P2 delivery packaging/format/support contract and retention (PARTIAL).** \`sovia_guarded_export.py\` is opt-in source only; the v0.10 unsigned portable ZIP excludes it. Output quotas, support/retention, multi-file crash consistency, and supported environment must be explicitly agreed before sale. Signed release, real listing and production require owner approval.

## What is not MVP and must not stall P1 acceptance

Cloud tenancy, auth, billing, alerts, HA, Docker Private, NAS compatibility, deep third-party integration and enterprise evidence certification are **P4+ proposals**, not proof that the offline P1 MVP is incomplete.

## New feature this checkpoint: aggregate no-report-file diagnostic

\`\`\`powershell
py -3 -I -B sovia_ephemeral_diagnostic.py --input examples/demo_five_rules.json --ack-sanitized-source
\`\`\`

Prints only summary event count, findings, allowlisted rule/severity counts and coverage limit count. It does **not** create output reports, SQLite DB or temporary input fixtures or send an API request. It still reads a local file. OS logs, shell redirection, external process observation and filesystem metadata cannot be ruled out; do not claim secure deletion or total absence of system traces. It is a **source-only helper**, not included in the existing v0.10 ZIP and not independently certified. No real customer input used in development.

## Performance and release truth

Last confirmed source baseline \`develop\` before this branch: \`d9820a61fe5db0b0b4624ee816bf0d59096114bb\` with GitHub Actions \`40479042113\` success (includes PR #34 writer ordering integration with PR #35). Test count and final SHA **must be refreshed after PR CI and integration**. No Vercel/Production URL, published signed installer, real customer source, legal privacy certification or commercial approval.
