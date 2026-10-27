# SOVIA P2 — synthetic evidence binding and negative privacy regression

Status: synthetic-only research/QA gate; **not a signed provenance system, real-origin authentication, n8n integration, legal permission, PII certification or production release**.

## Architectural decision

| Approach | Performance/cost | Risk/maintenance | Decision |
|---|---|---|---|
| Add source signatures, trust store, identities, external attestation and automatic real-n8n import | Expensive key distribution, trust, lifecycle and consent requirements | Cannot reliably prove a customer source without owner-controlled credentials/authority; unsafe for public synthetic repo | **Deferred until separately approved** |
| Verify SHA-256 **self-consistency** across fabricated summary, approved example policy and recomputed canonical output, with metadata heuristic scan | Offline Python stdlib, negligible incremental cost on bounded 1 MiB JSON | Hashes can be recomputed by anyone; heuristic privacy detection can miss data | **Implemented for synthetic QA only** |

The standalone `sovia_synthetic_evidence.py` operates read-only: it does not write output, retrieve API data, call the network, copy private source, alter the audit rules, or permit raw n8n execution import.

## Contract

An operator-authored unsigned manifest is expected to have exactly these keys:

```json
{
  "schema_version": "sovia.synthetic_evidence.v1",
  "synthetic_only": true,
  "origin_claim": "fabricated_offline_fixture",
  "pinned_release_tag": "n8n@2.44.7",
  "source_sha256": "<lowercase 64-hex SHA256 of canonicalized synthetic source JSON>",
  "policy_sha256": "<lowercase 64-hex SHA256 of canonicalized example policy JSON>",
  "expected_canonical_sha256": "<lowercase 64-hex SHA256 of derived SOVIA canonical JSON>"
}
```

The displayed placeholders are **not** a ready manifest. Tests build valid manifests using the already-implemented `sovia_n8n_sanitized.canonical_sha256()` and `sovia_n8n_execution_bridge.convert_synthetic()` functions, then mutate them to confirm rejection. These are deterministic hashes of parsed JSON (sorted keys, UTF-8, compact separators) and do not verify byte-for-byte original file contents. Both input files and the manifest are read with the same bounded 1 MiB input parser (duplicate key and nesting protections). Existing synthetic execution bridge and five-rule canonical evaluator are reused unchanged.

The gate:
1. Refuses unknown manifest fields, unpinned tags, incorrect source tag/claim and noncanonical hash formats.
2. Runs existing `sovia_pii_preflight.assert_no_high_risk_patterns` against the fabricated source and policy **before** conversion. It catches selected simulated email/mobile/ID/IP/UUID/key/token patterns but is not exhaustive.
3. Compares hashes for source and policy in constant-time, performs the existing strict bridge conversion **in memory**, scans derived canonical JSON again and compares its hash against the expected canonical hash.
4. Outputs only aggregated status flags, including `provenance_independently_authenticated:false`, `manifest_signature_verified:false`, `customer_authorization_verified:false` and `pii_absence_proven:false`.

A tampered summary with the same event result changes the source hash and is detected **if the manifest stays unchanged**. If a party modifies both source and manifest and recomputes all three hashes, the gate may accept the new fabricated dataset. **It does not prove authenticity, an independent human signature, data controller consent, sanitizer correctness or privacy**. The presence of `synthetic_only:true` is an unverified claim.

## Commands

```powershell
py -3 -m unittest discover -s tests -p test_synthetic_evidence.py -v
py -3 -I -B sovia_synthetic_evidence.py --input examples/synthetic_n8n_bridge_2x.json --policy examples/demo_policy.json --manifest LOCAL_FABRICATED_MANIFEST.json --synthetic-only
```

The second example works only after a valid locally generated **synthetic** manifest is supplied; this repository does not provide a signature/trust issuer. No real n8n/customer payload should be supplied. CLI returns exit 0 for consistency checks, 2 for sanitized rejection codes. The result never contains original values, input paths, matches or identifying data.

Regression cases include changed source metadata, stale policy or expected canonical hash, deliberately forged replacement manifests, unpinned claims, raw object fields, simulated credential and PII strings, oversized or duplicate JSON, symlink input, CLI non-disclosure and no-network/no-write checks. None of these constitute real-world sensitivity or false-negative measurements.

## Next real-world gates (still open)

Actual source provenance needs owner-approved authenticated producer/consumer identities, immutable evidence custody and signing-key lifecycle plus independently verified installed n8n build/version; actual customer data needs explicit data-controller authorization, upstream redaction/retention guarantees and independent privacy testing. On-device Windows Defender/SmartScreen, Korean report visual QA, release signing and commercial acceptance are separate outstanding tasks. Existing 12-file v0.10 portable ZIP and `main` remain unchanged.
