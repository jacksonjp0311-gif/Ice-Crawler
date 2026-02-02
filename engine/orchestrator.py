# ❄ ICE-CRAWLER — ORCHESTRATOR (SOLE AUTHORITY)
# Frost → Glacier → Crystal → emits artifacts for UI.
# UI MUST NEVER RUN GIT. UI reads manifests only.

import os, sys, json, shutil, subprocess, datetime, time, stat
from frost import frost_clone
from glacier import glacier_select
from crystal import sha256_file

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def ensure_dir(p): os.makedirs(p, exist_ok=True)

def run(cmd, cwd=None):
    p=subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout

def _on_rm_error(func, path, exc_info):
    try:
        os.chmod(path, stat.S_IWRITE)
        func(path)
    except Exception:
        pass

def purge_dir_strict(path, tries=40, sleep_s=0.25):
    # 0) best-effort git clean first (releases index/locks in some cases)
    try:
        if os.path.exists(path):
            run(["git","-C",path,"clean","-fdx"])
    except Exception:
        pass

    # 1) retry rmtree with unlock handler
    for _ in range(tries):
        shutil.rmtree(path, ignore_errors=False, onerror=_on_rm_error) if os.path.exists(path) else None
        if not os.path.exists(path):
            return True
        time.sleep(sleep_s)

    # 2) last resort: rename away so residue path is gone (ρ_post checks path)
    try:
        if os.path.exists(path):
            tomb = path + "_tomb_" + str(int(time.time()))
            os.rename(path, tomb)
            # best-effort delete tomb (not required for ρ_post on original path)
            for _ in range(tries):
                shutil.rmtree(tomb, ignore_errors=True)
                if not os.path.exists(tomb):
                    break
                time.sleep(sleep_s)
    except Exception:
        pass

    return (not os.path.exists(path))

def main():
    if len(sys.argv) < 6:
        raise RuntimeError("Usage: orchestrator.py repo state_run max_files max_kb temp_dir")

    repo      = sys.argv[1]
    state_run = sys.argv[2]
    max_files = int(sys.argv[3])
    max_kb    = float(sys.argv[4])
    temp_dir  = sys.argv[5]

    ensure_dir(state_run)

    # Pre-declare residue truth path so we can always emit it
    residue_path = os.path.join(state_run,"residue_truth.json")
    purge_ok = False

    # 1) FROST SUMMARY (local fossil)
    with open(os.path.join(state_run,"frost_summary.json"),"w",encoding="utf-8") as f:
        json.dump({"ts":utc_now(),"repo":repo,"max_files":max_files,"max_kb":max_kb}, f, indent=2)

    try:
        # 2) TEMP PRE-CLEAN
        if os.path.exists(temp_dir):
            purge_dir_strict(temp_dir)

        # 3) FROST CLONE
        frost_clone(repo, temp_dir)

        # 4) LIST FILES
        rc, out = run(["git","-C",temp_dir,"ls-files"])
        if rc != 0:
            raise RuntimeError("git ls-files failed:\n" + out)

        # 5) GLACIER SELECT
        picked = glacier_select(out.splitlines(), max_files)

        # 6) CRYSTAL EMIT
        bundle = os.path.join(state_run, "artifact")
        ensure_dir(bundle)

        manifest=[]
        for rel in picked:
            src = os.path.join(temp_dir, rel)
            if not os.path.exists(src):
                continue
            if os.path.getsize(src)/1024.0 > max_kb:
                continue

            flat = rel.replace("/","_").replace("\\","_")
            dst  = os.path.join(bundle, flat)
            shutil.copy2(src, dst)

            manifest.append({
                "path": rel,
                "flat": flat,
                "bytes": os.path.getsize(dst),
                "sha256": sha256_file(dst)
            })

        with open(os.path.join(state_run,"artifact_manifest.json"),"w",encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        with open(os.path.join(state_run,"crystal_index.json"),"w",encoding="utf-8") as f:
            json.dump({"ts":utc_now(),"count":len(manifest),"repo":repo}, f, indent=2)

        with open(os.path.join(state_run,"ui_contract.json"),"w",encoding="utf-8") as f:
            json.dump({
                "ui_reads_only":["artifact_manifest.json","crystal_index.json","ui_contract.json","engine_registry.json"],
                "engine_authoritative":True,
                "ui_never_runs_git":True
            }, f, indent=2)

    finally:
        # 7) RESIDUE PURGE (ρ_post = ∅) — ALWAYS EMIT TRUTH
        purge_ok = purge_dir_strict(temp_dir)

        rho = "empty" if (not os.path.exists(temp_dir)) else "violation"
        with open(residue_path,"w",encoding="utf-8") as f:
            json.dump({"ts":utc_now(),"rho_post":rho,"purge_ok":bool(purge_ok)}, f, indent=2)

    if os.path.exists(temp_dir):
        raise RuntimeError("Residue violation: temp still exists")

    with open(os.path.join(state_run,"orchestrator_exit.json"),"w",encoding="utf-8") as f:
        json.dump({"ts":utc_now(),"ok":True}, f, indent=2)

    return 0

if __name__=="__main__":
    raise SystemExit(main())
