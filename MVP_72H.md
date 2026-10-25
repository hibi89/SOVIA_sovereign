# SOVIA Audit Lite — 72-hour MVP execution contract
Approved delivery strategy from owner conversation, recorded 2026-10-26 KST. Targets are date/time-box goals, NOT completion claims or background execution.

## Core decision
Deliver a **working vertical slice before completeness**. Use final requirements/architecture as a gap checklist, fill features iteratively, start product-listing materials in parallel. Maintain security *minimums now*, postpone heavier penetration/soak/failover/enterprise assurance until **before real-customer deployment/sale**, not afterward.

## Day 1 — 2026-10-26 / make it run end to end
Aim: one synthetic JSON fixture -> safe parse/normalize -> deterministic 1+ finding -> local CLI -> simple HTML/terminal report.
- Canonical event and finding structures and fixture (valid / invalid / no-risk).
- Basic input guardrails: allowlist JSON shape, file size cap, no imported command execution, no network calls.
- One full-flow smoke test and a small number of focused unit tests.
- Commit tested slice to feature/p0-audit-core and record actual evidence.
Exit: repeatable command and output with explicit limits. A scaffold alone is NOT day-one success.

## Day 2 — 2026-10-27 / increase useful audit value
Aim: extend 3 mandatory risk types, ideally all 5 planned if practical: unknown/unauthorized tool, new external destination, sensitive target without asserted permission; stretch: burst and missing evidence.
- Event-based evidence references, rule IDs/versions, deterministic severity and policy coverage/unknown status.
- Add safe CSV importer and SQLite only if needed after working JSON path; never let infrastructure work stall the primary flow.
- Narrative and Korean HTML report with concrete "why it matters / what to change" sections.
- Add negative fixtures and regression checks.
Exit: healthy vs risky sample produces different, explainable results with evidence and known gaps.

## Day 3 — 2026-10-28 / polish and acceptance test
Aim: integrated local Audit Lite demo on a clean environment, one-command sample execution, reproducible report, simple read-only local UI when time permits.
- PDF generation or print-ready HTML (PDF should be finished in P2 if incomplete); JSON export.
- CLI help/install instructions and sample demo; evaluate original final blueprint against shipped behavior.
- Verify no credentials/raw prompts in repo, no external outbound request, no untrusted input execution, HTML escaping.
- Review test pass/fail counts, actual report files, UI if implemented; document untested items as UNVERIFIED.
Mandatory 72h exit: working offline input -> normalization -> >=3 correct transparent risk checks -> event evidence -> usable HTML report -> documented CLI and executable smoke/unit tests. Any missing feature must enter GAP_MATRIX.md, not silently be counted as complete.
Stretch: 5 rules, CSV import, PDF, SQLite persistence, local UI. Do not delay the first working outcome for them.

## Explicit security/testing split
**Always now (Day 1+):** input size/type validation, no execution of imported text, secrets and personal data excluded, redaction, HTML escaping, offline processing, test smoke, no exaggerated security claims.
**After MVP, before pilot/sale:** malformed/adversarial import suite, policy false-positive testing, output sanitization and spreadsheet injection check, packaging, real authorized sanitized fixture, rollback/delete/backup, dependency checks, customer contract/data-flow review.
**Cloud/Private pre-production:** tenant RBAC/isolation/negative tests, authentication, backup restore, alert replay, offline/no-egress verification, reliability and penetration testing as appropriately scoped.
No real customer data is allowed to bypass its security gate.

## Daily output format
For each Day: done vs planned, exact source SHA, test commands and pass/fail count, sample output/link, features vs blueprint gaps, remaining work, no made-up percent/time remaining. Target is three days of active supervised development, not work executed between chat turns.

## Stop / pivot
If PDF or UI threatens working flow, ship HTML/CLI and log gap. If one adapter integration fails twice without progress, pivot to documented JSON import. If time expires, report working verified scope and carry incomplete work to P2 without claiming 100% MVP.

## Branch and approvals
feature/p0-audit-core for MVP; develop integration; main stable after verified review. Owner approves payments, privacy changes, external data transfer or live listing/public deployment. Repo PUBLIC at last check; synthetic fixtures and public-safe designs only.
