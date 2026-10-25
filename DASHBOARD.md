# SOVIA Audit Lite v0.8 — 오프라인 감사 이력 대시보드

A static, standalone Korean HTML dashboard of an **existing SQLite v1 history database**, not a cloud website, live protection gateway, or authenticated multi-user app.

## PowerShell demo using synthetic data
Use a private local working folder and NEW filenames (never put generated reports or SQLite customer metadata in PUBLIC GitHub). Python 3.11+ was tested in CI.

    py -3 sovia_history.py import --input examples/demo_five_rules.json --db sample-history.sqlite
    py -3 sovia_dashboard.py --db sample-history.sqlite --output sample-dashboard.html
    start .\sample-dashboard.html

To refresh, choose a new HTML filename; existing snapshots are not overwritten. For existing SQLite history, only the second command is needed. See HISTORY.md for database import, no-clobber backup, restore and deletion.

## Screen sections and limits
Four headline counts: imported reports, unique events, findings, missing evidence pointers. Risk by severity and rule ID, latest 100 report rows, 100 finding rows, and 100 event time rows; 20 most frequent severity/rule groups. Overall totals cover all stored rows. Entries show hash prefixes, timestamps and evidence presence rather than raw event/agent/tool names or target/source text.

## Operational safety
Read-only SQLite connection, version/integrity/foreign-key checks and consistent snapshot; no DB modifications and no automatic original input read. HTML is escaped/size-bounded (160 chars per cell, 2 MB max) and generated with restricted CSP/no JavaScript, online assets, forms, server or remote requests. Output uses exclusive no-clobber file staging, rejects existing targets and SQLite/output aliases. Absent/corrupt/unsupported input fails without creating a report.

Hashed prefixes and timestamps remain linkable/potentially re-identifiable. This is pseudonymized metadata, **not anonymous data**. A static HTML file can be copied/shared, so protect/delete it under your policy. No source evidence is independently verified, and an absence of findings never proves safety. No access control for anyone with the file; no automatic refresh/filter, real-time alerts, power-loss secure erasure or customer-ready system.

## Test status
2026-10-26 KST: P2 v0.8 feature/p2-offline-dashboard implements a read-only SQLite v1 to standalone Korean HTML dashboard; no local server, JS, outbound network, data write or output overwrite. Tested source SHA c8bcbc9d9191c0bd98da66750fae3b456258391f; GitHub Actions https://github.com/hibi89/SOVIA_sovereign/actions/runs/40215480334 4/4 SUCCESS, Windows/Ubuntu x Python 3.11/3.13, each 148 discovered/138 PASS/10 optional PDF SKIP/0 FAIL. New tests 23. Not owner PC/browser visual QA, real customer records or production.
CLI, HTMLParser and synthetic unit integration run. NOT independently verified on owner's own Windows machine/browser (including visual layout/font), with real customer data, long-running concurrency, sale security gates, or Vercel/Production. PDF-specific cases skipped in this current CI and were tested historically in a different local environment.
