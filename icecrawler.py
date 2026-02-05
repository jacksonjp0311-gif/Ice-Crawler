#!/usr/bin/env python3
"""Canonical ICE-CRAWLER entrypoint.

Usage:
  python icecrawler.py
  python icecrawler.py --orchestrator <repo> <run_dir> <max_files> <max_kb> <temp_dir>
"""
import os
import platform
import subprocess
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
UI = os.path.join(ROOT, "ui", "ice_ui.py")
EXE_CANDIDATES = [
    os.path.join(ROOT, "IceCrawler.exe"),
    os.path.join(ROOT, "IceCrawler", "IceCrawler.exe"),
    os.path.join(ROOT, "dist", "IceCrawler", "IceCrawler.exe"),
]


def _run_python(args):
    return subprocess.call([sys.executable, UI, *args], cwd=ROOT)


def _run_exe(args):
    for exe in EXE_CANDIDATES:
        if os.path.exists(exe):
            try:
                return subprocess.call([exe, *args], cwd=ROOT)
            except OSError:
                continue
    return None


def main() -> int:
    args = sys.argv[1:]

    # Keep orchestrator path deterministic and interpreter-safe.
    if args and args[0] == "--orchestrator":
        return _run_python(args)

    # Python users should always be able to run this reliably.
    if platform.system() != "Windows" or os.environ.get("ICE_CRAWLER_FORCE_PYTHON") == "1":
        return _run_python(args)

    # On Windows, attempt EXE first, then auto-fallback to Python if EXE is missing/broken.
    rc = _run_exe(args)
    if rc is None or rc != 0:
        return _run_python(args)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
