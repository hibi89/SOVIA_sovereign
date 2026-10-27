# P2 synthetic privacy false-positive / false-negative triage

**Development-only, local/offline, zero-cost.** This implements repeatable, manually labeled synthetic test cases around the unchanged \`sovia_pii_preflight.py\` matcher. It never scans actual customer logs, redacts raw n8n exports, grants authorization, suppresses a warning, or measures performance on a representative population.

## Design decision

| Option | Risk and upkeep | Decision |
|---|---|---|
| Automatically suppress matching patterns when a person calls them a false positive | Bypasses a safety boundary, potentially accepts genuine secrets; requires persistent override lists | Do not implement |
| Compare fabricated, explicitly labeled patterns against existing matcher and output **aggregate** TP/TN/FP/FN counts | Deterministic, bounded, no match/paths/identifiers printed and no change to protections | Implemented |

The input must be an exact JSON envelope containing \`schema_version: "sovia.privacy_triage.v1"\`, \`synthetic_only: true\`, and 1–100 \`cases\`. Each case is exactly \`{"case_id":"lowercase-code","specimen":"fabricated-string","expected_reject":true/false}\`. The upper bound for specimen length is 256 characters and IDs cannot contain customer names or emails. Real source use is prohibited, though a boolean assertion cannot technically prove a sample is fabricated. The input file itself remains unmodified, and no output file is generated.

The score is computed against the unchanged PII matcher. **TP** = synthetically labeled reject, matcher rejects; **TN** = labeled allow, matcher allows; **FP** = labeled allow, matcher rejects; **FN** = labeled reject, matcher allows. A matcher internal error is **never** treated as a valid detection. Exit status: **0** when no label disagreements, **3** when FP or FN exists and human review is required, **2** for malformed data/unsupported use. Output consists solely of aggregate counts and explicit \`privacy_absence_proven:false\`, \`representative_population_validated:false\`, \`suppression_applied:false\`. Neither safe status nor rates constitute measured privacy performance.

## Commands (synthetic only)

~~~powershell
py -3 -I -B sovia_privacy_triage.py --input examples/synthetic_privacy_baseline.json --synthetic-only
py -3 -I -B sovia_privacy_triage.py --input examples/synthetic_privacy_review_queue.json --synthetic-only
py -3 -m unittest discover -s tests -p test_privacy_triage.py -v
~~~

The baseline is intentionally all correct: 9 synthetic cases, **6 TP, 3 TN, 0 FP, 0 FN**, exit 0. The **separate intentional disagreement** case set contains one benign-looking internal IP address rejected by the conservative scanner (FP), one descriptive surrogate label marked as sensitive by a human but undetected by a regex (FN), and a safe code (TN); it **must return exit 3** and is not a release blocker for the *separate baseline suite*. It illustrates blind spots, not observed incidents or population metrics.

## Reviewer workflow

When a discrepancy is detected, keep the real source **blocked**; do not put original values in public issues, CI tests or LLM prompts. Create a fabricated pattern-equivalent test case, assign a proposed expectation with a human reviewer, and record the human decision in a private owner-controlled review ledger if real data is ever authorized. For benign metadata that resembles an IP or credential, **recode upstream to a reviewed nonpersonal alias** such as \`scope.internal\`, then rerun the unchanged scanner, mapping invariants and policy audit. For a missed sensitive field, reject it upstream and add synthetic negative tests; do not change unknown permissions to true. The mapper's finding-equivalence and the audit core remain unchanged.

False-positive adjudication here is **a test and document process, not an executable allowlist/exemption**. See [FALSE_POSITIVE_REVIEW.md](FALSE_POSITIVE_REVIEW.md) and [OWNER_WINDOWS_ACCEPTANCE.md](OWNER_WINDOWS_ACCEPTANCE.md). Real n8n version mapping, true consent evidence, operator authentication, PII reliability, lawful retention/deletion and manual Windows signoff remain open P2 gates.
