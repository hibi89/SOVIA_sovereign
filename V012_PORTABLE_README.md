# SOVIA Audit Lite 0.12.0-beta: strictly separate synthetic-only candidate

NOT signed, customer-released, privacy-certified, native n8n-integrated, or production deployed.

New nine-member ZIP: version 0.12.0-beta, format SOVIA_PORTABLE_V012_V1, fixed prefix SOVIA-V012/, new verifier and detached SHA-256 transport checksum. Neither checksum nor manifest proves publisher identity. Old v0.10/v0.11.2 binaries, source and hash baselines stay unchanged.

Use ONLY sovia_audit_v012.py for corrected fractional UTC BURST_TOOLS findings. The packaged legacy sovia_audit.py is an unchanged strict validation dependency and retains its historical bug; it must not be advertised as corrected. The source-only printable preview uses the new candidate.

SQLite history v2, via sovia_history_v012.py, keys SHA-256(engine-version + NUL + normalized-source-hash) and stores only version/metadata hashes, finding counts and import time. It REFUSES existing SQLite history schema v1 and supports no automatic migration, mixed-version import, or deletion. Source-derived report_id can still match older risk analyses; compare engine-version-scoped identity, not old report_id alone.

Python 3.11+ standard library, trusted source checkout. Prepare dist and use fresh paths:

    python -I -B build_portable_v012.py --output dist/SOVIA-Audit-Lite-0.12.0-beta.zip
    python -I -B verify_portable_v012.py --archive dist/SOVIA-Audit-Lite-0.12.0-beta.zip --sha256-file dist/SOVIA-Audit-Lite-0.12.0-beta.zip.sha256 --extract-to NEW-V012

The NEW-V012 extraction root contains the nine member files directly. From inside it, create output files OUTSIDE the installed folder:

    python -I -B sovia_audit_v012.py --input examples/demo_temporal_boundary.json --html-output ../boundary.html --json-output ../boundary.json --synthetic-only
    python -I -B sovia_history_v012.py import --db ../ledger-v2.sqlite3 --input examples/demo_temporal_boundary.json --synthetic-only
    python -I -B sovia_history_v012.py status --db ../ledger-v2.sqlite3
    python -I -B sovia_history_v012.py backup --db ../ledger-v2.sqlite3 --output ../backup-v2.sqlite3
    python -I -B sovia_history_v012.py restore --input ../backup-v2.sqlite3 --db ../restored-v2.sqlite3

Fractional boundary fixture: three fabricated events, zero burst findings. Five-rule fixture: three events, five findings. Synthetic-only is an unverified operator assertion and heuristic PII matching does NOT prove data sanitization or authorization. No supported real n8n extraction, data retention agreement, physical owner Windows/Defender/browser/print check, digitally signed installer, PDF font certification or customer sale.

Before commercial use: real authorized n8n source/version, privacy/consent, retention/support, signing, separate v0.12 user-PC acceptance and explicit owner approval.
