# SOVIA Audit Lite v0.9.0-beta — portable offline package

**Status:** synthetic-test beta, not signed, not a production/customer release. The package contains only the offline stdlib Python auditor/history/dashboard, optional local-font PDF generator, strict CSV parser, a static verifier, docs and **three fabricated examples**. No executable installer, customer data, private configuration, service daemon, telemetry, standalone font or hidden background task.

## Requirements
- Windows with Python 3.11+ available through `py -3` (Python 3.11/3.13 verified on GitHub-hosted runners). On Linux/macOS use `python3`.
- For HTML, JSON, CSV, SQLite and dashboard, no pip, package manager or internet connection is needed. Automatic PDF output is **optional** and needs separately installed ReportLab 4.x and a locally installed Korean TTF. PDF cases were skipped in portable CI.
- New, unused folder for extraction. Keep original log files, any non-synthetic audit reports, SQLite history, snapshots and output HTML in a **different private local directory** outside the app installation and GitHub.

## Obtain and verify the beta ZIP

For the latest verified CI run in [GitHub Actions](https://github.com/hibi89/SOVIA_sovereign/actions), open the successful `SOVIA offline regression` run on `develop` and download the **sovia-portable-beta** workflow artifact (a GitHub-hosted ZIP containing the inner beta `.zip` and `.sha256`). This is a CI artifact, not a signed GitHub Release or commercially supported installer. GitHub download/login availability and artifact retention can vary; rebuild from the verified source if absent.

To build from checked-out project source instead:

    py -3 build_portable.py --output dist\SOVIA-Audit-Lite-0.9.0-beta.zip

First create the `dist` folder; the command refuses existing output or checksum files. The `.sha256` file records the inner ZIP checksum, **not** a digital signature. Compare checksums with a separately trusted value/source when provenance matters; replacing both ZIP and checksum could bypass a mere integrity check.

From trusted repository source, verify and extract to an unused directory:

    py -3 verify_portable.py --archive dist\SOVIA-Audit-Lite-0.9.0-beta.zip --sha256-file dist\SOVIA-Audit-Lite-0.9.0-beta.zip.sha256 --extract-to SOVIA-install

The verifier rejects unexpected/duplicate paths, symlinks, unknown manifest fields, oversized payloads, checksum mismatches and existing target directories; it reads and verifies ZIP contents **before** extraction. Then verify the freshly extracted payload (before creating any local reports in it):

    py -3 SOVIA-install\verify_portable.py --directory SOVIA-install

Files live directly inside `SOVIA-install`, not in an additional nested SOVIA folder. No installation to Program Files, registry changes, internet, external services, authentication or machine privileges.

## Clean-demo audit → local history → HTML dashboard

In PowerShell:

    mkdir sovia-output
    py -3 -I -B SOVIA-install\sovia_audit.py --input SOVIA-install\examples\demo_five_rules.json --output sovia-output\audit.html --json-output sovia-output\audit.json
    py -3 -I -B SOVIA-install\sovia_history.py import --input SOVIA-install\examples\demo_five_rules.json --db sovia-output\history.sqlite
    py -3 -I -B SOVIA-install\sovia_dashboard.py --db sovia-output\history.sqlite --output sovia-output\dashboard.html
    start .\sovia-output\dashboard.html

Expected synthetic demonstration: 3 input events and 5 deterministic policy findings; history 1 report/3 unique events/5 findings; HTML dashboard generated locally. The output directory must already exist and filenames must be new. To refresh HTML, use a *different unused filename*. CSV source import requires explicit `--policy`; see `HISTORY.md` in the full repository for additional examples. To back up an existing DB, use `sovia_history.py backup --db ... --output <NEW_FILE>` and test restore into another NEW path before deletion.

## Privacy and operational boundaries

The audit itself does not execute logged agent operations or send data to the network. The **optional** SQLite history stores pseudonymous digest metadata, not raw prompt/event labels; timestamps and hashes remain potentially linkable. Static HTML can expose such metadata if shared. Do not use real customer input without permission, source traceability, retention and privacy review.

The verifier checks **integrity and allowlisted content**, not software authenticity, legal certification, malware-free origin or secure erasure. Use official/trusted GitHub source, independently trusted checksums and standard OS controls. Existing source files and any other snapshots/reports must be managed separately. Never publish client records, fonts or local outputs into this PUBLIC repo.

## QA status and known gaps

At authoring, this is code for a synthetic portable v0.9 beta CI milestone. Test evidence and exact run SHA must be checked in current `STATUS.md` and `TEST_PLAN.md`. Independent owner Windows installation/browser rendering, malicious third-party ZIP/signature, PDF fonts on owner PC, AV/SmartScreen, signed binary installer, real authorized n8n samples, privacy/false positives, disk failure and commercial support are NOT accepted yet. No Production/Vercel/app deployment.


## Verified CI checkpoint 2026-10-26
**CURRENT P2 PORTABLE BETA CHECKPOINT (2026-10-26 KST):** The feature/p2-portable-package branch now builds an offline SOVIA Audit Lite 0.9.0-beta ZIP with an allowlisted 10-file source/synthetic payload, embedded manifest, detached checksum, strict verifier and new-directory-only extraction. Test SHA 7dffc94401e6843b9fa792edfd1a886e4757950b. [GitHub Actions result](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40216762276) finished **4/4 success**, Windows and Ubuntu × Python 3.11/3.13, each **177 discovered / 167 PASS / 10 optional-PDF SKIP / 0 FAIL**. Clean extracted portable ZIP passed real isolated Python audit (3 events/5 findings) → SQLite idempotency → offline HTML dashboard → SQLite backup/restore on all four jobs. Archive SHA256 **6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3** matched all four environments. The unsigned ZIP + detached checksum were uploaded as GitHub Actions artifact **sovia-portable-beta**, artifact ID 12607951989. NOT a signed installer, real customer use, user-PC validation or production. NEXT: green PR merge to develop, then owner Windows installation/browser/optional PDF testing and commercial privacy gates. Default main is docs only.
The previous author-time test disclaimer above has been superseded by this actual CI result. Browser/owner PC and commercialization gates remain unverified.
