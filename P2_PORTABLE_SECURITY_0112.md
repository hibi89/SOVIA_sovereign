# SOVIA Audit Lite v0.11.2-beta — direct-mode metadata safety floor

## Defect fixed
In v0.11.1-beta, `sovia_n8n_direct_audit.py` applied the existing PII/credential **heuristic pattern** preflight only under `--mode approved-local`. Selecting `--synthetic-only` skipped that check, even when a pre-sanitized n8n-like metadata envelope contained recognizable personal or secret-like tokens. A mode flag is not cryptographic proof of fabricated data.

## Fix
The direct reporting flow now checks the same source and policy metadata in **both** modes before rendering any report. Specifically, it runs `sovia_pii_preflight.assert_no_high_risk_patterns(document, policy_doc)` after strict conversion and before HTML/JSON serialization. `approved-local` still additionally verifies the existing unsigned hash-bound operator assertions. Rejected cases use one constant `CONTRACT_OR_REVIEW_REJECTED` code; no matched values, tokens, local paths, output files or staged files are exposed.

The packaged `owner_p2_selfcheck.py` now requires the direct CLI to report `pii_pattern_scan_executed: true`, `pii_absence_proven: false`, `source_authorization_independently_verified: false`. A missing privacy floor causes the synthetic owner self-check to fail.

## Regression and compatibility

- New focused cases insert a fabricated Luhn-compatible number in a synthetic step identifier and a token-like pattern in the synthetic policy. Both must be rejected without report files; a CLI rejection must never echo the sensitive field or local path.
- The existing clean synthetic 3-event, 5-finding direct audit still works and must report that the heuristic ran.
- Existing Windows+Ubuntu Python 3.11/3.13, v0.10 legacy ZIP and v0.11.2 extracted-package regression gates remain mandatory.
- Because the packaged direct auditor, PII module, owner self-check and package README changed, this is a **new v0.11.2-beta** archive, not an overwrite of the historic v0.11.1-beta ZIP.

## Explicit limits

This fix protects only the **direct pre-sanitized n8n-like source-to-report path**; the basic canonical JSON auditor, separate sanitized converter in synthetic mode, other developer tools and pre-existing original report export are not thereby certified as PII-free. It is a pattern detector, not complete PII detection or de-identification. Deliberately disguised or new identifiers can escape detection. Source user intent and attestation claims are not independently authenticated. There is no real native n8n API connection, legal authorization, real customer test, PDF visual approval, antivirus approval, signed release or production service. Actual owner Windows/browser/manual checks remain NOT_CHECKED.

Use private authorized and independently sanitized sources only. All test data and regressions in the public repo remain fabricated.
