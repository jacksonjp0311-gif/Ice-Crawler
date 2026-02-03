# ui/design/asset_loader.py
# ❄ ICE-CRAWLER — CANON ASSET LOADER
# Pure skin resolution. No truth logic.

import os
from .theme import ASSET_ROOT

def asset_path(name: str) -> str:
    return os.path.join(ASSET_ROOT, name)

def exists(name: str) -> bool:
    return os.path.exists(asset_path(name))
