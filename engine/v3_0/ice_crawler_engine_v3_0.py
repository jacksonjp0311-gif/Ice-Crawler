import os, sys, json, hashlib, shutil, subprocess, datetime, time, stat

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd,cwd=None):
    p=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
    return p.returncode,p.stdout

def ensure_dir(p):
    os.makedirs(p,exist_ok=True)

def _on_rm_error(func,path,exc):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def purge_dir(path,tries=12):
    for k in range(tries):
        try:
            shutil.rmtree(path,onerror=_on_rm_error)
        except Exception:
            pass
        time.sleep(0.25*(k+1))
        if not os.path.exists(path):
            return True
    return not os.path.exists(path)

def main():
    if len(sys.argv) < 6:
        raise RuntimeError("Usage: repo state temp max_files max_kb")

    repo, state, temp = sys.argv[1], sys.argv[2], sys.argv[3]
    max_files, max_kb = int(sys.argv[4]), float(sys.argv[5])

    ensure_dir(state)

    # FROST SUMMARY (local run fossil)
    with open(os.path.join(state,"frost_summary.json"),"w",encoding="utf-8") as f:
        json.dump({"ts":utc_now(),"repo":repo,"max_files":max_files,"max_kb":max_kb}, f, indent=2)

    # PURGE TEMP IF EXISTS (pre-clean)
    if os.path.exists(temp):
        purge_dir(temp)

    rc,out = run(["git","clone","--depth=1",repo,temp])
    if rc != 0:
        raise RuntimeError("git clone failed:\n" + out)

    bundle = os.path.join(state,"artifact")
    ensure_dir(bundle)

    rc, files = run(["git","-C",temp,"ls-files"])
    if rc != 0:
        raise RuntimeError("git ls-files failed:\n" + files)

    picked=[]
    for line in files.splitlines():
        if len(picked) >= max_files:
            break
        ll=line.lower().strip()
        if not ll:
            continue
        if ll.endswith((".py",".ps1",".c",".h",".md",".txt",".json",".yml",".yaml")):
            picked.append(line.strip())

    manifest=[]
    for rel in picked:
        src=os.path.join(temp,rel)
        if not os.path.exists(src):
            continue
        if os.path.getsize(src)/1024.0 > max_kb:
            continue

        flat = rel.replace("/","_").replace("\\","_")
        dst  = os.path.join(bundle,flat)
        shutil.copy2(src,dst)

        manifest.append({
            "path": rel,
            "flat": flat,
            "bytes": os.path.getsize(dst),
            "sha256": sha256_file(dst)
        })

    with open(os.path.join(state,"artifact_manifest.json"),"w",encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    with open(os.path.join(state,"crystal_index.json"),"w",encoding="utf-8") as f:
        json.dump({
            "ts": utc_now(),
            "count": len(manifest),
            "repo": repo
        }, f, indent=2)

    # UI CONTRACT (SINGULAR, NO DUPLICATE KEYS — CANON LOCK)
    with open(os.path.join(state,"ui_contract.json"),"w",encoding="utf-8") as f:
        json.dump({
            "ui_reads_only": [
                "artifact_manifest.json",
                "crystal_index.json",
                "ui_contract.json"
            ],
            "engine_authoritative": True,
            "ui_never_runs_git": True
        }, f, indent=2)

    # RESIDUE PURGE (post)
    ok = purge_dir(temp)
    if not ok:
        raise RuntimeError("Residue violation: temp still exists")

    with open(os.path.join(state,"residue_truth.json"),"w",encoding="utf-8") as f:
        json.dump({"ts":utc_now(),"rho_post":"empty"}, f, indent=2)

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
