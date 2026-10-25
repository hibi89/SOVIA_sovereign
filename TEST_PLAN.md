# SOVIA test plan and observed evidence
Updated 2026-10-26 KST, code commit 2eda8c37a3ed06702aba14cb53790da3cbaf8e83.

## Executed tests
| Environment | Command | Pass | Fail | Observation |
|---|---|---:|---:|---|
| Python 3.13.5 local | python -m unittest discover -s tests -q | 29 | 0 | Three baseline rules; 2 added rules; UTC burst boundaries, independent run; evidence unknown; timeline escaping; invalid inputs; stable output |
| Python 3.13.5 local | python -m compileall -q sovia_audit.py tests | 1 command | 0 | Syntax compile |
| Python 3.13.5 local | python sovia_audit.py --input examples/demo_five_rules.json --output report_day2_final.html --json-output report_day2_final.json | 1 smoke | 0 | 3 events, 5 findings, five distinct rules |
| Local static artifact check | Inspect generated report_day2_final.html / report_day2_final.json | 1 smoke | 0 | Rendered HTML string with timeline + 5 finding table and JSON schema; not a real browser test |

Source, tests and synthetic fixtures uploaded via GitHub blobs with content SHA matching local tested files. No GitHub Actions, clean Windows, production or genuine customer verification.

## Day3 and commercial test gates
P1: output collision and interrupted write tests, clean start instructions, local report visual check, additional malformed inputs, deterministic replay, no outside dependencies; include tests in GitHub code. P2 BEFORE SALE: sanitized authorized real sample, CSV formula escaping, resource limits, backups/restore, deletion, false-positive/false-negative review, provenance and sensitive content redaction, packaging/license/support. P4/P5: tenant isolation, RBAC, alert retry, disaster recovery, offline no-egress and production URL browser/API/security checks.

## Failure record
Initial burst rule test fixture had timestamps at the 60-second boundary and incorrectly expected three calls within a one-minute window; fixture corrected, tests rerun (29/29 passing). This was a fixture issue, not proof of a production outage. Digest label corrected from input_sha256 to normalized_policy_sha256 to avoid implying original file hash.
