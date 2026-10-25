# SOVIA Sovereign

**Independent AI Agent Audit** — evidence-based explainable retrospective risk analysis for synthetic agent execution events.

**Current state (2026-10-26): P1 local synthetic proof of concept implemented on `feature/p0-audit-core`, NOT sold, deployed, certified or production-ready.** The `main` branch may still hold docs-only until integration review. See [STATUS.md](STATUS.md) for authoritative branch evidence.

> Repository **PUBLIC** at last verification. Do not upload credentials, real customer records, raw prompts, proprietary policies or private sources. Visibility changes require owner approval.

## Run the prototype (feature branch)
Requires Python 3.10+; no third-party packages and no external API keys.

```powershell
py -3 sovia_audit.py --input examples/demo.json --output report.html --json-output report.json
py -3 -m unittest discover -s tests -v
```

Open generated `report.html` locally. The provided fictional fixture generates 2 events and 3 explainable HIGH findings. For input contract and limitations see [QUICKSTART.md](QUICKSTART.md). This is **retrospective and synthetic**, not live blocking or intrusion prevention.

## Exact new-chat continuation phrase
```text
[소비아소버린 깃헙 레포지토리 보고 작업이어가셈]
```
Lead agent reads [RESUME.md](RESUME.md), [HANDOFF.md](HANDOFF.md), [STATUS.md](STATUS.md) and live GitHub heads, then advances the next verified unblocked task. `ㄱ` continues development.

## Delivery strategy
1. P1: three active-day local MVP (original Oct 26–28) with input bounds, 3+ deterministic rules, evidence pointer, HTML/JSON and runnable unit tests. First slice implemented; remaining P1 gaps in [GAP_MATRIX.md](GAP_MATRIX.md).
2. P2: fill blueprint gaps (CSV/PDF/SQLite/UI/adapter), security/recovery/installer and genuine sanitized authorized input validation before sale.
3. P3: marketplace copy and demo may be prepared as **drafts only**, publish after owner approval and commercial readiness.
4. P4+: revenue-validated Cloud and contracted Private reuse a single core, with Hybrid/advanced controls conditional on demand.

Zero-cash starting plan; no hosted telemetry, SaaS account, paid LLM, billing or deployment exists.

## Project references
[Operating rules](AGENTS.md) · [PRD](REQUIREMENTS.md) · [MVP 72h](MVP_72H.md) · [Gaps](GAP_MATRIX.md) · [Architecture](ARCHITECTURE.md) · [Roadmap](ROADMAP.md) · [Test plan](TEST_PLAN.md) · [Security](SECURITY.md) · [Listing draft](LISTING_PREP.md) · [Business](GO_TO_MARKET.md) · [Decisions](DECISIONS.md) · [Branches](BRANCHING.md) · [Current status](STATUS.md) · [Handoff](HANDOFF.md).
