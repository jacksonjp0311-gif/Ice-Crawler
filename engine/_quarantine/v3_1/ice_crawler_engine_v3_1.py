# ICE-CRAWLER ENGINE v3.1 — AUTHORITATIVE CRYSTAL EMITTER
# UI reads ONLY emitted artifacts. Engine owns truth.

import os, sys, json, hashlib, shutil, subprocess, datetime, time, stat

def utc():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def sha256(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""):
            h.update(c)
    return h.hexdigest()

def run(cmd,cwd=None):
    p=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    return p.returncode,p.stdout

def ensure(d): os.makedirs(d,exist_ok=True)

def purge(path):
    if os.path.exists(path):
        shutil.rmtree(path,ignore_errors=True)
    return not os.path.exists(path)

def main():
    repo,state,temp,max_files,max_kb = sys.argv[1],sys.argv[2],sys.argv[3],int(sys.argv[4]),float(sys.argv[5])
    ensure(state)

    rc,out = run(["git","clone","--depth=1",repo,temp])
    if rc!=0: raise RuntimeError(out)

    bundle=os.path.join(state,"artifact")
    ensure(bundle)

    rc,files = run(["git","-C",temp,"ls-files"])
    picked=[]
    for f in files.splitlines():
        if len(picked)>=max_files: break
        if f.lower().endswith((".py",".ps1",".md",".json",".txt")):
            picked.append(f)

    manifest=[]
    for rel in picked:
        src=os.path.join(temp,rel)
        if os.path.getsize(src)/1024.0>max_kb: continue
        flat=rel.replace("/","_")
        dst=os.path.join(bundle,flat)
        shutil.copy2(src,dst)
        manifest.append({"path":rel,"sha256":sha256(dst)})

    json.dump(manifest,open(os.path.join(state,"artifact_manifest.json"),"w"),indent=2)
    json.dump({"ts":utc(),"count":len(manifest)},open(os.path.join(state,"crystal_index.json"),"w"),indent=2)

    json.dump({
        "engine_authoritative":True,
        "ui_reads_only":["artifact_manifest.json","crystal_index.json"]
    },open(os.path.join(state,"ui_contract.json"),"w"),indent=2)

    if not purge(temp): raise RuntimeError("Residue violation")

if __name__=="__main__":
    main()
