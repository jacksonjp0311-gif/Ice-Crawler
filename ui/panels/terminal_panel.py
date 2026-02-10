# ui/panels/terminal_panel.py — Bottom tabbed terminal (Output | Events)

import tkinter as tk
from tkinter import ttk
from .base_panel import BasePanel


class TerminalPanel(BasePanel):
    """Tabbed terminal panel with Output and Events tabs."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self._collapsed = False
        self._build()

    def _build(self):
        # Header bar
        self.header = tk.Frame(self, bg="#0a1929", height=28)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.toggle_btn = tk.Label(
            self.header, text="\u25bc", fg=self.BLUE2, bg="#0a1929",
            font=("Consolas", 10, "bold"), cursor="hand2",
        )
        self.toggle_btn.pack(side="left", padx=(8, 4), pady=2)

        tk.Label(
            self.header, text="TERMINAL", fg=self.DIM, bg="#0a1929",
            font=("Segoe UI", 9, "bold"),
        ).pack(side="left", pady=2)

        # Notebook
        self.notebook = ttk.Notebook(self, style="IDE.TNotebook")
        self.notebook.pack(fill="both", expand=True)

        # Output tab
        output_frame = tk.Frame(self.notebook, bg=self.BG)
        self.notebook.add(output_frame, text="  Output  ")
        self.output_text = tk.Text(
            output_frame, bg=self.TEXT_BG, fg=self.BLUE2,
            insertbackground=self.BLUE2, relief="flat",
            font=("Consolas", 9), wrap="word",
        )
        self.output_text.pack(fill="both", expand=True, padx=4, pady=4)
        self.output_text.configure(state="disabled")

        # Events tab
        events_frame = tk.Frame(self.notebook, bg=self.BG)
        self.notebook.add(events_frame, text="  Events  ")
        self.events_text = tk.Text(
            events_frame, bg=self.TEXT_BG, fg=self.BLUE2,
            insertbackground=self.BLUE2, relief="flat",
            font=("Consolas", 9), wrap="word",
        )
        self.events_text.pack(fill="both", expand=True, padx=4, pady=4)
        self.events_text.configure(state="disabled")
