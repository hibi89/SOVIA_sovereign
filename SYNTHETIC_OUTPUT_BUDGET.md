# P2 synthetic output budget dry run — source only

## Reason
[PR #32](https://github.com/hibi89/SOVIA_sovereign/pull/32) demonstrated 1,000 fabricated alert-dense events produce 4,998 findings and roughly 2.14 MB of **compact** JSON despite a ~307 KB input. The real audit CLI uses `indent=2` (larger) and also emits full HTML. Existing 1 MiB input validation is NOT a report output cap.

## Alternatives and decision
- **A: modify the shipped auditor/portable archive immediately.** More immediate enforcement but changes the tested 12-file ZIP, output/rollback behavior and unapproved delivery limits; requires broader regression and deployment review.
- **B: source-only deterministic, fail-closed output preflight using the actual real renderers** (**selected**). It measures exact HTML bytes and indented JSON bytes, checks separate hypothetical per-file budgets, emits only aggregate metadata, and never writes reports. No customer data or network. Protects current beta behavior; makes the expansion risk measurable before choosing an approved export policy.
- C: sell input 1 MiB/1,000 events as an implied output limit — rejected as inaccurate.

## Command and exit codes

```bash
python -I -B sovia_output_budget.py --synthetic-only --events 1000 --profile alert_dense --budget-bytes 1048576
```

Supported counts 10/100/500/1000; profiles normal/alert_dense; **simulated** per-file budgets 1/2/4 MiB only. Exit **0** within simulated limits, **3** would exceed the selected simulated budget, **2** invalid arguments/source issues. No actual report exported, no path accepted, no overwrite, no customer quotas set. The temporary fabricated parser input is deleted automatically.

```bash
python -m unittest discover -s tests -v
```

## Explicit remaining risks
This is a preflight API + demonstration only, NOT enforcement in `sovia_audit.py`, `build_portable.py` or the v0.10 ZIP. PDF, CSV, filesystem available space, allocation bounds, multi-output transactional recovery, real data and concurrent loads remain unverified. `assess_report` measures finished serializations in memory; it is not streaming or safe for arbitrarily large reports outside the source parser's bounded contract. No SLA, storage quota or customer environment has been approved. Before activating an actual output policy, obtain an approved budget based on customer environment, preserve no-overwrite/rollback behavior, add real CLI integration tests and independently verify owner Windows/browser/PDF/Defender.
