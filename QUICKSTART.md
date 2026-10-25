# SOVIA Audit Lite v0.6.0 — offline synthetic quickstart
Tested: Python 3.13.5 on Linux. Standard library only, no API keys or external calls. Windows Python 3.10+ is a design target, not an independently tested platform.

## One-command demonstration
Use a directory containing sovia_audit.py and examples/demo_five_rules.json. In PowerShell, run with NEW unused output filenames:

    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json --findings-csv findings.csv --events-csv events.csv

Or on Linux/macOS use python3 in place of py -3. The synthetic scenario produces 3 events, 5 findings and 4 output files:
- report.html — Korean risk table and chronological event timeline.
- report.json — full machine-readable canonical normalized report, findings and limits.
- findings.csv — 5 rows with rule/severity/event/evidence/rationale/remediation.
- events.csv — 3 normalized UTC ordered event rows.

Optional --findings-csv and --events-csv can be omitted. All outputs are **new files only**: never overwrite existing reports. Directories must already exist; unsupported hardlink filesystem causes safe failure. Avoid exporting confidential original data into a PUBLIC source repository.

## CSV details / limitations
CSV uses csv.writer with UTF-8 BOM and CRLF for common spreadsheet compatibility; formula-like values with potentially dangerous leading = + - @ receive an apostrophe prefix even when preceded by certain whitespace or Unicode marks. This was exercised by synthetic automated tests; not verified across Excel/Sheets versions or import settings, not a universal injection guarantee. CSV export is implemented; CSV **source import is now available only with a separate JSON policy**; see below. Original unsanitized payloads or captured prompts must NOT be supplied to commercial use until approval and redaction procedures exist.

## Source format and risk semantics
Input JSON schema_version "1.0", policy object and <=1000 events, file <=1MiB, nesting <=16. Events require event_id, occurred_at_utc (timezone), agent_id, run_id, tool_name; optional target, destination_domain, permission_asserted, outcome and source_pointer. Policies: allowed_tools, approved_destinations, sensitive_targets, optional max_tool_calls_per_minute integer 1..1000.
Risk rules: unauthorized tool; unapproved destination; sensitive target access lacking explicit permission; configurable burst in trailing 60 seconds; missing evidence pointer. Missing policy is unknown, and provided pointers are not independently checked. Reports do not certify compliance, detect unobserved actions or assure zero leaks.

## Verification
Run py -3 -m unittest discover -s tests -v (67 tests passed on the verified developer Linux Python 3.13.5). Existing filename -> exit 2; choose new paths each invocation. HTML+JSON+CSVs have best-effort rollback, not a multi-file transaction under system crash or concurrent readers. Before commercial usage, independent Windows test, backup/delete/recovery, real authorized sanitized logs and security review must pass.

## Optional Korean PDF output (P2 v0.5.0)
Existing HTML/JSON/CSV exports work without installing anything. To add a PDF file install the optional free Python package on the intended machine:

    py -3 -m pip install "reportlab>=4,<5"

Then run with **new unused output filenames**:

    py -3 sovia_audit.py --input examples/demo_five_rules.json --output report.html --json-output report.json --findings-csv findings.csv --events-csv events.csv --pdf-output report.pdf

If the system cannot find a Korean TrueType font, specify `--pdf-font "C:\Windows\Fonts\malgun.ttf"` (actual path may vary). Only use a font locally installed and usable under its license; do not upload or distribute its standalone file. The PDF uses A4 landscape, evidence status and Korean warnings. Missing dependency/font fails the invocation before any outputs are published. PDF contains user-supplied *normalized data only*, no raw prompts, and is not a compliance certificate. 2026-10-26 local ReportLab 4.4.9, 67/67 tests PASS, one-page synthetic PDF text/render PASS; 115-event six-page pagination PASS. No independent Windows/Excel/customer validation. Generated PDF may embed font glyphs; the project ZIP contains no fonts.

**Isolated Python packaging check:** after optional PDF module path fix at a7a1c6b8e151, extracted ZIP now also runs with `python -I -B` and PDF output. 67/67 tests pass in developer Linux environment; independent Windows not tested.


## Source CSV input (P2 v0.6, synthetic-only)
JSON input above remains unchanged. With a metadata-only **CSV input**, supply a **separate JSON policy** because CSV rows cannot establish authorization rules:

    py -3 sovia_audit.py --input examples/demo_source.csv --policy examples/demo_policy.json --output source-report.html --json-output source-report.json

Fixture equality check: 3 synthetic CSV rows produce the same 5 findings and normalized report as examples/demo_five_rules.json. Output files must not exist. CSV required headers: event_id, occurred_at_utc, agent_id, run_id, tool_name. Optional allowlisted headers: target, destination_domain, permission_asserted, outcome, source_pointer. No arbitrary/duplicate headers or extra cells, no raw_prompt/documents. Header names exact case. Permission field must be \`true\`, \`false\` or blank (= unknown), never inferred. Input supports BOM/UTF-8 and standard quoted cells, max 1 MiB and 1,000 rows; canonical event validation then checks IDs, timestamps, domains, duplicates and source pointers. \`--policy\` requires a JSON object with only \`schema_version: "1.0"\` and \`policy\` with supported rules; never accept a customer's unknown format by pretending full audit coverage. CSV strings are data, never executed. Source and policy are read-only; output never overwrites them.

GitHub Actions synthetic offline regression at workflow run 40212874275: Python 3.11 and 3.13 both successful; each 92 tests discovered / 82 passed / 10 optional PDF skipped / 0 failed. New actual Windows/NTFS and customer data validation remain unverified.
