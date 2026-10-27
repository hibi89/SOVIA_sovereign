# SOVIA P2 — synthetic-only pinned n8n execution summary bridge

**This is NOT raw n8n execution importing, actual API compatibility, verified PII redaction or customer data processing.** Input consists of fabricated summaries and already-sanitized per-tool steps; the operator's `synthetic_only` declaration is not independently authenticated.

## Design tradeoff (2026-10-27 KST)

| Design | Benefit | Risk | Decision |
|---|---|---|---|
| Turn n8n `getExecution` summary (`status`, `startedAt`) into invented SOVIA tool event | Simple converter | Fabricates actions/outcomes and incorrect authorization findings when node-level evidence absent | **Rejected** |
| Require independently fabricated `sanitized_steps` plus version-tagged summary; feed steps to existing `sovia_n8n_sanitized.convert` | Preserves all 5 real audit rules and explicit missing-evidence semantics; no raw values | No evidence of real n8n interoperability or real safe sanitation | **Implemented — synthetic-only** |

## Format and version-specific strict types

`sovia_n8n_execution_bridge.py` accepts exactly six top-level fields:

```json
{
  "format": "sovia.n8n_execution_bridge.synthetic.v1",
  "synthetic_only": true,
  "source_kind": "synthetic_public_execution_summary_plus_sanitized_steps",
  "pinned_release_tag": "n8n@2.44.7",
  "execution_summary": {
    "id": "101",
    "workflowId": "201",
    "status": "error",
    "startedAt": "2026-10-25T15:01:00Z"
  },
  "sanitized_steps": [
    {
      "step_id": "node-1",
      "occurred_at_utc": "2026-10-25T15:01:01Z",
      "tool_code": "approved_lookup",
      "outcome_code": "success",
      "evidence_ref": "synthetic:1"
    }
  ]
}
```

The version-tag reference is limited to published `n8n@1.123.88` and `n8n@2.44.7` source specifications as documented in [N8N_EXECUTION_PUBLIC_SCHEMA.md](N8N_EXECUTION_PUBLIC_SCHEMA.md). For fabricated fixtures **only**, 1.x IDs must be positive Python integer values, while 2.x IDs must be canonical, positive, digit-only strings. Both bounded to twelve decimal digits. This deliberately restrictive subset is not a claim about actual IDs from real installations.

`execution_summary` accepts only `id`, `workflowId`, `status`, `startedAt`. These are **validated as metadata, never converted into tool executions**. `status` does not overwrite any step outcome; `startedAt` does not generate or replace any per-step timestamp. The explicit `sanitized_steps` (1–1000 only) use the existing strict SOVIA sanitized adapter field allowlist and its canonical evaluator. The adapter's source-pointer/permission/target/destination unknown values are preserved, not inferred. Its existing five risk rules and redacted failure behavior remain unchanged.

Unknown envelope keys, raw `data`, `workflowData`, `customData`, `credentials`, `items`, `parameters`, `binary`, `prompt`, extra summary fields, unknown tags, wrong ID types, unsupported status/UTC, non-synthetic claim, duplicate or malformed events, and unsigned/unsupported policy fields fail closed before any output. **This is not a comprehensive personal-data filter.** Operator may falsely label actual data synthetic; users must never pass real execution data to this tool.

## Offline usage

```powershell
py -3 -I -B sovia_n8n_execution_bridge.py --input examples/synthetic_n8n_bridge_1x.json --policy examples/demo_policy.json --output example_canonical_1x.json --synthetic-only
py -3 -I -B sovia_n8n_execution_bridge.py --input examples/synthetic_n8n_bridge_2x.json --policy examples/demo_policy.json --output example_canonical_2x.json --synthetic-only
py -3 -I -B sovia_audit.py --input example_canonical_2x.json --output example_audit_2x.html --json-output example_audit_2x.json
py -3 -m unittest discover -s tests -p test_n8n_execution_bridge.py -v
```

Output paths must not exist and must not alias inputs. Existing canonical core/SQLite/HTML/PDF, `main` and v0.10 portable ZIP are unchanged. CLI success means **a fabricated step contract was converted**, not verified customer source authority, node execution accuracy, n8n API connectivity, independent privacy clearance or production readiness. There is no n8n network/API request, source customer data, deletion, telemetry or credentials.

## Commercial gate remains OPEN

Before real integration or release, obtain explicit owner approval, data-controller agreement and live source scope, independently validate a pinned actual n8n version, design read-only allowlisted upstream sanitizer and source provenance with no secret/item bodies, test privacy false negatives, determine retention/backups, and complete the owner's physical Windows/browser/Defender/optional Korean PDF acceptance. Neither `synthetic_only` nor the version tag authenticates any of these facts.
