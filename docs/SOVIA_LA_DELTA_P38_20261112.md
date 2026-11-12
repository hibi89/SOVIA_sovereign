# SOVIA P38 — verified synthetic LA review delta (2026-11-12 KST)

## Design and choice
The standalone P2 synthetic LA reviewer previously produced one independently consistency-checked owner report, but could not compare two reports without reading potentially sensitive source records. This feature adds a *source-only*, offline, aggregate review-delta CLI. Do not treat the result as authenticated LA evidence or chronological truth.

- **Option A**: compare raw plan, audit, and observation documents or unverified report JSON. Easier but repeats sensitive data handling, may disclose row IDs, and invites unauthenticated summaries; rejected.
- **Option B (chosen)**: require both original unmodified P2 review bundles to pass existing fixed-file manifest/JSON/HTML consistency checks, then tally only allowlisted severity counts (CRITICAL/HIGH/MEDIUM/LOW/UNKNOWN) by plan, post-audit, and reconciliation category; accept operator-supplied order as an assertion only. No new service, package dependency or customer data. Cheaper and compatible with existing P2 source; data minimization and safe failure improved.

## Implemented
- `sovia_la_review_delta.py` standalone `python -I -B` compatible script, explicit local module loader, read-only with `--synthetic-only` acknowledgement. It checks both bundles before/after, refuses same directory, symlink, altered output, extra or missing file, oversize or unsupported severity; checks SHA256 before/after. Returns aggregate per-severity previous/current/delta, count changes and digest but **no IDs, events, policy, targets, source pointers or raw log rows**.
- All results remain `REVIEW_REQUIRED_UNAUTHENTICATED` even if risks decrease or identical documents are compared. No execution authorization, real LA evidence verification, or validated chronology. Bytes/metadata can be concurrently altered between check steps; checks are best-effort, not TOCTOU protection.
- `tests/test_sovia_la_review_delta.py`: 7 tests for a new missing-observation risk, no disclosure, same report never cleared, same-path refusal, tamper/symlink refusal, and actual isolated `-I -B` CLI refusal+success. Existing P2 portable ZIP **v0.13 is unchanged and does not include this source-only P38 command**.

## Exact evidence
- Functional+test commit `cb41fcf85bd8f2b9cc9aeb430184ed2a5056ffa5`.
- [GitHub Actions run #43204176313](https://github.com/hibi89/SOVIA_sovereign/actions/runs/43204176313), PR #71: **4/4 SUCCESS** at exact source SHA. Each environment discovered **924** tests, **0 FAIL**:
  - Windows Python 3.11 and 3.13: **913 PASS, 11 SKIP** each.
  - Ubuntu Python 3.11 and 3.13: **902 PASS, 22 SKIP** each.
  - Existing Windows hosted CMD/Edge/portable ZIP tests and Ubuntu standalone ZIP smoke remain green. Source-only new delta is covered by the 7 new tests; not packaged in existing ZIP.
- Two intermediate source runs **failed then were repaired**, do not mistake for successful:
  1. #43203817892: isolated `python -I` omitted script module search path; corrected with explicit local module spec loading, matching SOVIA's established isolated CLI design.
  2. #43203995169: imported review module under a separate name so its `ReviewError` class differs from the ordinary imported class; corrected test expectation to import the delta module's actual class. Final #43204176313 green. No unresolved known CI regression.
- The original 13-file v0.13 package SHA/historical v0.10/v0.11.2/v0.12 frozen packages remain untouched. No customer files/API/credentials, external AI/paid service, production, security/permissions, or release change.

## Engineering scoring and remaining work
- Old **85% provisional engineering**; P38 adds **+2pp provisional** for actual bounded source-only cross-report risk-delta function and 4-platform regression, weighted against unchanged full product blueprint. **Now 87% provisional; NOT 95%; sale RELEASE HOLD.** Percent is a reasoned milestone estimate, not CI pass percentage, customer acceptance, legal eligibility or LA authenticity.
- Unclosed requirements: approved versioned genuine first-party Lightning Azent event/receipt projection, exact source consent/provenance and real sanitized local ingestion, parity/false-positive review, customer Windows10/11/Defender/SmartScreen/print, customer pilot and licensing/signing/support. A packaged next-version delivery of P38 is pending before calling the operator ZIP feature complete.

## Reproduce
Create two **synthetic-only** review folders using existing `sovia_la_owner_review.py --synthetic-only` with distinct fabricated observation examples, then:
```sh
python -I -B sovia_la_review_delta.py --previous ./old-review --current ./new-review --synthetic-only
python -m unittest discover -s tests -v
```
The new delta code does **not** rewrite or delete either review directory and creates no files. Vercel/Production: not applicable.

## Next / approval
Package P38 in a **new** independently versioned offline candidate while preserving v0.13, then full isolated release ZIP tests if this is prioritized. For actual LA/customer integration obtain an owner-approved minimal sanitized receipt contract; do not copy private HAE/LA internals into this PUBLIC repository. Physical Windows security acceptance and sale require owner decision. Date/verification: 2026-11-12 KST, exact feature SHA and run above; documentation commits are not new feature-test SHA.
