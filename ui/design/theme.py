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
# IDE CHROME CONSTANTS
# ─────────────────────────────────────────────
SIDEBAR_BG  = "#050b14"
FOOTER_BG   = "#040810"
TERMINAL_BG = "#050b14"
SASH_COLOR  = "#0a1929"
TAB_BG      = "#0b1a2e"
TAB_FG      = "#6fb9c9"
TAB_ACTIVE_BG = "#071427"
TAB_ACTIVE_FG = "#4fe3ff"
NOTEBOOK_BG = "#050b14"
SEPARATOR    = "#0d3a5a"

# ─────────────────────────────────────────────
# ASSET ROOT (SKIN ONLY)
# ─────────────────────────────────────────────
HERE = os.path.dirname(__file__)
ASSET_ROOT = os.path.abspath(os.path.join(HERE,"..","assets"))
