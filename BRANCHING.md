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

## Integration checkpoint 2026-10-26
PR #12 integrated `feature/p0-audit-core` into `develop` at merge SHA `c5dc6099a76f5f3f9f3ca523855f88487bb4fa26` after 4/4 Ubuntu+Windows CI; no promotion to `main`. `feature/p0-audit-core` is a historical active branch; next approved P2 SQLite task should create a fresh scoped branch from `develop` when work starts. Avoid rebasing, deleting or force-pushing existing branch.

## P2 integration checkpoint 2026-10-26
PR [#13](https://github.com/hibi89/SOVIA_sovereign/pull/13) merged tested opt-in SQLite audit history from `feature/p2-sqlite-history` to `develop`, merge SHA `edf8ea3de4a4fd781de34642b3d3f07a1ff67e10`; post-merge CI [40214911902](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40214911902) 4/4 SUCCESS. No `main` code promotion. Next scoped branch for offline read-only dashboard should start from current `develop`, not the historical feature branch.

## P2 offline dashboard integration 2026-10-26
[PR #14](https://github.com/hibi89/SOVIA_sovereign/pull/14) merged feature/p2-offline-dashboard into develop SHA 1123851900aee34d1c02d2a4590c6a0b5852727d. Post-merge CI [40215946752](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215946752) all 4 OS/Python jobs SUCCESS (each 138 passed / 10 PDF optional skipped). main remains documentation-only; next new branch from develop targets portable offline packaging and clean-install verification. Do not force-push or discard historical branches.
