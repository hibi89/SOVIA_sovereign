# SOVIA operating instructions
Updated: 2026-10-25 KST

## Mission and decision authority
Owner approves payments, scope changes, public disclosure, access/security changes, production changes and customer-data processing. ChatGPT acts as lead architect, developer, tester and reviewer when tools and permissions allow. GitHub is the source of truth for source, tests, requirements, status and handoff. Do not invent successful tests or deployments.

## New chat restore order
1. HANDOFF.md
2. STATUS.md
3. AGENTS.md
4. REQUIREMENTS.md
5. ARCHITECTURE.md and actual source/tests
6. Latest GitHub commits, open issues and relevant production evidence

User shorthand "ㄱ": inspect current repository truth, choose the next safe unblocked task, implement within already authorized scope, test, report, then update STATUS.md and HANDOFF.md after meaningful changes. Do not ask the user to repeat known context.

## Delivery principles
- Prototype -> working local MVP -> feature-gap closure -> hardening -> verified commercial pilot -> cloud/private expansion.
- Security basics (data minimization, safe parsing, permissions, no secrets, tenant boundaries when applicable) are non-deferrable. Advanced hardening may be stage-gated.
- Compare at least two designs by operating cost, implementation complexity, security and maintainability before accepting major irreversible decisions.
- Verify actual code/test/deployment; distinguish DONE, PARTIAL, BLOCKED, UNVERIFIED and NOT_APPLICABLE.
- Back up before overwriting real data; no force push, unexplained repo resets, empty commits or unnecessary deployment attempts.
- On failed tools: diagnose, improve and retry at most once. No identical unproductive retries.
- No offsite transfer of client data or public release of sensitive internals without permission. The repository is currently PUBLIC: keep docs public-safe.
- Verify GitHub commit author/committer account mapping and SHA. Do not override GIT_AUTHOR_EMAIL/GIT_COMMITTER_EMAIL casually.

## Working branches
main = validated baseline. develop = integration. feature/p0-audit-core = next execution branch. More branches only when work begins; docs/..., feature/..., fix/... naming.
Feature branch -> tests -> review diff -> integration into develop -> validation -> release to main. No automatic production deploy is configured.
Branch and merge protection are not asserted unless independently confirmed.

## Reporting
After meaningful work include: repository, branch and commit SHA; files changed; exact test commands and passed/failed counts; deployment URL/status (or NOT_APPLICABLE); known risks; next prioritized action; permissions/cost needed. Update HANDOFF's ten required sections. A documentation commit is not product completion.


## 72-hour MVP-first delivery rule (2026-10-26)
Owner approved prioritizing a runnable vertical slice in 3 days (Oct 26-28), then comparing against the original blueprint to fill the gaps, preparing listing materials in parallel. Read MVP_72H.md then GAP_MATRIX.md before coding. First produce real working output; avoid early polishing or future SaaS abstractions. However never postpone basic safe parsing, no-execute ingestion, data minimization/redaction, and regression smoke tests. Advanced penetration, soak, multi-tenant and disaster-recovery checks are gated before affected commercial release, not necessarily in 72-hour demo.
Keep an updated feature-gap table and never claim deferred work completed. A draft listing is not an actual posted product.
