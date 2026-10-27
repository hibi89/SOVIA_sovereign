# SOVIA Audit Lite v0.11.2-beta — P2 offline portable CANDIDATE

**Not signed. Not a customer release, security certification, native n8n integration, or production distribution.** This candidate packages already-developed P2 opt-in source tools in a separately versioned strict allowlist ZIP. v0.10 remains unchanged. No phone-home, service daemon, installer, credentials, source customer logs, or extra files.

## What is included

The strictly fixed 18-file payload contains the five-rule offline auditor, CSV parser, optional PDF source, SQLite history, dashboard, strict pre-sanitized n8n-like metadata converter, direct one-command audit, optional PII *pattern* filter, developer-only HTML/JSON budget exporter, aggregate diagnostic without report creation, P2 verifier, P2 synthetic owner selfcheck, Windows launcher, this guide and four **fabricated** examples. There is no raw n8n execution importer, API connector, private data, packaged PDF font or signed binary.

Python **3.11+** required (stdlib flows need no pip or internet). ReportLab plus locally licensed Korean font are required **only for optional PDF**; CI skips those scenarios without dependencies.

## Build from trusted repo checkout

Create the target `dist` folder in advance. Use fresh filenames; existing artifacts are never overwritten.

```powershell
py -3 -I -B build_portable_p2.py --output dist\SOVIA-Audit-Lite-0.11.2-beta.zip
py -3 -I -B verify_portable_p2.py --archive dist\SOVIA-Audit-Lite-0.11.2-beta.zip --sha256-file dist\SOVIA-Audit-Lite-0.11.2-beta.zip.sha256 --extract-to NEW-SOVIA-P2-INSTALL
```

**Provenance warning:** SHA256 plus manifest check detect accidental/unauthorized changes relative to the trusted expected value; if both archive and checksum are replaced, a detached checksum does *not* prove publisher identity. No digital signature or Windows SmartScreen approval is claimed.

## From extracted `NEW-SOVIA-P2-INSTALL/SOVIA-P2` folder

Run **`RUN_P2_SELF_CHECK.cmd`** on Windows; it chooses Python and places newly created **synthetic-only** results in an adjacent `SOVIA_P2_DIAGNOSTICS` folder. Or:

```powershell
py -3 -I -B owner_p2_selfcheck.py --output-dir ..\SOVIA_P2_DIAGNOSTICS
```

The P2 selfcheck verifies pristine installed files first, runs synthetic 3-event/5-finding standard audit, direct one-command audit, zero-report-file aggregate diagnosis, SQLite history/dedup/dashboard/backup/recovery, and optional PDF where dependencies permit. It **never** marks manual browser, Korean PDF visual, Windows Defender/SmartScreen or commercial approval as PASS. Keep all results outside the verified app folder.

Manually run direct sanitized synthetic audit (choose fresh output paths *outside* install):

```powershell
py -3 -I -B sovia_n8n_direct_audit.py --input examples\demo_n8n_sanitized.json --policy examples\demo_policy.json --html-output ..\NEW-SAMPLE.html --json-output ..\NEW-SAMPLE.json --synthetic-only --local-test-budget-bytes 1048576
```

Run aggregate diagnosis without report files:

```powershell
py -3 -I -B sovia_ephemeral_diagnostic.py --input examples\demo_five_rules.json --ack-sanitized-source
```

The old SOVIA base commands still exist. All audit source inputs and outputs must be approved, sanitized and privately retained outside the app installation; generated JSON/HTML can contain event metadata. `approved-local` review claims are unsigned and do not establish consent; PII pattern checks are incomplete; native n8n export and actual installed version remain unverified. The optional output size limit is a developer-selected 1/2/4 MiB test ceiling, not a customer quota or SLA. Disk capacity check is best effort; multi-file writes are not crash-atomic.

## Verification boundary

This release candidate passes only when real fresh ZIP extraction, the bundled P2 selfcheck and legacy v0.10 CI regressions complete. Separately required before a commercial delivery: owner physical Windows/browser/Korean PDF/Defender acceptance, lawful/authorized real source n8n version mapping, comprehensive PII policy, backup/retention/support contract, signing and explicit release approval. No active hosted production URL or paid services.
