#!/usr/bin/env python3
"""Cross-platform root launcher for ICE-CRAWLER UI."""
import os
import platform
import subprocess
import sys

ROOT = os.path.abspath(os.path.dirname(__file__))
EXE = os.path.join(ROOT, "IceCrawler.exe")
UI = os.path.join(ROOT, "ui", "ice_ui.py")


def main() -> int:
    if platform.system() == "Windows" and os.path.exists(EXE):
        return subprocess.call([EXE], cwd=ROOT)
    return subprocess.call([sys.executable, UI], cwd=ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
