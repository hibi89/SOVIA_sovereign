# SOVIA P2 — owner synthetic artifact **static** preflight (source-only)

Status: **offline, read-only, simulation-only**. Does NOT independently verify the owner's Windows PC, browser appearance, Korean PDF glyphs, Defender/SmartScreen, native installed n8n or production readiness.

## Purpose / architectural distinction

The existing portable v0.10 beta's `owner_selfcheck.py` performs synthetic audit/SQLite/dashboard generation, while existing `sovia_owner_evidence.py` cross-checks a portable SHA-256, a selfcheck JSON and manually *declared* results. Neither inspects the actual generated HTML pages for *static* active markup/resources, verifies their visible count literals against JSON or examines optional PDF presence/headers.

This new source-only `sovia_owner_artifact_preflight.py` fills that **separate** gap. It is not bundled into the existing 12-file beta, does not modify earlier files or write results, and never launches a program, HTML/PDF viewer or network request.

## Inputs

```powershell
py -3 -I -B sovia_owner_artifact_preflight.py --results-dir "LOCAL_PATH_TO_SOVIA_SELF_CHECK_..."
```

Use a private, **existing** results folder created by the v0.10 `RUN_SELF_CHECK.cmd`, containing:
- `SELF_CHECK_RESULT.json`
- `synthetic-audit.json`
- `synthetic-audit.html`
- `synthetic-dashboard.html`
- `synthetic-audit.pdf` **only if** original selfcheck reported `GENERATED_NEEDS_VISUAL_REVIEW`

The standalone module loads existing `sovia_owner_evidence.py` and `sovia_audit.py` from its sibling source folder. Python 3.11+, stdlib only. It refuses symlinked inputs, missing artifacts and oversized files; JSON reads use existing duplicate-key/size/depth-limited parser. It never reads customer n8n execution records.

## Bounded validation

1. Validate selfcheck's existing strict v0.10 synthetic Windows **claim** contract: mandatory checks PASS, synthetic 3 events/5 findings/1 report, owner visual/security decisions remain NOT_CHECKED. A synthetic Windows label or selfcheck report is **not proof** of actual owner-device execution.
2. Require generated report JSON has **3 events**, **5 findings** and all 5 existing rule IDs. Validate 16-hex report ID.
3. Parse local UTF-8 audit HTML and require 2 tables, correct ID, 3-event/5-finding textual summary and explicit coverage warning. Parse dashboard with 5 tables, offline warning, 1/3/5 summary numbers and exact CSP restrictions including `default-src 'none'`, `script-src 'none'`, `connect-src 'none'`.
4. Reject script, iframe, img, link, external-resource attributes, inline event handlers, duplicate attrs, meta redirects and obvious CSS `@import`/`url(...)`/`expression(...)`; this is a **heuristic static allowlist, not a complete HTML security audit or browser runtime test**.
5. If optional PDF was generated, require bounded local file with `%PDF-` header and `%%EOF` marker only. This cannot detect malicious PDF internals, broken Korean glyphs, font substitutions, page overflow, or legibility. If selfcheck skipped PDF, reject contradictory existing PDF; if original PDF selfcheck failed, stop with rejection.

Success returns `SYNTHETIC_ARTIFACT_STATIC_CHECKS_PASSED_MANUAL_PENDING`. Every actual acceptance flag remains false; no printed absolute paths, machine identifiers or document contents. Errors yield `REJECTED` with a fixed code (exit 2), success exit 0.

## Required human checks and caution

**Still manually open the actual audit HTML, local dashboard HTML and generated PDF where applicable; inspect Korean text, responsiveness, layout and evidence readability.** Observe Defender/SmartScreen without bypassing warnings or disabling protections. Use `OWNER_WINDOWS_ACCEPTANCE.md` and the existing `sovia_owner_evidence.py` for separate user-declared review recording, recognizing self-declared results are never independently verified. Do not upload `SOVIA_DIAGNOSTICS` or real files/screenshots into the PUBLIC GitHub repo.

Static checks can catch synthetic output tampering/accidental active markup but cannot guarantee XSS freedom, no browser network requests under all conditions, real machine compatibility, absence of customer PII, real n8n integration, or signing/provenance. Signed release and production require separate owner approval.

## Repeatable regression evidence

```powershell
py -3 -m unittest discover -s tests -p test_owner_artifact_preflight.py -v
py -3 -m unittest discover -s tests -v
py -3 portable_smoke.py
```

Adversarial tests create *only synthetic* reports in temporary folders. No actual browser/Windows visual/antivirus outcome may be declared PASS from CI. Existing v0.10 portable ZIP and `main` are unchanged.
