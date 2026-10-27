# P2 guarded local export — optional source-only beta utility

## Problem, designs and selected mitigation

Previously the SOVIA source parser rejected JSON input >1 MiB / >1000 events, but a 1000-event fabricated alert-dense input (~307 KB) produced >2.14 MB compact JSON findings. Output expansion is independent of input size. The original CLI rendered the full report before staging and used exclusive hard links plus best-effort rollback, but had no per-file size check or early free-space estimate.

1. **Directly change sovia_audit.py and the old portable ZIP**: broader immediate coverage but changes tested release identity and all historic customers/CLI behavior, may impose an unapproved quota.
2. **Add an explicit opt-in source-only guarded CLI**, using the real core and existing atomic-ish writer (**implemented**): preserves old CLI and v0.10 ZIP checksum, checks actual byte sizes before any staging and best-effort free disk space by filesystem, reuses exclusive no-clobber writer and tests failure rollback.
3. **Input-only size check**: rejected because output may be much larger than input.

## Usage: trusted local host / authorized sanitized structured JSON only

Run from the developer checkout (not included in old v0.10 portable ZIP):

~~~sh
python -I -B sovia_guarded_export.py --input examples/demo_five_rules.json --html-output NEW_REPORT.html --json-output NEW_REPORT.json --local-test-budget-bytes 1048576
~~~

The caller must choose two new report paths, an existing output directory and one fixed **local test** per-file ceiling: 1048576 (1MiB), 2097152 (2MiB), or 4194304 (4MiB). The option is **not** a customer quota, product promise, or default. Return 0 on complete local writing, 2 on rejection; JSON stdout/stderr include fixed or aggregate fields and no source paths or raw event values.

This opt-in helper supports only canonical JSON and HTML+JSON. The existing CSV/PDF exports and all default CLI uses remain unchanged, **not protected by this helper**. It never sends telemetry, executes captured tool calls, uploads files or persists input copies; it writes only the two user-selected local output files when it succeeds.

## Failure protections (scope of claim)

- Validate the input using the existing 1 MiB/depth/event guards, reject input symlinks, duplicate input/output paths, occupied targets and missing output directories.
- Render actual Korean HTML and indented JSON completely in memory, measure UTF-8 sizes of both. Reject if *either* output exceeds the explicitly chosen local test budget; create no outputs in this case.
- Estimate free disk space for *both* files combined per filesystem, with an extra 64 KiB per file reserve. This is only a best-effort snapshot; concurrent writers, OS quotas, network shares, permissions and real disk allocation may still cause a later write to fail.
- Reuse original write_reports_atomically: write/fsync temp in the target directory, publish by exclusive hard links, never intentionally overwrite, attempt to remove only this process's newly linked files when a stage/publish error occurs. This is **not an atomic multi-file filesystem transaction**, nor a power-loss durability guarantee. Concurrent readers may observe one file before the other.
- Failure simulation exercises disk-space rejection and failures on the first/second publish link; verifies staged temporaries removed and target rollback for those specific synthetic cases. Real ENOSPC/OS ACL/network filesystem and race behavior on the owner's machine remain **unverified**.
- The user remains responsible for local lawful source authorization, sensitive content and original backups. The script can contain source event data in output JSON, and should not be run on unsanitized customer logs.

## Tests

~~~sh
python -m unittest discover -s tests -v
python -I -B sovia_guarded_export.py --help
python portable_smoke.py
~~~

GitHub Actions on Windows and Ubuntu with Python 3.11/3.13 validate the source and untouched portable beta. Real installed n8n, owner Windows Defender, browser Korean glyph rendering, PDF, signed release and commercial support remain pending. No Vercel/Production or listing.

## Next decision before packaging / commercialization

Require owner-approved supported formats, maximum report size, retention handling and specific operating environments. Then decide whether to integrate into the actual CLI and create an explicitly versioned new portable ZIP; never silently replace the old 12-file v0.10 archive or call this utility production-ready.
