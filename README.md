# SOVIA Sovereign
Independent evidence-based AI agent behavior audit: offline-first retrospective risk analysis.

## Verified state (2026-10-26 KST)
Python v0.2.0 local prototype on feature/p0-audit-core. 5 deterministic rules, event timeline, Korean HTML and JSON outputs; 29 local unit tests passed, 0 failed; 3-event five-risk synthetic CLI demo reproduced. main/develop stay docs-only pending review; no hosted production app, no live customers, no commercial readiness. This GitHub repository is PUBLIC, so never upload secrets, customer logs or confidential prompts.

## Run prototype
Requires Python 3.10+ (tested on 3.13.5). Checkout feature/p0-audit-core, then run:

    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json
    py -3 -m unittest discover -s tests -q

Read QUICKSTART.md for event/policy contract and caveats. The product diagnoses supplied synthetic records; it does not block real-time attacks, certify security or verify source log completeness.

## Continue the project in a new chat
[소비아소버린 깃헙 레포지토리 보고 작업이어가셈]

Or use ㄱ. Read HANDOFF.md -> STATUS.md -> AGENTS.md -> REQUIREMENTS.md -> actual source; compare live branch HEAD first. Work next P1 Day3, then GAP_MATRIX.md fill, then commercial security and owner-approved sale; Cloud/Private later when justified.

References: AGENTS.md, REQUIREMENTS.md, ARCHITECTURE.md, MVP_72H.md, GAP_MATRIX.md, TEST_PLAN.md, QUICKSTART.md, STATUS.md, HANDOFF.md, SECURITY.md and LISTING_PREP.md.
