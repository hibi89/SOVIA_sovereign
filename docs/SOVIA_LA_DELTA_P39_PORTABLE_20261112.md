# SOVIA P39 — Separate v0.14 offline LA review-delta candidate (2026-11-12 KST)

## Goal / design trade-off
P38 already computes only minimized, independent, **unauthenticated synthetic** LA-risk count differences across two verified review folders. P39 makes that owner workflow installable from one **separately versioned source-only ZIP** without modifying historical v0.13 and frozen v0.12/v0.11.2/v0.10 releases.

- A: overwrite/relabel the existing v0.13 ZIP and reuse its SHA. Lower development effort but breaks artifact provenance, auditability and historic restoration; rejected.
- B: new deterministic **SOVIA-LA-Delta-0.14.0-beta.zip**, distinct version, prefix, fixed allowlist and verifier, with a new Windows `RUN_LA_DELTA.cmd` and synthetic missing-observation fixture. Selected: maintains source/version rollback, no customer data, external AI or runtime/service changes, and no extra Python packages. This is still **unsigned and NOT retail**.

## Delivered implementation
- `verify_portable_la_delta.py` reuses proven v0.13→v0.12 verifier using *isolated* local module objects, specializing version `0.14.0-la-delta-beta`, format `SOVIA_PORTABLE_LA_DELTA_V1`, prefix `SOVIA-LA-DELTA/` and exact 18-file allowlist; existing verifier global state outside the isolated instance remains unchanged.
- `build_portable_la_delta.py` reuses the existing bounded no-overwrite atomic builder via separate instance, different fixed ZIP filename and detached unsigned SHA256.
- `RUN_LA_DELTA.cmd [--ci]` verifies all extracted ZIP files **before executing** synthetic code; uses Python3.11+ with no installation; creates two NEW sibling synthetic report folders, compares them with `sovia_la_review_delta.py` and prints risk-count JSON only. Repeat refuses previously-created folders; preexisting user folders are not deleted/overwritten. It never downloads dependencies, opens remote URLs, or executes an actual Lightning Azent workflow.
- `examples/demo_la_observations_gap.json`: fabricated one-missing-event delta source. `LA_DELTA_PORTABLE_README.md` describes operator commands and limits.
- `portable_smoke_la_delta.py` and `tests/test_portable_la_delta.py`: actual clean extraction→isolated `-I -B` two reviews→aggregate delta with missing observation→no-raw-ID, no-clobber, tamper refusal→final extracted-file integrity. On Windows, actually execute `cmd.exe /d /c RUN_LA_DELTA.cmd --ci`, rerun must return code2. The existing 13-file v0.13 builder is re-run to assert determinism/version preservation.

## Exact verification evidence
- Exact feature+test commit: `3470020b974e09ca864d030bca3fa580216aa91b` on public `hibi89/SOVIA_sovereign@feature/kmong-la-review-p2-20261112`; [draft PR #71](https://github.com/hibi89/SOVIA_sovereign/pull/71) remains unmerged.
- [Actions #43205824976](https://github.com/hibi89/SOVIA_sovereign/actions/runs/43205824976) **4/4 SUCCESS** on the **exact commit**, 928 discovered per platform:
  - Windows Python3.11, 3.13: **917 PASS / 11 SKIP / 0 FAIL each**; new actual Windows CMD generation and rerun refusal test PASS both.
  - Ubuntu Python3.11, 3.13: **905 PASS / 23 Windows-only SKIP / 0 FAIL each**; new standalone 0.14 ZIP full clean extraction and real isolated P38 delta tests PASS.
  - Existing P2 Edge/Windows CMD, v0.12 and v0.13 portable tests continued PASS; no code modifications to 0.13 builder/verifier or old release archives.
- CI creates the v0.14 ZIP in temporary test folders. It **does not upload a standalone persistent v0.14 release or chat artifact**. Source-archive transfer to chat was attempted but failed at the network/URL-access layer. Do not claim a downloadable ZIP or distribution release exists.
- Actual consumer physical Windows10/11, installed antivirus/SmartScreen, genuine first-party Lightning Azent execution/authenticated event receipts, customer source authority, privacy/retention/legal/rights, digital signing, support/pilot and owner GO **NOT VERIFIED**.

## Technical score and decision
- Existing **87% provisional engineering** from P38 source-only source-backed delta; **+3pp provisional** for an actually verified, separately versioned, deterministic, independently extractable Windows-capable offline candidate, including real GitHub-hosted CMD journey and tamper/no-clobber regression.
- Whole product **90% provisional engineering / 95% NOT ACHIEVED / commercial RELEASE HOLD**. This weighted score is a design-scope estimate, not sales availability, CI pass percentage or real LA integration. Missing exact first-party LA authorized receipt contract and consumer acceptance cannot be made up by synthetic tests.

## Build/reproduce locally from exact SHA
```sh
python -m unittest discover -s tests -v
python -I -B portable_smoke_la_delta.py
python -I -B build_portable_la_delta.py --output dist/SOVIA-LA-Delta-0.14.0-beta.zip
python -I -B verify_portable_la_delta.py --archive dist/SOVIA-LA-Delta-0.14.0-beta.zip --sha256-file dist/SOVIA-LA-Delta-0.14.0-beta.zip.sha256
```
Create `dist/` first and ensure both output filenames are NEW. On a **trusted Windows** host, extract to a NEW folder and run `RUN_LA_DELTA.cmd --ci`; this run remains unapproved for real customer data.

## Next / retained boundaries
1. Obtain owner-approved, versioned **minimal genuine Lightning Azent sanitized receipt** with declared consent, provenance and field policy (no copying PRIVATE HAE/LA code into PUBLIC SOVIA); prove actual local read-only ingestion and fail-closed unknown state.
2. Independently test sample real inputs after explicit permission, privacy/false positives, customer Windows10/11/Defender/SmartScreen/report usability, contractual rights and support.
3. Only after external approvals decide sale/release and artifact distribution. No Vercel/Production currently applies.
4. Preserve this source SHA and existing historic v0.13 P38-free ZIP. No silent upstream merge, billing or repo permission change.

**Updated:** 2026-11-12 KST. CI evidence belongs to exact code SHA above, later documentation commits are not function/test-verified SHAs.
