# P2 — local owner Windows evidence consistency checker

**Development-source-only** `sovia_owner_evidence.py` cross-checks the existing v0.10 inner portable ZIP, the old synthetic self-check JSON and a separate human-supplied manual-review JSON. It is **NOT** a device attestation, authenticated signature, legal customer approval, independent witness, security certification or commercial release gate.

## Chosen architecture

| Candidate | Consequence | Selection |
|---|---|---|
| Set the old self-check's manual fields to PASS from its automated results | Incorrectly certifies HTML/PDF visuals and Windows antivirus from CI or a self-declared value | Rejected |
| **Separate read-only checker** with actual ZIP SHA-256 verification, strict self-check contract and manually entered review statuses | No changes to old v0.10 artifact or owner selfcheck; claims are transparent, bounded, offline and never promoted to independent proof | Implemented |

## Required inputs

1. `--portable-zip`: **inner** 12-file v0.10.0-beta portable ZIP (not the outer GitHub Actions artifact download). The checker hashes actual local bytes and requires one of **two explicit pinned synthetic beta build hashes**: archived original `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`, or writer-hardening source rebuild `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`. Both contain 12 files and are unsigned; a matching digest is not trusted provenance or real-PC attestation. Missing/symlink/oversized/altered ZIP fails closed. It does not extract ZIP or run embedded executables.
2. `--selfcheck`: existing `SELF_CHECK_RESULT.json` produced by unchanged `RUN_SELF_CHECK.cmd` and `owner_selfcheck.py` on a computer. Checks required: v0.10, purpose synthetic only, system label Windows, Python >=3.11, `AUTOMATED_PASS_MANUAL_PENDING`, six automatic PASS checks, 3 events/5 findings/1 report, old five manual fields still `NOT_CHECKED`, and documented optional PDF status.
3. `--manual-review`: a **separately written local** JSON with only these fields:

```json
{
  "schema_version": "sovia.owner_windows_review.v1",
  "manual_checks": {
    "audit_html_visual": "NOT_CHECKED",
    "dashboard_html_visual": "NOT_CHECKED",
    "antivirus_or_smartscreen": "NOT_CHECKED",
    "korean_pdf_visual": "NOT_TESTED"
  }
}
```

All mandatory items accept only `PASS`, `FAIL` or `NOT_CHECKED`. Optional PDF also accepts `NOT_TESTED`. An automatic `SKIPPED_REPORTLAB_MISSING` or `SKIPPED_KOREAN_TTF_MISSING` cannot be paired with a PDF `PASS`. A `FAILED_OPTIONAL_PDF` automatic result or an explicit human PDF `FAIL` leaves the review **BLOCKED**, even when other fields are declared PASS. Existing reports and ZIP are **never** overwritten; the checker creates no files and prints only aggregate status and bools.

## Offline command example

```powershell
py -3 -I -B sovia_owner_evidence.py --portable-zip "local-inner-portable.zip" --selfcheck "SELF_CHECK_RESULT.json" --manual-review "review.json"
```

The paths are examples; do not upload actual owner machine details, screenshots or results to PUBLIC GitHub. CLI exit **0** means only `OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED`, **3** means `MANUAL_REVIEW_PENDING` or `MANUAL_REVIEW_BLOCKED`, and **2** means rejected schema/auto-evidence/hash mismatch. Output always states `owner_identity_verified:false`, `owner_device_execution_independently_verified:false`, `manual_observations_independently_verified:false`, `commercial_release_approved:false`. It cannot prove that claimed Windows execution occurred on the owner's PC or that manual decisions are truthful. Do not use status 0 to advertise commercial release. This is a **separate source-only** test aid, not added to the old portable ZIP.

## Verification and remaining work

Focused unit tests use a **fabricated Windows self-check record**, a locally built synthetic portable ZIP and fabricated manual claims; they never connect to the real owner's PC. Run `python -m unittest discover -s tests -p test_owner_evidence.py -v` and full Windows/Ubuntu Python 3.11/3.13 CI with the existing v0.10 ZIP smoke. This is NOT actual PC acceptance.

Real-device HTML/dashboard legibility, browser/antivirus/SmartScreen observations, optional Korean PDF visual, customer authorization, n8n native metadata compatibility, privacy/legal retention, installer/release support and owner commercial permission remain open. Follow [OWNER_WINDOWS_ACCEPTANCE.md](OWNER_WINDOWS_ACCEPTANCE.md) for in-person steps; never bypass antivirus or upload protected input.
