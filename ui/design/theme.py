# ui/design/theme.py
# ❄ ICE-CRAWLER — PHOTO-LOCK THEME CONSTANTS
# Skin-only layer. No truth logic.

import os

BG      = "#05080d"
PANEL   = "#0b141c"

CYAN    = "#6fe7ff"
CYAN2   = "#3bbcd6"

TEXT    = "#d8fbff"

FONT_UI = ("Segoe UI", 18)
FONT_BTN= ("Segoe UI", 20, "bold")
FONT_LOGO=("Segoe UI", 60, "bold")
FONT_BOX=("Consolas", 16)

# ─────────────────────────────────────────────
# ASSET ROOT (SKIN ONLY)
# ─────────────────────────────────────────────
HERE = os.path.dirname(__file__)
ASSET_ROOT = os.path.abspath(os.path.join(HERE,"..","assets"))
