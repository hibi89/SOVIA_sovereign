## 2026-10-27 verified candidate checkpoint

[PR #53](https://github.com/hibi89/SOVIA_sovereign/pull/53) merged 9a1e21c279e27e03dc4bb75e43cb385dc5bfe1d1. [CI 40509368149](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40509368149) Windows/Ubuntu Python3.11/3.13 **4/4 SUCCESS**, 797 tests per job, 0 fails, original v0.10 and v0.11.2 immutable ZIP SHA-256 clean extract smoke PASS. New 0.12 source-only evaluator / CLI and opt-in preview are verified on synthetic inputs; no commercial package or real n8n support. Legacy history/report identity migration OPEN and Issue #52 intentionally remains OPEN for supported release. Current CI generated Edge synthetic A4 but this run's PDF was not independently raster-inspected.

---

# SOVIA 0.12 temporal correctness candidate — NOT A CUSTOMER RELEASE

## Reproducible defect

Three fabricated events (same agent/run, max 2 tool calls per 60 seconds):
E1 15:01:00Z, E2 15:01:00.500000Z, E3 15:02:00.300000Z.
Original audit lexical order is E2,E1,E3 and incorrectly emits one BURST_TOOLS alert.
True UTC time order E1,E2,E3 evicts E1 (60.3 seconds old at E3), leaving two valid calls, no alert.

## Design alternatives and scope

A. Full legacy engine copy and one-line fix: easy isolation, but duplicates ~20 KB strict code and future maintenance.
B. Versioned source-only adapter: reuse legacy validation, normalization, provenance and four rules; recompute ONLY burst risk using UTC-aware datetime and stable event-ID tie. Less maintenance, no frozen archive change, but the new candidate depends on old evaluator, and old SQLite history requires versioned report identity migration before interoperability.

Option B implemented for TESTING ONLY. No approved shipping package, no signature, no customer data, no real native n8n. Existing 0.10/0.11.2 package and hashes are strictly unchanged. The old CLI/engine still contains the bug; a v0.12 candidate must not be conflated with release of a corrected commercial auditor.

Changed modules: sovia_audit_v012.py (new, offline standalone source-only CLI), tests/test_temporal_successor.py, source-only printable preview now reuses corrected candidate evaluator, and this record. Version marker 0.12.0-preview, updated BURST_TOOLS rule version 1.1, report schema 1.0. Report ID remains derived solely from normalized source and policy, so it can equal the historic report ID even with different findings. DO NOT import this candidate into legacy SQLite metadata history before an explicit schema/report-identity migration is designed and verified.

## Synthetic proof command

Run in a trusted checkout Python 3.11 or later:
python -I -B sovia_audit_v012.py --input examples/demo_five_rules.json --html-output NEW.html --json-output NEW.json --synthetic-only

Expected fabricated demo: 3 events and 5 findings. Test fractional 60-second boundary via tests/test_temporal_successor.py. All uses offline with a heuristic PII-pattern preflight; pattern absence/consent or source provenance is NOT certified. No supported customer event count/quotas, no cloud, production, billing, real authorized n8n integration, user-PC/Defender/SmartScreen or optional Korean PDF proof. GitHub CI on Windows/Ubuntu Python3.11/3.13 and both legacy extracted-ZIP smoke is required before merge.
