# ui/design/asset_loader.py
# ❄ ICE-CRAWLER — ASSET ROOT TRUTH (MEIPASS-AWARE)

import os, sys

def is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def asset_root(repo_root: str) -> str:
    """
    Returns absolute path to assets root.
    - Frozen: assets extracted under sys._MEIPASS/assets (PyInstaller add-data)
    - Dev:    repo_root/ui/assets
    """
    if is_frozen():
        return os.path.join(sys._MEIPASS, "assets")
    return os.path.join(repo_root, "ui", "assets")

def resolve(repo_root: str, *parts: str) -> str:
    return os.path.join(asset_root(repo_root), *parts)
