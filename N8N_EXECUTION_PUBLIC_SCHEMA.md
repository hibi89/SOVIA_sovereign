# SOVIA P2 — officially pinned n8n Public API getExecution schema research

**Only tagged public OpenAPI source field names are inspected. No n8n request, execution import, raw event conversion, real API compatibility test, or customer data.** This research is separate from the n8n Public API *workflow* schema contract in [N8N_PINNED_PUBLIC_SCHEMA.md](N8N_PINNED_PUBLIC_SCHEMA.md).

## Exact official GitHub source provenance (checked 2026-10-27)

Repository: [n8n-io/n8n](https://github.com/n8n-io/n8n). No unpinned branch or live n8n instance is used at runtime.

| Release tag | Pinned release commit | Public API getExecution response schema | Blob SHA |
|---|---|---|---|
| `n8n@1.123.88` | `6b88ad7f6be54df9f26efe17e0c249e345b40375` | [schemas/execution.yml](https://github.com/n8n-io/n8n/blob/n8n%401.123.88/packages/cli/src/public-api/v1/handlers/executions/spec/schemas/execution.yml) | `e20e27a02402563f3904c8b0468d56d32a42196c` |
| `n8n@2.44.7` | `cbe3950c51759577f9e611d28f8f5cd01828eaef` | [paths/getExecution.generated.yml](https://github.com/n8n-io/n8n/blob/n8n%402.44.7/packages/cli/src/public-api/v1/handlers/executions/spec/paths/getExecution.generated.yml), embedded response properties | `329097122a6bfda7410314ff4ca73878c34b6918` |

For 1.x, [executions.id.yml](https://github.com/n8n-io/n8n/blob/n8n%401.123.88/packages/cli/src/public-api/v1/handlers/executions/spec/paths/executions.id.yml) connects the GET response to `../schemas/execution.yml` (operation blob `f8b60da7a25c09cdad6d31d4f7b22f4a430a2d58`). For 2.x, the generated operation embeds its own response schema; the former `spec/schemas` directory does not exist at that tag. These Git identifiers are **source provenance only**, not evidence of installed n8n versions, request behavior, authorization, payload privacy or source compatibility.

## Observed public API getExecution 200 schema differences

- 1.x definition: **12** top-level property names.
- 2.x definition: **23** top-level property names (**11 added, zero removed** *within these two source definitions*): `binaryDataSizeBytes`, `createdAt`, `dataTooLargeToDisplay`, `deduplicationKey`, `deletedAt`, `jsonSizeBytes`, `storedAt`, `tracingContext`, `usedPrivateCredentials`, `workflowData`, `workflowVersionId`.
- Declared types change **number → string** for `id`, `workflowId`, `retryOf` and `retrySuccessId`. This is exactly what the two YAML files declare; actual service versions may differ.
- The 2.x GET response explicitly marks **19 fields required**. The 1.x standalone `execution.yml` does **not specify** a `required` array. Therefore absence of a 1.x required declaration is **not evidence of optional runtime values**.
- 1.x GET operation declares optional `includeData` without a default in its referenced parameter YAML. 2.x GET declares `includeData` default `'false'`; `ignoreDataSizeLimit` default `'false'`; and `redactExecutionData` with redacted `true`, potentially revealing `false` (requires `execution:reveal` scope), while omission follows the workflow policy. **These switches do not prove any record is safe to ingest.** No SOVIA code invokes them.

### Two designs compared

| Approach | Value | Cost/risk | Decision |
|---|---|---|---|
| Live n8n HTTP adapter and payload mapper | Direct customer data integration | Real execution objects may carry prompts, binary data, credentials/PII; needs approved owner, verified version, scoped API, real sanitizer, privacy and retention tests | **NOT BUILT** |
| Version-pinned **synthetic property-name-only** delta and rejection tests | Source-backed visibility into API drift and types, deterministic offline tests | Does not validate any actual response/value, still leaves live compatibility unresolved | **BUILT** |

`sovia_n8n_execution_reference.py` compares only explicitly fabricated `field_keys` in a strict five-field envelope. It refuses unknown names, unpinned versions, malformed/oversized manifests, and names `data`, `customData`, `workflowData` even though these are part of public schemas (guard against later accidental payload acceptance). Exact permitted names also **ALWAYS block import**. If an operator instead supplies an actual execution response, it is rejected as an invalid envelope, not parsed for values.

Example (synthetic **names**, not an API response):

```json
{
  "schema_version": "sovia.n8n_pinned_execution_keys.v1",
  "synthetic_only": true,
  "source_kind": "public_api_get_execution_response_keyset_only",
  "pinned_release_tag": "n8n@2.44.7",
  "field_keys": ["id", "status", "mode", "startedAt", "workflowId"]
}
```

Reproduce without Internet, credentials or customer files:

```powershell
py -3 -I -B sovia_n8n_execution_reference.py --show-public-delta
py -3 -I -B sovia_n8n_execution_reference.py --input examples/n8n_pinned_execution_1x_keys.json --synthetic-only
py -3 -I -B sovia_n8n_execution_reference.py --input examples/n8n_pinned_execution_2x_keys.json --synthetic-only
py -3 -m unittest discover -s tests -p test_n8n_execution_reference.py -v
```

Only the public static-delta command exits `0`. A shape recognition exits `3` (`PUBLIC_EXECUTION_KEYSET_ONLY_IMPORT_BLOCKED`); rejected/invalid manifests exit `2` with fixed codes. All reports explicitly state `request_performed:false`, `conversion_performed:false`, `raw_n8n_import_supported:false`, `n8n_instance_version_verified:false`, `customer_authorization_verified:false`, `pii_redaction_verified:false`. This is a **source-only research helper**, not part of the older 12-file Audit Lite v0.10 ZIP.

## Next gated engineering step

For an authorized live integration: approve an exact installed n8n release, user/data-controller scope and ingestion design; independently verify actual query/response schemas; ensure access/read-only scopes and upstream redaction; design minimization rules for `data`/`workflowData`/`customData` and metadata, with consent and retention; validate sanitized outputs through the existing SOVIA gate; run owner physical Windows/AV/Korean PDF acceptance. No real API, data/permission changes, release, listing or deployment was performed here.
