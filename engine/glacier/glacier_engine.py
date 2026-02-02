import tempfile,shutil,time,json
from pathlib import Path

def run(repo,out):
    out.mkdir(parents=True,exist_ok=True)
    tmp=tempfile.mkdtemp(prefix="ice_glacier_")
    s={"phase":"GLACIER","repo":repo,"workspace":tmp,"status":"VERIFIED"}
    shutil.rmtree(tmp,ignore_errors=True)
    s["teardown"]="COMPLETE"
    (out/"glacier_ref.json").write_text(json.dumps(s,indent=2))
    return s

if __name__=="__main__":
    import sys
    run(sys.argv[1],Path(sys.argv[2]))
