## P2 follow-up — official pinned public API workflow key references (2026-10-27)

[**N8N_PINNED_PUBLIC_SCHEMA.md**](N8N_PINNED_PUBLIC_SCHEMA.md) records verified GitHub source **tag, release commit SHA, schema blob SHA and top-level Public API workflow YAML fields** for `n8n@1.123.88` and `n8n@2.44.7`. A separate `sovia_n8n_pinned_reference.py` does **synthetic key-only comparisons** and blocks ALL raw import (including exact key matches). It is **not evidence of real n8n API support** or version-specific execution data compatibility, nor an upgrade to the mock probe. No existing converter/portable behavior changes.

---

# SOVIA P2 — n8n source-profile / version-claim key-only probe

**Scope: synthetic-only source capability probe, NOT native n8n version support.** It never ingests real n8n workflow exports, execution responses, node parameters, credentials, items, binary data, runData or customer/prompt contents. No n8n API credentials/network.

## Primary design decision

| Candidate | Advantage | Safety, upkeep, accuracy | Decision |
|---|---|---|---|
| Auto-import raw n8n workflow/execution exports for claimed 1.x/2.x versions | Faster live integrations | Raw execution data can contain personal info/secrets, unverified exact version-specific API schema, high burden to prove provenance and PII removal | **Not implemented** |
| Strict synthetic **key-name-only** shape profiler with explicit source family and claimed version | Cheap offline contracts, counterexamples and no raw values | Does **not** establish genuine vendor compatibility or legal source authority | **Implemented** |

n8n documentation distinguishes executions (including execution data and workflow status) from workflow editing/sharing/export and has separate external binary data handling. For background, see:
- [n8n all executions](https://docs.n8n.io/workflows/executions/all-executions/)
- [n8n workflow sharing/export permissions](https://docs.n8n.io/workflows/sharing/)
- [n8n external binary data](https://docs.n8n.io/hosting/scaling/external-storage/)

These links are **design context only**, not attestation that SOVIA has validated n8n 1.x or 2.x exports. Versions `1.0.0` and `2.6.4` in the examples are *fabricated claims for classification* and were not verified against a specific live installation or downloaded release fixtures.

## Contract

`sovia_n8n_compatibility.py` accepts exactly:
```json
{
  "schema_version": "sovia.n8n_compatibility_probe.v1",
  "synthetic_only": true,
  "source_profile": "sovia_sanitized_metadata_v1",
  "claimed_n8n_version": "not_applicable",
  "field_keys": ["format", "workflow_id", "execution_id", "steps"]
}
```

Supported **probe labels**, not supported importers:
- `sovia_sanitized_metadata_v1`: exact four synthetic SOVIA envelope key names are recognized; missing ones block; arbitrary extra keys block. No n8n version claim allowed.
- `mock_n8n_workflow_export`: a fabricated subset of top-level workflow field names (names only). Claimed semantic-version strings with major 1 or 2 produce **UNVERIFIED_RAW_PROFILE_BLOCKED**; unknown major produces **UNRECOGNIZED_VERSION_BLOCKED**.
- `mock_n8n_execution_api`: fabricated names-only execution summary (no run values). Same blocked logic.

Any data-like/credential/binary/parameter/raw-execution field name is refused outright; keys must be unique, short and follow a fixed grammar. Malformed envelopes, unsupported profiles, duplicate keys and oversized input fail closed. The probe has no data-transforming option or "permit" switch. Every result states:
`raw_n8n_import_supported:false`,
`n8n_version_independently_verified:false`,
`native_n8n_schema_compatibility_verified:false`,
`source_authorization_verified:false`,
`payload_inspected:false`, and
`conversion_performed:false`.
Even sanitized keyset success is **only a synthetic key-name match**, not proof that values, PII cleanup, schema or customer consent are valid.

## Commands

```powershell
py -3 -I -B sovia_n8n_compatibility.py --input examples/synthetic_n8n_probe_sanitized_v1.json --synthetic-only
py -3 -I -B sovia_n8n_compatibility.py --input examples/synthetic_n8n_probe_mock_1x.json --synthetic-only
py -3 -I -B sovia_n8n_compatibility.py --input examples/synthetic_n8n_probe_mock_2x.json --synthetic-only
py -3 -m unittest discover -s tests -p test_n8n_compatibility.py -v
```

Exit **0** only for recognized synthetic SOVIA four-key envelope, **3** for an unsupported/unverified raw or missing-key profile, **2** for invalid or private-payload-shaped manifests. Results contain aggregate missing-key count and a version **bucket** only; no values or paths printed.

## Boundaries / future genuine adapter

`sovia_n8n_sanitized.py` remains the sole existing conversion pathway for **already sanitized** metadata and enforces its own strict event validation. Its `approved-local` path also requires a self-asserted operator hash manifest plus preflight, but this cannot verify identity, consent, or complete PII absence. This new probe never bypasses those checks.

Before a real n8n version adapter can be claimed, separately approve the source scope, select pinned n8n release tags/API schemas, build mock fixtures *from authorized public non-sensitive reference definitions*, provide a local allowlisted upstream sanitizer, prove no raw payload/credential persistence, and test malformed/unsupported versions. No such live compatibility test, software publication, portable ZIP update, customer input or paid deployment is performed here. The old v0.10 12-file ZIP and default `main` are unchanged.
