# SOVIA test plan and verified execution log
Updated 2026-10-26 KST.

## P1 actual tests
| Date (KST) | Branch/source commit | Command | Pass | Fail | Scope |
|---|---|---|---:|---:|---|
| 2026-10-26 | feature/p0-audit-core / a1c566921a62 | `python -m unittest discover -s tests -v` | 12 | 0 | synthetic 3 rules, safe event, unknown policies, timestamp, duplicate ID/key, boolean type, escaping, ignored raw prompt, 1MiB rejection, CLI end-to-end, input overwrite rejection |
| 2026-10-26 | same | `python sovia_audit.py --input examples/demo.json --output report.html --json-output report.json` | 1 smoke | 0 | 2 synthetic events, 3 findings, generated HTML and JSON |
| 2026-10-26 | same | `python -m compileall -q sovia_audit.py tests` | 1 command | 0 | Python syntax compile |

Local source and all fixture/test files were Git blob hash-matched to source commit. Remote GitHub CI NOT_RUN, clean Windows environment NOT_RUN, HTML browser rendering NOT_RUN, actual external calls verification not independently observed. All tests synthetic; no customer data.

## Remaining P1 tests
Deeply nested input, missing required fields, invalid/non-UTF8, invalid domain and policy types, deterministic repeat runs, read-only import, unexpected failures and side effects, no network by inspection/sandbox tests, unknown status semantically accurate, output reports escaped and semantically reviewed. Add HTML visual browser preview, clean Python environment execution.

## Before commercial offer (P2)
Malicious/oversized import matrix; supported CSV spreadsheet formula injection; real authorized sanitized input and source adaptation; false positives; output redaction/PII review; storage integrity and deletion; backup/restore/retry/idempotency; clean-install guide; dependency/license/commercial claims review; no customer data processing without approval. **P1 success is not P2 success.**

## Cloud future
Tenant negative isolation, auth/RBAC, alerts retry, quotas, billing sandbox, incident recovery, deployment SHA+live browser/API/asset checks.

## Private future
Air-gapped test/no-egress, OS support matrix, backups/upgrades/recovery, local access control. No claim of complete security validation.
