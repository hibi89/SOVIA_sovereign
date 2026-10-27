# Direct pre-sanitized n8n-like metadata audit (P2, source-only)

This utility removes an intermediate canonical JSON file and the need for two commands. **It is not a native n8n API connector or a raw n8n execution parser.** It consumes only the `sovia.n8n_sanitized.v1` strict metadata envelope and a separate SOVIA v1 policy. It delegates to the original five-rule evaluator, existing PII-pattern preflight (approved-local only), attestation checker, Korean HTML renderer, and no-clobber report writer.

## Fabricated-data one-command demo

```sh
python -I -B sovia_n8n_direct_audit.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --html-output NEW_SAMPLE.html --json-output NEW_SAMPLE.json --synthetic-only
```

Expected synthetic result is **3 events and 5 findings**. Generates only the two explicitly chosen output files, not an intermediate canonical JSON or SQLite database. Existing converter and default audit CLI remain unchanged. Inputs and outputs should be kept outside this public GitHub repository. Both HTML and JSON include event metadata.

## Operator-claim path (NOT verified consent)

```sh
python -I -B sovia_n8n_direct_audit.py --mode approved-local --input LOCAL_PRE_SANITIZED.json --policy LOCAL_POLICY.json --attestation LOCAL_REVIEW.json --html-output NEW_REPORT.html --json-output NEW_REPORT.json
```

An operator must first independently determine lawful basis, upstream redaction and permissions. The existing unsigned attestation gate checks exact document hashes, scope, asserted flags and expiry. The existing PII heuristic runs before publication. Neither proves source authenticity, legal authorization, completeness of sanitization, or real n8n API compatibility. A forged operator claim remains possible. Never supply real customer data without the owner's separately approved handling conditions.

## Boundaries

- Raw n8n exports, item JSON, workflow credentials, arbitrary nested results, unexpected fields and oversized inputs fail closed under the existing converter/schema. The `--synthetic-only` flag asserts user intent but does not authenticate synthetic provenance.
- Source/policy/attestation symlinks, output aliases, occupied output paths and missing output directories are refused. Reports are written with the existing staged, fsynced, exclusive-hardlink writer and best-effort rollback. Multi-file publication is **not** a transaction for concurrent readers or power loss.
- No network requests, hosted LLM, database writes, report intermediates or extra input copies. Local memory, OS logging and shell redirection cannot be ruled out.
- There is no automatic size budget in this path; use the separate `sovia_guarded_export.py` for explicitly chosen local size-budget tests on canonical JSON. Commercial quotas, latency, privacy assurance, actual n8n source mapping and release are NOT approved.
- Source-only utility is deliberately excluded from the existing unsigned 12-file v0.10 beta ZIP. Original default CLI, historical source files, GitHub main branch, customer settings and deployment are unchanged.

## Tests

```sh
python -m unittest discover -s tests -v
python portable_smoke.py
```

Windows and Ubuntu, Python 3.11/3.13 CI are synthetic-only. Physical owner Windows/browser/Defender/Korean PDF review, genuine authorized installed n8n source/version validation and signed customer delivery remain outstanding.
