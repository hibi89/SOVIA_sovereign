# SOVIA P95 technical milestone — first-party PRIVATE LA local synthetic SQLite → PUBLIC SOVIA and standalone v0.15 (2026-11-12 KST)

## Scope and design comparison
Customer 100% blueprint remains full independent AI-agent policy audit. This P95 milestone verifies technical boundaries but **no real person/customer authorization**, legal rights, physical consumer device or production. Prior P40 90% already implemented synthetic minimal public claim checks, P39 source-only package. Missing core was an actual first-party LA source behind privacy boundary and installable independent SOVIA checker.

Two architectures:
- A: import PRIVATE HAE/LA implementation, source SQLite ledgers, run IDs, original customer file paths or payload into PUBLIC SOVIA repository/CI. Tempting for quick completeness but invalid consent/source/IP/data custody and unauthenticated public data; **REJECTED**.
- B: introduce **isolated PRIVATE feature branch** with real LA synthetic SQLite execution and read-only first-party evidence validation, convert only strict generic aggregates and pseudonymous step metadata inside private CI, test against pinned public P40 SOVIA code without uploading private sources to public, and build a wholly separate public v0.15 unsigned consumer candidate. Chosen; public version is source-only and label-only, not a real customer pipeline.

## Implemented
**P41 (+2 engineering points):** PRIVATE `hibi89/HAE@feature/sovia-la-projection-p41-20261112` adapter `packages/lightning-azent/sovia_projection_private.py` (outside frozen P18 zipapp inventory) calls actual `HAEBridge.evidence` against real local SQLite to validate completed plan status and business receipts, then exports only SOVIA P40 exact allowlisted minimal synthetic fields. `tests/test_sovia_projection_p41.py` nine tests. Unapproved calls, completed-but-missing business receipts, tampered audit, changed run plan, wrong external fingerprint rejected; no run ID, plan content, path or business records returned. Caller-asserted SOVIA fingerprint **does not prove same run identity**.

**P43 (+2 engineering points):** PRIVATE `sovia_semantic_projection_private.py` maps **actual** first-party LA `step_completed` audit events to alias `step001/step002`, fixed fabricated event times/target metadata and P2 SOVIA plan/observation contracts **only for two allowlisted synthetic CSV→SQLite operations**. Verifies every normalized LA step has exactly one matching operation+completed event, and denies missing/duplicate/failed steps. The operator's LA write approval does **not** implicitly authorize the independent SOVIA policy, whose distinct allowlist raises the write risk. `tests/test_sovia_semantic_projection_p43.py` five tests and `verify_sovia_p41_roundtrip.py` executes true private HAE natural-language intent→LA SQLite and actual receipt extraction→redacted SOVIA plan/observation→real public `sovia_la_owner_review.py` audit→P40 minimal claim check. Exact PUBLIC SOVIA P40 source SHA pinned by read-only private CI checkout: `63c9a329de71470089e0a866e802a20ce9a48ad6`. No PRIVATE implementation/source/files entered public GitHub/CI.

**P42 (+1 engineering point):** PUBLIC separate `SOVIA-LA-Minimal-0.15.0-beta.zip` fixed inventory **23** source files, canonical deterministic builder/checksum verifier, contains SOVIA P40 minimal checker and a separate *FABRICATED LA-LIKE* synthetic-only demo, `RUN_LA_MINIMAL.cmd --ci` on actual Windows. Independent isolated extraction, no overwrite, fake status/auth false, report tamper, legacy 0.14/0.13 byte identity tests. The public package intentionally does not include PRIVATE LA engine or execute real LA; only the **private CI proof** does.

