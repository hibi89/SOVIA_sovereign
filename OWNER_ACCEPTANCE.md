# SOVIA owner Windows acceptance — v0.10 beta

This is an **owner-only, synthetic-data acceptance checklist**, not a signed software release, full penetration test, antivirus certification or authorization to use real customer logs.

## 1. Files and prerequisites

- Download the **sovia-portable-beta** artifact from the successful `SOVIA offline regression` run on the verified `develop` commit. It contains a nested portable ZIP and SHA-256 checksum; do not mistake the outer Actions artifact ZIP for the inner distribution ZIP.
- Install/locate a trusted Python **3.11 or newer** yourself (the diagnostics never downloads or installs dependencies). No administrator privileges, network, hosted web server, paid API or background tasks are needed for the basic audit.
- Check the ZIP digest against an **independently trusted** checksum published with the specific CI run/source revision. A checksum beside the same ZIP is **not a digital signature**, and cannot establish the publisher's identity.
- Extract using the trusted repository's `verify_portable.py --archive ... --sha256-file ... --extract-to NEW_FOLDER`, or use the OS extractor only after trusted integrity checks. Never run bundled scripts from an untrusted ZIP.

## 2. Double-click local diagnostic

In the fresh extracted `SOVIA` folder, double-click **RUN_SELF_CHECK.cmd** or run it from Command Prompt. The launcher checks the installed Python launcher (`py -3`), with a `python` fallback. It calls bundled `owner_selfcheck.py` using isolated `-I -B`. It does not perform a network request, install packages, open the browser automatically or access your documents.

A new output directory is created beside the app under `SOVIA_DIAGNOSTICS/SOVIA_SELF_CHECK_<unique>`. Repeating it creates another **new** folder. Inspect `SELF_CHECK_RESULT.json` there.

| Result code | Meaning |
|---|---|
| `AUTOMATED_PASS_MANUAL_PENDING` | Package integrity, synthetic JSON audit, SQLite idempotency/recovery and HTML dashboard checks passed on **this machine**. Manual visual/privacy tests are still required. |
| `AUTOMATED_FAILED` | At least one required synthetic local step failed; `error_code` narrows the failure without embedding your paths or private input. |
| `SKIPPED_REPORTLAB_MISSING` | Optional PDF package absent; HTML/SQLite are unaffected. |
| `SKIPPED_KOREAN_TTF_MISSING` | Optional system Korean TTF not found; no font is downloaded. |
| `GENERATED_NEEDS_VISUAL_REVIEW` | A synthetic PDF was produced, but Korean characters/pages **must be checked manually**. |
| `FAILED_OPTIONAL_PDF` | PDF generation failed although dependencies appeared available; retain HTML fallback and inspect locally. |

The script does **not** automatically mark manual checks as PASS. Do not infer browser appearance, PDF legibility, absence of false positives, or commercial readiness from a synthetic green JSON file.

## 3. Manual approval checklist

- [ ] Open `synthetic-audit.html` locally and confirm Korean labels, correct **3 synthetic events / 5 rule findings**, readable table layout and unverified-evidence warnings.
- [ ] Open `synthetic-dashboard.html` and check headline counters **1 report / 3 events / 5 findings**, recent timeline, mobile/desktop scrolling and Korean font legibility.
- [ ] If a synthetic PDF was generated, open `synthetic-audit.pdf` in your usual viewer; inspect all Korean text, page breaks, table columns and finding rationale. Optional ReportLab 4.x and an OS-installed Korean TTF are prerequisites; no font is shipped.
- [ ] Check your own Windows Defender/SmartScreen outcome without bypassing warnings; if blocked, record the exact local status and investigate package provenance.
- [ ] Verify source data remain unchanged, reports are in a private non-Git folder, backup/restore output is separate and no customer logs are present.
- [ ] For real use, confirm client consent, retention deletion policy, supported input provenance and privacy assessment **separately**. This synthetic diagnostic is not sufficient.

## 4. Troubleshooting without leaking sensitive files

If nothing opens, check that Python 3.11+ is callable with `py -3 --version` or `python --version` and that the extracted folder includes `MANIFEST.json`. Use `python -I -B owner_selfcheck.py --output-dir ..\SOVIA_DIAGNOSTICS` if the batch launcher is blocked by policy.

Never upload the whole diagnostics folder, original logs, PDF font files, `.env`, secrets or customer DB to a public issue. A safely redacted subset of `SELF_CHECK_RESULT.json` (status, checks, error_code) may be enough to diagnose a failure; even OS version info can be sensitive. If a verifier reports a modified file, re-download and verify from a trusted source rather than editing manifest hashes to suppress the warning.

## 5. Validation boundaries

GitHub-hosted Windows is not the owner's PC. The owner should only record this checklist as complete **after running it locally**; no remote assistant can claim a Windows desktop visual/antivirus pass from CI. CI checks are synthetic and do not authorize installing any unsigned code on a client system, uploading client logs or publishing a paid release. Commercial readiness remains gated on sanitized, consented customer input, privacy, failure recovery, documentation and support policies.
