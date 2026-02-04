# ui/design/asset_loader.py
# ❄ ICE-CRAWLER v5.0D — ASSET ROOT TRUTH (MEIPASS-AWARE + SIGNATURE COMPAT)

import os, sys

def is_frozen():
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")

def _dev_assets_root() -> str:
    # ui/design/asset_loader.py -> ui/assets
    here = os.path.dirname(__file__)            # .../ui/design
    return os.path.abspath(os.path.join(here, "..", "assets"))

def asset_root(repo_root: str | None = None) -> str:
    """
    Frozen: sys._MEIPASS/assets (PyInstaller add-data "ui\\assets;assets")
    Dev:
      - if repo_root provided: <repo_root>/ui/assets
      - else: infer from this file: <...>/ui/assets
    """
    if is_frozen():
        return os.path.join(sys._MEIPASS, "assets")

    if repo_root:
        return os.path.join(repo_root, "ui", "assets")

    return _dev_assets_root()

def asset_path(*args) -> str:
    """
    COMPAT EXPORT (required by design.layout)
      • asset_path("snowflake.png")                 -> ok
      • asset_path(repo_root, "snowflake.png")      -> ok
    """
    if len(args) == 1:
        name = args[0]
        return os.path.join(asset_root(None), name)

    if len(args) == 2:
        repo_root, name = args
        return os.path.join(asset_root(repo_root), name)

    raise TypeError("asset_path() expects (name) or (repo_root, name)")

def exists(*args) -> bool:
    return os.path.exists(asset_path(*args))
