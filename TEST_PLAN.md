# SOVIA test plan, execution evidence and remaining gates
Updated 2026-10-26 KST. P1 code commit 8957e872a0519dae208f49c51c848f95f35f7046.

## Actual test runs (Python 3.13.5 local)
| Command | Result | Scope |
|---|---|---|
| python -m unittest discover -s tests -q | PASS 40 / FAIL 0 | 29 existing + 11 additional: output pre-exists, JSON/HTML no-clobber, staged publish rollback on simulated second file failure, staging cleanup, report completeness, repeat-run, dangling symlink target, isolated temp copy, raw prompt omitted, invalid output directory, patched socket (no attempted connection), HTML two tables |
| python -m compileall -q sovia_audit.py tests | PASS | Syntax |
| python sovia_audit.py --input examples/demo_five_rules.json --output <unused>.html --json-output <unused>.json | PASS; exit 0, 3 events, 5 unique findings | Offline synthetic CLI |
| python -I -B sovia_audit.py inside temp copy | PASS, 5 findings | Same-machine isolated-directory environment; not actual new Windows PC |
| Headless Chromium page.set_content(generated HTML) | PASS: 2 tables, 5 findings, 3 timeline events, 0 page errors/console errors; 1280 px no overflow | Browser rendering of markup, NOT browser file:// navigation |

Day3 transient failures: dangling symlink path bug detected by new test (CLI exit 0 unexpectedly), corrected absolute-target handling; final rerun 40/40 pass. Chromium file:// navigation blocked administratively, pivot to page.set_content with successful DOM render. Neither was a verified production incident.

## Limitations/remaining tests
- Multi-output publication uses exclusive hard links with fsync-staged full files; best-effort rollback for normal errors but no guarantee of full multi-file atomic visibility or power-loss recovery.
- Filesystems without os.link/hardlink support fail safely, need Windows/NTFS and unsupported-filesystem test.
- No GitHub Actions test claim; no second machine/browser actual file URL, no native installer, no real log feeds, tenant security or network capture.
- Before selling: genuine permissioned sanitized input, PII scanning, CSV injection defense, false positives, file corruption/recovery, deletion/backups, platform compatibility, support/disclaimer/contract, external service risk review.
- Cloud/Private future: tenant boundary, auth/RBAC, rate limits, alerts replay, billing sandbox, restore, disconnected offline no-egress and live deployment browser/API checks.
