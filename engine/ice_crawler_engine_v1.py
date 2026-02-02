import os, sys, json, hashlib, shutil, subprocess, datetime

def utc_now():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat()+"Z"

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()

def run(cmd, cwd=None):
    p = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout

def ensure_dir(p):
    os.makedirs(p, exist_ok=True)

def main():
    # argv: target_repo, state_run_dir, temp_dir, max_files, max_kb
    if len(sys.argv) < 6:
        print("usage: engine.py <target_repo> <state_run> <temp_dir> <max_files> <max_kb>")
        return 2

    target_repo = sys.argv[1]
    state_run   = sys.argv[2]
    temp_dir    = sys.argv[3]
    max_files   = int(sys.argv[4])
    max_kb      = float(sys.argv[5])

    ensure_dir(state_run)

    # ── FROST (telemetry)
    frost = {
        "ts": utc_now(),
        "repo": target_repo,
        "max_files": max_files,
        "max_kb": max_kb
    }
    with open(os.path.join(state_run, "frost_summary.json"), "w", encoding="utf-8") as f:
        json.dump(frost, f, indent=2)

    # ── GLACIER (ephemeral clone)
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir, ignore_errors=True)

    rc, out = run(["git", "clone", "--depth=1", target_repo, temp_dir])
    with open(os.path.join(state_run, "glacier_log.txt"), "w", encoding="utf-8") as f:
        f.write(out)
    if rc != 0:
        raise RuntimeError("git clone failed")

    # ── CRYSTAL Π (bounded projection)
    bundle = os.path.join(state_run, "artifact")
    ensure_dir(bundle)

    rc, files_out = run(["git", "-C", temp_dir, "ls-files"])
    if rc != 0:
        raise RuntimeError("git ls-files failed")

    allow_ext = (".py",".ps1",".c",".h",".md",".txt",".json",".yml",".yaml")
    picked = []
    for line in files_out.splitlines():
        p = line.strip()
        if not p: 
            continue
        if not p.lower().endswith(allow_ext):
            continue
        picked.append(p)
        if len(picked) >= max_files:
            break

    manifest = []
    for rel in picked:
        src = os.path.join(temp_dir, rel)
        if not os.path.exists(src):
            continue

        size_kb = os.path.getsize(src)/1024.0
        if size_kb > max_kb:
            continue

        flat_name = rel.replace("\\","_").replace("/","_")
        dst = os.path.join(bundle, flat_name)

        ensure_dir(os.path.dirname(dst))
        shutil.copy2(src, dst)

        manifest.append({
            "path": rel,
            "kb": round(size_kb, 2),
            "sha256": sha256_file(dst)
        })

    with open(os.path.join(state_run, "artifact_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    idx = {
        "ts": utc_now(),
        "count": len(manifest),
        "top_files": [m["path"] for m in manifest[:25]]
    }
    with open(os.path.join(state_run, "crystal_index.json"), "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2)

    # ── RESIDUE LOCK (ρ = ∅)
    shutil.rmtree(temp_dir, ignore_errors=True)
    if os.path.exists(temp_dir):
        raise RuntimeError("Residue violation: temp still exists")

    with open(os.path.join(state_run, "residue_truth.json"), "w", encoding="utf-8") as f:
        json.dump({"ts": utc_now(), "rho_post": "empty"}, f, indent=2)

    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as e:
        # Engine failure artifact (engine-local)
        try:
            state_run = sys.argv[2] if len(sys.argv) > 2 else "."
            with open(os.path.join(state_run, "engine_failure.json"), "w", encoding="utf-8") as f:
                json.dump({"ts": utc_now(), "error": str(e)}, f, indent=2)
        except Exception:
            pass
        print("ENGINE_ERROR:", str(e))
        raise
