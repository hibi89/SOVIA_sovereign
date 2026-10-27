## CURRENT P2 update — 2026-10-27: local evidence crosscheck

[PR #23](https://github.com/hibi89/SOVIA_sovereign/pull/23) integrates the source-only read-only `sovia_owner_evidence.py` checker into `develop` at `8e120a9db2baa1b490d2ce3987979366185fcf39`. The local operator may compare actual inner v0.10 ZIP hash, unmodified `SELF_CHECK_RESULT.json`, and separately declared manual findings. See [OWNER_EVIDENCE_CHECKER.md](OWNER_EVIDENCE_CHECKER.md) for the exact schema/command. **Its strongest result is `OPERATOR_CLAIMS_CONSISTENT_UNVERIFIED`, never independently validated owner-PC execution or commercial signoff**. Automated tests are Windows/Ubuntu CI only; the owner-device items below remain **NOT_CHECKED**. The checker is NOT inside the existing portable ZIP.

---

# SOVIA P2 — owner's actual Windows PC acceptance checklist

**Status: manual acceptance NOT PERFORMED.** CI passing on GitHub-hosted Windows is not proof of the owner's Windows machine, browser, Korean fonts, PDF rendering, antivirus or SmartScreen behavior. No automatic marking of manual fields as PASS.

## Test scope, before opening any program

Use only the existing **v0.10.0-beta 12-file unsigned portable ZIP** from the project's verified GitHub Actions CI artifact named `sovia-portable-beta` (provided it is still available). The verified synthetic artifact was produced by [Windows/Ubuntu run 40218991467](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40218991467); see [TEST_PLAN.md](TEST_PLAN.md). If that artifact is no longer retrievable, mark **BLOCKED — ARTIFACT_UNAVAILABLE** rather than substituting a random GitHub branch ZIP or guessing its integrity hash.

**No real customer input** is allowed in this check. If Windows/Defender flags the unsigned ZIP or launcher, do not disable antivirus, bypass SmartScreen, or add blanket exclusions to force the test. Record the block status and obtain independent release/security review before reconsidering.

Do not compare SHA-256 of GitHub's *outer downloadable artifact ZIP* with the hash of the inner 12-file portable ZIP. Previous documented verified 12-file inner ZIP SHA-256 is:

`894d83d5df3aa99fcd324454c9b28b2d3257b1dfc4465f963937e98c7a888f8b`

Use PowerShell `Get-FileHash -Algorithm SHA256 -Path <inner-portable-zip>` only after independently identifying which file is that inner portable ZIP; if unclear, mark **BLOCKED**. After extraction, the bundled `owner_selfcheck.py` runs its own allowlisted file manifest verification before any included auditing actions.

## Owner-specific steps (only when the owner chooses to test)

1. In a new empty local non-synced directory, extract the verified inner portable ZIP; do not extract over an existing installation. Ensure `RUN_SELF_CHECK.cmd`, `owner_selfcheck.py`, `verify_portable.py` and `examples\demo_five_rules.json` are present. Do not run from Downloads archive preview.
2. Confirm Python **3.11 or later**. On Windows PowerShell: `py -3 --version` (or `python --version` if the launcher is absent). If unavailable, mark **BLOCKED_PYTHON** rather than claiming a pass. The standalone ZIP is **not a native compiled EXE**.
3. Run the extracted `RUN_SELF_CHECK.cmd` once. This uses only synthetic input, invokes Python isolated mode and creates unique results in a sibling `SOVIA_DIAGNOSTICS\SOVIA_SELF_CHECK_...` folder. It never needs API tokens or a running n8n instance.
4. Open `SELF_CHECK_RESULT.json` in the new results folder. Expected automatic status: **`AUTOMATED_PASS_MANUAL_PENDING`**; `checks.python`, `package_integrity`, `audit`, `sqlite`, `dashboard`, `recovery` each **PASS**, with `synthetic.events=3`, `synthetic.findings=5`, `synthetic.reports=1`. Any failure/unknown value is a **BLOCK**, not a PASS.
5. Open `synthetic-audit.html` and `synthetic-dashboard.html` in a locally installed Windows browser. Verify Korean characters display without broken glyphs, risk rows and UTC timeline match 3 events / 5 findings, dashboard's recent event timeline is readable, no Internet/API request is required, links/overflow/zoom are usable. A Python/CI pass does not confirm these visual properties.
6. If optional PDF status is `GENERATED_NEEDS_VISUAL_REVIEW`, open `synthetic-audit.pdf` locally and check Korean font rendering, pages, tables and evidence text. If `SKIPPED_REPORTLAB_MISSING` or `SKIPPED_KOREAN_TTF_MISSING`, record **PDF_NOT_TESTED** rather than PASS. Installing optional Python ReportLab/using a valid local Korean TTF is a separate operator choice; do not copy font files into this PUBLIC repo. If `FAILED_OPTIONAL_PDF`, record failure and investigate.
7. Record Defender/SmartScreen observation, including whether an unsigned script/file was blocked or warned. **Never** disable protections as part of a successful test. Do not upload local Windows identifiers, paths, screenshots with personal data, crash reports or ZIPs from actual work to the public repository.

## Acceptance matrix (initially unverified)

| Item | Required evidence | Initial state |
|---|---|---|
| Provenance / hash and pristine extracted manifest | Verified inner ZIP hash and selfcheck `package_integrity=PASS` | NOT_CHECKED |
| Python support and Windows launcher | Native owner-PC Python >=3.11, CMD return code 0 | NOT_CHECKED |
| Offline synthetic counts/recovery | JSON report checks and 3 event / 5 finding consistency | NOT_CHECKED |
| Korean HTML audit/browser | Manual visual inspection, readability and no network | NOT_CHECKED |
| Korean local dashboard/browser | Manual KPI/timeline/zoom inspection | NOT_CHECKED |
| Optional Korean PDF | Manual visual PASS, or accurately recorded NOT_TESTED | NOT_CHECKED |
| Windows Defender/SmartScreen | Unmodified protection observation; no forced bypass | NOT_CHECKED |
| Owner decision for pilot and privacy/retention | Owner approval and independent customer-scope consent gates | NOT_CHECKED |

**Exit criteria:** The tool may be described as *owner-device synthetic accepted* only when evidence exists for each mandatory device/HTML/dashboard/security item. PDF can be clearly excluded from that narrow claim if optional PDF is not supported; do not claim PDF acceptance. Real customer onboarding and sale still require separately approved n8n compatibility, authenticated consent, data retention/deletion, and commercial support.

The latest source-only P2 privacy triage and registry extensions are **not included in the v0.10 portable ZIP**. Do not tell the owner the ZIP includes them. Manual Windows acceptance here is about the existing v0.10 audit/history/dashboard/optional PDF baseline.
