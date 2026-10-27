# SOVIA P2 v0.11.1-beta — archive extraction and local self-check safety

## Scope and backward compatibility

This is a separate **unsigned developer acceptance candidate**, not a signed installer, public product release, customer compliance certification, actual n8n connection, or production deployment. Earlier [v0.11.0-beta build CI 40484567239](https://github.com/hibi89/SOVIA_sovereign/actions/runs/40484567239) remains a distinct historical ZIP with SHA256 `a15ce8bebcb894c991fcb6e2b4fdc793e6460c31fb5067b97f73acf820cd1d70`. The independent v0.10 historical ZIP remains unchanged SHA256 `68c05795f871bd3698526f8fc34e4e58e60e4ec03f18fbbd0b56524d41f6f2d9`. A new version label v0.11.1-beta avoids silently reusing an existing filename for modified packaged code.

## Fix A: archive changed between verify and extract

In `verify_portable_p2.extract_verified`, the old path verified an on-disk ZIP, then opened the archive path a second time during extraction. A local replacement in between could cause extraction of a different ZIP. Now the extractor reads a bounded snapshot of archive bytes **after** verify and requires its SHA256 to match the exact verified digest. Extraction reads only this pinned `io.BytesIO` snapshot, not a third uncontrolled filesystem read.

Limits: the filesystem must be locally trusted enough to run a Python verifier. This is not a digital signature, anti-malware certification, prevention of a forged ZIP+SHA256 pair, or power-loss atomic install.

## Fix B: owner synthetic result contamination

In `owner_p2_selfcheck.check`, the old flow created a result folder before verifying the installed allowlisted files. Supplying `--output-dir` inside the pristine install would make that install fail later verification. Now the script first checks Python version and validates the extracted 18-file package, **before writing any diagnostics**, and refuses output paths resolving inside the verified installation directory. Existing valid result folders *outside* the installation continue to work. If package integrity fails, the CLI rejects without creating output results.

Limits: executing the verifier itself requires trusted source provenance, and third-party changes after verification are still a local race. Actual Windows Defender/SmartScreen, browser visual checks and Korean PDF rendering remain manual and explicitly NOT_CHECKED.

## Test & CI gates

```sh
python -m unittest discover -s tests -v
python portable_smoke.py
python portable_smoke_p2.py
python -I -B build_portable_p2.py --output dist/SOVIA-Audit-Lite-0.11.1-beta.zip
```

Four new synthetic regression cases check post-verification ZIP byte replacement, tampered installed bundle with zero results, rejected in-install result folder, and safe out-of-install results. CI builds and verifies a **separate v0.11.1-beta artifact** and keeps old v0.10 verification unchanged. Existing v0.11.0-beta CI build remains accessible through its original run while GitHub retention permits.

No real customer data, n8n API, network credentials, production services or payments used. Do not infer real-world approval from GitHub-hosted Windows test success.
