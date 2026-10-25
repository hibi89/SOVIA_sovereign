# SOVIA Audit Lite — opt-in SQLite history v0.7

Scope: experimental offline metadata history on synthetic and **authorized, sanitized** records. No service, vendor SaaS, API, network or paid dependency. The original `sovia_audit.py` CLI remains completely stateless unless the separate command below is run. These are no-clobber examples: choose NEW output names.

## Quickstart (PowerShell, Python 3.11+ CI verified)

    py -3 sovia_history.py import --input examples/demo_five_rules.json --db my-history.sqlite
    py -3 sovia_history.py status --db my-history.sqlite
    py -3 sovia_history.py backup --db my-history.sqlite --output backup-01.sqlite
    py -3 sovia_history.py restore --input backup-01.sqlite --db recovered-history.sqlite
    py -3 sovia_history.py purge --db recovered-history.sqlite --all --confirm-delete

For existing databases, **make and verify a backup before importing more files**. The importer itself is transactional but does not create automatic recovery snapshots. Never overwrite an existing snapshot. Test restores to a NEW unused path, then check its status.

For a specific report only:

    py -3 sovia_history.py purge --db my-history.sqlite --report-id REPORT_ID --confirm-delete

For metadata-only source CSV (policy must be explicitly supplied):

    py -3 sovia_history.py import --input examples/demo_source.csv --policy examples/demo_policy.json --db my-history.sqlite

`status` outputs report/event/finding counts. `import` outputs report_id and either imported or already_present. The restore command **never** overwrites an existing database. Backup uses SQLite's transactionally consistent backup API; it does not copy a live file using unsafe filesystem byte copying.

## Storage schema: strict version 1

The database contains:
- reports: digest-derived report ID, full content digest, engine version, time and finding/event counts
- events: SHA-256 event identity and normalized-content digest; UTC time, SHA-256 agent/run/tool tokens; source pointer PRESENT/MISSING as a boolean, never its text
- report_events: report-to-event links for idempotency and deduplication across policy changes
- findings: rule ID, severity, evidence-status enum and hashed event key only

Never stores source JSON, CSV rows, raw prompts, tool arguments, customer documents, event IDs, raw agent/run/tool/target labels, destination strings or source pointer text. SHA-256 pseudonymization **is not anonymity**; short/guessable labels and event times may allow inference or linkage. Local report HTML/JSON/CSV/PDF output from the separate audit CLI has different privacy properties. Keep real inputs/reports/databases/backups outside the PUBLIC Git repository and follow customer retention/consent requirements.

Duplicate report ID + same digest is a no-op. Same logical event (agent/run/event ID) with changed normalized event data is explicitly rejected, and the whole transaction rolls back. Distinct policy evaluations of the same unchanged events are separate reports sharing event rows. Schema version 1 is strict; unknown, inconsistent or future version databases are refused rather than overwritten. No database upgrade/migration to future versions is provided yet.

Targeted deletion drops one report and only event rows with no remaining report reference. `--all --confirm-delete` deletes history rows, enables SQLite secure_delete and VACUUMs local pages. This is **not forensic erasure**, nor deletion of original source files, snapshots, operating system backup copies, SSD blocks or exported reports. Backups require separate explicit deletion/retention handling. No auto-retention/automatic data lifecycle yet.

## Test status and limits

P2 v0.7 source commit `59b982bc8960e38a948c68e49d874457de3e01fa`. GitHub Actions [run 40214522381](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214522381): **Windows + Ubuntu, Python 3.11 + 3.13, 4/4 success**. Each ran 125 tests, 115 PASS / 10 skipped optional PDF / 0 FAIL. Tests include 33 history cases: duplicate import, conflict rollback, JSON/CSV equality, no raw user labels, safe snapshot/restore/delete, corrupted DB and isolated Python. Windows-first run [40214395712](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214395712) exposed read-only fsync and unclosed test SQLite handles. Both fixed and actually re-tested in successful run.

NOT VERIFIED: independent end-user Windows setup, real customer/n8n integration, live GUI, concurrent multi-process stress, full encrypted backup/restore procedure, disk-full/power-loss resilience, secure physical erasure, privacy legal compliance, ReportLab PDF in current CI, production deployment. This stage is NOT commercial-ready.
