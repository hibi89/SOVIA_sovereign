# Branch strategy and release discipline
Updated 2026-10-25 KST

## Permanent branches
main: reviewed baseline/documentation. Future public release/production source only when formally approved.
develop: active integration after feature tests; use PR or review before main.

## Active work branch
feature/p0-audit-core: first actual code implementation after user approves scoped plan. Initially same baseline as develop/main. Never call mere branch creation code completion.

## On-demand branches (create only at start of task)
feature/p1-audit-lite, feature/p2-connectors, feature/p3-cloud, feature/p4-private, fix/<issue>, docs/<scope>.
Avoid creating a forest of stale empty branches; delete only after merge and explicit maintenance decision.

## Change protocol
Read current HEAD and relevant docs; back up affected persistent data; code smallest vertical slice; run tests; inspect changed files and identity; commit; open/review PR as appropriate; merge to develop; run acceptance; promote to main only verified. Vercel or other deployment settings remain unchanged unless approved.
After each meaningful milestone update STATUS/HANDOFF and link actual SHAs. Never force push, rewrite history or embed keys.
