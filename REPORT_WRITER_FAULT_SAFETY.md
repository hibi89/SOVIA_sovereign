# P2 report publisher fault injection — 2026-10-27

## Actual risk and minimal fix

The original `write_reports_atomically` linked a finished staging file to its destination *before* calling `os.stat(staging)` to record identity for potential rollback. If that post-link metadata call failed, the published path was never registered for rollback: a new output could survive a failed batch. The original routine also created an OS staging file descriptor before rejecting a non-bytes payload, risking an unclosed file descriptor.

Changed only `sovia_audit.py` writer ordering: validate payload **before** `mkstemp`; record `os.stat(staging)` **before** `os.link(staging, destination)`. Existing exclusive hardlink publication, staged `fsync`, symlink/existing target rejection and best-effort inode-matched rollback remain in place. The audit engine, rules, JSON/CSV schema, data limits and report serialization stay unchanged.

## Alternatives

1. **Add more tests without fixing publisher:** lowest byte-level compatibility risk, but leaves a known orphan-output error path (rejected).
2. **Minimal ordering fix with adversarial tests** (selected): no new customer limits/dependencies; changes source and therefore deterministic portable ZIP hash, requiring full portable regression.
3. **Replace with new transactional journal/DB:** larger storage/security surface, still cannot guarantee transactions to ordinary filesystem concurrent readers (deferred).

## Tests and scope

`tests/test_report_writer_faults.py`: 10 synthetic only cases including injected `ENOSPC` at first/second stage fsync, metadata errors before and after publication boundaries, concurrent new-target collision and its preservation, hardlink denial, second-link failure rollback, invalid input no staging descriptor, normal bytes/Unicode, existing target protection. All use temporary files and fault injection. Run `python -m unittest discover -s tests -v`; CI also runs `python portable_smoke.py` on Windows/Ubuntu Python 3.11/3.13.

**Important:** The portability ZIP is generated from current source; updating `sovia_audit.py` intentionally changes its SHA256. Historical v0.10 checksum `894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b` remains applicable only to prior source builds and archived Actions artifacts, **not** to the new source bundle. Do not represent either ZIP as signed or customer-ready. The rebuilt 12-file source beta ZIP SHA-256 measured identically on Ubuntu and Windows runners is `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`. `sovia_owner_evidence.py` explicitly pins this alongside the historical checksum; unknown digests still fail closed. A full four-platform green CI and extracted-ZIP verification is required before accepting it as regression evidence.

This fix does **not** guarantee transactional multi-file filesystem writes under power loss, malicious concurrent mutation, unavailable hardlinks, directory fsync, antivirus lock, externally shared directories or device corruption. It does not enforce a report output budget or perform PDF/browser/user-device validation. Any failed publish can require manual inspection for external racing writers and prior artifacts. No real customer data, production deployment or commercial offer was used.
