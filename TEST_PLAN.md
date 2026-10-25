# SOVIA test plan — P2 CSV export checkpoint
Updated 2026-10-26 KST. Source/tests verified commit 6b3be7a4512049caa5a329776e2a63462cd6c8fa.

## Actually executed
| Command / probe | Result | Interpretation |
|---|---|---|
| python -m unittest discover -s tests -v | 54 PASS / 0 FAIL | 40 prior + 14 new CSV checks |
| python -m compileall -q sovia_audit.py tests | PASS | Python syntax |
| python sovia_audit.py --input examples/demo_five_rules.json --output output/report.html --json-output output/report.json --findings-csv output/findings.csv --events-csv output/events.csv | PASS exit 0 | Fake 3 events, 5 findings, findings.csv 5 rows, events.csv 3 rows, all 4 files nonempty |
| Temporary clean folder, python -I -B and four flags | PASS exit 0 | Same-machine isolated execution, not second Windows machine |
| Local Git blob SHA check | PASS | Source eb886ab5d9a24663f3414cecf74c5dcd9d48f205; tests/test_csv.py 29858eca381a9e161554bc02cd78776278d7034f match remote |

14 CSV-specific tests: fixed finding/event headers and counts, timezone stable ordering, BOM+Korean+CRLF, formula-like strings starting = + - @ (including Unicode prefix characters), dangerous values in both outputs, comma/quote handling, raw_prompt exclusion, empty-safe findings header, bad export kind, 4-output CLI, existing CSV preservation, duplicate-output rejection, simulated failure of fourth staged publish rolling back all prior files, optional CSV disabled by default.

## Unverified / commercial gates
Excel/Google Sheets actual UI and import variations not tested; spreadsheet formula escaping is defense-in-depth not a certified complete barrier. CSV ingestion unsupported. NTFS/external drives and hardlink compatibility not tested; fail safely. Simulated rollback only, no power-loss guarantee, group of four files not atomic for observers. Real source log provenance, PII scanning, backups, deletion, false positives, clean Windows install and operational end-to-end must pass before sale. Cloud/Private tenant/offline checks not applicable until those modes exist.
