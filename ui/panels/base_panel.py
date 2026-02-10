# ui/panels/base_panel.py — Base class for all IDE panels

import tkinter as tk


class BasePanel(tk.Frame):
    """Thin base for every IDE panel. Sets background and exposes BG."""

    BG = "#050b14"
    PANEL = "#071427"
    BLUE = "#00d5ff"
    BLUE2 = "#4fe3ff"
    ORANGE = "#ff9b1a"
    ORANGE2 = "#ff6a00"
    DIM = "#6fb9c9"
    TEXT_BG = "#061729"

    def __init__(self, master, **kw):
        kw.setdefault("bg", self.BG)
        super().__init__(master, **kw)
