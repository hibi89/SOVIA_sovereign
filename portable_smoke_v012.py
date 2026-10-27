"""v0.12 isolated package end-to-end fabricated-data acceptance. Not a release."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from build_portable_v012 import DEFAULT_NAME, build
from verify_portable_v012 import extract_verified, verify_directory

def call(script, *args):
    proc=subprocess.run([sys.executable,"-I","-B",str(script),
                         *[str(a) for a in args]],capture_output=True,
                        text=True,timeout=35)
    if proc.returncode:
        raise RuntimeError("isolated V012 smoke subprocess failed")
    return json.loads(proc.stdout)

def smoke():
    with tempfile.TemporaryDirectory(prefix="sovia-v012-extracted-") as tmp:
        root=Path(tmp)
        artifact=root/DEFAULT_NAME
        result=build(artifact)
        extracted=root/"fresh-install"
        extract_verified(artifact,extracted,artifact.with_name(artifact.name+".sha256"))
        verify_directory(extracted)
        engine=extracted/"sovia_audit_v012.py"
        sample=extracted/"examples"/"demo_temporal_boundary.json"
        golden=extracted/"examples"/"demo_five_rules.json"
        boundary=call(engine,"--input",sample,"--html-output",root/"boundary.html",
                      "--json-output",root/"boundary.json","--synthetic-only")
        if (boundary["events"],boundary["findings"])!=(3,0):
            raise RuntimeError("incorrect synthetic boundary oracle")
        page=(root/"boundary.html").read_text(encoding="utf-8")
        if page.index("2026-10-25T15:01:00Z") >= page.index("2026-10-25T15:01:00.500000Z"):
            raise RuntimeError("v0.12 packaged HTML chronology incorrect")
        five=call(engine,"--input",golden,"--html-output",root/"gold.html",
                  "--json-output",root/"gold.json","--synthetic-only")
        if (five["events"],five["findings"])!=(3,5):
            raise RuntimeError("incorrect synthetic five-rule oracle")
        history=extracted/"sovia_history_v012.py"
        db=root/"ledger-v2.sqlite3"
        first=call(history,"import","--db",db,"--input",sample,"--synthetic-only")
        again=call(history,"import","--db",db,"--input",sample,"--synthetic-only")
        if first["status"]!="imported" or again["status"]!="already_present":
            raise RuntimeError("versioned history import/dedup failure")
        before=call(history,"status","--db",db)
        if (before["schema_version"],before["reports"],before["finding_count_total"])!=(2,1,0):
            raise RuntimeError("versioned history schema/count mismatch")
        snap=root/"snapshot.sqlite3"
        clone=root/"restore.sqlite3"
        call(history,"backup","--db",db,"--output",snap)
        call(history,"restore","--input",snap,"--db",clone)
        if call(history,"status","--db",clone)!=before:
            raise RuntimeError("versioned history recovery mismatch")
        verify_directory(extracted)
        return {"status":"v012_portable_clean_install_pass",
                "version":"0.12.0-beta","files":result["files"],
                "zip_sha256":result["sha256"],"boundary_events":3,
                "boundary_findings":0,"five_rule_findings":5,
                "history_schema_version":2,"history_backup_restored":True,
                "legacy_history_migrated":False,"owner_manual_acceptance":False,
                "commercial_release_approved":False}

if __name__=="__main__":
    print(json.dumps(smoke(),sort_keys=True))
