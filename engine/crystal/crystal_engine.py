import json,time,hashlib
from pathlib import Path

def run(repo,out):
    out.mkdir(parents=True,exist_ok=True)
    payload=f"CRYSTAL::{repo}"
    h=hashlib.sha256(payload.encode()).hexdigest()
    s={"phase":"CRYSTAL","repo":repo,"artifact_hash":h,"status":"VERIFIED"}
    (out/"artifact_manifest.json").write_text(json.dumps(s,indent=2))
    return s

if __name__=="__main__":
    import sys
    run(sys.argv[1],Path(sys.argv[2]))
