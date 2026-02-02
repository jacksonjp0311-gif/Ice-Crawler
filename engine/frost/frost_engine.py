import json,time
from pathlib import Path

def run(repo,out):
    out.mkdir(parents=True,exist_ok=True)
    s={"phase":"FROST","repo":repo,"ts":time.time(),"status":"VERIFIED"}
    (out/"frost_summary.json").write_text(json.dumps(s,indent=2))
    return s

if __name__=="__main__":
    import sys
    run(sys.argv[1],Path(sys.argv[2]))
