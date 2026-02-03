# ui/design/layout.py
# ❄ ICE-CRAWLER — PHOTO-LOCK LAYOUT BUILDERS
# Builds the reference UI panels. No fossil logic.

import tkinter as tk
from tkinter import ttk
from .theme import *

def apply_style(style: ttk.Style):

    style.theme_use("clam")

    style.configure("TFrame", background=BG)

    style.configure("TLabel",
        background=BG,
        foreground=TEXT,
        font=FONT_UI
    )

    style.configure("TButton",
        font=FONT_BTN,
        padding=16,
        background=PANEL,
        foreground=CYAN
    )

    style.configure("Ice.Horizontal.TProgressbar",
        troughcolor="#111820",
        background=CYAN2,
        thickness=28
    )


def build_surface(app, phases):

    # ───────── TOP INPUT PANEL ─────────
    top = ttk.Frame(app, padding=22)
    top.pack(fill="x")

    app.url_entry = ttk.Entry(top, font=("Segoe UI", 20))
    app.url_entry.pack(fill="x", pady=(0,18))
    app.url_entry.insert(0,"Enter URL or GitHub URL")

    app.submit_btn = ttk.Button(
        top,
        text="Submit to Ice-Crawler",
        command=app.on_submit
    )
    app.submit_btn.pack(fill="x")

    # ───────── CENTER BODY ─────────
    mid = ttk.Frame(app, padding=30)
    mid.pack(fill="both", expand=True)

    ladder = ttk.Frame(mid)
    ladder.pack(side="left", padx=35)

    app.phase_labels={}
    for phase in phases:
        lbl = ttk.Label(ladder,text=f"⬤ {phase}",font=("Segoe UI", 24))
        lbl.pack(anchor="w", pady=20)
        app.phase_labels[phase]=lbl

    logo = ttk.Frame(mid)
    logo.pack(side="left", expand=True)

    ttk.Label(
        logo,
        text="ICE\nCRAWLER ❄",
        font=FONT_LOGO,
        foreground=CYAN,
        justify="center"
    ).pack(pady=60)

    # ───────── PROGRESS BAR ─────────
    app.progress = ttk.Progressbar(
        app,
        style="Ice.Horizontal.TProgressbar",
        maximum=100
    )
    app.progress.pack(fill="x", padx=70, pady=20)

    # ───────── OUTPUT PANEL ─────────
    bottom = ttk.Frame(app, padding=24)
    bottom.pack(fill="x")

    ttk.Label(
        bottom,
        text="Copy paste this link to the artifact on your local device:",
        font=("Segoe UI", 20)
    ).pack(anchor="w", pady=(0,14))

    app.output_box = tk.Text(
        bottom,
        height=2,
        font=FONT_BOX,
        bg="#0d1117",
        fg=CYAN,
        relief="flat"
    )
    app.output_box.pack(fill="x")
