## 2026-10-27 P2 update — bounded synthetic capacity measured, NO customer performance guarantee

[PR #32](https://github.com/hibi89/SOVIA_sovereign/pull/32), [4/4 successful CI 40473847652](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40473847652). Source-only benchmark `sovia_capacity_benchmark.py` and guide `SYNTHETIC_CAPACITY.md` measured fixed fabricated 10/100/500/1000 event normal+alert-dense core cases on Windows/Ubuntu × Python 3.11/3.13, 632 tests/job, zero failures. The **technical source JSON input guards** are <=1,048,576 bytes and <=1000 events, both must hold; they are **NOT customer package quotas or guaranteed speed**. One-round 1000 alert-dense core timings were 315–568 ms on cloud CI, including tracemalloc overhead and excluding file output/PDF/SQLite. The dense result expands from 307201 input bytes to **2136699 JSON report bytes** (4998 findings), so storage/export/report size needs a separate commercial guard.

**Buyer wording DRAFT, not released:** “명시된 v1.0 구조화 실행 이벤트의 로컬 사후 규칙 분석을 지원하는 제품을 검증 중입니다. 현재 코드에 파일 1MiB·이벤트 1000개 입력 상한이 있으나 **판매 제공량·처리시간·실제 지원 OS·데이터 출처 및 납품 범위는 검증 후 계약별 확정**합니다.” Do not quote 315ms, 1000 events, memory allocations or optional PDF as a supported buyer guarantee. Price 199,000 KRW remains speculative, not a confirmed package. Real customer consent/n8n integration, owner Windows/browser/Defender and Korean PDF manual acceptance, incident/privacy/retention terms, accepted screenshots and owner publication approval still OPEN. No public listing or release performed.

---

## 2026-10-27 P2 update — reproducible synthetic SAMPLE pack source (NOT published)

[PR #31](https://github.com/hibi89/SOVIA_sovereign/pull/31) adds **source-only** `sovia_demo_pack.py` with full test coverage; see `SALES_SYNTHETIC_SAMPLE.md`. It runs the existing deterministic SOVIA engine on one **locked fabricated 3-event/5-finding fixture**, then writes to a new local folder: visibly/print-watermarked SAMPLE HTML, explicitly labeled JSON, honest buyer-facing scope, and unsigned checksums. It does **not** fabricate screenshots, demonstrate actual owner Windows/browser rendering, authorize customer logs, publish a marketplace listing, claim a signed release or replace original v0.10 ZIP. A working generator meets the code prerequisite, **not** the checklist's owner-reviewed/publication tasks.

[PR CI 40472609343](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40472609343) full Windows/Ubuntu × Python 3.11/3.13 4/4 SUCCESS, 599 tests/job, 0 FAIL; old portable ZIP unchanged. Local owner review of actual sample and real app screenshots remain pending. Pricing `199,000 KRW` remains purely a hypothesis, not a quote, supported volume/delivery commitment or released offer.

---

# SOVIA Audit Lite — product listing preparation (DRAFT, not published)
Date: 2026-10-26 KST
A draft for online listing on Krmong, a product site, technical blog or B2B outreach. No commercial claims until feature tests and legal readiness confirm them.

## Working positioning
Name (pending trademark review): SOVIA Audit Lite
One-line promise (conditional on features demonstrated): "AI 에이전트 실행 로그를 근거 중심으로 분석하여 도구 사용·접근 정책 위반을 한국어 보고서로 정리합니다."
Target buyer: AI automation development agencies and SMB owners responsible for deployed agents.
Differentiator: read-only, explainable evidence-oriented audit and remediation report, not a replacement for EDR/IDS/attorneys.

## Offer concept (PRICE HYPOTHESIS)
Proposed one-time 199,000 KRW for **one supported agent/source**, fixed supported log schema, capped input size and a single report. Event quota, revision turnaround and delivery hours TBD by actual benchmarks.
Deliverable after verified build: Korean findings summary, each finding linked to observed event, scoped recommendations, report in tested output formats, unknown/unobserved disclaimer.
Cannot claim real-time blocking, zero data leakage, certified security, universal integration, 24/7 human monitoring, all NAS compatibility or cross-customer monitoring.

## Launch collateral built in parallel (no customer data)
[ ] Verifiable demo on synthetic normal, suspicious, malformed fixtures
[ ] 2-3 REAL screenshots of running app/report (after implementation; no fabricated app screenshot)
[ ] 1 redacted sample report from synthetic events, with obvious SAMPLE watermark
[ ] Supported inputs and environment matrix (one verified version before listing)
[ ] What is included/excluded, supported volume, delivery time and revision policy
[ ] Privacy processing explanation: local-only default, secrets/raw prompts not required
[ ] FAQ: observability limit, false positives, not certification, setup requirements
[ ] English/Korean search terms and SEO landing page content
[ ] Refund/support/billing language; applicable business registration and tax requirements
[ ] Trademark/name-risk and IP check before spend
[ ] Price/cost/service-time worksheet and buyer interviews
[ ] Owner approval prior to public commercial listing or offsite data collection

## No-cost online discovery
Public-safe GitHub synopsis, sanitized tutorial/demo, written technical how-to (n8n AI agent risk logs), direct non-intrusive remote agency outreach. Krmong is a channel, not the only customer pipeline.
Do not spend on ads, commercial hosting, paid LLM APIs or domain until signal and owner authorization.

## Publication gate
Minimum: actual runnable product, controlled input contract, honest screenshots/report, supported environments tested, data-handling/retention policy, terms and support scope, customer authorization, incident escalation limitations, owner final approval. A scheduled launch date does NOT override this gate.
