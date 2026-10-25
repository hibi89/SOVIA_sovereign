# SOVIA test and acceptance plan
Status: PLANNED, zero tests run as of 2026-10-25 KST.

## P1 MVP test suites
- Schema parser: valid JSON/CSV, unknown fields, invalid timestamp, oversized file/row, duplicate IDs, wrong types.
- Canonical adapter: identical logical events produce stable normalized output; timezone roundtrip; UTF-8/Korean.
- Rules: seeded fixtures trigger expected findings with exact event references; safe fixtures produce no invented issues.
- Evidence: file pointer, input digest, event count, rule version, missing/unknown status consistent.
- Report: deterministic content for same fixture and rule set, HTML escape hostile text, PDF conversion if installed, no secret leakage.
- CLI: offline test, return codes, bad path, read-only input, output path sandbox, purge and repeat execution idempotency.
- Failure recovery: interrupted import, duplicated retry, corrupted SQLite and disk-full simulation.
- Security smoke: malicious filenames, prompt injection strings treated as data, large nested JSON, poisoned CSV formulas, path traversal.
No predetermined pass counts: log actual command, timestamp, counts and evidence after execution.

## Commercial pilot validation
Install on a clean machine, sanitize genuine sample logs, confirm policy coverage/false positives, validate scope and redactions with customer, backup/restore test, documented license/support/retention, fail-closed where necessary. No production certification inferred.

## Cloud future suite
Cross-tenant isolation incl unauthorized object IDs, RBAC, auth lifecycle, alert dedup+retry, quota, data deletion, billing sandbox, restored backup, agent offline heartbeat. Production test: HTTP, assets, dashboard render, console/network, API, charts/tables, full customer login/logout and permission checks. Verify deployed Git SHA equals target commit SHA.

## Private future suite
Disconnected install, no-egress packet observation, restart/recovery, offline upgrade with rollback, local user authorization and backup, NAS/OS support matrix. Unsupported devices remain UNSUPPORTED.

## Test status log
| Time (KST) | SHA | Command | Pass | Fail | Status |
|---|---|---|---:|---:|---|
| 2026-10-25 | N/A | Not yet executed | 0 | 0 | NOT_RUN |


## 2026-10-26 three-tier testing allocation
**P1 72-hour mandatory each day:** CLI smoke on small synthetic file, known-safe / known-risk oracle cases, invalid type/size rejection, never execute imported strings, offline no external API, report escape and evidence linkage. Record exact commands, test counts and sample artifact checks. A date target is not a PASS.
**P2 before listing/pilot:** complete broader negative/adversarial and regression suite above, fresh-machine install, sanctioned sanitized n8n or supported format fixture, retention/delete and recovery, report limitations, false positives. Any sale-threatening issue blocks commercial release.
**P4/P5 preproduction:** isolation, auth, billing, resilience, monitoring, restore, no-egress, and live URL/UX/API security validation. Penetration and endurance tests where meaningful.
No tests performed as of this documentation plan change; no fabricated counts.
