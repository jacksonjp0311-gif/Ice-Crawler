# ui/panels/main_content.py — Title, URL input, submit, progress, output residue

import tkinter as tk
from .base_panel import BasePanel
from ui.animations import RitualTriangleButton, StatusIndicator, attach_snowflake

PLACEHOLDER = "Paste a GitHub URL (recommended) or repo URL..."


class MainContent(BasePanel):
    """Central panel: header, URL entry, submit button, progress bar, output residue."""

    def __init__(self, master, root_window, submit_command=None,
                 artifact_command=None, **kw):
        super().__init__(master, **kw)
        self.root_window = root_window
        self.submit_command = submit_command
        self.artifact_command = artifact_command
        self._placeholder_active = True
        self._build()

    def _build(self):
        # --- Header ---
        header = tk.Frame(self, bg=self.BG)
        header.pack(fill="x", padx=16, pady=(12, 4))

        title_row = tk.Frame(header, bg=self.BG)
        title_row.pack(fill="x")

        tk.Label(
            title_row, text="ICE-CRAWLER", fg=self.BLUE2, bg=self.BG,
            font=("Segoe UI", 26, "bold"),
        ).pack(side="left")

        self.snowflake_canvas = attach_snowflake(title_row, self.root_window)
        self.snowflake_canvas.pack(side="left", padx=(8, 0))

        self.status_indicator_label = tk.Label(
            title_row, text="STATUS: IDLE", fg=self.BLUE2, bg=self.BG,
            font=("Consolas", 11, "bold"),
        )
        self.status_indicator_label.pack(side="right")
        self.status_indicator = StatusIndicator(self.status_indicator_label)

        tk.Label(
            header,
            text="Event-Truth Ladder \u2022 Photo-Lock UI \u2022 Fossil Reader",
            fg=self.BLUE, bg=self.BG, font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w")

        # --- URL input row ---
        top = tk.Frame(self, bg=self.BG)
        top.pack(fill="x", padx=16, pady=(6, 8))

        self.url_entry = tk.Entry(
            top, bg=self.PANEL, fg=self.DIM, insertbackground=self.BLUE2,
            relief="flat", font=("Consolas", 13),
        )
        self.url_entry.pack(side="left", fill="x", expand=True, ipady=6)
        self.url_entry.insert(0, PLACEHOLDER)
        self.url_entry.bind("<FocusIn>", self._on_url_focus_in)
        self.url_entry.bind("<FocusOut>", self._on_url_focus_out)

        action_panel = tk.Frame(top, bg=self.BG)
        action_panel.pack(side="left", padx=(12, 0))

        button_row = tk.Frame(action_panel, bg=self.BG)
        button_row.pack(anchor="w")

        self.submit_btn = RitualTriangleButton(
            button_row, command=self.submit_command, w=90, h=74,
        )
        self.submit_btn.pack(side="left")

        self.submit_lbl = tk.Label(
            button_row, text="PRESS TO SUBMIT\nTO ICE CRAWLER",
            fg=self.ORANGE, bg=self.BG, justify="left",
            font=("Segoe UI", 10, "bold"),
        )
        self.submit_lbl.pack(side="left", padx=(6, 0))

        self._submit_line_1 = tk.Frame(action_panel, bg=self.ORANGE, height=1, width=200)
        self._submit_line_1.pack(anchor="w", pady=(4, 0))
        self._submit_line_2 = tk.Frame(action_panel, bg=self.ORANGE, height=1, width=140)
        self._submit_line_2.pack(anchor="w", pady=(2, 0))

        # --- Progress bar ---
        self.progress_canvas = tk.Canvas(
            self, height=18, bg=self.BG, highlightthickness=0, bd=0,
        )
        self.progress_canvas.pack(fill="x", padx=16, pady=(2, 8))

        # --- Output residue ---
        lower = tk.Frame(self, bg=self.BG)
        lower.pack(fill="both", expand=True, padx=16, pady=(0, 4))

        self.output_panel = tk.Frame(lower, bg=self.BG)
        self.output_panel.pack(fill="both", expand=True, anchor="w")

        tk.Label(
            self.output_panel, text="OUTPUT RESIDUE", fg=self.ORANGE, bg=self.BG,
            font=("Segoe UI", 12, "bold"),
        ).pack(anchor="w")

        tk.Frame(self.output_panel, bg=self.ORANGE, height=2, width=180).pack(
            anchor="w", pady=(2, 4)
        )

        self.artifact_link = tk.Label(
            self.output_panel, text="All that remains...",
            fg=self.BLUE2, bg=self.BG, cursor="hand2",
            font=("Consolas", 11), wraplength=700, justify="left", anchor="w",
        )
        self.artifact_link.pack(anchor="w", pady=(2, 6))
        self.artifact_link.bind("<Button-1>", lambda _e: self._on_artifact_click())

        self.agent_residue_label = tk.Label(
            self.output_panel, text="", fg=self.BLUE2, bg=self.BG,
            font=("Consolas", 10, "bold"), justify="left", anchor="w",
        )
        self.agent_residue_label.pack(anchor="w", pady=(0, 6))
        self.agent_residue_label.pack_forget()

    def _on_artifact_click(self):
        if self.artifact_command:
            self.artifact_command()

    def _on_url_focus_in(self, _):
        if self._placeholder_active:
            self.url_entry.delete(0, "end")
            self.url_entry.configure(fg=self.BLUE2)
            self._placeholder_active = False

    def _on_url_focus_out(self, _):
        if not self.url_entry.get().strip():
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, PLACEHOLDER)
            self.url_entry.configure(fg=self.DIM)
            self._placeholder_active = True