## Exact source and platform evidence
- PRIVATE final functional+regression commit **`7b27c4926ee353d537a1526d8b4d2919b9f86eeb`**, [Windows+Ubuntu Actions #43215726885](https://github.com/hibi89/HAE/actions/runs/43215726885) **2/2 SUCCESS**. Both Python3.11 LA **128 discovered, 128 PASS/0 FAIL**, original HAE **91 PASS/0 FAIL**, Windows focused backup **1 PASS**. Synthetic cross-run terminal: `REAL_SYNTHETIC_LA_SQLITE_STEPS_TO_SOVIA_AUDIT_PASS`; SOVIA matched two pseudonymous steps and independently flagged unauthorized write; after deletion of actual LA SQLite step audit event, projection refused. The first attempt #43212701824 FAILED frozen P18 zipapp inventory when adapter file wrongly placed inside package; moved outside with unchanged P18 allowlist. P43 initial #43215548711 FAILED a test expectation when duplicate step displaced terminal; repaired by inserting final terminal event after duplicate and final CI green. Do not repeat those designs.
- PUBLIC v0.15 source+tests **`a6991d062e657073fd5c5df077c87db9aa390515`**, [Actions #43214296725](https://github.com/hibi89/SOVIA_sovereign/actions/runs/43214296725) **4/4 SUCCESS** exact SHA, **944 discovered each, 0 FAIL**: Windows Python3.11/3.13 **933 PASS/11 SKIP** each, Ubuntu3.11/3.13 **920 PASS/24 SKIP** each. Real hosted Windows CMD exit0 and re-entry refused with exit2, canonical standalone 0.15 ZIP and prior 0.14 bytes preserved.
- Source SHA links differ from docs/CI-artifact workflow follow-up SHA. A transient 14-day CI source ZIP+detached unsigned SHA is **a review artifact, not a release**. GitHub artifact persistence and new workflow verification must be checked in the follow-up CI run.

## Honest acceptance scoring, boundaries
Engineering baseline **90% provisional**; P41 private actual first-party SQLite validated minimal output **+2pp**; P43 actual step-event privacy projection & independent SOVIA policy comparison **+2pp**; P42 new independently versioned source-only consumer candidate with actual Windows CMD tests **+1pp**. **Total 95% PROVISIONAL ENGINEERING milestone.** This score estimates delivered blueprint functionality, not test success percent or verified customer/sales readiness.

**Unverified / reserved for owner's final 100% acceptance:** actual owner-authenticated LA consent and source provenance, cryptographically/semantically validated LA↔SOVIA identity across real runs, authorized REAL sanitized customer data beyond synthetic/temporary local SQLite, complete telemetry beyond two supported operations, physical buyer Windows10/11/Defender/SmartScreen, browser/print/installation UX, data privacy/retention/licensing/signing, independent false-positive human review, support/pilot and explicit commercial GO. SHA/detached checksum is unsigned and NOT proof of owner identity. PUBLIC synthetic checker always `REVIEW_REQUIRED_NOT_AUTHENTICATED`; no claiming authenticated compliance or safety clearance.

## Source/backup/commands
Public `hibi89/SOVIA_sovereign@feature/kmong-la-review-p2-20261112` draft PR #71 unmerged; original `develop`/`main`, old 0.10/0.11.2/0.12/0.13/0.14 versions unchanged. Private `hibi89/HAE@feature/sovia-la-projection-p41-20261112` is isolated branch from `feature/la-p17-audit-evidence-20261112@febb0ebe773afa47ab596377196b4c98c501028d`; original LA baseline and HAE main untouched. No private input/payload/code uploaded public, tokens/keys absent, no deployment/paid external API or force-push.

From public source checkout, create **new empty** `dist/` and run:
```sh
python -m unittest discover -s tests -v
python -I -B portable_smoke_la_minimal.py
python -I -B build_portable_la_minimal.py --output dist/SOVIA-LA-Minimal-0.15.0-beta.zip
python -I -B verify_portable_la_minimal.py --archive dist/SOVIA-LA-Minimal-0.15.0-beta.zip --sha256-file dist/SOVIA-LA-Minimal-0.15.0-beta.zip.sha256
```
Windows extracted new-only folder: `RUN_LA_MINIMAL.cmd --ci`. From an authorized PRIVATE HAE feature checkout with matching PUBLIC SOVIA pinned SHA local checkout: `python -I -B packages/lightning-azent/verify_sovia_p41_roundtrip.py --public-source path/to/public-p40`. This private test is synthetic only and requires local SQLite/Python3.11, not real customer files or remote API.

## Next steps and release HOLD
1. Owner approves exactly which real LA event/approval provenance, source and privacy mapping can be consumed. No public copying of private schemas or raw customer records.
2. Independently test genuine consented local real-source run against actual event semantics, including failed, skipped, resumed and unseen steps; verify identity and provenance, customer false positives; enforce bounded rollback.
3. Test physical buyer Windows10/11 with Defender/SmartScreen and customer report usability, legal licensing/privacy retention/rights, support and pilot. Explicit owner approval required for signing, distribution, deployment or retail listing.
4. No Vercel/Production; do not call `Ready` or CI PASS proof of real buyer behavior.

**Updated:** 2026-11-12 KST. Exact feature/test CI proof scope above; document/CI artifact SHA and artifact ID need separate final check.
