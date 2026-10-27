# SOVIA P2 — offline metadata privacy-pattern preflight

**Development feature, synthetic-only evidence.** This is a heuristic **rejection** layer, not automatic anonymization, a complete personal-data detector, approved n8n import, consent proof, legal compliance certification, or a production release.

## Design trade-offs

| Option | Speed and expense | Accuracy and maintenance | Choice |
|---|---|---|---|
| Automatically mask any plausible PII in raw n8n logs | Unbounded raw data access/complex redaction; requires vendor-format upkeep and extensive tests | Misses embedded secrets or corrupts tool/evidence metadata; difficult to prove safety | Not implemented |
| Reject suspicious patterns in **already sanitized allowlisted metadata** before any report is published | Local stdlib scanning, bounded input, no network/cost | False negatives and false positives; rules require review | **Implemented for `approved-local` only** |

## What the program actually checks

`sovia_pii_preflight.py` recursively scans decoded source and policy string values (and their keys) before local `approved-local` conversion. It heuristically rejects:

- Email-address patterns, Korean mobile numbers (including common separators), Korean resident registration number-shaped sequences
- Valid IPv4 and IPv6 literals (including bracketed URLs and scoped IPv6), UUID-shaped identifiers, payment-card numbers passing Luhn
- AWS-style access keys, common API-token prefixes, JWT-shaped strings and opaque identifiers of 40+ characters

These are **synthetic patterns**, not an exhaustive identification system; contextual names, organization IDs, encoded values, indirect inference, IPv6-like identifiers embedded in longer tokens, arbitrary hashes, and secrets of other shapes may evade it. Some benign addresses, internal IPs, IDs or randomly generated references will be rejected. Inputs should be standardized to short, operator-approved nonpersonal codes *before* being imported, and any risk assessment needs separate human review.

The scanner returns only a generic code (`PREFLIGHT_REJECTED`) on suspected content, never a matched value, path, token or detailed location. It never modifies or transmits inputs. It has bounded traversal (depth 16, 20,000 nodes, 4,096 characters per string) and no third-party dependencies.

## Behavior and scope

- **`--mode approved-local`:** canonical schema validation → local metadata preflight → verify existing operator review claims and source/policy SHA-256 → create a NEW canonical JSON only after all conditions pass. If either preflight or assertion fails, it emits a generic error and no output.
- **`--mode synthetic`:** retains previous public-demo behavior without requiring a review manifest or running this new preflight. This mode is *only for artificial fixtures* and **must never be used as a customer-data authorization workaround**.
- The success JSON reports `pii_pattern_scan_executed` and always `pii_absence_proven:false`, plus `authorization_independently_verified:false`. A clean scan is *not* an assurance that no private content exists.
- The old 5-rule audit, CSV/PDF/SQLite history, dashboard, retention inventory, v0.10 twelve-file portable ZIP and Windows self-check are not edited or repackaged. The new preflight and approved-local adapter are development-source functions only.

## Example using synthetic data

```sh
python sovia_n8n_sanitized.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --output new-demo.json
python -m unittest discover -s tests -p test_pii_preflight.py -v
```

For an operator-reviewed local input, also supply `--mode approved-local --attestation REVIEW.json` with the matching claims/digests from [N8N_APPROVAL_GATE.md](N8N_APPROVAL_GATE.md). Do **not** upload personal logs, screenshots, credentials, local reports or manifest content to this PUBLIC GitHub repository. n8n API compatibility, authentic legal permission, real-customer source field mapping, storage/backup erasure policy, false-positive adjudication and owner's Windows visual/AV/PDF acceptance remain pre-sale blockers.

## Verification gate

Run GitHub Actions Windows/Ubuntu × Python 3.11/3.13 full unittest and portable smoke. The isolated cases use synthetic placeholders such as well-known card test digits; **no real person or payment credentials**. CI success means only the defined patterns and prior functions were exercised, not that actual PII was comprehensively removed.
