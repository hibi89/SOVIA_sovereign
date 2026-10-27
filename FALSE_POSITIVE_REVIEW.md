## Executable synthetic triage (development addendum — 2026-10-27)

See [PRIVACY_TRIAGE.md](PRIVACY_TRIAGE.md) and `sovia_privacy_triage.py` for an aggregate TP/TN/FP/FN comparison over **fabricated labeled cases only**. The deliberate review-queue example returns exit code 3 when an internal-IP-looking code is blocked but human-labeled benign and when a sensitive-looking descriptive code is missed. It **does not change any rejection rules or grant overrides**. For the owner's Windows beta evidence gates see [OWNER_WINDOWS_ACCEPTANCE.md](OWNER_WINDOWS_ACCEPTANCE.md); all manual statuses are initially NOT_CHECKED.

---

# SOVIA P2 — false-positive triage procedure (not an allowlist bypass)

**This is a review process specification and synthetic test protocol, not an independent security or privacy clearance.**

When `approved-local` PII preflight or the synthetic safe-code registry returns `PREFLIGHT_REJECTED`, `REGISTRY_PRIVACY_PREFLIGHT_REJECTED`, `UNREGISTERED_METADATA_CODE`, or a mapping collision, **do not disable the scanner or bypass it by switching real input to `synthetic` mode**. Refusals are safe defaults. Never copy real data to the PUBLIC GitHub repository or developer issue tracker.

## Resolution states

1. **BLOCKED**: Current source unchanged and not processed. No result report is published.
2. **UNDER_REVIEW**: Data owner checks the original locally, away from public repos and external LLMs, for provenance, genuine authorization, sensitivity, scope and existing retention plan. The reviewer's identity and decision may be recorded in a customer-controlled private system; SOVIA currently does **not** verify that identity or record such decisions.
3. **REPLACE_WITH_SAFE_CODE**: If the source is actually non-sensitive and the refusal is a false positive, replace the source field *upstream* with an explicit, reviewed lower-case nonpersonal code such as `scope.public`; add it to the safe-code registry and make any corresponding policy mapping consistent. For legitimate sensitive values, exclude them instead, or keep the workflow blocked. Do not paste personal values into mapping keys.
4. **RETEST**: Recompute input/policy digests, renew the operator's review manifest (when used), rerun the complete preflight and audit, and compare risk findings. If any new mapping makes an unauthorized tool authorized, blocks should remain.
5. **ACCEPTANCE**: Only permitted after no refusal, risk-finding equivalence, human-reviewed coverage notes, local backup/retention policy and actual customer approvals; a technical green test is **not** legal compliance approval.

## Practical review scenarios

| Synthetic case | Expected behavior | Review approach |
|---|---|---|
| `target_code` accidentally contains private IPv4 `10.0.0.5` | Heuristic refusal, no output | Review whether an internal address is truly needed; use approved `scope.internal` code if legitimately non-sensitive |
| Code contains an email/phone/ID-like string | Refuse | Remove identifier upstream; never put it into aliases or comments |
| Two source tool codes map to `tool.lookup` | Refuse as ambiguous | Keep separate standard codes so tool authorization is not merged |
| Tool missing from registry | Refuse | Add explicit mapping only after identifying tool meaning; no guess or permissive default |
| Missing `allowed_tools` policy | Preserve **unknown**, not safe | Obtain operator-owned policy independently; never invent permission |

When creating a synthetic regression for a suspected false positive, replace private inputs with fabricated test tokens demonstrating only the same **pattern**, not any original value. Validate both false-positive rate and false-negative surface through controlled synthetic fixtures, documenting blocked/accepted decisions in private governance as appropriate. No automated suppression file or wildcard exception is permitted by the current implementation.

## Precommercial blockers

SOVIA has not established real customer authorization, authenticated reviewers, full Korean PIPA/GDPR scope, real n8n version mapping, automatic PII removal, legal retention/disposal, independent customer's Windows validation or full coverage metrics. Owner approval is required before accessing any client logs, changing privacy/access settings, releasing/selling software, or destructive actions.
