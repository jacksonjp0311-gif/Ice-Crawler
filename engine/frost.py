import subprocess, datetime, json, sys

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()

def _run(cmd):
    creationflags = 0
    startupinfo = None
    if sys.platform.startswith("win"):
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
        startupinfo=startupinfo,
    )
    return p.returncode, p.stdout

def frost_telemetry(repo_url: str):
    # TELEMETRY-ONLY: resolve HEAD hash (NO CLONE HERE)
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
