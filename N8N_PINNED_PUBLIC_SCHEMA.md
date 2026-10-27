# SOVIA P2 — n8n official tagged Public API workflow schema key contracts

**Source-verifiable public-schema key research, not native n8n import or real data processing.** This stage reads only static field-name reference data extracted from **two official n8n Git release tags**. It does not inspect customer exports, n8n node bodies, API execution payloads, credentials, real workflows or private repositories.

## Verified primary references (frozen 2026-10-27)

Official repository: `n8n-io/n8n`. Fixed file path in **both** tags:

`packages/cli/src/public-api/v1/handlers/workflows/spec/schemas/workflow.yml`

| Source tag | Official commit SHA | Official GitHub file blob SHA | Workflow properties | Required |
|---|---|---|---:|---|
| `n8n@1.123.88` | `6b88ad7f6be54df9f26efe17e0c249e345b40375` | `7f36ea82d077db612b6cea4807ccaa7ee1e1227e` | 12 | 4 |
| `n8n@2.44.7` | `cbe3950c51759577f9e611d28f8f5cd01828eaef` | `0eb571b216406d9d2d4b6e072195a1296124e6fc` | 21 | 4 |

Read original tagged schemas: [n8n 1.123.88 workflow.yml](https://github.com/n8n-io/n8n/blob/n8n%401.123.88/packages/cli/src/public-api/v1/handlers/workflows/spec/schemas/workflow.yml) and [n8n 2.44.7 workflow.yml](https://github.com/n8n-io/n8n/blob/n8n%402.44.7/packages/cli/src/public-api/v1/handlers/workflows/spec/schemas/workflow.yml). Commit SHAs and file blobs were independently fetched via GitHub at development time; runtime never reaches GitHub. We analyzed the **top-level Public API workflow schema only**. This is **not** equivalent to a JSON export's runtime contract, the public **execution** API response, or the schema of node parameters.

The unchanged four required top-level properties in both source files are `name`, `nodes`, `connections`, `settings`. The observed nine properties in 2.44.7 but absent in 1.123.88 are:

`activeVersionId`, `description`, `isArchived`, `meta`, `nodeGroups`, `parentFolderId`, `pinData`, `triggerCount`, `versionId`.

No 1.123.88 top-level property was absent in 2.44.7 **within these two source files**. Differences are field-name observations, **not proof of stable semantics, optionality at endpoints, API behavior or compatibility**. Especially `pinData` and `staticData` can represent data-bearing fields; this tool refuses even their **names** in submitted manifests to prevent accidental future relaxation.

## Design decision

| Option | Benefit | Risk and scope | Decision |
|---|---|---|---|
| Parse/export actual versioned n8n workflow or executions | Directly useful for integration | Raw payloads, node credentials/parameters, schema drift, customer authorization/privacy and storage risks | Not implemented |
| Freeze a **known official Public API source-schema property reference** and compare **fabricated field names only** | Cheap, deterministic source provenance and negative regression tests | No evidence that actual n8n instances or user data fit these schemas | Implemented |

`sovia_n8n_pinned_reference.py` exposes `--show-public-delta` and a strictly **synthetic-only key-name manifest** comparison.

Example (fabricated data, not an export):

```json
{
  "schema_version": "sovia.n8n_pinned_workflow_keys.v1",
  "synthetic_only": true,
  "source_kind": "public_api_workflow_keyset_only",
  "pinned_release_tag": "n8n@2.44.7",
  "field_keys": ["name", "nodes", "connections", "settings", "id", "description", "versionId", "activeVersionId"]
}
```

Compare keys **offline**:

```powershell
py -3 -I -B sovia_n8n_pinned_reference.py --show-public-delta
py -3 -I -B sovia_n8n_pinned_reference.py --input examples/n8n_pinned_public_1x_keys.json --synthetic-only
py -3 -I -B sovia_n8n_pinned_reference.py --input examples/n8n_pinned_public_2x_keys.json --synthetic-only
py -3 -m unittest discover -s tests -p test_n8n_pinned_reference.py -v
```

The `--show-public-delta` command has exit 0 because it only prints official **public property-name differences**. A synthetic manifest match **always exits 3** and reports `PINNED_PUBLIC_API_KEYSET_RECOGNIZED_IMPORT_BLOCKED`; missing required keys also exit 3. Invalid input, unsupported release tags, unknown fields, suspicious optional data-field names and malformed JSON exit 2 with generic codes. **There is no success exit allowing actual import.**

Output always contains `raw_workflow_or_execution_import_supported:false`, `n8n_runtime_version_verified:false`, `native_api_integration_verified:false`, `source_authorization_verified:false`, `customer_payload_inspected:false`, `conversion_performed:false`. Merely knowing the official source file's commit SHA does not independently authenticate a user's running n8n instance.

## Commercial gaps / future adapter conditions

To build a real n8n adapter later, separately approve the target source and access, validate pinned Public API operations and version-specific **execution** response schema, safely map only explicitly authorized and sanitized fields, block item content and secret material, test known version drift and independent output evidence, and obtain owner-device/manual acceptance. Nothing here relaxes prior synthetic-only `sovia_n8n_compatibility.py`, `sovia_n8n_sanitized.py`, PII pattern preflight or operator claims gate. Prior 12-file v0.10 portable ZIP, default `main`, production and customer data are all untouched.
