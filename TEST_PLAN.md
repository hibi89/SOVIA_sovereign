# SOVIA CROSS-PLATFORM CI UPDATE — 2026-10-26 KST

Code commit d204b76fdb545b32696a3d8aa97c35c1ffbb1355 updated CLI input/output alias comparison using resolved target paths. First Windows run 40213209092 failed one assertion because existing input preservation produced the wrong error string on Windows; no source input was overwritten. GitHub Actions rerun https://github.com/hibi89/SOVIA_sovereign/actions/runs/40213287272 **completed SUCCESS in all four jobs**: Ubuntu Python 3.11/3.13, Windows Python 3.11/3.13. Each: 92 tests discovered; 82 passed, 10 skipped (optional PDF dependency absent), 0 failed; compile step also PASS. Confirmed in CI run result/job endpoint. GitHub-hosted Windows is not the owner's laptop, and Korean PDF/Office, real sanitized data, installer/recovery and production remain UNVERIFIED.

---

# SOVIA TEST PLAN — current CSV source milestone, 2026-10-26 KST

Current CI source SHA: 5c99ca3ca1205a26b586a057874172f6607d3e19. [GitHub Actions run 40212874275](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40212874275): Python 3.11 and Python 3.13 both completed SUCCESS, each `python -m compileall -q sovia_audit.py sovia_csv_input.py sovia_pdf.py tests` PASS and `python -m unittest discover -s tests -v`: **Ran 92 tests, OK (skipped=10)**, i.e. 82 executed PASS and 0 FAIL each. 10 skips are optional ReportLab/Korean PDF paths, not verified in this CI run. Newly added 25 tests (17 parser + 8 CLI) cover CSV schema/permissions/overlong input/header injection/malformed quoting, report equivalence with JSON, isolated Python run, error no-write, policy overwrite and no network. Independent local parser subset was 17 PASS/0 FAIL. No Windows, Excel or real customer-data tests conducted. No production URL.

---

## Earlier verified milestones (historical)

# SOVIA test plan — P2 CSV export checkpoint
Updated 2026-10-26 KST. Source/tests verified commit 6b3be7a4512049caa5a329776e2a63462cd6c8fa.

## Actually executed
| Command / probe | Result | Interpretation |
|---|---|---|
| python -m unittest discover -s tests -v | 66 PASS / 0 FAIL | 40 P1 + 14 CSV + 12 optional-PDF checks |
| python -m compileall -q sovia_audit.py tests | PASS | Python syntax |
| python sovia_audit.py --input examples/demo_five_rules.json --output output/report.html --json-output output/report.json --findings-csv output/findings.csv --events-csv output/events.csv | PASS exit 0 | Fake 3 events, 5 findings, findings.csv 5 rows, events.csv 3 rows, all 4 files nonempty |
| Temporary clean folder, python -I -B and four flags | PASS exit 0 | Same-machine isolated execution, not second Windows machine |
| Local Git blob SHA check | PASS | Source eb886ab5d9a24663f3414cecf74c5dcd9d48f205; tests/test_csv.py 29858eca381a9e161554bc02cd78776278d7034f match remote |

14 CSV-specific tests: fixed finding/event headers and counts, timezone stable ordering, BOM+Korean+CRLF, formula-like strings starting = + - @ (including Unicode prefix characters), dangerous values in both outputs, comma/quote handling, raw_prompt exclusion, empty-safe findings header, bad export kind, 4-output CLI, existing CSV preservation, duplicate-output rejection, simulated failure of fourth staged publish rolling back all prior files, optional CSV disabled by default.

## Unverified / commercial gates
Excel/Google Sheets actual UI and import variations not tested; spreadsheet formula escaping is defense-in-depth not a certified complete barrier. CSV ingestion unsupported. NTFS/external drives and hardlink compatibility not tested; fail safely. Simulated rollback only, no power-loss guarantee, group of four files not atomic for observers. Real source log provenance, PII scanning, backups, deletion, false positives, clean Windows install and operational end-to-end must pass before sale. Cloud/Private tenant/offline checks not applicable until those modes exist.

## PDF milestone observed (2026-10-26 KST)
- Code commit e2ffa99485b57d1e07d6b1ac119226fb86b045ed. Python 3.13.5, optional ReportLab 4.4.9 installed in developer environment.
- `python -m unittest discover -s tests -q` = 67 passed / 0 failed, PDF tests cover optional default-CLI, invalid font/no partial outputs, file collision, byte-stream integrity, Korean font discovery, deterministic output, no-clobber, rollback on hardlink failure, safe no-findings case, raw prompt omission, five output formats. PDF-specific tests are SKIPPED on machines without ReportLab; do not claim PDF verified there.
- Synthetic 3-event/5-finding PDF generated, rendered to 1 landscape A4 PNG, visually inspected no clipping; PyMuPDF extracted Korean headings and five rule IDs.
- Synthetic 115-event PDF generated 6 pages; repeated column headers observed; text page coordinates within page bounds.
- Not verified: fresh Windows device, Malgun Gothic registration, Office PDF viewing, unsupported filesystem, PDF/A, power-loss recovery, authentic customer log source and complete PII redaction. CLI PDF requires optional package and system TTF.

## Isolated-Python PDF hotfix — 2026-10-26 KST
- During extracted ZIP independent smoke, `python -I -B sovia_audit.py ... --pdf-output ...` initially failed because isolated Python excludes the script directory from sys.path. Existing normal-mode PDF and prior 66 tests worked; this exposed an untested packaging path, not a runtime production incident.
- Fixed optional module loading to import ONLY the adjacent `sovia_pdf.py` via `importlib.util.spec_from_file_location`, without network or global sys.path mutation. Added isolated-PDF regression; final developer run `python -m unittest discover -s tests -q`: **67 PASS / 0 FAIL**, syntax PASS, isolated `-I -B` output PASS.
- Verified from extracted ZIP `SOVIA_Audit_Lite_P2_PDF_verified.zip`: 67 tests PASS, HTML+JSON+PDF CLI smoke PASS (3 events / 5 findings). ZIP SHA-256 `2fdc573567edd691a3c19280b24ca4932ea5d0092a6ab327ee1da394375639ff`. No standalone font files in ZIP.
- Final tested code hotfix GitHub SHA `a7a1c6b8e1518887c357aa101c8d254b228c4270`. P2 incomplete: Windows/NTFS and user-side ReportLab/Malgun Gothic, genuine sanctioned input and commercial safety remain UNVERIFIED. Deployment NONE.
