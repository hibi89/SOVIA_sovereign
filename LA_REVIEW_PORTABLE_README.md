# SOVIA LA Review 0.13.0-beta — offline synthetic-only candidate

This is a separately versioned **unsigned source ZIP candidate** for testing.
It does not replace the immutable SOVIA 0.10 / 0.11.2 / 0.12 beta packages,
and is not approved for sale, deployment, or genuine customer records.

## What it does
- Compares a fabricated plan and fabricated normalized observation IDs using
  the existing independent plan preflight, v0.12 post-audit and reconciliation.
- Displays three classes separately: planned risks, post-audit risks and
  planned-versus-observed discrepancies.
- Creates only a NEW output folder with `review.json`, `review.html`,
  `manifest.json`. No raw event rows, raw policies, prompts or customer files
  are exported. A separate read-only verifier checks file hashes and renders
  HTML again to check JSON/HTML consistency.
- No network, n8n API, external telemetry, live LA integration or execution.

## Windows 10/11 owner synthetic demo
1. Install an existing trusted Python 3.11+ interpreter; nothing is downloaded.
2. Verify the original `.zip` and adjacent `.zip.sha256` with the separately
   supplied `verify_portable_la_review.py` script before extracting. The
   transport digest is **unsigned** and cannot authenticate a publisher.
3. Unzip once into a **new empty directory**. Double-click
   `RUN_LA_REVIEW.cmd` to verify the pristine folder and execute only the
   bundled fabricated demo, saving results in a NEW sibling folder
   `SOVIA-LA-synthetic-review`.
4. Open the generated local `review.html`. A second click refuses to overwrite.
   Modify any bundled payload and the startup verification refuses execution.

For automation use `RUN_LA_REVIEW.cmd --ci` (no browser or pause). For direct
Python testing, from the package's extracted root:

```sh
python -I -B sovia_la_owner_review.py --plan examples/demo_la_plan_review.json --policy examples/demo_policy.json --observations examples/demo_la_observations.json --output-dir ../NEW-LA-REVIEW --synthetic-only
python -I -B sovia_la_owner_review.py --verify-output-dir ../NEW-LA-REVIEW
```

## Trust and limitations
All source/observation claims are **unauthenticated synthetic assertions**.
No finding is not proof of non-execution. A checksum or manifest can detect
accidental/partial edits but is not a signature; anyone replacing the entire
unsigned package or report could recalculate all digests. Filesystem guards
are best-effort and not a race-free security boundary. There is no real
Lightning Azent receipt ingestion, API authorization, independent PII
certification, actual end-user Windows/Defender/SmartScreen/print acceptance,
commercial license, customer pilot, or approved release. Keep RELEASE HOLD.

Existing report data stays local, and any interrupted output folder is left
for human inspection rather than silently treated as verified.
