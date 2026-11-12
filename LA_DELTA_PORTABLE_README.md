# SOVIA 0.14.0 LA review delta beta — synthetic-only, not for retail

**This is a new source-only, unsigned ZIP.** The 0.13 LA-review beta and frozen v0.12/v0.11.2/v0.10 artifacts remain untouched. This archive includes only publicly fabricated fixtures; no customer logs, private HAE/Lightning Azent source, credentials, binaries, interpreter, model, web service, or actual integration.

## Run on a Windows machine with Python 3.11+
Verify the original ZIP with the adjacent .sha256 using an independently obtained trusted file or repository-owned verifier; this checksum is **not a signature**. Extract into a NEW directory. Run `RUN_LA_DELTA.cmd` (or `RUN_LA_DELTA.cmd --ci`). The script verifies its own fixed package, generates two NEW sibling folders `SOVIA-LA-DELTA-before` and `SOVIA-LA-DELTA-after` from fabricated events, and prints only verified aggregate risk severity changes. It rejects duplicate runs rather than overwrite prior output.

You may also run `RUN_LA_REVIEW.cmd` for the original 0.13-style single fabricated review demonstration, which creates a different sibling folder.

On a developer machine, compare **two already-created synthetic-only review bundles**:

```sh
python -I -B sovia_la_review_delta.py --previous path/to/before --current path/to/after --synthetic-only
```

The command validates both input folders, prints a JSON severity/count difference and creates no files. Higher or lower counts do **not** prove the underlying events are real, complete, chronological or safe, and neither comparison grants execution approval.

Original customer audit or LA records, legal provenance, human-approved permission scope, physical Windows/Defender/SmartScreen, PDF/print, signing, licensing and genuine customer acceptance are not verified. Commercial RELEASE HOLD.
