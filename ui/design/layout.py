# ui/design/layout.py
# ❄ ICE-CRAWLER — PHOTO-LOCK UI SURFACE v4.5
#
# Adds:
#  • Snowflake icon injection
#  • Glow overlay behind progress bar
#  • Fossil event viewer panel
#  • Open Artifact button
#  • Ladder pulse animation hook

import os
import tkinter as tk
from tkinter import ttk
from .theme import *
from .asset_loader import asset_path, exists

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

    # ───────── LOGO PANEL ─────────
    logo = ttk.Frame(mid)
    logo.pack(side="left", expand=True)

    # Optional snowflake icon
    app.snow_img = None
    snow_path = asset_path("snowflake.png")

    if os.path.exists(snow_path):
        try:
            app.snow_img = tk.PhotoImage(file=snow_path)
            tk.Label(
                logo,
                image=app.snow_img,
                bg=BG
            ).pack(pady=(10,10))
        except:
            pass

    ttk.Label(
        logo,
        text="ICE\nCRAWLER",
        font=FONT_LOGO,
        foreground=CYAN,
        justify="center"
    ).pack(pady=20)

    # ───────── PROGRESS BAR + GLOW ─────────
    prog_frame = ttk.Frame(app)
    prog_frame.pack(fill="x", padx=70, pady=12)

    glow_path = asset_path("glow.png")
    app.glow_img = None

    if os.path.exists(glow_path):
        try:
            app.glow_img = tk.PhotoImage(file=glow_path)
            tk.Label(
                prog_frame,
                image=app.glow_img,
                bg=BG
            ).pack()
        except:
            pass

    app.progress = ttk.Progressbar(
        prog_frame,
        style="Ice.Horizontal.TProgressbar",
        maximum=100
    )
    app.progress.pack(fill="x")

    # ───────── OUTPUT PANEL ─────────
    bottom = ttk.Frame(app, padding=18)
    bottom.pack(fill="x")

    ttk.Label(
        bottom,
        text="Artifact Path (Local Fossil Output):",
        font=("Segoe UI", 18)
    ).pack(anchor="w", pady=(0,8))

    app.output_box = tk.Text(
        bottom,
        height=2,
        font=FONT_BOX,
        bg="#0d1117",
        fg=CYAN,
        relief="flat"
    )
    app.output_box.pack(fill="x")

    # ───────── OPEN ARTIFACT BUTTON ─────────
    app.open_btn = ttk.Button(
        bottom,
        text="Open Artifact Folder",
        command=app.open_artifact
    )
    app.open_btn.pack(fill="x", pady=(12,12))

    # ───────── EVENT VIEWER PANEL ─────────
    ttk.Label(
        bottom,
        text="Event Fossil Viewer:",
        font=("Segoe UI", 16)
    ).pack(anchor="w")

    app.event_view = tk.Text(
        bottom,
        height=8,
        font=("Consolas", 12),
        bg="#05080d",
        fg=TEXT,
        relief="flat"
    )
    app.event_view.pack(fill="both", expand=True)
