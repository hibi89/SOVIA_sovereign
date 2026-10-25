# SOVIA Sovereign — Independent AI-Agent Audit

**Local-first retrospective agent risk and evidence audit.** Python standard-library executable proof of concept v0.3.0 on branch feature/p0-audit-core. No mandatory LLM, cloud server, paid API or remote telemetry.

## P1 MVP (verified 2026-10-26 KST)
Structured fictional JSON events -> bounded canonical UTC events -> 5 deterministic evidence-linked findings -> Korean HTML risk table and event timeline + machine-readable JSON. Missing policy/evidence explicitly unknown. 40 local unit tests pass, 0 fail; clean temporary copy using isolated Python -I -B passes; Chromium can render generated HTML markup (5 findings, 3 timeline events). Existing output files protected against overwrite; staged output writes with rollback on expected errors.

**Not ready for sale or customer log ingestion:** clean Windows device/install, original provenance, source-specific integrations, privacy/redaction, false positives, recovery, deeper security and independent operational checks remain pending. GitHub repository remains PUBLIC — do not commit secrets/customer documents/private prompts.

## Run from feature/p0-audit-core
Windows PowerShell:

    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json
    py -3 -m unittest discover -s tests -q

Use unused output filenames for each run. See [QUICKSTART](QUICKSTART.md) for details and platform limits, [GAP_MATRIX](GAP_MATRIX.md) for full blueprint gaps, [STATUS](STATUS.md) for evidence and [HANDOFF](HANDOFF.md) for work resumption.

## Product path
P1 3 active-day MVP proof -> P2 fill CSV/PDF/SQLite/UI/authorized adapter and commercial safeguards -> owner-approved listing and paid customer evidence -> shared-core Cloud/Private expansion only if justified. Production URL and Vercel deployment do not exist.

## Continuation trigger
[소비아소버린 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. Read HANDOFF.md -> STATUS.md -> AGENTS.md -> REQUIREMENTS.md -> source/tests, always recheck live SHA; proceed with next safe unit.
