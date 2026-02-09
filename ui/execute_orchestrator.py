# ui/execute_orchestrator.py
# ❄ ICE-CRAWLER — Execution bridge for submit requests

import json
import os
import subprocess
import sys
import time

SUBMIT_REQUEST = "submit_request.json"
INBOX_DIR = "inbox"


def is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def repo_root():
    if is_frozen():
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def ui_dir():
    return os.path.join(repo_root(), "ui")


def latest_run_path_file():
    return os.path.join(ui_dir(), "latest_run_path.txt")


def write_latest_run_path(run_path: str):
    try:
        open(latest_run_path_file(), "w", encoding="utf-8").write(run_path or "")
    except Exception:
        pass


def ensure_runs_dir():
    os.makedirs(os.path.join(repo_root(), "state", "runs"), exist_ok=True)


def new_run_dir():
    ensure_runs_dir()
    run_tag = time.strftime("run_%Y%m%d_%H%M%S")
    p = os.path.join(repo_root(), "state", "runs", run_tag)
    os.makedirs(p, exist_ok=True)
    return p


def request_path_from_args(argv):
    if "--request" in argv:
        idx = argv.index("--request")
        if idx + 1 < len(argv):
            return argv[idx + 1]
    return os.path.join(ui_dir(), INBOX_DIR, SUBMIT_REQUEST)


def read_request(path: str):
    if not os.path.exists(path):
        return None
    try:
        return json.loads(open(path, "r", encoding="utf-8").read())
    except Exception:
        return None


def run_orchestrator(repo_url: str, out_run_dir: str):
    temp_dir = os.path.join(repo_root(), "state", "_temp_repo")
    if is_frozen():
        cmd = [sys.executable, "--orchestrator", repo_url, out_run_dir, "50", "120", temp_dir]
    else:
        cmd = [sys.executable, "-m", "engine.orchestrator", repo_url, out_run_dir, "50", "120", temp_dir]
    creationflags = 0
    startupinfo = None
    if sys.platform.startswith("win"):
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0
    p = subprocess.run(
        cmd,
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
        startupinfo=startupinfo,
    )
    try:
        open(os.path.join(out_run_dir, "ui_stdout.txt"), "w", encoding="utf-8").write(p.stdout or "")
        open(os.path.join(out_run_dir, "ui_rc.txt"), "w", encoding="utf-8").write(str(p.returncode))
    except Exception:
        pass
    return p.returncode


def main(argv=None):
    argv = argv or sys.argv[1:]
    request_path = request_path_from_args(argv)
    request = read_request(request_path)
    if not request:
        print(f"[execute_orchestrator] Missing submit request: {request_path}")
        return 1

    repo_url = request.get("repo_url")
    if not repo_url:
        print("[execute_orchestrator] Missing repo_url in submit request.")
        return 1

    run_dir = request.get("run_dir") or new_run_dir()
    os.makedirs(run_dir, exist_ok=True)
    write_latest_run_path(run_dir)

    print(f"[execute_orchestrator] Running orchestrator for {repo_url}")
    return run_orchestrator(repo_url, run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
