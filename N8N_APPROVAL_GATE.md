# SOVIA P2 operator-claim gate for previously sanitized local event metadata

**Status:** Synthetic-only implementation and local operator attestation mechanism. It is **NOT** a certificate of consent, a real n8n export parser, a PII scrubber, a legal-retention enforcer, or a production/customer-approved integration.

## Two considered designs

| Design | Compatibility | Cost/performance | Maintainability | Consequence |
|---|---|---|---|---|
| Enforce new approval manifest for **every** conversion | Breaks existing synthetic demonstrations and scripts | One extra manifest for all inputs; no paid services | Simple uniform policy but unnecessarily invasive | Rejected |
| Keep existing `synthetic` mode; introduce explicit `approved-local` mode requiring operator assertions bound to exact source and policy content | Existing P1/P2 synthetic flows unchanged | Stdlib SHA-256 over bounded JSON; zero paid services | Separate, testable gate and strict disclosures | **Chosen** |

## Trust boundaries and limitations

Data owner obtains legal basis/authorization **outside SOVIA**, reviews local source metadata and customer retention policy, and explicitly supplies a review manifest. SOVIA verifies that the **operator supplied exact true flags**, that both parsed local files match SHA-256 digests in the manifest, and that the UTC review expiry is valid and at most 30 days in the future. The manifest is neither signed nor bound to an authenticated identity, so **any operator can forge it**. A valid manifest proves only *claim format + integrity binding*, **not** real consent or effective sanitization. The original n8n synthetic-contract adapter still rejects unknown fields, raw execution data, node params, prompts and credentials. It does not independently inspect raw content or determine GDPR/PIPA compliance.

The exact JSON manifest keys (no extras permitted):

```json
{
  "schema_version": "1.0",
  "scope": "locally_reviewed_metadata",
  "source_sha256": "<64 lowercase hex SHA-256 of canonicalized parsed source JSON>",
  "policy_sha256": "<64 lowercase hex SHA-256 of canonicalized parsed policy JSON>",
  "source_authorized": true,
  "fields_reviewed": true,
  "retention_plan_documented": true,
  "expires_utc": "YYYY-MM-DDTHH:MM:SSZ"
}
```

The placeholders in this *schema explanation* are not real hash values. Compute a digest over the **same parsed JSON object used for conversion** using `sovia_n8n_sanitized.canonical_sha256(document)` (UTF-8; `json.dumps(sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`). This is content binding, not proof of publisher authenticity or customer approval. Do not embed customer names, emails, tokens, locations, instructions, or policy details in the manifest.

Sample isolated Python commands (using synthetic source, no external network):

```sh
python sovia_n8n_sanitized.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --output NEW_synthetic.json
python -m unittest discover -s tests -p test_n8n_operator_gate.py -v
```

For the *operator-claim pathway*, first produce and review a manifest **locally** with appropriate assertions and matching hashes; no automatic approval, dummy consent or auto-manifest generation is provided. Use a NEW output path:

```sh
python sovia_n8n_sanitized.py --input LOCAL_SANITIZED.json --policy LOCAL_POLICY.json --mode approved-local --attestation LOCAL_REVIEW.json --output NEW_CANONICAL.json
```

The converter reads files as bounded JSON (1 MiB each; up to 1,000 steps) and publishes a **new canonical JSON** only after validation. In `approved-local` mode, before loading the source, policy, or operator manifest, the converter now inspects the *lexical path and all ancestor components* without following symlinks and refuses POSIX symlinks and reported Windows NTFS reparse junctions; it likewise rejects a linked output-parent or an occupied output leaf. This best-effort preflight helps avoid silently redirected approved files and destination folders, but cannot exclude path-replacement races or guarantee confinement against an adversarial local process. Linked folders (including some mapped/sync folders) may need an explicit ordinary directory instead. `synthetic` demonstration mode retains its previous path handling for compatibility. It never modifies source, policy, review file, prior report or SQLite. It prints `CONVERTED_WITH_UNVERIFIED_OPERATOR_CLAIMS` and `authorization_independently_verified:false`, never `APPROVED` or `CONSENT_VERIFIED`. Absent/false acknowledgements, changed documents, invalid/expired/too-long-lived expiry, unknown keys, source aliases, malformed/deep JSON and occupied output paths fail closed with structured codes and no path or payload echoed.

**The existing synthetic mode** remains the default for backward-compatible synthetic demos. It is not suitable as an authorization bypass for real customer input: a manually typed CLI mode does not enforce the identity or legal status of data. The `approved-local` mode similarly does not turn unreviewed customer logs into authorized ones. Before any pilot, implement authenticated/operator-reviewed provenance, approved actual n8n version and field mapping, preflight content/PII controls, accessible deletion/backup lifecycle, written consent/contract boundaries, and independent Windows/Defender/browser/Korean-PDF testing.

This source unit is **not included in the existing 12-file SOVIA v0.10 portable package**. `main`, customer production and Vercel are not affected.
