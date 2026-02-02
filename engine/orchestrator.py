import os, sys, json, shutil, subprocess, datetime, time, stat
from frost import frost_telemetry, glacier_clone
from glacier import glacier_select, glacier_emit
from crystal import sha256_file, crystal_seal

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
    try:
        if os.path.exists(path):
            run(["git","-C",path,"clean","-fdx"])
    except Exception:
        pass
    for _ in range(tries):
        if os.path.exists(path):
            try:
                shutil.rmtree(path, ignore_errors=False, onerror=_on_rm_error)
            except Exception:
                pass
        if not os.path.exists(path):
            return True
        time.sleep(sleep_s)
    return (not os.path.exists(path))

def emit_ui(state_run: str, event: str):
    p = os.path.join(state_run,"ui_events.jsonl")
    with open(p,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts":utc_now(),"event":event})+"\n")

def main():
    repo      = sys.argv[1]
    state_run = sys.argv[2]
    max_files = int(sys.argv[3])
    max_kb    = float(sys.argv[4])
    temp_dir  = sys.argv[5]

    ensure_dir(state_run)
    residue_path = os.path.join(state_run,"residue_truth.json")

    # Frost: telemetry-only
    frost = frost_telemetry(repo)
    with open(os.path.join(state_run,"frost_summary.json"),"w",encoding="utf-8") as f:
        json.dump(frost, f, indent=2)
    emit_ui(state_run, "FROST_VERIFIED")

    try:
        if os.path.exists(temp_dir):
            purge_dir_strict(temp_dir)

        # Glacier: ephemeral clone
        emit_ui(state_run, "GLACIER_PENDING")
        glacier_clone(repo, temp_dir)

        rc, out = run(["git","-C",temp_dir,"ls-files"])
        picked = glacier_select(out.splitlines(), max_files)
        glacier_emit(state_run, picked, frost.get("head","unknown"))
        emit_ui(state_run, "GLACIER_VERIFIED")

        # Crystal: deterministic bundle
        emit_ui(state_run, "CRYSTAL_PENDING")
        bundle = os.path.join(state_run, "artifact")
        ensure_dir(bundle)

        manifest=[]
        for rel in picked:
            src=os.path.join(temp_dir, rel)
            if not os.path.exists(src): continue
            if os.path.getsize(src)/1024.0 > max_kb: continue

            flat=rel.replace("/","_")
            dst=os.path.join(bundle, flat)
            shutil.copy2(src,dst)

            manifest.append({"path":rel,"sha256":sha256_file(dst)})

        # stable order
        manifest = sorted(manifest, key=lambda x: x["path"])

        with open(os.path.join(state_run,"artifact_manifest.json"),"w",encoding="utf-8") as f:
            json.dump(manifest,f,indent=2)

        with open(os.path.join(state_run,"crystal_index.json"),"w",encoding="utf-8") as f:
            json.dump({"ts":utc_now(),"count":len(manifest)},f,indent=2)

        crystal_seal(state_run, manifest)

        with open(os.path.join(state_run,"ui_contract.json"),"w",encoding="utf-8") as f:
            json.dump({"ui_reads_only":["artifact_manifest.json","artifact_hashes.json","crystal_index.json","engine_registry.json","ui_events.jsonl"],
                       "ui_never_runs_git":True},f,indent=2)

        emit_ui(state_run, "CRYSTAL_VERIFIED")

    finally:
        purge_ok = purge_dir_strict(temp_dir)
        rho = "empty" if (not os.path.exists(temp_dir)) else "violation"
        with open(residue_path,"w",encoding="utf-8") as f:
            json.dump({"ts":utc_now(),"rho_post":rho,"purge_ok":purge_ok}, f, indent=2)

    if os.path.exists(temp_dir):
        raise RuntimeError("Residue violation")

    emit_ui(state_run, "RESIDUE_EMPTY_LOCK")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
