import datetime
import subprocess
import sys


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()


def _silent_subprocess_kwargs() -> dict:
    if not sys.platform.startswith("win"):
        return {}
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return {"creationflags": creationflags, "startupinfo": startupinfo}


def _run(cmd):
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **_silent_subprocess_kwargs(),
    )
    return p.returncode, p.stdout


def frost_telemetry(repo_url: str):
    # TELEMETRY-ONLY: resolve HEAD hash (NO CLONE HERE)
    rc, out = _run(["git", "ls-remote", repo_url, "HEAD"])
    head = "unknown"
    if rc == 0 and out.strip():
        head = out.strip().split()[0]
    return {
        "ts": utc_now(),
        "repo": repo_url,
        "head": head,
        "mode": "telemetry_only",
        "clone_permitted": False,
    }
