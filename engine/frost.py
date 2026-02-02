import subprocess, datetime, json

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def _run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout

def frost_telemetry(repo_url: str):
    # Network-only: resolve HEAD hash (no clone here)
    rc, out = _run(["git","ls-remote",repo_url,"HEAD"])
    head = "unknown"
    if rc == 0 and out.strip():
        head = out.strip().split()[0]
    return {
        "ts": utc_now(),
        "repo": repo_url,
        "head": head,
        "mode": "telemetry_only",
        "clone_permitted": False
    }

def glacier_clone(repo_url: str, temp_dir: str):
    # Glacier performs materialization (ephemeral), still shallow
    subprocess.check_call(["git","clone","--depth=1","--single-branch",repo_url,temp_dir])
