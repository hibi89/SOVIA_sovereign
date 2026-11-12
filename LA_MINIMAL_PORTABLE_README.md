# SOVIA LA Minimal 0.15.0-beta — UNSIGNED synthetic-only candidate

This is a **separate** reproducible Python-source ZIP for a public, offline SOVIA audit workflow. It includes the P40 `sovia_la_minimal_projection.py` contract checker. Earlier 0.14/0.13 and frozen 0.12/0.11.2/0.10 versions are not modified.

## Scope
- Requires Python 3.11 or newer already on the local host. No install, network access, external AI/API, private LA source, SQLite customer DB, personal files, model weights or secrets.
- Verify the archive against its detached SHA256 and trusted source. A checksum is **not a digital signature**.
- Extract into a **NEW** directory. Run `RUN_LA_MINIMAL.cmd --ci` for a fabricated local two-file P40 demo. It verifies the extracted package, produces a synthetic owner review and an **invented** LA-like projection and demonstrates independent consistency checks. Re-running refuses to overwrite the previous report. This demo does NOT execute genuine Lightning Azent.
- After an approved PRIVATE first-party LA test has separately produced a minimal **synthetic** projection, verify it offline using:
```
python -I -B sovia_la_minimal_projection.py --projection synthetic-projection.json --review-dir synthetic-sovia-review --synthetic-only
```
The plan fingerprint in the projection must refer to a synthetic SOVIA review for that test. Even equality **does not establish** LA↔SOVIA plan identity, provenance, a real authenticated human decision or full event coverage. P40 always returns NOT_AUTHENTICATED and does not run tools.
- This candidate is for engineering review only. Physical customer Windows10/11 / Defender / SmartScreen, authorized genuine LA source, human consent, privacy, commercial legal and licensing, customer support/pilot and seller GO are **NOT TESTED**; RELEASE HOLD.
