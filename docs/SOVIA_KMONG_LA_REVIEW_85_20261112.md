# SOVIA P2 LA synthetic owner review — 75% → 85% provisional engineering (2026-11-12 KST)

## Scope and design choice
This is a PUBLIC, synthetic-only, Python 3.11+ local-first product milestone, not a new real Lightning Azent runtime integration. A) Import live private HAE/LA receipts and customer data now: high provenance/consent risk, sensitive source boundary, unverified native receipt schema and runtime dependencies. B) Preserve the existing retrospective public SOVIA audit and implement a separate synthetic-only owner-facing reviewer with independent packaging/integrity tests: selected. B is lower-cost, repeatable without customer material and does not alter the old immutable package. A remains the eventual product gate; nothing here claims it complete.

## Functional changes
- Previous status bug: a planned-vs-observed identifier match could result in `SYNTHETIC_MATCH_NOT_AUTHENTICATED` while plan or independent retrospective audit found HIGH policy risks. Fixed to `SYNTHETIC_REVIEW_REQUIRED`; zero-risk synthetics still report unauthenticated status, never approval.
- Correlation result now carries strictly reduced plan and retrospective rule identifier/severity only, plus prior mismatch findings; no raw agent events, policy body, secret, evidence pointers or customer records.
- `sovia_la_owner_review.py`: explicit `--synthetic-only` offline owner CLI, Korean CSP/JS-free HTML with plan/post-audit/mismatch tables and explicit unknown limits, JSON and SHA256 manifest in a NEW destination; strict bounded input and no-clobber, link/reparse rejection, atomic no-overwrite file creation with visible INCOMPLETE marker, independent read-only manifest and JSON/HTML agreement check, corrupted/missing/extra content refusal.
- New separate `0.13.0-la-review-beta` 13-file unsigned ZIP, deterministic builder and strict verifier reusing legacy v0.12 logic via fresh module instances (old code/version/files/checksums unchanged). `RUN_LA_REVIEW.cmd --ci` validates extracted files before offline synthetic review, no browser/pause in CI. Independent extracted ZIP → reviewer → integrity verification → tamper/duplicate refusal smoke. Customer executable installation, cryptographic signing and authorized runtime receipt ingestion NOT present.
- Added Python unit/negative cases, Windows actual cmd.exe synthetic test and Ubuntu CI ZIP artifact only. No external credentials, paid APIs, original records, deployment, customer service, or repo visibility changes.

## Exact verified run
Feature source SHA **45c3ca88b5533d5ac2599b248abe4c8ee57c5953**, PR [#71](https://github.com/hibi89/SOVIA_sovereign/pull/71) draft/unmerged, based on `develop` SHA `7418b23aff9b3abbd3faf5d1477e7244ec82b681`.
[Actions #43111064491](https://github.com/hibi89/SOVIA_sovereign/actions/runs/43111064491) at **exact source SHA**, 4/4 SUCCESS, all 917 discovered per platform, **0 FAIL**:
- Windows Python3.11: 906 PASS, 11 SKIP; Windows Python3.13: 906 PASS, 11 SKIP.
- Ubuntu Python3.11: 895 PASS, 22 SKIP; Ubuntu Python3.13: 895 PASS, 22 SKIP.
- Windows3.11 `verify_local.ps1` PASS; hosted Windows actual `cmd.exe` new launcher success/relaunch no-overwrite/tampered installer refusal; legacy package suites, capacity and browser Edge synthetic tests passed as part of workflow.
- Ubuntu3.11 separate `python -I -B build_portable_la_review.py` → verify archive and SHA → `python -I -B portable_smoke_la_review.py` **PASS**: 13 allowlisted files, SHA256 `3f1bdb3334f4e40b60bbd205ce961f49f38a8660cb279b1eb99b6a6518e02a2b`, source not exported, risk preserved, existing output refused and mutation refused. Artifact `sovia-la-review-synthetic-v013`, ID `13897230966` (14-day retention), **unsigned, NOT release**.
- Historical new-package smoke CI #43110873703 FAILED due `-I` omitting script import path, remedied with explicit local module loading; final #43111064491 all jobs SUCCESS. Earlier isolated CLI import failure also corrected. Do not replay failed import strategy.

## Engineering score / release gates
Previous central product score 75% → **85% provisional engineering scope (+10p)** assigned to bug/risk-preservation +2, reviewer tables/redacted structured output +2, provenance-safe no-clobber/integrity +2, separately packaged OS-matrix tested customer-operator synthetic workflow +4. This is a subjective blueprint-scope appraisal, **not** 85% of true customers accepted or a sales gate. Product remains **RELEASE HOLD**; actual Lightning Azent stable authenticated receipt contract, genuine first-party LA integration, user consent/source provenance, local physical owner Win10/11 Defender/SmartScreen/real PDF/print/accessibility, privacy false-positives/retention/legal/support/signing, 1–2 approved genuine customer pilots and distribution approval remain unverified. No secure race-free filesystem guarantee; SHA not a digital signature.

## Test/usage/recovery
- `python -m unittest discover -s tests -v`
- `python -I -B portable_smoke_la_review.py`
- `python -I -B build_portable_la_review.py --output dist/SOVIA-LA-Review-0.13.0-beta.zip` (create `dist` first, output must not already exist)
- `python -I -B verify_portable_la_review.py --archive dist/SOVIA-LA-Review-0.13.0-beta.zip --sha256-file dist/SOVIA-LA-Review-0.13.0-beta.zip.sha256`
- Portable extracted folder: `RUN_LA_REVIEW.cmd --ci` Windows; repeat must HOLD. History permits normal Git revert; old package binaries and default main/develop are untouched. No Vercel/Production (NOT_APPLICABLE).

## Next
Review PR #71 and full source/CI; obtain versioned minimal LA receipt contract from the LA owner, then implement a separate approved local read-only adapter without copying PRIVATE HAE source into PUBLIC repo. After source provenance and privacy review, run native genuine LA→SOVIA test and physical Windows QA; do not ship or approve customer data ingestion before authorization.
