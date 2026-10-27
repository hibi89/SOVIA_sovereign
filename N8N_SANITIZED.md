# SOVIA synthetic n8n-like sanitized metadata adapter (P2)

**Status:** Experimental offline converter on a development branch. **NOT** a live n8n API connection, parser of real n8n execution exports, proof of customer consent, or commercial-supported integration.

## Chosen architecture

| Choice | Performance / costs | Maintainability | Safety | Decision |
|---|---|---|---|---|
| Import full n8n execution export, including node data, parameters, item JSON and arbitrary payloads | Potentially less manual redaction but much larger/unbounded attack and data surface; version-sensitive | High recurring burden | High risk of prompt, credential, PII or document exposure | Not implemented |
| Define a small **pre-sanitized, versioned metadata-only envelope** and convert to SOVIA canonical v1 | O(number of steps), <=1000 bounded events and <=1 MiB input, zero paid API calls | Strict schema and reusable offline audit core | Rejects unrecognized keys; still requires authorized sanitization upstream | **Implemented** |

### Execution and data separation

User/authorized data owner manually prepares a local sanitized metadata file → `sovia_n8n_sanitized.py` strict schema reader → canonical SOVIA JSON → existing `sovia_audit.py` unchanged → optional existing reports and SQLite. The converter does **not** fetch n8n executions, authenticate to an n8n instance, call external APIs, redact original payloads, execute nodes, or retain its own history. The separately supplied audit policy is treated as a **claim by the operator**, not independent authorization proof.

The input file must contain exactly `format`, `workflow_id`, `execution_id` and `steps`. Format equals `sovia.n8n_sanitized.v1`. Each step must contain `step_id`, `occurred_at_utc` (with timezone), `tool_code`; optional keys are `target_code`, `destination_domain`, `permission_asserted` (true/false/null), `outcome_code` (success/error/unknown), `evidence_ref`. IDs/codes/evidence refs allow only 1–80 ASCII letters, digits, underscores, dots, colons or hyphens. `destination_domain` is a hostname, **not** a URL. Policy is separate SOVIA v1 JSON: `schema_version` plus `policy` with supported four keys only.

**Reject all other fields**, notably raw `data`, `resultData`, `json`, `binary`, `parameters`, `credentials`, prompts, webhook payloads, and arbitrary n8n execution objects. It is intentional that real n8n exports will be rejected. Empty or unknown permission is **not** inferred as true; absent evidence remains absent. A source evidence pointer is unverified even when supplied. Names that happen to match the code pattern might still be sensitive: upstream human/governance validation remains necessary.

## Synthetic usage

Start in the source branch or an integrated development checkout, with Python 3.11+ (standard library only). Use an **unused** output filename and a private directory for any non-synthetic output.

```sh
python sovia_n8n_sanitized.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --output demo-n8n-canonical.json
python sovia_audit.py --input demo-n8n-canonical.json --output demo-n8n-report.html
python -m unittest discover -s tests -p test_n8n_sanitized.py -v
```

The synthetic 3-step example is designed to trigger the existing five deterministic finding types. Converter outputs a canonical **NEW** JSON file via the existing no-clobber atomic publishing method; input/policy are read-only. No source files are overwritten. It reports only aggregate conversion count and a warning that evidence is not independently verified; error messages do not echo supplied source paths or content.

### Scope/limitations and commercial gate

- Raw execution export compatibility with any specific n8n version is **NOT VERIFIED**. Official n8n docs: <https://docs.n8n.io/workflows/executions/all-executions/>. Actual allowed source fields, workflow identity, timestamps and policy must be mapped and sanitized **outside** this converter before real use.
- Enforcing a strict format is a partial **reject-by-default** control, not effective automatic PII scrubbing. `workflow_id`, `target_code` or domain strings can still be linkable/personal even when syntactically valid.
- The output canonical JSON and subsequent audit HTML/JSON/CSV/PDF may contain metadata; existing `RETENTION.md` inventory does **not** delete or set a legal retention period. No customer original input without informed authorization, retention boundaries and human review.
- This module and example are **not** included in the v0.10 12-file portable ZIP. Owner Windows/Defender/PDF manual acceptance, approved real customer fixtures, n8n schema version compatibility, upstream sanitization QA, false-positive review, data removal policies and commercial licensing/support remain pending.
- Changes in n8n execution format require a separately reviewed adapter version and synthetic/authorized non-sensitive contract tests; never silently guess nested fields or grant permission.

## Acceptance

The new converter's isolated tests must pass on GitHub Actions Windows/Ubuntu × Python 3.11/3.13; existing audit/CSV/SQLite/dashboard/portable smoke must continue to pass. A CI pass tests **synthetic contract and regression compatibility only**, not actual n8n customer integration. Integrate into `develop` after a green reviewed PR; leave `main` untouched.
