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


## Latest portable v0.9 develop checkpoint 2026-10-26
**LATEST INTEGRATION (2026-10-26 KST):** [PR #15](https://github.com/hibi89/SOVIA_sovereign/pull/15) merged v0.9.0-beta deterministic portable ZIP/verifier/synthetic full smoke into `develop`, merge SHA `0a16a032dc26970ba197aa8e874a22fcb2a2c0a6`. [Post-merge Actions run 40217328939](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40217328939) **4/4 SUCCESS** (Windows+Ubuntu × Python 3.11/3.13), per job 177 discovered / 167 PASS / 10 optional PDF SKIP / 0 FAIL, and full clean-extracted isolated-Python audit→SQLite→dashboard→backup/restore PASS. Tested reproducible ZIP SHA256 `6442c6896118fc44cd309fcd6596a59d6a17bb6e8252ddc45a8b15c34d5fd7c3`. `sovia-portable-beta` downloadable from Actions artifacts, unsigned ZIP+checksum, NOT an official signed Release. **On ㄱ**: inspect newest `develop`, then start P2 owner-Windows acceptance/self-check workflow (one-command local diagnostics; sample/fresh-folder tests), optional PDF/font/visual/manual verification guidance, then real authorized data/privacy/retention/failure-handling commercial gates. Do NOT redo JSON/CSV/SQLite/dashboard/package or merge PR #15 again. `main` remains docs-only; no Production/Vercel, no owner device/customer validation or sale approval. Earlier sections are archival.


## Owner v0.10 feature and CI checkpoint 2026-10-26
feature/p2-owner-selfcheck was created from develop 0070339329684d880a0503aa7eb690ba642ebaed for isolated Python/Windows .cmd self-check and portable v0.10. Tested executable at SHA cadc2baf8302f9583196fba7b6618c5c264d5a24, CI 40218607947 4/4 green. PR #16 exists, merge only after green latest head; keep default main docs-only and unsigned beta separate from production.


## v0.10 integration checkpoint (2026-10-26)
**LATEST VERIFIED INTEGRATION — 2026-10-26 KST:** [PR #16](https://github.com/hibi89/SOVIA_sovereign/pull/16) merged SOVIA v0.10.0-beta Windows one-click synthetic self-check, 12-file portable ZIP and optional Korean PDF/font diagnostic into `develop` at merge SHA `60a2ea28fed91d320211ee8f8ec594c24971d472`. [Post-merge CI run 40218991467](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218991467) **4/4 SUCCESS**: Windows Python 3.11/3.13 each 189 discovered/179 PASS/10 PDF SKIP/0 FAIL, Ubuntu 3.11/3.13 each 189 discovered/178 PASS/11 SKIP (Windows .cmd test)/0 FAIL; all four include full extracted-ZIP synthetic audit/SQLite/dashboard/recovery/self-check. Same 12-file ZIP SHA256 `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`, unsigned CI artifact `sovia-portable-beta` available. **PR integration DONE; DO NOT repeat.** On `ㄱ` next: verify latest develop HEAD and continue P2 product acceptance/privacy/retention/authorized n8n-like sanitized source or adversarial tests, prioritizing safe offline work. Actual owner's Windows PC, browser visuals, AV/SmartScreen, ReportLab+Korean TTF PDF visual, customer data and commercial/production are **NOT VERIFIED** and need owner/local evidence. `main` remains docs-only and unreleased. Earlier feature-only references are archived.

