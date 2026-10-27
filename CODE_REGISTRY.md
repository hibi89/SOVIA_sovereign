# SOVIA P2 — explicit safe-code registry (synthetic-only)

**Status:** Development tool for already sanitized *synthetic* metadata. Not native n8n API integration, raw-log sanitization, anonymization, customer consent, or a commercial feature.

## Architecture decision

| Option | Speed and zero-cost operation | Reliability and maintenance | Decision |
|---|---|---|---|
| Auto-detect names, infer risk categories and replace possible PII | Fast for unknown formats but requires unsafe access to raw logs | May hide private content, collapse distinct tools and change audit findings | **Rejected** |
| Explicit lower-case code registry with bijective/injective mappings and policy-aware conversion | Local stdlib, bounded input, no tokens/paid APIs; operator lists allowed aliases | Unregistered values fail closed; deterministic; versioned and testable | **Implemented** |

The registry contains **only presanitized code aliases and their approved standard codes**, never raw user/customer names, phone numbers, IDs, prompts or documents. There is no automatic mapping from a customer name to a surrogate label and no unsupervised identification.

`sovia_code_registry.py` checks a strict v1 JSON registry:
```json
{
  "schema_version": "1.0",
  "kind": "sovia.safe_code_registry.v1",
  "tool_codes": {"approved_lookup": "tool.lookup", "unauthorized_export": "tool.export"},
  "target_codes": {"public_docs": "scope.public", "client_records": "scope.sensitive"}
}
```

Both keys and values must match `[a-z][a-z0-9_.:-]{0,79}`; aliases with uppercase/spaces, personal-data patterns, missing entries, or ambiguous **two-to-one mappings** are rejected. Tool and target maps are separate. The same maps are applied to `policy.allowed_tools` and `policy.sensitive_targets`, respectively, **before re-evaluating** the canonical audit. No mapping changes permissions, evidence pointers, timestamps, destinations, event IDs or policy thresholds. Unknown policy fields remain rejected by the existing adapter; absent policy remains unknown.

**Critical invariant:** The old five risk rules must produce the *same rule IDs, event IDs, severities and coverage warnings* before/after mapping. If not, conversion fails with `AUDIT_FINDING_DRIFT`; it never silently converts an unauthorized tool into an allowed one. Both original input/policy/registry and resulting canonical JSON are passed through the existing offline PII-pattern preflight; note this is heuristic and cannot prove safe anonymity. Any suspected string triggers a generic error without printing the match.

## Synthetic local usage

```sh
python sovia_code_registry.py --input examples/demo_n8n_sanitized.json --policy examples/demo_policy.json --registry examples/demo_code_registry.json --output new-audit-canonical.json --synthetic-only
python sovia_audit.py --input new-audit-canonical.json --output new-report.html
python -m unittest discover -s tests -p test_code_registry.py -v
```

The optional `--synthetic-only` flag is required for this CLI; it is **not** customer-data authorization. Output must be a new filename in a pre-existing directory; the existing audit no-overwrite writer publishes the file. The old n8n-like adapter `synthetic` and `approved-local` modes are **unchanged**, including SHA-bound operator assertions. This mapper is a separate synthetic helper and **is not wired into the customer-review attestation pipeline**; a new transformed document would need a newly reviewed assertion before any future authorized use.

The mapped code is **not guaranteed anonymous or unlinkable**. An attacker with the mapping registry can reverse a listed label, and the remaining event/timestamp/domain metadata can also link records. All real customers, consent evidence, actual n8n formats, effective PII handling and retention policies remain unverified. Old portable v0.10 ZIP is deliberately unchanged; `main` and Production are untouched.

## Regression and false positives

31 focused synthetic tests exercise 3 events/5 findings, complete and injective mapping, known policy values, absent-policy uncertainty, missing reference protection, PII/secret refusal, duplicate targets, raw export rejection, new-file-only publication, isolated Windows/Python CLI and offline operation. An apparent false positive from the preflight must be handled under [FALSE_POSITIVE_REVIEW.md](FALSE_POSITIVE_REVIEW.md): no automatic suppression/exception in the matcher, no raw customer data in PUBLIC GitHub. All merges require Windows+Ubuntu Python 3.11/3.13 full CI and legacy ZIP smoke.
