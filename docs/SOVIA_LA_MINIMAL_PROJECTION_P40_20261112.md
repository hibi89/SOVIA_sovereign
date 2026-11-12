# SOVIA P40 — public-safe minimal LA-like synthetic projection cross-check (2026-11-12 KST)

## Goal and architectural decision
SOVIA P39 (90% provisional engineering) has an independently verified, source-only v0.14 synthetic LA review-delta package. An actual first-party Lightning Azent receipt is a future integration gate, not something that a public SOVIA package may silently import from the user's PRIVATE HAE/LA repository.

Two approaches were evaluated:
- **A: Directly accept/commit private LA `evidence()`, underlying SQLite ledger, audit events, step IDs or original source JSON in public SOVIA.** Functionally convenient but exposes private implementation/data and falsely treats a producer's self-verified status as independent human consent or authenticated SOVIA evidence. **Rejected.**
- **B: Define a strict, public, source-free synthetic-only minimal projection** with a declared plan fingerprint, bounded step/outcome totals, asserted terminal audit count and explicit `source_authenticated=false` / `approval_authenticated=false` / `stream_completeness_verified=false`. Compare that projection read-only against an **already verified synthetic SOVIA owner-review bundle**, refusing unexpected keys and any asserted authentication. **Selected.** No external API, packages, private code, customer records or system permissions.

A producer's plan SHA and a SOVIA plan fingerprint can use **different canonical encodings**. Matching strings are not proof of the same workflow or run; a real private producer/translator and an explicitly approved canonical plan mapping contract are REQUIRED before treating plan comparisons as meaningful cross-product parity.

## Delivered code
- `sovia_la_minimal_projection.py`: standalone `python -I -B` compatible, read-only offline tool, imports only adjacent PUBLIC `sovia_la_owner_review.py` via explicit module loader.
- CLI requires `--synthetic-only` **before** reading either file; a maximum 16KiB single synthetic projection file, known exact JSON fields, zero unknown raw metadata, integer non-bool bounded counts, canonical SHA256 syntax, and refusal of symlink/reparse paths, duplicate JSON keys or oversized input. Projection's three authentication/completeness booleans MUST be false.
- Reuses independent bundle verifier for original owner-review `manifest.json` / `review.json` / `review.html` and rechecks source bytes around analysis. Detects claimed plan-digest mismatch, planned-vs-recorded count mismatch, incomplete/failed steps, missing claimed terminal audit and preserved SOVIA risk findings.
- Returns only aggregate counts and reason codes; never raw event rows, step IDs, private workflow plan, tokens, customer paths, execution permission, or a trustworthy authenticated result. **Status ALWAYS `REVIEW_REQUIRED_NOT_AUTHENTICATED`**, including the count-matching case. Source SHA is not a signature, no race-free filesystem confinement guarantee.
- `tests/test_sovia_la_minimal_projection.py`: **12 synthetic** normal/adversarial checks including isolated real `-I -B` subprocess, refusal without explicit acknowledgement, tamper, duplicate keys, linked input, oversized projection, invented `authenticated=true`, unknown raw-event fields, forged counts/status, original SHA preservation and existing SOVIA risks retained.

## Exact executed verification
- Feature + all 12 tests committed as `63c9a329de71470089e0a866e802a20ce9a48ad6`, public `hibi89/SOVIA_sovereign@feature/kmong-la-review-p2-20261112`, draft PR #71 unmerged.
- [GitHub Actions #43210005055](https://github.com/hibi89/SOVIA_sovereign/actions/runs/43210005055) at **exact source SHA** **4/4 SUCCESS**, 940 discovered per job, 0 FAIL:
  - Windows Python3.11: 929 PASS /11 SKIP; Windows Python3.13: 929 PASS /11 SKIP.
  - Ubuntu Python3.11: 917 PASS /23 SKIP; Ubuntu Python3.13: 917 PASS /23 SKIP.
  - The old v0.13/0.14 ZIP, hosted Windows CMD/Edge offline tests, and portable source review smoke remained PASS. **P40 is source-only and is NOT in the existing v0.14 customer candidate ZIP.**
- CI exercises public fabricated metadata, **NOT actual Lightning Azent producer receipts** or first-party run-to-report identity, genuine owner approval, or customer privacy/licensing/physical PC acceptance.

## Versioned minimal synthetic input fields
A caller provides exactly these top-level keys:
```json
{
  "schema_version": "sovia.la_minimal_projection.synthetic.v1",
  "source_kind": "DECLARED_LA_LIKE_SYNTHETIC",
  "synthetic_only": true,
  "source_authenticated": false,
  "approval_authenticated": false,
  "stream_completeness_verified": false,
  "plan_fingerprint_sha256": "64 lowercase hex characters from a matching synthetic SOVIA plan",
  "run_status": "completed",
  "steps": {"declared": 2, "recorded": 2, "completed": 2, "skipped": 0, "failed": 0, "running": 0},
  "audit": {"event_count": 4, "terminal_completion_claimed": true, "write_approval_claims": 1}
}
```
This is a schema illustration, not a distributable live receipt, and the fingerprint example text is a placeholder that must be substituted in a synthetic test. No plan raw text or real LA data is permitted in this mode.

```sh
python -I -B sovia_la_minimal_projection.py --projection NEW_SYNTHETIC_MINIMAL.json --review-dir EXISTING_SYNTHETIC_SOVIA_REVIEW --synthetic-only
python -m unittest discover -s tests -v
```

## Engineering milestone / unclosed gates
**Maintain 90% provisional engineering / P95 NOT ACHIEVED / commercial RELEASE HOLD**. P40 closes an input minimization, explicit source boundary and fail-closed cross-check design gap, but should **not** receive a new percentage increment until a real first-party LA adapter with approved versioned mapping and actual source-backed integration test is verified. No Production/Vercel applies.

Next step is a **PRIVATE, owner-authorized LA producer-side adapter** that exports only a minimal projection from genuinely consented source; this public repo must never import private code, raw plan, original SQLite ledger or private events. Independently validate the round-trip on a clean local environment, with authenticated provenance and identity/authorization separately evaluated. Physical Windows10/11 Defender/SmartScreen, customer pilots, privacy/retention/licensing/support and seller GO remain open.

**As-of:** 2026-11-12 KST. Exact function/test SHA and hosted OS matrix above. Documentation-only HEAD commits are not the tested functional SHA.
