# SOVIA P2 — synthetic capacity and bounded core workload measurement

**Status: non-SLA, unapproved customer quota.** A deterministic benchmark of fabricated data only. It is **not** a real client workload test, owner Windows PC performance certificate, production load test, memory leak analysis, runtime security audit or contract promise.

## Actual core input constraints vs performance measurements

These are **source-code validation bounds** from existing `sovia_audit.py`, independent of this benchmark:

| Constraint | Actual canonical JSON parser/engine limit | Scope |
|---|---|---|
| File read | **1,048,576 bytes (1 MiB)** | Canonical `read_document`; JSON input only in this benchmark |
| Event array | **at most 1,000 events** | `evaluate` canonical event records |
| JSON depth | **at most 16 nesting levels** | Parsed JSON structures |
| IDs and fields | Existing strict text, domain, timestamp validation | Supported schema v1.0; not arbitrary n8n execution JSON |

A 1,000-event input still fails if it exceeds 1 MiB or violates schema/field/policy rules. Conversely passing a synthetic 1,000-event test **does not** mean all 1,000-event real customer records are supported commercially.

## Bench design

`sovia_capacity_benchmark.py` is **source-only** and uses exclusively programmatically fabricated `*.example` domains, `sim-####` IDs, constant policy, no raw prompts/credentials and no customer source data. It generates two deliberately different deterministic profiles:

- `normal`: all tools/destinations approved, synthetic evidence references present, **0 findings**.
- `alert_dense`: all tools/destinations violate policy, simulated sensitive scope without asserted permission and missing evidence, plus dense 1/sec calls over a 2/minute threshold. Expected **4 × events + (events − 2)** findings for supported counts. This intentionally stresses result/report rendering, not customer behavior.

For 10, 100, 500 and 1,000 events, it writes a synthetic fixture to an automatically cleaned temporary local folder. **Measured work**: canonical bounded JSON disk read → actual five-rule `evaluate` → Korean HTML `render_html` → actual JSON report serialization. It records serialized input byte count, findings and HTML/JSON byte counts. Wall-clock time uses `time.perf_counter_ns()`; Python tracked peak allocations use `tracemalloc`. Neither is process resident memory (RSS), whole-device memory, CPU utilization nor an external service response-time measurement.

**Not included in timing**: input fixture generation, report publication/fsync, PDF/font support, SQLite/history, backup/restore, browser rendering, real n8n API/authorization, upstream redaction or cloud networking. `tracemalloc` can itself add timing overhead; metrics from 1–3 repeats are illustrative and device/interpreter-dependent.

## Run

```powershell
py -3 -I -B sovia_capacity_benchmark.py --synthetic-only --counts 10,100,500,1000 --profiles normal,alert_dense --rounds 1
```

Safe options: event counts are an allowlisted subset of **10,100,500,1000**; profiles an allowlisted subset of **normal,alert_dense**; repeats **1–3**. Unknown options, extra modes, duplicate cases and missing `--synthetic-only` refuse execution. This script accepts **no arbitrary input file**, no real customer values and writes no persistent benchmark output. It prints only one aggregate machine-readable JSON object with standardized labels for status and explicit booleans `performance_sla_or_commercial_quota_approved:false`, `actual_customer_data_used:false`, `independent_owner_machine_verified:false`.

CI adds the same command after the full test suite on GitHub-hosted Windows/Ubuntu × Python 3.11/3.13 and before existing v0.10 portable smoke. Absolute timings/peaks should be read from the **specific successful CI run logs** and not treated as reproducible hardware guarantees, P95 latency, leakage proof or a published supported quota. A benchmark passing at a count only demonstrates that **that exact synthetic profile** completed on that runner.

## Proposed narrow buyer-facing promise (NOT APPROVED)

“정해진 SOVIA v1.0 JSON 구조를 이용한 로컬 사후 규칙 감사 도구입니다. 파일 최대 1 MiB 및 이벤트 1,000건 이하라는 기술적 입력 상한은 있습니다. **실제 고객에게 제공할 건수, 허용 보고서 규모, 처리 시간, 운용 OS, 납품·수정 범위는 별도 실데이터 사용 승인과 실기기 검증 후 확정합니다.**”

The draft `LISTING_PREP.md` 199,000 KRW figure is a **price hypothesis** only. Do not advertise `1,000 events processed in X ms`, memory ceiling, PDF availability, arbitrary raw n8n import, confidentiality certification or real-time safety until corresponding owner-approved evidence exists.

## Failure and stop conditions

Wrong count/profile, exception, missing local Python module, input >1 MiB, unexpected event/finding count, missing rendered HTML/JSON or exhausted resources means **no capacity evidence** for that case. No bypass of core limits, no data uploads, no CI runner hardware/username disclosure and no auto-change to user files or repo release settings. Any genuinely authorized client representative benchmark requires independent privacy+source/legal+retention and explicit owner permission.
