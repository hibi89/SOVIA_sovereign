# SOVIA Audit Lite 0.12.0-beta: strictly separate synthetic-only candidate

NOT signed, customer-released, privacy-certified, native n8n-integrated, or production deployed.

New thirteen-member ZIP: version 0.12.0-beta, format SOVIA_PORTABLE_V012_V1, fixed prefix SOVIA-V012/, new verifier and detached SHA-256 transport checksum. Neither checksum nor manifest proves publisher identity. Old v0.10/v0.11.2 binaries, source and hash baselines stay unchanged.

Use ONLY sovia_audit_v012.py for corrected fractional UTC BURST_TOOLS findings. The packaged legacy sovia_audit.py is an unchanged strict validation dependency and retains its historical bug; it must not be advertised as corrected. The source-only printable preview uses the new candidate.

SQLite history v2, via sovia_history_v012.py, keys SHA-256(engine-version + NUL + normalized-source-hash) and stores only version/metadata hashes, finding counts and import time. It REFUSES existing SQLite history schema v1 and supports no automatic migration, mixed-version import, or deletion. Source-derived report_id can still match older risk analyses; compare engine-version-scoped identity, not old report_id alone.

Python 3.11+ standard library, trusted source checkout. Prepare dist and use fresh paths:

    python -I -B build_portable_v012.py --output dist/SOVIA-Audit-Lite-0.12.0-beta.zip
    python -I -B verify_portable_v012.py --archive dist/SOVIA-Audit-Lite-0.12.0-beta.zip --sha256-file dist/SOVIA-Audit-Lite-0.12.0-beta.zip.sha256 --extract-to NEW-V012

The NEW-V012 extraction root contains the thirteen member files directly. From inside it, run the **one-command minimum working unit** into a NEW directory OUTSIDE the install folder (Python 3.11+ stdlib, no web UI required):

    python -I -B sovia_mvp_v012.py --input examples/demo_five_rules.json --output-dir ../sovia-mvp-output --synthetic-only

Three files appear in the new folder: `report.html` (basic front end), `report.json` (structured audit result), `history.sqlite3` (versioned metadata ledger). The five-rule fixture yields three events and five findings. Reuse neither output folder nor existing files; the tool never overwrites. An interrupted run can leave an incomplete *new* output folder; rerun using a different new folder. `--synthetic-only` is an unverified claim, NOT authorization to load real customer data.

**P2 synthetic n8n metadata contract (not native n8n support):** The same single command accepts the bundled fabricated, already-sanitized `sovia.n8n_sanitized.v1` fixture with a separately supplied allowlisted policy. This converts strictly checked metadata into canonical SOVIA events in an ephemeral local staging folder and then uses the corrected v0.12 engine and history ledger:

    python -I -B sovia_mvp_v012.py --source-format n8n-sanitized --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --output-dir ../sovia-n8n-demo --synthetic-only

The output inventory is the same three files (`report.html`, `report.json`, `history.sqlite3`), with no canonical intermediary in final output. Temporary canonical staging is not securely erased and OS/filesystem traces may remain; do not pass original live n8n logs, tokens or customer data. This does not validate an installed n8n version, upstream redaction, provenance or customer authorization. The `--source-format n8n-sanitized` flag requires `--policy`; canonical mode explicitly rejects it. Inputs are never overwritten.

Individual expert CLI commands still work for debugging and backups:

    python -I -B sovia_audit_v012.py --input examples/demo_temporal_boundary.json --html-output ../boundary.html --json-output ../boundary.json --synthetic-only
    python -I -B sovia_history_v012.py import --db ../ledger-v2.sqlite3 --input examples/demo_temporal_boundary.json --synthetic-only
    python -I -B sovia_history_v012.py status --db ../ledger-v2.sqlite3
    python -I -B sovia_history_v012.py backup --db ../ledger-v2.sqlite3 --output ../backup-v2.sqlite3
    python -I -B sovia_history_v012.py restore --input ../backup-v2.sqlite3 --db ../restored-v2.sqlite3

Fractional boundary fixture: three fabricated events, zero burst findings. Five-rule fixture: three events, five findings. Synthetic-only is an unverified operator assertion and heuristic PII matching does NOT prove data sanitization or authorization. No supported real n8n extraction, data retention agreement, physical owner Windows/Defender/browser/print check, digitally signed installer, PDF font certification or customer sale.

Before commercial use: real authorized n8n source/version, privacy/consent, retention/support, signing, separate v0.12 user-PC acceptance and explicit owner approval.
